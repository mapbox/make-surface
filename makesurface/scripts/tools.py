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

def handleGrib2(gribArr, otrans):
    from rasterio import Affine
    import numpy as np
    outAff = Affine(otrans.a,otrans.b,otrans.c - 180.0,
             otrans.d,otrans.e,otrans.f)
    oshape = gribArr.shape
    fixGrib = np.hstack((gribArr[0:-1, oshape[1] / 2:-1],gribArr[0:-1, 0:oshape[1] / 2]))
    return fixGrib, outAff

if __name__ == '__main__':
    rasterIndexer()
    handleGrib2()