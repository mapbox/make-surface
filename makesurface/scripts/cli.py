# Skeleton of a CLI

import click

import makesurface

@click.command()
@click.argument('infile', type=str)
@click.argument('outfile', type=str)
@click.option('--classes', default=10,
    help='Number of output classes (ignored if class file specified)')
@click.option('--classfile',
    help='One-line CSV of break values')
@click.option('--weight', default=0.5,
    help='Weighting between equal interval and quantile breaks')
@click.option('--smoothing', type=float,
    help='Sigma for optional gaussian smoothing (default = no smoothing)')
@click.option('--nodata', default=None,
    help='Manually defined nodata value - can be any number or "min"')
def cli(infile, outfile, classes, classfile, weight, smoothing, nodata):
    """
    Vectorize a raster
    """
    ## Input handling
    if nodata:
        try:
            nodata = float(nodata)
        except:
            pass
        if type(nodata) != float and nodata != 'min' and nodata != 'nodata':
            click.echo('Invalid nodata value of ' + str(nodata) + ' - ignoring')
            nodata = None
    makesurface.vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing)