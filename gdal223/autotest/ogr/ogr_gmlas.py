#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# $Id: ogr_gmlas.py 40973 2017-12-07 17:03:50Z rouault $
#
# Project:  GDAL/OGR Test Suite
# Purpose:  GMLAS driver testing.
# Author:   Even Rouault, <even dot rouault at spatialys dot com>
#
# Initial development funded by the European Earth observation programme
# Copernicus
#
#******************************************************************************
# Copyright (c) 2016, Even Rouault, <even dot rouault at spatialys dot com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

try:
    from BaseHTTPServer import BaseHTTPRequestHandler
except:
    from http.server import BaseHTTPRequestHandler

import os
import os.path
import sys

sys.path.append( '../pymod' )

import gdaltest
import ogrtest
import webserver

from osgeo import gdal
from osgeo import ogr


###############################################################################

def compare_ogrinfo_output(gmlfile, reffile, options = ''):

    import test_cli_utilities

    if test_cli_utilities.get_ogrinfo_path() is None:
        return 'skip'

    tmpfilename = 'tmp/' + os.path.basename(gmlfile) + '.txt'
    ret = gdaltest.runexternal(test_cli_utilities.get_ogrinfo_path() +
        ' -ro -al GMLAS:' + gmlfile +
        ' -oo EXPOSE_METADATA_LAYERS=YES '+
        '-oo @KEEP_RELATIVE_PATHS_FOR_METADATA=YES '+
        '-oo @EXPOSE_SCHEMAS_NAME_IN_METADATA=NO ' +
        '-oo @EXPOSE_CONFIGURATION_IN_METADATA=NO' + ' ' + options,
        encoding = 'utf-8')
    ret = ret.replace('\r\n', '\n')
    ret = ret.replace('data\\gmlas\\', 'data/gmlas/') # Windows
    expected = open(reffile, 'rb').read().decode('utf-8')
    expected = expected.replace('\r\n', '\n')
    if ret != expected:
        gdaltest.post_reason('fail')
        print('Got:')
        print(ret)
        open(tmpfilename, 'wb').write(ret.encode('utf-8'))
        print('Diff:')
        os.system('diff -u ' + reffile + ' ' + tmpfilename)
        #os.unlink(tmpfilename)
        return 'fail'
    return 'success'

###############################################################################
# Basic test

def ogr_gmlas_basic():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    gdal.SetConfigOption('GMLAS_WARN_UNEXPECTED', 'YES')

    # FileGDB embedded libxml2 cause random crashes with CPLValidateXML() use of external libxml2
    ogrtest.old_val_GDAL_XML_VALIDATION = gdal.GetConfigOption('GDAL_XML_VALIDATION')
    if ogr.GetDriverByName('FileGDB') is not None and ogrtest.old_val_GDAL_XML_VALIDATION is None:
        gdal.SetConfigOption('GDAL_XML_VALIDATION', 'NO')

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_test1.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    # Skip tests when -fsanitize is used
    if gdaltest.is_travis_branch('sanitize'):
       print('Skipping because of -sanitize')
       return 'skip'

    return compare_ogrinfo_output('data/gmlas/gmlas_test1.xml',
                                  'data/gmlas/gmlas_test1.txt')


    return 'success'

###############################################################################
# Run test_ogrsf

def ogr_gmlas_test_ogrsf():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # Skip tests when -fsanitize is used
    if gdaltest.is_travis_branch('sanitize'):
       print('Skipping because of -sanitize')
       return 'skip'

    import test_cli_utilities

    if test_cli_utilities.get_test_ogrsf_path() is None:
        return 'skip'

    ret = gdaltest.runexternal(test_cli_utilities.get_test_ogrsf_path() + ' -ro GMLAS:data/gmlas/gmlas_test1.xml')

    if ret.find('INFO') == -1 or ret.find('ERROR') != -1:
        print(ret)
        return 'fail'

    return 'success'

###############################################################################
# Test virtual file support

def ogr_gmlas_virtual_file():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_8.xml',
"""<myns:main_elt xmlns:myns="http://myns"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://myns ogr_gmlas_8.xsd"/>""")

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_8.xsd',
"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:myns="http://myns"
           targetNamespace="http://myns"
           elementFormDefault="qualified" attributeFormDefault="unqualified">
