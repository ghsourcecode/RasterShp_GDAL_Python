#!/usr/bin/env python
# encoding: utf-8
'''
实现在geoserver中对workspace、datastore、layergroup、layer、style的操作
@author: DaiH
@date: 2018/6/6 13:38
'''

import os
import sys
import uuid
import json
import requests


'''
requests库对rest的操作，主要用get、put、post、delete，为了和rest服务命名规则一致，以下函数的命名也以这几个关键字开头
'''
global geoserverRestUrl
geoserverRestUrl = 'http://localhost:8090/geoserver/rest'
auth = ('admin', 'geoserver')

def getWorkspaces():
    '''
    获取geoserver上workspaces，请求返回的内容为zip压缩过的html
    :return:
    '''
    url = geoserverRestUrl + '/workspaces'
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml,*/*;'}
    response = requests.get(url, auth=auth, headers=headers)
    print('response code:' + str(response.status_code))
    file = open('resp_workspaces.html', 'wb')
    file.write(response.content)
    file.close()

def getWorkspaces(name):
    print('获取指定name的workspace下的layer group')
    url = geoserverRestUrl + '/workspaces/' + name
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml,*/*;'}
    response = requests.get(url, auth=auth, headers=headers)
    print('response code:' + str(response.status_code))
    file = open('resp_workspaces.html', 'wb')
    file.write(response.content)
    file.close()

def postWorkspaces(name):
    print('创建workspaces')
    data = '<workspace><name>'+ name + '</name></workspace>'
    url = geoserverRestUrl + '/workspaces'
    headers = {'Content-type': 'text/xml'}
    response = requests.post(url, auth = auth, data=data, headers = headers)
    print('response code: ' + str(response.status_code))
    if response.status_code == 201:
        print('Success Created')
    elif response.status_code == 401:
        print('Unable to add workspace as it already exists')
    else:
        print('Failed Created')

def deleteWorkspaces(name, recurse=False):
    '''
    recurse 标识是否删除有内容的workspaces，False时，不删除
    '''
    print('删除workspaces')
    url = geoserverRestUrl + '/workspaces/' + name + '?recurse=' + str(recurse)
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml,*/*;'}
    response = requests.delete(url, auth = auth, headers = headers)
    print('response code: ' + str(response.status_code))

def getDataStoreFromWorkspace(workspaceName):
    print('获取workspace下的datastore列表')
    url = geoserverRestUrl + '/workspaces/' + workspaceName + '/datastores'
    headers = {'Accept' : 'text/html,application/xhtml+xml,application/xml,*/*'}
    response = requests.get(url, auth = auth, headers = headers)
    file = open('resp_datastore.html', 'wb')
    file.write(response.content)
    file.close()
    print('response code:' + str(response.status_code))

def getDataStoreFromWorkspace(workspaceName, datastoreName):
    print('获取workspace->datastore下的数据列表')
    url = geoserverRestUrl + '/workspaces/' + workspaceName + '/datastores/' + datastoreName
    headers = {'Accept' : 'text/html,application/xhtml+xml,application/xml,*/*'}
    response = requests.get(url, auth = auth, headers = headers)
    file = open('resp_datastore.html', 'wb')
    file.write(response.content)
    file.close()
    print('response code:' + str(response.status_code))

def postDataStoreToWorkspace(workspaceName, dataStoreName, shpPath):
    '''
    此方法没有接收要上传到datastore中的数据，此处只能上传shp
    :param workspaceName:
    :param dataStoreName:
    :return:
    '''
    print('在指定的workspace中创建datastore')
    url = geoserverRestUrl + '/workspaces/' + workspaceName + '/datastores'
    headers = {'Content-type' : 'application/xml'}
    # data的内容格式有xml和json，数据源类型：GeoPackage、PostGIS、Shapefile、Directory of spatial files (shapefiles)
    # 和Web Feature Service，不同的数据类型，dataStoreBody也不相同，
    # 具体查看：http://docs.geoserver.org/stable/en/user/rest/index.html#rest
    dataStoreBody = '<dataStore><name>'+ dataStoreName +'</name><connectionParameters><url>file://' + shpPath \
                    + '</url><filetype>shapefile</filetype></connectionParameters></dataStore>'
    response = requests.post(url, auth=auth, data=dataStoreBody, headers=headers)
    print('response_code: ' + str(response.status_code))

