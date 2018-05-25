#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/24 10:56
'''

from osgeo import ogr
import os,math

def copyDatasource():
    '''
    我们使用了CopyDataSource()的方法来对数据进行复制的操作。
    这个函数的第1个参数是要进行复制的数据源，第2个参数是要生成的数据的路径，
    并且返回一个指针。为了将数据写入到硬盘，必须释放这个指标，使用Release()方法。
    :return:
    '''
    inshp = '/gdata/world_borders.shp'
    ds = ogr.Open(inshp)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    outputfile = '/gdata/world_borders_copy.shp'
    if os.access( outputfile, os.F_OK ):
        driver.DeleteDataSource( outputfile )
        pt_cp = driver.CopyDataSource(ds, outputfile)
        pt_cp.Release()

def copyLayer():
    '''
    为了对layer进行拷贝操作，首先得有数据源。在这里首先建立了newds这一数据源，
    然后使用newds的CopyLayer()方法来对图层进行拷贝操作。值得注意的是，当图层拷贝完成之后，
    需要对newds使用Destroy()操作，才能将数据写入到磁盘。

    CopyLayer()方法的第1个参数是OGR的Layer对象，第2个参数是要生成的图层的名称。
    对于Shapefile来说，这个名称是没有用的，但是无论如何，都要给出一个字符串型的变量。
    :return:
    '''
    inshp = '/gdata/world_borders.shp'
    ds = ogr.Open(inshp)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    outputfile = '/gdata/world_borders_copy2.shp'
    if os.access(outputfile, os.F_OK):
        driver.DeleteDataSource(outputfile)
    layer = ds.GetLayer()
    newds = driver.CreateDataSource(outputfile)
    # layernew = newds.CreateLayer('linescopy',None,ogr.wkbLineString)
    pt_layer = newds.CopyLayer(layer, 'abcd')
    newds.Destroy()


def copyFeatures():
    '''
    Destroy()不能省略，Destroy()除了销毁数据还担负了数据flush到磁盘的任务。
    如果没有这一句，那么刚才创建的一系列Feature都不会写入磁盘的文件中。
    :return:
    '''
    inshp = '/gdata/world_borders.shp'
    ds = ogr.Open(inshp)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    outputfile = '/gdata/world_borders_copy3.shp'
    if os.access(outputfile, os.F_OK):
        driver.DeleteDataSource(outputfile)
    newds = driver.CreateDataSource(outputfile)
    layernew = newds.CreateLayer('worldcopy', None, ogr.wkbLineString)
    layer = ds.GetLayer()
    extent = layer.GetExtent()
    feature = layer.GetNextFeature()
    while feature is not None:
        layernew.CreateFeature(feature)
        feature = layer.GetNextFeature()
    newds.Destroy()