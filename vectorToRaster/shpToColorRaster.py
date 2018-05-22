import random
from osgeo import gdal, ogr, osr
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

def rasterize2Tif(shppath, pixel_size, noDataValue, rasterpath):
    '''
    函数不能使用
    :param shppath:
    :param pixel_size:
    :param noDataValue:
    :param rasterpath:
    :return:
    '''
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
    '''
    实现将不同通道的颜色分量输出到不同 tif 文件中，之后再合成输出的 tif，这种方式可被下面的 rasterizeToRGB3Bands 函数替换
    :param shppath:
    :param pixel_size:
    :param colors:
    :param redrasterpath:
    :param greenrasterpath:
    :param bluerasterpath:
    :return:
    '''
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

def rasterizeToRGB3Bands(shppath, pixel_size, colors, outrasterpath):
    '''
    将 shp 栅格化 tif, 颜色信息写到3个 band 中，shp 图中每个面用不同颜色填充
    :param shppath:
    :param level:
    :param colors:
    :param outrasterpath:
    :return:
    '''
    # Open the data source
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    red_source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")

    source_layer = red_source_ds.GetLayer(0)

    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()

    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(gridcodename, ogr.OFTReal)# rasterize gridcode(不同等级渲染不同颜色)
    source_layer.CreateField(field_def)

    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(gridcodename)
    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        gridcode = feature.GetField(gridcodename)
        red = int(colors[gridcode][0])
        feature.SetField(field_index, gridcode + 1)
        source_layer.SetFeature(feature)

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 3
    # band target
    target_ds = gdal.GetDriverByName('GTiff').Create(outrasterpath, x_res, y_res, bands, gdal.GDT_Byte)
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
    # rasterizelayer 第2个参数是band名
    err = gdal.RasterizeLayer(target_ds, [1, 2, 3],
                              source_layer,
                              burn_values=[0, 0, 0],
                              options=["ATTRIBUTE=%s" % gridcodename])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    # 设置 3 个band 的值
    redBand = target_ds.GetRasterBand(1)
    redArray = redBand.ReadAsArray()
    greenBand = target_ds.GetRasterBand(2)
    greenArray = greenBand.ReadAsArray()
    blueBand = target_ds.GetRasterBand(3)
    blueArray = blueBand.ReadAsArray()
    width = redArray.shape[1]
    height = redArray.shape[0]
    for x in range(0, height - 1):
        for y in range(0, width - 1):
            code = redArray[x][y]
            if code > 0:
                redArray[x][y] = colors[code - 1][0]
                greenArray[x][y] = colors[code - 1][1]
                blueArray[x][y] = colors[code - 1][2]
    redBand.WriteArray(redArray)
    greenBand.WriteArray(greenArray)
    blueBand.WriteArray(blueArray)
    redBand.FlushCache()
    greenBand.FlushCache()
    blueBand.FlushCache()

    orig_data_source.Destroy()

def rasterizeToSingleColor3Bands(shppath, pixel_size, color, outrasterpath):
    '''
    栅格化单一颜色到 tif 图
    :param shppath:
    :param level:
    :param colors:
    :param outrasterpath:
    :return:
    '''
    # Open the data source
    orig_data_source = ogr.Open(shppath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    red_source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")

    source_layer = red_source_ds.GetLayer(0)

    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    bands = 3
    # band target
    target_ds = gdal.GetDriverByName('GTiff').Create(outrasterpath, x_res, y_res, bands, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
            x_min, pixel_size, 0,
            y_max, 0, -pixel_size,
        ))
    target_ds.GetRasterBand(1).SetNoDataValue(0)
    target_ds.GetRasterBand(2).SetNoDataValue(0)
    target_ds.GetRasterBand(3).SetNoDataValue(0)

    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        proj = osr.SpatialReference()
        proj.ImportFromEPSG(4326)
        target_ds.SetProjection(proj.ExportToWkt())
    # rasterizelayer 第2个参数是band名
    err = gdal.RasterizeLayer(target_ds, [1, 2, 3],
                              source_layer,
                              burn_values=color)
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    orig_data_source.Destroy()