def putDataStoreInWorkspace(workspaceName, dataStoreName, newShpPath):
    print('更新workspace中的datastore')
    url = geoserverRestUrl + '/workspaces/' + workspaceName + '/datastores/' + dataStoreName
    headers = {'content-type':'application/xml'}
    newDataStoreBody = '<dataStore><name>'+ dataStoreName +'</name><enabled>true</enabled><connectionParameters><url>file://' + newShpPath \
                    + '</url><filetype>shapefile</filetype></connectionParameters></dataStore>'
    response = requests.put(url, auth=auth, data=newDataStoreBody, headers=headers)
    print('resp code: ' + str(response.status_code))

def putAddDataToDataStore(workspaceName, dataStoreName, shpPath):
    print('向datastore中增加数据')

def deleteDataStoreFromWorkspace(workspaceName, dataStoreName, recurse=False):#recurse 标识是否删除datastore内的数据,默认为false
    print('删除workspace中的datastore')
    url = geoserverRestUrl + '/workspaces/' + workspaceName + '/datastores/' + datastoreName + '?recurse=' + str(recurse)
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml,*/*;'}
    response = requests.delete(url, auth=auth, headers=headers)
    print('response code: ' + str(response.status_code))

def getWMS():
    '''
    获取其他服务的capabilities，只需要更改下面url中的wms为其他服务类型即可
    :return:
    '''
    print('获取geoserver上发布的wms的能力')
    url = geoserverRestUrl[:geoserverRestUrl.rfind('/')] + '/services/wms/workspaces/?service=wms&version=1.1.1&request=GetCapabilities'
    headers = {'Accept': 'application/xml'}
    response = requests.get(url, auth=auth, headers=headers)
    file = open('resp_wms.xml', 'wb')
    file.write(response.content)
    file.close()
    print('response code: ' + str(response.status_code))

def getStyles():
    print('获取geoserver服务器上的styles')
    url = geoserverRestUrl + '/styles'
    headers = {'Accept': 'application/xml'}
    response = requests.get(url, auth=auth, headers=headers)
    file = open('resp_styles.xml', 'wb')
    file.write(response.content)
    file.close()
    print('response code: ' + response.status_code)

def postStyle(styleFilePath):
    print('上传一个style')
    file = open(styleFilePath, 'r')
    content = file.read()
    url = geoserverRestUrl + '/styles'
    # application/xml,application/json,application/vnd.ogc.sld+xml
    headers = {'Content-type': 'application/vnd.ogc.sld+xml'}
    response = requests.post(url, auth=auth, data=content, headers=headers)
    print('response code: ' + str(response.status_code))

def seedLayer():
    '''
    json格式：
    seedRequest:{
      "name": "string",
      "bounds": {
        "coords": {}
      },
      "gridSetId": "string",
      "zoomStart": 0,
      "zoomStop": 0,
      "type": "seed",
      "threadCount": 0,
      "parameters": {
        "entry": {
          "string": "string"
        }
      }
    }
    :return:
    '''
    print('缓存瓦片')
    # 示例： http://localhost:8090/geoserver/gwc/rest/seed/{layer}.{format}, format的取值为json或xml
    url = 'http://localhost:8090/geoserver/gwc/rest/seed/layerGroupWorkspace:testLayerGroup2.json'
    headers = {'Content-type': 'application/json'}
    data = {
        'seedRequest':{
            'name': 'sedreq',
            'gridSetId': 'My_EPSG:3857',
            'format':'image/jpeg',
            'zoomStart': 0,
            'zoomStop': 5,
            'type': 'seed',     #可取值为：seed (add tiles), reseed (replace tiles), or truncate (remove tiles).
            'threadCount': 5
        }
    }
    jsonData = json.dumps(data)
    response = requests.post(url, auth=auth, data=jsonData, headers=headers)

    headersxml = {'Content-type': 'application/xml'}
    dataxml = '<seedRequest><name>seedreq</name><gridSetId>EPSG:4326</gridSetId><zoomStart>0</zoomStart><zoomStop>5</zoomStop><type>seed</type><threadCount>5</threadCount></seedRequest>'
    # response = requests.post(url, auth=auth, data=dataxml, headers=headersxml)
    # print('resp code: ' + str(response.status_code))

def getSeedingStatus():
    print('获取当前执行的seed的线程状态')
    url = geoserverRestUrl[:geoserverRestUrl.rfind('/')] + '/gwc/rest/seed.json'
    headers = {'Content-type': 'application/json'}
    response = requests.get(url, auth=auth, headers=headers)
    jsonresult = json.loads(response.text)['long-array-array']
    for result in jsonresult:
        status = result.pop(-1)
        print(status)
    print('resp_code: ' + str(response.status_code))



def seedLayer(geoserverUri, auth, wmsLayerName, gridsetId, zoomStart, zoomStop, threadCount):
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
            'type': 'seed', #seedType: 缓存类型，可取值为:seed (add tiles), reseed (replace tiles), or truncate (remove tiles)
            'threadCount': threadCount
        }
    }
    jsonData = json.dumps(data)
    response = requests.post(url, auth=auth, data=jsonData, headers=headers)
    return response.status_code


def createGridSet():
    print('创建gridset，即用于缓存瓦片的分级规则及分辨率')
    url = geoserverRestUrl[:geoserverRestUrl.rfind('/')] + '/gwc/rest/gridsets/my_epsg:3857'
    headers = {'Content-type': 'application/xml'}
    file = open('gridsetTestExample.xml', 'r')
    data = file.read()

    response = requests.put(url, auth=auth, data=data, headers=headers)

    print('resp code: ' + str(response.status_code))


def createGeoWebCacheLayer():
    '''
    该暂时不需要，还是是太清楚geoserver 提供geowebcache->layers接口的作用
    :return:
    '''
    print('创建geowebcache layer')
    url = 'http://localhost:8090/geoserver/gwc/rest/layers/testcreatewebcache:webcache.xml'
    headers = {'Content-type': 'application/xml'}
    data = {
        "GeoServerLayer":{
            "id": "createcachelayer",
            "enabled": "false",
            "inMemoryCached": "true",
            "name": "createcachelayerName",
            "mimeFormats": [
                "image/png"
            ],
            "gridSubsets": {
                "gridSubset": {
                    "gridSetName": "EPSG:4326",
                    "extent": {
                        "bounds": 0
                    },
                    "zoomStart": 0,
                    "zoomStop": 5
                }
            }
        }
    }
    jsonData = json.dumps(data)
    # response = requests.put(url, auth=auth, data=jsonData, headers=headers)

    xmlData = '<Layer>'\
                  '<id>testcreatewebcache:webcache</id>' \
                  '<enabled>true</enabled>' \
                  '<inMemoryCached>true</inMemoryCached>' \
                  '<name>testcreatewebcache:webcache</name>' \
                  '<mimeFormats>image/png</mimeFormats>' \
                  '<gridSubsets>' \
                    '<gridSubset>' \
                        '<gridSetName>My_EPSG:3857</gridSetName>' \
                        '<zoomStart>0</zoomStart>' \
                        '<zoomStop>5</zoomStop>' \
                    '</gridSubset>' \
                  '</gridSubsets>' \
              '</Layer>'
    response = requests.put(url, auth=auth, data=xmlData, headers=headers)


    print('resp code: ' + str(response.status_code))

def getGeoWebCacheLayer():
    print('获取已发布的layer')
    url = 'http://localhost:8090/geoserver/gwc/rest/layers/testcreatewebcache:webcache'
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml,*/*;'}
    response = requests.get(url, auth=auth, headers=headers)
    file = open('geowebcachelayer_layer.xml', 'wb')
    file.write(response.content)
    file.close()
    print('resp code: ' + str(response.status_code))

