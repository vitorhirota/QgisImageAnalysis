# -*- coding: utf-8 -*-

#***********************************************************************
#
# Image Analysis
# ----------------------------------------------------------------------
# QGIS Image Analysis plugin for image segmentation and classification
#
# Vitor Hirota (vitor.hirota [at] gmail.com), INPE 2013
#
# This source is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This code is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# A copy of the GNU General Public License is available on the World
# Wide Web at <http://www.gnu.org/copyleft/gpl.html>. You can also
# obtain it by writing to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.
#
#***********************************************************************

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox, QWidget
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar

from analysis_ui import Ui_AnalysisWidget as Ui_Widget

import util
import classifier
import segmenter
import statistics

# from QgsMapLayer
VectorLayer = 0
RasterLayer = 1

# MESSAGE_LEVEL = util.AttrDict({
#     'INFO': 0,
#     'WARNING': 1,
#     'CRITICAL': 2
# })

class AnalysisWidget(QWidget, Ui_Widget):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.layers = self.iface.legendInterface().layers()
        self.task = None

        self.iface.mapCanvas().layersChanged.connect(self.layers_changed)

        self.tabs = ['segm', 'stats', 'clf']
        self.tab_ipts = {
            'segm': [self.segm_raster_ipt, self.segm_clusters_ipt],
            'stats': [self.stats_raster_ipt, self.stats_segm_ipt],
            'clf': [self.class_segm_ipt, self.class_roi_ipt,
                    self.class_roi_field, self.svm_kernel_ipt, self.svm_c_ipt,
                    self.svm_kgamma_ipt, self.svm_kdegree_ipt,
                    self.svm_kcoeff_ipt],
        }
        self.modules = {
            'segm': segmenter,
            'stats': statistics,
            'clf': classifier
        }

        self.ok_btn.pressed.connect(self.run)

        self.tabWidget.currentChanged['int'].connect(self.update_tab_focus)
        self.tabWidgetClf.currentChanged['int'].connect(self.update_subfocus_clf)
        self.update_tab_focus(self.tabWidget.currentIndex())

        self.class_roi_ipt.currentIndexChanged['QString'].connect(self.update_roi_field)
        self.svm_kernel_ipt.currentIndexChanged.connect(self.update_svm_attr)

    def log(self, msg, level='info'):
        level_dict = {
            'info': QgsMessageLog.INFO,
            'warn': QgsMessageLog.WARNING,
            'crit': QgsMessageLog.CRITICAL,
        }
        QgsMessageLog.logMessage(str(msg), level=level_dict[level])

    def layers_changed(self):
        layers = self.iface.legendInterface().layers()
        if self.layers != layers:
            self.layers = layers
            self.update_tab_focus(self.tabWidget.currentIndex())

    def get_layers(self, ltype):
        return [l for l in self.layers if l.type() == ltype]

    def get_layer(self, ltype, name):
        return [l for l in self.get_layers(ltype) if l.name() == name][0]

    def update_combo_box(self, ltype, ipt):
        ipt.clear()
        ipt.addItems([u'',] + [l.name() for l in self.get_layers(ltype)])

    def update_tab_order(self, inputs):
        ipts = [self.tabWidget, self.ok_btn]
        ipts[1:1] = inputs
        for i in range(len(ipts)-1):
            self.setTabOrder(ipts[i], ipts[i+1])

    def update_tab_focus(self, index):
        getattr(self, 'update_focus_%s' % self.tabs[index])()
        self.tabWidget.setFocus()

    def update_focus_segm(self):
        # update combo boxes
        self.update_combo_box(RasterLayer, self.segm_raster_ipt)
        # tab order
        self.update_tab_order(self.tab_ipts['segm'])

    def update_focus_stats(self):
        self.update_combo_box(RasterLayer, self.stats_raster_ipt)
        self.update_combo_box(VectorLayer, self.stats_segm_ipt)
        # tab order
        self.update_tab_order(self.tab_ipts['stats'])

    def update_focus_clf(self):
        self.update_combo_box(0, self.class_segm_ipt)
        self.update_combo_box(0, self.class_roi_ipt)
        self.update_subfocus_clf()

    def update_subfocus_clf(self):
        idx = self.tabWidgetClf.currentIndex() and [3, None] or [None, 3]
        ipts = self.tab_ipts['clf'][slice(*idx)] + [self.tabWidgetClf]
        self.update_tab_order(ipts)

    def update_roi_field(self, layer_name):
        self.class_roi_field.clear()
        if layer_name:
            layer = self.get_layer(VectorLayer, layer_name)
            fields = layer.dataProvider().fieldNameMap().keys()
            self.class_roi_field.addItems(fields)

    def update_svm_attr(self, item_index):
        kernel = self.svm_kernel_ipt.currentText().lower()
        ipts = self.tab_ipts['clf'][5:]
        attr_list = {
            'linear': [],
            'poly': ipts[1:],
            'rbf': ipts[0:1],
            'sigmoid': ipts[2:3],
        }
        for ipt in ipts:
            ipt.setEnabled(ipt in attr_list[kernel])

    def get_text(self, ipt):
        try:
            return ipt.currentText()
        except AttributeError:
            return ipt.cleanText()

    def run(self):
        # create a new task instance
        tab_name = self.tabs[self.tabWidget.currentIndex()]
        self.log('starting %s' % tab_name)
        # set task up
        args = [self.get_text(ipt)
                for ipt in self.tab_ipts[tab_name]]
        task = self.modules[tab_name].Task(self, *args)
        # validate
        if not task.is_valid():
            QMessageBox.critical(self.iface.mainWindow(), 'Error',
                                 task.invalid)
            return
        # update gui
        self.ok_btn.setEnabled(False)
        self.cancel_btn.pressed.connect(task.kill)
        self.progressBar.setValue(0)
        # configure QgsMessageBar
        action = self.tabWidget.tabText(self.tabWidget.currentIndex())
        messageBar = self.iface.messageBar().createMessage(action, '')
        msgProgressBar = QtGui.QProgressBar()
        msgProgressBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        cancelButton = QtGui.QPushButton()
        cancelButton.setText('Cancel')
        cancelButton.clicked.connect(self.cancel_btn.click)
        messageBar.layout().addWidget(msgProgressBar)
        messageBar.layout().addWidget(cancelButton)
        self.iface.messageBar().pushWidget(messageBar, QgsMessageBar.INFO)
        # hold objects
        self.messageBar = messageBar
        self.action = action
        # fire task
        task.run()



        # self.ok_btn.setEnabled(False)
        # self.progressBar.setValue(0)
        # self.thread = QtCore.QThread()
        # # create a new worker instance
        # tab_name = self.tabs[self.tabWidget.currentIndex()]
        # self.log('starting %s' % tab_name)
        # # set worker up
        # args = [self.get_text(ipt) for ipt in self.tab_ipts[tab_name]]
        # worker = self.modules[tab_name].Worker(self)
        # self.worker = worker
        # # worker = util.Worker()
        # self.post_run = worker.post_run
        # worker.setup(*args)
        # # validate
        # if not worker.is_valid():
        #     QMessageBox.critical(self.iface.mainWindow(), 'Error',
        #                          worker.invalid)
        #     self.kill()
        #     return
        # # configure QgsMessageBar
        # action = self.tabWidget.tabText(self.tabWidget.currentIndex())
        # messageBar = self.iface.messageBar().createMessage(action, '')
        # progressBar = QtGui.QProgressBar()
        # progressBar.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        # cancelButton = QtGui.QPushButton()
        # cancelButton.setText('Cancel')
        # cancelButton.clicked.connect(self.cancel_btn.click)
        # messageBar.layout().addWidget(progressBar)
        # messageBar.layout().addWidget(cancelButton)
        # self.iface.messageBar().pushWidget(messageBar, QgsMessageBar.INFO)
        # # start the worker in a new thread
        # worker.moveToThread(self.thread)
        # self.thread.started.connect(worker.run)
        # # setup signals
        # worker.log.connect(self.log)
        # worker.status.connect(self.status)
        # worker.progress.connect(progressBar.setValue)
        # worker.progress.connect(self.progressBar.setValue)
        # worker.error.connect(self.error)
        # worker.finished.connect(self.finish)
        # # hold objects
        # self.messageBar = messageBar
        # self.action = action
        # # fire thread
        # self.thread.start(priority=5)
        # self.thread.exec_()


if __name__ == "__main__":
    pass
