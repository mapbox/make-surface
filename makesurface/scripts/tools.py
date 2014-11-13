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

def doThis(hi):
    return 'Hi %s' % (hi)