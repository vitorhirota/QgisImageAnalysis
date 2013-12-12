ImageClassifier
===============

QGIS plugin for semi-automatic image classification using SVM.

## Dependencies

* [pyshp][1]
* [scikit-learn][2]

## Installation

Just download the .zip and extracts the content on your qgis plugin folder (usually HOME/.qgis2/python/plugins)

## Usage

The plugin classifies segments, instead of a raster image.

It works with the given inputs:

* raster image
* segmented shapefile
* ROIs shapefile

The raster image is just used for generating statistics for each segment (mean, median, standard deviation), in case needed, and saving the data to the segmented shapefile.

ROIs can be hand created, and need to have a column containing a given numerical class.

The plugin will then intersect roi polygons with the segments to train an SVM.

## License

This plugin is released under the MIT License.

[1]: http://code.google.com/p/pyshp/
[2]: http://scikit-learn.org/
