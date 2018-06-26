#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/6/25 10:35
'''

import os
import sys
from osgeo import ogr

def wkt2ogr(shpPath):
    shape = ogr.Open(shpPath)
    layer = shape.GetLayer()
    feature = layer.GetNextFeature()
    geom = feature.GetGeometryRef()
    wkt = geom.ExportToWkt()
    # View the WKT
    print(wkt)
    # Ingest the WKT we made and check the envelope
    poly = ogr.CreateGeometryFromWkt(wkt)
    print(poly.GetEnvelope())

def json2Geom():
    # Parse GeoJson data
    jsdata = """{ 
    "type": "Feature", 
    "id": "OpenLayers.Feature.Vector_314", 
    "properties": {}, 
    "geometry": { 
        "type": "Point", 
        "coordinates": [ 97.03125, 39.7265625 ] 
    }, 
    "crs": { 
        "type": "name", 
        "properties": { 
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84" 
        } 
    } 
    }"""
    # Try to eval() the data
    point = eval(jsdata)
    print(point["geometry"])
    # Use the json module
    import json
    print(json.loads(jsdata))
    # Parse and then dump GeoJSON
    pydata = json.loads(jsdata)
    print(json.dumps(pydata))

def geojsonWkt():
    import geojson
    p = geojson.Point([-92, 37])
    geojs = geojson.dumps(p)
    print(geojs)
    # Use __geo_interface__ between geojson and shapely
    from shapely.geometry import asShape
    point = asShape(p)
    print(point.wkt)


# Examine a shapefile with pyshp     import shapefile
import shapefile
shp = shapefile.Reader("point")
for feature in shp.shapeRecords():
    point = feature.shape.points[0]
    rec = feature.record[0]
    print(point[0], point[1], rec)

# Examine and update a dbf file with dbfpy
from dbfpy import dbf
def dbfRead():
    db = dbf.Dbf("GIS_CensusTract_poly.dbf")
    print(db[0])
    rec = db[0]
    field = rec["POPULAT10"]
    rec["POPULAT10"] = field
    rec["POPULAT10"] = field+1
    rec.store()
    del rec
    print(db[0]["POPULAT10"])


# Numpy/gdalnumeric - Read an image, extract a band, save a new image
from osgeo import gdalnumeric
def gdalNum():
    srcArray = gdalnumeric.LoadFile("SatImage.tif")
    band1 = srcArray[0]
    gdalnumeric.SaveArray(band1, "band1.jpg", format="JPEG")


# Rasterize a shapefile with PNGCanvas
import shapefile
import pngcanvas
def shp2Png():
    r = shapefile.Reader("hancock.shp")
    xdist = r.bbox[2] - r.bbox[0]
    ydist = r.bbox[3] - r.bbox[1]
    iwidth = 400
    iheight = 600
    xratio = iwidth / xdist
    yratio = iheight / ydist
    pixels = []
    for x, y in r.shapes()[0].points:
        px = int(iwidth - ((r.bbox[2] - x) * xratio))
        py = int((r.bbox[3] - y) * yratio)
        pixels.append([px, py])
    c = pngcanvas.PNGCanvas(iwidth, iheight)
    c.polyline(pixels)
    f = open("hancock_pngcvs.png", "wb")
    f.write(c.dump())
    f.close()

if __name__ == '__main__':
    root = os.getcwd()
    print('root: ' + root)

    shpPath = sys.path[0]
    print('shpPath: ' + shpPath)

    parent1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    parent2 = os.path.abspath(os.path.dirname(__file__) + os.path.sep + '..')
    print('praent1: ' + parent1 + '\n' + 'parent2: ' + parent2)

    shpPath = parent1 + '/testdata/TestPolygon.shp'
    # wkt2ogr(shpPath)

    json2Geom()
    geojsonWkt()