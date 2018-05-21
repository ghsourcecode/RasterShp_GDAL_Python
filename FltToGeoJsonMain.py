#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/18 9:59
'''

import os
import sys
import numpy
import ast
try:
    from osgeo import gdal
except ImportError:
    import gdal
import flt.flttoshp as flttoshp
import flt.shpToGeoJson as shpToGeoJson

classified = [(0, 0, 0.013435),
                (1, 0.013435, 0.037422),
                (2, 0.037422, 0.080247),
                (3, 0.080247, 0.156709),
                (4, 0.156709, 0.293223),
                (5, 0.293223, 0.536956),
                (6, 0.536956, 0.972118),
                (7, 0.972118, 1.749056),
                (8, 1.749056, 3.136204),
                (9, 3.136204, 5.612822)]
def fltToGeoJson(fltpath, classify, outGeoJsonPath):
    # 下面路径为中间结果路径，程序运行结束后，删除
    root = os.getcwd()
    tempParent = 'testdata/temp'
    tempFltToTifPath = tempParent + '/flttotif.tif'
    classifyTifPath = tempParent + '/classified.tif'
    maskTifPath = tempParent + '/mask.tif'
    tempTifToShpPath = root + '/' + tempParent + '/flttoshp.shp'
    ogr2ogrPath = root + '/gdal223/ogr2ogr.py'

    flttoshp.fltToShp(fltpath, tempFltToTifPath, classify, classifyTifPath, maskTifPath, tempTifToShpPath)
    shpToGeoJson.exportShpToGeoJson(ogr2ogrPath, tempTifToShpPath, outGeoJsonPath)


if __name__ == '__main__':
    gdal.AllRegister()
    argvs = gdal.GeneralCmdLineProcessor(sys.argv)
    if argvs is None:
        sys.exit(0)

    # test instance
    # root = os.getcwd()
    # fltpath = root + '/testdata/rain_2016.flt'
    # classify = classified
    # outGeoJsonPath = root + '/testdata/out/shpToJson.json'
    # main(fltpath, classify, outGeoJsonPath)

    print('argv 0: ' + argvs[0])
    print('argv 1: ' + argvs[1].split('=')[1])
    print('argv 2: ' + argvs[2].split('=')[1])
    print('argv 3: ' + argvs[3].split('=')[1])

    fltpath = argvs[1].split('=')[1]
    classifyString = argvs[2].split('=')[1]
    classifyList = ast.literal_eval(classifyString)
    classify = numpy.array(classifyList)
    outGeoJsonPath = argvs[3].split('=')[1]
    fltToGeoJson(fltpath, classify, outGeoJsonPath)

