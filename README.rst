makesurface ``cool-tools``
==========================  

A few basic surface creation routines using (primarily) `rasterio <https://github.com/mapbox/rasterio>`_, `fiona <https://github.com/Toblerity/Fiona>`_, and `shapely <https://github.com/Toblerity/shapely>`_

.. role:: console(code)
   :language: console

Installation
------------

1. Install dependencies:

- :console:`rasterio`
- :console:`fiona`
- :console:`shapely`
- :console:`scipy`

2. Clone this repo:

:console:`git clone git@github.com:mapbox/make-surface.git`

3. CD into :console:`make-surface` then `pip install -e .`

Alternatively, install straight from GitHub:

.. code-block:: bash

   pip install -e git+git@github.com:mapbox/make-surface.git#egg=makesurface

Or, install from PyPI

.. code-block:: bash

pip install makesurface --pre

Usage - Vectorize
-----------------

:console:`makesurface vectorize <input raster> <output shapefile> [OPTIONS]`

Takes an input raster, and converts into a stacked shapefile. Sort of like :console:`gdal polygonize` with more control. Also prints out a cartocss template for stylizing (one style for each class).

Turns this:

.. image:: https://cloud.githubusercontent.com/assets/5084513/5039999/fb1a75f4-6b5b-11e4-9cf8-888ace189c8c.png

Into this:

.. image:: https://cloud.githubusercontent.com/assets/5084513/5040006/29fe36c6-6b5c-11e4-8ad5-07c3edb6c66c.png


Arguments

* :console:`<input raster>` Input single-band raster to class and vectorize

* :console:`<output shapefile>` Output shapefile to create - output will be "stacked", with lower values including areas of higher values

Options:
* :console:`-b, --band TEXT`          Input band to vectorize. Can be a number, or a band name [default = 1]
* :console:`-cl, --classes TEXT`      Number of output classes, OR "all" for rounded input values (ignored if class file specified) [default = 10]
* :console:`-cf, --classfile TEXT`    One-line CSV of break values [default = None]
* :console:`-w, --weight INTEGER`     Weighting between equal interval and quantile breaks [default = 1 / equal interval]
* :console:`-s, --smoothing INTEGER`  Value by which to zoom and smooth the data [default = None]
* :console:`-nd, --nodata TEXT`       Manually defined nodata value - can be any number or "min" [default = None]
* :console:`-set, --setnodata FLOAT`  Value to set nodata to (eg, if nodata / masked, set pixel to this value) [default = None]
* :console:`-c, --carto`
* :console:`-n, --nibble`            Expand mask by 1 pixel
* :console:`-g, --globewrap`          Flag for processing of 0 - 360 grib2 rasters
* :console:`-rf, --rapfix TEXT      Rap Mask - Use only for fixing RAP.grib2s
* :console:`--axonometrize FLOAT`     EXPERIMENTAL
* :console:`-ns, --nosimple`
* :console:`--help`                   Show this message and exit.

Usage - Triangulate
-------------------

:console:`makesurface triangulate ZOOM [OPTIONS]`

Creates an empty triangular lattice:
.. image:: https://cloud.githubusercontent.com/assets/5084513/5363377/79925be8-7f90-11e4-8cd0-86705600b983.png

Arguments:
* :console: `ZOOM` Zoom level tile size to create triangular lattice at (where triangle size == tile size at zoom)

Options:
* :console:`--bbox TEXT`    Bounding Box ("w s e n") to create lattice in
* :console:`--tile TEXT`   Tile ("x y z") to create lattice in
* :console:`--output TEXT`  File to write to (.geojson)
* :console:`--help`         Show this message and exit.

Usage - fillfacets
------------------
:console:`makesurface fillfacets [OPTIONS] INFILE SAMPLERASTER`

Use GeoJSON-like geometry to get raster values

Options:
* :console:`--output TEXT`      Write output to .json [default - print to stdout]
* :console:`--zooming INTEGER`  Manual upsampling of raster for sampling [Default = upsampling by estimated polygon density]
* :console:`-g, --globewrap`    Flag for processing of 0 - 360 grib2 rasters
* :console:`--help`             Show this message and exit.
