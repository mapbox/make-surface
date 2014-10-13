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

parser.add_argument('--nodata',
                     help='Forced nodata value')


args = parser.parse_args()


classNumber = int(args.classes)

if args.w == None:
    classWeight = 0.5
else:
    classWeight = float(args.w)

if args.nodata == None:
    nodata = 'none'
elif args.nodata == 'nodata':
    nodata = 'nodata'
elif args.nodata == 'min':
    nodata = 'min'
elif type(args.nodata) == int or type(args.nodata) == float:
    nodata = float(args.nodata)
else:
    nodata = 'none'
    print "invalid nodata value - ignoring"

def classify(zArr,classes,weighting=0.5):
    'convert crime kernel surface into classed surface for polygonization'
    outRas = np.empty(zArr.shape)
    zMax = np.nanmax(zArr)
    zMin = np.nanmin(zArr)
    zRange = zMax-zMin
    zInterval = zRange/float(classes)
    breaks = {}
    print "Classifying into "+str(classes)+" classes between "+str(zMin)+" and "+str(zMax)
    for i in range(0,classes):
        eQint = i*zInterval+zMin
        quant = np.percentile(zArr[np.isfinite(zArr)], i/float(classes)*100)
        cClass = weighting*eQint+(1.0-weighting)*quant
        breaks[i+1] = cClass
        outRas[np.where(zArr>cClass)] = i+1
    outRas[np.isnan(zArr)] = 0
    breaks[0] = -999

    return outRas.astype(np.uint8), breaks

with rasterio.open(args.infile,'r') as src:
    inarr = src.read_band(1)
    oshape = src.shape
    oaff = src.affine
    ocrs = src.crs['init'].split(':')[1]
    if nodata == 'min':
        inarr[np.where(inarr==inarr.min())] = None
    elif nodata == 'nodata':
        inarr[np.where(inarr==src.nodatavals[0])] = None
    elif nodata == 'none':
        pass
    else:
        inarr[np.where(inarr==nodata)] = None
    

classRas, breaks = classify(inarr,10,1)

schema = { 'geometry': 'MultiPolygon', 'properties': { 'value': 'float' } }

with fiona.collection(args.outfile, "w", "ESRI Shapefile", schema, crs=from_epsg(ocrs)) as outshp:
    tRas = np.zeros(classRas.shape,dtype=np.uint8)
    for i in range(max(breaks.keys()),0,-1):
        tRas[np.where(classRas<=i)] = 1
        tRas[np.where(classRas>i)] = 0
        tRas[np.where(classRas==0)] = 0
        for feature, shapes in features.shapes(np.asarray(tRas,order='C'),transform=oaff):
            if shapes == 1:
                featurelist = []
                for f in feature['coordinates']:
                    featurelist.append(Polygon(f))
                poly = MultiPolygon(featurelist)
                outshp.write({'geometry': mapping(poly),'properties': {'value': breaks[i]}})