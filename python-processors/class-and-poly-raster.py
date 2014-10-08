import csv, os, fiona, json, sys, argparse
from rasterio import features, Affine
import rasterio
from shapely.geometry import Polygon, MultiPolygon, mapping
from fiona.crs import from_epsg
import numpy as np

parser = argparse.ArgumentParser(description='Classify and vectorize a singleband raster.')

parser.add_argument('infile',
                    help='Input Raster')

parser.add_argument('outfile',
                    help='Output Shapefile')

parser.add_argument('classes',
                    help='Number of output classes')

parser.add_argument('--w',
                     help='Classification weighting - 0=quantile, 1=equal interval, weighting between')

parser.add_argument('--min',
                     help='Forced minimum value')

args = parser.parse_args()


classNumber = int(args.classes)

if args.w == None:
    classWeight = 0.5
else:
    classWeight = float(args.w)

def classify(zArr,classes,weighting=0.5,forceMin=0):
    'convert crime kernel surface into classed surface for polygonization'
    outRas = np.zeros(zArr.shape)
    zMax = zArr.max()
    if forceMin != 0:
        zMin = zArr.min()
    else:
        zMin = 0
        zArr[np.where(zArr<0)] = 0.0
    zRange = zMax-zMin
    zInterval = zRange/float(classes)
    breaks = {}
    print "Classifying into "+str(classes)+" classes between "+str(zMin)+" and "+str(zMax)
    for i in range(0,classes):
        eQint = i*zInterval+zMin
        quant = np.percentile(zArr, i/float(classes)*100)
        cClass = weighting*eQint+(1.0-weighting)*quant
        breaks[i] = cClass
        outRas[np.where(zArr>cClass)] = i
    return outRas.astype(np.uint8), breaks


with rasterio.open(args.infile,'r') as src:
    inarr = src.read_band(1)
    oshape = src.shape
    oaff = src.affine
    ocrs = src.crs['init'].split(':')[1]

if args.min == None:
    forceMin = inarr.min()
else:
    forceMin = float(args.min)
    
classRas, breaks = classify(inarr,20,1,forceMin)

schema = { 'geometry': 'MultiPolygon', 'properties': { 'value': 'float' } }

print "Writing to shp..."

with fiona.collection(args.outfile, "w", "ESRI Shapefile", schema, crs=from_epsg(ocrs)) as outshp:
    for feature, shapes in features.shapes(np.asarray(classRas,order='C'),transform=oaff):
        featurelist = []
        for f in feature['coordinates']:
            featurelist.append(Polygon(f))
        poly = MultiPolygon(featurelist)
        outshp.write({'geometry': mapping(poly),'properties': {'value': breaks[shapes]}})