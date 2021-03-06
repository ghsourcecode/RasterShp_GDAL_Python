import gdal, ogr, osr, os
import numpy as np

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

########################################################################
# main 入口
########################################################################
if __name__ == '__main__':
    rasterfn = '../testdata/Extract_tif11.tif'
    newValue = 0
    newRasterfn = '../testdata/out/SlopeNew.tif'

    # Convert Raster to array
    rasterArray = raster2array(rasterfn)

    # Get no data value of array
    noDataValue = getNoDataValue(rasterfn)

    # Updata no data value in array with new value

    # rasterArray[[j for i in rasterArray for j in i if j == noDataValue]] = newValue
    row = rasterArray.shape[0]
    col = rasterArray.shape[1]
    for i in range(0, row):
        for j in range(0, col):
            if rasterArray[i][j] - noDataValue <= 1e-09:
                rasterArray[i][j] = newValue

    # Write updated array to new raster
    array2raster(rasterfn,newRasterfn,rasterArray)

