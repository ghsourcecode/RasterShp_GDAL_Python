#!/usr/bin/env python
# encoding: utf-8
'''
用gsconfig-1.0.9操作geoserver rest api
@author: DaiH
@date: 2018/6/7 17:59
'''

from geoserver.catalog import Catalog
import geoserver.util as geoUtil
cat = Catalog('http://localhost:8090/geoserver/rest', username="admin", password="geoserver")

def getPostWorkspaceDataStore():
    print('用gsconfig获取/创建workspace、datastore')
    workspace = cat.get_workspace('workspaceName')
    if workspace is None:
        workspace = cat.create_workspace('workspaceName', 'http://example.com/testWorkspace')
    datastore = cat.get_store('datastoreName')
    if datastore is None:
        datastore = cat.create_datastore('datastoreName', 'newWorkspaceName')
    print('datastore success')
    print('workspace success')

def publishShpLayerFromFeatureStore(workspaceName, workspaceUri, featureStoreName, layerName, shpPath,
                                    over_write=False, native_crs='EPSG:4326', srs='EPSG:4326'):
    print('创建featurestore并发布layer')
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = cat.create_workspace(workspaceName, workspaceUri)
    shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
    featureStore = cat.get_store(featureStoreName, workspace)
    if featureStore is None:
        cat.create_featurestore(featureStoreName, shapefile_plus_sidecars, workspace)
        featureStore = cat.get_store(featureStoreName, workspace)
    publishedLayer = cat.publish_featuretype(layerName, featureStore, over_write, native_crs, srs)
    print('success')
    return publishedLayer

def publishShpLayerFromDataStore(workspaceName, workspaceUri, dataStoreName, layerName, shpPath,
                                 over_write=False, native_crs='EPSG:4326', srs='EPSG:4326'):
    print('创建datastore，上传shp到datastore中，并发布layer')
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = cat.create_workspace(workspaceName, workspaceUri)
    shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
    dataStore = cat.get_store(dataStoreName, workspaceName)
    if dataStore is None:
        dataStore = cat.create_datastore(dataStoreName, workspaceName)
    cat.add_data_to_store(dataStore, layerName, shapefile_plus_sidecars, workspaceName)
    publishedLayer = cat.publish_featuretype(layerName, dataStore, over_write, native_crs, srs)
    print('publish success')

def publishLayerFromPostGIS():
    print('从postgis数据发布图层，暂时未实现')

def modifyDataStore(workspaceName, dataStoreName):
    print('修改datastore属性，并保存')
    dataStore = cat.get_store(dataStoreName, workspaceName)
    # at this point that_store is still enabled in GeoServer
    dataStore.enabled = False
    # now it is disabled
    cat.save(dataStore)

def createStyleFromSldFile(styleName, sldFilePath):
    print('从sld文件创建style')
    sldFile = open(sldFilePath)
    str = sldFile.read().encode('utf-8')
    createdStyle = cat.create_style(styleName, str, overwrite=True)
    print('style publish success')

def setLayerStyle(layer, styleName):
    print('设置发布的layer的style')
    # 设置layer新style
    layer.default_style = styleName
    cat.save(layer)

def deleteStyle(styleName):
    print('删除style')
    style = cat.get_style(styleName)
    if style is not None:
        cat.delete(style, recurse=True) #recurse标识该style被使用时，是否删除

if __name__ == '__main__':
    # getPostWorkspaceDataStore()

    workspaceName = 'acme31'
    workspaceUri = 'www.decom.cn/' + workspaceName
    datastoreName = 'ds31'
    layerName = 'p_layer31'
    shpPath = 'E:/Data/geowebcachedata/publish/prov_region'
    # publishShpLayerFromFeatureStore()
    # publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath)

    styleName = 'test_style'
    sldFilePath = 'mytest_province_sld.xml'
    createStyleFromSldFile(styleName, sldFilePath)

    layer = cat.get_layer(layerName)
    # setLayerStyle(layer, styleName)

    deleteStyle(styleName)
