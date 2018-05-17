#!/usr/bin/env python
# ******************************************************************************
#
#  Project:  GDAL
#  Purpose:  Example doing range based classification
#  Author:   Frank Warmerdam, warmerdam@pobox.com
#
# ******************************************************************************
#  Copyright (c) 2008, Frank Warmerdam <warmerdam@pobox.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
# ******************************************************************************

import sys
import gdal
import gdalnumeric
import ogr
import osr

try:
    import numpy
except:
    import Numeric as numpy



# gdalnumeric.SaveArray( dst_image, 'classes.tif' )

def readTif(fileName):
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
        return
    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数
    im_bands = dataset.RasterCount  # 波段数
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 获取数据
    im_geotrans = dataset.GetGeoTransform()  # 获取仿射矩阵信息
    im_proj = dataset.GetProjection()  # 获取投影信息
    band = dataset.GetRasterBand(1)
    noDataValue = band.GetNoDataValue()
    # im_blueBand =  im_data[0,0:im_height,0:im_width]#获取蓝波段
    # im_greenBand = im_data[1,0:im_height,0:im_width]#获取绿波段
    # im_redBand =   im_data[2,0:im_height,0:im_width]#获取红波段
    # im_nirBand = im_data[3,0:im_height,0:im_width]#获取近红外波段
    return im_data, im_width, im_height, im_bands, im_geotrans, im_proj, noDataValue


def writeTiff(im_data, im_width, im_height, im_bands, im_geotrans, im_proj, noDataValue, path):
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
        im_bands, (im_height, im_width) = 1, im_data.shape
    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, im_width, im_height, im_bands, datatype)
    dataset.GetRasterBand(1).SetNoDataValue(noDataValue)
    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset


# polygonize
def rasterToVector(classifyRasterPath, outPath):
    format = 'ESRI Shapefile'
    options = ['8CONNECTED=8']
    quiet_flag = 0
    src_filename = classifyRasterPath
    src_band_n = 1

    dst_filename = outPath
    dst_layername = 'out'
    dst_fieldname = None
    dst_field = -1

    mask = 'default'

    gdal.AllRegister()
    try:
        gdal.Polygonize
    except:
        print('')
        print('gdal.Polygonize() not available.  You are likely using "old gen"')
        print('bindings or an older version of the next gen bindings.')
        print('')
        sys.exit(1)
    # =============================================================================
    #	Open source file
    # =============================================================================
    src_ds = gdal.Open(src_filename)
    if src_ds is None:
        print('Unable to open %s' % src_filename)
        sys.exit(1)

    srcband = src_ds.GetRasterBand(src_band_n)

    if mask is 'default':
        maskband = srcband.GetMaskBand()
    elif mask is 'none':
        maskband = None
    else:
        mask_ds = gdal.Open(mask)
        maskband = mask_ds.GetRasterBand(1)

    # =============================================================================
    #       Try opening the destination file as an existing file.
    # =============================================================================

    try:
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        dst_ds = ogr.Open(dst_filename, update=1)
        gdal.PopErrorHandler()
    except:
        dst_ds = None

    # =============================================================================
    # 	Create output file.
    # =============================================================================
    if dst_ds is None:
        drv = ogr.GetDriverByName(format)
        if not quiet_flag:
            print('Creating output %s of format %s.' % (dst_filename, format))
        dst_ds = drv.CreateDataSource(dst_filename)

    # =============================================================================
    #       Find or create destination layer.
    # =============================================================================
    try:
        dst_layer = dst_ds.GetLayerByName(dst_layername)
    except:
        dst_layer = None

    if dst_layer is None:

        srs = None
        if src_ds.GetProjectionRef() != '':
            srs = osr.SpatialReference()
            srs.ImportFromWkt(src_ds.GetProjectionRef())

        dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)

        if dst_fieldname is None:
            dst_fieldname = 'DN'

        fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
        dst_layer.CreateField(fd)
        dst_field = 0
    else:
        if dst_fieldname is not None:
            dst_field = dst_layer.GetLayerDefn().GetFieldIndex(dst_fieldname)
            if dst_field < 0:
                print("Warning: cannot find field '%s' in layer '%s'" % (dst_fieldname, dst_layername))

    # =============================================================================
    #	Invoke algorithm.
    # =============================================================================

    if quiet_flag:
        prog_func = None
    else:
        prog_func = gdal.TermProgress

    result = gdal.Polygonize(srcband, maskband, dst_layer, dst_field, options,
                             callback=prog_func)

    srcband = None
    src_ds = None
    dst_ds = None
    mask_ds = None

if __name__ == '__main__':

    class_defs = [(1, 0, 2),
                  (2, 2, 3),
                  (3, 3, 6)]

    src_ds = gdal.Open('E:/pythontest/python_gdal_testdata/Extract_tif11.tif')
    xsize = src_ds.RasterXSize
    ysize = src_ds.RasterYSize

    src_image = gdalnumeric.LoadFile('E:/pythontest/python_gdal_testdata/Extract_tif11.tif')

    dst_image = numpy.zeros((ysize, xsize))

    for class_info in class_defs:
        class_id = class_info[0]
        class_start = class_info[1]
        class_end = class_info[2]

        class_value = numpy.ones((ysize, xsize)) * class_id

        mask = numpy.bitwise_and(
            numpy.greater_equal(src_image, class_start),
            numpy.less_equal(src_image, class_end))

        dst_image = numpy.choose(mask, (dst_image, class_value))

    im_data, im_width, im_height, im_bands, im_geotrans, im_proj, noDataValue = readTif(
        'E:/pythontest/python_gdal_testdata/Extract_tif11.tif')
    path = 'E:/pythontest/python_gdal_testdata/ab.tif'
    writeTiff(dst_image, im_width, im_height, im_bands, im_geotrans, im_proj, noDataValue, path)
    rasterToVector(path, 'E:/pythontest/python_gdal_testdata/rtov.shp')