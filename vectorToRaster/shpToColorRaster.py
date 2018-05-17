import random
from osgeo import gdal, ogr
import os
import numpy

colorvalue = "__color__"
alpha = 1
colors = numpy.array([
        [255, 255, 128, alpha],
        [229, 252, 114, alpha],
        [205, 250, 100, alpha],
        [179, 245, 86, alpha],
        [155, 242, 73, alpha],
        [129, 237, 57, alpha],
        [102, 232, 42, alpha],
        [75, 227, 25, alpha],
        [57, 222, 24, alpha],
        [62, 209, 54, alpha],
        [62, 199, 75, alpha],
        [60, 189, 95, alpha],
        [59, 179, 113, alpha],
        [54, 168, 130, alpha],
        [44, 158, 147, alpha],
        [31, 150, 166, alpha],
        [30, 134, 166, alpha],
        [32, 116, 161, alpha],
        [34, 95, 153, alpha],
        [33, 79, 148, alpha],
        [31, 62, 140, alpha],
        [27, 46, 133, alpha],
        [20, 31, 128, alpha],
        [12, 16, 120, alpha]
    ])

def rasterize(shppath, pixel_size, noDataValue, rasterpath):
    # Open the data source
    # orig_data_source = ogr.Open("test.shp")
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(
            orig_data_source, "")
    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(colorvalue, ogr.OFTReal)
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(colorvalue)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        feature.SetField(field_index, random.randint(0, 255))
        source_layer.SetFeature(feature)
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('GTiff').Create(rasterpath, x_res, y_res, 3, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')
    # Rasterize
    """
    RasterizeLayer(Dataset dataset, int bands, Layer layer, void pfnTransformer = None, 
        void pTransformArg = None, 
        int burn_values = 0, char options = None, GDALProgressFunc callback = 0, 
        void callback_data = None) -> int
    """
    err = gdal.RasterizeLayer(target_ds, (3, 2, 1), source_layer,
                              burn_values=(0, 0, 0),
                              options=["ATTRIBUTE=%s" % colorvalue])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

def rasterize2(shppath, pixel_size, noDataValue, rasterpath):
    # Open the data source
    # orig_data_source = ogr.Open("test.shp")
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(colorvalue, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(colorvalue)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField('gridcode')
        feature.SetField(field_index, random.randint(0, 255)) #random.randint(0, 255)
        source_layer.SetFeature(feature)
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 1
    target_ds = gdal.GetDriverByName('GTiff').Create(rasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')


    # 根据feature中属性值，确定R G B三个波段的值
    # 采用3个颜色数组,代表 RGB 三通道
    rArray = numpy.zeros((x_res, y_res))
    gArray = numpy.zeros((x_res, y_res))
    bArray = numpy.zeros((x_res, y_res))
    # for feature in source_layer:
    #     feature.SetField(field_index, random.randint(0, 255)) #random.randint(0, 255)
    #     source_layer.SetFeature(feature)


    for i in range(bands):
        target_ds.GetRasterBand(i + 1).SetNoDataValue(-9999)
        target_ds.GetRasterBand(i + 1).Fill(-9999)

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, [1],
                              source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % colorvalue])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)


def redRasterize(shppath, pixel_size, noDataValue, rasterpath):
    # Open the data source
    # orig_data_source = ogr.Open("test.shp")
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(colorvalue, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(colorvalue)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField('gridcode')
        redcolor = int(colors[gridcode][0])
        feature.SetField(field_index, redcolor) #random.randint(0, 255)
        source_layer.SetFeature(feature)
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 1
    target_ds = gdal.GetDriverByName('GTiff').Create(rasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    for i in range(bands):
        target_ds.GetRasterBand(i + 1).SetNoDataValue(-9999)
        target_ds.GetRasterBand(i + 1).Fill(-9999)

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, [1],
                              source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % colorvalue])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
    orig_data_source.Destroy()

def greenRasterize(shppath, pixel_size, noDataValue, rasterpath):
    # Open the data source
    # orig_data_source = ogr.Open("test.shp")
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(colorvalue, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(colorvalue)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField('gridcode')
        greencolor = int(colors[gridcode][1])
        feature.SetField(field_index, greencolor) #random.randint(0, 255)
        source_layer.SetFeature(feature)
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 1
    target_ds = gdal.GetDriverByName('GTiff').Create(rasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    for i in range(bands):
        target_ds.GetRasterBand(i + 1).SetNoDataValue(-9999)
        target_ds.GetRasterBand(i + 1).Fill(-9999)

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, [1],
                              source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % colorvalue])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
    orig_data_source.Destroy()

def blueRasterize(shppath, pixel_size, noDataValue, rasterpath):
    # Open the data source
    # orig_data_source = ogr.Open("test.shp")
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    source_layer = source_ds.GetLayer(0)
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(colorvalue, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(colorvalue)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField('gridcode')
        bluecolor = int(colors[gridcode][2])
        feature.SetField(field_index, bluecolor) #random.randint(0, 255)
        source_layer.SetFeature(feature)
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 1
    target_ds = gdal.GetDriverByName('GTiff').Create(rasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    for i in range(bands):
        target_ds.GetRasterBand(i + 1).SetNoDataValue(-9999)
        target_ds.GetRasterBand(i + 1).Fill(-9999)

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, [1],
                              source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % colorvalue])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
    orig_data_source.Destroy()

if __name__ == '__main__':
    root = os.path.dirname(os.getcwd());
    shpPath = root + '/testdata/flttoshp.shp'
    pixel = 0.01
    nodatavalue = -9999

    # threebandsrasterpath = root + '/testdata/threebands.tif'
    # rasterize(shpPath, pixel, None, threebandsrasterpath)

    # rasterPath = root + '/testdata/outraster1.tif'
    # rasterize2(shpPath, pixel, nodatavalue, rasterPath)
    # rasterPath = root + '/testdata/outraster2.tif'
    # rasterize2(shpPath, pixel, nodatavalue, rasterPath)
    # rasterPath = root + '/testdata/outraster3.tif'
    # rasterize2(shpPath, pixel, nodatavalue, rasterPath)

    redRasterPath = root + '/testdata/outraster1.tif'
    redRasterize(shpPath, pixel, nodatavalue, redRasterPath)
    greenRasterPath = root + '/testdata/outraster2.tif'
    greenRasterize(shpPath, pixel, nodatavalue, greenRasterPath)
    blueRasterPath = root + '/testdata/outraster3.tif'
    blueRasterize(shpPath, pixel, nodatavalue, blueRasterPath)
