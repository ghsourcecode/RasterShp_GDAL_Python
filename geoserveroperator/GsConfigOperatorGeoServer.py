#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/6/15 16:06
'''

import uuid
import json
import time
import requests
import threading
import geoserver.util as geoUtil
from geoserver.catalog import Catalog, FailedRequestError

class GsConfigOperatorGeoServer:
    def __init__(self, cat):
        self.cat = cat
        self.geoserverUri = cat.gs_base_url[:cat.gs_base_url.rfind('/')]
        self.auth = (cat.username, cat.password)

    def getWorkspace(self, workspaceName):
        return self.cat.get_workspace(workspaceName)

    def createWorkspace(self, workspaceName, workspaceUri):
        workspace = self.cat.get_workspace(workspaceName)
        if workspace is None:
            workspace = self.cat.create_workspace(workspaceName, workspaceUri)
        return workspace

    def deleteWorkspace(self, workspaceName):
        workspace = self.cat.get_workspace(workspaceName)
        try:
            self.cat.delete(workspace, purge=None, recurse=True)  # recurse 标识是否删除包含内容的对象
        except FailedRequestError as e:
            print(e)
        except Exception as e:
            print(e)

    def getDataStore(self, datastoreName, workspaceName=None):
        return self.cat.get_store(datastoreName, workspaceName)

    def createDataStore(self, datastoreName, workspaceName):
        datastore = self.cat.get_store(datastoreName, workspaceName)
        if datastore is None:
            datastore = self.cat.create_datastore(datastoreName, workspaceName)
        return datastore

    def deleteDataStore(self, datastoreName, workspaceName):
        datastore = self.cat.get_store(datastoreName, workspaceName)
        try:
            self.cat.delete(datastore, purge=None, recurse=True)
        except Exception as e:
            print(e)

    def getStyle(self, styleName, workspaceName=None):
        return self.cat.get_style(styleName, workspaceName)

    def createStyleFromSldFile(self, styleName, sldFilePath):
        sldFile = open(sldFilePath)
        str = sldFile.read().encode('utf-8')
        style = self.cat.get_style(styleName)
        if style is not None:
            self.cat.create_style(styleName, str, overwrite=True)
        else:
            self.cat.create_style(styleName, str)

    def setLayerStyle(self, layer, styleName):
        # 设置layer新style
        layer.default_style = styleName
        self.cat.save(layer)

    def getLayerGruop(self, layerGroupName, workspaceName=None):
        return self.cat.get_layergroup(layerGroupName, workspaceName)

    def createLayerGroup(self, layerGroupName, layerNames, styleNames, workspaceName):
        layerGroup = self.cat.create_layergroup(layerGroupName)
        layerGroup.layers = layerNames
        layerGroup.styles = styleNames
        layerGroup.workspace = workspaceName
        # layerGroup.bounds = [str(73.441277), str(135.086930), str(18.159829), str(53.561771), 'EPSG:4326']  # minx, maxx, miny, maxy, crs = box
        self.cat.save(layerGroup)

    def getWMSLayer(self, wmsLayerName):
        return self.cat.get_layer(wmsLayerName)

    def publishShpLayerFromDataStore(self, workspaceName, workspaceUri, datastoreName, layerName, shpPath,
                                     native_crs='EPSG:4326', srs='EPSG:4326'):
        '''
        :param shpPath: shppath中的shape文件名不能包含扩展名.shp
        '''
        workspace = self.getWorkspace(workspaceName)
        if workspace is None:
            workspace = self.createWorkspace(workspaceName, workspaceUri)
        dataStore = self.getDataStore(datastoreName, workspaceName)
        if dataStore is None:
            dataStore = self.createDataStore(datastoreName, workspaceName)
        shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
        self.cat.add_data_to_store(dataStore, layerName, shapefile_plus_sidecars, workspaceName)

    def seedLayer(self, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount):
        '''
        :param geoserverUri:  http://localhost:8090/geoserver
        :param gridsetId: 该值必须是发布的wmslayer tilecache 设置的gridsets中的一个，如果不是会报错
        :param zoomStart: 开始缓存的级别
        :param zoomStop:
        :param threadCount:
        :return:
        '''
        url = self.geoserverUri + '/gwc/rest/seed/' + wmsLayerName + '.json'
        headers = {'Content-type': 'application/json'}
        data = {
            'seedRequest': {
                'name': str(uuid.uuid1()),
                'gridSetId': gridsetId,
                'format': 'image/jpeg',
                'zoomStart': zoomStart,
                'zoomStop': zoomStop,
                # seedType: 缓存类型，可取值为:seed (add tiles), reseed (replace tiles), or truncate (remove tiles)
                'type': 'seed',
                'threadCount': threadCount
            }
        }
        jsonData = json.dumps(data)
        response = requests.post(url, auth=self.auth, data=jsonData, headers=headers)
        print('resp_code: ' + str(response.status_code))
        return response.status_code

    def publishWmsLayer(self, workspaceName, workspaceUri, datastoreName, layerName, shpPath,
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
        layer = self.getWMSLayer(layerName)
        wmsLayerName = workspaceName + ':' + layerName
        if layer is not None:
            print('The \'' + layerName + '\' already exists in geoserver.')
            return self.geoserverUri + '/' + workspaceName + '/wms', wmsLayerName, \
                   self.geoserverUri + '/gwc/rest/wmts/' + wmsLayerName + '/default/' + srs + '/' + srs + ':{level}/{row}/{col}?format=image/png'
        self.publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName,
                                          layerName, shpPath, native_crs, srs)
        return self.geoserverUri + '/' + workspaceName + '/wms', wmsLayerName, \
               self.geoserverUri + '/' + 'gwc/rest/wmts/' + wmsLayerName + '/default/' + srs + '/' + srs + ':{level}/{row}/{col}?format=image/png'

    def setWMSLayerStyle(self, wmsLayer, styleName, sldFilePath=None):
        if sldFilePath is not None:
            self.createStyleFromSldFile(styleName, sldFilePath)
        wmsLayer.default_style = styleName
        self.cat.save(wmsLayer)

    def seedWMSLayer(self, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount):
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
        thread = threading.Thread(group=None, target=self.seedLayer,
                                  args=(wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount))
        thread.start()

    def getSeedStatus(self, wmsLayerName):
        # geoserverUri = 'http://localhost:8090/geoserver'
        url = self.geoserverUri + '/gwc/rest/seed/' + wmsLayerName + '.json'
        headers = {'Content-type': 'application/json'}
        response = requests.get(url, auth=self.auth, headers=headers)
        rsjson = json.loads(response.text)
        array = rsjson['long-array-array']
        isend = False
        if len(array) < 1:
            return 'DONE'
        # subarray: [tiles processed, total number of tiles to process, number of remaining tiles, Task ID, Task status]
        for subarray in array:
            status = subarray.pop(-1)  # Task status：-1 = ABORTED, 0 = PENDING, 1 = RUNNING, 2 = DONE
            if status != 2:
                isend = False
                break
            else:
                isend = True
        if isend:
            return 'DONE'
        else:
            return 'RUNNING'