#!/usr/bin/env python
###############################################################################
# $Id: nwt_grd.py 34386 2016-06-22 17:18:53Z rouault $
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test Northwood GRD driver
# Author:   Chaitanya kumar CH, <chaitanya at osgeo dot in>
#
###############################################################################
# Copyright (c) 2009, Chaitanya kumar CH, <chaitanya at osgeo dot in>
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

import sys
import shutil

sys.path.append('../pymod')

from osgeo import gdal
import gdaltest

###############################################################################
# Test a GRD dataset with three bands + Z

def nwt_grd_1():

    tst1 = gdaltest.GDALTest('NWT_GRD', 'nwt_grd.grd', 1, 28093)
    status1 = tst1.testOpen()
    tst2 = gdaltest.GDALTest('NWT_GRD', 'nwt_grd.grd', 2, 33690)
    status2 = tst2.testOpen()
    tst3 = gdaltest.GDALTest('NWT_GRD', 'nwt_grd.grd', 3, 20365)
    status3 = tst3.testOpen()
    tst4 = gdaltest.GDALTest('NWT_GRD', 'nwt_grd.grd', 4, 25856)
    status4 = tst4.testOpen()
    if status1 == 'success' and status2 == 'success' and status3 == 'success' and status4 == 'success':
        return 'success'
    else:
        return 'fail'

def nwt_grd_2():
    """
    Test writing a GRD via CreateCopy
    """
    shutil.copy('data/nwt_grd.grd', 'tmp/nwt_grd.grd')
    tst1 = gdaltest.GDALTest('NWT_GRD', 'tmp/nwt_grd.grd', 1, 25856, filename_absolute = 1, open_options = ['BAND_COUNT=1'])
    ret = tst1.testCreateCopy(new_filename = 'tmp/out.grd', check_minmax = 0, dest_open_options = ['BAND_COUNT=1'])
    gdal.Unlink('tmp/nwt_grd.grd')
    gdal.Unlink('tmp/nwt_grd.grd.aux.xml')
    return ret

gdaltest_list = [
    nwt_grd_1, nwt_grd_2 ]

if __name__ == '__main__':

    gdaltest.setup_run('nwt_grd')

    gdaltest.run_tests(gdaltest_list)

    gdaltest.summarize()

