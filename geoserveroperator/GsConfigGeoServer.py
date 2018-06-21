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
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = cat.create_workspace(workspaceName, workspaceUri)
    return workspace

def deleteWorkspace(workspaceName):
    workspace = cat.get_workspace(workspaceName)
    try:
        cat.delete(workspace, purge=None, recurse=True) #recurse 标识是否删除包含内容的对象
    except FailedRequestError as e:
        print(e)
    except Exception as e:
        print(e)

def createDataStore(datastoreName, workspaceName):
    datastore = cat.get_store(datastoreName, workspaceName)
    if datastore is None:
        datastore = cat.create_datastore(datastoreName, workspaceName)
    return datastore

def deleteDataStore(datastoreName, workspaceName):
    datastore = cat.get_store(datastoreName, workspaceName)
    try:
        cat.delete(datastore, purge=None, recurse=True)
    except Exception as e:
        print(e)

def publishShpLayerFromFeatureStore(workspaceName, workspaceUri, featureStoreName, layerName, shpPath,
                                    native_crs='EPSG:4326', srs='EPSG:4326'):
    '''
    2018-6-12:
    该方法在测试后，出现无法发布featuretype的问题，暂时不知道原因，所以用下面的方法替换
    2018-6-19:
    经过测试，发现该方法中的 cat.publish_featuretype 只能用于发布postgis数据库中的数据，采用如下所示示例，具体还有待测试;
    要发布shp数据的wms服务，应该用publishShpLayerFromDataStore方法
    '''
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = cat.create_workspace(workspaceName, workspaceUri)
    shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
    featureStore = cat.get_store(featureStoreName, workspace)
    if featureStore is None:
        featureStore = cat.create_datastore('newDatastoreName', 'newWorkspaceName')
        featureStore.connection_parameters.update(host='localhost', port='5432', database='postgis', user='postgres',
                                        passwd='password', dbtype='postgis', schema='postgis')
        cat.save(featureStore)
    publishedLayer = cat.publish_featuretype(layerName, featureStore, native_crs, srs)
    print('success')
    return publishedLayer

def publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath,
                                 native_crs='EPSG:4326', srs='EPSG:4326'):
    '''
    2018-6-19：
    经测试，调用 cat.add_data_to_store 方法后，不需要再调用cat.publish_featuretype方法，即可发布shp数据wms服务
    :param shpPath: shppath中的shape文件名不能包含扩展名.shp
    '''
    workspace = cat.get_workspace(workspaceName)
    if workspace is None:
        workspace = createWorkspace(workspaceName, workspaceUri)
    dataStore = cat.get_store(datastoreName, workspaceName)
    if dataStore is None:
        dataStore = createDataStore(datastoreName, workspaceName)
    shapefile_plus_sidecars = geoUtil.shapefile_and_friends(shpPath)
    # 将shp数据添加到datastore中，添加之后，即发布了wms服务
    cat.add_data_to_store(dataStore, layerName, shapefile_plus_sidecars, workspaceName, overwrite = True)

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

def createLayerGroup(layerGropuName, layernames, styles, workspaceName):
    print('创建layer group')
    try:
        cat.create_layergroup(layerGropuName, layernames, workspace = workspaceName)
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
    sldFile = open(sldFilePath)
    str = sldFile.read().encode('utf-8')
    style = cat.get_style(styleName)
    if style is not None:
        cat.create_style(styleName, str, overwrite=True)
    else:
        cat.create_style(styleName, str)


def setLayerStyle(layer, styleName):
    print('设置发布的layer的style')
    # 设置layer新style
    layer.default_style = styleName
    cat.save(layer)
    cat.get

def deleteStyle(styleName):
    print('删除style')
    style = cat.get_style(styleName)
    if style is not None:
        cat.delete(style, recurse=True) #recurse标识该style被使用时，是否删除



if __name__ == '__main__':
    # getPostWorkspaceDataStore()

    workspaceName = 'layerGroupWorkspace1'
    workspaceUri = 'www.decom.cn/' + workspaceName
    datastoreName = 'layerGropuDataStore1'
    layerName = 'provregion'
    shpPath = 'E:/Data/geowebcachedata/publish/provregion'
    layerName2 = 'jiangxi_river2'
    shpPath2 = 'E:/Data/geowebcachedata/publish/jiangxi_river2'
    # createWorkspace(workspaceName, workspaceUri)
    # deleteWorkspace(workspaceName)
    # publishShpLayerFromFeatureStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath)


    # testGroup = cat.get_layergroup('testgroup', workspaceName)

    # publishShpLayerFromDataStore("testcreatewebcache", 'www.decom.cn/testcreatewebcache', 'testcreatedatastore', 'webcache', 'E:/Data/geowebcachedata/publish/county')

    # publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName, shpPath)
    # publishShpLayerFromDataStore(workspaceName, workspaceUri, datastoreName, layerName2, shpPath2)
    # layer1 = cat.get_layer(layerName)
    # layer2 = cat.get_layer(layerName2)
    # layerList = [layer1, layer2]
    # layerNameList = [layerName, layerName2]
    #
    # provStyleName = 'prov_style'
    # polygonSldPath = 'mytest_province_sld.xml'
    # createStyleFromSldFile(provStyleName, polygonSldPath)
    # riverStyleName = 'river2_style'
    # lineSldPath = 'mytest_line_sld.xml'
    # createStyleFromSldFile(riverStyleName, lineSldPath)
    # style1 = cat.get_style(provStyleName)
    # style2 = cat.get_style(riverStyleName)
    # styleList = [provStyleName, riverStyleName]
    # styleNameList = [provStyleName, riverStyleName]
    #
    # # 测试创建 layergroup
    # layerGroupName = 'testLayerGroup2'
    # lg = cat.create_layergroup(layerGroupName)
    # lg.layers = layerNameList
    # lg.styles = styleNameList
    # lg.workspace = workspaceName
    # # lg.bounds = [str(73.441277), str(135.086930), str(18.159829), str(53.561771), 'EPSG:4326'] # minx, maxx, miny, maxy, crs = box
    # cat.save(lg)

    # deleteLayerGroup(layerGroupName, workspaceName)

    # deleteDataStoreFromWorkspace(datastoreName, workspaceName)

    # layer = cat.get_stylelayer(layerName)
    # setLayerStyle(layer, styleName)

    # deleteStyle(styleName)


    print('sdsl')
