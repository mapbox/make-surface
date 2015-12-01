import fiona, rasterio, mercantile, tools, json, click
from rasterio import features, Affine, coords
import numpy as np

np.seterr(divide='ignore', invalid='ignore')

def filterBadJSON(feat):
    for f in feat:
        try:
            yield json.loads(f)
        except:
            pass

def getBounds(features):
    xy = np.vstack(list(f['geometry']['coordinates'][0] for f in features))
    return coords.BoundingBox(
        xy[:,0].min(),
        xy[:,1].min(),
        xy[:,0].max(),
        xy[:,1].max()
        )

def getGJSONinfo(geoJSONinfo):
    """
    Loads a lattice of GeoJSON, bounds, and creates a list mapping an on-the-fly UID w/ the actual index value.
    """
    features = list(i for i in filterBadJSON(geoJSONinfo))
    UIDs = list(feat['properties']['qt'] for feat in features)

    featDimensions = int(np.sqrt(len(features)/2.0))
    
    return features, UIDs, featDimensions

def getRasterInfo(filePath):
    """
    Load the raster, and get the crs (geoJSON needs to be projected into this crs to know what part of the raster to extract)
    """
    with rasterio.open(filePath, 'r') as src:
        return src.crs, src.bounds, src.count

def loadRaster(filePath, bands, bounds, setnodata):
    """

    """
    with rasterio.drivers():
        with rasterio.open(filePath,'r') as src:
            oaff = src.affine
            upperLeft = src.index(bounds.left, bounds.top)
            lowerRight = src.index(bounds.right, bounds.bottom)

            return np.dstack(list(
                src.read(i[1], boundless=True, out=np.zeros((lowerRight[0] - upperLeft[0], lowerRight[1] - upperLeft[1]), dtype=np.uint8) + setnodata, window=((upperLeft[0], lowerRight[0]),(upperLeft[1], lowerRight[1]))
                    ) for i in bands
                )), oaff

def addGeoJSONprop(feat, bands, rasArr, color):
    for i in bands:
        feat['properties'][i[0]] = rasArr[i[2]].item()
    if color:
        bhex = '#'
        for i in bands:
            color = hex(rasArr[i[2]].item()).replace('0x', '')
            if len(color) == 1:
                color = '0' + color
            bhex += color
        feat['properties']['color'] = bhex
    return feat

def getCenter(feat):
    point = np.array(feat)
    return np.mean(point[0:-1,0]),np.mean(point[0:-1,1])

def getData(rasArr, inds, bands, setnodata):
    try:
        return {b[0]: rasArr[inds[0], inds[1], b[2]].item() for b in bands}
    except:
        return {b[0]: setnodata for b in bands}

def getRasterValues(geoJSON, rasArr, UIDs, bounds, outputGeom, bands, color, setnodata, outGeoJSON=False):
    rasInd = tools.rasterIndexer(rasArr.shape, bounds)

    indices = list(
        rasInd.getIndices(getCenter(feat['geometry']['coordinates'][0])
        ) for feat in geoJSON)

    if outputGeom:
        if outGeoJSON:
            geoJSON = outGeoJSON
        return list(
            addGeoJSONprop(feat, bands, rasArr[indices[i][0],indices[i][1]], color) for i, feat in enumerate(geoJSON)
            )
    else: 
        return list(
            {
                'qt': UIDs[i],
                'attributes': getData(rasArr, inds, bands, setnodata)
            } for i, inds in enumerate(indices)
            )

def batchStride(output, batchsize):
    return list(
        {
            d.keys()[0]: d[d.keys()[0]] for d in output[i:i + batchsize]
        } for i in range(0, len(output), batchsize)
        )

def upsampleRaster(rasArr, featDims, zooming=None):
    from scipy.ndimage import zoom
    from math import ceil
    if zooming and type(zooming) == int:
        zoomFactor = zooming
    else:
        zoomFactor = (int(ceil(featDims / float(min(rasArr.shape[0:2])))) * 2)

    return zoom(rasArr, (zoomFactor, zoomFactor, 1), order=1)

def projectShapes(features, toCRS):
    import pyproj
    from functools import partial
    import fiona.crs as fcrs
    from shapely.geometry import shape, mapping
    from shapely.ops import transform as shpTrans

    project = partial(
        pyproj.transform,
        pyproj.Proj(fcrs.from_epsg(4326)),
        pyproj.Proj(toCRS))

    return list(
        {'geometry': mapping(
            shpTrans(
                project,
                shape(feat['geometry']))
        )} for feat in features
        )

def handleBandArgs(bands, rasBands):
    if len(bands) == 0:
        return list(
            ('band_%d' % i, i, i - 1) for i in range(1, rasBands + 1) 
            )
    else:
        return list(
            (b[1], int(b[0]), i) for i, b in enumerate(bands)
            )

def fillFacets(geoJSONpath, rasterPath, noProject, output, bands, zooming, batchprint, outputGeom, color, setnodata):
    geoJSON, uidMap, featDims = getGJSONinfo(geoJSONpath)

    rasCRS, rasBounds, rasBands = getRasterInfo(rasterPath)

    bands = handleBandArgs(bands, rasBands)

    if noProject or (hasattr(rasCRS, 'proj') and rasCRS['proj'] == 'longlat'):
        noProject = True
        bounds = getBounds(geoJSON)
    else:
        ogeoJson = geoJSON
        geoJSON = projectShapes(geoJSON, rasCRS)
        bounds = getBounds(geoJSON)

    rasArr, oaff = loadRaster(rasterPath, bands, bounds, setnodata)

    if min(rasArr.shape[0:2]) < 2 * featDims or zooming:
        rasArr = upsampleRaster(rasArr, featDims, zooming)

    if noProject:
        sampleVals = getRasterValues(geoJSON, rasArr, uidMap, bounds, outputGeom, bands, color, setnodata)
    else:
        sampleVals = getRasterValues(geoJSON, rasArr, uidMap, bounds, outputGeom, bands, color, setnodata, ogeoJson)

    if batchprint and outputGeom != True:
        sampleVals = batchStride(sampleVals, int(batchprint))

    if output:
        with open(output, 'w') as oFile:
            oFile.write(json.dumps({
                "type": "FeatureCollection",
                "features": list(sampleVals)
                }))
    else:
        for feat in sampleVals:
            try:
                click.echo(json.dumps(feat).rstrip())
            except IOError as e:
                pass