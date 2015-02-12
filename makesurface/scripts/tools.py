class dataOutput:
    def printout(self, outval):
        import click, json
        click.echo(json.dumps(outval))
    def saveout(self, outval):
        self.data.append(outval)
    def __init__(self, savedata=False):
        if savedata:
            self.out = self.saveout
            self.data = list()
        else:
            self.out = self.printout

class rasterIndexer:
    def __init__(self, shape, bounds):
        self.shape = shape
        self.bounds = bounds
        self.xRange = bounds.right - bounds.left
        self.yRange = bounds.top - bounds.bottom

    def getIndices(self, x, y=None):
        if y == None:
            y = x[1]
            x = x[0]

        return [int((1 - (y - self.bounds.bottom) / self.yRange) * self.shape[0]),
                int(((x - self.bounds.left) / self.xRange) * self.shape[1])]

def resampleAffine(otrans, factor):
    from rasterio import Affine
    return Affine(otrans.a / float(factor),otrans.b,otrans.c,
             otrans.d,otrans.e / float(factor), otrans.f)



def fixRap(rapArr, maskPath):
    import rasterio
    import numpy as np

    with rasterio.open(maskPath, 'r') as src:
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

def quadtree(x, y, zoom):
    import numpy as np
    xA = (2 ** np.arange(zoom))[::-1]
    xA = (x / xA) % 2
    yA = (2 ** np.arange(zoom))[::-1]
    yA = (y / yA) % 2
    out = np.zeros(zoom, dtype=np.str)
    out[np.where((xA == 0) & (yA == 0))] = '0'
    out[np.where((xA == 1) & (yA == 0))] = '1'
    out[np.where((xA == 0) & (yA == 1))] = '2'
    out[np.where((xA == 1) & (yA == 1))] = '3'
    return out

if __name__ == '__main__':
    quadtree()
    rasterIndexer()
    handleGrib2()
    resampleAffine()
    zoomSmooth()