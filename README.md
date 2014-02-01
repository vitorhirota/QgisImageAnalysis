ImageAnalysis
=============

QGIS plugin for Image Analysis, featuring image segmentation, segment
statistics calculation and segment label propagation.

This plugin was firstly developed as separate plugins as part of a Pattern
Recognition class final project at the Applied Computation Graduation Program
at the Brazilian National Institute for Space Research (INPE).

## Dependencies

* [scikit-learn][1]

## Installation

Just download the .zip and extracts the content on your qgis plugin folder
(HOME/.qgis2/python/plugins on *NIX platforms)

## Usage

### Segmentation

Given a raster image, this method segments the image by first clustering it
with a k-means method and then labeling connected components. Output is a
shapefile with all the segments found.

### Statistics computation

After the raster image is segmented, this method computes mean, median and
standard deviation for each segment, based on all the pixels of the original
raster image that resides inside that segment. Output is saved on the .dbf
file of the segmented shapefile.

### Classification

Given a segments shapefile, and a ROIs shapefile, a SVM is trained with the
intersection of the two shapefiles, which is then used to propagate the labels
to the rest of the segments. Output is a new classified shapefile.

## License

This plugin is released under the GNU GPL License.

[1]: http://scikit-learn.org/
