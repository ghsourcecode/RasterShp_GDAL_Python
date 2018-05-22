#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/18 16:34
'''

import os
import ast
import numpy
import sys
try:
    from osgeo import gdal
except ImportError:
    import gdal
import util.makedirs as makedirs
import vectorToRaster.shpToColorRaster as rasterize

alpha = 1
globalcolors = numpy.array([
        [255, 255, 128, alpha],
        [229, 252, 114, alpha],
        [205, 250, 100, alpha],
        [179, 245, 86, alpha],
        [155, 242, 73, alpha],
        [129, 237, 57, alpha],
        [102, 232, 42, alpha],
        [75, 227, 25, alpha],
        [57, 222, 24, alpha],
        [62, 209, 54, alpha],
        [62, 199, 75, alpha],
        [60, 189, 95, alpha],
        [59, 179, 113, alpha],
        [54, 168, 130, alpha],
        [44, 158, 147, alpha],
        [31, 150, 166, alpha],
        [30, 134, 166, alpha],
        [32, 116, 161, alpha],
        [34, 95, 153, alpha],
        [33, 79, 148, alpha],
        [31, 62, 140, alpha],
        [27, 46, 133, alpha],
        [20, 31, 128, alpha],
        [12, 16, 120, alpha]
    ])

if __name__ == '__main__':
    gdal.AllRegister()
    argvs = gdal.GeneralCmdLineProcessor(sys.argv)

    print('argvs[0]:' + argvs[0] if argvs != None else None)
    print('argvs[1]:' + argvs[1].split('=')[1] if len(argvs) > 1 != None else None)
    print('argvs[2]:' + argvs[2].split('=')[1] if len(argvs) > 1 != None else None)
    print('argvs[3]:' + argvs[3].split('=')[1] if len(argvs) > 1 != None else None)

    shpPath = argvs[1].split('=')[1] if len(argvs) > 1 else None
    resolution = float(argvs[2].split('=')[1]) if len(argvs) > 1 else None
    colorsString = argvs[3].split('=')[1] if len(argvs) > 1 else None
    colorslist = ast.literal_eval(colorsString) if colorsString != None else None
    colors = numpy.array(colorslist) if colorslist != None else None
    outRaster = argvs[4].split('=')[1] if len(argvs) > 1 else None

    # test start
    root = os.getcwd()
    shpPath = root + '/testdata/flttoshp.shp'
    pixel = 0.001
    r = root + '/testdata/temp/red.tif'
    g = root + '/testdata/temp/green.tif'
    b = root + '/testdata/temp/blue.tif'
    rasterize.rasterizeToRGB(shpPath, pixel, globalcolors, r, g, b)
    # 合成rgb
    mergePyPath = root + '/gdal223/gdal_merge.py'
    out = root + '/testdata/temp/outmerge.tif'
    os.system('python ' + mergePyPath + ' -separate -n 0 -a_nodata 0 -of GTiff -o ' + out + ' ' + r + ' ' + g + ' ' + b)
    # test end

    # pyFolder = os.getcwd()
    # print('current py folder: ' + pyFolder)
    # tempFolder = pyFolder + '/temprgb'
    # makedirs.mkdir(tempFolder)
    # r = tempFolder + '/red.tif'
    # g = tempFolder + '/green.tif'
    # b = tempFolder + '/blue.tif'
    # rasterize.rasterizeToRGB(shpPath, resolution, colors, r, g, b)
    # # 合成 rgb
    # mergePyPath = pyFolder + '/gdal223/gdal_merge.py'
    # os.system('python ' + mergePyPath + ' -separate -n 0 -a_nodata 0 -of GTiff -o ' + outRaster + ' ' + r + ' ' + g + ' ' + b)
