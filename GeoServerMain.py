#!/usr/bin/env python
# encoding: utf-8
'''
调用geoserver发布wms/wmts服务，并可根需要是否预先生成瓦片
为了保证生成可用在arcgis for js 4.x版加载预先生成的瓦片，在安装好geoserver时，应当根据geoserver已有的epsg:900913 gridset
瓦片切割方式，创建 epsg:3857的gridset（两种投影类型一致，只是名称不一样）
@author: DaiH
@date: 2018/6/15 9:26
'''

import os
import sys
import shutil
import time
import threading
import operator
from geoserver.catalog import Catalog, FailedRequestError
from geoserveroperator.GsConfigOperatorGeoServer import GsConfigOperatorGeoServer

global cat
global gsconfigGeoServerInstance

class SeedThread(threading.Thread):
    def __init__(self, callback):
        super(SeedThread, self).__init__()
        self.callback = callback

    def run(self):
        time.sleep(5)
        self.callback(5)

def callback(result):
    print('callback ' + str(result))

def getSeedStatus(url, auth):
    while True:
        rsjson = gsconfigGeoServerInstance.getSeedingStatus(url, auth)
        array = rsjson['long-array-array']
        isend = False
        # subarray: [tiles processed, total number of tiles to process, number of remaining tiles, Task ID, Task status]
        for subarray in array:
            status = subarray.pop(-1) # Task status：-1 = ABORTED, 0 = PENDING, 1 = RUNNING, 2 = DONE
            if status != 2:
                isend = False
                break
            else:
                isend = True
        if isend:
            break
        time.sleep(1)
    return 'success'



# if __name__ == '__main__':
#     print('生成geoserver wms/wmts服务')
#     geoserverUri = 'http://localhost:8090/geoserver'
#     username = 'admin'
#     password = 'geoserver'
#     # auth = (username, password)
#     # 初始化catalog
#     cat = Catalog(geoserverUri + '/rest', username=username, password=password)
#     gsconfigGeoServerInstance = GsConfigOperatorGeoServer(cat)
#
#     workspaceName = 'wpname'
#     workspaceUri = geoserverUri + '/' + workspaceName
#     datastoreName = 'dsname'
#     layerName = 'lyname'
#     shpPath = 'E:/Data/geowebcachedata/county' #shp路径不能带扩展名
#     # 发布wms/wmts layer
#     wmsURL, wmsLayerName, wmtsURL = gsconfigGeoServerInstance.publishWmsLayer(workspaceName, workspaceUri, datastoreName, layerName, shpPath)
#     wmsLayer = gsconfigGeoServerInstance.getWMSLayer(wmsLayerName)
#     if wmsLayer is None:
#         raise RuntimeError('wmslayer 没有发布成功')
#
#     # 输出发布后的地址
#     mainModuleFolderAbsolutePath = sys.path[0] #主模块目录
#     outFileName = 'out.txt'
#     outFilePath = mainModuleFolderAbsolutePath + '/' + outFileName
#     if os.path.exists(outFilePath):
#         os.remove(outFilePath)
#     outStr = 'wmsURL=' + wmsURL + '\n' + 'wmsLayerName=' + wmsLayerName + '\n' + 'wmtsURL=' + wmtsURL
#     with open(outFilePath, 'w') as out:
#         out.write(outStr)
#
#     # 设置style
#     styleName = 'fltresolve'
#     sldPath = 'geoserveroperator/style/mytest_province_sld.xml'
#     gsconfigGeoServerInstance.setWMSLayerStyle(wmsLayer, styleName, sldPath)
#
#     # 生成wmslayer 瓦片
#     wmsLayerName = workspaceName + ':' + layerName
#     gridsetID = 'EPSG:3857'
#     zoomStart = 0
#     zoomStop = 9
#     threadCount = 6
#     gsconfigGeoServerInstance.seedWMSLayer(wmsLayerName, gridsetID, zoomStart, zoomStop, threadCount)
#
#     # 查看wmslayer生成瓦片状态
#     status = gsconfigGeoServerInstance.getSeedStatus(wmsLayerName)
#     while True:
#         if operator.eq(status, 'DONE'):
#             print('done')
#             break
#         else:
#             print('seeding……')
#             status = gsconfigGeoServerInstance.getSeedStatus(wmsLayerName)

    # print('thread start……')
    # callbackThread = SeedThread(callback)
    # callbackThread.start()
    # print('thread end')

if __name__ == '__main__':
    print('生成geoserver wms/wmts服务')
    tm = time.time()
    geoserverUri = sys.argv[1].split('=')[1]
    username = sys.argv[2].split('=')[1]
    password = sys.argv[3].split('=')[1]
    # 初始化catalog
    cat = Catalog(geoserverUri + '/rest', username=username, password=password)
    gsconfigGeoServerInstance = GsConfigOperatorGeoServer(cat)

    workspaceName = sys.argv[4].split('=')[1]
    workspaceUri = geoserverUri + '/' + workspaceName
    datastoreName = sys.argv[5].split('=')[1]
    layerName = sys.argv[6].split('=')[1]
    shpPath = sys.argv[7].split('=')[1]  # shp路径不能带扩展名
    # 发布wms/wmts layer
    wmsURL, wmsLayerName, wmtsURL = gsconfigGeoServerInstance.publishWmsLayer(workspaceName, workspaceUri,
                                                                              datastoreName, layerName, shpPath)
    wmsLayer = gsconfigGeoServerInstance.getWMSLayer(wmsLayerName)
    if wmsLayer is None:
        raise RuntimeError('wmslayer 没有发布成功')

    # 设置style
    styleName = sys.argv[8].split('=')[1]
    if not operator.eq(styleName.lower(), 'none'):
        sldPath = sys.argv[9].split('=')[1]
        gsconfigGeoServerInstance.setWMSLayerStyle(wmsLayer, styleName, sldPath)

    # 生成wmslayer 瓦片
    isCached = sys.argv[10].split('=')[1]
    if operator.eq(isCached.lower(), 'true'):
        wmsLayerName = workspaceName + ':' + layerName
        gridsetID = sys.argv[11].split('=')[1]
        zoomStart = int(sys.argv[12].split('=')[1])
        zoomStop = int(sys.argv[13].split('=')[1])
        threadCount = int(sys.argv[14].split('=')[1])
        gsconfigGeoServerInstance.seedWMSLayer(wmsLayerName, gridsetID, zoomStart, zoomStop, threadCount)

    # 查看wmslayer生成瓦片状态
    # status = gsconfigGeoServerInstance.getSeedStatus(wmsLayerName)
    # while True:
    #     if operator.eq(status, 'DONE'):
    #         print('done')
    #         break
    #     else:
    #         print('seeding……')
    #         status = gsconfigGeoServerInstance.getSeedStatus(wmsLayerName)

    # 输出发布后的地址
    outFilePath = sys.argv[15].split('=')[1]
    if os.path.exists(outFilePath):
        os.remove(outFilePath)
    outStr = 'wmsURL=' + wmsURL + '\n' + 'wmsLayerName=' + wmsLayerName + '\n' + 'wmtsURL=' + wmtsURL
    with open(outFilePath, 'w') as out:
        out.write(outStr)

    print('elipse time：' + str(time.time() - tm) + ' s')
