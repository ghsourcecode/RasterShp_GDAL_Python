#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/6/15 16:06
'''

import uuid
import json
import requests
import geoserver.util as geoUtil
from geoserver.catalog import Catalog, FailedRequestError

class GsConfigOperatorGeoServer:
    def __init__(self, cat):
        self.cat = cat

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

    def getWMSLayer(self, layerName):
        return self.cat.get_layer(layerName)

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

    def seedLayer(self, geoserverUri, auth, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount):
        '''

        :param geoserverUri:  http://localhost:8090/geoserver
        :param gridsetId: 该值必须是发布的wmslayer tilecache 设置的gridsets中的一个，如果不是会报错
        :param zoomStart: 开始缓存的级别
        :param zoomStop:
        :param threadCount:
        :return:
        '''
        url = geoserverUri + '/gwc/rest/seed/' + wmsLayerName + '.json'
        headers = {'Content-type': 'application/json'}
        data = {
            'seedRequest': {
                'name': str(uuid.uuid1()),
                'gridSetId': gridsetId,
                'format': 'image/jpeg',
                'zoomStart': zoomStart,
                'zoomStop': zoomStop,
                'type': 'seed',
                 # seedType: 缓存类型，可取值为:seed (add tiles), reseed (replace tiles), or truncate (remove tiles)
                'threadCount': threadCount
            }
        }
        jsonData = json.dumps(data)
        response = requests.post(url, auth=auth, data=jsonData, headers=headers)
        return response.status_code