<xs:element name="main_elt" type="xs:string"/>
</xs:schema>""")


    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_8.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    gdal.Unlink('/vsimem/ogr_gmlas_8.xml')
    gdal.Unlink('/vsimem/ogr_gmlas_8.xsd')

    return 'success'

###############################################################################
# Test opening with XSD option

def ogr_gmlas_datafile_with_xsd_option():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['XSD=data/gmlas/gmlas_test1.xsd'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################
# Test opening with just XSD option

def ogr_gmlas_no_datafile_with_xsd_option():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_test1.xsd'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################
# Test opening with just XSD option but pointing to a non-xsd filename

def ogr_gmlas_no_datafile_xsd_which_is_not_xsd():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_test1.xml'])
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find("invalid content in 'schema' element") < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test opening with nothing

def ogr_gmlas_no_datafile_no_xsd():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:')
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find('XSD open option must be provided when no XML data file is passed') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test opening an inexisting GML file

def ogr_gmlas_non_existing_gml():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:/vsimem/i_do_not_exist.gml')
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find('Cannot open /vsimem/i_do_not_exist.gml') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test opening with just XSD option but pointing to a non existing file

def ogr_gmlas_non_existing_xsd():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=/vsimem/i_do_not_exist.xsd'])
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find('Cannot resolve /vsimem/i_do_not_exist.xsd') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test opening a GML file without schemaLocation

def ogr_gmlas_gml_without_schema_location():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_gml_without_schema_location.xml',
"""<MYNS:main_elt xmlns:MYNS="http://myns"/>""")

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_gml_without_schema_location.xml')
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find('No schema locations found when analyzing data file: XSD open option must be provided') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    gdal.Unlink('/vsimem/ogr_gmlas_gml_without_schema_location.xml')

    return 'success'

###############################################################################
# Test invalid schema

def ogr_gmlas_invalid_schema():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_invalid_schema.xml')
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find('invalid content') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test invalid XML

def ogr_gmlas_invalid_xml():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_invalid_xml.xml')
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if gdal.GetLastErrorMsg().find('input ended before all started tags were ended') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test links with gml:ReferenceType

def ogr_gmlas_gml_Reference():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_test_targetelement.xml')
    if ds.GetLayerCount() != 3:
        gdaltest.post_reason('fail')
        print(ds.GetLayerCount())
        return 'fail'

    lyr = ds.GetLayerByName('main_elt')
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f['reference_existing_target_elt_with_required_id_href'] != '#BAZ' or \
       f['reference_existing_target_elt_with_required_id_pkid'] != 'BAZ' or \
       f['reference_existing_target_elt_with_optional_id_href'] != '#BAZ2' or \
       f['refe_exis_targ_elt_with_opti_id_targe_elt_with_optio_id_pkid'] != 'F36BAD21BD2F14DDCA8852DBF8C90DBC_target_elt_with_optional_id_1' or \
       f['reference_existing_abstract_target_elt_href'] != '#BAW' or \
       f.IsFieldSet('reference_existing_abstract_target_elt_nillable_href') or \
       f['reference_existing_abstract_target_elt_nillable_nil'] != 1:
           gdaltest.post_reason('fail')
           f.DumpReadable()
           return 'fail'

    return 'success'

###############################################################################
# Test that we fix ambiguities in class names

def ogr_gmlas_same_element_in_different_ns():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_same_element_in_different_ns.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    #for i in range(ds.GetLayerCount()):
    #    print(ds.GetLayer(i).GetName())

    if ds.GetLayerCount() != 5:
        gdaltest.post_reason('fail')
        print(ds.GetLayerCount())
        return 'fail'
    lyr = ds.GetLayerByName('elt')
    f = lyr.GetNextFeature()
    if f.IsFieldSet('abstractElt_other_ns_realizationOfAbstractElt_pkid') == 0:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if ds.GetLayerByName('myns_realizationOfAbstractElt') is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if ds.GetLayerByName('other_ns_realizationOfAbstractElt') is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if ds.GetLayerByName('elt_elt2_abstractElt_myns_realizationOfAbstractElt') is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if ds.GetLayerByName('elt_elt2_abstractElt_other_ns_realizationOfAbstractElt') is None:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################
# Test a corner case of relative path resolution

def ogr_gmlas_corner_case_relative_path():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = ogr.Open('GMLAS:../ogr/data/gmlas/gmlas_test1.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################
# Test unexpected repeated element

def ogr_gmlas_unexpected_repeated_element():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_unexpected_repeated_element.xml')
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f is None or f['foo'] != 'foo_again': # somewhat arbitrary to keep the latest one!
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if gdal.GetLastErrorMsg().find('Unexpected element myns:main_elt/myns:foo') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'
    f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    return 'success'

###############################################################################
# Test unexpected repeated element

def ogr_gmlas_unexpected_repeated_element_variant():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_unexpected_repeated_element_variant.xml')
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f is None or f['foo'] != 'foo_again': # somewhat arbitrary to keep the latest one!
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if gdal.GetLastErrorMsg().find('Unexpected element myns:main_elt/myns:foo') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'
    f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    return 'success'

###############################################################################
# Test reading geometries embedded in a geometry property element

def ogr_gmlas_geometryproperty():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32.gml', open_options = [
            'CONFIG_FILE=<Configuration><LayerBuildingRules><GML><IncludeGeometryXML>true</IncludeGeometryXML></GML></LayerBuildingRules></Configuration>'])
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        geom_field_count = lyr.GetLayerDefn().GetGeomFieldCount()
    if geom_field_count != 15:
        gdaltest.post_reason('fail')
        print(geom_field_count)
        return 'fail'
    f = lyr.GetNextFeature()
    if f['geometryProperty_xml'] != ' <gml:Point gml:id="poly.geom.Geometry" srsName="urn:ogc:def:crs:EPSG::4326"> <gml:pos>49 2</gml:pos> </gml:Point> ':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if not f.IsFieldNull('geometryPropertyEmpty_xml'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if f['pointProperty_xml'] != '<gml:Point gml:id="poly.geom.Point"><gml:pos srsName="http://www.opengis.net/def/crs/EPSG/0/4326">50 3</gml:pos></gml:Point>':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if f['pointPropertyRepeated_xml'] != [
            '<gml:Point gml:id="poly.geom.pointPropertyRepeated.1"><gml:pos>0 1</gml:pos></gml:Point>',
            '<gml:Point gml:id="poly.geom.pointPropertyRepeated.2"><gml:pos>1 2</gml:pos></gml:Point>',
            '<gml:Point gml:id="poly.geom.pointPropertyRepeated.3"><gml:pos>3 4</gml:pos></gml:Point>']:
        gdaltest.post_reason('fail')
        print(f['pointPropertyRepeated_xml'])
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryProperty')
    sr = lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetSpatialRef()
    if sr is None or sr.ExportToWkt().find('4326') < 0 or sr.ExportToWkt().find('AXIS') >= 0:
        gdaltest.post_reason('fail')
        print(sr)
        return 'fail'
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    # Axis swapping
    if wkt != 'POINT (2 49)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryPropertyEmpty')
    if f.GetGeomFieldRef(geom_idx) is not None:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('pointProperty')
    sr = lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetSpatialRef()
    if sr is None or sr.ExportToWkt().find('4326') < 0 or sr.ExportToWkt().find('AXIS') >= 0:
        gdaltest.post_reason('fail')
        print(sr)
        return 'fail'
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    if wkt != 'POINT (3 50)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('lineStringProperty')
    sr = lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetSpatialRef()
    if sr is None or sr.ExportToWkt().find('4326') < 0 or sr.ExportToWkt().find('AXIS') >= 0:
        gdaltest.post_reason('fail')
        print(sr)
        return 'fail'
    if lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetType() != ogr.wkbLineString:
        gdaltest.post_reason('fail')
        print(lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetType())
        return 'fail'
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    if wkt != 'LINESTRING (2 49)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('pointPropertyRepeated')
    if lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetType() != ogr.wkbUnknown:
        gdaltest.post_reason('fail')
        print(lyr.GetLayerDefn().GetGeomFieldDefn(geom_idx).GetType())
        return 'fail'
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    if wkt != 'GEOMETRYCOLLECTION (POINT (0 1),POINT (1 2),POINT (3 4))':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('mycustompointproperty_point')
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    if wkt != 'POINT (5 6)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    # Test that on-the-fly reprojection works
    f = lyr.GetNextFeature()
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryProperty')
    geom = f.GetGeomFieldRef(geom_idx)
    if ogrtest.check_feature_geometry(geom, 'POINT (3.0 0.0)') != 0:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    # Failed reprojection
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryProperty')
    if f.GetGeomFieldRef(geom_idx) is not None:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    # Test SWAP_COORDINATES=NO
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32.gml',
                     open_options= ['SWAP_COORDINATES=NO'])
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryProperty')
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    # Axis swapping
    if wkt != 'POINT (49 2)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('lineStringProperty')
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    # Axis swapping
    if wkt != 'LINESTRING (2 49)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    # Test SWAP_COORDINATES=YES
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32.gml',
                     open_options= ['SWAP_COORDINATES=YES'])
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryProperty')
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    # Axis swapping
    if wkt != 'POINT (2 49)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('lineStringProperty')
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    # Axis swapping
    if wkt != 'LINESTRING (49 2)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test reading geometries referenced by a AbstractGeometry element

def ogr_gmlas_abstractgeometry():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_abstractgeometry_gml32.gml', open_options = [
            'CONFIG_FILE=<Configuration><LayerBuildingRules><GML><IncludeGeometryXML>true</IncludeGeometryXML></GML></LayerBuildingRules></Configuration>'])
    lyr = ds.GetLayer(0)
    if lyr.GetLayerDefn().GetGeomFieldCount() != 2:
        gdaltest.post_reason('fail')
        print(lyr.GetLayerDefn().GetGeomFieldCount())
        return 'fail'
    f = lyr.GetNextFeature()
    if f['AbstractGeometry_xml'] != '<gml:Point gml:id="test.geom.0"><gml:pos>0 1</gml:pos></gml:Point>':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if f['repeated_AbstractGeometry_xml'] != [
            '<gml:Point gml:id="test.geom.repeated.1"><gml:pos>0 1</gml:pos>',
            '<gml:Point gml:id="test.geom.repeated.2"><gml:pos>1 2</gml:pos>']:
        gdaltest.post_reason('fail')
        print(f['repeated_AbstractGeometry_xml'])
        f.DumpReadable()
        return 'fail'
    wkt = f.GetGeomFieldRef(0).ExportToWkt()
    if wkt != 'POINT (0 1)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    wkt = f.GetGeomFieldRef(1).ExportToWkt()
    if wkt != 'GEOMETRYCOLLECTION (POINT (0 1),POINT (1 2))':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test validation against schema

class MyHandler:
    def __init__(self):
        self.error_list = []

    def error_handler(self, err_type, err_no, err_msg):
        if err_type != 1: # 1 == Debug
            self.error_list.append((err_type, err_no, err_msg))

def ogr_gmlas_validate():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # By default check we are silent about validation error
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_validate.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    gdal.SetConfigOption('GMLAS_WARN_UNEXPECTED', None)
    lyr = ds.GetLayer(0)
    lyr.GetFeatureCount()
    gdal.SetConfigOption('GMLAS_WARN_UNEXPECTED', 'YES')
    gdal.PopErrorHandler()
    if len(myhandler.error_list) != 0:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_validate.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    lyr = ds.GetLayer(0)
    lyr.GetFeatureCount()
    gdal.PopErrorHandler()
    # Unexpected element with xpath=myns:main_elt/myns:bar (subxpath=myns:main_elt/myns:bar) found
    if len(myhandler.error_list) < 2:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'

    # Enable validation on a doc without validation errors
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['VALIDATE=YES'])
    gdal.PopErrorHandler()
    if ds is None:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'
    if len(myhandler.error_list) != 0:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'

    # Enable validation on a doc without validation error, and with explicit XSD
    gdal.FileFromMemBuffer('/vsimem/gmlas_test1.xml',
                           open('data/gmlas/gmlas_test1.xml').read() )
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    ds = gdal.OpenEx('GMLAS:/vsimem/gmlas_test1.xml', open_options = [
                'XSD=' + os.getcwd() + '/data/gmlas/gmlas_test1.xsd', 'VALIDATE=YES'])
    gdal.PopErrorHandler()
    gdal.Unlink('/vsimem/gmlas_test1.xml')
    if ds is None:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'
    if len(myhandler.error_list) != 0:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'

    # Validation errors, but do not prevent dataset opening
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_validate.xml', open_options = ['VALIDATE=YES'])
    gdal.PopErrorHandler()
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if len(myhandler.error_list) != 5:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        print(len(myhandler.error_list))
        return 'fail'

    # Validation errors and do prevent dataset opening
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_validate.xml', open_options = ['VALIDATE=YES', 'FAIL_IF_VALIDATION_ERROR=YES'])
    gdal.PopErrorHandler()
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'
    if len(myhandler.error_list) != 6:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        print(len(myhandler.error_list))
        return 'fail'

    # Test that validation without doc doesn't crash
    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_test1.xsd', 'VALIDATE=YES'])
    gdal.PopErrorHandler()
    if ds is None:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'
    if len(myhandler.error_list) != 0:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'

    return 'success'

###############################################################################
# Test correct namespace prefix handling

def ogr_gmlas_test_ns_prefix():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # The schema doesn't directly import xlink, but indirectly references it
    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_test_targetelement.xsd'])

    lyr = ds.GetLayerByName('_ogr_fields_metadata')
    f = lyr.GetNextFeature()
    if f['field_xpath'] != 'myns:main_elt/myns:reference_missing_target_elt/@xlink:href':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test parsing documents without namespace

def ogr_gmlas_no_namespace():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_no_namespace.xml')
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['foo'] != 'bar':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test CONFIG_FILE

def ogr_gmlas_conf():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # Non existing file
    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['CONFIG_FILE=not_existing'])
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'

    # Broken conf file
    gdal.FileFromMemBuffer('/vsimem/my_conf.xml', "<broken>")
    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['CONFIG_FILE=/vsimem/my_conf.xml'])
    gdal.Unlink('/vsimem/my_conf.xml')
    if ds is not None:
        gdaltest.post_reason('fail')
        return 'fail'

    # Valid XML, but not validating
    gdal.FileFromMemBuffer('/vsimem/my_conf.xml', "<not_validating/>")
    with gdaltest.error_handler():
        gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['CONFIG_FILE=/vsimem/my_conf.xml'])
    gdal.Unlink('/vsimem/my_conf.xml')

    # Inlined conf file + UseArrays = false
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = [
            'CONFIG_FILE=<Configuration><LayerBuildingRules><UseArrays>false</UseArrays></LayerBuildingRules></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayerByName('main_elt_string_array')
    if lyr.GetFeatureCount() != 2:
        gdaltest.post_reason('fail')
        return 'fail'

    # AlwaysGenerateOGRId = true
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = [
            'CONFIG_FILE=<Configuration><LayerBuildingRules><AlwaysGenerateOGRId>true</AlwaysGenerateOGRId></LayerBuildingRules></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayerByName('main_elt')
    f = lyr.GetNextFeature()
    if f['ogr_pkid'].find('main_elt_1') < 0 or \
       f['otherns_id'] != 'otherns_id':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    # IncludeGeometryXML = false
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32.gml', open_options = [
            'CONFIG_FILE=<Configuration><LayerBuildingRules><GML><IncludeGeometryXML>false</IncludeGeometryXML></GML></LayerBuildingRules></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        if lyr.GetLayerDefn().GetFieldIndex('geometryProperty_xml') >= 0:
            gdaltest.post_reason('fail')
            return 'fail'
    f = lyr.GetNextFeature()
    geom_idx = lyr.GetLayerDefn().GetGeomFieldIndex('geometryProperty')
    wkt = f.GetGeomFieldRef(geom_idx).ExportToWkt()
    if wkt != 'POINT (2 49)':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    # ExposeMetadataLayers = true
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_abstractgeometry_gml32.gml', open_options = [
            'CONFIG_FILE=<Configuration><ExposeMetadataLayers>true</ExposeMetadataLayers></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if ds.GetLayerCount() != 5:
        gdaltest.post_reason('fail')
        print(ds.GetLayerCount())
        return 'fail'
    # Test override with open option
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_abstractgeometry_gml32.gml', open_options = [
            'EXPOSE_METADATA_LAYERS=NO',
            'CONFIG_FILE=<Configuration><ExposeMetadataLayers>true</ExposeMetadataLayers></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        print(ds.GetLayerCount())
        return 'fail'

    # Turn on validation and error on validation
    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_validate.xml', open_options = [
            'CONFIG_FILE=<Configuration><Validation enabled="true"><FailIfError>true</FailIfError></Validation></Configuration>'])
    if ds is not None or gdal.GetLastErrorMsg().find('Validation') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    return 'success'

###############################################################################
# Test IgnoredXPaths aspect of config file

def ogr_gmlas_conf_ignored_xpath():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # Test unsupported and invalid XPaths
    for xpath in [ '',
                   '1',
                   '@',
                   '@/',
                   '.',
                   ':',
                   '/:',
                   'a:',
                   'a:1',
                   'foo[1]',
                   "foo[@bar='baz']" ]:
        with gdaltest.error_handler():
            gdal.OpenEx('GMLAS:', open_options = [
                    'XSD=data/gmlas/gmlas_test1.xsd',
                    """CONFIG_FILE=<Configuration>
                        <IgnoredXPaths>
                            <WarnIfIgnoredXPathFoundInDocInstance>true</WarnIfIgnoredXPathFoundInDocInstance>
                            <XPath>%s</XPath>
                        </IgnoredXPaths>
                    </Configuration>""" % xpath])
        if gdal.GetLastErrorMsg().find('XPath syntax') < 0:
            gdaltest.post_reason('fail')
            print(xpath)
            print(gdal.GetLastErrorMsg())
            return 'fail'

    # Test duplicating mapping
    with gdaltest.error_handler():
        gdal.OpenEx('GMLAS:', open_options = [
                    'XSD=data/gmlas/gmlas_test1.xsd',
                """CONFIG_FILE=<Configuration>
                    <IgnoredXPaths>
                        <Namespaces>
                            <Namespace prefix="ns" uri="http://ns1"/>
                            <Namespace prefix="ns" uri="http://ns2"/>
                        </Namespaces>
                    </IgnoredXPaths>
                </Configuration>"""])
    if gdal.GetLastErrorMsg().find('Prefix ns was already mapped') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Test XPath with implicit namespace, and warning
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = [
            """CONFIG_FILE=<Configuration>
                <IgnoredXPaths>
                    <WarnIfIgnoredXPathFoundInDocInstance>true</WarnIfIgnoredXPathFoundInDocInstance>
                    <XPath>@otherns:id</XPath>
                </IgnoredXPaths>
            </Configuration>"""])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayerByName('main_elt')
    if lyr.GetLayerDefn().GetFieldIndex('otherns_id') >= 0:
        gdaltest.post_reason('fail')
        return 'fail'
    with gdaltest.error_handler():
        lyr.GetNextFeature()
    if gdal.GetLastErrorMsg().find('Attribute with xpath=myns:main_elt/@otherns:id found in document but ignored') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Test XPath with explicit namespace, and warning suppression
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = [
            """CONFIG_FILE=<Configuration>
                <IgnoredXPaths>
                    <Namespaces>
                        <Namespace prefix="other_ns" uri="http://other_ns"/>
                    </Namespaces>
                    <XPath warnIfIgnoredXPathFoundInDocInstance="false">@other_ns:id</XPath>
                </IgnoredXPaths>
            </Configuration>"""])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayerByName('main_elt')
    lyr.GetNextFeature()
    if gdal.GetLastErrorMsg() != '':
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Test various XPath syntaxes
    ds = gdal.OpenEx('GMLAS:', open_options = [
                    'XSD=data/gmlas/gmlas_test1.xsd',
            """CONFIG_FILE=<Configuration>
                <IgnoredXPaths>
                    <WarnIfIgnoredXPathFoundInDocInstance>false</WarnIfIgnoredXPathFoundInDocInstance>
                    <XPath>myns:main_elt/@optionalStrAttr</XPath>
                    <XPath>myns:main_elt//@fixedValUnset</XPath>
                    <XPath>myns:main_elt/myns:base_int</XPath>
                    <XPath>//myns:string</XPath>
                    <XPath>myns:main_elt//myns:string_array</XPath>

                    <XPath>a</XPath> <!-- no match -->
                    <XPath>unknown_ns:foo</XPath> <!-- no match -->
                    <XPath>myns:main_elt/myns:int_arra</XPath> <!-- no match -->
                    <XPath>foo/myns:long</XPath> <!-- no match -->
                </IgnoredXPaths>
            </Configuration>"""])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayerByName('main_elt')

    # Ignored fields
    if lyr.GetLayerDefn().GetFieldIndex('optionalStrAttr') >= 0:
        gdaltest.post_reason('fail')
        return 'fail'
    if lyr.GetLayerDefn().GetFieldIndex('fixedValUnset') >= 0:
        gdaltest.post_reason('fail')
        return 'fail'
    if lyr.GetLayerDefn().GetFieldIndex('base_int') >= 0:
        gdaltest.post_reason('fail')
        return 'fail'
    if lyr.GetLayerDefn().GetFieldIndex('string') >= 0:
        gdaltest.post_reason('fail')
        return 'fail'
    if lyr.GetLayerDefn().GetFieldIndex('string_array') >= 0:
        gdaltest.post_reason('fail')
        return 'fail'

    # Present fields
    if lyr.GetLayerDefn().GetFieldIndex('int_array') < 0:
        gdaltest.post_reason('fail')
        return 'fail'
    if lyr.GetLayerDefn().GetFieldIndex('long') < 0:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################

do_log = False
class GMLASHTTPHandler(BaseHTTPRequestHandler):

    def log_request(self, code='-', size='-'):
        return

    def do_GET(self):

        try:
            if do_log:
                f = open('/tmp/log.txt', 'a')
                f.write('GET %s\n' % self.path)
                f.close()

            if self.path.startswith('/vsimem/'):
                from osgeo import gdal
                f = gdal.VSIFOpenL(self.path, "rb")
                if f is None:
                    self.send_response(404)
                    self.end_headers()
                else:
                    gdal.VSIFSeekL(f, 0, 2)
                    size = gdal.VSIFTellL(f)
                    gdal.VSIFSeekL(f, 0, 0)
                    content = gdal.VSIFReadL(1, size, f)
                    gdal.VSIFCloseL(f)
                    self.protocol_version = 'HTTP/1.0'
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(content)
                return

            return
        except IOError:
            pass

        self.send_error(404,'File Not Found: %s' % self.path)

###############################################################################
# Test schema caching

def ogr_gmlas_cache():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    try:
        drv = gdal.GetDriverByName( 'HTTP' )
    except:
        drv = None

    if drv is None:
        return 'skip'

    (webserver_process, webserver_port) = webserver.launch(handler = GMLASHTTPHandler)
    if webserver_port == 0:
        return 'skip'

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_cache.xml',
"""<main_elt xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:noNamespaceSchemaLocation="http://localhost:%d/vsimem/ogr_gmlas_cache.xsd">
    <foo>bar</foo>
