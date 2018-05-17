'''
调用 gdal 自带脚本，将 shp 文件转为 geojson
'''

import os
os.system('python E:/PycharmProject/gdalpython2/gdal223/ogr2ogr.py -f "GeoJSON" E:/PycharmProject/gdalpython2/testdata/out/outputGeoJson.json E:/PycharmProject/gdalpython2/testdata/out/flttoshp.shp')