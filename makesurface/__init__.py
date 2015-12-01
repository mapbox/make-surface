from scripts import vectorize_raster, triangulate_raster, fill_facets, new_filler

def vectorize(infile, outfile, classes, classfile, weight, nodata, smoothing, bidx, cartoCSS, axonometrize, nosimple, setNoData, nibbleMask, outvar):
    vectorize_raster.vectorizeRaster(infile, outfile, classes, classfile, weight, nodata, smoothing, bidx, cartoCSS, axonometrize, nosimple, setNoData, nibbleMask, outvar)

def triangulate(zoom, output, bounds, tile, tableid, boundsfile):
    triangulate_raster.triangulate(zoom, output, bounds, tile, tableid, boundsfile)

def fillfacets(infile, sampleRaster, noproject, output, band, zooming, batchprint, outputGeom, color, setnodata):
    fill_facets.fillFacets(infile, sampleRaster, noproject, output, band, zooming, batchprint, outputGeom, color, setnodata)

def filltris(infile, sampleraster, outfile):
    new_filler.fillValues(infile, sampleraster, outfile)