</main_elt>
""" % webserver_port )

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_cache.xsd',
"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           elementFormDefault="qualified" attributeFormDefault="unqualified">
<xs:include schemaLocation="ogr_gmlas_cache_2.xsd"/>
</xs:schema>""")

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_cache_2.xsd',
"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           elementFormDefault="qualified" attributeFormDefault="unqualified">
<xs:element name="main_elt">
  <xs:complexType>
    <xs:sequence>
        <xs:element name="foo" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>
</xs:element>
</xs:schema>""")

    # First try with remote schema download disabled
    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'CONFIG_FILE=<Configuration><AllowRemoteSchemaDownload>false</AllowRemoteSchemaDownload><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is not None or gdal.GetLastErrorMsg().find('Cannot resolve') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Test invalid cache directory
    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/inexisting_directory/not/exist</Directory></SchemaCache></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        print(ds.GetLayerCount())
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    # Will create the directory and download and cache
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        print(ds.GetLayerCount())
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    gdal.Unlink('/vsimem/my/gmlas_cache/' + gdal.ReadDir('/vsimem/my/gmlas_cache')[0])

    # Will reuse the directory and download and cache
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    # With XSD open option
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'XSD=http://localhost:%d/vsimem/ogr_gmlas_cache.xsd' % webserver_port,
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    webserver.server_stop(webserver_process, webserver_port)

    # Now re-open with the webserver turned off
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        return 'fail'

    # Re try but ask for refresh
    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'REFRESH_CACHE=YES',
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is not None or gdal.GetLastErrorMsg().find('Cannot resolve') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    # Re try with non existing cached schema
    gdal.Unlink('/vsimem/my/gmlas_cache/' + gdal.ReadDir('/vsimem/my/gmlas_cache')[0])

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_cache.xml', open_options = [
            'CONFIG_FILE=<Configuration><SchemaCache><Directory>/vsimem/my/gmlas_cache</Directory></SchemaCache></Configuration>'])
    if ds is not None or gdal.GetLastErrorMsg().find('Cannot resolve') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Cleanup
    gdal.Unlink('/vsimem/ogr_gmlas_cache.xml')
    gdal.Unlink('/vsimem/ogr_gmlas_cache.xsd')
    gdal.Unlink('/vsimem/ogr_gmlas_cache_2.xsd')

    files = gdal.ReadDir('/vsimem/my/gmlas_cache')
    for my_file in files:
        gdal.Unlink('/vsimem/my/gmlas_cache/' + my_file)
    gdal.Rmdir('/vsimem/my/gmlas_cache')
    gdal.Rmdir('/vsimem/my')

    return 'success'


###############################################################################
# Test good working of linking to a child through its id attribute

def ogr_gmlas_link_nested_independant_child():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_link_nested_independant_child.xml')
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['second_my_id'] != 'second_id':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test some pattern found in geosciml schemas

def ogr_gmlas_composition_compositionPart():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_composition_compositionPart.xml')

    lyr = ds.GetLayerByName('first_composition')
    f = lyr.GetNextFeature()
    if f.IsFieldSet('parent_ogr_pkid') == 0 or f.IsFieldSet('CompositionPart_pkid') == 0:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f.IsFieldSet('parent_ogr_pkid') == 0 or f.IsFieldSet('CompositionPart_pkid') == 0:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('CompositionPart')
    f = lyr.GetNextFeature()
    if f.IsFieldSet('my_id') == 0 or f.IsFieldSet('a') == 0:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f.IsFieldSet('my_id') == 0 or f.IsFieldSet('a') == 0:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test that when importing GML we expose by default only elements deriving
# from _Feature/AbstractFeature

def ogr_gmlas_instantiate_only_gml_feature():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:',
        open_options = ['XSD=data/gmlas/gmlas_instantiate_only_gml_feature.xsd'])
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    return 'success'

###############################################################################
# Test that WFS style timeStamp are ignored for hash generation

def ogr_gmlas_timestamp_ignored_for_hash():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_timestamp_ignored_for_hash_foo.xml')
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    pkid = f['ogr_pkid']

    ds = ogr.Open('GMLAS:data/gmlas/gmlas_timestamp_ignored_for_hash_bar.xml')
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['ogr_pkid'] != pkid:
        gdaltest.post_reason('fail')
        print(pkid)
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test dataset GetNextFeature()

def ogr_gmlas_dataset_getnextfeature():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml')

    if ds.TestCapability(ogr.ODsCRandomLayerRead) != 1:
        gdaltest.post_reason('fail')
        return 'fail'

    count = 0
    last_l = None
    while True:
        f, l = ds.GetNextFeature()
        if f is None:
            if l is not None:
                gdaltest.post_reason('fail')
                return 'fail'
            break
        count += 1
        last_l = l

    base_count = 59
    if count != base_count:
        gdaltest.post_reason('fail')
        print(count)
        return 'fail'

    if last_l.GetName() != 'main_elt':
        gdaltest.post_reason('fail')
        print(last_l.GetName())
        return 'fail'

    f, l = ds.GetNextFeature()
    if f is not None or l is not None:
        gdaltest.post_reason('fail')
        return 'fail'

    ds.ResetReading()
    last_pct =  0
    while True:
        f, l, pct = ds.GetNextFeature( include_pct = True )
        last_pct = pct
        if f is None:
            if l is not None:
                gdaltest.post_reason('fail')
                return 'fail'
            break
    if last_pct != 1.0:
        gdaltest.post_reason('fail')
        print(last_pct - 1.0)
        return 'fail'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['EXPOSE_METADATA_LAYERS=YES'])
    fc_map = {}
    for layer_name in ('_ogr_fields_metadata',
                       '_ogr_layers_metadata',
                       '_ogr_layer_relationships',
                       '_ogr_other_metadata' ):
        fc_map[layer_name] = ds.GetLayerByName(layer_name).GetFeatureCount()
    ds = None

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = ['EXPOSE_METADATA_LAYERS=YES'])
    count = 0
    while True:
        f, l = ds.GetNextFeature()
        if f is None:
            if l is not None:
                gdaltest.post_reason('fail')
                return 'fail'
            break
        count += 1

    expected_count = base_count
    expected_count += fc_map['_ogr_fields_metadata']
    expected_count += fc_map['_ogr_layers_metadata']
    expected_count += fc_map['_ogr_layer_relationships']
    expected_count += fc_map['_ogr_other_metadata']
    if count != expected_count:
        gdaltest.post_reason('fail')
        print(count)
        return 'fail'

    f, l = ds.GetNextFeature()
    if f is not None or l is not None:
        gdaltest.post_reason('fail')
        return 'fail'

    ds.ResetReading()

    count = 0
    while True:
        f, l = ds.GetNextFeature()
        if f is None:
            if l is not None:
                gdaltest.post_reason('fail')
                return 'fail'
            break
        count += 1

    if count != expected_count:
        gdaltest.post_reason('fail')
        print(count)
        print(expected_count)
        return 'fail'


    for layers in [ ['_ogr_fields_metadata'],
                    ['_ogr_layers_metadata'],
                    ['_ogr_layer_relationships'],
                    ['_ogr_fields_metadata', '_ogr_layers_metadata'],
                    ['_ogr_fields_metadata', '_ogr_layer_relationships'],
                    ['_ogr_layers_metadata', '_ogr_layer_relationships'],
                  ]:

        ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml')
        expected_count = base_count
        for layer in layers:
            ds.GetLayerByName(layer)
            expected_count += fc_map[layer]

        count = 0
        while True:
            f, l = ds.GetNextFeature()
            if f is None:
                if l is not None:
                    gdaltest.post_reason('fail')
                    return 'fail'
                break
            count += 1

        if count != expected_count:
            gdaltest.post_reason('fail')
            print(count)
            print(expected_count)
            return 'fail'

        f, l = ds.GetNextFeature()
        if f is not None or l is not None:
            gdaltest.post_reason('fail')
            return 'fail'

    # Test iterating over metadata layers on XSD-only based dataset
    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_test1.xsd', 'EXPOSE_METADATA_LAYERS=YES'])
    count = 0
    last_l = None
    while True:
        f, l = ds.GetNextFeature()
        if f is None:
            if l is not None:
                gdaltest.post_reason('fail')
                return 'fail'
            break
        count += 1
        last_l = l

    if count == 0:
        gdaltest.post_reason('fail')
        print(count)
        return 'fail'


    return 'success'

###############################################################################
#  Test that with schemas that have a structure like a base:identifier, we
# will inline it.

def ogr_gmlas_inline_identifier():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:', open_options=['XSD=data/gmlas/gmlas_inline_identifier.xsd'])
    if ds.GetLayerCount() != 2:
        gdaltest.post_reason('fail')
        print( ds.GetLayerCount() )
        for i in range( ds.GetLayerCount() ):
            print(ds.GetLayer(i).GetName())
        return 'fail'
    lyr = ds.GetLayer(0)
    if lyr.GetLayerDefn().GetFieldIndex('identifier_foo') < 0:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################
#  Test that we can handle things like gml:name and au:name

def ogr_gmlas_avoid_same_name_inlined_classes():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:', open_options=['XSD=data/gmlas/gmlas_avoid_same_name_inlined_classes.xsd'])
    if ds.GetLayerCount() != 3:
        gdaltest.post_reason('fail')
        print( ds.GetLayerCount() )
        return 'fail'
    lyr = ds.GetLayerByName('myFeature_ns1_dt')
    if lyr is None:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayerByName('myFeature_ns2_dt')
    if lyr is None:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'


###############################################################################
#  Test validation with an optional fixed attribute that is ignored

def ogr_gmlas_validate_ignored_fixed_attribute():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    myhandler = MyHandler()
    gdal.PushErrorHandler(myhandler.error_handler)
    gdal.OpenEx('GMLAS:data/gmlas/gmlas_validate_ignored_fixed_attribute.xml',
        open_options = [ 'VALIDATE=YES',
                         'CONFIG_FILE=<Configuration><IgnoredXPaths><XPath>@bar</XPath></IgnoredXPaths></Configuration>'])
    gdal.PopErrorHandler()
    if len(myhandler.error_list) != 0:
        gdaltest.post_reason('fail')
        print(myhandler.error_list)
        return 'fail'

    return 'success'


###############################################################################
#  Test REMOVE_UNUSED_LAYERS and REMOVE_UNUSED_FIELDS options

def ogr_gmlas_remove_unused_layers_and_fields():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_remove_unused_layers_and_fields.xml',
                     open_options = ['REMOVE_UNUSED_LAYERS=YES',
                                     'REMOVE_UNUSED_FIELDS=YES'])
    if ds.GetLayerCount() != 1:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if lyr.GetLayerDefn().GetFieldCount() != 4:
        gdaltest.post_reason('fail')
        print(lyr.GetLayerDefn().GetFieldCount())
        f.DumpReadable()
        return 'fail'
    if f['used1'] != 'foo' or f['used2'] != 'bar' or f['nillable_nilReason'] != 'unknown':
        gdaltest.post_reason('fail')
        return 'fail'

    lyr = ds.GetLayerByName('_ogr_layers_metadata')
    if lyr.GetFeatureCount() != 1:
        gdaltest.post_reason('fail')
        for f in lyr:
            f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('_ogr_fields_metadata')
    if lyr.GetFeatureCount() != 7:
        gdaltest.post_reason('fail')
        for f in lyr:
            f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('_ogr_layer_relationships')
    if lyr.GetFeatureCount() != 0:
        gdaltest.post_reason('fail')
        for f in lyr:
            f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
#  Test xlink resolution

def ogr_gmlas_xlink_resolver():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    try:
        drv = gdal.GetDriverByName( 'HTTP' )
    except:
        drv = None

    if drv is None:
        return 'skip'

    (webserver_process, webserver_port) = webserver.launch(handler = GMLASHTTPHandler)
    if webserver_port == 0:
        return 'skip'

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_xlink_resolver.xsd',
"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
              xmlns:xlink="http://fake_xlink"
              elementFormDefault="qualified"
              attributeFormDefault="unqualified">

<xs:import namespace="http://fake_xlink" schemaLocation="ogr_gmlas_xlink_resolver_fake_xlink.xsd"/>

<xs:element name="FeatureCollection">
  <xs:complexType>
    <xs:sequence>
        <xs:element ref="main_elt" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>
</xs:element>

<xs:element name="main_elt">
  <xs:complexType>
    <xs:sequence>
        <xs:element name="my_link">
            <xs:complexType>
                <xs:sequence/>
                <xs:attribute name="attr_before" type="xs:string"/>
                <xs:attribute ref="xlink:href"/>
                <xs:attribute name="attr_after" type="xs:string"/>
            </xs:complexType>
        </xs:element>
        <xs:element name="my_link2" minOccurs="0">
            <xs:complexType>
                <xs:sequence/>
                <xs:attribute name="attr_before" type="xs:string"/>
                <xs:attribute ref="xlink:href"/>
                <xs:attribute name="attr_after" type="xs:string"/>
            </xs:complexType>
        </xs:element>
    </xs:sequence>
  </xs:complexType>
</xs:element>

</xs:schema>""")

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_xlink_resolver_fake_xlink.xsd',
                           open('data/gmlas/gmlas_fake_xlink.xsd','rb').read())

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_xlink_resolver.xml',
"""
<FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:xlink="http://fake_xlink"
          xsi:noNamespaceSchemaLocation="ogr_gmlas_xlink_resolver.xsd">
  <main_elt>
    <my_link attr_before="a" xlink:href="http://localhost:%d/vsimem/resource.xml" attr_after="b"/>
  </main_elt>
  <main_elt>
    <my_link xlink:href="http://localhost:%d/vsimem/resource2.xml"/>
  </main_elt>
</FeatureCollection>""" % (webserver_port, webserver_port))

    # By default, no resolution
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml')
    lyr = ds.GetLayer(0)
    if lyr.GetLayerDefn().GetFieldIndex('my_link_rawcontent') >= 0:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None

    # Enable resolution, but only from local cache
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <DefaultResolution enabled="true">
                <AllowRemoteDownload>false</AllowRemoteDownload>
            </DefaultResolution>
        </XLinkResolution></Configuration>"""] )
    lyr = ds.GetLayer(0)
    if lyr.GetLayerDefn().GetFieldIndex('my_link_rawcontent') < 0:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    f = lyr.GetNextFeature()
    if f.IsFieldSet('my_link_rawcontent'):
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    # Try again but this time with the cached file
    cached_file = '/vsimem/gmlas_xlink_cache/localhost_%d_vsimem_resource.xml' % webserver_port
    gdal.FileFromMemBuffer(cached_file, 'foo')
    lyr.ResetReading()
    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'foo':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None
    gdal.Unlink(cached_file)

    # Enable remote resolution (but local caching disabled)
    gdal.FileFromMemBuffer('/vsimem/resource.xml', 'bar')
    gdal.FileFromMemBuffer('/vsimem/resource2.xml', 'baz')
    gdal.SetConfigOption('GMLAS_XLINK_RAM_CACHE_SIZE', '5')
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <DefaultResolution enabled="true">
                <AllowRemoteDownload>true</AllowRemoteDownload>
            </DefaultResolution>
        </XLinkResolution></Configuration>"""] )
    gdal.SetConfigOption('GMLAS_XLINK_RAM_CACHE_SIZE', None)
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'bar':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    # Check that the content is not cached
    if gdal.VSIStatL(cached_file) is not None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    # Delete the remote file and check that we can retrieve it from RAM cache
    gdal.Unlink('/vsimem/resource.xml')
    lyr.ResetReading()
    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'bar':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'baz':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    gdal.Unlink('/vsimem/resource2.xml')
    lyr.ResetReading()
    # /vsimem/resource.xml has been evicted from the cache
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] is not None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'baz':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    ds = None

    # Enable remote resolution and caching
    gdal.FileFromMemBuffer('/vsimem/resource.xml', 'bar')
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <DefaultResolution enabled="true">
                <AllowRemoteDownload>true</AllowRemoteDownload>
                <CacheResults>true</CacheResults>
            </DefaultResolution>
        </XLinkResolution></Configuration>"""] )
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'bar':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    # Check that the content is cached
    if gdal.VSIStatL(cached_file) is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None

    # Enable remote resolution and caching and REFRESH_CACHE
    gdal.FileFromMemBuffer('/vsimem/resource.xml', 'baz')
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ['REFRESH_CACHE=YES', """CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <DefaultResolution enabled="true">
                <AllowRemoteDownload>true</AllowRemoteDownload>
                <CacheResults>true</CacheResults>
            </DefaultResolution>
        </XLinkResolution></Configuration>"""] )
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['my_link_rawcontent' ] != 'baz':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    # Check that the content is cached
    if gdal.VSIStatL(cached_file) is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None

    # Test absent remote resource
    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_xlink_resolver_absent_resource.xml',
"""
<main_elt xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:xlink="http://fake_xlink"
          xsi:noNamespaceSchemaLocation="ogr_gmlas_xlink_resolver.xsd">
    <my_link xlink:href="http://localhost:%d/vsimem/resource_not_existing.xml"/>
