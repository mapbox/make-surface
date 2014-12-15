# Skeleton of a CLI

import click

import makesurface

@click.group()
def cli():
    pass

@click.command()
@click.argument('infile', type=str)

@click.argument('outfile', type=str)

@click.option('--band', '-b', default=None,
    help='Input band to vectorize. Can be a number, or a band name [default = 1]')

@click.option('--classes', '-cl', default='10',
    help='Number of output classes, OR "all" for rounded input values (ignored if class file specified) [default = 10]')

@click.option('--classfile', '-cf', 
    help='One-line CSV of break values [default = None]')

@click.option('--weight', '-w', default=1.0,
    help='Weighting between equal interval and quantile breaks [default = 1 / equal interval]')

@click.option('--smoothing', '-s', type=int,
    help='Value by which to zoom and smooth the data [default = None]')

@click.option('--nodata', '-nd', default=None,
    help='Manually defined nodata value - can be any number or "min" [default = None]')

@click.option('--setnodata', '-set', default=None, type=float,
    help='Value to set nodata to (eg, if nodata / masked, set pixel to this value) [default = None]')

@click.option('--carto', '-c', is_flag=True)

@click.option('--nibble', '-n', is_flag=True,
    help='Expand mask by 1 pixel')

@click.option('--globewrap', '-g', is_flag=True,
    help='Flag for processing of 0 - 360 grib2 rasters')

@click.option('--rapfix', '-rf', default=None,
    help='Rap Mask - Use only for fixing RAP.grib2s')

@click.option('--axonometrize', type=float, default=None,
    help='EXPERIMENTAL')

@click.option('--nosimple', '-ns', is_flag=True)

def vectorize(infile, outfile, classes, classfile, weight, smoothing, nodata, band, carto, globewrap, axonometrize, nosimple, setnodata, nibble, rapfix):
    """
    Vectorize a raster
    """
    makesurface.vectorize(infile, outfile, classes, classfile, weight, nodata, smoothing, band, carto, globewrap, axonometrize, nosimple, setnodata, nibble, rapfix)

@click.command()
@click.option('--bbox', type=str, default=None,
    help='Bounding Box ("w s e n") to create lattice in')
@click.option('--tile', type=str, default=None,
    help='Tile ("x y z") to create lattice in')
@click.option('--output', type=str, default=None,
    help='File to write to (.geojson)')
@click.argument('zoom', type=int)
def triangulate(zoom, output, bbox, tile):
    '''
    Creates triangular lattice at specified zoom (where triangle size == tile size)'
    '''
    makesurface.triangulate(zoom, output, bbox, tile)

cli.add_command(vectorize)
cli.add_command(triangulate)