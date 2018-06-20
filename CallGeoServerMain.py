#!/usr/bin/env python
# encoding: utf-8
'''
调用geoserver发布wms/wmts服务，并可根需要是否预先生成瓦片
为了保证生成可用在arcgis for js 4.x版加载预先生成的瓦片，在安装好geoserver时，应当根据geoserver已有的epsg:900913 gridset
瓦片切割方式，创建 epsg:3857的gridset（两种投影类型一致，只是名称不一样）
@author: DaiH
@date: 2018/6/15 9:26
'''

import threading
from geoserver.catalog import Catalog, FailedRequestError
from geoserveroperator.GsConfigOperatorGeoServer import GsConfigOperatorGeoServer

global cat
global gsconfigGeoServerInstance

def publishWmsLayer(workspaceName, workspaceUri, datastoreName, layerName, shpPath,
                    native_crs='EPSG:4326', srs='EPSG:4326'):
    '''
    将shp图发布成wms/wmts服务，并返回wms/wmts url，
    :param workspaceName:
    :param workspaceUri:
    :param datastoreName:
    :param layerName: 发布之后，图层的名称
    :param shpPath:
    :param native_srs: shp图空间参考
    :param srs: 发布之后的空间参考
    :return: wms/wmts地址
    '''
    layer = gsconfigGeoServerInstance.getWMSLayer(layerName)
    wmsLayerName = workspaceName + ':' + layerName
    if layer is not None:
        print('The \'' + layerName + '\' already exists in geoserver.')
        return gsconfigGeoServerInstance.cat.gs_base_url + '/' + workspaceName + '/wms', wmsLayerName,\
           gsconfigGeoServerInstance.cat.gs_base_url + '/gwc/rest/wmts/' + wmsLayerName + '/default/' + srs + '/' + srs +':{level}/{row}/{col}?format=image/png'
    gsconfigGeoServerInstance.publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath, native_crs, srs)
    return gsconfigGeoServerInstance.cat.gs_base_url + workspaceName + '/wms', wmsLayerName,\
           gsconfigGeoServerInstance.cat.gs_base_url + 'gwc/rest/wmts/' + wmsLayerName + '/default/' + srs + '/' + srs +':{level}/{row}/{col}?format=image/png'

def setWMSLayerStyle(wmsLayer, styleName, sldFilePath):
    style = gsconfigGeoServerInstance.createStyleFromSldFile(styleName, sldFilePath)
    wmsLayer.default_style = styleName
    cat.save(wmsLayer)

def seedWMSLayer(geoserverUri, auth, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount):
    '''
    :param geoserverUri: geoserver地址，例如：http://localhost:8090/geoserver
    :param auth: 连接geoserver的用户名和密码
    :param wmsLayerName:要切片的已发布为wms 服务的layer名称
    :param gridsetId: 指输出瓦片的预定义规则
    :param zoomStart:开始层级
    :param zoomStop:结束层级
    :param threadCount:线程个数
    :return:
    '''
    print('seeding……')
    thread = threading.Thread(group=None, target=gsconfigGeoServerInstance.seedLayer,
                              args=(geoserverUri, auth, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount))
    thread.start()


if __name__ == '__main__':
    print('生成geoserver wms/wmts服务')
    geoserverUri = 'http://localhost:8090/geoserver'
    username = 'admin'
    password = 'geoserver'
    auth = (username, password)
    # 初始化catalog
    cat = Catalog(geoserverUri + '/rest', username=username, password=password)
    gsconfigGeoServerInstance = GsConfigOperatorGeoServer(cat)

    workspaceName = 'wpname'
    workspaceUri = 'http://decom.cn/wpname'
    datastoreName = 'dsname'
    layerName = 'lyname'
    shpPath = 'E:/Data/geowebcachedata/county'
    styleName = 'countystyle'
    sldPath = 'geoserveroperator/mytest_province_sld.xml'
    wmsURL, wmsLayerName, wmtsURL = publishWmsLayer(workspaceName, workspaceUri, datastoreName, layerName, shpPath, styleName, sldPath)

    wmsLayerName = workspaceName + ':' + layerName
    gridsetId = 'EPSG:3857'
    zoomStart = 0
    zoomStop = 5
    threadCount = 6
    seedWMSLayer(geoserverUri, auth, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount)
    print('pre seed……')

