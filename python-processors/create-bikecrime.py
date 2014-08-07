
import csv, os, fiona, json, sys, argparse
from scipy import stats
from rasterio import features, Affine
from shapely.geometry import Polygon, MultiPolygon, mapping
from fiona.crs import from_epsg
import numpy as np

parser = argparse.ArgumentParser(description='Create Density Surface from GeoJSON points.')

parser.add_argument('infile',
                    help='Input GeoJSON')

parser.add_argument('outfile',
                    help='Output Shapefile')

parser.add_argument('cellsize',
                    help='Grid size of analysis raster, in meters')

parser.add_argument('kernel',
                    help='Kernel bandwidth')

parser.add_argument('classes',
                    help='Number of output classes')

parser.add_argument('--w',
                     help='Classification weighting')

args = parser.parse_args()

cellSize = int(args.cellsize)

kernBW = float(args.kernel)

classNumber = int(args.classes)

if args.w == None:
    classWeight = 0.5
else:
    classWeight = float(args.w)

def lnglatToXY(ll):
    from math import pi, log, tan
    D2R = pi / 180.0
    A = 6378137.0
    x = (A * ll[0] * D2R)
    y = (A * log(tan((pi*0.25) + (0.5 * ll[1] * D2R))))
    return x,y

def classify(zArr,classes,weighting=0.5):
    'convert crime kernel surface into classed surface for polygonization'
    outRas = np.zeros(zArr.shape)
    zMax = zArr.max()
    zMin = zArr.min()
    zRange = zMax-zMin
    zInterval = zRange/float(classes)
    print "Classifying into "+str(classes)+" classes between "+str(zMin)+" and "+str(zMax)
    for i in range(0,classes):
        eQint = i*zInterval+zMin
        quant = np.percentile(zArr, i/float(classes)*100)
        cClass = weighting*eQint+(1.0-weighting)*quant
        outRas[np.where(zArr>cClass)] = cClass
    return ((outRas/zMax)*256).astype(np.uint8)



with open(args.infile, 'r') as pointFile:
    geojson = json.loads(pointFile.read())

xys = []

for f in geojson['features']:
    xys.append(lnglatToXY(f['geometry']['coordinates']))
del geojson

xys = np.array(xys)

xmin = xys[:,0].min()
xmax = xys[:,0].max()
ymin = xys[:,1].min()
ymax = xys[:,1].max()
X, Y = np.mgrid[xmin:xmax:cellSize, ymin:ymax:cellSize]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([xys[:,0], xys[:,1]])
del xys
print "Running gaussian kernel.."
kernel = stats.gaussian_kde(values,bw_method=kernBW)
Z = np.reshape(kernel(positions).T, X.shape)
del kernel, positions, X, Y
Ztemp = (Z*10e+10).astype(np.uint16)
del Z

print "Classifying..."
Z16 = classify(Ztemp,classNumber,classWeight)
del Ztemp
pixel_size_x = (xmax - xmin)/Z16.shape[0]
pixel_size_y = (ymax - ymin)/Z16.shape[1]
upper_left_x = xmin - pixel_size_x/2.0
upper_left_y = ymax + pixel_size_y/2.0

transform = Affine(
                pixel_size_x, 0.0, upper_left_x,
                0.0, -pixel_size_y, upper_left_y)

schema = { 'geometry': 'MultiPolygon', 'properties': { 'value': 'int' } }

print "Writing to shp..."

with fiona.collection(args.outfile, "w", "ESRI Shapefile", schema, crs=from_epsg(3857)) as outshp:
    for feature, shapes in features.shapes(np.asarray(np.rot90(Z16.astype(np.uint8)),order='C'),transform=transform):
        featurelist = []
        for f in feature['coordinates']:
            featurelist.append(Polygon(f))
        poly = MultiPolygon(featurelist)
        outshp.write({'geometry': mapping(poly),'properties': {'value': shapes}})