</main_elt>""" % webserver_port)
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver_absent_resource.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <DefaultResolution enabled="true">
                <AllowRemoteDownload>true</AllowRemoteDownload>
            </DefaultResolution>
        </XLinkResolution></Configuration>"""] )
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f.IsFieldSet('my_link_rawcontent'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None

    # Test file size limit
    gdal.Unlink(cached_file)
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <MaxFileSize>1</MaxFileSize>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <DefaultResolution enabled="true">
                <AllowRemoteDownload>true</AllowRemoteDownload>
                <CacheResults>true</CacheResults>
            </DefaultResolution>
        </XLinkResolution></Configuration>"""] )
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if gdal.GetLastErrorMsg() == '':
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    # Check that the content is not cached
    if gdal.VSIStatL(cached_file) is not None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None

    # Test with URL specific rule with RawContent resolution
    gdal.FileFromMemBuffer('/vsimem/resource.xml', 'bar')
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <URLSpecificResolution>
                <URLPrefix>http://localhost:%d/vsimem/</URLPrefix>
                <AllowRemoteDownload>true</AllowRemoteDownload>
                <ResolutionMode>RawContent</ResolutionMode>
                <CacheResults>true</CacheResults>
            </URLSpecificResolution>
        </XLinkResolution></Configuration>""" % webserver_port] )
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['my_link_attr_before'] != 'a' or \
       f['my_link_href'] != 'http://localhost:%d/vsimem/resource.xml' % webserver_port or \
       f['my_link_rawcontent'] != 'bar' or \
       f['my_link_attr_after'] != 'b':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    # Check that the content is cached
    if gdal.VSIStatL(cached_file) is None:
        gdaltest.post_reason('fail')
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'
    ds = None

    # Test with URL specific rule with FieldsFromXPath resolution
    gdal.FileFromMemBuffer('/vsimem/subdir1/resource.xml', """
<?xml version='1.0' encoding='UTF-8'?>
<myns:top>
    <myns:foo>fooVal</myns:foo>
    <myns:bar>123</myns:bar>
</myns:top>""")
    gdal.FileFromMemBuffer('/vsimem/subdir2/resource2_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_very_long.xml', """
<?xml version='1.0' encoding='UTF-8'?>
<myns:top>
    <myns:foo>fooVal2</myns:foo>
    <myns:foo>fooVal3</myns:foo>
    <myns:baz val="345"/>
    <myns:xml_blob>foo<blob/>bar</myns:xml_blob>
    <long>1234567890123</long>
    <double>1.25</double>
    <datetime>2016-10-07T12:34:56Z</datetime>
</myns:top>""")
    gdal.FileFromMemBuffer('/vsimem/non_matching_resource.xml', 'foo')

    gdal.FileFromMemBuffer('/vsimem/ogr_gmlas_xlink_resolver.xml',
"""
<FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:xlink="http://fake_xlink"
          xsi:noNamespaceSchemaLocation="ogr_gmlas_xlink_resolver.xsd">
  <main_elt>
    <my_link attr_before="a" xlink:href="http://localhost:%d/vsimem/subdir1/resource.xml" attr_after="b"/>
    <my_link2 attr_before="a2" xlink:href="http://localhost:%d/vsimem/subdir2/resource2_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_very_long.xml" attr_after="b2"/>
  </main_elt>
  <main_elt>
    <my_link attr_before="a" xlink:href="http://localhost:%d/vsimem/non_matching_resource.xml" attr_after="b"/>
    <my_link2 attr_before="a2" xlink:href="http://localhost:%d/vsimem/subdir1/resource.xml" attr_after="b2"/>
  </main_elt>
</FeatureCollection>""" % (webserver_port, webserver_port,webserver_port, webserver_port))

    config_file = """<Configuration>
        <XLinkResolution>
            <CacheDirectory>/vsimem/gmlas_xlink_cache</CacheDirectory>
            <URLSpecificResolution>
                <URLPrefix>http://localhost:%d/vsimem/subdir1</URLPrefix>
                <HTTPHeader>
                    <Name>Accept</Name>
                    <Value>application/x-iso19135+xml</Value>
                </HTTPHeader>
                <HTTPHeader>
                    <Name>Accept-Language</Name>
                    <Value>en</Value>
                </HTTPHeader>
                <AllowRemoteDownload>true</AllowRemoteDownload>
                <ResolutionMode>FieldsFromXPath</ResolutionMode>
                <CacheResults>true</CacheResults>
                <Field>
                    <Name>foo</Name>
                    <Type>string</Type>
                    <XPath>myns:top/myns:foo</XPath>
                </Field>
                <Field>
                    <Name>bar</Name>
                    <Type>integer</Type>
                    <XPath>myns:top/myns:bar</XPath>
                </Field>
            </URLSpecificResolution>
            <URLSpecificResolution>
                <URLPrefix>http://localhost:%d/vsimem/subdir2</URLPrefix>
                <AllowRemoteDownload>true</AllowRemoteDownload>
                <ResolutionMode>FieldsFromXPath</ResolutionMode>
                <CacheResults>true</CacheResults>
                <Field>
                    <Name>foo</Name>
                    <Type>string</Type>
                    <XPath>myns:top/myns:foo</XPath>
                </Field>
                <Field>
                    <Name>baz</Name>
                    <Type>integer</Type>
                    <XPath>/myns:top/myns:baz/@val</XPath>
                </Field>
                <Field>
                    <Name>xml_blob</Name>
                    <Type>string</Type>
                    <XPath>//myns:xml_blob</XPath>
                </Field>
                <Field>
                    <Name>long</Name>
                    <Type>long</Type>
                    <XPath>//long</XPath>
                </Field>
                <Field>
                    <Name>double</Name>
                    <Type>double</Type>
                    <XPath>//double</XPath>
                </Field>
                <Field>
                    <Name>datetime</Name>
                    <Type>dateTime</Type>
                    <XPath>//datetime</XPath>
                </Field>
            </URLSpecificResolution>
        </XLinkResolution></Configuration>""" % (webserver_port,webserver_port)

    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ['CONFIG_FILE=' + config_file] )
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['my_link_attr_before'] != 'a' or \
       f['my_link_href'] != 'http://localhost:%d/vsimem/subdir1/resource.xml' % webserver_port or \
       f['my_link_foo'] != 'fooVal' or \
       f['my_link_bar'] != 123 or \
       f['my_link_attr_after'] != 'b' or \
       f['my_link2_attr_before'] != 'a2' or \
       f['my_link2_href'] != 'http://localhost:%d/vsimem/subdir2/resource2_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_very_long.xml' % webserver_port or \
       f['my_link2_foo'] != 'fooVal2 fooVal3' or \
       f['my_link2_baz'] != 345 or \
       f['my_link2_xml_blob'] != """foo<blob />
bar""" or \
       f['my_link2_long'] != 1234567890123 or \
       f['my_link2_double'] != 1.25 or \
       f['my_link2_datetime'] != '2016/10/07 12:34:56+00' or \
       f['my_link2_bar'] is not None or \
       f['my_link2_attr_after'] != 'b2':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    f = lyr.GetNextFeature()
    if f['my_link2_bar'] != 123:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    gdal.Unlink('/vsimem/subdir1/resource.xml')
    gdal.Unlink('/vsimem/subdir2/resource2_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_very_long.xml')

    # Test caching
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_xlink_resolver.xml',
        open_options = ['CONFIG_FILE=' + config_file] )
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['my_link_attr_before'] != 'a' or \
       f['my_link_href'] != 'http://localhost:%d/vsimem/subdir1/resource.xml' % webserver_port or \
       f['my_link_foo'] != 'fooVal' or \
       f['my_link_bar'] != 123 or \
       f['my_link_attr_after'] != 'b' or \
       f['my_link2_attr_before'] != 'a2' or \
       f['my_link2_href'] != 'http://localhost:%d/vsimem/subdir2/resource2_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_very_long.xml' % webserver_port or \
       f['my_link2_foo'] != 'fooVal2 fooVal3' or \
       f['my_link2_baz'] != 345 or \
       f['my_link2_bar'] is not None or \
       f['my_link2_attr_after'] != 'b2':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        webserver.server_stop(webserver_process, webserver_port)
        return 'fail'

    ds = None

    webserver.server_stop(webserver_process, webserver_port)

    gdal.Unlink('/vsimem/ogr_gmlas_xlink_resolver.xsd')
    gdal.Unlink('/vsimem/ogr_gmlas_xlink_resolver_fake_xlink.xsd')
    gdal.Unlink('/vsimem/ogr_gmlas_xlink_resolver.xml')
    gdal.Unlink('/vsimem/ogr_gmlas_xlink_resolver_absent_resource.xml')
    fl = gdal.ReadDir('/vsimem/gmlas_xlink_cache')
    if fl is not None:
        for filename in fl:
            gdal.Unlink('/vsimem/gmlas_xlink_cache/' + filename)
    gdal.Unlink('/vsimem/gmlas_xlink_cache')
    gdal.Unlink('/vsimem/resource.xml')
    gdal.Unlink('/vsimem/resource2.xml')
    gdal.Unlink('/vsimem/subdir1/resource.xml')
    gdal.Unlink('/vsimem/subdir2/resource2_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_super_very_long.xml')
    gdal.Unlink('/vsimem/non_matching_resource.xml')

    return 'success'

