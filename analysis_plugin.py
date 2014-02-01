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
from analysis_widget import AnalysisWidget

class ImageAnalysis(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def initGui(self):
        self.analysiswidget = AnalysisWidget(self.iface)
        # create the dockwidget with the correct parent
        self.andockwidget = QtGui.QDockWidget('Image Analysis',
                                              self.iface.mainWindow())
        self.andockwidget.setObjectName('AnalysisDockWidget')
        self.andockwidget.setMinimumSize(QtCore.QSize(335, 225))
        self.andockwidget.setWidget(self.analysiswidget)

        # add the dockwidget to iface
        self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                                 self.andockwidget)

    def unload(self):
        self.andockwidget.close()
        self.iface.removeDockWidget(self.andockwidget)


if __name__ == '__main__':
    pass
