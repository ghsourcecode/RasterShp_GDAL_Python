from osgeo import ogr
from osgeo import gdal
import math
import os
'''
shp 转 tif，转出的tif图是灰度的
'''
def shpToRaster(shpPath, pixel, rasterPath):
    # set pixel size
    # pixelx = 0.00002
    noDataValue = -9999

    # Shapefile input name
    # input projection must be in cartesian system in meters
    # input wgs 84 or EPSG: 4326 will NOT work!!!
    # TIF Raster file to be created

    # Open the data source get the layer object
    # assign extent coordinates
    # shp_driver = ogr.GetDriverByName('ESRI Shapefile')
    open_shp = ogr.Open(shpPath)
    shpLayer = open_shp.GetLayer()
    minx, maxx, miny, maxy = shpLayer.GetExtent()

    # calculate raster width height
    width = int((maxx - minx) / pixel)
    height = int((maxy - miny) / pixel)

    # set the image type for export
    image_type = 'GTiff'
    # image_type = 'HFA'
    driver = gdal.GetDriverByName(image_type)
    driver.Register()

    # create a new raster takes Parameters
    # Filename     the name of the dataset to create. UTF-8 encoded.
    # nXSize     width of created raster in pixels.
    # nYSize     height of created raster in pixels.
    # nBands     number of bands.
    # eType     type of raster.
    nBands  = 1
    outraster = driver.Create(rasterPath, width, height, nBands, gdal.GDT_Byte)
    outraster.SetGeoTransform((minx, pixel, 0, maxy, 0, -pixel))

    # get the raster band we want to export too
    rasterBand = outraster.GetRasterBand(1)

    # assign the no data value to empty cells
    rasterBand.SetNoDataValue(noDataValue)

    # run vectorToRaster to raster on new raster with input Shapefile
    gdal.RasterizeLayer(outraster, [1], shpLayer, burn_values=[255])


if __name__ == '__main__':
    currentFolder = os.getcwd()
    parentFolder = os.path.dirname(currentFolder)
    shpPath = parentFolder + '/testdata/flttoshp.shp'
    rasterPath = parentFolder + '/testdata/shptoraster.tif'
    pixel = 0.2
    shpToRaster(shpPath, pixel, rasterPath)