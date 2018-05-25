#!/usr/bin/env python
# encoding: utf-8
'''
创建 tif
@author: DaiH
@date: 2018/5/21 16:45
'''

import os
import numpy
import random
import gdal, ogr, osr
import util.project as project


def createArray(width, height):
    array = numpy.zeros((height, width))
    for r in range(0, height):
        for c in range(0,width):
            array[r][c] = random.randint(0, 255)
    return array


def createTif(tifPath):
    width = 100
    height =100
    bands = 3
    pixel = 0.2
    originx = 0
    originy = 40

    driver = gdal.GetDriverByName('GTiff')
    outTifDataset = driver.Create(tifPath, width, height, bands, gdal.GDT_Int32)
    outTifDataset.SetGeoTransform((originx, pixel, 0, originy, 0, -pixel))
    prj = project.defineProject(4326)
    outTifDataset.SetProjection(prj.ExportToWkt())

    redBandArray = createArray(width, height)
    redBand = outTifDataset.GetRasterBand(1)
    redBand.WriteArray(redBandArray)
    redBand.FlushCache()

    greenBandArray = createArray(width, height)
    greenBand = outTifDataset.GetRasterBand(2)
    greenBand.WriteArray(greenBandArray)
    greenBand.FlushCache()

    blueBandArray = createArray(width, height)
    blueBand = outTifDataset.GetRasterBand(3)
    blueBand.WriteArray(blueBandArray)
    blueBand.FlushCache()

    del outTifDataset


if __name__ == '__main__':
    tifPath = 'E:/PycharmProject/gdalpython2/testdata/threeband.tif'
    createTif(tifPath)