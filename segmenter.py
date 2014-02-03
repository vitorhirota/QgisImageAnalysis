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

import copy
import pickle
import os
import tempfile
import time

from qgis.core import *

import numpy as np
from osgeo import gdal
from sklearn.cluster import KMeans
from scipy import ndimage
from scipy import stats

import util

class Task(util.Task):
    def setup(self, *args):
        # unpack arguments
        raster_ipt, n_clusters = args
        try:
            self.rst_layer = self.parent.get_layer(QgsMapLayer.RasterLayer,
                                                   raster_ipt)
        except IndexError:
            self.valid = False
            self.invalid = 'Please, set raster image.'
            return
        # open raster images
        self.rst_ds = gdal.Open(self.rst_layer.source(), gdal.GA_ReadOnly)
        # create output raster
        filename = '%s/kmeans_c%s_%s.tif' % (
                        os.path.dirname(self.rst_layer.source()),
                        n_clusters,
                        int(time.time())
                    )
        x, y = self.rst_layer.width(), self.rst_layer.height()
        driver = gdal.GetDriverByName('GTiff')
        self.dst_ds = driver.Create(filename, x, y, 1, gdal.GDT_UInt32)
        self.dst_ds.SetGeoTransform(self.rst_ds.GetGeoTransform())
        self.dst_ds.SetProjection(self.rst_ds.GetProjection())

        self.worker = Worker(self.rst_layer, self.rst_ds, self.dst_ds,
                             n_clusters)
        self.filename = filename

    def post_run(self, obj):
        # add output raster to canvas
        rlayer = QgsRasterLayer(self.filename, os.path.basename(self.filename))
        QgsMapLayerRegistry.instance().addMapLayer(rlayer)

        self.completed = ('completed successfully. ')


