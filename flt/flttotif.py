import gdal, osr


def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    return band.ReadAsArray()

def getNoDataValue(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    return band.GetNoDataValue()

def array2raster(rasterfn,newRasterfn,array):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

def fltWithoutPrjToTiff(fltPath, tifPath):
    flt = gdal.Open(fltPath)
    fltarray = raster2array(fltPath)
    nodataValue = getNoDataValue(fltPath)

    geotransform = flt.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = flt.RasterXSize
    rows = flt.RasterYSize

    driver = gdal.GetDriverByName('GTiff')
    outTiff = driver.Create(tifPath, cols, rows, 1, gdal.GDT_Float32)
    outTiff.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight)) #此处是 2 层括号
    outband = outTiff.GetRasterBand(1)
    outband.SetNoDataValue(nodataValue)                                 #设置tif无数据值
    outband.WriteArray(fltarray)
    outTiffSRS = osr.SpatialReference()
    outTiffSRS.ImportFromEPSG(4326)
    outTiff.SetProjection(outTiffSRS.ExportToWkt())
    outband.FlushCache()

if __name__ == '__main__':
    fltpath = '../testdata/rain_2016.flt'
    tiffpath = '../testdata/out/flttotif.tif'
    fltWithoutPrjToTiff(fltpath, tiffpath)