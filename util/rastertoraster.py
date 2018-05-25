#!/usr/bin/env python
# encoding: utf-8
'''
栅格格式转换
@author: DaiH
@date: 2018/5/22 10:54
'''

import os
import sys


if __name__ == '__main__':
    currentFolder = os.getcwd()
    parent = os.path.dirname(currentFolder)
    sourceTif = parent + '/testdata/out/outraster.tif'
    targetPng = parent + '/testdata/out/outraster.png'
    gdalTranslateExe = parent + '/gdal223/gdal_translate.exe'
    # os.system(gdalTranslateExe + ' -of PNG ' + sourceTif + ' ' + targetPng)

    riverTif = parent + '/testdata/temp/riverraster.tif'
    riverTargetPng = parent + '/testdata/out/riverraster.png'
    os.system(gdalTranslateExe + ' -of PNG ' + riverTif + ' ' + riverTargetPng)
