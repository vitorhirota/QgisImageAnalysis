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

try:
    import cPickle as pickle
except:
    import pickle
import os
import subprocess
import sys
import tempfile
import time

from PyQt4 import QtCore
from qgis.core import *

import numpy as np
from osgeo import gdal
from sklearn.cluster import KMeans
from scipy import ndimage
from scipy import stats

import util

class Task(util.Task):
    def setup(self, *args):
        gdal.UseExceptions()
        # unpack arguments
        raster_ipt, n_clusters = args
        try:
            rst_layer = self.parent.get_layer(QgsMapLayer.RasterLayer,
                                                   raster_ipt)
        except IndexError:
            self.valid = False
            self.invalid = 'Please, set raster image.'
            return
        # open raster images
        rst_ds = gdal.Open(rst_layer.source(), gdal.GA_ReadOnly)
        # create temp output raster
        # tmp_rst = tempfile.NamedTemporaryFile()
        filename = '%s/kmeans_c%s_%s.tif' % (
                        os.path.dirname(rst_layer.source()),
                        n_clusters,
                        int(time.time())
                    )
        # calling gdal directly was crashing qgis
        subprocess.call("""%s -c "from osgeo import gdal
driver = gdal.GetDriverByName('GTiff')
dst_ds = driver.Create('%s', %s, %s, 1, gdal.GDT_UInt32)
dst_ds.SetGeoTransform(%s)
dst_ds.SetProjection('%s')
dst_ds = None"
""" % (sys.executable, filename, rst_ds.RasterXSize, rst_ds.RasterYSize,
       rst_ds.GetGeoTransform(), rst_ds.GetProjection().replace('"', '\\"')),
                        shell=True)
        self.dst_ds = gdal.Open(filename, gdal.GA_Update)

        self.worker = Worker(rst_ds, n_clusters)
        self.worker.update_raster.connect(self.update_raster)
        self.filename = filename
        self.rlayer = None

    def update_raster(self, obj):
        band = self.dst_ds.GetRasterBand(1)
        band.WriteArray(pickle.loads(str(obj)), 0, 0)
        band.FlushCache()
        band = None
        # remove/add output raster to canvas
        if self.rlayer:
            self.parent.layer_registry.removeMapLayer(self.rlayer.id())
        self.rlayer = QgsRasterLayer(self.filename,
                                     os.path.basename(self.filename))
        self.parent.layer_registry.addMapLayer(self.rlayer)


    def post_run(self, obj):
        # polygonize
        self.completed = ('completed successfully. ')


class Worker(util.Worker):
    update_raster = QtCore.pyqtSignal(str)

    def __init__(self, rst_ds, n_clusters):
        util.Worker.__init__(self)
        self.rst_ds = rst_ds
        self.n_clusters = int(n_clusters)

    @util.error_handler
    def run(self):
        rst_x = self.rst_ds.RasterXSize
        rst_y = self.rst_ds.RasterYSize
        bands = self.rst_ds.RasterCount
        data_rst = self.rst_ds.ReadAsArray()
        self.log.emit('each step may take a few minutes')

        kmeans = KMeans(n_clusters=self.n_clusters, init='k-means++', n_init=10)
        if self.abort:
            self.finished.emit(False, 'Terminated.')
            return
        self.status.emit('clustering data... ')
        clusters = kmeans.fit_predict(data_rst.reshape(6, rst_y*rst_x).T)
        clusters = clusters.reshape(rst_y, rst_x)
        self.progress.emit(15)
        self.update_raster.emit(pickle.dumps(clusters))

        self.status.emit('applying mode filter...')
        step = 0
        for i in range(1,rst_y-1):
            for j in range(1,rst_x-1):
                if self.abort:
                    self.finished.emit(False, 'Terminated.')
                    return
                retorno = stats.mode(clusters[i-1:i+2,j-1:j+2], axis=None)
                clusters[i][j]=retorno[0]
            step += 1
            if step % 10 == 0:
                self.calculate_progress(step, rst_y, 15, 50)
                self.update_raster.emit(pickle.dumps(clusters))

        self.status.emit('labelling connected components')
        segments = np.zeros(shape=(rst_y, rst_x), dtype=np.int32)
        components = 0
        step = 0
        for i in np.unique(clusters):
            if self.abort:
                self.finished.emit(False, 'Terminated.')
                return
            tmp = np.where(clusters==i, 1, 0).reshape(rst_y, rst_x)
            lbl, comp = ndimage.label(tmp)
            segments += np.ma.masked_equal(lbl, 0) + components
            components += comp
            step += 1
            self.calculate_progress(step, self.n_clusters, 65, 35)

        pickle_segments = pickle.dumps(segments)
        self.update_raster.emit(pickle_segments)
        self.output = pickle.dumps(pickle_segments)
