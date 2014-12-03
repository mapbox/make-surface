import click, fiona
import numpy as np
from rasterio import features
from shapely.geometry import Polygon, MultiPolygon, mapping
from multiprocessing import Pool


def toPolygons(outfile, schema, classRas, breaks, simplest, smoothing, crs, nodata, oaff, axonometrize, nosimple):
    
    tRas = np.zeros(classRas.shape, dtype=np.uint8)
    
    with fiona.open(outfile, "w", "ESRI Shapefile", schema, crs=crs) as outshp:
        
        click.echo("Simplifying: ", nl=False)
        
        for i in breaks:
            click.echo("%d, " % (i['break']), nl=False)
            tRas[np.where(classRas>=i['ind'])] = 1
            tRas[np.where(classRas<i['ind'])] = 0

            if nodata:
                tRas[np.where(classRas == 0)] = 0

            for feature, shapes in features.shapes(np.asarray(tRas,order='C'),transform=oaff):
                
                if shapes == 1:
                    featurelist = []

                    for c, f in enumerate(feature['coordinates']):
                        if len(f) > 5 or c == 0:
                            if axonometrize:
                                f = np.array(f)
                                f[:,1] += (axonometrize * i['break'])
                            if nosimple:
                                 poly = Polygon(f)
                            else:
                                poly = Polygon(f).simplify(simplest / float(smoothing), preserve_topology=True)
                            featurelist.append(poly)

                    if len(featurelist) != 0:
                        oPoly = MultiPolygon(featurelist)
                        outshp.write({'geometry': mapping(oPoly),'properties': {'value': i['break']}})

if __name__ == '__main__':
    toPolygons()