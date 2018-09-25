#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/9/20 9:39
'''

import gdal
import numpy
from osgeo import osr


def readTif(fileName):
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName+"文件无法打开")
        return
    im_width = dataset.RasterXSize #栅格矩阵的列数
    im_height = dataset.RasterYSize #栅格矩阵的行数
    im_bands = dataset.RasterCount #波段数
    im_data = dataset.ReadAsArray(0,0,im_width,im_height)#获取数据
    im_geotrans = dataset.GetGeoTransform()#获取仿射矩阵信息
    im_proj = dataset.GetProjection()#获取投影信息
    im_blueBand =  im_data[0,0:im_height,0:im_width]#获取蓝波段
    im_greenBand = im_data[1,0:im_height,0:im_width]#获取绿波段
    im_redBand =   im_data[2,0:im_height,0:im_width]#获取红波段
    im_nirBand = im_data[3,0:im_height,0:im_width]#获取近红外波段

def writeTiff(im_data,im_width,im_height,im_bands,im_geotrans,im_proj,path):
    '''
    用gdal 生成geotiff
    :param im_data: 要生成tif的像互值
    :param im_width: tif 宽度
    :param im_height:
    :param im_bands: 波段数
    :param im_geotrans: tif坐标范围等转换参数
    :param im_proj: 投影
    :param path: 输出路径
    :return:
    '''
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = numpy.array([im_data])
    else:
        im_bands, (im_height, im_width) = 1,im_data.shape
    #创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, im_width, im_height, im_bands, datatype)
    if(dataset!= None):
        dataset.SetGeoTransform(im_geotrans) #写入仿射变换参数
        dataset.SetProjection(im_proj) #写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i+1).WriteArray(im_data[i])
    dataset.FlushCache()
    del dataset

def createProjectFromEPSG(epsgCode):
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromEPSG(4326)
    return spatialReference

def createGeoTiffTransform():
    print("dks")

if __name__ == "__main__":
    print("测试读取geotiff")
    gdal.AllRegister()
    geotiffPath = "../testdata/flttotif.tif"
    # readTif(geotiffPath)

    '''numpy生成float类型的数组'''
    row = 100
    col = 200
    bands = 3
    imageData = numpy.zeros((bands, row, col), numpy.float)
    prj = createProjectFromEPSG(4326)
    prjWkt = prj.ExportToWkt()
    '''生成geotiff的transform'''
    minx = 115
    maxy = 39
    xresolution = 0.1
    yresolution = -0.1
    xroll = 0
    yroll = 0
    geotiffTransform = (minx, xresolution, xroll, maxy, yroll, yresolution)
    outPath = "../testdata/pngToTiff/writetifftest.tif"
    writeTiff(imageData, col, row, bands, geotiffTransform, prjWkt, outPath)

