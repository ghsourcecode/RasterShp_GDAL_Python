import random
from osgeo import gdal, ogr
import os
import numpy

gridcodename = "gridcode"
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

def rasterize2ThreeBands(shppath, pixel_size, noDataValue, rasterpath):
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
    field_def = ogr.FieldDefn(gridcodename, ogr.OFTReal)
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(gridcodename)
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
                              options=["ATTRIBUTE=%s" % gridcodename])
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
    field_def = ogr.FieldDefn(gridcodename, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(gridcodename)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField(gridcodename)
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
                              options=["ATTRIBUTE=%s" % gridcodename])
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
    field_def = ogr.FieldDefn(gridcodename, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(gridcodename)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField(gridcodename)
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

    # for i in range(bands):
    #     target_ds.GetRasterBand(i + 1).SetNoDataValue(-9999)
    #     target_ds.GetRasterBand(i + 1).Fill(-9999)

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, [1],
                              source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % gridcodename])
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
    field_def = ogr.FieldDefn(gridcodename, ogr.OFTReal)# RASTERIZE_COLOR_FIELD
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(gridcodename)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField(gridcodename)
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

    # for i in range(bands):
    #     target_ds.GetRasterBand(i + 1).SetNoDataValue(-9999)
    #     target_ds.GetRasterBand(i + 1).Fill(-9999)

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, [1],
                              source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % gridcodename])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
    orig_data_source.Destroy()

def rasterizeToRGB(shppath, pixel_size, colors, redrasterpath, greenrasterpath, bluerasterpath):
    # Open the data source
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    red_source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    green_source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    blue_source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")

    red_source_layer = red_source_ds.GetLayer(0)
    green_source_layer = green_source_ds.GetLayer(0)
    blue_source_layer = blue_source_ds.GetLayer(0)

    source_srs = red_source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = red_source_layer.GetExtent()

    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(gridcodename, ogr.OFTReal)# rasterize gridcode(不同等级渲染不同颜色)
    red_source_layer.CreateField(field_def)
    green_source_layer.CreateField(field_def)
    blue_source_layer.CreateField(field_def)

    source_layer_def = red_source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(gridcodename)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    # red band
    for feature in red_source_layer:
        gridcode = feature.GetField(gridcodename)
        redBand = int(colors[gridcode][0])
        feature.SetField(field_index, redBand)
        red_source_layer.SetFeature(feature)
    # green band
    for feature in green_source_layer:
        gridcode = feature.GetField(gridcodename)
        greenBand = int(colors[gridcode][1])
        feature.SetField(field_index, greenBand)
        green_source_layer.SetFeature(feature)
    # blue band
    for feature in blue_source_layer:
        gridcode = feature.GetField(gridcodename)
        blueBand = int(colors[gridcode][2])
        feature.SetField(field_index, blueBand)
        blue_source_layer.SetFeature(feature)

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 1
    # red band target
    red_target_ds = gdal.GetDriverByName('GTiff').Create(redrasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    red_target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    if source_srs:
        # Make the target raster have the same projection as the source
        red_target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        red_target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    # Rasterize
    err = gdal.RasterizeLayer(red_target_ds, [1],
                              red_source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % gridcodename])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    # green band target
    green_target_ds = gdal.GetDriverByName('GTiff').Create(greenrasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    green_target_ds.SetGeoTransform((
        x_min, pixel_size, 0,
        y_max, 0, -pixel_size,
    ))
    if source_srs:
        # Make the target raster have the same projection as the source
        green_target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        green_target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    # Rasterize
    err = gdal.RasterizeLayer(green_target_ds, [1],
                              green_source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % gridcodename])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    # blue band target
    blue_target_ds = gdal.GetDriverByName('GTiff').Create(bluerasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    blue_target_ds.SetGeoTransform((
        x_min, pixel_size, 0,
        y_max, 0, -pixel_size,
    ))
    if source_srs:
        # Make the target raster have the same projection as the source
        blue_target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        blue_target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    # Rasterize
    err = gdal.RasterizeLayer(blue_target_ds, [1],
                              blue_source_layer,
                              burn_values=[0],
                              options=["ATTRIBUTE=%s" % gridcodename])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    orig_data_source.Destroy()

if __name__ == '__main__':
    root = os.path.dirname(os.getcwd());
    shpPath = root + '/testdata/flttoshp.shp'
    pixel = 0.01
    redrasterpath = root + '/testdata/temp/red.tif'
    greenrasterpath = root + '/testdata/temp/green.tif'
    bluerasterpath = root + '/testdata/temp/blue.tif'
    rasterizeToRGB(shpPath, pixel, colors, redrasterpath, greenrasterpath, bluerasterpath)