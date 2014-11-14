makesurface
===========

A few basic surface creation routines using: `rasterio`, `fiona`, and `shapely`

Installation
------------

1. Install dependencies:

- `rasterio`
- `fiona`
- `shapely`
- `scipy`
- `scikit-image`

2. Clone this repo:

`git clone git@github.com:mapbox/make-surface.git`

3. CD into `make-surface` then pip install .

Usage
------

Takes an input raster, and converts into a stacked shapefile. Sort of like `gdal polygonize` with more control. Also prints out a cartocss template for stylizing (one style for each class).

`makesurface <input raster> <output shapefile> [OPTIONS]`

Arguments

* `<input raster>` Input single-band raster to class and vectorize

* `<output shapefile>` Output shapefile to create - output will be "stacked", with lower values including areas of higher values

Options

* `--classfile <TEXT>` - Filepath to one-line CSV of manually defined break values

* `--classes <INTEGER>` (default = 10) - Number of sections to vectorize into; Ignored if `classfile` specified

* `--weight <FLOAT>` (default = 0.5) - parameter to weight classification type; 0 = quantile breaks, 1 = equal interval, anywhere between 0 and 1 weights the classification between the two; Ignored if `classfile` specified

* `--smoothing <FLOAT>` (default = no smoothing) - optional parameter that defines the kernel sigma used in a gaussian smoothing operation prior to classification; If none, no smoothing is performed

* `--nodata <ANY NUMBER OR "min">` (default = nodata from metadata) - Manually defined nodata value - can be any number or "min"

* `--help` Show this message and exit;