###############################################################################
# Test UTF-8 support

def ogr_gmlas_recoding():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    if sys.version_info >= (3,0,0):
        accent = '\u00e9'
    else:
        exec("accent = u'\\u00e9'")
        accent = accent.encode('UTF-8')

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_recoding.xml')
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if f['attr'] != accent:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test schema without namespace prefix

def ogr_gmlas_schema_without_namespace_prefix():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # Generic http:// namespace URI
    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_schema_without_namespace_prefix_generic_http_uri.xsd'])
    lyr = ds.GetLayerByName('_ogr_layers_metadata')
    f = lyr.GetNextFeature()
    if f['layer_xpath'] != 'my_ns:main_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    gdal.Unlink('/vsimem/ogr_gmlas_schema_without_namespace_prefix.xsd')

    # http://www.opengis.net/ namespace URI

    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_schema_without_namespace_prefix_opengis_uri.xsd'])
    lyr = ds.GetLayerByName('_ogr_layers_metadata')
    f = lyr.GetNextFeature()
    if f['layer_xpath'] != 'fake_3_0:main_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    gdal.Unlink('/vsimem/ogr_gmlas_schema_without_namespace_prefix.xsd')

    # Non http:// namespace URI

    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_schema_without_namespace_prefix_non_http_uri.xsd'])
    lyr = ds.GetLayerByName('_ogr_layers_metadata')
    f = lyr.GetNextFeature()
    if f['layer_xpath'] != 'my_namespace:main_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test parsing truncated XML

def ogr_gmlas_truncated_xml():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_truncated_xml.xml')
    lyr = ds.GetLayer(0)
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test identifier truncation

def ogr_gmlas_identifier_truncation():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:', open_options = [
            'XSD=data/gmlas/gmlas_identifier_truncation.xsd',
            'CONFIG_FILE=<Configuration><LayerBuildingRules><IdentifierMaxLength>10</IdentifierMaxLength><PostgreSQLIdentifierLaundering>false</PostgreSQLIdentifierLaundering></LayerBuildingRules></Configuration>'])
    lyr = ds.GetLayerByName('v_l_i_clas')
    if lyr is None:
        gdaltest.post_reason('fail')
        print(ds.GetLayer(0).GetName())
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(1).GetName()
    if s != 'v_l_idTifi':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(2).GetName()
    if s != 'an_lo_ide1':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(3).GetName()
    if s != 'an_lo_ide2':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(4).GetName()
    if s != 'x':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(5).GetName()
    if s != 'noTCAMELCa':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(6).GetName()
    if s != 'suuuuuuuuu':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(7).GetName()
    if s != '_r_l_o_n_g':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    lyr = ds.GetLayerByName('a_l_i_cla1')
    if lyr is None:
        gdaltest.post_reason('fail')
        print(ds.GetLayer(1).GetName())
        return 'fail'
    lyr = ds.GetLayerByName('a_l_i_cla2')
    if lyr is None:
        gdaltest.post_reason('fail')
        print(ds.GetLayer(2).GetName())
        return 'fail'
    lyr = ds.GetLayerByName('y')
    if lyr is None:
        gdaltest.post_reason('fail')
        print(ds.GetLayer(3).GetName())
        return 'fail'
    ds = None

    return 'success'

###############################################################################
# Test behaviour when identifiers have same case

def ogr_gmlas_identifier_case_ambiguity():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:', open_options = [
            'XSD=data/gmlas/gmlas_identifier_case_ambiguity.xsd',
            'CONFIG_FILE=<Configuration><LayerBuildingRules><PostgreSQLIdentifierLaundering>false</PostgreSQLIdentifierLaundering></LayerBuildingRules></Configuration>'])
    lyr = ds.GetLayerByName('differentcase1')
    if lyr is None:
        gdaltest.post_reason('fail')
        print(ds.GetLayer(0).GetName())
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(1).GetName()
    if s != 'differentcase1':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    s = lyr.GetLayerDefn().GetFieldDefn(2).GetName()
    if s != 'DifferentCASE2':
        gdaltest.post_reason('fail')
        print(s)
        return 'fail'
    lyr = ds.GetLayerByName('DifferentCASE2')
    if lyr is None:
        gdaltest.post_reason('fail')
        print(ds.GetLayer(0).GetName())
        return 'fail'
    ds = None

    return 'success'

###############################################################################
# Test writing support

def ogr_gmlas_writer():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    if ogr.GetDriverByName('SQLite') is None:
        return 'skip'

    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = [ 'EXPOSE_METADATA_LAYERS=YES' ])
    tmp_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer.db', src_ds, format = 'SQLite')
    src_ds = None
    ret_ds = gdal.VectorTranslate('tmp/gmlas_test1_generated.xml', tmp_ds, \
                                  format = 'GMLAS', \
                                  datasetCreationOptions = ['WRAPPING=GMLAS_FEATURECOLLECTION'])
    tmp_ds = None
    gdal.Unlink('/vsimem/ogr_gmlas_writer.db')

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    return 'success'

###############################################################################
# Check the generated .xml and .xsd

def ogr_gmlas_writer_check_xml_xsd():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    if ogr.GetDriverByName('SQLite') is None:
        return 'skip'

    got = open('tmp/gmlas_test1_generated.xml', 'rt').read()
    got = got.replace('\r\n', '\n')
    pos = got.find('http://myns ') + len('http://myns ')
    pos_end = got.find('"', pos)
    absolute_xsd = got[pos:pos_end]
    if not absolute_xsd.endswith('gmlas_test1.xsd') or not os.path.exists(absolute_xsd):
        gdaltest.post_reason('fail')
        print(absolute_xsd)
        return 'fail'
    got = got.replace(absolute_xsd, 'gmlas_test1.xsd')

    expected = open('data/gmlas/gmlas_test1_generated.xml', 'rt').read()
    expected = expected.replace('\r\n', '\n')

    if got != expected:
        gdaltest.post_reason('fail')

        print('Got:')
        print(got)
        print('')

        print('Diff:')
        os.system('diff -u data/gmlas/gmlas_test1_generated.xml tmp/gmlas_test1_generated.xml')
        return 'fail'

    got = open('tmp/gmlas_test1_generated.xsd', 'rt').read()
    got = got.replace('\r\n', '\n')
    pos = got.find('schemaLocation="') + len('schemaLocation="')
    pos_end = got.find('"', pos)
    absolute_xsd = got[pos:pos_end]
    if not absolute_xsd.endswith('gmlas_test1.xsd') or not os.path.exists(absolute_xsd):
        gdaltest.post_reason('fail')
        print(absolute_xsd)
        return 'fail'
    got = got.replace(absolute_xsd, 'gmlas_test1.xsd')

    expected = open('data/gmlas/gmlas_test1_generated.xsd', 'rt').read()
    expected = expected.replace('\r\n', '\n')

    if got != expected:
        gdaltest.post_reason('fail')

        print('Got:')
        print(got)
        print('')

        print('Diff:')
        os.system('diff -u data/gmlas/gmlas_test1_generated.xsd tmp/gmlas_test1_generated.xsd')
        return 'fail'

    return 'success'

###############################################################################
# Check that the .xml read back by the GMLAS driver has the same content
# as the original one.

