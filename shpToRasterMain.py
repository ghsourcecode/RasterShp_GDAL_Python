#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/18 16:34
'''

import os
import numpy
import vectorToRaster.shpToColorRaster as rasterize

alpha = 1
colors = numpy.array([
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
    root = os.getcwd()
    shpPath = root + '/testdata/flttoshp.shp'
    pixel = 0.01
    r = root + '/testdata/temp/red.tif'
    g = root + '/testdata/temp/green.tif'
    b = root + '/testdata/temp/blue.tif'
    rasterize.rasterizeToRGB(shpPath, pixel, colors, r, g, b)

    # 合成rgb
    mergePyPath = root + '/gdal223/gdal_merge.py'
    out = root + '/testdata/temp/outmerge.tif'
    os.system('python ' + mergePyPath + ' -separate -n 0 -a_nodata 0 -of GTiff -o ' + out + ' ' + r + ' ' + g + ' ' + b)
