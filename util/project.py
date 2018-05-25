from osgeo import gdal
from osgeo import osr
import ogr
import os
import numpy

def getSRSPair(dataset):
    '''
    获得给定数据的投影参考系和地理参考系
    :param dataset: GDAL地理数据
    :return: 投影参考系和地理参考系
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def geo2lonlat(dataset, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]


def lonlat2geo(dataset, lon, lat):
    '''
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lon, lat)对应的投影坐标
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]

def imagexy2geo(dataset, row, col):
    '''
    根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
    :param dataset: GDAL地理数据
    :param row: 像素的行号
    :param col: 像素的列号
    :return: 行列号(row, col)对应的投影坐标或地理坐标(x, y)
    '''
    trans = dataset.GetGeoTransform()
    px = trans[0] + row * trans[1] + col * trans[2]
    py = trans[3] + row * trans[4] + col * trans[5]
    return px, py


def geo2imagexy(dataset, x, y):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param dataset: GDAL地理数据
    :param x: 投影或地理坐标x
    :param y: 投影或地理坐标y
    :return: 影坐标或地理坐标(x, y)对应的影像图上行列号(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = numpy.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = numpy.array([x - trans[0], y - trans[3]])
    return numpy.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解

def defineProject(epsgCode):
    '''
    建立一个新的Projection：
    首先导入osr库，之后使用osr.SpatialReference()创建SpatialReference对象

     之后用下列语句向SpatialReference对象导入投影信息
        •ImportFromWkt(<wkt>)
        •ImportFromEPSG(<epsg>)
        •ImportFromProj4(<proj4>)
        •ImportFromESRI(<proj_lines>)
        •ImportFromPCI(<proj>, <units>, <parms>)
        •ImportFromUSGS(<proj_code>, <zone>)
        •ImportFromXML(<xml>)

    导出Projection，使用下面的语句可以导出为字符串
        •ExportToWkt()
        •ExportToPrettyWkt()
        •ExportToProj4()
        •ExportToPCI()
        •ExportToUSGS()
        •ExportToXML()
    '''
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromEPSG(epsgCode)

    return spatialReference

def getProjectString():
    '''
     测试得到定义的投影信息
    '''
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromEPSG(4326)
    epsg4326wktstring = spatialReference.ExportToWkt()
    print('epse 4326 wkt: ' + epsg4326wktstring)

def project(sourceFile, targetFile):
    '''
    投影转换
    :return:
    '''
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # input SpatialReference
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(2927)

    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # get the input layer
    inDataSet = driver.Open(r'c:\data\spatial\basemap.shp')
    inLayer = inDataSet.GetLayer()

    # create the output layer
    outputShapefile = r'c:\data\spatial\basemap_4326.shp'
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("basemap_4326", geom_type=ogr.wkbMultiPolygon)

    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # dereference the features and get the next input feature
        outFeature = None
        inFeature = inLayer.GetNextFeature()

    # Save and close the shapefiles
    inDataSet = None
    outDataSet = None

if __name__ == '__main__':
    gdal.AllRegister()
    dataset = gdal.Open(r"E:\pythontest\python_gdal_testdata\Extract_tif11.tif")
    print('数据投影：')
    print(dataset.GetGeoTransform())
    print('数据的大小（行，列）：')
    print('(%s %s)' % (dataset.RasterYSize, dataset.RasterXSize))

    x = 464201
    y = 5818760
    lon = 122.47242
    lat = 52.51778
    row = 2399
    col = 3751

    print('投影坐标 -> 经纬度：')
    coords = geo2lonlat(dataset, x, y)
    print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))
    print('经纬度 -> 投影坐标：')
    coords = lonlat2geo(dataset, lon, lat)
    print('(%s, %s)->(%s, %s)' % (lon, lat, coords[0], coords[1]))

    print('图上坐标 -> 投影坐标：')
    coords = imagexy2geo(dataset, row, col)
    print('(%s, %s)->(%s, %s)' % (row, col, coords[0], coords[1]))
    print('投影坐标 -> 图上坐标：')
    coords = geo2imagexy(dataset, x, y)
    print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))

    # 测试输出投影信息
    getProjectString()