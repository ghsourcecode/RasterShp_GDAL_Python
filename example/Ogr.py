#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/6/25 11:54
'''

import osgeo.ogr
import os.path
import sys
import ogr
import osr
import os
import shutil
import utm

mypath = os.path.dirname(os.path.realpath(sys.argv[0]))
shapefile_name = os.path.join(mypath, "../files/tl_2012_us_state.shp")
shapefile = osgeo.ogr.Open(shapefile_name)
numLayers = shapefile.GetLayerCount()
layer = shapefile.GetLayer(0)
feature = layer.GetFeature(2)


print("Shapefile contains %d layers" % numLayers)

def readShpLayers():
    for layerNum in range(numLayers):
        layer = shapefile.GetLayer(layerNum)
        spatialRef = layer.GetSpatialRef().ExportToProj4()
        numFeatures = layer.GetFeatureCount()
        print
        "Layer %d has spatial reference %s" % (layerNum, spatialRef)
        print
        "Layer %d has %d features" % (layerNum, numFeatures)
        print

        for featureNum in range(numFeatures):
            feature = layer.GetFeature(featureNum)
            featureName = feature.GetField("NAME")

            print
            "Feature %d has name %s" % (featureNum, featureName)

def readAttributes():
    attributes = feature.items()

    for key, value in attributes.items():
        print(" %s = %s" % (key, value))

    geometry = feature.GetGeometryRef()
    geometryName = geometry.GetGeometryName()

    print("Feature's geometry data consists of a %s" % geometryName)


def analyzeGeometry(geometry, indent=0):
    s = []
    s.append("  " * indent)
    s.append(geometry.GetGeometryName())
    if geometry.GetPointCount() > 0:
        s.append(" with %d data points" % geometry.GetPointCount())
    if geometry.GetGeometryCount() > 0:
        s.append(" containing:")

    print("".join(s))

    for i in range(geometry.GetGeometryCount()):
        analyzeGeometry(geometry.GetGeometryRef(i), indent + 1)

def reproject():
    # Source and target file names
    srcName = "NYC_MUSEUMS_LAMBERT.shp"
    tgtName = "NYC_MUSEUMS_GEO.shp"

    # Target spatial reference
    tgt_spatRef = osr.SpatialReference()
    tgt_spatRef.ImportFromEPSG(4326)

    # Source shapefile
    driver = ogr.GetDriverByName("ESRI Shapefile")
    src = driver.Open(srcName, 0)
    srcLyr = src.GetLayer()

    # Source spatial reference
    src_spatRef = srcLyr.GetSpatialRef()

    # Target shapefile -
    # delete if it's already
    # there.
    if os.path.exists(tgtName):
        driver.DeleteDataSource(tgtName)
    tgt = driver.CreateDataSource(tgtName)
    lyrName = os.path.splitext(tgtName)[0]
    tgtLyr = tgt.CreateLayer(lyrName, geom_type=ogr.wkbPoint)

    # Layer definition
    featDef = srcLyr.GetLayerDefn()

    # Spatial Transform
    trans = osr.CoordinateTransformation(src_spatRef, tgt_spatRef)

    # Reproject and copy features
    srcFeat = srcLyr.GetNextFeature()
    while srcFeat:
        geom = srcFeat.GetGeometryRef()
        geom.Transform(trans)
        feature = ogr.Feature(featDef)
        feature.SetGeometry(geom)
        tgtLyr.CreateFeature(feature)
        feature.Destroy()
        srcFeat.Destroy()
        srcFeat = srcLyr.GetNextFeature()
    src.Destroy()
    tgt.Destroy()

    # Create the prj file
    tgt_spatRef.MorphToESRI()
    prj = open(lyrName + ".prj", "w")
    prj.write(tgt_spatRef.ExportToWkt())
    prj.close()

    # Just copy dbf contents over rather
    # than rebuild the dbf using the
    # ogr API since we're not changing
    # anything.
    srcDbf = os.path.splitext(srcName)[0] + ".dbf"
    tgtDbf = lyrName + ".dbf"
    shutil.copyfile(srcDbf, tgtDbf)

def readShp():
    r = shapefile.Reader("MSCities_Geo_Pts")
    print(r)
    print(r.bbox)
    print(r.shapeType)
    print(r.numRecords)
    print(r.fields)
    print([item[0] for item in r.fields[1:]])
    print(r.record(2))
    print(r.record(2)[4])
    fieldNames = [item[0] for item in r.fields[1:]]
    name10 = fieldNames.index("NAME10")
    print
    name10
    print
    r.record(2)[name10]
    zipRec = zip(fieldNames, r)
    print
    zipRec
    for z in zipRec:
        if z[0] == "NAME10":
            print
            z[1]
    for rec in enumerate(r.records()[:3]):
        print
        rec[0] + 1, ": ", rec[1]
    counter = 0
    for rec in r.iterRecords():
        counter += 1
    print(counter)
    geom = r.shape(0)
    print(geom.points)