class Worker(util.Worker):
    def __init__(self, rst_layer, rst_ds, dst_ds, n_clusters):
        util.Worker.__init__(self)
        self.rst_layer = rst_layer
        self.rst_ds = rst_ds
        self.dst_ds = dst_ds
        self.n_clusters = int(n_clusters)
        self.percentage = 0
        # self.tmp_rst = tempfile.NamedTemporaryFile()

    @util.error_handler
    def run(self):
        # ok = True

        # dataSetPixels = gdal.Open(self.rst_layer.source())
        dataSetPixels = self.rst_ds
        sourceIntermediario = self.rst_layer.source()
        sourceIntermediario = sourceIntermediario.split('.')

        colunas = dataSetPixels.RasterXSize
        linhas = dataSetPixels.RasterYSize
        bandas = dataSetPixels.RasterCount
        geoTransform = dataSetPixels.GetGeoTransform()

        # listaDeBandas = []
        # for i in range(bandas):
        #     listaDeBandas.append(dataSetPixels.GetRasterBand(i+1).ReadAsArray(0,0,colunas,linhas))
        #     self.calculate_progress()
        # #fim for

        # matrizCaracteristica = np.zeros(shape=(colunas*linhas,bandas))
        # #retirando os elementos da lista com as matrizes e colocando na matriz que vai para o kmeans
        # for i in range(listaDeBandas.__len__()):
        #     temp = listaDeBandas[i]
        #     matrizTemp = np.zeros(shape=(linhas,colunas))
        #     #inicio for
        #     for m in range(linhas):
        #         for n in range(colunas):
        #             matrizTemp[m][n]=temp[m][n]
        #             self.calculate_progress()
        #         #fim for
        #     #fim for
        #     #transferindo elementos para a matriz uqe vai para o kmenas
        #     cont = 0
        #     for j in range(linhas):
        #         for k in range(colunas):
        #             matrizCaracteristica[cont][i]=matrizTemp[j][k]
        #             cont = cont + 1
        #             self.calculate_progress()
        #         #fim for
        #     #fim for
        # #fim for da lista
        data_rst = self.rst_ds.ReadAsArray()
        matrizCaracteristica = data_rst.reshape(6, linhas*colunas).T

        ###Realiza K-means
        kmeans = KMeans(n_clusters=self.n_clusters, init='k-means++', n_init=10)
        # KMeans()
        self.status.emit('clustering data (this may take a few minutes)... ')
        clusters = kmeans.fit_predict(data_rst.reshape(6, linhas*colunas).T)
        self.progress.emit(10)
        matrizFinal = clusters
        # kmeans.fit(matrizCaracteristica)
        # matrizFinal = kmeans.predict(matrizCaracteristica)
        # matrizFinal.shape = linhas,colunas
        # # img_plt3 = plt.imshow(matrizFinal,cmap=plt.cm.spectral)
        # array3 = img_plt3.to_rgba(img_plt3.get_array(), alpha=None)
        # matrizRed = np.zeros(shape=(linhas,colunas))
        # matrizGreen = np.zeros(shape=(linhas,colunas))
        # matrizBlue = np.zeros(shape=(linhas,colunas))
        # for i in range(linhas):
        #     for j in range(colunas):
        #         matrizRed[i][j]= array3[i][j][0]
        #         matrizGreen[i][j] = array3[i][j][1]
        #         matrizBlue[i][j] = array3[i][j][2]
        #     #fim for
        # #fim for

        # plot kmeans result in canvas
        # sourceFinal = sourceIntermediario[0]+'KmeansCores.'+sourceIntermediario[1]
        # dst_filename = sourceFinal
        # dst_ds = driver.Create( dst_filename, colunas, linhas, 3, gdal.GDT_Float32)
        # dst_ds.GetRasterBand(1).WriteArray(matrizRed)
        # dst_ds.GetRasterBand(2).WriteArray(matrizGreen)
        # dst_ds.GetRasterBand(3).WriteArray(matrizBlue)
        # dst_ds.SetGeoTransform(geoTransform)
        # dst_ds = None
        # sourceFinal = sourceIntermediario[0]+'KmeansGrayScale.'+sourceIntermediario[1]
        # dst_filename2 = sourceFinal
        # dst_ds2 = driver.Create( dst_filename2, colunas, linhas, 1, gdal.GDT_UInt32)
        # dst_ds2.GetRasterBand(1).WriteArray(matrizFinal)
        # dst_ds2.SetGeoTransform(geoTransform)
        # dst_ds2 = None

        # ###Realiza filtro da moda
        # # matrizParaFiltroModa = np.zeros(shape=(linhas,colunas))
        # for i in range(linhas):
        #     for j in range(colunas):
        #         matrizParaFiltroModa[i][j]=matrizFinal[i][j]
        #     #fim for
        # #fim for

        self.status.emit('applying mode filter...')
        matrizAuxiliar = np.zeros(shape=(3,3))
        matrizParaFiltroModa = matrizFinal.reshape(linhas, colunas)
        step = 0
        for i in range(1,linhas-1):
            for j in range(1,colunas-1):
                # matrizAuxiliar[0][0]=matrizParaFiltroModa[i-1][j-1]
                # matrizAuxiliar[0][1]=matrizParaFiltroModa[i-1][j]
                # matrizAuxiliar[0][2]=matrizParaFiltroModa[i-1][j+1]
                # matrizAuxiliar[1][0]=matrizParaFiltroModa[i][j-1]
                # matrizAuxiliar[1][1]=matrizParaFiltroModa[i][j]
                # matrizAuxiliar[1][2]=matrizParaFiltroModa[i][j+1]
                # matrizAuxiliar[2][0]=matrizParaFiltroModa[i+1][j-1]
                # matrizAuxiliar[2][1]=matrizParaFiltroModa[i+1][j]
                # matrizAuxiliar[2][2]=matrizParaFiltroModa[i+1][j+1]
                retorno = stats.mode(matrizParaFiltroModa[i-1:i+2,j-1:j+2], axis=None)
                matrizParaFiltroModa[i][j]=retorno[0]
            step += 1
            self.calculate_progress(step, linhas, 10, 30)
            #fim for
        #fim for

        # img_plt2=plt.imshow(matrizParaFiltroModa,cmap=plt.cm.spectral)
        # array2 = img_plt2.to_rgba(img_plt2.get_array(), alpha=None)
        # sourceFinal = sourceIntermediario[0]+'FiltroModaGrayScale.'+sourceIntermediario[1]
        # dst_filename3 = sourceFinal
        # dst_ds3 = driver.Create( dst_filename3, colunas, linhas, 1, gdal.GDT_UInt32)
        # dst_ds3.GetRasterBand(1).WriteArray(matrizParaFiltroModa)
        # dst_ds3.SetGeoTransform(geoTransform)
        # dst_ds3 = None
        # # matrizRed2 = np.zeros(shape=(linhas,colunas))
        # # matrizGreen2 = np.zeros(shape=(linhas,colunas))
        # # matrizBlue2 = np.zeros(shape=(linhas,colunas))
        # for i in range(linhas):
        #     for j in range(colunas):
        #         matrizRed2[i][j]= array2[i][j][0]
        #         matrizGreen2[i][j] = array2[i][j][1]
        #         matrizBlue2[i][j] = array2[i][j][2]
        #     #fim for
        # #fim for

        # sourceFinal = sourceIntermediario[0]+'FiltroModaCores.'+sourceIntermediario[1]
        # dst_filename4 = sourceFinal
        # dst_ds4 = driver.Create( dst_filename4, colunas, linhas, 3, gdal.GDT_Float32)
        # dst_ds4.GetRasterBand(1).WriteArray(matrizRed2)
        # dst_ds4.GetRasterBand(2).WriteArray(matrizGreen2)
        # dst_ds4.GetRasterBand(3).WriteArray(matrizBlue2)
        # dst_ds4.SetGeoTransform(geoTransform)
        # dst_ds4 = None

        ###Realiza Componentes Conectados
        # listaDeMatrizes = []
        # for i in range(n_clusters):
        #     listaDeMatrizes.append(matrizParaFiltroModa)
        # #fim for
        matrizes = [np.where(clusters==i, 1, 0).reshape(linhas, colunas)
                    for i in np.unique(clusters)]
        # listaDeMatrizesDois = []
        # elemento = 0
        # for i in range(n_clusters):
        #     matrizTempDois = np.zeros(shape=(linhas,colunas))
        #     tempDois = matrizParaFiltroModa.copy()
        #     for m in range(linhas):
        #         for n in range(colunas):
        #             matrizTempDois[m][n]=tempDois[m][n]
        #         #fim for
        #     #fim for
        #     for j in range(linhas):
        #         for k in range(colunas):
        #             if matrizTempDois[j][k]==elemento:
        #                 matrizTempDois[j][k]=1
        #             else:
        #                 matrizTempDois[j][k]=0
        #         #fim for
        #     #fim for
        #     listaDeMatrizesDois.append(matrizTempDois)
        #     elemento = elemento + 1
        # #fim for

        self.status.emit('labelling connected components')
        segments = np.zeros(shape=(linhas, colunas))
        components = 0
        step = 0
        for i in np.unique(clusters):
            tmp = np.where(clusters==i, 1, 0).reshape(linhas, colunas)
            lbl, comp = ndimage.label(tmp)
            segments += np.ma.masked_equal(lbl, 0) + components
            components += comp

        # listaDeMatrizesDois = copy.copy(matrizes)
        # listaLabel = []
        # componentes = 0
        # step = 0
        # for i in range(self.n_clusters):
        #     matrizTempTres = listaDeMatrizesDois.pop()
        #     # matrizTempTres = np.zeros(shape=(linhas,colunas))
        #     # tempTres = listaDeMatrizesDois.pop()
        #     # for m in range(linhas):
        #     #     for n in range(colunas):
        #     #         matrizTempTres[m][n]=tempTres[m][n]
        #     #     #fim for
        #     # #fim for
        #     labelImage, numeroDeComponentes = ndimage.label(matrizTempTres)
        #     if i==0:
        #         componentes = numeroDeComponentes
        #         listaLabel.append(labelImage)
        #     else:
        #         for j in range(linhas):
        #             for k in range(colunas):
        #                 if labelImage[j][k] != 0:
        #                     labelImage[j][k]=labelImage[j][k]+componentes
        #                 #fim if
        #             #fim for
        #         #fim for
        #         componentes = componentes + numeroDeComponentes
        #         listaLabel.append(labelImage)
            #fim else
            step += 1
            self.calculate_progress(step, self.n_clusters, 40, 30)
        # #fim for
        # matrizSomaFinal = np.zeros(shape=(linhas,colunas))
        # step = 0
        # for i in range(self.n_clusters):
        #     matrizTempQuatro = np.zeros(shape=(linhas,colunas))
        #     tempQuatro = listaLabel.pop()
        #     for m in range(linhas):
        #         for n in range(colunas):
        #             matrizTempQuatro[m][n]=tempQuatro[m][n]
        #         #fim for
        #     #fim for
        #     for j in range(linhas):
        #         for k in range(colunas):
        #             matrizSomaFinal[j][k]=matrizSomaFinal[j][k]+matrizTempQuatro[j][k]
        #         #fim for
        #     #fim for
        #     step += 1
        #     self.calculate_progress(step, self.n_clusters, 70, 30)
        # #fim for
        # #plt.imshow(matrizSomaFinal,cmap=plt.cm.spectral)
        # #plt.show()
        # img_plt = plt.imshow(matrizSomaFinal,cmap=plt.cm.spectral)
        # array = img_plt.to_rgba(img_plt.get_array(), alpha=None)
        # sourceFinal = sourceIntermediario[0]+'SegmentadoGrayScale.'+sourceIntermediario[1]
        # dst_filename5 = sourceFinal

        matrizSomaFinal = segments
        # import pydevd; pydevd.settrace()
        self.dst_ds.GetRasterBand(1).WriteArray(matrizSomaFinal)
        # self.dst_ds = None

        # self.output = pickle.dumps(filename)
        # self.output = pickle.dumps(matrizSomaFinal)

        # # matrizRed3 = np.zeros(shape=(linhas,colunas))
        # # matrizGreen3 = np.zeros(shape=(linhas,colunas))
        # # matrizBlue3 = np.zeros(shape=(linhas,colunas))
        # for i in range(linhas):
        #     for j in range(colunas):
        #         matrizRed3[i][j]= array[i][j][0]
        #         matrizGreen3[i][j] = array[i][j][1]
        #         matrizBlue3[i][j] = array[i][j][2]
        #     #fim for
        # #fim for
        # sourceFinal = sourceIntermediario[0]+'SegmentadoCores.'+sourceIntermediario[1]
        # dst_filename6 = sourceFinal
        # dst_ds6 = driver.Create( dst_filename6, colunas, linhas, 3, gdal.GDT_Float32)
        # dst_ds6.GetRasterBand(1).WriteArray(matrizRed3)
        # dst_ds6.GetRasterBand(2).WriteArray(matrizGreen3)
        # dst_ds6.GetRasterBand(3).WriteArray(matrizBlue3)
        # dst_ds6.SetGeoTransform(geoTransform)
        # dst_ds6 = None

        # QMessageBox.information(self.iface.mainWindow(), 'Execucao Encerrada', 'O Plugin Concluiu Sua Execucao')

