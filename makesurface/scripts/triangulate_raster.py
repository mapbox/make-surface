import rasterio, mercantile, json, click
import numpy as np
from matplotlib.pyplot import plot, show

def quadtree(x, y, zoom ):
    '''
    This is slow right now - speed it up
    '''
    key = {
        (True, True) : '0',
        (False, True) : '1',
        (True, False) : '2',
        (False, False) : '3'
    }

    tile = mercantile.parent(x, y, zoom)
    quadkey = key[(x) % 2 == 0, (y) % 2 == 0]
    quadkey = key[(tile.x) % 2 == 0, (tile.y) % 2 == 0] + quadkey

    for z in range(zoom - 1, 1, -1):
        tile = mercantile.parent(tile.x, tile.y, z)
        quadkey = key[(tile.x) % 2 == 0, (tile.y) % 2 == 0] + quadkey
    return quadkey

def getCorners(bounds, boolKey):
    coordOrd = {
        True: [
                   [0, 2, 3, 0],
                   [0, 2, 1, 0]
                ],
        False: [
                   [3, 1, 2, 3],
                   [3, 1, 0, 3]
                ]
        }

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



def triangulate(bounds, zoom, output):
    gJSON = {
        "type": "FeatureCollection",
        "features": []
    }
    bounds = np.array(bounds.split(' ')).astype(np.float64)
    tileMin = mercantile.tile(bounds[0], bounds[3], zoom)
    tileMax = mercantile.tile(bounds[2], bounds[1], zoom)
    for r in range(tileMin.y, tileMax.y + 1):
        for c in range(tileMin.x, tileMax.x + 1):
            quad = quadtree(c, r, zoom)
            boolKey = (r+c) % 2 == 0
            coords = getCorners(mercantile.bounds(c, r, zoom), boolKey)
            gJSON['features'].append({
                "type": "Feature",
                "properties": {
                    "quadtree": quad + '0'
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords[0].tolist()]
                }
                })
            gJSON['features'].append({
                "type": "Feature",
                "properties": {
                    "quadtree": quad + '1'
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords[1].tolist()]
                }
                })
            # plot(coords[0][:,0], coords[0][:,1], c='red')
            # plot(coords[1][:,0], coords[1][:,1], c='blue')

    # show()
    stdout = click.get_text_stream('stdout')
    stdout.write(json.dumps(gJSON, indent=2))