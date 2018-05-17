#!/usr/bin/python
# -*- coding: UTF-8 -*-

import gdal, osr
from gdalconst import *

def rasterReproject():
    # 获取源数据及栅格信息
    gdal.AllRegister()
    src_data = gdal.Open("smallaster.img")
    # 获取源的坐标信息
    srcSRS_wkt = src_data.GetProjection()
    srcSRS = osr.SpatialReference()
    srcSRS.ImportFromWkt(srcSRS_wkt)
    # 获取栅格尺寸
    src_width = src_data.RasterXSize
    src_height = src_data.RasterYSize
    src_count = src_data.RasterCount
    # 获取源图像的仿射变换参数
    src_trans = src_data.GetGeoTransform()
    OriginLX_src = src_trans[0]
    OriginTY_src = src_trans[3]
    pixl_w_src = src_trans[1]
    pixl_h_src = src_trans[5]

    OriginRX_src = OriginLX_src + pixl_w_src * src_width
    OriginBY_src = OriginTY_src + pixl_h_src * src_height
    # 创建输出图像
    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    dst_data = driver.Create("tpix1.tif", src_width, src_height, src_count)
    # 设置输出图像的坐标
    dstSRS = osr.SpatialReference()
    dstSRS.ImportFromEPSG(4326)
    # 投影转换
    ct = osr.CoordinateTransformation(srcSRS, dstSRS)
    # 计算目标影像的左上和右下坐标,即目标影像的仿射变换参数
    OriginLX_dst, OriginTY_dst, temp = ct.TransformPoint(OriginLX_src, OriginTY_src)
    OriginRX_dst, OriginBY_dst, temp = ct.TransformPoint(OriginRX_src, OriginBY_src)

    pixl_w_dst = (OriginRX_dst - OriginLX_dst) / src_width
    pixl_h_dst = (OriginBY_dst - OriginTY_dst) / src_height
    dst_trans = [OriginLX_dst, pixl_w_dst, 0, OriginTY_dst, 0, pixl_h_dst]
    # print outTrans
    dstSRS_wkt = dstSRS.ExportToWkt()
    # 设置仿射变换系数及投影
    dst_data.SetGeoTransform(dst_trans)
    dst_data.SetProjection(dstSRS_wkt)
    # 重新投影
    gdal.ReprojectImage(src_data, dst_data, srcSRS_wkt, dstSRS_wkt, GRA_Bilinear)
    # 创建四级金字塔
    gdal.SetConfigOption('HFA_USE_RRD', 'YES')
    dst_data.BuildOverviews(overviewlist=[2, 4, 8, 16])
    # 计算统计值
    for i in range(0, src_count):
        band = dst_data.GetRasterBand(i + 1)
        band.SetNoDataValue(-99)
        print
        band.GetStatistics(0, 1)