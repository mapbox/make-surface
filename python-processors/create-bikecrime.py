
import csv, os, fiona
from scipy import stats
from rasterio import features, Affine
from shapely.geometry import Polygon, MultiPolygon, mapping
from fiona.crs import from_epsg
import numpy as np

def latlngToXY(ll):
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
    print zMin,zMax
    for i in range(0,classes):
        eQint = i*zInterval+zMin
        quant = np.percentile(zArr, i/float(classes)*100)
        cClass = weighting*eQint+(1.0-weighting)*quant
        outRas[np.where(zArr>cClass)] = cClass
        print eQint, quant
    return ((outRas/zMax)*256).astype(np.uint8)

xys = []

sdir = '/Users/dnomadb/python-minis/data-doers/sfpd_incident_all_csv'
print "Reading file.."
for w, f in enumerate(os.listdir(sdir)):
    afile = os.path.join(sdir,f)
    year = int(f.replace('.csv','').split('_')[-1])
    with open(afile, 'r') as ofile:
        reader = csv.DictReader(ofile)
        for row in reader:
            for i in row:
                bikeEval = row[i].lower()
                if bikeEval.find('bike') != -1 or bikeEval.find('bicycle') != -1:
                    for weight in range(w+1):
                        xys.append(latlngToXY([float(row['X']), float(row['Y'])]))

xys = np.array(xys)
xys = xys[np.where(xys[:,0]<-122.0)]
xys = xys[np.where(xys[:,1]>30.0)]
xmin = xys[:,0].min()
xmax = xys[:,0].max()
ymin = xys[:,1].min()
ymax = xys[:,1].max()
X, Y = np.mgrid[xmin:xmax:50, ymin:ymax:50]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([xys[:,0], xys[:,1]])
del xys
print "Running gaussian kernel.."
kernel = stats.gaussian_kde(values,bw_method=0.05)
Z = np.reshape(kernel(positions).T, X.shape)
del kernel, positions, X, Y
Ztemp = (Z*10e+10).astype(np.uint16)
del Z
print "Classifying..."
Z16 = classify(Ztemp,50,0.4)
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

shpfile = "crimepolys-50.shp"


with fiona.collection(shpfile, "w", "ESRI Shapefile", schema, crs=from_epsg(3857)) as outshp:
    for feature, shapes in features.shapes(np.asarray(np.rot90(Z16.astype(np.uint8)),order='C'),transform=transform):
        featurelist = []
        for f in feature['coordinates']:
            featurelist.append(Polygon(f))
        poly = MultiPolygon(featurelist)
        outshp.write({'geometry': mapping(poly),'properties': {'value': shapes}});

