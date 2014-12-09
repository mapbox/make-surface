import rasterio, mercantile, json, click, sys
import numpy as np

def quadtree(x, y, zoom):
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
    quadKey = [
        key[(x) % 2 == 0, (y) % 2 == 0],
        key[(tile.x) % 2 == 0, (tile.y) % 2 == 0]
    ]

    for z in range(zoom - 1, 1, -1):
        tile = mercantile.parent(tile.x, tile.y, z)
        quadKey.append(key[(tile.x) % 2 == 0, (tile.y) % 2 == 0])

    return ''.join(reversed(quadKey))

def getCorners(bounds, boolKey):
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

def triangulate(zoom, output, bounds, tile):
    if bounds:
        bounds = np.array(bounds.split(' ')).astype(np.float64)
    elif tile:
        tile = np.array(tile.split(' ')).astype(np.uint16)
        tBounds = mercantile.bounds(tile[0], tile[0], tile[0])
        bounds = np.array([tBounds.west, tBounds.south, tBounds.east-0.0001 , tBounds.north])
    else:
        sys.exit('Error: A bounds or tile must be specified')

    gJSON = {
        "type": "FeatureCollection",
        "features": []
    }
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

    if output:
        with open(output, 'w') as oFile:
            oFile.write(json.dumps(gJSON, indent=2))
    else:
        stdout = click.get_text_stream('stdout')
        stdout.write(json.dumps(gJSON, indent=2))