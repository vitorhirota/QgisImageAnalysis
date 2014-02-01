# -*- coding: utf-8 -*-

#***********************************************************************
#
# Image Analysis
# ----------------------------------------------------------------------
# Image segmentation using K-Means an labeling connected components
#
# Jose Renato Garcia Braga (jgarciabraga [at] gmail.com), INPE 2013
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

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
from qgis.core import *

# import gdal
# from gdalconst import *
# from osgeo import gdal
import numpy
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
# from scipy import ndimage
# from scipy import stats

# # import ui
# from resources import ui_segmenter as ui

import util

class Task(util.Task):
    def setup(self, *args):
        # unpack arguments
        raster_ipt, clusters = args
        try:
            self.rst_layer = self.parent.get_layer(QgsMapLayer.RasterLayer,
                                                   raster_ipt)
        except IndexError:
            self.valid = False
            self.invalid = 'Please, set raster image.'
            return
        self.worker = Worker(self.rst_layer, clusters)

    def post_run(self, obj):
        pass


class Worker(util.Worker):
    def __init__(self, rst_layer, clusters):
        util.Worker.__init__(self)
        self.rst_layer = rst_layer
        self.clusters = clusters

    @util.error_handler
    def run(self):
        ok = True

        driver = gdal.GetDriverByName('GTiff')
        dataSetPixels = gdal.Open(self.rst_layer.source())
        sourceIntermediario = self.rst_layer.source()
        sourceIntermediario = sourceIntermediario.split('.')

        colunas = dataSetPixels.RasterXSize
        linhas = dataSetPixels.RasterYSize
        bandas = dataSetPixels.RasterCount
        geoTransform = dataSetPixels.GetGeoTransform()

        listaDeBandas = []
        for i in range(bandas):
            listaDeBandas.append(dataSetPixels.GetRasterBand(i+1).ReadAsArray(0,0,colunas,linhas))
        #fim for

        matrizCaracteristica = numpy.zeros(shape=(colunas*linhas,bandas))
        #retirando os elementos da lista com as matrizes e colocando na matriz que vai para o kmeans
        for i in range(listaDeBandas.__len__()):
            temp = listaDeBandas[i]
            matrizTemp = numpy.zeros(shape=(linhas,colunas))
            #inicio for
            for m in range(linhas):
                for n in range(colunas):
                    matrizTemp[m][n]=temp[m][n]
                #fim for
            #fim for
            #transferindo elementos para a matriz uqe vai para o kmenas
            cont = 0
            for j in range(linhas):
                for k in range(colunas):
                    matrizCaracteristica[cont][i]=matrizTemp[j][k]
                    cont = cont + 1
                #fim for
            #fim for
        #fim for da lista

        ###Realiza K-means
        kmeans = KMeans(n_clusters=clusters, init='k-means++', n_init=10)
        kmeans.fit(matrizCaracteristica)
        Z = kmeans.predict(matrizCaracteristica)
        matrizFinal = Z
        matrizFinal.shape = linhas,colunas
        img_plt3 = plt.imshow(matrizFinal,cmap=plt.cm.spectral)
        array3 = img_plt3.to_rgba(img_plt3.get_array(), alpha=None)
        matrizRed = numpy.zeros(shape=(linhas,colunas))
        matrizGreen = numpy.zeros(shape=(linhas,colunas))
        matrizBlue = numpy.zeros(shape=(linhas,colunas))
        for i in range(linhas):
            for j in range(colunas):
                matrizRed[i][j]= array3[i][j][0]
                matrizGreen[i][j] = array3[i][j][1]
                matrizBlue[i][j] = array3[i][j][2]
            #fim for
        #fim for

        sourceFinal = sourceIntermediario[0]+'KmeansCores.'+sourceIntermediario[1]
        dst_filename = sourceFinal
        dst_ds = driver.Create( dst_filename, colunas, linhas, 3, gdal.GDT_Float32)
        dst_ds.GetRasterBand(1).WriteArray(matrizRed)
        dst_ds.GetRasterBand(2).WriteArray(matrizGreen)
        dst_ds.GetRasterBand(3).WriteArray(matrizBlue)
        dst_ds.SetGeoTransform(geoTransform)
        dst_ds = None
        sourceFinal = sourceIntermediario[0]+'KmeansGrayScale.'+sourceIntermediario[1]
        dst_filename2 = sourceFinal
        dst_ds2 = driver.Create( dst_filename2, colunas, linhas, 1, gdal.GDT_UInt32)
        dst_ds2.GetRasterBand(1).WriteArray(matrizFinal)
        dst_ds2.SetGeoTransform(geoTransform)
        dst_ds2 = None

        ###Realiza filtro da moda
        # matrizParaFiltroModa = numpy.zeros(shape=(linhas,colunas))
        for i in range(linhas):
            for j in range(colunas):
                matrizParaFiltroModa[i][j]=matrizFinal[i][j]
            #fim for
        #fim for

        # matrizAuxiliar = numpy.zeros(shape=(3,3))
        for i in range(1,linhas-1):
            for j in range(1,colunas-1):
                matrizAuxiliar[0][0]=matrizParaFiltroModa[i-1][j-1]
                matrizAuxiliar[0][1]=matrizParaFiltroModa[i-1][j]
                matrizAuxiliar[0][2]=matrizParaFiltroModa[i-1][j+1]
                matrizAuxiliar[1][0]=matrizParaFiltroModa[i][j-1]
                matrizAuxiliar[1][1]=matrizParaFiltroModa[i][j]
                matrizAuxiliar[1][2]=matrizParaFiltroModa[i][j+1]
                matrizAuxiliar[2][0]=matrizParaFiltroModa[i+1][j-1]
                matrizAuxiliar[2][1]=matrizParaFiltroModa[i+1][j]
                matrizAuxiliar[2][2]=matrizParaFiltroModa[i+1][j+1]
                retorno = stats.mode(matrizAuxiliar,axis=None)
                matrizParaFiltroModa[i][j]=retorno[0]
            #fim for
        #fim for

        img_plt2=plt.imshow(matrizParaFiltroModa,cmap=plt.cm.spectral)
        array2 = img_plt2.to_rgba(img_plt2.get_array(), alpha=None)
        sourceFinal = sourceIntermediario[0]+'FiltroModaGrayScale.'+sourceIntermediario[1]
        dst_filename3 = sourceFinal
        dst_ds3 = driver.Create( dst_filename3, colunas, linhas, 1, gdal.GDT_UInt32)
        dst_ds3.GetRasterBand(1).WriteArray(matrizParaFiltroModa)
        dst_ds3.SetGeoTransform(geoTransform)
        dst_ds3 = None
        # matrizRed2 = numpy.zeros(shape=(linhas,colunas))
        # matrizGreen2 = numpy.zeros(shape=(linhas,colunas))
        # matrizBlue2 = numpy.zeros(shape=(linhas,colunas))
        for i in range(linhas):
            for j in range(colunas):
                matrizRed2[i][j]= array2[i][j][0]
                matrizGreen2[i][j] = array2[i][j][1]
                matrizBlue2[i][j] = array2[i][j][2]
            #fim for
        #fim for

        sourceFinal = sourceIntermediario[0]+'FiltroModaCores.'+sourceIntermediario[1]
        dst_filename4 = sourceFinal
        dst_ds4 = driver.Create( dst_filename4, colunas, linhas, 3, gdal.GDT_Float32)
        dst_ds4.GetRasterBand(1).WriteArray(matrizRed2)
        dst_ds4.GetRasterBand(2).WriteArray(matrizGreen2)
        dst_ds4.GetRasterBand(3).WriteArray(matrizBlue2)
        dst_ds4.SetGeoTransform(geoTransform)
        dst_ds4 = None

        ###Realiza Componentes Conectados
        listaDeMatrizes = []
        for i in range(clusters):
            listaDeMatrizes.append(matrizParaFiltroModa)
        #fim for
        listaDeMatrizesDois = []
        elemento = 0
        for i in range(clusters):
            # matrizTempDois = numpy.zeros(shape=(linhas,colunas))
            tempDois = listaDeMatrizes.pop()
            for m in range(linhas):
                for n in range(colunas):
                    matrizTempDois[m][n]=tempDois[m][n]
                #fim for
            #fim for
            for j in range(linhas):
                for k in range(colunas):
                    if matrizTempDois[j][k]==elemento:
                        matrizTempDois[j][k]=1
                    else:
                        matrizTempDois[j][k]=0
                #fim for
            #fim for
            listaDeMatrizesDois.append(matrizTempDois)
            elemento = elemento + 1
        #fim for
        listaLabel = []
        componentes = 0
        for i in range(clusters):
            # matrizTempTres = numpy.zeros(shape=(linhas,colunas))
            tempTres = listaDeMatrizesDois.pop()
            for m in range(linhas):
                for n in range(colunas):
                    matrizTempTres[m][n]=tempTres[m][n]
                #fim for
            #fim for
            labelImage, numeroDeComponentes = ndimage.label(matrizTempTres)
            if i==0:
                componentes = numeroDeComponentes
                listaLabel.append(labelImage)
            else:
                for j in range(linhas):
                    for k in range(colunas):
                        if labelImage[j][k] != 0:
                            labelImage[j][k]=labelImage[j][k]+componentes
                        #fim if
                    #fim for
                #fim for
                componentes = componentes + numeroDeComponentes
                listaLabel.append(labelImage)
            #fim else
        #fim for
        # matrizSomaFinal = numpy.zeros(shape=(linhas,colunas))
        for i in range(clusters):
            # matrizTempQuatro = numpy.zeros(shape=(linhas,colunas))
            tempQuatro = listaLabel.pop()
            for m in range(linhas):
                for n in range(colunas):
                    matrizTempQuatro[m][n]=tempQuatro[m][n]
                #fim for
            #fim for
            for j in range(linhas):
                for k in range(colunas):
                    matrizSomaFinal[j][k]=matrizSomaFinal[j][k]+matrizTempQuatro[j][k]
                #fim for
            #fim for
        #fim for
        #plt.imshow(matrizSomaFinal,cmap=plt.cm.spectral)
        #plt.show()
        img_plt = plt.imshow(matrizSomaFinal,cmap=plt.cm.spectral)
        array = img_plt.to_rgba(img_plt.get_array(), alpha=None)
        sourceFinal = sourceIntermediario[0]+'SegmentadoGrayScale.'+sourceIntermediario[1]
        dst_filename5 = sourceFinal
        dst_ds5 = driver.Create( dst_filename5, colunas, linhas, 1, gdal.GDT_UInt32)
        dst_ds5.GetRasterBand(1).WriteArray(matrizSomaFinal)
        dst_ds5.SetGeoTransform(geoTransform)
        dst_ds5 = None
        # matrizRed3 = numpy.zeros(shape=(linhas,colunas))
        # matrizGreen3 = numpy.zeros(shape=(linhas,colunas))
        # matrizBlue3 = numpy.zeros(shape=(linhas,colunas))
        for i in range(linhas):
            for j in range(colunas):
                matrizRed3[i][j]= array[i][j][0]
                matrizGreen3[i][j] = array[i][j][1]
                matrizBlue3[i][j] = array[i][j][2]
            #fim for
        #fim for
        sourceFinal = sourceIntermediario[0]+'SegmentadoCores.'+sourceIntermediario[1]
        dst_filename6 = sourceFinal
        dst_ds6 = driver.Create( dst_filename6, colunas, linhas, 3, gdal.GDT_Float32)
        dst_ds6.GetRasterBand(1).WriteArray(matrizRed3)
        dst_ds6.GetRasterBand(2).WriteArray(matrizGreen3)
        dst_ds6.GetRasterBand(3).WriteArray(matrizBlue3)
        dst_ds6.SetGeoTransform(geoTransform)
        dst_ds6 = None
        QMessageBox.information(self.iface.mainWindow(), 'Execucao Encerrada', 'O Plugin Concluiu Sua Execucao')