def ogr_gmlas_writer_check_xml_read_back():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    if ogr.GetDriverByName('SQLite') is None:
        return 'skip'

    # Skip tests when -fsanitize is used
    if gdaltest.is_travis_branch('sanitize'):
       print('Skipping because of -sanitize')
       return 'skip'

    import test_cli_utilities

    if test_cli_utilities.get_ogrinfo_path() is None:
        gdal.Unlink('tmp/gmlas_test1_generated.xml')
        gdal.Unlink('tmp/gmlas_test1_generated.xsd')
        return 'skip'

    # Compare the ogrinfo dump of the generated .xml with a reference one
    ret = gdaltest.runexternal(test_cli_utilities.get_ogrinfo_path() +
        ' -ro -al GMLAS:tmp/gmlas_test1_generated.xml -oo VALIDATE=YES ' +
        '-oo EXPOSE_METADATA_LAYERS=YES ' +
        '-oo @KEEP_RELATIVE_PATHS_FOR_METADATA=YES ' +
        '-oo @EXPOSE_SCHEMAS_NAME_IN_METADATA=NO ' +
        '-oo @EXPOSE_CONFIGURATION_IN_METADATA=NO -oo @HASH=fake_hash')
    expected = open('data/gmlas/gmlas_test1.txt', 'rt').read()
    expected = expected.replace('\r\n', '\n')
    expected = expected.replace('data/gmlas/gmlas_test1.xml', 'tmp/gmlas_test1_generated.xml')
    expected = expected.replace('data/gmlas/gmlas_test1.xsd', os.path.join(os.getcwd(), 'data/gmlas/gmlas_test1.xsd'))
    expected = expected.replace('\\', '/')
    ret_for_comparison = ret.replace('\r\n', '\n')
    ret_for_comparison = ret_for_comparison.replace('\\', '/')
    ret_for_comparison = ret_for_comparison.replace('fake_hash', '3CF9893502A592E8CF5EA6EF3D8F8C7B')

    if ret_for_comparison != expected:
        gdaltest.post_reason('fail')

        print('XML:')
        print(open('tmp/gmlas_test1_generated.xml', 'rt').read())
        print('')

        print('XSD:')
        print(open('tmp/gmlas_test1_generated.xsd', 'rt').read())
        print('')

        print('ogrinfo dump:')
        print(ret)
        print('')

        open('tmp/gmlas_test1_generated_got.txt', 'wt').write(ret_for_comparison)
        open('tmp/gmlas_test1_generated_expected.txt', 'wt').write(expected)
        print('Diff:')
        os.system('diff -u tmp/gmlas_test1_generated_expected.txt tmp/gmlas_test1_generated_got.txt')

        os.unlink('tmp/gmlas_test1_generated_expected.txt')
        os.unlink('tmp/gmlas_test1_generated_got.txt')
        return 'fail'

    gdal.Unlink('tmp/gmlas_test1_generated.xml')
    gdal.Unlink('tmp/gmlas_test1_generated.xsd')

    return 'success'

###############################################################################
# Test writing support with geometries

def ogr_gmlas_writer_gml():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml',
                    open_options = [ 'EXPOSE_METADATA_LAYERS=YES', '@HASH=hash' ])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    # Test also with GMLAS: prefix as it is likely people might use it
    # as it is needed for the read side.
    ret_ds = gdal.VectorTranslate('GMLAS:/vsimem/ogr_gmlas_writer_gml.xml', tmp_ds, \
        format = 'GMLAS', \
        datasetCreationOptions = ['WRAPPING=GMLAS_FEATURECOLLECTION',
                                  'LAYERS={SPATIAL_LAYERS}'])
    tmp_ds = None

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    f = gdal.VSIFOpenL('/vsimem/ogr_gmlas_writer_gml.xml', 'rb')
    if f is None:
        gdaltest.post_reason('fail')
        return 'fail'
    content = gdal.VSIFReadL(1, 10000, f).decode('utf-8')
    gdal.VSIFCloseL(f)

    gdal.Unlink('/vsimem/ogr_gmlas_writer_gml.xml')
    gdal.Unlink('/vsimem/ogr_gmlas_writer_gml.xsd')

    if content.find('xmlns:gml="http://fake_gml32"') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    if content.find('<ogr:geometryProperty><gml:Point srsName="http://www.opengis.net/def/crs/EPSG/0/4326" gml:id="hash_test_1.geom0"><gml:pos>49 2</gml:pos></gml:Point></ogr:geometryProperty>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    if content.find('<ogr:pointProperty><gml:Point srsName="http://www.opengis.net/def/crs/EPSG/0/4326" gml:id="hash_test_1.geom2"><gml:pos>50 3</gml:pos></gml:Point></ogr:pointProperty>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    if content.find('      <ogr:pointPropertyRepeated><gml:Point gml:id="hash_test_1.geom13.0"><gml:pos>0 1</gml:pos></gml:Point></ogr:pointPropertyRepeated>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    if content.find('      <ogr:pointPropertyRepeated><gml:Point gml:id="hash_test_1.geom13.1"><gml:pos>1 2</gml:pos></gml:Point></ogr:pointPropertyRepeated>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    return 'success'

###############################################################################
# Test writing support with geometries and -a_srs

def ogr_gmlas_writer_gml_assign_srs():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml',
                    open_options = [ 'EXPOSE_METADATA_LAYERS=YES', '@HASH=hash' ])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None

    ret_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer_gml.xml', tmp_ds, \
        format = 'GMLAS', \
        dstSRS = 'EPSG:32631', \
        reproject = False)
    tmp_ds = None

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    f = gdal.VSIFOpenL('/vsimem/ogr_gmlas_writer_gml.xml', 'rb')
    if f is None:
        gdaltest.post_reason('fail')
        return 'fail'
    content = gdal.VSIFReadL(1, 10000, f).decode('utf-8')
    gdal.VSIFCloseL(f)

    gdal.Unlink('/vsimem/ogr_gmlas_writer_gml.xml')
    gdal.Unlink('/vsimem/ogr_gmlas_writer_gml.xsd')

    if content.find('http://www.opengis.net/def/crs/EPSG/0/32631') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    # No geometry, but to test that the proxied ExecuteSQL() works

    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_test1.xml', open_options = [ 'EXPOSE_METADATA_LAYERS=YES' ])
    tmp_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer.db', src_ds, format = 'SQLite')
    src_ds = None
    gdal.VectorTranslate('/vsimem/gmlas_test1_generated_ref0.xml', tmp_ds, \
                                  format = 'GMLAS', \
                                  dstSRS = 'EPSG:32631', \
                                  reproject = False, \
                                  datasetCreationOptions = ['WRAPPING=GMLAS_FEATURECOLLECTION'] )
    gdal.VectorTranslate('/vsimem/gmlas_test1_generated_asrs.xml', tmp_ds, \
                                  format = 'GMLAS', \
                                  dstSRS = 'EPSG:32631', \
                                  reproject = False, \
                                  datasetCreationOptions = ['WRAPPING=GMLAS_FEATURECOLLECTION'] )
    tmp_ds = None
    gdal.Unlink('/vsimem/ogr_gmlas_writer.db')

    if gdal.VSIStatL('/vsimem/gmlas_test1_generated_ref0.xml').size != gdal.VSIStatL('/vsimem/gmlas_test1_generated_asrs.xml').size:
        gdaltest.post_reason('fail')
        print(gdal.VSIStatL('/vsimem/gmlas_test1_generated_ref0.xml').size)
        print(gdal.VSIStatL('/vsimem/gmlas_test1_generated_asrs.xml').size)
        return 'fail'

    gdal.Unlink('/vsimem/gmlas_test1_generated_ref0.xml')
    gdal.Unlink('/vsimem/gmlas_test1_generated_ref0.xsd')
    gdal.Unlink('/vsimem/gmlas_test1_generated_asrs.xml')
    gdal.Unlink('/vsimem/gmlas_test1_generated_asrs.xsd')

    return 'success'

###############################################################################
# Test writing support with geometries with original XML content preserved

def ogr_gmlas_writer_gml_original_xml():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml',
                    open_options = [ 'EXPOSE_METADATA_LAYERS=YES',
                                     'CONFIG_FILE=<Configuration><LayerBuildingRules><GML><IncludeGeometryXML>true</IncludeGeometryXML></GML></LayerBuildingRules></Configuration>'])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    ret_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer_gml.xml', tmp_ds, format = 'GMLAS', \
                                  datasetCreationOptions = ['WRAPPING=GMLAS_FEATURECOLLECTION'])
    tmp_ds = None

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'
    ret_ds = None

    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_writer_gml.xml', open_options=['VALIDATE=YES'])
    if ds is None or gdal.GetLastErrorMsg() != '':
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    f = gdal.VSIFOpenL('/vsimem/ogr_gmlas_writer_gml.xml', 'rb')
    if f is None:
        gdaltest.post_reason('fail')
        return 'fail'
    content = gdal.VSIFReadL(1, 10000, f).decode('utf-8')
    gdal.VSIFCloseL(f)

    gdal.Unlink('/vsimem/ogr_gmlas_writer_gml.xml')
    gdal.Unlink('/vsimem/ogr_gmlas_writer_gml.xsd')

    if content.find('<ogr:geometryProperty> <gml:Point gml:id="poly.geom.Geometry" srsName="urn:ogc:def:crs:EPSG::4326"> <gml:pos>49 2</gml:pos> </gml:Point> </ogr:geometryProperty>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    if content.find('      <ogr:pointPropertyRepeated><gml:Point gml:id="poly.geom.pointPropertyRepeated.1"><gml:pos>0 1</gml:pos></gml:Point></ogr:pointPropertyRepeated>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    if content.find('      <ogr:pointPropertyRepeated><gml:Point gml:id="poly.geom.pointPropertyRepeated.2"><gml:pos>1 2</gml:pos></gml:Point></ogr:pointPropertyRepeated>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    return 'success'

###############################################################################
# Test writing support with XSD, INDENT_SIZE, COMMENT, OUTPUT_XSD_FILENAME, TIMESTAMP options

def ogr_gmlas_writer_options():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml', open_options = [ '@HASH=hash' ])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    ret_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer_options.xml', tmp_ds, format = 'GMLAS',
        datasetCreationOptions = ['LAYERS=test',
                                  'WRAPPING=GMLAS_FEATURECOLLECTION',
                                  'INPUT_XSD=data/gmlas/gmlas_geometryproperty_gml32.xsd',
                                  'INDENT_SIZE=4',
                                  'COMMENT=---a comment---',
                                  'SRSNAME_FORMAT=OGC_URN',
                                  'OUTPUT_XSD_FILENAME=/vsimem/my_schema.xsd'])
    tmp_ds = None

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    f = gdal.VSIFOpenL('/vsimem/ogr_gmlas_writer_options.xml', 'rb')
    if f is None:
        gdaltest.post_reason('fail')
        return 'fail'
    content = gdal.VSIFReadL(1, 10000, f).decode('utf-8')
    gdal.VSIFCloseL(f)

    gdal.Unlink('/vsimem/ogr_gmlas_writer_options.xml')

    if gdal.VSIStatL('/vsimem/my_schema.xsd') is None:
        gdaltest.post_reason('fail')
        return 'fail'

    gdal.Unlink('/vsimem/my_schema.xsd')

    # Test indentation size
    if content.find('\n        <ogr:test gml:id="poly.0">') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    # Test comment
    if content.find('\n<!-- - - -a comment- - - -->') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    # Test OUTPUT_XSD_FILENAME
    if content.find('/vsimem/my_schema.xsd') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    # Test SRSNAME_FORMAT=OGC_URN
    if content.find('<ogr:geometryProperty><gml:Point srsName="urn:ogc:def:crs:EPSG::4326" gml:id="hash_test_1.geom0"><gml:pos>49 2</gml:pos></gml:Point></ogr:geometryProperty>') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'


    # Test TIMESTAMP option
    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml', \
        open_options = [ '@HASH=hash', 'EXPOSE_METADATA_LAYERS=YES' ])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    ret_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer_options.xml', tmp_ds, format = 'GMLAS',
        datasetCreationOptions = ['TIMESTAMP=1970-01-01T12:34:56Z', '@REOPEN_DATASET_WITH_GMLAS=NO'])
    tmp_ds = None

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    f = gdal.VSIFOpenL('/vsimem/ogr_gmlas_writer_options.xml', 'rb')
    if f is None:
        gdaltest.post_reason('fail')
        return 'fail'
    content = gdal.VSIFReadL(1, 10000, f).decode('utf-8')
    gdal.VSIFCloseL(f)

    gdal.Unlink('/vsimem/ogr_gmlas_writer_options.xml')

    if gdal.VSIStatL('/vsimem/my_schema.xsd') is not None:
        gdaltest.post_reason('fail')
        return 'fail'

    if content.find('timeStamp="1970-01-01T12:34:56Z"') < 0 or \
       content.find('xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd ') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'


    # Test WFS20_SCHEMALOCATION option
    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml', \
        open_options = [ '@HASH=hash', 'EXPOSE_METADATA_LAYERS=YES' ])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    ret_ds = gdal.VectorTranslate('/vsimem/ogr_gmlas_writer_options.xml', tmp_ds, format = 'GMLAS',
        datasetCreationOptions = ['WFS20_SCHEMALOCATION=/vsimem/fake_wfs.xsd'])
    tmp_ds = None

    if ret_ds is None:
        gdaltest.post_reason('fail')
        return 'fail'

    gdal.FileFromMemBuffer('/vsimem/fake_wfs.xsd',
"""
<!-- fake wfs schema enough for our purposes -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://www.opengis.net/wfs/2.0"
           elementFormDefault="qualified">
    <xs:element name="FeatureCollection">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="member" minOccurs="0" maxOccurs="unbounded"/>
            </xs:sequence>
            <xs:attribute name="timeStamp" type="xs:dateTime" use="required"/>
            <xs:attribute name="numberMatched" type="xs:string" fixed="unknown" use="required"/>
            <xs:attribute name="numberReturned" type="xs:nonNegativeInteger" use="required"/>
        </xs:complexType>
    </xs:element>
</xs:schema>
""")
    ds = gdal.OpenEx('GMLAS:/vsimem/ogr_gmlas_writer_options.xml', open_options=['VALIDATE=YES'])
    gdal.Unlink('/vsimem/fake_wfs.xsd')

    if ds is None or gdal.GetLastErrorMsg() != '':
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    f = gdal.VSIFOpenL('/vsimem/ogr_gmlas_writer_options.xml', 'rb')
    if f is None:
        gdaltest.post_reason('fail')
        return 'fail'
    content = gdal.VSIFReadL(1, 10000, f).decode('utf-8')
    gdal.VSIFCloseL(f)

    gdal.Unlink('/vsimem/ogr_gmlas_writer_options.xml')

    if gdal.VSIStatL('/vsimem/my_schema.xsd') is not None:
        gdaltest.post_reason('fail')
        return 'fail'

    if content.find('xsi:schemaLocation="http://www.opengis.net/wfs/2.0 /vsimem/fake_wfs.xsd ') < 0:
        gdaltest.post_reason('fail')
        print(content)
        return 'fail'

    return 'success'

