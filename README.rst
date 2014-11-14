makesurface
===========

A few basic surface creation routines using (primarily) `rasterio <https://github.com/mapbox/rasterio>`_, `fiona <https://github.com/Toblerity/Fiona>`_, and `shapely <https://github.com/Toblerity/shapely>`_

Installation
------------

.. role:: console(code)
   :language: console

1. Install dependencies:

- :console:`rasterio`
- :console:`fiona`
- :console:`shapely`
- :console:`scipy`
- :console:`scikit-image`

2. Clone this repo:

:console:`git clone git@github.com:mapbox/make-surface.git`

3. CD into :console:`make-surface` then `pip install -e .`

Alternatively, install straight from GitHub:

.. code-block:: bash

   pip install -e git+git@github.com:mapbox/make-surface.git#egg=makesurface

Usage
------

Takes an input raster, and converts into a stacked shapefile. Sort of like :console:`gdal polygonize` with more control. Also prints out a cartocss template for stylizing (one style for each class).

Turns this:

.. image:: https://cloud.githubusercontent.com/assets/5084513/5039999/fb1a75f4-6b5b-11e4-9cf8-888ace189c8c.png

Into this:

.. image:: https://cloud.githubusercontent.com/assets/5084513/5040006/29fe36c6-6b5c-11e4-8ad5-07c3edb6c66c.png

:console:`makesurface <input raster> <output shapefile> [OPTIONS]`

Arguments

* :console:`<input raster>` Input single-band raster to class and vectorize

* :console:`<output shapefile>` Output shapefile to create - output will be "stacked", with lower values including areas of higher values

Options

* :console:`--classfile <TEXT>` - Filepath to one-line CSV of manually defined break values

* :console:`--classes <INTEGER>` (default = 10) - Number of sections to vectorize into; Ignored if `classfile` specified

* :console:`--weight <FLOAT>` (default = 0.5) - parameter to weight classification type; 0 = quantile breaks, 1 = equal interval, anywhere between 0 and 1 weights the classification between the two; Ignored if `classfile` specified

* :console:`--smoothing <FLOAT>` (default = no smoothing) - optional parameter that defines the kernel sigma used in a gaussian smoothing operation prior to classification; If none, no smoothing is performed

* :console:`--nodata <ANY NUMBER OR "min">` (default = nodata from metadata) - Manually defined nodata value - can be any number or "min"

* :console:`--carto` (default = none) - Flag to include stdout printing of cartoCSS for classes

* :console:`--help` Show this message and exit;
