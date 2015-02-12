import fiona, json, rasterio, click
from rasterio import features, Affine
from shapely.geometry import Polygon, MultiPolygon, mapping
from fiona.crs import from_epsg
import numpy as np
import tools
from scipy.ndimage import zoom
from scipy.ndimage.filters import median_filter, maximum_filter

def classify(inArr, classes, weighting):
    outRas = np.zeros(inArr.shape, dtype=np.uint8)
    zMax = np.max(inArr)
    zMin = np.min(inArr)

    if weighting == 1:
        tempArray = np.zeros(1)
    else:
        tempArray = np.copy(inArr.data)
        tempArray[np.where(inArr.mask == True)] = None
    zRange = zMax-zMin
    zInterval = zRange / float(classes)
    breaks = []

    for i in range(classes):
        eQint = i * zInterval + zMin
        if weighting == 1:
            quant = 0
        else:
            quant = np.percentile(tempArray[np.isfinite(tempArray)], i/float(classes) * 100)
        cClass = weighting * eQint + (1.0 - weighting) * quant
        breaks.append(cClass)
        outRas[np.where(inArr > cClass)] = i
    outRas[np.where(inArr.mask == True)] = 0
    del tempArray

    return outRas.astype(np.uint8), breaks

def classifyAll(inArr):
    outRas = np.zeros(inArr.shape, dtype=np.uint8)
    zMax = np.max(inArr)
    zMin = np.min(inArr)
    zRange = zMax-zMin
    classes = int(zRange)
    zInterval = zRange / float(classes)
    
    outRas += 1
    breaks = [int(zMin)]
    for i in range(1, classes):
        cClass = int(i * zInterval + zMin)
        breaks.append(cClass)
        outRas[np.where(inArr >= cClass)] = i + 1
    outRas[np.where(inArr.mask == True)] = 0
    return outRas.astype(np.uint8), breaks

def classifyManual(inArr, classArr):
    outRas = np.zeros(inArr.shape)
    breaks = {}
    for i in range(len(classArr)):
        breaks[i + 1] = float(classArr[i])
        outRas[np.where(inArr >= classArr[i])] = i + 1
    outRas[np.where(inArr.mask == True)] = 0
    breaks[0] = -999
    return outRas.astype(np.uint8), breaks

def zoomSmooth(inArr, smoothing, inAffine):
    zoomReg = zoom(inArr.data, smoothing, order=0)
    zoomed = zoom(inArr.data, smoothing, order=1)
    zoomMask = zoom(inArr.mask, smoothing, order=0)
    zoomed[np.where(zoomed > inArr.max())] = inArr.max()
    zoomed[np.where(zoomed < inArr.min())] = inArr.min()
    inArr = np.ma.array(zoomed, mask=zoomMask)
    oaff = tools.resampleAffine(inAffine, smoothing)
    del zoomed, zoomMask
    return inArr, oaff

def vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, band, cartoCSS, axonometrize, nosimple, setNoData, nibbleMask, outvar):

    with rasterio.drivers():
        with rasterio.open(infile, 'r') as src:
            try:
                band = int(band)
            except:
                raise ValueError('Band must be an integer')

            inarr = src.read_band(band)
            oshape = src.shape
            oaff = src.affine

            if (type(setNoData) == int or type(setNoData) == float) and hasattr(inarr, 'mask'):
                inarr[np.where(inarr.mask == True)] = setNoData
                nodata = True

            simplest = ((src.bounds.top - src.bounds.bottom) / float(src.shape[0]))

            if nodata == 'min':
                maskArr = np.zeros(inarr.shape, dtype=np.bool)
                maskArr[np.where(inarr == inarr.min())] = True
                inarr = np.ma.array(inarr, mask=maskArr)
                del maskArr
            elif type(nodata) == int or type(nodata) == float:
                maskArr = np.zeros(inarr.shape, dtype=np.bool)
                maskArr[np.where(inarr == nodata)] = True
                inarr = np.ma.array(inarr, mas=maskArr)
                del maskArr
            elif src.meta['nodata'] == None or np.isnan(src.meta['nodata']) or nodata:
                maskArr = np.zeros(inarr.shape, dtype=np.bool)
                inarr = np.ma.array(inarr, mask=maskArr)
                del maskArr
            elif (type(src.meta['nodata']) == int or type(src.meta['nodata']) == float) and hasattr(inarr, 'mask'):
                nodata = True

            if nibbleMask:
                inarr.mask = maximum_filter(inarr.mask, size=3)

    if smoothing and smoothing > 1:
        inarr, oaff = zoomSmooth(inarr, smoothing, oaff)

    else:
        smoothing = 1

    if classfile:
        with open(classfile, 'r') as ofile:
            classifiers = ofile.read().split(',')
            classRas, breaks = classifyManual(inarr, np.array(classifiers).astype(inarr.dtype))
    elif classes == 'all':
        classRas, breaks = classifyAll(inarr)
    else:
        classRas, breaks = classify(inarr, int(classes), weight)

    # filtering for speckling
    classRas = median_filter(classRas, size=2)

    # print out cartocss for classes
    if cartoCSS:
        for i in breaks:
            click.echo('[value = ' + str(breaks[i]) + '] { polygon-fill: @class' + str(i) + '}')

    if outfile:
        outputHandler = tools.dataOutput(True)
    else:
        outputHandler = tools.dataOutput()

    for i, br in enumerate(breaks): 
        tRas = (classRas >= i).astype(np.uint8)
        if nodata:
            tRas[np.where(classRas == 0)] = 0
        for feature, shapes in features.shapes(np.asarray(tRas,order='C'),transform=oaff):
            if shapes == 1:
                featurelist = []
                for c, f in enumerate(feature['coordinates']):
                    if len(f) > 5 or c == 0:
                        if axonometrize:
                            f = np.array(f)
                            f[:,1] += (axonometrize * br)
                        if nosimple:
                             poly = Polygon(f)
                        else:
                            poly = Polygon(f).simplify(simplest / float(smoothing), preserve_topology=True)
                        featurelist.append(poly)
                if len(featurelist) != 0:
                    oPoly = MultiPolygon(featurelist)
                    outputHandler.out({
                        'type': 'Feature',
                        'geometry': mapping(oPoly),
                        'properties': {
                            outvar: br
                        }
                        })
    if outfile:
        with open(outfile, 'w') as ofile:
            ofile.write(json.dumps({
                "type": "FeatureCollection",
                "features": outputHandler.data
            }))