###############################################################################
# Test writing support error handle

def ogr_gmlas_writer_errors():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # Source dataset is empty
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', gdal.GetDriverByName('Memory').Create('',0,0,0,0), format = 'GMLAS')
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Source dataset has no layers') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Missing input schemas
    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml')
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', tmp_ds, format = 'GMLAS')
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Cannot establish schema since no INPUT_XSD creation option specified and no _ogr_other_metadata found in source dataset') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Invalid input schema
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', tmp_ds, format = 'GMLAS', \
                                      datasetCreationOptions = [ 'INPUT_XSD=/i_do_not/exist.xsd' ])
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Cannot resolve /i_do_not/exist.xsd') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Invalid output .xml name
    src_ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometryproperty_gml32_no_error.gml', \
                open_options = [ 'EXPOSE_METADATA_LAYERS=YES' ])
    tmp_ds = gdal.VectorTranslate('', src_ds, format = 'Memory')
    src_ds = None
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/i_am/not/valid.xml', tmp_ds, format = 'GMLAS', \
                                      datasetCreationOptions = [ 'GENERATE_XSD=NO' ])
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Cannot create /i_am/not/valid.xml') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # .xsd extension not allowed
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/i_am/not/valid.xsd', tmp_ds, format = 'GMLAS', \
                                      datasetCreationOptions = [ 'GENERATE_XSD=NO' ])
    if ret_ds is not None or gdal.GetLastErrorMsg().find('.xsd extension is not valid') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Invalid output .xsd name
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', tmp_ds, format = 'GMLAS', \
                                      datasetCreationOptions = [ 'WRAPPING=GMLAS_FEATURECOLLECTION',
                                                                 'OUTPUT_XSD_FILENAME=/i_am/not/valid.xsd' ])
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Cannot create /i_am/not/valid.xsd') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'
    gdal.Unlink('/vsimem/valid.xml')

    # Invalid CONFIG_FILE
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', tmp_ds, format = 'GMLAS', \
                                      datasetCreationOptions = [ 'CONFIG_FILE=/i/do_not/exist' ])
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Loading of configuration failed') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Invalid layer name
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', tmp_ds, format = 'GMLAS', \
                                      datasetCreationOptions = [ 'LAYERS=foo' ])
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Layer foo specified in LAYERS option does not exist') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'
    gdal.Unlink('/vsimem/valid.xml')

    # _ogr_layers_metadata not found
    src_ds = gdal.GetDriverByName('Memory').Create('',0,0,0,0)
    src_ds.CreateLayer('_ogr_other_metadata')
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', src_ds, format = 'GMLAS')
    if ret_ds is not None or gdal.GetLastErrorMsg().find('_ogr_layers_metadata not found') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # _ogr_fields_metadata not found
    src_ds = gdal.GetDriverByName('Memory').Create('',0,0,0,0)
    src_ds.CreateLayer('_ogr_other_metadata')
    src_ds.CreateLayer('_ogr_layers_metadata')
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', src_ds, format = 'GMLAS')
    if ret_ds is not None or gdal.GetLastErrorMsg().find('_ogr_fields_metadata not found') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # _ogr_layer_relationships not found
    src_ds = gdal.GetDriverByName('Memory').Create('',0,0,0,0)
    src_ds.CreateLayer('_ogr_other_metadata')
    src_ds.CreateLayer('_ogr_layers_metadata')
    src_ds.CreateLayer('_ogr_fields_metadata')
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', src_ds, format = 'GMLAS')
    if ret_ds is not None or gdal.GetLastErrorMsg().find('_ogr_layer_relationships not found') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'

    # Cannot find field layer_name in _ogr_layers_metadata layer
    src_ds = gdal.GetDriverByName('Memory').Create('',0,0,0,0)
    src_ds.CreateLayer('_ogr_other_metadata')
    src_ds.CreateLayer('_ogr_layers_metadata')
    src_ds.CreateLayer('_ogr_fields_metadata')
    src_ds.CreateLayer('_ogr_layer_relationships')
    with gdaltest.error_handler():
        ret_ds = gdal.VectorTranslate('/vsimem/valid.xml', src_ds, format = 'GMLAS')
    if ret_ds is not None or gdal.GetLastErrorMsg().find('Cannot find field layer_name in _ogr_layers_metadata layer') < 0:
        gdaltest.post_reason('fail')
        print(gdal.GetLastErrorMsg())
        return 'fail'
    gdal.Unlink('/vsimem/valid.xml')
    gdal.Unlink('/vsimem/valid.xsd')

    return 'success'

###############################################################################
# Test reading a particular construct with group, etc... that could cause
# crashes

def ogr_gmlas_read_fake_gmljp2():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/fake_gmljp2.xml')

    count = 0
    while True:
        f, l = ds.GetNextFeature()
        if f is None:
            if l is not None:
                gdaltest.post_reason('fail')
                return 'fail'
            break
        count += 1

    if count != 5:
        gdaltest.post_reason('fail')
        print(count)
        return 'fail'

    return 'success'

###############################################################################
#  Test TypingConstraints

def ogr_gmlas_typing_constraints():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # One substitution, no repetition
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_typing_constraints_one_subst_no_repetition.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
<TypingConstraints>
        <Namespaces>
            <Namespace prefix="myns_modified_for_fun" uri="http://myns"/>
        </Namespaces>
        <ChildConstraint>
            <ContainerXPath>myns_modified_for_fun:main_elt/myns_modified_for_fun:foo</ContainerXPath>
            <ChildrenElements>
                <Element>myns_modified_for_fun:bar</Element>
            </ChildrenElements>
        </ChildConstraint>
    </TypingConstraints>
