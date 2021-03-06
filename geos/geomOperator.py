#!/usr/bin/env python
# encoding: utf-8
'''
使用ge
@author: DaiH
@date: 2018/6/20 18:13
'''

from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import LinearRing
from shapely.geometry import Polygon
from shapely.geometry import MultiPoint
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPolygon
from shapely.geometry import asPoint
from shapely.geometry import asLineString
from shapely.geometry import asLinearRing
from shapely.geometry import asPolygon
from shapely.geometry import asMultiPoint
from shapely.geometry import asMultiLineString
from shapely.geometry import asMultiPolygon
from shapely.geometry import asShape
from shapely.geometry import shape
from shapely.wkt import dumps, loads
from pprint import pprint
import json
import operator

'''
shapely geos 拓扑判断接口：
Unary Predicates:
object.has_z
object.is_ccw  是否counter-clockwise（逆时针）
object.is_empty
object.is_ring  Returns True if the feature is closed.
object.is_simple  Returns True if the feature does not cross itself.
object.is_valid  Returns True if a feature is “valid” in the sense of

Binary Predicates:
# Returns True if the set-theoretic boundary, interior, and exterior of the object coincide with those of the other.
object.equals(other) 
# Returns True if the object is approximately equal to the other at all points to specified decimal place precision.
object.almost_equals(other[, decimal=6])
# Returns True if no points of other lie in the exterior of the object 
# and at least one point of the interior of other lies in the interior of object.
object.contains(other) 
# Returns True if the interior of the object intersects the interior of the other but does not contain it, 
# and the dimension of the intersection is less than the dimension of the one or the other.
object.crosses(other)
# Returns True if the boundary and interior of the object do not intersect at all with those of the other.
object.disjoint(other)
# Returns True if the boundary or interior of the object intersect in any way with those of the other.
object.intersects(other)
# Returns True if the object’s boundary and interior intersect only with the interior of the other (not its boundary or exterior).
object.within(other)

object.difference(other)
exp:
a = Point(1, 1).buffer(1.5)
b = Point(2, 1).buffer(1.5)
a.difference(b)

object.intersection(other)
exp:
a = Point(1, 1).buffer(1.5)
b = Point(2, 1).buffer(1.5)
a.intersection(b)

object.symmetric_difference(other)
exp:
a = Point(1, 1).buffer(1.5)
b = Point(2, 1).buffer(1.5)
a.symmetric_difference(b)

object.union(other)
exp:
a = Point(1, 1).buffer(1.5)
b = Point(2, 1).buffer(1.5)
a.union(b)

'''
def wktToGeom():
    wktPoly = "POLYGON((0 0,4 0,4 4,0 4,0 0),(1 1, 2 1, 2 2, 1 2,1 1))"
    poly = loads(wktPoly)
    print(poly.area)
    print(poly.wkt)

def intersection(geomA, geomB):
    return geomA.intersection(geomB)

def geojsonToGeom():
    print('json/geojson to geometry')
    geojsonPath = 'E:/PycharmProject/gdalpython2/testdata/out/shptojson.json'
    geojsonFile = open(geojsonPath, 'r')
    geojson = geojsonFile.read()

    featuresJson = json.loads(geojson)
    features = featuresJson['features']
    for feature in features:
        geometry = feature['geometry']
        type = geometry['type'].lower()

        if operator.eq(type, 'multipolygon'):
            length = len(geometry['coordinates'])

            print('multipolygon coords length: ' + str(length))
        else:
            length = len(geometry['coordinates'])
            polygon1 = shape(geometry)  #shape: Returns a new, independent geometry with coordinates copied from the context.
            polygon = asShape(geometry) #asShape: Adapts the context to a geometry interface. The coordinates remain stored in the context.
            if length > 1:
                print('polygon coords length: ' + str(length))


    print('ass')







if __name__ == '__main__':
    a = Point(1, 1).buffer(1.5)
    b = Point(2, 1).buffer(1.5)
    intersecter = intersection(a, b)

    wkt = dumps(intersecter)

    pprint('**: ' + wkt)
    pprint(intersecter)

    geojsonToGeom()
