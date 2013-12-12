# -*- coding: utf-8 -*-

#******************************************************************************
#
# Image Classifier
# ---------------------------------------------------------
# Label propagation with SVMs
#
# Vitor Hirota (vitor.hirota [at] gmail.com), INPE 2013
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import numpy as np
import processing
import shapefile
from osgeo import gdal
from sklearn import svm
from sklearn import preprocessing

import inspect
import os
import tempfile

import ui
import util


class Dialog(QDialog, ui.Ui_Dialog):

    img_layer = None
    seg_layer = None
    roi_layer = None

    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.layers = self.iface.legendInterface().layers()

        raster_layers = [u'',] + [l.name() for l in self.__get_layers(ltype='raster')]
        vector_layers = [u'',] + [l.name() for l in self.__get_layers(ltype='vector')]

        self.input_ipt.addItems(raster_layers)
        self.segm_ipt.addItems(vector_layers)
        self.roi_ipt.addItems(vector_layers)

        # set events
        self.input_ipt.currentIndexChanged['QString'].connect(self.holdLayers)
        self.segm_ipt.currentIndexChanged['QString'].connect(self.holdLayers)
        self.roi_ipt.currentIndexChanged['QString'].connect(self.holdLayers)
        self.roi_ipt.currentIndexChanged['QString'].connect(self.updateRoiField)
        self.kernel_ipt.currentIndexChanged.connect(self.updateSVMKernelAttr)
        self.segm_stats_btn.clicked.connect(self.generateStats)

    def __log(self, msg, level='info'):
        level_dict = {
            'info': QgsMessageLog.INFO,
            'warn': QgsMessageLog.WARNING,
            'crit': QgsMessageLog.CRITICAL,
        }
        QgsMessageLog.logMessage(str(msg), level=level_dict[level])

    def __message(self, title, text, mtype='info'):
        type_dict = {
            'about': QMessageBox.about,
            'info': QMessageBox.information,
            'warn': QMessageBox.warning,
            'crit': QMessageBox.critical,
            'quest': QMessageBox.question,
        }
        type_dict[mtype](self.iface.mainWindow(), title, text)

    def __get_layers(self, ltype=None, name=None):
        l = lambda s: True
        typeCheck, nameCheck = l, l
        if ltype:
            # filter by layer type: 1 - raster, 0 - vector
            if type(ltype) == str:
                ltype = ltype == 'raster' and 1 or ltype == 'vector' and 0
            typeCheck = lambda s: s.type() == ltype
        if name:
            nameCheck = lambda s: s.name() == name
        return [l for l in self.layers if typeCheck(l) and nameCheck(l)]

    def __get_fields(self, layer_name):
        layer = self.__get_layers('vector', layer_name)[0]
        provider = layer.dataProvider()
        return provider.fieldNameMap().keys()

    def __validate(self, function=None):
        if not (self.img_layer and self.seg_layer):
            img = not self.img_layer and 'Input' or 'Segmented'
            self.__message('Error', '%s Image not set.' % img, 'crit')
            return False

        if function == 'stats':
            try:
                self.seg_ras_layer = self.__get_layers('raster', self.seg_layer.name())[0]
            except IndexError:
                self.__message('Error',
                               'In order to generate stats, a raster ' +
                               'segmented image must also be present. ' +
                               'Both layers must have the same name.',
                               'crit')
                return False

        if function == 'classify':
            if not self.roi_layer:
                self.__message('Error', 'ROI layer not set.', 'crit')
                return False

        return True


    def holdLayers(self, layer_name):
        attr_dict = {
            # combobox: (self.attr, layer_type)
            'input_ipt': ('img_layer', 1),
            'segm_ipt': ('seg_layer', 0),
            'roi_ipt': ('roi_layer', 0),
        }
        _sender = self.sender().objectName()
        setattr(self,
                attr_dict[_sender][0],
                self.__get_layers(attr_dict[_sender][1], layer_name)[0])
        return

    def updateRoiField(self, layer_name):
        fields = self.__get_fields(layer_name)
        self.roi_class_field_ipt.clear()
        self.roi_class_field_ipt.addItems(fields)

    def updateSVMKernelAttr(self, item_index):
        attributes = {'degree', 'coeff', 'gamma'}
        attr_list = {
            'linear': set(),
            'poly': {'degree', 'coeff'},
            'rbf': {'gamma'},
            'sigmoid': {'coeff'},
        }
        kernel = self.kernel_ipt.currentText().lower()
        for attr in attributes:
            ipt = getattr(self, 'k%s_ipt' % attr)
            ipt.setEnabled(attr in attr_list[kernel])

    def generateStats(self):
        if not self.__validate('stats'):
            return

        # to-do progress dialog
        # self.progressBar.setMaximum(10)
        # import time
        # count = 10
        # for i in range(10):
        #         time.sleep(1)
        #         self.progressBar.setValue(i + 1)

        shp_name = self.seg_layer.source()
        seg_editor = shapefile.Editor(shp_name)

        if len(seg_editor.fields) > 2:
            self.__log('zonal stats might already be present')
            # zonal stats are probably present
            return

        # dataProvider = self.seg_layer.dataProvider()

        # if len(dataProvider.attributeIndexes()) > 1:
        #     self.__log('zonal stats might already be present')
        #     # zonal stats are probably present
        #     return

        # open rasters
        img_ds = gdal.Open(self.img_layer.source())
        seg_ds = gdal.Open(self.seg_ras_layer.source())
        # read arrays
        data_img = img_ds.ReadAsArray()
        data_seg = seg_ds.ReadAsArray()

        # transpose img information into a vector of band-dimensional vectors
        img_vector = data_img.transpose(1,2,0).reshape(data_seg.size,6)

        # get indices for each segment in a 1d vector
        u, indices = np.unique(data_seg, return_inverse=True)

        # create fields
        fields = ['average', 'median', 'var']
        for b in range(img_ds.RasterCount):
            for i in fields:
                seg_editor.field('_'.join([str(b), i]), 'N', 15, 5)
        # iterate through each feature in the shp file (segment),
        # calculate zonal statistics and write to shp field
        arr = np.zeros((1, len(seg_editor.fields)-2))
        func_names = [np.average, np.median, np.std]
        for rec in seg_editor.records:
            segment_id = rec[0]
            mat = np.multiply(img_vector.T, (indices == segment_id-1))
            mat = (mat.T[np.all(mat.T > 0, axis=1)]).T # filter 0 values
            stats = np.array([np.apply_over_axes(f, mat, [1]).flatten().tolist()
                              for f in func_names]).T.flatten()
            arr = np.vstack((arr, stats))

        seg_editor.records = np.c_[seg_editor.records, arr[1:,:]]
        seg_editor.saveDbf(shp_name)

        # self.seg_layer.dataProvider().reloadData() # this crashes qgis

        self.__message('Success', 'Statistics generation done.')

    def selectOutputFile(self):
        self.output_lineEdit.setText(QFileDialog.getOpenFileName())

    def addLayerIntoCanvas(self, fileInfo):
        vl = self.iface.addVectorLayer(fileInfo.filePath(), fileInfo.baseName(), "ogr")
        if vl != None and vl.isValid():
            if hasattr(self, 'lastEncoding'):
                vl.setProviderEncoding(self.lastEncoding)

    def accept(self):
        self.__log('threading')
        # self.thread = ClassificationThread(self.iface.mainWindow(),
        #                                    self,
        #                                    'classify')
        # self.connect(self.thread, SIGNAL("classify(QString)"), self.classify)

        # QObject.connect(self.thread, SIGNAL("runFinished(PyQt_PyObject)"), self.runFinishedFromThread)
        # QObject.connect(self.thread, SIGNAL("runStatus(PyQt_PyObject)"), self.runStatusFromThread)
        # QObject.connect(self.thread, SIGNAL("runRange(PyQt_PyObject)"), self.runRangeFromThread)
        # self.cancel_close.setText(self.tr("Cancel"))
        # QObject.connect(self.confirm_buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.cancelThread)
        # self.thread.start()

        self.classify()

    def classify(self):
        if not self.__validate('classify'):
            return

        data = []
        # intersect roi with segments and extract attributes
        vproviderA = self.roi_layer.dataProvider()
        vproviderB = self.seg_layer.dataProvider()
        fields = util.combineVectorFields(self.roi_layer, self.seg_layer)

        inFeatA = QgsFeature()
        inFeatB = QgsFeature()
        # outFeat = QgsFeature()
        nElement = 0

        index = util.createIndex(vproviderB)

        # nFeat = vproviderA.featureCount()
        # self.emit(SIGNAL("runStatus(PyQt_PyObject)"), 0)
        # self.emit(SIGNAL("runRange(PyQt_PyObject)"), (0, nFeat))

        fitA = vproviderA.getFeatures()
        while fitA.nextFeature(inFeatA):
            # nElement += 1
            # self.emit(SIGNAL("runStatus(PyQt_PyObject)"), nElement)
            geom = QgsGeometry(inFeatA.geometry())
            atMapA = inFeatA.attributes()
            intersects = index.intersects(geom.boundingBox())
            for id in intersects:
                vproviderB.getFeatures(QgsFeatureRequest().setFilterFid(int(id))).nextFeature(inFeatB)
                tmpGeom = QgsGeometry(inFeatB.geometry())
                try:
                    if geom.intersects(tmpGeom):
                        atMapB = inFeatB.attributes()
                        int_geom = QgsGeometry(geom.intersection(tmpGeom))
                        if int_geom.wkbType() == 0:
                            int_com = geom.combine(tmpGeom)
                            int_sym = geom.symDifference(tmpGeom)
                            int_geom = QgsGeometry(int_com.difference(int_sym))
                        try:
                            gList = util.getGeomType(geom.wkbType())
                            if int_geom.wkbType() in gList:
                                # outFeat.setGeometry(int_geom)
                                # outFeat.setAttributes(atMapB + atMapA)
                                # data.append(outFeat.attributes()[1:])
                                # filter segment id
                                data.append(atMapB[1:]+atMapA)
                        except Exception as e:
                              FEATURE_EXCEPT = False
                              continue
                except Exception as e:
                    self.__message('Error', '%s: %s' % (e.errno, e.strerror), 'crit')
                    break

        # read train data
        data = np.array(data)
        samples = data[:,:-1]
        labels = data[:,-1].astype(int)

        # read classification data
        class_shp = shapefile.Reader(self.seg_layer.source())
        data = np.array(class_shp.records())[:,1:]

        classifier = svm.SVC(kernel=str(self.kernel_ipt.currentText().lower()),
                             C=float(self.c_ipt.cleanText()),
                             coef0=float(self.kcoeff_ipt.cleanText()),
                             degree=float(self.kdegree_ipt.cleanText()),
                             gamma=float(self.kgamma_ipt.cleanText()))
        classifier.fit(preprocessing.scale(samples), labels)
        classified = classifier.predict(preprocessing.scale(data))

        # create a copy of the segmented shapefile
        temp = tempfile.NamedTemporaryFile(prefix='classify_%s_c%s_' % (
                                            self.kernel_ipt.currentText().lower(),
                                            self.c_ipt.cleanText().replace('.', '_')
                                           ),
                                           dir=os.path.dirname(self.seg_layer.source()))
        shp_name = '%s.shp' % temp.name
        seg_dp = self.seg_layer.dataProvider()
        shp = QgsVectorFileWriter.writeAsVectorFormat(self.seg_layer,
                                                      shp_name,
                                                      seg_dp.encoding(),
                                                      seg_dp.crs())

        # edit shape records
        e = shapefile.Editor(shp_name)
        e.fields = e.fields[0:2]
        e.field('Class', 'N', 5, 0)
        e.records = np.c_[np.array(e.records)[:,0], classified]
        e.saveDbf(shp_name)
        # add layer to project
        class_layer = self.iface.addVectorLayer(shp_name,
                                                os.path.basename(temp.name).split('.')[0],
                                                self.seg_layer.providerType())
        # set same style as roi layer
        # this crashes qgis
        # renderer = self.roi_layer.rendererV2()
        # renderer.setClassAttribute('Class')
        # class_layer.setRendererV2(renderer)
        # self.iface.legendInterface().refreshLayerSymbology(class_layer)

        self.__message('Success', 'Classification completed successfully.')
        return



class ClassificationThread(QThread):
    def __init__(self, parentThread, parentObject, function, kwargs=None):
        QThread.__init__(self, parentThread)
        self.parent = parentObject
        self.running = False
        self.function = function
        # self.parent.__log('threaded')

    def run(self):
        self.running = True
        # result = getattr(self, self.function)()
        self.emit(SIGNAL('classify(QString)'), "from work thread")
        return

    def stop(self):
        self.running = False


