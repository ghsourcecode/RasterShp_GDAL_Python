'''
调用 gdal 自带脚本，将 shp 文件转为 geojson
'''

import os
def exportShpToGeoJson(shpPath, outGeoJsonPath):
    currentParentFolderPath = os.path.dirname(os.getcwd())
    ogr2ogrPath = currentParentFolderPath + '/gdal223/ogr2ogr.py'

    os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" ' + outGeoJsonPath + ' ' + shpPath)
    # 输出投影转换后的geojson
    # os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" -a_srs epsg:3857 -t_srs epsg:3857 ' + outGeoJsonPath + ' ' + shpPath)

if __name__ == '__main__':
    shpPath = r'E:\PycharmProject\gdalpython2\testdata\flttoshp.shp'
    outGeoJsonPath = r'E:\PycharmProject\gdalpython2\testdata\out\shpToGeoJson.json'
    exportShpToGeoJson(shpPath, outGeoJsonPath)