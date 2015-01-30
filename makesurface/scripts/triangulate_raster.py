import rasterio, mercantile, json, click, sys
import tools
import numpy as np

coordOrd = {
    False: [
               [0, 2, 3, 0],
               [0, 2, 1, 0]
            ],
    True: [
               [3, 1, 2, 3],
               [3, 1, 0, 3]
            ]
    }

class facetParent:
    def __init__(self):   
        self.dirMap = {
                       'n': 0,
                       's': 1
        }
        self.relInd = {
                       (True, True) : 0,
                       (False, True) : 1,
                       (True, False) : 2,
                       (False, False) : 3
                       }
        self.dirTree = {
            True: (
                ('n', 's'),
                ('n', 'n'),
                ('s', 's'),
                ('n', 's')
                ),
            False: (
                ('n', 'n'),
                ('n', 's'),
                ('n', 's'),
                ('s', 's')
                )
            }
    def getParents(self, direction, x, y, z):
        dirs = []
        for zoom in range(z):
            orientation = (x / 2 + y / 2) % 2 == 0
            direction = self.dirTree[orientation][self.relInd[x % 2 == 0, y % 2 == 0]][self.dirMap[direction]]
            dirs.append(direction)
            x = x / 2
            y = y / 2
        return list(reversed(dirs))

def getCorners(bounds, boolKey):
    corners = np.array([
        [bounds.west, bounds.south],
        [bounds.east, bounds.south],
        [bounds.east, bounds.north],
        [bounds.west, bounds.north]
        ])

    return [
        corners[coordOrd[boolKey][0]],
        corners[coordOrd[boolKey][1]]
    ]

def createFacets(tileMin, tileMax, zoom, parentGet):
    for r in range(tileMin.y, tileMax.y + 1):
        for c in range(tileMin.x, tileMax.x + 1):
            quad = tools.quadtree(c, r, zoom)
            boolKey = (r+c) % 2 == 0
            n = parentGet.getParents('n', c, r, zoom)
            s = parentGet.getParents('s', c, r, zoom)
            coords = getCorners(mercantile.bounds(c, r, zoom), boolKey)
            nQT = ''.join(np.dstack((n, quad)).flatten()) + 'n'
            sQT = ''.join(np.dstack((s, quad)).flatten()) + 's'

            yield {
                "type": "Feature",
                "properties": {
                    "quadtree": nQT
                    },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords[0].tolist()]
                    }
                }
            yield {
                "type": "Feature",
                "properties": {
                    "quadtree": sQT,
                    },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords[1].tolist()]
                    }
                }

def triangulate(zoom, output, bounds=None, tile=None):
    if bounds:
        bounds = np.array(bounds).astype(np.float64)
    elif tile:
        epsilon = 1.0e-10
        tile = np.array(tile).astype(np.uint16)
        tBounds = mercantile.bounds(*tile)
        bounds = np.array([
            tBounds.west + epsilon,
            tBounds.south + epsilon,
            tBounds.east - epsilon,
            tBounds.north - epsilon
            ])
    else:
        sys.exit('Error: A bounds or tile must be specified')

    tileMin = mercantile.tile(bounds[0], bounds[3], zoom)
    tileMax = mercantile.tile(bounds[2], bounds[1], zoom)

    pGet = facetParent()

    gJSON = createFacets(tileMin, tileMax, zoom, pGet)

    if output:
        with open(output, 'w') as oFile:
            for feat in gJSON:
                oFile.write(json.dumps(feat) + '\n')
    else:
        for feat in gJSON:
            click.echo(json.dumps(feat))
