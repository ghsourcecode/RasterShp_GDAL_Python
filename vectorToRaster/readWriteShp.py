# -*- coding: cp936 -*-
try:
    from osgeo import gdal
    from osgeo import ogr
    import os
    import osr
except ImportError:
    import gdal
    import ogr
####################################################################################
# 读 shp
####################################################################################
def readVectorFile():
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    currentFolder = os.getcwd()
    parentFolder = os.path.dirname(currentFolder)
    strVectorFile = parentFolder + "/testdata/flttoshp.shp"
    print(strVectorFile)

    # 注册所有的驱动
    ogr.RegisterAll()

    # 打开数据
    dataSource = ogr.Open(strVectorFile, 0)
    if dataSource == None:
        print("打开文件【%s】失败！", strVectorFile)
        return

    print("打开文件【%s】成功！", strVectorFile)

    # 获取该数据源中的图层个数，一般shp数据图层只有一个，如果是mdb、dxf等图层就会有多个
    iLayerCount = dataSource.GetLayerCount()

    # 获取第一个图层
    oLayer = dataSource.GetLayerByIndex(0)
    if oLayer == None:
        print("获取第%d个图层失败！\n", 0)
        return

    # 对图层进行初始化，如果对图层进行了过滤操作，执行这句后，之前的过滤全部清空
    oLayer.ResetReading()

    # 通过属性表的SQL语句对图层中的要素进行筛选，这部分详细参考SQL查询章节内容
    # oLayer.SetAttributeFilter("\"NAME99\"LIKE \"北京市市辖区\"")

    # 通过指定的几何对象对图层中的要素进行筛选
    # oLayer.SetSpatialFilter()

    # 通过指定的四至范围对图层中的要素进行筛选
    # oLayer.SetSpatialFilterRect()

    # 获取图层中的属性表表头并输出
    print("属性表结构信息：")
    oDefn = oLayer.GetLayerDefn()
    iFieldCount = oDefn.GetFieldCount()
    for iAttr in range(iFieldCount):
        oField = oDefn.GetFieldDefn(iAttr)
        print("%s: %s(%d.%d)" % ( oField.GetNameRef(), oField.GetFieldTypeName(oField.GetType()), oField.GetWidth(), oField.GetPrecision()))

        # 输出图层中的要素个数
    print("要素个数 = %d", oLayer.GetFeatureCount(0))

    oFeature = oLayer.GetNextFeature()
    # 下面开始遍历图层中的要素
    while oFeature is not None:
        print("当前处理第%d个: \n属性值：", oFeature.GetFID())
        # 获取要素中的属性表内容
        for iField in range(iFieldCount):
            oFieldDefn = oDefn.GetFieldDefn(iField)
            line = " %s (%s) = " % (oFieldDefn.GetNameRef(), ogr.GetFieldTypeName(oFieldDefn.GetType()))

            if oFeature.IsFieldSet(iField):
                line = line + "%s" % (oFeature.GetFieldAsString(iField))
        else:
            line = line + "(null)"

        print(line)

        # 获取要素中的几何体
        oGeometry = oFeature.GetGeometryRef()

        # 为了演示，只输出一个要素信息
        break

    # 释放内存
    oFeature.Destroy()
    # 关闭数据源，相当于文件系统操作中的关闭文件
    dataSource.Destroy()
    print("数据集关闭！")

