rem 说明
rem geoserverUri 为部署的geoserver服务器地址
rem username和password 为geoserver用户名和密码
rem pngPath是要发布的png图片路径（要用绝对路径）
rem extent用于指定图片范围范围（经纬度）,minx/maxx是纬度, miny/maxy 是经度
rem workspaceName是要发布的工作空间名称，类似分类的大类
rem datastore是发布后图片的数据存储
rem overwrite指示是否覆盖workspace/datastore，可取false｜true
rem outFilePath服务发布成功后返回的服务地址存储文件路径(要用绝对地址)
CHCP 65001
python E:/PycharmProject/gdalpython2/GsConfigPublishPng.py geoserverUri=http://localhost:8081/geoserver username=admin password=geoserver pngPath=E:\PycharmProject\gdalpython2\testdata\pngToTiff\pngtotiff.png extent="[104.394262, 112.099669, 20.833333, 26.599407]" workspaceName=publish_png_workspace datastoreName=publish_png_datastore overwrite=true outFilePath=E:/temp/out.txt
@pause