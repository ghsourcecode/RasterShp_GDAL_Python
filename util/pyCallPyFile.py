'''
在一个 py 文件中，编写：
import os
os.system("python filename")
filename最好是全路径+文件名；

如：
os.system('python E:/PycharmProject/gdalpython2/gdal223/ogr2ogr.py -f "GeoJSON" outputGeoJson.json flttoshp.shp')
其他方法：

    execfile('xx.py')，括号内为py文件路径；

    如果需要传参数，就用os.system()那种方法；

    如果还想获得这个文件的输出，那就得用os.popen（）；

example:
Convert ESRI Shapefile to geoJSON:
ogr2ogr -f "GeoJSON" output.json input.shp

Convert ESRI Shapefile to geoJSON with Coordinates Conversion (here LAMBERT 1972 (EPSG:31370) to WGS84):
ogr2ogr -f "GeoJSON" -s_srs "EPSG:31370" -t_srs "WGS84" output.json input.shp
'''