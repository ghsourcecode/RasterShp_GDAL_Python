#!/usr/bin/env python
# encoding: utf-8
'''
将dem hillshade 与生成的栅格融合
@author: DaiH
@date: 2018/5/21 13:43
'''

import os

if __name__ == '__main__':
    root = os.getcwd()
    hillshade = root + '/testdata/jxdemhs.tif'
    raster = root + '/testdata/outmerge.tif'
    outMerge = root + '/testdata/out.tif'
    mergePyPath = root + '/gdal223/gdal_merge.py'

    # os.system('python ' + mergePyPath + ' -separate -n 0 -a_nodata 0 -of GTiff -o ' + outMerge + ' ' + hillshade + ' ' + raster)

    # 融合几张 png
    outLevel = root + '/testdata/out/baseriver.png'
    level1 = root + '/testdata/out/outraster.png'
    level2 = root + '/testdata/out/riverraster.png'
    os.system('python ' + mergePyPath + ' -separate -n 0 -a_nodata 0 -of GTiff -o ' + outLevel + ' ' + level1 + ' ' + level2)

    retilePath = root + '/gdal223/gdal_retile.py'
    # os.mkdir('testdata/outretile')
    # os.system('python ' + retilePath + ' -v -levels 2 -r bilinear -targetDir testdata/outretile testdata/outmerge.tif')