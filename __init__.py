# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""

def name():
    return "ImageClassifier"
def author():
    return "Vitor Hirota, DPI INPE"
def email():
    return ""
def description():
    return "Image Classifier"
def version():
    return "Version 1.0"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "2.0"
# def qgisMaximumVersion():
#     return "2.99"
def classFactory(iface):
    from plugin import ImageClassifier
    return ImageClassifier(iface)
