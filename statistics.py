# -*- coding: utf-8 -*-

#***********************************************************************
#
# Image Analysis
# ----------------------------------------------------------------------
# Segment statistics calculator based on raster
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

import time

from qgis.core import *

import numpy as np
from osgeo import gdal
from osgeo import ogr

import util


class Task(util.Task):
    def setup(self, *args):
        # unpack arguments
        stats_raster, stats_segm = args
        try:
            self.seg_layer = self.parent.get_layer(QgsMapLayer.VectorLayer,
                                                   stats_segm)
            self.rst_layer = self.parent.get_layer(QgsMapLayer.RasterLayer,
                                                   stats_raster)
        except IndexError:
            self.valid = False
            self.invalid = 'Please, set raster and segmented images.'
            return
        # # open images
        rst_ds = gdal.Open(self.rst_layer.source(), gdal.GA_ReadOnly)
        # setup worker
        self.worker = Worker(self.seg_layer, self.rst_layer, rst_ds)

    def post_run(self, obj):
        feat_count = obj
        self.completed = ('completed successfully. '
                          + 'Layer <b>%s</b> updated with <i>%s</i> fields.'
                          % (self.parent.stats_segm_ipt.currentText(),
                             feat_count))
        # refresh attributes & values
        self.seg_layer.updateFields()


class Worker(util.Worker):
    def __init__(self, seg_layer, rst_layer, rst_ds):
        util.Worker.__init__(self)
        self.seg_layer = seg_layer
        self.rst_layer = rst_layer
        self.rst_ds = rst_ds

    @util.error_handler
    def run(self):
        # to-do, move to init, notify user of more than 1 field
        # if len(self.seg_layer.fields) > 2:
        #     self.__log('zonal stats might already be present')
        #     # zonal stats are probably present
        #     return

        # open images, moved to task, crashed qgis
        # rst_ds = gdal.Open(self.rst_layer.source())
        rst_ds = self.rst_ds
        seg_dp = self.seg_layer.dataProvider()
        # create temporary raster off segmented image
        self.status.emit('temporary rasterizing segments.')
        time.sleep(0.5)
        args = ('', rst_ds.RasterXSize, rst_ds.RasterYSize, 1, gdal.GDT_UInt16)
        segr_ds = gdal.GetDriverByName('MEM').Create(*args)
        segr_ds.SetGeoTransform(rst_ds.GetGeoTransform())
        segr_bd = segr_ds.GetRasterBand(1)
        segr_bd.Fill(0) #initialise raster with zeros
        segr_bd.SetNoDataValue(0)
        # rasterize arguments
        seg_ds = ogr.Open(self.seg_layer.source())
        # gets the first field on seg layer to burn pixels
        attrs = ['ATTRIBUTE=%s' % seg_dp.fields()[0].name()]
        err = gdal.RasterizeLayer(segr_ds, [1], seg_ds.GetLayer(),
                                  options=attrs)
        if err:
            raise Exception("error rasterizing segments layer: %s" % err)
        self.progress.emit(15)
        segr_ds.FlushCache()

        self.status.emit('setting data up.')
        time.sleep(0.5)
        # read arrays
        data_img = rst_ds.ReadAsArray()
        data_seg = segr_ds.ReadAsArray()

        # transpose img information into a vector of band-dimensional vectors
        img_vector = data_img.transpose(1,2,0).reshape(data_seg.size,6)

        # get indices for each segment in a 1d vector
        u, indices = np.unique(data_seg, return_inverse=True)

        self.progress.emit(30)

        self.seg_layer.beginEditCommand("Statistics generation")
        try:
            # create fields
            field_names = ['avg', 'mdn', 'var']
            # type: QVariant.Double
            fields = [QgsField('_'.join([str(b+1), i]), 6, 'Real', 15, 5)
                        for b in range(rst_ds.RasterCount)
                        for i in field_names]
            seg_dp.addAttributes(fields)
            self.progress.emit(40)
            # iterate through each feature in the shp file (segment),
            # calculate zonal statistics and write to shp field
            func_names = [np.average, np.median, np.std]
            feat_count = seg_dp.featureCount()
            n_iter = 0
            self.status.emit('calculating...')
            for feat in seg_dp.getFeatures():
                segment_id = feat.attributes()[0]
                mat = np.multiply(img_vector.T, (indices == segment_id-1))
                mat = (mat.T[np.all(mat.T > 0, axis=1)]).T # filter 0 values
                stats = np.array([np.apply_over_axes(f, mat, [1]).flatten()
                                  for f in func_names]).T.flatten()
                seg_dp.changeAttributeValues({
                        feat.id(): dict(zip(range(len(feat.attributes())),
                                            [segment_id] + stats.tolist()))
                    })
                # feat.setAttributes([segment_id] + stats.tolist())

                n_iter += 1
                self.progress.emit(n_iter * 60 / feat_count + 40)
        except Exception, e:
            self.seg_layer.destroyEditCommand()
            raise e
        else:
            self.seg_layer.endEditCommand()

        self.output = str(feat_count)
        self.status.emit('Statistics generation done.')

