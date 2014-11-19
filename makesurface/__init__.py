import fiona, json, rasterio, click
from rasterio import features, Affine
from shapely.geometry import Polygon, MultiPolygon, mapping
from fiona.crs import from_epsg
import numpy as np
from skimage.filter import gaussian_filter
from scripts import tools
import matplotlib.pyplot as plot
from scipy.ndimage import zoom


def classify(zArr, classes, weighting):
    outRas = np.zeros(zArr.shape)
    zMax = np.max(zArr)
    zMin = np.min(zArr)
    zRange = zMax-zMin
    click.echo(zRange)
    zInterval = zRange / float(classes)
    breaks = {}
    click.echo("Classifying into " + str(classes) + " classes between " + str(zMin) + " and " + str(zMax))
    for i in range(0, classes):
        eQint = i * zInterval + zMin
        quant = np.percentile(zArr[np.isfinite(zArr)], i/float(classes) * 100)
        cClass = weighting * eQint + (1.0 - weighting) * quant
        breaks[i + 1] = cClass
        outRas[np.where(zArr > cClass)] = i + 1
    outRas[np.where(zArr.mask == True)] = 0
    breaks[0] = -999
    return outRas.astype(np.uint8), breaks

def classifyAll(zArr, classes, weighting):
    outRas = np.zeros(zArr.shape)
    zMax = np.max(zArr)
    zMin = np.min(zArr)
    zRange = zMax-zMin
    classes = int(zRange)
    zInterval = zRange / float(classes)
    breaks = {}
    click.echo("Classifying into " + str(classes) + " classes between " + str(zMin) + " and " + str(zMax))
    for i in range(0, classes):
        cClass = int(i * zInterval + zMin)
        breaks[i + 1] = cClass
        outRas[np.where(zArr > cClass)] = i + 1
    outRas[np.where(zArr.mask == True)] = 0
    breaks[0] = -999
    return outRas.astype(np.uint8), breaks

def classifyManual(zArr, classArr):
    outRas = np.zeros(zArr.shape)
    breaks = {}
    click.echo("Manually Classifiying into ")
    for i in range(len(classArr)):
        breaks[i + 1] = float(classArr[i])
        outRas[np.where(zArr > classArr[i])] = i + 1
    outRas[np.where(zArr.mask == True)] = 0
    breaks[0] = -999
    return outRas.astype(np.uint8), breaks

def vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, band, cartoCSS, grib2):
    with rasterio.open(infile, 'r') as src:
        inarr = src.read_band(band)
        oshape = src.shape
        oaff = src.affine
        if 'init' in src.crs:
            ocrs = from_epsg(src.crs['init'].split(':')[1])
        elif 'a' in src.crs:
            ocrs = src.crs
        else:
            ocrs = from_epsg(4326)
        simplest = ((src.bounds.top - src.bounds.bottom) / float(src.shape[0]))
        if nodata == 'min':
            inarr[np.where(inarr == inarr.min())] = None
        elif nodata == 'nodata':
            inarr[np.where(inarr == src.nodatavals[0])] = None
        elif nodata == None:
            pass
        else:
            inarr[np.where(inarr == nodata)] = None
    
    zoomReg = zoom(inarr.data, 3, order=0)
    zoomed = zoom(inarr.data, 3, order=1)
    zoomMask = zoom(inarr.mask, 3, order=0)
    zoomed[np.where(zoomed > inarr.max())] = inarr.max()
    zoomed[np.where(zoomed < inarr.min())] = inarr.min()
    inarr = np.ma.array(zoomed, mask=zoomMask)
    oaff = tools.resampleAffine(oaff, 3)

    if grib2:
        inarr, oaff = tools.handleGrib2(inarr, oaff)

    if smoothing:
        click.echo('Pre-smoothing raster w/ sigma of '+ str(smoothing))
        inarr = gaussian_filter(inarr.astype(np.float64), sigma=smoothing)

    if classfile:
        with open(classfile, 'r') as ofile:
            classifiers = ofile.read().split(',')
            classRas, breaks = classifyManual(inarr, np.array(classifiers).astype(inarr.dtype))
    else:
        classRas, breaks = classify(inarr, classes, weight)

    if cartoCSS:
        for i in breaks:
            click.echo('[value = ' + str(breaks[i]) + '] { polygon-fill: @class' + str(i) + '}')

    schema = { 'geometry': 'MultiPolygon', 'properties': { 'value': 'float' } }

    with fiona.collection(outfile, "w", "ESRI Shapefile", schema, crs=ocrs) as outshp:
        tRas = np.zeros(classRas.shape, dtype=np.uint8)
        for i in range(1, max(breaks.keys()) + 1):
            click.echo("Simplifying " + str(breaks[i]))
            tRas[np.where(classRas>=i)] = 1
            tRas[np.where(classRas<i)] = 0
            if nodata:
                tRas[np.where(classRas == 0)] = 100
            for feature, shapes in features.shapes(np.asarray(tRas,order='C'),transform=oaff):
                if shapes == 1:
                    featurelist = []
                    for c, f in enumerate(feature['coordinates']):
                        if len(f) > 5 or c == 0:
                            poly = Polygon(f)#.simplify(simplest, preserve_topology=True)
                            featurelist.append(poly)
                    if len(featurelist) != 0:
                        oPoly = MultiPolygon(featurelist)
                        outshp.write({'geometry': mapping(oPoly),'properties': {'value': breaks[i]}})