import fiona, argparse
from rasterio import features
import rasterio as rio
import numpy as np

parser = argparse.ArgumentParser(description='Create Density Surface from GeoJSON points.')

parser.add_argument('infile',
                    help='Input Raster')

parser.add_argument('inshp',
                    help='Input Shapefile')


parser.add_argument('field',
                    help='Input Shapefile')

args = parser.parse_args()

src = rio.open(args.infile,'r')
nir = src.read_band(4)
oshape = src.shape
otrans = src.transform
src.close()
fields = []
with fiona.collection(args.inshp, "r") as shp:
    for feat in shp:
        fields.append(feat['properties'][args.field])
    rasters = features.rasterize(((feat['geometry'],feat['properties'][args.field]) for feat in shp),
        out_shape=oshape,
        transform=otrans)

fields = list(set(fields))

out = {}

for i in fields:
    valuearr = nir[np.where(rasters == i)]
    out[i] = valuearr.ravel()

print out


