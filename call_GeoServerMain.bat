rem 说明
rem geoserverUri 为部署的geoserver服务器地址
rem username和password 为geoserver用户名和密码
rem workspaceName是要发布的工作空间名称，类似分类的大类
rem datastore是对应具体shp数据的存储位置文件夹名称，一般在geoserver部署目录data/data文件夹下，发布数据时，不同的shp数据，最好用不同的名称，因为在进行测试时发现，向同一个datastore中上传多个shp文件后，再次发布以前的shp数据wms服务失败，具体原因未知
rem layerName是发布服务后的图层名称
rem shpPath是要发布的shape文件路径，shp文件要包含'shx'、'shp'、'dbf'、'prj'几个文件，但路径中不能包含shp文件扩展名
rem styleName是设置要发布服务的图层的样式名，参数值可为字符串或none，如果styleName不为none，需要保证geoserver上已存在该名称的style，或设置sldPath，程序会发布style至geoserver服务器，并设置为styleName
rem sldPath是要发布sld文件路径（要用绝对路径）
rem isCached指示是否预先缓存发布的服务的瓦片，取值为true/false（不区分大小写），如果为false，则后面的参数几个有缓存的参数全部设置none；如果为true，后面的参数必须设置
rem gridsetID指缓存方案ID，目前只能设置为EPSG:3857,该方案在安装geoserver时已经添加
rem zoomStart、zoomStop、threadCount指缓存起始级别、结束级别和缓存瓦片的线程数，线程数越大，切割瓦片越快，但对机器性能要求高
rem outFilePath指发布服务后的服务地址和图层名称输出的txt文件位置（要用绝对路径）
CHCP 65001
python E:/PycharmProject/gdalpython2/GeoServerMain.py geoserverUri=http://localhost:8090/geoserver username=admin password=geoserver workspaceName=publish_workspace_name datastoreName=publish_datastore_name layerName=publish_layer_name shpPath=E:/Data/geowebcachedata/county styleName=none sldPath=publish_style_path isCached=true gridsetID=EPSG:3857 zoomStart=0 zoomStop=6 threadCount=6 outFilePath=E:/temp/out.txt
@pause