def getGeoWebCacheLayers():
    print('获取geowebcache layers')
    url = 'http://localhost:8090/geoserver/gwc/rest/layers'
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml,*/*;'}
    response = requests.get(url, auth=auth, headers=headers)
    file = open('geowebcachelayer.xml', 'wb')
    file.write(response.content)
    file.close()
    print('resp code: ' + str(response.status_code))

if __name__ == '__main__':
    # getWorkspaces()
    workspaceName = 'acme6'
    datastoreName = 'china_county_5'
    shpPath = 'E:/Data/geowebcachedata/county.shp'
    newShpPath = 'E:/Data/geowebcachedata/jiangxi_river2.shp'
    recure = True           #标识是否删除有内容的workspace
    # getWorkspaces(workspacename)
    # postWorkspaces(workspaceName)
    # deleteWorkspaces(workspaceName, recure)

    # getDataStoreFromWorkspace(workspaceName)
    # getDataStoreFromWorkspace(workspaceName, datastoreName)
    # postDataStoreToWorkspace(workspaceName, datastoreName, shpPath)
    # deleteDataStoreFromWorkspace(workspaceName, datastoreName, True)
    # putDataStoreInWorkspace(workspaceName, datastoreName, shpPath)

    styleFilePath = 'style_example.xml'
    # getWMS()
    # getStyles()
    # postStyle(styleFilePath)

    # seedLayer()
    # createGeoWebCacheLayer()
    # getGeoWebCacheLayer()
    # getGeoWebCacheLayers()

    # createGridSet()

    getSeedingStatus()
