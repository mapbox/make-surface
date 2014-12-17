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
        return rasArr[frInd[0]:toInd[0] + 1, frInd[1]:toInd[1] + 1], oaff

def getRasterValues(geoJSONpath, rasArr, oaff, UIDs, bounds):
    with fiona.open(geoJSONpath, 'r') as gJSON:
        xCell = (bounds[2] - bounds[0]) / float(rasArr.shape[1])
        yCell = (bounds[3] - bounds[1]) / float(rasArr.shape[0])
        readaff = Affine(xCell, 0.00,bounds[0],
                        0.00,-yCell, bounds[3])
        sampleRaster = features.rasterize(
                ((feat['geometry'], i) for i, feat in enumerate(gJSON)),
                out_shape=rasArr.shape,
                transform=readaff)
    return list({UIDs[i]:np.mean(rasArr[np.where(sampleRaster == i)])} for i in range(len(UIDs)))
    

def upsampleRaster(rasArr, featDims):
    from scipy.ndimage import zoom
    zoomFactor = int(featDims / min(rasArr.shape)) * 4
    return zoom(rasArr, zoomFactor, order=1)

uidMap, bounds, featDims = getGJSONinfo('/Users/dnomadb/Documents/lattices/lattice12.geojson')

rasArr, oaff = loadRaster('/Users/dnomadb/Downloads/gfs.t18z.mastergrb2f00', 1, bounds, True)

if min(rasArr.shape) < 3 * featDims:
    rasArr = upsampleRaster(rasArr, featDims)

print json.dumps(getRasterValues('/Users/dnomadb/Documents/lattices/lattice12.geojson', rasArr, oaff, uidMap, bounds), indent=2)
