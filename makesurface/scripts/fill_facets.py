import fiona, rasterio, mercantile, tools, json, click
from rasterio import features, Affine
import numpy as np

def getGJSONinfo(geoJSONpath):
    """
    Loads a lattice of GeoJSON, bounds, and creates a list mapping an on-the-fly UID w/ the actual index value.
    """
    with fiona.open(geoJSONpath, 'r') as gJSON:
        UIDs = list(feat['properties']['quadtree'] for feat in gJSON)
        featDimensions = int(np.sqrt(len(gJSON)/2.0))
        geoJSON = list(gJSON)
        return geoJSON, UIDs, gJSON.bounds, featDimensions

def getRasterInfo(filePath):
    """
    Load the raster, and get the crs (geoJSON needs to be projected into this crs to know what part of the raster to extract)
    """
    with rasterio.open(filePath, 'r') as src:
        return src.crs, src.bounds

def loadRaster(filePath, band, bounds):
    """

    """
    with rasterio.drivers():
        with rasterio.open(filePath,'r') as src:
            rasArr = src.read_band(band)

            oaff = src.affine
            rasbounds = src.bounds

            rasInd = tools.rasterIndexer(rasArr.shape, rasbounds)
            frInd = rasInd.getIndices(bounds[0], bounds[3])
            toInd = rasInd.getIndices(bounds[2], bounds[1])
            return rasArr[frInd[0]:toInd[0] + 1, frInd[1]:toInd[1] + 1], oaff

def addGeoJSONprop(feat, propName, propValue):
    feat['properties'][propName] = propValue
    return feat

def getCenter(feat):
    point = np.array(feat)
    return np.mean(point[0:-1,0]), np.mean(point[0:-1,1])

def getRasterValues(geoJSON, rasArr, UIDs, bounds):

    rasInd = tools.rasterIndexer(rasArr.shape, bounds)
    indices = list(rasInd.getIndices(getCenter(feat['geometry']['coordinates'][0])) for feat in geoJSON)

    return list({UIDs[i]: rasArr[inds[0], inds[1]]} for i, inds in enumerate(indices))



def upsampleRaster(rasArr, featDims, densify=None):
    from scipy.ndimage import zoom
    if densify and type(densify) == int:
        zoomFactor = densify
    else:
        zoomFactor = int(featDims / min(rasArr.shape)) * 4
    return zoom(rasArr, zoomFactor, order=1)

def projectBounds(bbox, toCRS):
    import pyproj
    toProj = pyproj.Proj(toCRS)
    xCoords = (bbox[0], bbox[2], bbox[2], bbox[0])
    yCoords = (bbox[1], bbox[1], bbox[3], bbox[1])
    outBbox = toProj(xCoords, yCoords)
    return (min(outBbox[0]),
            min(outBbox[1]),
            max(outBbox[0]),
            max(outBbox[1]))

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
        )} for feat in features)

def fillFacets(geoJSONpath, rasterPath, globeWrap, output, densify=False):

    geoJSON, uidMap, bounds, featDims = getGJSONinfo(geoJSONpath)

    rasCRS, rasBounds = getRasterInfo(rasterPath)

    if globeWrap:
        pass
    else:
        geoJSON = projectShapes(geoJSON, rasCRS)
        bounds =  projectBounds(bounds, rasCRS)

    rasArr, oaff = loadRaster(rasterPath, 1, bounds)

    if min(rasArr.shape) < 3 * featDims or densify:
        rasArr = upsampleRaster(rasArr, featDims, densify)

    sampleVals = getRasterValues(geoJSON, rasArr, uidMap, rasBounds)

    if output:
        with open(output, 'w') as oFile:
            oFile.write(json.dumps(sampleVals, indent=2))
    else:
        click.echo(json.dumps(sampleVals, indent=2))