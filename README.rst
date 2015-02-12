makesurface ``cool-tools``
==========================

Raster --> vector surface creation tools in python

Installation
------------

From GitHub:
~~~~~~~~~~~~

``pip install -e git+git@github.com:mapbox/make-surface.git#egg=makesurface``

From PyPI
~~~~~~~~~

``pip install makesurface --pre``

Manual
~~~~~~

1. Install dependencies:

'click>=3.0', 'fiona', 'numpy', 'rasterio', 'shapely', 'scipy',
'mercantile', 'pyproj'

2. Clone this repo:

:console:``git clone git@github.com:mapbox/make-surface.git``

3. cd into :console:``make-surface`` then ``pip install -e .``

Usage - Vectorize
-----------------

``makesurface vectorize [OPTIONS] INFILE``

Takes an input raster, and converts into a stacked shapefile. Sort of
like ``gdal polygonize`` with more control, optimized for vector tiles.
Also can print out a CartoCSS template for stylizing (one style for each
class).

.. figure:: https://cloud.githubusercontent.com/assets/5084513/6178638/ba760e44-b2c5-11e4-840f-a56bf8b9376f.png
   :alt: image

   image

Options:

::

      --outfile TEXT           Write to GeoJSON
      -b, --bidx INTEGER       Input band to vectorize. [default = 1]
      -cl, --classes TEXT      Number of output classes, OR "all" for rounded
                               input values (ignored if class file specified)
                               [default = 10]
      -cf, --classfile TEXT    One-line CSV of break values [default = None]
      -w, --weight FLOAT       Weighting between equal interval and quantile
                               breaks [default = 1 / equal interval]
      -s, --smoothing INTEGER  Value by which to zoom and smooth the data [default
                               = None]
      -n, --nodata TEXT        Manually defined nodata value - can be any number
                               or "min" [default = None]
      -ov, --outvar TEXT       Name of output variable [Default = value]
      -set, --setnodata FLOAT  Value to set nodata to (eg, if nodata / masked, set
                               pixel to this value) [default = None]
      -c, --carto
      -ni, --nibble            Expand mask by 1 pixel
      --axonometrize FLOAT     EXPERIMENTAL
      -ns, --nosimple
      --help                   Show this message and exit.

Usage - Triangulate
-------------------

``makesurface triangulate [OPTIONS] ZOOM``

Creates an empty triangular lattice: |image0|

::

    Options:
      --bounds FLOAT...  Bounding Box ("w s e n") to create lattice in
      --tile INTEGER...  Tile ("x y z") to create lattice in
      --output TEXT      File to write to (.geojson)
      --help             Show this message and exit.

Usage - fillfacets
------------------

``makesurface fillfacets [OPTIONS] SAMPLERASTER [INFILE]``

Use GeoJSON-like triangle geometry to get average regional raster value
for that geometry

.. figure:: https://cloud.githubusercontent.com/assets/5084513/6178628/a32990d0-b2c5-11e4-87b0-e7505c38e26f.png
   :alt: image

   image

Options:

::

      --output TEXT           Write output to .json [default - print to stdout]
      -b, --bidxs TEXT...     Band to sample [default=1]
      --zooming INTEGER       Manual upsampling of raster for sampling [Default =
                              upsampling by estimated polygon density]
      -np, --noproject        Do not project data
      -ogjs, --outputgeojson  Output updated GeoJSON
      -bp, --batchprint TEXT
      -cl, --color
      --help                  Show this message and exit.

.. |image0| image:: https://cloud.githubusercontent.com/assets/5084513/5363377/79925be8-7f90-11e4-8cd0-86705600b983.png
