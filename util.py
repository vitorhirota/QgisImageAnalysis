# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# fTools
# Copyright (C) 2008-2011  Carson Farmer
# EMAIL: carson.farmer (at) gmail.com
# WEB  : http://www.ftools.ca/fTools.html
#
# A collection of data management and analysis tools for vector data
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from qgis.core import *

# This is a subset of fTools utils functions needed to intersect polygons

# From two input field maps, create single field map
def combineVectorFields( layerA, layerB ):
    fieldsA = layerA.dataProvider().fields()
    fieldsB = layerB.dataProvider().fields()
    fieldsB = testForUniqueness( fieldsA, fieldsB )
    for f in fieldsB:
      fieldsA.append( f )
    return fieldsA


# Convinience function to create a spatial index for input QgsVectorDataProvider
def createIndex( provider ):
    feat = QgsFeature()
    index = QgsSpatialIndex()
    fit = provider.getFeatures()
    while fit.nextFeature( feat ):
        index.insertFeature( feat )
    return index


def getGeomType(gT):
  if gT == 3 or gT == 6:
    gTypeListPoly = [ QGis.WKBPolygon, QGis.WKBMultiPolygon ]
    return gTypeListPoly
  elif gT == 2 or gT == 5:
    gTypeListLine = [ QGis.WKBLineString, QGis.WKBMultiLineString ]
    return gTypeListLine
  elif gT == 1 or gT == 4:
    gTypeListPoint = [ QGis.WKBPoint, QGis.WKBMultiPoint ]
    return gTypeListPoint


# Check if two input field maps are unique, and resolve name issues if they aren't
def testForUniqueness( fieldList1, fieldList2 ):
    changed = True
    while changed:
        changed = False
        for i in range(0,len(fieldList1)):
            for j in range(0,len(fieldList2)):
                if fieldList1[i].name() == fieldList2[j].name():
                    fieldList2[j] = createUniqueFieldName( fieldList2[j] )
                    changed = True
    return fieldList2


# Create a unique field name based on input field name
def createUniqueFieldName( field ):
    check = field.name()[-2:]
    shortName = field.name()[:8]
    if check[0] == "_":
        try:
            val = int( check[-1:] )
            if val < 2:
                val = 2
            else:
                val = val + 1
            field.setName( shortName[len( shortName )-1:] + unicode( val ) )
        except exceptions.ValueError:
            field.setName( shortName + "_2" )
    else:
        field.setName( shortName + "_2" )
    return field
