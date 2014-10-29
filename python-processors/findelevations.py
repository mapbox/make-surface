from shapely.wkb import dumps, loads
import fiona
import numpy as np
import psycopg2
from shapely.geometry import LineString
import requests
from math import pi, atan, exp, ceil

def inverse(xy):
    R2D = 180.0 / pi
    A = 6378137.0
    return [(xy[0] * R2D / A),((pi*0.5) - 2.0 * atan(exp(-xy[1] / A))) * R2D]

def parseSingleLine(lineGeom):
    return [inverse(c) for c in lineGeom.coords]

def parseMultiLine(lineGeoms):
    conlengths = [g.length for g in lineGeoms]
    maxInd = conlengths.index(max(conlengths))
    return parseSingleLine(lineGeoms[maxInd])

def makeSingleArray(loadline):
    if loadline.type == 'MultiLineString':
        loaded = np.array(parseMultiLine(loadline))
    else:
        loaded = np.array(parseSingleLine(loadline))
    return loaded

def findMinVariation(conSeq, samples, interval):
    if len(conSeq) != len(samples):
        return "ERROR"
    returnArr =  np.round(samples / interval) * interval
    bases = list(set(returnArr - (conSeq * interval)))
    matches = []
    for i in bases:
        matches.append(np.abs(np.sum(returnArr - (i + conSeq * interval))))
    return (bases[matches.index(min(matches))] + conSeq * interval).astype(np.uint16)

def findAllElevations(lineArray, interval, samplingInterval=200):
    samples = []
    actuals = []
    for i in lineArray:
        actuals.append(i[0])
        loaded = loads(bytes(i[1]), True)
        aline = np.array(makeSingleArray(loaded))
        stringline = ';'.join([','.join(a) for a in np.around(aline[0:-1:int(ceil(aline.shape[0] / float(samplingInterval)))], decimals=6).astype(str)])
        req = requests.get(baseURL+stringline)
        elevs = np.array([e['ele'] for e in req.json()['results']])
        samples.append(np.mean(elevs))
    actuals = np.array(actuals)
    samples = np.array(samples)
    intervalers = ((actuals - min(actuals)) / interval).astype(np.uint16)
    outEst = findMinVariation(intervalers, samples, interval)
    print actuals - outEst
    return outEst

baseURL = 'https://api.tiles.mapbox.com/v4/surface/mapbox.mapbox-terrain-v1.json?layer=contour&fields=ele&interpolate=false&access_token=pk.eyJ1IjoiYm9iYnlzdWQiLCJhIjoiTi16MElIUSJ9.Clrqck--7WmHeqqvtFdYig&points='

conn = psycopg2.connect("dbname=terrain user=postgres port=5432")
cur = conn.cursor()
queryString = "SELECT ele, geom FROM %s" % ("next_cons",)
cur.execute(queryString)
cQuer = cur.fetchall()


results = findAllElevations(cQuer, 10)

print results

