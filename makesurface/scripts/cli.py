# Skeleton of a CLI

import click

import makesurface

@click.command()
@click.argument('infile', type=str)

@click.argument('outfile', type=str)

@click.option('--band', '-b', default=1,
    help='Input band to vectorize [default = 1]')

@click.option('--classes', '-cl', default='10',
    help='Number of output classes, OR all for rounded input values (ignored if class file specified) [default = 10]')

@click.option('--classfile', '-cf', 
    help='One-line CSV of break values [default = None]')

@click.option('--weight', '-w', default=1,
    help='Weighting between equal interval and quantile breaks [default = 0.5]')

@click.option('--smoothing', '-s', type=int,
    help='Value by which to zoom and smooth the data [default = None]')

@click.option('--nodata', '-nd', default=None,
    help='Manually defined nodata value - can be any number or "min" [default = None]')

@click.option('--setnodata', '-set', default=None, type=float,
    help='Value to set nodata to (eg, if nodata / masked, set pixel to this value) [default = None]')

@click.option('--carto', '-c', is_flag=True)

@click.option('--nibble', '-n', is_flag=True,
    help='Expand mask by 1 pixel')

@click.option('--grib2', '-g', is_flag=True,
    help='Flag for processing of 0 - 360 grib2 rasters')

@click.option('--axonometrize', type=float, default=None,
    help='EXPERIMENTAL')

@click.option('--nosimple', '-ns', is_flag=True)

def cli(infile, outfile, classes, classfile, weight, smoothing, nodata, band, carto, grib2, axonometrize, nosimple, setnodata, nibble):
    """
    Vectorize a raster
    """
    makesurface.vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, band, carto, grib2, axonometrize, nosimple, setnodata, nibble)
