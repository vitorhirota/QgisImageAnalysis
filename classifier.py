# -*- coding: utf-8 -*-

#***********************************************************************
#
# Image Analysis
# ----------------------------------------------------------------------
# Label propagation with SVMs
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

import pickle
import time

from qgis.core import *

import numpy as np
from sklearn import svm
from sklearn import preprocessing

import util


class Task(util.Task):
    def setup(self, *args):
        # unpack arguments
        class_segm, class_roi, class_roi_field = args[0:3]
        svm_kernel, svm_c, svm_kgamma, svm_kdegree, svm_kcoeff = args[3:]
        try:
            self.seg_layer = self.parent.get_layer(QgsMapLayer.VectorLayer,
                                                   class_segm)
            self.roi_layer = self.parent.get_layer(QgsMapLayer.VectorLayer,
                                                   class_roi)
        except IndexError:
            self.valid = False
            self.invalid = 'Please, set segmented and roi images.'
            return
        self.svm_dict = {
            'kernel': str(svm_kernel.lower()),
            'C': float(svm_c),
            'gamma': float(svm_kgamma),
            'degree': float(svm_kdegree),
            'coef0': float(svm_kcoeff),
        }
        # setup worker
        self.worker = Worker(self.seg_layer,
                             self.roi_layer,
                             class_roi_field,
                             self.svm_dict)

    def post_run(self, obj):
        predictions = pickle.loads(obj)
        # create a new layer
        layer_crs = self.seg_layer.crs().authid()
        layer_uri = ('MultiPolygon?crs=%s&'
                     + 'field=ID:integer&field=Class:integer') % layer_crs
        layer_name = 'classification_%s_C%s_%s' % (
                        self.svm_dict['kernel'],
                        self.svm_dict['C'],
                        int(time.time())
                    )
        prediction_layer = QgsVectorLayer(layer_uri, layer_name, 'memory')
        prediction_dp = prediction_layer.dataProvider()
        # copy features
        for seg_feat in self.seg_layer.dataProvider().getFeatures():
            feat = QgsFeature()
            feat.setGeometry(seg_feat.geometry())
            feat.setAttributes([seg_feat.attributes()[0], predictions.pop(0)])
            prediction_dp.addFeatures([feat])
        self.parent.log('features: %s' % feat.attributes())
        # set same style as roi layer
        renderer = self.roi_layer.rendererV2()
        prediction_layer.setRendererV2(renderer)
        # add layer to canvas and refresh gui
        QgsMapLayerRegistry.instance().addMapLayer(prediction_layer)
        iface = self.parent.iface
        iface.legendInterface().refreshLayerSymbology(prediction_layer)
        iface.mapCanvas().refresh()

        self.completed = ('completed successfully. '
                          + 'Layer <b>%s</b> added to the canvas.' % layer_name)


class Worker(util.Worker):
    def __init__(self, seg_layer, roi_layer, roi_field, svm_dict):
        util.Worker.__init__(self)
        self.seg_layer = seg_layer
        self.roi_layer = roi_layer
        self.roi_field = roi_field
        self.svm_dict = svm_dict

    @util.error_handler
    def run(self):
        roi_data = []
        seg_data = []

        provider_roi = self.roi_layer.dataProvider()
        provider_seg = self.seg_layer.dataProvider()

        feat_seg = QgsFeature()

        self.status.emit('building spatial index')
        time.sleep(0.3)
        index = QgsSpatialIndex()
        piter = 0
        feat_count = provider_seg.featureCount()
        for f in provider_seg.getFeatures():
            seg_data.append(f.attributes()[1:])
            index.insertFeature(f)
            piter += 1
            self.progress.emit(piter * 15 / feat_count)


        self.status.emit('extracting attributes')
        self.log.emit('extracting attributes from roi segments intersection')
        time.sleep(0.3)
        # intersect roi with segments and extract attributes
        piter = 0
        feat_count = provider_roi.featureCount()
        for feat_roi in provider_roi.getFeatures():
            geom = feat_roi.geometry()
            attr_roi = feat_roi.attributes()
            intersects = index.intersects(geom.boundingBox())
            for fid in intersects:
                ffilter = QgsFeatureRequest().setFilterFid(int(fid))
                provider_seg.getFeatures(ffilter).nextFeature(feat_seg)
                # filter geometries that does not intersect
                if geom.intersects(feat_seg.geometry()):
                    attr_seg = feat_seg.attributes()
                    roi_data.append(attr_seg[1:] + attr_roi)
            # emit progress
            piter += 1
            self.progress.emit(15 + (piter * 55 / feat_count))

        # read train data
        roi_data = np.array(roi_data)
        samples = roi_data[:,:-1]
        labels = roi_data[:,-1].astype(int)
        # svm fit and predict
        self.status.emit('svm: fitting data')
        time.sleep(0.3)
        classifier = svm.SVC(**self.svm_dict)
        classifier.fit(preprocessing.scale(samples), labels)
        self.progress.emit(85)

        self.status.emit('svm: predicting labels')
        time.sleep(0.3)
        seg_data = preprocessing.scale(seg_data)
        predictions = classifier.predict(seg_data).tolist()
        self.progress.emit(100)

        self.output = pickle.dumps(predictions)

