# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""

def name():
    return "Image Analysis"

def author():
    return "Vitor Hirota Makiyama, José Renato Garcia Braga, DPI INPE"

def email():
    return "vitor.hirota@gmail.com, jgarciabraga@gmail.com"

def description():
    return "Image Analysis toolkit for segmentation/classification."

def version():
    return "1.0"

def icon():
    return "resources/icon.png"

def qgisMinimumVersion():
    return "2.0"

# def qgisMaximumVersion():
#     return "2.99"

def classFactory(iface):
    from analysis_plugin import ImageAnalysis
    return ImageAnalysis(iface)
