# -*- coding: utf-8 -*-

#******************************************************************************
#
# Image Classifier
# ---------------------------------------------------------
# Label propagation with SVMs
#
# Vitor Hirota (vitor.hirota [at] gmail.com), INPE 2013
#
#
# The MIT License (MIT)
#
# Copyright (c) 2013 Vitor Hirota (vitor.hirota [at] gmail.com), INPE
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#******************************************************************************

from PyQt4.QtCore import QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import QAction, QMessageBox, QIcon
from qgis.core import *
import classifier
import resource_rc

class ImageClassifier:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None

    def initGui(self):
        # Create action that will start plugin
        self.action = QAction(QIcon(":/plugins/ImageClassifier/icons/icon.png"),
                                    "&ImageClassifier",
                                    self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Image Classifier", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("ImageClassifier", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run
    def run(self):
        dialog = classifier.Dialog(self.iface)
        dialog.exec_()


if __name__ == "__main__":
    pass
