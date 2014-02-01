# -*- coding: utf-8 -*-

#***********************************************************************
#
# Image Analysis
# ----------------------------------------------------------------------
# Utility functions and base classes
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
# from qgis.core import *
from qgis.core import QgsMapLayer, QgsMessageLog, QgsVectorLayer
from qgis.gui import QgsMessageBar


def error_handler(run_fn):
    def wrapped(self, *args, **kwargs):
        try:
            self.log.emit('worker: run started')
            run_fn(self, *args, **kwargs)
        except:
            import traceback
            self.error.emit(traceback.format_exc())
            error_msg = 'Failed. Please check the logs for details.'
            self.finished.emit(False, error_msg)
        else:
            self.log.emit('worker: completed successfully')
            self.finished.emit(True, self.output)
    return wrapped


class Task(QtCore.QObject):
    def __init__(self, parent, *args):
        self.parent = parent
        self.valid = True
        self.worker = None
        self.setup(*args)

    def is_valid(self):
        return self.valid

    def run(self):
        # move worker to a new thread
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        # setup signals
        self.worker.log.connect(self.parent.log)
        self.worker.status.connect(self.status)
        self.worker.progress.connect(self.progress)
        self.worker.error.connect(self.error)
        self.worker.finished.connect(self.finish)
        # fire thread
        self.thread.start()
        self.thread.exec_()

    def clear_message_bar(self, msg, level=QgsMessageBar.INFO):
        mb = self.parent.iface.messageBar()
        mb.popWidget(self.parent.messageBar)
        mb.pushMessage(self.parent.action, msg, level=level)

    def post_run(self):
        pass

    def status(self, msg=''):
        self.parent.log(msg)
        self.parent.messageBar.setText(msg)

    def progress(self, value):
        self.parent.progressBar.setValue(value)
        pb = self.parent.messageBar.findChildren(QtGui.QProgressBar)[0]
        pb.setValue(value)

    def error(self, msg):
        self.parent.log(msg, level='crit')

    def kill(self):
        self.parent.log('worker: killing')
        self.worker.kill()
        self.parent.ok_btn.setEnabled(True)
        self.parent.progressBar.setValue(0)

    def finish(self, success, output):
        # post run
        if success:
            self.post_run(output)
            self.clear_message_bar(self.completed, duration=10)
        else:
            self.clear_message_bar(output, level=QgsMessageBar.CRITICAL,)
        # update gui
        self.parent.ok_btn.setEnabled(True)
        # clean up task, worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()


class Worker(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.abort = False
        self.output = None

    def setup(self, *args, **kwargs):
        pass

    def run(self):
        pass

    def kill(self):
        self.abort = True

    log = QtCore.pyqtSignal(str)
    status = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int)
    error = QtCore.pyqtSignal(str)
    # killed = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal(bool, str)
