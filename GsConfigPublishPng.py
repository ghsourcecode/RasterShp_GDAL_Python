#!/usr/bin/env python
# encoding: utf-8
'''
该类主要完成通过gsconfig发布 worldimage栅格图，即将没有坐标的jpg和png发布为wms服务

@author: DaiH
@date: 2018/9/13 13:52
'''
import os
import sys
import cv2
import numpy
import shutil
from osgeo import gdal
from osgeo import osr
from geoserver.catalog import Catalog, FailedRequestError
# cat = Catalog("http://localhost:8081/geoserver/rest", username="admin", password="geoserver")

global cat
'''tiff的wgs84坐标范围'''
global tiffBound;

def createPngWmsLayer():
    print("publish png wms layer")
    worksapceName = "pngWorkspace1"
    datastoreName = "pngDataStore1"
    pngWorkspace = cat.get_workspace(worksapceName)
    if pngWorkspace is None:
        pngWorkspace = cat.create_workspace(worksapceName, "http://localpng.com/pngWorkspace1")
    pngDataStore = cat.get_store(datastoreName, workspace=pngWorkspace)
    data = "E:/Data/temp/rtest.png"
    if pngDataStore is None:
        pngDataStore = cat.create_coveragestore(datastoreName, data=data, workspace=pngWorkspace)

    data = "file:coverages/img_sample/rtest.png"
    cat.add_data_to_store(store=pngDataStore, name= "pnglayer", data=data, workspace=pngWorkspace)
    # pngWmsLayer = cat.create_wmslayer(workspace=pngWorkspace, store=pngDataStore, name="pngWmsLayer", nativeName="pngWmsLayer")
    print("create wmslayer end")

def convertPngToTiff(pngPath, outTiffPath):
    # img = cv2.imread(pngPath)
    img = cv2.imdecode(numpy.fromfile(pngPath, dtype=numpy.uint8), cv2.IMREAD_COLOR) # 解决中文路径问题
    blue, green, red = cv2.split(img)

    '''numpy size方法求array行列数'''
    # rows = numpy.size(blue, 0)#行数
    # cols = numpy.size(blue, 1)#列数
    '''numpy shape方法求array行列数'''
    rows = blue.shape[0]
    cols = blue.shape[1]
    alpha = numpy.zeros((rows, cols))  # 透明度
    for rowIndex in range(rows):
        for colIndex in range(cols):
            b = blue[rowIndex][colIndex]
            g = green[rowIndex][colIndex]
            r = red[rowIndex][colIndex]
            if b == g == r == 0:
                alpha[rowIndex][colIndex] = 0
            else:
                alpha[rowIndex][colIndex] = 255

    imgDataList = []
    imgDataList.append(red)
    imgDataList.append(green)
    imgDataList.append(blue)
    imgDataList.append(alpha) # 透明度波段
    imgData = numpy.array(imgDataList, dtype=numpy.int8)

    prj = osr.SpatialReference()
    prj.ImportFromEPSG(4326)
    prjWkt = prj.ExportToWkt()

    minx = tiffBound[0]
    maxx = tiffBound[1]
    miny = tiffBound[2]
    maxy = tiffBound[3]

    xres = (maxx - minx) / cols
    yres = (maxy - miny) / rows

    transform = (minx, xres, 0, maxy, 0, -yres)

    writeTiff(imgData, cols, rows, 4, transform, prjWkt, outTiffPath)

def writeTiff(im_data, im_width, im_height, im_bands, im_geotrans, im_proj, path):
    '''
    用gdal 生成geotiff
    :param im_data: 要生成tif的像互值
    :param im_width: tif 宽度
    :param im_height:
    :param im_bands: 波段数
    :param im_geotrans: tif坐标范围等转换参数
    :param im_proj: 投影
    :param path: 输出路径
    :return:
    '''
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
        im_bands, (im_height, im_width) = 1,im_data.shape
    #创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, im_width, im_height, im_bands, datatype)

    if(dataset!= None):
        dataset.SetGeoTransform(im_geotrans) #写入仿射变换参数
        dataset.SetProjection(im_proj) #写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i+1).WriteArray(im_data[i])

    dataset.FlushCache()
    del dataset

