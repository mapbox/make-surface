class rasterIndexer:
    def __init__(self, shape, bounds):
        self.shape = shape
        self.bounds = bounds
        self.xRange = bounds.right - bounds.left
        self.yRange = bounds.top - bounds.bottom
        self.cellSizeX = (self.xRange) / shape[1]
        self.cellSizeY = (self.yRange) / shape[0]

    def getIndices(self, x, y):
        return [int(((1 - y - self.bounds.bottom) / self.yRange) * self.shape[0]),
                int(((x - self.bounds.left) / self.xRange) * self.shape[1])]

def resampleAffine(otrans, factor):
    from rasterio import Affine
    return Affine(otrans.a / float(factor),otrans.b,otrans.c,
             otrans.d,otrans.e / float(factor), otrans.f)

def handleGrib2(gribArr, otrans):
    from rasterio import Affine
    import numpy as np
    from scipy.ndimage import zoom

    gribArr = zoom(gribArr, 2, order=1)
    outAff = Affine(otrans.a / 2.0, otrans.b,otrans.c - 180.0 + (otrans.a / 2.0),
             otrans.d,otrans.e / 2.0, otrans.f)
    oshape = gribArr.shape
    fixGrib = np.hstack((gribArr[:, oshape[1] / 2 + 1:oshape[1]],gribArr[:, 0:oshape[1] / 2 + 1]))

    return fixGrib, outAff

def fixRap(rapArr, maskPath):
    import rasterio
    import numpy as np

    with rasterio.open('/Users/dnomadb/satellite-lcc/sampler/mask.tif', 'r') as src:
        maskBand = src.read_band(1)
        rapArr.mask[np.where(maskBand == 0)] = True
    
    return rapArr.mask

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

if __name__ == '__main__':
    rasterIndexer()
    handleGrib2()
    resampleAffine()
    zoomSmooth()