#!/usr/bin/env python
# encoding: utf-8
'''
用gsconfig-1.0.9操作geoserver rest api
@author: DaiH
@date: 2018/6/7 17:59
'''

from geoserver.catalog import Catalog, FailedRequestError
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

def createWorkspace(workspaceName, workspaceUri):
    print('创建workspace')
    workspace = cat.create_workspace(workspaceName, workspaceUri)
    if workspace is None:
        print('创建workspace失败')
    else:
        print('创建workspace成功')

def deleteWorkspace(workspaceName):
    print('删除workspace')
    workspace = cat.get_workspace(workspaceName)
    try:
        cat.delete(workspace, purge=None, recurse=True) #recurse 标识是否删除包含内容的对象
    except FailedRequestError as e:
        print(e)
    except Exception as e:
        print(e)

def publishShpLayerFromFeatureStore(workspaceName, workspaceUri, featureStoreName, layerName, shpPath,
                                    native_crs='EPSG:4326', srs='EPSG:4326'):
    '''
    该方法在2018-6-12测试后，出现无法发布featuretype的问题，暂时不知道原因，所以用下面的方法替换
    '''
    print('创建featurestore并发布layer')
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = cat.create_workspace(workspaceName, workspaceUri)
    shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
    featureStore = cat.get_store(featureStoreName, workspace)
    if featureStore is None:
        cat.create_featurestore(featureStoreName, shapefile_plus_sidecars, workspace)
        featureStore = cat.get_store(featureStoreName, workspace)
    publishedLayer = cat.publish_featuretype(layerName, featureStore, native_crs, srs)
    print('success')
    return publishedLayer

def publishShpLayerFromDataStore(workspaceName, workspaceUri, dataStoreName, layerName, shpPath,
                                 native_crs='EPSG:4326', srs='EPSG:4326'):
    print('创建datastore，上传shp到datastore中，并发布layer')
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = cat.create_workspace(workspaceName, workspaceUri)
    shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
    dataStore = cat.get_store(dataStoreName, workspaceName)
    if dataStore is None:
        dataStore = cat.create_datastore(dataStoreName, workspaceName)
    cat.add_data_to_store(dataStore, layerName, shapefile_plus_sidecars, workspaceName)
    publishedFeatureType = cat.publish_featuretype(layerName, dataStore, native_crs, srs)
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

def deleteDataStoreFromWorkspace(dataStoreName, wrokspaceName):
    print('从worrkspace中删除datastore')
    datastore = cat.get_store(dataStoreName, wrokspaceName)
    try:
        cat.delete(datastore, purge=None, recurse=True) #recurse 标识是否删除包含内容的对象
    except Exception as e:
        print(e)

def createLayerGroup(layerGropuName, layers, styles, workspace):
    print('创建layer group')
    try:
        cat.create_layergroup(layerGropuName, layers, workspace = workspace)
    except Exception as e:
        print(e)

def deleteLayerGroup(layerGroupName, workspaceName):
    print('删除layer group')
    layerGroup = cat.get_layergroup(layerGroupName, workspaceName)
    cat.delete(layerGroup, purge=None, recurse=True)
    print('delete success')


def testCreateLayerGroup():
    print('测试创建layergroup')
    workspaceName = 'bc51'
    workspaceUri = 'www.decom.cn/' + workspaceName
    datastoreName = 'dd51'
    createWorkspace(workspaceName, workspaceUri)

    layerName = 'prov_region'
    shpPath = 'E:/Data/geowebcachedata/publish/prov_region'
    layerName2 = 'river2'
    shpPath2 = 'E:/Data/geowebcachedata/publish/river2'
    layerNameList = [layerName, layerName2]
    publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath)
    publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName2, shpPath2)

    provStyleName = 'prov_style'
    polygonSldPath = 'mytest_province_sld.xml'
    createStyleFromSldFile(provStyleName, polygonSldPath)
    riverStyleName = 'river2_style'
    lineSldPath = 'mytest_line_sld.xml'
    createStyleFromSldFile(riverStyleName, lineSldPath)
    styleList = [provStyleName, riverStyleName]
    styleNameList = [provStyleName, riverStyleName]

    # 测试创建 layergroup
    layerGroupName = 'testLayerGroup2'
    layerGroup = cat.create_layergroup(layerGroupName)
    layerGroup.layers = layerNameList
    layerGroup.styles = styleNameList
    layerGroup.workspace = workspaceName
    layerGroup.bounds = [str(73.441277), str(135.086930), str(18.159829), str(53.561771), 'EPSG:4326']  # minx, maxx, miny, maxy, crs = box
    cat.save(layerGroup)

def createStyleFromSldFile(styleName, sldFilePath):
    print('从sld文件创建style')
    sldFile = open(sldFilePath)
    str = sldFile.read().encode('utf-8')
    style = cat.get_style(styleName)
    if style is not None:
        cat.create_style(styleName, str, overwrite=True)
    else:
        cat.create_style(styleName, str)

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

    workspaceName = 'layerGroupWorkspace'
    workspaceUri = 'www.decom.cn/' + workspaceName
    datastoreName = 'layerGropuDataStore'
    layerName = 'prov_region'
    shpPath = 'E:/Data/geowebcachedata/publish/prov_region'
    layerName2 = 'river2'
    shpPath2 = 'E:/Data/geowebcachedata/publish/river2'
    # createWorkspace(workspaceName, workspaceUri)
    # deleteWorkspace(workspaceName)
    # publishShpLayerFromFeatureStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath)


    # testGroup = cat.get_layergroup('testgroup', workspaceName)

    publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath)
    publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName2, shpPath2)
    layer1 = cat.get_layer(layerName)
    layer2 = cat.get_layer(layerName2)
    layerList = [layer1, layer2]
    layerNameList = [layerName, layerName2]

    provStyleName = 'prov_style'
    polygonSldPath = 'mytest_province_sld.xml'
    createStyleFromSldFile(provStyleName, polygonSldPath)
    riverStyleName = 'river2_style'
    lineSldPath = 'mytest_line_sld.xml'
    createStyleFromSldFile(riverStyleName, lineSldPath)
    style1 = cat.get_style(provStyleName)
    style2 = cat.get_style(riverStyleName)
    styleList = [provStyleName, riverStyleName]
    styleNameList = [provStyleName, riverStyleName]

    # 测试创建 layergroup
    layerGroupName = 'testLayerGroup2'
    lg = cat.create_layergroup(layerGroupName)
    lg.layers = layerNameList
    lg.styles = styleNameList
    lg.workspace = workspaceName
    lg.bounds = [str(73.441277), str(135.086930), str(18.159829), str(53.561771), 'EPSG:4326'] # minx, maxx, miny, maxy, crs = box
    cat.save(lg)

    # deleteLayerGroup(layerGroupName, workspaceName)

    # deleteDataStoreFromWorkspace(datastoreName, workspaceName)

    # layer = cat.get_stylelayer(layerName)
    # setLayerStyle(layer, styleName)

    # deleteStyle(styleName)