'''
根据指定的google瓦片等级，计算出 shp 文件经纬度范围所在行列号范围，生成一张覆盖行列号范围的一张 tif 图，并不生成瓦片。
    说明：这么做的目的是想在使用 gdal 工具生成金字塔时，保证基于生成的 tif 图生成的瓦片行列号正确，或者改变思路，就用该方法
    生成指定 level 的google瓦片
    （未研究如何将多个 shp 图生成到同一张图中）
'''
def rasterizeToGoogleTile(shpPath, level, colors, outRasterPath):
    shpDataSource = ogr.Open(shpPath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    sourceDataSource = ogr.GetDriverByName('Memory').CopyDataSource(shpDataSource, '')
    shpLayer = sourceDataSource.GetLayer(0)
    shpReference = shpLayer.GetSpatialRef()
    minx, maxx, miny, maxy = shpLayer.GetExtent()

    fieldName = 'gridcode'
    field_def = ogr.FieldDefn(fieldName, ogr.OFTReal)
    shpLayer.CreateField(field_def)
    layer_def = shpLayer.GetLayerDefn()
    fieldIndex = layer_def.GetFieldIndex(fieldName)
    for feature in shpLayer:
        gridcode = feature.GetField(fieldName)  # shp文件中应当有 fieldName 的字段
        feature.SetField(fieldIndex, gridcode + 1)
        shpLayer.SetFeature(feature)

    # 计算输入 shp 所在google瓦片行列号范围
    originx = -180
    originy = 180       # google 瓦片从左上角开始计算
    tileResolution = getGoogleTileBandOfLevel(level, False)
    tolerance = 1.0e-9
    remainder = (minx - originx) % tileResolution
    minCol = None
    maxCol = None
    minRow = None
    maxRow = None
    if remainder <= tolerance:
        minCol = int((minx - originx) / tileResolution) - 1
    else:
        minCol = int((minx - originx) / tileResolution)
    remainder = (maxx - originx) % tileResolution
    if remainder <= tolerance:
        maxCol = int((maxx - originx) / tileResolution) - 1
    else:
        maxCol = int((maxx - originx) / tileResolution)
    remainder = (miny - originy) % tileResolution
    if remainder < tolerance:
        maxRow = abs(int((miny - originy) / tileResolution)) - 1
    else:
        maxRow = abs(int((miny - originy) / tileResolution))
    remainder = (maxy - originy) % tileResolution
    if remainder <= tolerance:
        minRow = abs(int((maxy - originy) / tileResolution)) - 1
    else:
        minRow = abs(int((maxy - originy) / tileResolution))

    # 计算输出tif坐标范围
    outMinX = minCol * tileResolution + originx
    outMaxX = (maxCol + 1) * tileResolution + originx    # 列号加1的目的是：列号乘分辨率为瓦片左边界坐标
    outMinY = originy - (maxRow + 1) * tileResolution    # 行号加1的目的是：行号乘分辨率为瓦片上边界坐标
    outMaxY = originy - minRow * tileResolution

    # create the destination source, 宽、高乘256是因为每一个瓦片的大小是256* 256
    width = int((outMaxX - outMinX) / tileResolution) * 256
    heigh = int((outMaxY - outMinY) / tileResolution) * 256
    pixel = tileResolution / 256
    bands = 3
    outRaster = gdal.GetDriverByName('GTiff').Create(outRasterPath, width, heigh, bands, gdal.GDT_Byte)
    outRaster.SetGeoTransform((
        outMinX, pixel, 0,
        outMaxY, 0, -pixel
    ))
    if shpReference:
        outRaster.SetProjection(shpReference.ExportToWkt())
    else:
        wgs84 = osr.SpatialReference()
        wgs84.ImportFromEPSG(4326)
        outRaster.SetProjection(wgs84.ExportToWkt())

    err = gdal.RasterizeLayer(outRaster, [1, 2, 3],
                              shpLayer,
                              burn_values=[0, 0, 0],
                              options=["ATTRIBUTE=%s" % fieldName]) # fieldName为修改shp文件后的字段名
    redBand = outRaster.GetRasterBand(1)
    redBandArray = redBand.ReadAsArray()
    greenBand = outRaster.GetRasterBand(2)
    greenBandArray = greenBand.ReadAsArray()
    blueBand = outRaster.GetRasterBand(3)
    blueBandArray = blueBand.ReadAsArray()
    for x in range(0, heigh - 1):
        for y in range(0, width - 1):
            code = redBandArray[x][y]
            if code > 0:
                redBandArray[x][y] = colors[code - 1][0]
                greenBandArray[x][y] = colors[code - 1][1]
                blueBandArray[x][y] = colors[code - 1][2]
    redBand.WriteArray(redBandArray)
    greenBand.WriteArray(greenBandArray)
    blueBand.WriteArray(blueBandArray)
    redBand.FlushCache()
    greenBand.FlushCache()
    blueBand.FlushCache()

def rasterizeToGoogleTileTest(shpPath, level, colors, outRasterPath):
    shpDataSource = ogr.Open(shpPath)
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    sourceDataSource = ogr.GetDriverByName('Memory').CopyDataSource(shpDataSource, '')
    shpLayer = sourceDataSource.GetLayer(0)
    shpReference = shpLayer.GetSpatialRef()
    minx, maxx, miny, maxy = shpLayer.GetExtent()

    fieldName = 'gridcode'
    field_def = ogr.FieldDefn(fieldName, ogr.OFTReal)
    shpLayer.CreateField(field_def)
    layer_def = shpLayer.GetLayerDefn()
    fieldIndex = layer_def.GetFieldIndex(fieldName)
    for feature in shpLayer:
        gridcode = feature.GetField(fieldName)  # shp文件中应当有 fieldName 的字段
        feature.SetField(fieldIndex, gridcode + 1)
        shpLayer.SetFeature(feature)

    # 计算输入 shp 所在google瓦片行列号范围
    originx = -180
    originy = 180       # google 瓦片从左上角开始计算
    tileResolution = getGoogleTileBandOfLevel(level, False)
    tolerance = 1.0e-9
    remainder = (minx - originx) % tileResolution
    minCol = None
    maxCol = None
    minRow = None
    maxRow = None
    if remainder <= tolerance:
        minCol = int((minx - originx) / tileResolution) - 1
    else:
        minCol = int((minx - originx) / tileResolution)
    remainder = (maxx - originx) % tileResolution
    if remainder <= tolerance:
        maxCol = int((maxx - originx) / tileResolution) - 1
    else:
        maxCol = int((maxx - originx) / tileResolution)
    remainder = (miny - originy) % tileResolution
    if remainder < tolerance:
        maxRow = abs(int((miny - originy) / tileResolution)) - 1
    else:
        maxRow = abs(int((miny - originy) / tileResolution))
    remainder = (maxy - originy) % tileResolution
    if remainder <= tolerance:
        minRow = abs(int((maxy - originy) / tileResolution)) - 1
    else:
        minRow = abs(int((maxy - originy) / tileResolution))

    # 计算输出tif坐标范围
    outMinX = (minCol + 2) * tileResolution + originx
    outMaxX = (minCol + 3) * tileResolution + originx    # 列号加1的目的是：列号乘分辨率为瓦片左边界坐标
    outMinY = originy - (maxRow) * tileResolution    # 行号加1的目的是：行号乘分辨率为瓦片上边界坐标
    outMaxY = originy - (maxRow - 1)* tileResolution

    # create the destination source, 宽、高乘256是因为每一个瓦片的大小是256* 256
    width = int((outMaxX - outMinX) / tileResolution) * 256
    heigh = int((outMaxY - outMinY) / tileResolution) * 256
    pixel = tileResolution / 256
    bands = 3
    outRaster = gdal.GetDriverByName('GTiff').Create(outRasterPath, width, heigh, bands, gdal.GDT_Byte)
    outRaster.SetGeoTransform((
        outMinX, pixel, 0,
        outMaxY, 0, -pixel
    ))
    if shpReference:
        outRaster.SetProjection(shpReference.ExportToWkt())
    else:
        wgs84 = osr.SpatialReference()
        wgs84.ImportFromEPSG(4326)
        outRaster.SetProjection(wgs84.ExportToWkt())

    err = gdal.RasterizeLayer(outRaster, [1, 2, 3],
                              shpLayer,
                              burn_values=[0, 0, 0],
                              options=["ATTRIBUTE=%s" % fieldName]) # fieldName为修改shp文件后的字段名
    redBand = outRaster.GetRasterBand(1)
    redBandArray = redBand.ReadAsArray()
    greenBand = outRaster.GetRasterBand(2)
    greenBandArray = greenBand.ReadAsArray()
    blueBand = outRaster.GetRasterBand(3)
    blueBandArray = blueBand.ReadAsArray()
    for x in range(0, heigh - 1):
        for y in range(0, width - 1):
            code = redBandArray[x][y]
            if code > 0:
                redBandArray[x][y] = colors[code - 1][0]
                greenBandArray[x][y] = colors[code - 1][1]
                blueBandArray[x][y] = colors[code - 1][2]
    redBand.WriteArray(redBandArray)
    greenBand.WriteArray(greenBandArray)
    blueBand.WriteArray(blueBandArray)
    redBand.FlushCache()
    greenBand.FlushCache()
    blueBand.FlushCache()

def getGoogleTileBandOfLevel(level, isProj):
    '''
    根据层级计算瓦片分辨率
    google瓦片分级标准
        投影后的坐标范围：（minx, miny, maxx, maxy）
            Bounds(地图范围)：[-20037508.3427892, -20037508.3427892, 20037508.3427892, 20037508.3427892]
        不投影的坐标范围：（minx, miny, maxx, maxy）
            Bounds(地图范围)：[-180, -180, 180, 180]
    层级      行       列
     0        1        1
     1        2        2
     2        4        4
     ..       ..       ..
     n        2^n      2^n
     则每层瓦片分辨率：
        (maxx - minx) / 2^n

    :param level:
    :param isProj: 是否返回投影后分辨率，以米为单位
    :return:
    '''
    projMinX = -20037508.3427892
    projMaxX = 20037508.3427892
    minx = -180
    maxx = 180
    if isProj:
        return (projMaxX - projMinX) / numpy.power(2, level)
    else:
        return (maxx - minx) / numpy.power(2, level)



if __name__ == '__main__':
    root = os.path.dirname(os.getcwd());
    shpPath = root + '/testdata/flttoshp.shp'
    pixel = 0.01
    redrasterpath = root + '/testdata/temp/red.tif'
    greenrasterpath = root + '/testdata/temp/green.tif'
    bluerasterpath = root + '/testdata/temp/blue.tif'
    alpharasterpath = root + '/testdata/temp/alpha.tif'
    # rasterizeToRGB(shpPath, pixel, colors, redrasterpath, greenrasterpath, bluerasterpath)
    # rasterizeToRGBA(shpPath, pixel, colors, redrasterpath, greenrasterpath, bluerasterpath, alpharasterpath)

    rasterpath = root + '/testdata/temp/rasterpath2.tif'
    # rasterizeTo3Bands(shpPath, pixel, colors, rasterpath)

    riverPath = root + '/testdata/jiangxiriver.shp'
    riverRasterPath = root + '/testdata/temp/riverraster.tif'
    color = [10, 120, 89]
    # rasterizeToSingleColor3Bands(riverPath, pixel, color, riverRasterPath)

    # 测试输出google瓦片规则栅格
    level = 8
    outGoogleRaster = root + '/testdata/temp/googleRaster_3_' + str(level) + '.tif'
    rasterizeToGoogleTileTest(shpPath, level, colors, outGoogleRaster)