####################################################################################
# 写 shp
####################################################################################
def writeVectorFile():
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    currentFolder = os.getcwd()
    parentFolder = os.path.dirname(currentFolder)
    strVectorFile = parentFolder + "/testdata/TestPolygon.shp"

    # 注册所有的驱动
    ogr.RegisterAll()

    # 创建数据，这里以创建ESRI的shp文件为例
    strDriverName = "ESRI Shapefile"
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s 驱动不可用！\n", strDriverName)
        return

    # 创建数据源
    oDS = oDriver.CreateDataSource(strVectorFile)
    if oDS == None:
        print("创建文件【%s】失败！", strVectorFile)
        return

    # 创建图层，创建一个多边形图层，指定空间参考，如果不需要设置投影，可以将srs参数置为None
    srs = osr.SpatialReference();
    srs.ImportFromEPSG(4326)
    papszLCO = []
    oLayer = oDS.CreateLayer("TestPolygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("图层创建失败！\n")
        return

    # 下面创建属性表
    # 先创建一个叫FieldID的整型属性
    oFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)
    oLayer.CreateField(oFieldID, 1)

    # 再创建一个叫FeatureName的字符型属性，字符长度为50
    oFieldName = ogr.FieldDefn("FieldName", ogr.OFTString)
    oFieldName.SetWidth(100)
    oLayer.CreateField(oFieldName, 1)

    #从layer中读取相应的feature类型，并创建feature
    oDefn = oLayer.GetLayerDefn()

    # # 创建三角形要素
    # oFeatureTriangle = ogr.Feature(oDefn)
    # oFeatureTriangle.SetField(0, 0)
    # oFeatureTriangle.SetField(1, "三角形")
    # geomTriangle = ogr.CreateGeometryFromWkt("POLYGON ((0 0,20 0,10 15,0 0))")
    # oFeatureTriangle.SetGeometry(geomTriangle)
    # oLayer.CreateFeature(oFeatureTriangle)
    #
    # # 创建矩形要素
    # oFeatureRectangle = ogr.Feature(oDefn)
    # oFeatureRectangle.SetField(0, 1)
    # oFeatureRectangle.SetField(1, "矩形")
    # geomRectangle = ogr.CreateGeometryFromWkt("POLYGON ((30 0,60 0,60 30,30 30,30 0))")
    # oFeatureRectangle.SetGeometry(geomRectangle)
    # oLayer.CreateFeature(oFeatureRectangle)

    oFeaturePentagon = ogr.Feature(oDefn)
    oFeaturePentagon.SetField(0, 0)
    oFeaturePentagon.SetField(1, "三角形")
    geomTriangle = ogr.CreateGeometryFromWkt("POLYGON ((0 0,20 0,10 15,0 0))")
    oFeaturePentagon.SetGeometry(geomTriangle)
    oLayer.CreateFeature(oFeaturePentagon)
    # 创建五角形要素
    oFeaturePentagon = ogr.Feature(oDefn)
    oFeaturePentagon.SetField(0, 2)
    oFeaturePentagon.SetField(1, "五角形")
    geomPentagon = ogr.CreateGeometryFromWkt("POLYGON ((70 0,85 0,90 15,80 30,65 15,700))")
    oFeaturePentagon.SetGeometry(geomPentagon)
    oLayer.CreateFeature(oFeaturePentagon)

    oDS.Destroy()
    print("数据集创建完成！\n")

####################################################################################
# 删除矢量
####################################################################################
def deleteVector(strVectorFile):
    # 注册所有的驱动
    ogr.RegisterAll()

    # 打开矢量
    oDS = ogr.Open(strVectorFile, 0)
    if oDS == None:
        return
    oDriver = oDS.GetDriver()

    # 重要：此处需要关闭数据源，如果不关闭，会导致删除shp时，无法完全删除shp文件
    oDS.Destroy()

    if oDriver == None:
        os.remove(strVectorFile)
        return
    if oDriver.DeleteDataSource(strVectorFile) == ogr.OGRERR_NONE:
        return
    else:
        os.remove(strVectorFile)

####################################################################################
# 重命名矢量, 包括：shp, geojson
####################################################################################
def renameVector(strOldFile, strNewFile):
    # 注册所有的驱动
    ogr.RegisterAll()

    # 打开矢量
    oDS = ogr.Open(strOldFile, 0)
    if oDS == None:
        return

    oDriver = oDS.GetDriver()

    if oDriver == None:
        return

    oDDS = oDriver.CopyDataSource(oDS, strNewFile, [])
    oDDS.Destroy()
    # 重要：此处需要关闭数据源，如果不关闭，会导致删除shp时，无法完全删除shp文件
    oDS.Destroy()

    if oDDS == None:
        os.rename(strOldFile, strNewFile)

    if oDriver.DeleteDataSource(strOldFile) == ogr.OGRERR_NONE:
        return
    else:
        os.rename(strOldFile, strNewFile)

def copyDataSource(fromLocation, toLocation):
    '''
    复制矢量文件
    :param fromLocation:
    :param toLocation:
    :return:
    '''

    ogr.RegisterAll()

    sourceDatasource = ogr.Open(fromLocation)
    if sourceDatasource == None:
        print('文件不存在')

    driver = sourceDatasource.GetDriver()
    if driver == None:
        return

    targetDatasource = driver.CopyDataSource(sourceDatasource, toLocation, [])
    sourceDatasource.Destroy()
    targetDatasource.Destroy()

if __name__ == '__main__':
    readVectorFile()
    writeVectorFile()

    currentParentFolder = os.path.dirname(os.getcwd())
    oldShpName = currentParentFolder + '/testdata/TestPolygon.shp'
    newShpName = currentParentFolder + '/testdata/TestPolygonnew.shp'

    # copyDataSource(oldShpName, newShpName)

    renameVector(oldShpName, newShpName)
    deleteVector(newShpName)

