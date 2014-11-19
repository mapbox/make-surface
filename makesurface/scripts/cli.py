# Skeleton of a CLI

import click

import makesurface

@click.command()
@click.argument('infile', type=str)
@click.argument('outfile', type=str)
@click.option('--band', default=1,
    help='Input band to vectorize [default = 1]')
@click.option('--classes', default='10',
    help='Number of output classes, OR all for rounded input values (ignored if class file specified) [default = 10]')
@click.option('--classfile',
    help='One-line CSV of break values [default = None]')
@click.option('--weight', default=0.5,
    help='Weighting between equal interval and quantile breaks [default = 0.5]')
@click.option('--smoothing', type=int,
    help='Value by which to zoom and smooth the data [default = None]')
@click.option('--nodata', default=None,
    help='Manually defined nodata value - can be any number or "min" [default = None]')
@click.option('--carto', is_flag=True)
@click.option('--grib2', is_flag=True,
    help='Flag for processing of 0 - 360 grib2 rasters')
def cli(infile, outfile, classes, classfile, weight, smoothing, nodata, band, carto, grib2):
    """
    Vectorize a raster
    """
    try:
        classes = int(classes)
    except:
        pass
    makesurface.vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, band, carto, grib2)