</Configuration>"""])
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if not f.IsFieldSetAndNotNull('foo_bar_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    lyr = ds.GetLayer(1)
    f = lyr.GetNextFeature()
    if f.GetField('value') != 'baz':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    ds = None


    # One substitution, with repetition

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_typing_constraints_one_subst_with_repetition.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
<TypingConstraints>
        <Namespaces>
            <Namespace prefix="myns_modified_for_fun" uri="http://myns"/>
        </Namespaces>
        <ChildConstraint>
            <ContainerXPath>myns_modified_for_fun:main_elt/myns_modified_for_fun:foo</ContainerXPath>
            <ChildrenElements>
                <Element>myns_modified_for_fun:bar</Element>
            </ChildrenElements>
        </ChildConstraint>
    </TypingConstraints>
</Configuration>"""])
    lyr = ds.GetLayer('main_elt_foo_bar')
    if lyr.GetFeatureCount() != 2:
        gdaltest.post_reason('fail')
        return 'fail'
    lyr = ds.GetLayer('bar')
    f = lyr.GetNextFeature()
    if f.GetField('value') != 'baz':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f.GetField('value') != 'baz2':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    ds = None

    # 2 substitutions
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_typing_constraints_two_subst.xml',
        open_options = ["""CONFIG_FILE=<Configuration>
<TypingConstraints>
        <Namespaces>
            <Namespace prefix="myns_modified_for_fun" uri="http://myns"/>
        </Namespaces>
        <ChildConstraint>
            <ContainerXPath>myns_modified_for_fun:main_elt/myns_modified_for_fun:foo</ContainerXPath>
            <ChildrenElements>
                <Element>myns_modified_for_fun:bar</Element>
                <Element>myns_modified_for_fun:baz</Element>
            </ChildrenElements>
        </ChildConstraint>
    </TypingConstraints>
</Configuration>"""])
    lyr = ds.GetLayer(0)
    f = lyr.GetNextFeature()
    if not f.IsFieldSetAndNotNull('foo_bar_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if f.IsFieldSetAndNotNull('foo_baz_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    lyr = ds.GetLayer(1)
    f = lyr.GetNextFeature()
    if f.GetField('value') != 'baz':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    ds = None

    return 'success'

###############################################################################
#  Test swe:DataArray

def ogr_gmlas_swe_dataarray():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_swe_dataarray.xml')

    lyr = ds.GetLayerByName('dataarray_1_components')
    f = lyr.GetNextFeature()
    if not f.IsFieldSetAndNotNull('parent_ogr_pkid') or \
       f.GetField('myTime') != '2016/09/01 00:00:00+01' or \
       f.GetField('myCategory') != '1' or \
       f.GetField('myQuantity') != 2.34 or \
       f.GetField('myCount') != 3 or \
       f.GetField('myText') != 'foo' or \
       f.GetField('myBoolean') != True:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f.GetField('myTime') != '2017/09/01 00:00:00' or \
       f.GetField('myCategory') != '2' or \
       f.GetField('myQuantity') != 3.45:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('dataarray_2')
    f = lyr.GetNextFeature()
    if f.GetField('myTime') != '2016/09/01 00:00:00+01' or \
       f.GetField('myCategory') != '1' or \
       f.GetField('myQuantity') != 2.34:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f.GetField('myTime') != '2017/09/01 00:00:00' or \
       f.GetField('myCategory') is not None or \
       f.GetField('myQuantity') != 3.45:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('dataarray_3')
    f = lyr.GetNextFeature()
    if f.GetField('myTime') != '2016/09/01 00:00:00+01' or \
       f.GetField('myCategory') != '1' or \
       f.GetField('myQuantity') != 2.34:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f.GetField('myTime') != '2017/09/01 00:00:00' or \
       f.GetField('myCategory') is not None or \
       f.GetField('myQuantity') != 3.45:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    f = lyr.GetNextFeature()
    if f is not None:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    ds = None

    return 'success'


###############################################################################
#  Test swe:DataRecord

def ogr_gmlas_swe_datarecord():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    gdal.ErrorReset()
    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_swe_datarecord.xml', open_options = ['VALIDATE=YES'])
    if gdal.GetLastErrorMsg() != '':
        gdaltest.post_reason('fail')
        return 'fail'
    ds = None

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_swe_datarecord.xml')
    lyr = ds.GetLayerByName('main_elt_foo')
    if lyr.GetLayerDefn().GetFieldCount() != 12:
        gdaltest.post_reason('fail')
        print(lyr.GetLayerDefn().GetFieldCount())
        return 'fail'
    f = lyr.GetNextFeature()
    if f.GetField('mytime_value') != '2017/09/01 00:00:00' or \
       f.GetField('mycategory_value') != 'myvalue' or \
       f.GetField('mycategory_identifier') != 'myidentifier' or \
       f.GetField('mycategory_codespace_href') != 'http://example.com' or \
       f.GetField('myquantity_value') != 1.23 or \
       f.GetField('mycount_value') != 2 or \
       f.GetField('mytext_value') != 'foo' or \
       f.GetField('myboolean_value') != True:
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    ds = None

    return 'success'

###############################################################################
#  Test a xs:any field at end of a type declaration

def ogr_gmlas_any_field_at_end_of_declaration():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    # Simplified test case for
    # http://schemas.earthresourceml.org/earthresourceml-lite/1.0/erml-lite.xsd 
    # http://services.ga.gov.au/earthresource/ows?service=wfs&version=2.0.0&request=GetFeature&typenames=erl:CommodityResourceView&count=10

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_any_field_at_end_of_declaration.xml')
    lyr = ds.GetLayerByName('main_elt')
    # Will warn about 'Unexpected element with xpath=main_elt/extra (subxpath=main_elt/extra) found'
    # This should be fixed at some point
    gdal.ErrorReset()
    with gdaltest.error_handler():
        f = lyr.GetNextFeature()
    if gdal.GetLastErrorMsg() == '':
        gdaltest.post_reason('fail')
        return 'fail'
    if f.GetField('foo') != 'bar':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'
    if f.GetField('value') != '<something>baz</something>':
        print('Expected fail: value != <something>baz</something>')

    return 'success'

###############################################################################
#  Test auxiliary schema without namespace prefix

def ogr_gmlas_aux_schema_without_namespace_prefix():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_aux_schema_without_namespace_prefix.xml')
    lyr = ds.GetLayerByName('main_elt')
    f = lyr.GetNextFeature()
    if not f.IsFieldSetAndNotNull('generic_pkid'):
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
# Test importing a GML geometry that is in an element that is a substitutionGroup
# of another one (#6990)

def ogr_gmlas_geometry_as_substitutiongroup():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_geometry_as_substitutiongroup.xml')
    lyr = ds.GetLayerByName('foo')
    f = lyr.GetNextFeature()
    if f.GetGeometryRef() is None:
        f.DumpReadable()
        return 'fail'
    ds = None

    return 'success'

###############################################################################
def ogr_gmlas_extra_piezometre():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    return compare_ogrinfo_output('data/gmlas/real_world/Piezometre.06512X0037.STREMY.2.gml',
                                  'data/gmlas/real_world/output/Piezometre.06512X0037.STREMY.2.txt',
                                  options = '-oo REMOVE_UNUSED_LAYERS=YES')

###############################################################################
def ogr_gmlas_extra_eureg():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    return compare_ogrinfo_output('data/gmlas/real_world/EUReg.example.gml',
                                  'data/gmlas/real_world/output/EUReg.example.txt',
                                  options = '-oo REMOVE_UNUSED_LAYERS=YES')


###############################################################################
# Test a schema that has nothing interesting in it but imports another
# schema

def ogr_gmlas_no_element_in_first_choice_schema():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    ds = gdal.OpenEx('GMLAS:', open_options = ['XSD=data/gmlas/gmlas_no_element_in_first_choice_schema.xsd'])
    lyr = ds.GetLayerByName('_ogr_layers_metadata')
    f = lyr.GetNextFeature()
    if f['layer_xpath'] != 'my_ns:main_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'


###############################################################################
# Test cross-layer links with xlink:href="#my_id"

def ogr_gmlas_internal_xlink_href():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    with gdaltest.error_handler():
        ds = gdal.OpenEx('GMLAS:data/gmlas/gmlas_internal_xlink_href.xml')
        lyr = ds.GetLayerByName('main_elt')
        f = lyr.GetNextFeature()
    if f['link_to_second_or_third_elt_href'] != '#does_not_exist' or \
       f.IsFieldSet('link_to_second_or_third_elt_second_elt_pkid') or \
       f.IsFieldSet('link_to_second_or_third_elt_third_elt_pkid') or \
       f.IsFieldSet('link_to_third_elt_third_elt_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['link_to_second_or_third_elt_href'] != '#id2' or \
       f['link_to_second_or_third_elt_second_elt_pkid'] != 'id2' or \
       f.IsFieldSet('link_to_second_or_third_elt_third_elt_pkid') or \
       f.IsFieldSet('link_to_third_elt_third_elt_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['link_to_second_or_third_elt_href'] != '#id3' or \
       f['link_to_second_or_third_elt_second_elt_pkid'] != 'id3' or \
       f.IsFieldSet('link_to_second_or_third_elt_third_elt_pkid') or \
       f.IsFieldSet('link_to_third_elt_third_elt_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['link_to_second_or_third_elt_href'] != '#id4' or \
       f.IsFieldSet('link_to_second_or_third_elt_second_elt_pkid') or \
       f['link_to_second_or_third_elt_third_elt_pkid'] != 'D1013B7E44F28C976B976A4314FA4A09_third_elt_1' or \
       f.IsFieldSet('link_to_third_elt_third_elt_pkid'):
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['link_to_third_elt_href'] != '#id4' or \
       f.IsFieldSet('link_to_second_or_third_elt_second_elt_pkid') or \
       f.IsFieldSet('link_to_second_or_third_elt_third_elt_pkid') or \
       f['link_to_third_elt_third_elt_pkid'] != 'D1013B7E44F28C976B976A4314FA4A09_third_elt_1':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('_ogr_fields_metadata')
    f = lyr.GetNextFeature()
    if f['layer_name'] != 'main_elt' or f['field_index'] != 1 or \
       f['field_name'] != 'link_to_second_or_third_elt_href':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['layer_name'] != 'main_elt' or f['field_index'] != 2 or \
       f['field_name'] != 'link_to_second_or_third_elt_second_elt_pkid' or \
       f['field_xpath'] != 'main_elt/link_to_second_or_third_elt/second_elt' or \
       f['field_type'] != 'string' or \
       f['field_is_list'] != 0 or \
       f['field_min_occurs'] != 0 or \
       f['field_max_occurs'] != 1 or \
       f['field_category'] != 'PATH_TO_CHILD_ELEMENT_WITH_LINK' or \
       f['field_related_layer'] != 'second_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['layer_name'] != 'main_elt' or f['field_index'] != 3 or \
       f['field_name'] != 'link_to_second_or_third_elt_third_elt_pkid' or \
       f['field_xpath'] != 'main_elt/link_to_second_or_third_elt/third_elt' or \
       f['field_type'] != 'string' or \
       f['field_is_list'] != 0 or \
       f['field_min_occurs'] != 0 or \
       f['field_max_occurs'] != 1 or \
       f['field_category'] != 'PATH_TO_CHILD_ELEMENT_WITH_LINK' or \
       f['field_related_layer'] != 'third_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['layer_name'] != 'main_elt' or f['field_index'] != 4 or \
       f['field_name'] != 'link_to_second_or_third_elt':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['layer_name'] != 'main_elt' or f['field_index'] != 5 or \
       f['field_name'] != 'link_to_third_elt_href':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['layer_name'] != 'main_elt' or f['field_index'] != 6 or \
       f['field_name'] != 'link_to_third_elt_third_elt_pkid':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['layer_name'] != 'third_elt' or f['field_index'] != 1 or \
       f['field_name'] != 'id':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    lyr = ds.GetLayerByName('_ogr_layer_relationships')
    f = lyr.GetNextFeature()
    if f['parent_layer'] != 'main_elt' or \
       f['parent_pkid'] != 'ogr_pkid' or \
       f['parent_element_name'] != 'link_to_third_elt_third_elt_pkid' or \
       f['child_layer'] != 'third_elt' or \
       f['child_pkid'] != 'ogr_pkid':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['parent_layer'] != 'main_elt' or \
       f['parent_pkid'] != 'ogr_pkid' or \
       f['parent_element_name'] != 'link_to_second_or_third_elt_second_elt_pkid' or \
       f['child_layer'] != 'second_elt' or \
       f['child_pkid'] != 'id':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    f = lyr.GetNextFeature()
    if f['parent_layer'] != 'main_elt' or \
       f['parent_pkid'] != 'ogr_pkid' or \
       f['parent_element_name'] != 'link_to_second_or_third_elt_third_elt_pkid' or \
       f['child_layer'] != 'third_elt' or \
       f['child_pkid'] != 'ogr_pkid':
        gdaltest.post_reason('fail')
        f.DumpReadable()
        return 'fail'

    return 'success'

###############################################################################
#  Cleanup

def ogr_gmlas_cleanup():

    if ogr.GetDriverByName('GMLAS') is None:
        return 'skip'

    files = gdal.ReadDir('/vsimem/')
    if files is not None:
        print('Remaining files: ' + str(files))

    gdal.SetConfigOption('GMLAS_WARN_UNEXPECTED', None)
    gdal.SetConfigOption('GDAL_XML_VALIDATION', ogrtest.old_val_GDAL_XML_VALIDATION)

    return 'success'

gdaltest_list = [
    ogr_gmlas_basic,
    ogr_gmlas_test_ogrsf,
    ogr_gmlas_virtual_file,
    ogr_gmlas_datafile_with_xsd_option,
    ogr_gmlas_no_datafile_with_xsd_option,
    ogr_gmlas_no_datafile_xsd_which_is_not_xsd,
    ogr_gmlas_no_datafile_no_xsd,
    ogr_gmlas_non_existing_gml,
    ogr_gmlas_non_existing_xsd,
    ogr_gmlas_gml_without_schema_location,
    ogr_gmlas_invalid_schema,
    ogr_gmlas_invalid_xml,
    ogr_gmlas_gml_Reference,
    ogr_gmlas_same_element_in_different_ns,
    ogr_gmlas_corner_case_relative_path,
    ogr_gmlas_unexpected_repeated_element,
    ogr_gmlas_unexpected_repeated_element_variant,
    ogr_gmlas_geometryproperty,
    ogr_gmlas_abstractgeometry,
    ogr_gmlas_validate,
    ogr_gmlas_test_ns_prefix,
    ogr_gmlas_no_namespace,
    ogr_gmlas_conf,
    ogr_gmlas_conf_ignored_xpath,
    ogr_gmlas_cache,
    ogr_gmlas_link_nested_independant_child,
    ogr_gmlas_composition_compositionPart,
    ogr_gmlas_instantiate_only_gml_feature,
    ogr_gmlas_timestamp_ignored_for_hash,
    ogr_gmlas_dataset_getnextfeature,
    ogr_gmlas_inline_identifier,
    ogr_gmlas_avoid_same_name_inlined_classes,
    ogr_gmlas_validate_ignored_fixed_attribute,
    ogr_gmlas_remove_unused_layers_and_fields,
    ogr_gmlas_xlink_resolver,
    ogr_gmlas_recoding,
    ogr_gmlas_schema_without_namespace_prefix,
    ogr_gmlas_truncated_xml,
    ogr_gmlas_identifier_truncation,
    ogr_gmlas_identifier_case_ambiguity,
    ogr_gmlas_writer,
    ogr_gmlas_writer_check_xml_xsd,
    ogr_gmlas_writer_check_xml_read_back,
    ogr_gmlas_writer_gml,
    ogr_gmlas_writer_gml_assign_srs,
    ogr_gmlas_writer_gml_original_xml,
    ogr_gmlas_writer_options,
    ogr_gmlas_writer_errors,
    ogr_gmlas_read_fake_gmljp2,
    ogr_gmlas_typing_constraints,
    ogr_gmlas_swe_dataarray,
    ogr_gmlas_swe_datarecord,
    ogr_gmlas_any_field_at_end_of_declaration,
    ogr_gmlas_aux_schema_without_namespace_prefix,
    ogr_gmlas_geometry_as_substitutiongroup,
    ogr_gmlas_no_element_in_first_choice_schema,
    ogr_gmlas_internal_xlink_href,
    ogr_gmlas_cleanup ]

# gdaltest_list = [ ogr_gmlas_basic, ogr_gmlas_aux_schema_without_namespace_prefix, ogr_gmlas_cleanup ]

# Test only work if using "python ogr_gmlas.py"
gdaltest_extra_list = [
    ogr_gmlas_extra_piezometre,
    ogr_gmlas_extra_eureg
]

if __name__ == '__main__':

    gdaltest.setup_run( 'ogr_gmlas' )

    gdaltest.run_tests( gdaltest_list + gdaltest_extra_list )

    gdaltest.summarize()
