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

# import pickle
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
        rst_x = self.rst_ds.RasterXSize
        rst_y = self.rst_ds.RasterYSize
        bands = self.rst_ds.RasterCount
        data_rst = self.rst_ds.ReadAsArray()

        ###Realiza K-means
        kmeans = KMeans(n_clusters=self.n_clusters, init='k-means++', n_init=10)
        # KMeans()
        self.status.emit('clustering data (this may take a few minutes)... ')
        clusters = kmeans.fit_predict(data_rst.reshape(6, rst_y*rst_x).T)
        self.progress.emit(10)

        self.status.emit('applying mode filter...')
        clusters = clusters.reshape(rst_y, rst_x)
        step = 0
        for i in range(1,rst_y-1):
            for j in range(1,rst_x-1):
                retorno = stats.mode(clusters[i-1:i+2,j-1:j+2], axis=None)
                clusters[i][j]=retorno[0]
            step += 1
            self.calculate_progress(step, rst_y, 10, 30)

        self.status.emit('labelling connected components')
        segments = np.zeros(shape=(rst_y, rst_x))
        components = 0
        step = 0
        for i in np.unique(clusters):
            tmp = np.where(clusters==i, 1, 0).reshape(rst_y, rst_x)
            lbl, comp = ndimage.label(tmp)
            segments += np.ma.masked_equal(lbl, 0) + components
            components += comp
            step += 1
            self.calculate_progress(step, self.n_clusters, 40, 30)

        # import pydevd; pydevd.settrace()
        self.dst_ds.GetRasterBand(1).WriteArray(segments)
