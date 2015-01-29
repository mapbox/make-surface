from scripts import vectorize_raster, triangulate_raster, fill_facets

def vectorize(infile, outfile, classes, classfile, weight, nodata, smoothing, bidx, cartoCSS, axonometrize, nosimple, setNoData, nibbleMask, outvar):
    vectorize_raster.vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, bidx, cartoCSS, axonometrize, nosimple, setNoData, nibbleMask, outvar)

def triangulate(zoom, output, bounds, tile):
    triangulate_raster.triangulate(zoom, output, bounds, tile)

def fillfacets(infile, sampleRaster, noproject, output, band, zooming, batchprint, outputGeom, color):
    fill_facets.fillFacets(infile, sampleRaster, noproject, output, band, zooming, batchprint, outputGeom, color)