def publishGeoTiff(geotiffPath, workspaceName, datastoreName, overwrite=False):
    tiffWorkspace = cat.get_workspace(workspaceName)
    if not tiffWorkspace:
        tiffWorkspace = cat.create_workspace(workspaceName, "http://localhost:8081/workspace/" + workspaceName)
    # tiffDatastore = cat.get_store(tiffDatastoreName, tiffWorkspace)
    # if not tiffDatastore:
    #     tiffDatastore = cat.create_coveragestore(tiffDatastoreName, geotiffPath, tiffWorkspace, overwrite)
    tiffDatastore = cat.create_coveragestore(datastoreName, geotiffPath, tiffWorkspace, overwrite)
    return cat.gs_base_url + workspaceName + "/wms", workspaceName + ":" + datastoreName

def deleteWorkspace(workspaceName):
    workspace = cat.get_workspace(workspaceName)
    try:
        cat.delete(workspace, purge=None, recurse=True) #recurse 标识是否删除包含内容的对象
    except FailedRequestError as e:
        print(e)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    print("publish png wmslayer main")
    cat = Catalog("http://localhost:8081/geoserver/rest", username="admin", password="geoserver")

    '''测试opencv是否安装成功'''
    # img = cv2.imread("../testdata/pngToTiff/pngtotiff.png")
    # cv2.namedWindow("image window")
    # cv2.imshow("image window", img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # deleteWorkspace("geotiffWorkspace")
    # currentDir = os.getcwd();
    # print(os.path.abspath(os.path.dirname(currentDir) + os.path.sep + "."))
    # overwrite = True if (str(True).lower() == "true") else False
    # pngPath = "../testdata/pngToTiff/pngtotiff.png"
    # pngPath = "E:/临时工作/geoserver+python/release_v1.1/geoserver_python_release/data/pngtotif/pngtotiff.png"
    # outTiffPath = currentDir + "/tmp"
    # if not os.path.exists(outTiffPath):
    #     os.makedirs(outTiffPath)
    # outTiffPath += "/out12.tif"
    # convertPngToTiff(pngPath, outTiffPath)
    # workspaceName = "geotiffWorkspace"
    # datastoreName = "geotiffDatastore"
    # wmsUrl, wmsLayerName = publishGeoTiff(outTiffPath, workspaceName, datastoreName, True)
    # outURLPath = "../testdata/pngToTiff/out.txt"
    # outFile = open(r"E:\PycharmProject\gdalpython2\testdata\pngToTiff\out.txt", mode="w")
    # outFile.write("wmsUrl=" + wmsUrl + "\n")
    # outFile.write("wmsLayerName=" + wmsLayerName)
    # shutil.rmtree(os.path.abspath(os.path.dirname(outTiffPath) + os.path.sep + "."))

    '''cmd调用时走该代码'''
    geoserverUri = sys.argv[1].split('=')[1]
    username = sys.argv[2].split('=')[1]
    password = sys.argv[3].split('=')[1]
    cat = Catalog(geoserverUri + "/rest", username=username, password=password)
    pngPath = sys.argv[4].split('=')[1]
    # 经纬度范围
    # tiffBound = [104.394262, 112.099669, 20.833333, 26.599407];
    extent = sys.argv[5].split('=')[1]
    length = len(extent)
    extent = extent[1 : length - 1]
    extentArr = extent.split(",")
    if not len(extentArr) == 4:
        print("经纬度范围设置有误")
    minx =float(extentArr[0].strip())
    maxx =float(extentArr[1].strip())
    miny =float(extentArr[2].strip())
    maxy =float(extentArr[3].strip())
    tiffBound = [minx, maxx, miny, maxy]

    outTiffPathParent = os.path.abspath(os.path.dirname(pngPath) + os.path.sep + ".") + "/tmp"
    if not os.path.exists(outTiffPathParent):
        os.makedirs(outTiffPathParent)
    outTiffPath = outTiffPathParent + "/tempCovert.tif"
    convertPngToTiff(pngPath, outTiffPath)
    workspaceName = sys.argv[6].split('=')[1]
    datastoreName = sys.argv[7].split('=')[1]
    overwrite = sys.argv[8].split('=')[1]
    overwrite = True if (str(True).lower() == overwrite) else False
    wmsUrl, wmsLayerName = publishGeoTiff(outTiffPath, workspaceName, datastoreName, overwrite)
    outURLPath = sys.argv[9].split('=')[1]
    outURLPathParent = os.path.dirname(outURLPath) + os.path.sep + "."
    if not os.path.exists(outURLPathParent):
        os.makedirs(outURLPathParent)
    outFile = open(outURLPath, mode="w")
    outFile.write("wmsUrl=" + wmsUrl + "\n")
    outFile.write("wmsLayerName=" + wmsLayerName)
    shutil.rmtree(outTiffPathParent)