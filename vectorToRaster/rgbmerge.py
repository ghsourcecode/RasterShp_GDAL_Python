'''
将矢量栅格化时，输出的3个或4个tif图，融合成一个
'''

import os
import numpy
import util.globalVariable as globalVar

if __name__ == '__main__':
    root = os.path.dirname(os.getcwd())
    mergePyPath = root + '/gdal223/gdal_merge.py'
    out = root + '/testdata/outmerge.tif'
    r = root + '/testdata/outraster1.tif'
    g = root + '/testdata/outraster2.tif'
    b = root + '/testdata/outraster3.tif'
    a = root + '/testdata/outraster1.tif'
    os.system('python ' + mergePyPath + ' -separate -n 0 -a_nodata 0 -of GTiff -o ' + out + ' ' + r + ' ' + g + ' ' + b) #

