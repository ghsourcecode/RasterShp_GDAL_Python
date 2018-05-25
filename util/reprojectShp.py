#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/24 10:27
'''

import gdal, ogr, osr
import os

def reprojectExample():
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

def reprojectExample(fromShpPath, toEPSGCode, toShpPath):
    '''
    投影转换
    :return:
    '''
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(fromShpPath)
    copyInDataset = ogr.GetDriverByName("Memory").CopyDataSource(inDataSet, "")
    inLayer = copyInDataset.GetLayer(0)
    inSpatialRef = inLayer.GetSpatialRef()

    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(toEPSGCode)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # create the output layer
    outputShapefile = toShpPath
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("outshp_epsg_3857", outSpatialRef, ogr.wkbPolygon, [])
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    feature = inLayer.GetNextFeature()
    while feature:
        try:
            # get the input geometry
            geom = feature.GetGeometryRef()
            # reproject the geometry
            geom.Transform(coordTrans)
            feature.SetGeometry(geom)
            inLayer.SetFeature(feature)
            feature = None
            feature = inLayer.GetNextFeature()
        except Exception as e:
            print('type %s'%type(e))

    # for feature in inLayer:
    #     try:
    #         # get the input geometry
    #         geom = feature.GetGeometryRef()
    #         # reproject the geometry
    #         geom.Transform(coordTrans)
    #         feature.SetGeometry(geom)
    #         inLayer.SetFeature(feature)
    #     except Exception as e:
    #         print('type %s'%type(e))

    # Save and close the shapefiles
    tempCopy = driver.CopyDataSource(copyInDataset, toShpPath)
    tempCopy.SetProjection(outSpatialRef.ExportToWkt())

def reproject(fromShpPath, toEPSGCode, toShpPath):
    '''
    投影转换
    :return:
    '''
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(fromShpPath)
    copyInDataset = ogr.GetDriverByName("Memory").CopyDataSource(inDataSet, "")
    inDataSet = None
    inLayer = copyInDataset.GetLayer(0)
    inSpatialRef = inLayer.GetSpatialRef()

    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(toEPSGCode)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # create the output layer
    outputShapefile = toShpPath
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("outshp_epsg_3857", outSpatialRef, ogr.wkbPolygon, [])
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    for feature in inLayer:
        try:
            # get the input geometry
            geom = feature.GetGeometryRef()
            # reproject the geometry
            geom.Transform(coordTrans)
            feature.SetGeometry(geom)
            outLayer.CreateFeature(feature)
        except Exception as e:
            print('type %s'%type(e))
    outDataSet.Destroy()
