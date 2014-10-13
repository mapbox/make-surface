# python-processors

A few basic surface creation routines using `rasterio`, `fiona`, and `shapely`

## class-and-poly-raster.py

Takes an input raster, and converts into a stacked shapefile. Sort of like `gdal polygonize` with more control.

### Usage

`python class-and-poly-raster.py <input raster> <output shapefile> <number of classes> --w <weighting> --nodata <nodatatype>`

* `<input raster>` Input single-band raster to class and vectorize

* `<output shapefile>` Output shapefile to create - output will be "stacked", with lower values including areas of higher values

* `<number of classes>` Number of sections to vectorize into

* `--w <weighting>` (default = 0.5) - optional parameter to weight classification type. 0 = quantile breaks, 1 = equal interval, anywhere between 0 and 1 weights the classification between the two

* `--nodata <nodatatype>` How to treat nodata. Default = None. Valid options:
 *`min` Uses minimum value from dataset
 * `nodata` Uses nodata value derived from metadata (note - is many times incorrect)
 * Any float or integer value

