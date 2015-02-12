# Skeleton of a CLI

import click

import makesurface

@click.group()
def cli():
    pass

@click.command()
@click.argument('infile', type=str)
@click.option('--outfile', type=str, default=False,
    help='Write to GeoJSON')
@click.option('--bidx', '-b', default=1,
    help='Input band to vectorize. [default = 1]')
@click.option('--classes', '-cl', default='10',
    help='Number of output classes, OR "all" for rounded input values (ignored if class file specified) [default = 10]')
@click.option('--classfile', '-cf', 
    help='One-line CSV of break values [default = None]')
@click.option('--weight', '-w', default=1.0,
    help='Weighting between equal interval and quantile breaks [default = 1 / equal interval]')
@click.option('--smoothing', '-s', type=int,
    help='Value by which to zoom and smooth the data [default = None]')
@click.option('--nodata', '-n', default=None,
    help='Manually defined nodata value - can be any number or "min" [default = None]')
@click.option('--outvar', '-ov', default='value',
    help='Name of output variable [Default = value]')
@click.option('--setnodata', '-set', default=None, type=float,
    help='Value to set nodata to (eg, if nodata / masked, set pixel to this value) [default = None]')
@click.option('--carto', '-c', is_flag=True)
@click.option('--nibble', '-ni', is_flag=True,
    help='Expand mask by 1 pixel')
@click.option('--axonometrize', type=float, default=None,
    help='EXPERIMENTAL')
@click.option('--nosimple', '-ns', is_flag=True)

def vectorize(infile, outfile, classes, classfile, weight, smoothing, nodata, bidx, carto, axonometrize, nosimple, setnodata, nibble, outvar):
    """
    Vectorize a raster
    """
    makesurface.vectorize(infile, outfile, classes, classfile, weight, nodata, smoothing, bidx, carto, axonometrize, nosimple, setnodata, nibble, outvar)

@click.command()
@click.option('--bounds', nargs=4, type=float, default=None,
    help='Bounding Box ("w s e n") to create lattice in')
@click.option('--tile', nargs=3, type=int, default=None,
    help='Tile ("x y z") to create lattice in')
@click.option('--output', type=str, default=None,
    help='File to write to (.geojson)')
@click.argument('zoom', type=int)

def triangulate(zoom, output, bounds, tile):
    """
    Creates triangular lattice at specified zoom (where triangle size == tile size)'
    """
    makesurface.triangulate(zoom, output, bounds, tile)

@click.command()
@click.argument('sampleraster', type=click.Path(exists=True))
@click.argument('infile', default='-', required=False)
@click.option('--output', type=str, default=None,
    help='Write output to .json [default - print to stdout]')
@click.option('--bidxs', '-b', type=str, nargs=2, multiple=True,
    help='Band to sample [default=1]')
@click.option('--zooming', type=int, default=None,
    help='Manual upsampling of raster for sampling [Default = upsampling by estimated polygon density]')
@click.option('--noproject', '-np', is_flag=True,
    help='Do not project data')
@click.option('--outputgeojson', '-ogjs', is_flag=True, default=False,
    help='Output updated GeoJSON')
@click.option('--batchprint', '-bp', default=None)
@click.option('--color', '-cl', default=False, is_flag=True)

def fillfacets(infile, sampleraster, output, noproject, bidxs, zooming, batchprint, outputgeojson, color):
    """
    Use GeoJSON-like geometry to get raster values
    """
    try:
        input = click.open_file(infile).readlines()
    except IOError:
        input = [infile]

    makesurface.fillfacets(input, sampleraster, noproject, output, bidxs, zooming, batchprint, outputgeojson, color)

cli.add_command(vectorize)
cli.add_command(triangulate)
cli.add_command(fillfacets)
