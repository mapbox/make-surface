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

``makesurface vectorize <input raster> <output shapefile> [OPTIONS]``

Takes an input raster, and converts into a stacked shapefile. Sort of
like ``gdal polygonize`` with more control, optimized for vector tiles.
Also can print out a CartoCSS template for stylizing (one style for each
class).

Arguments

``<input raster>`` \| Input single-band raster to class and vectorize

``<output shapefile>`` \| Output shapefile to create - output will be
"stacked", with lower values including areas of higher values

Options:

+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| Shortcode        | Option        | Type                          | Description                                                                                     | Default              |
+==================+===============+===============================+=================================================================================================+======================+
| -b               | --bidx        | INTEGER                       | Input band to vectorize.                                                                        | 1                    |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -cl              | --classes     | TEXT                          | Number of output classes, OR "all" for rounded input values (ignored if class file specified)   | 10                   |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -cf              | --classfile   | TEXT                          | One-line CSV of break values                                                                    | None                 |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -w               | --weight      | FLOAT                         | Weighting between equal interval and quantile breaks                                            | 1 / equal interval   |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -s               | --smoothing   | INTEGER                       | Value by which to zoom and smooth the data                                                      | None                 |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -n               | --nodata      | TEXT                          | Manually defined nodata value - can be any number or "min"                                      | None                 |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -ov              | --outvar      | TEXT                          | Name of output variable                                                                         | 'value'              |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -set             | --setnodata   | FLOAT                         | Value to set nodata to (eg, if nodata / masked, set pixel to this value)                        | None                 |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -c               | --carto       | BOOLEAN                       | Flag to print out cartocss                                                                      | False                |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -ni              | --nibble      | BOOLEAN                       | Expand mask by 1 pixel                                                                          | False                |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| --axonometrize   | FLOAT         | EXPERIMENTAL                  | False                                                                                           |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| -ns              | --nosimple    | BOOLEAN                       | Don't simplify polygons                                                                         | False                |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+
| --help           |               | Show this message and exit.   |
+------------------+---------------+-------------------------------+-------------------------------------------------------------------------------------------------+----------------------+

Usage - Triangulate
-------------------

``makesurface triangulate <ZOOM> [OPTIONS]``

Creates an empty triangular lattice: |image0|

Arguments: ``<ZOOM>`` Zoom level tile size to create triangular lattice
at (where triangle size == tile size at zoom)

+------------+--------+-------------------------------------------------+
| Option     | Type   | Description                                     |
+============+========+=================================================+
| --bbox     | TEXT   | Bounding Box ("w s e n") to create lattice in   |
+------------+--------+-------------------------------------------------+
| --tile     | TEXT   | Tile ("x y z") to create lattice in             |
+------------+--------+-------------------------------------------------+
| --output   | TEXT   | File to write to (.geojson)                     |
+------------+--------+-------------------------------------------------+
| --help     |        | Show this message and exit.                     |
+------------+--------+-------------------------------------------------+

Usage - fillfacets
------------------

``makesurface fillfacets [OPTIONS] <INFILE> <SAMPLERASTER>``

Use GeoJSON-like triangle geometry to get average regional raster value
for that geometry

+-------------+-----------+------------------------------------------------------------------------------------------------+
| Option      | Type      | Description                                                                                    |
+=============+===========+================================================================================================+
| --output    | TEXT      | Write output to .json [default - print to stdout]                                              |
+-------------+-----------+------------------------------------------------------------------------------------------------+
| --zooming   | INTEGER   | Manual upsampling of raster for sampling [Default = upsampling by estimated polygon density]   |
+-------------+-----------+------------------------------------------------------------------------------------------------+
| --help      |           | Show this message and exit.                                                                    |
+-------------+-----------+------------------------------------------------------------------------------------------------+

.. |image0| image:: https://cloud.githubusercontent.com/assets/5084513/5363377/79925be8-7f90-11e4-8cd0-86705600b983.png
