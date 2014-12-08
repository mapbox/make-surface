import rasterio
import mercantile

def triangulate(infile, zoom):
    with rasterio.drivers():
        with rasterio.open(infile, 'r') as src:
            print src.bounds