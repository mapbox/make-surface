from scripts import vectorize_raster, triangulate_raster

def vectorize(infile, outfile, classes, classfile, weight, nodata, smoothing, band, cartoCSS, globeWrap, axonometrize, nosimple, setNoData, nibbleMask, rapFix):
    vectorize_raster.vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, band, cartoCSS, globeWrap, axonometrize, nosimple, setNoData, nibbleMask, rapFix)

def triangulate(zoom, output, bounds, tile):
    triangulate_raster.triangulate(zoom, output, bounds, tile)