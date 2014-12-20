import fiona, rasterio, mercantile, tools, json
from rasterio import features, Affine
import numpy as np
from matplotlib.pyplot import show, imshow


def getGJSONinfo(geoJSONpath):
    """
    Loads a lattice of GeoJSON, bounds, and creates a list mapping an on-the-fly UID w/ the actual index value.
    """
    with fiona.open(geoJSONpath, 'r') as gJSON:
        UIDs = list(feat['properties']['quadtree'] for feat in gJSON)
        featDimensions = int(np.sqrt(len(gJSON)/2.0))
        geoJSON = list(gJSON)
        return geoJSON, UIDs, gJSON.bounds, featDimensions

def loadRaster(filePath, band, bounds, grib2):
    with rasterio.open(filePath,'r') as src:
        rasArr = src.read_band(band)
        oaff = src.affine
        rasbounds = src.bounds
        if grib2:
            rasArr, oaff, rasbounds = tools.handleGrib2(rasArr, oaff)
        rasInd = tools.rasterIndexer(rasArr.shape, rasbounds)
        frInd = rasInd.getIndices(bounds[0], bounds[3])
        toInd = rasInd.getIndices(bounds[2], bounds[1])
        return rasArr[frInd[0]:toInd[0] + 1, frInd[1]:toInd[1] + 1], oaff, src.crs

def addGeoJSONprop(feat, propName, propValue):
    feat['properties'][propName] = propValue
    return feat

def getRasterValues(geoJSON, rasArr, oaff, UIDs, bounds, output):
    xCell = (bounds[2] - bounds[0]) / float(rasArr.shape[1])
    yCell = (bounds[3] - bounds[1]) / float(rasArr.shape[0])
    readaff = Affine(xCell, 0.00,bounds[0],
                    0.00,-yCell, bounds[3])
    sampleRaster = features.rasterize(
            ((feat['coordinates'], i) for i, feat in enumerate(geoJSON)),
            out_shape=rasArr.shape,
            transform=readaff)
    if output == 'GeoJSON':
        return {
            "type": "FeatureCollection",
            "features": list(addGeoJSONprop(feat, 'value', np.mean(rasArr[np.where(sampleRaster == i)])) for i, feat in enumerate(geoJSON))
        }
    else:
        return list({UIDs[i]:np.mean(rasArr[np.where(sampleRaster == i)])} for i, feat in enumerate(geoJSON))


def upsampleRaster(rasArr, featDims):
    from scipy.ndimage import zoom
    zoomFactor = int(featDims / min(rasArr.shape)) * 4
    return zoom(rasArr, zoomFactor, order=1)

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
        mapping(
            shpTrans(
                project,
                shape(feat['geometry']))
        ) for feat in features)

geoJSON, uidMap, bounds, featDims = getGJSONinfo('/Users/dnomadb/Documents/lattices/lattice12.geojson')

rasArr, oaff, rasCRS= loadRaster('/Users/dnomadb/Downloads/hrrr.t00z.wrfsfcf00 (2).grib2', 1, bounds, True)

geoJSON = projectShapes(geoJSON, rasCRS)

if min(rasArr.shape) < 3 * featDims:
    rasArr = upsampleRaster(rasArr, featDims)

with open('/Users/dnomadb/Documents/lattices/lattice12-vals.geojson', 'w') as oFile:
    oFile.write(json.dumps(getRasterValues(geoJSON, rasArr, oaff, uidMap, bounds, 'GeoJSON'), indent=2))