'''
调用 gdal 自带脚本，将 shp 文件转为 geojson
'''

import os
from gdal import ogr

def exportShpToGeoJson(sourceShpPath, outGeoJsonPath):
    '''
    将shp转换为geojson，参数要用绝对路径
    :param sourceShpPath:
    :param outGeoJsonPath:
    :return:
    '''
    currentParentFolderPath = os.path.dirname(os.getcwd())
    ogr2ogrPath = currentParentFolderPath + '/gdal223/ogr2ogr.py'

    os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" ' + outGeoJsonPath + ' ' + sourceShpPath)
    # 输出投影转换后的geojson
    # os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" -a_srs epsg:3857 -t_srs epsg:3857 ' + outGeoJsonPath + ' ' + shpPath)

def exportShpToGeoJson(ogr2ogrPath, sourceShpPath, outGeoJsonPath):
    '''
    将shp转换为geojson，参数要用绝对路径
    :param org2ogrPath:
    :param sourceShpPath:
    :param outGeoJsonPath:
    :return:
    '''
    os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" ' + outGeoJsonPath + ' ' + sourceShpPath)
    # 输出投影转换后的geojson
    # os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" -a_srs epsg:3857 -t_srs epsg:3857 ' + outGeoJsonPath + ' ' + shpPath)

def exportShpToGeoJson(ogr2ogrPath, sourceShpPath, outGeoJsonPath, clipShpPath=None):
    '''
    daih 2018-6-22
    将shp转换为geojson，并用clipShpPath指定的shp裁切sourceShpPath后再输出转换结果(参数要用绝对路径)
    :param org2ogrPath:
    :param sourceShpPath:
    :param outGeoJsonPath:
    :return:
    '''
    if clipShpPath is not None:
        os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" ' + outGeoJsonPath + ' ' + sourceShpPath + ' -clipsrc ' + clipShpPath)
    else:
        os.system('python' + ' ' + ogr2ogrPath + ' -f "GeoJSON" ' + outGeoJsonPath + ' ' + sourceShpPath)

if __name__ == '__main__':
    shpPath = r'E:\PycharmProject\gdalpython2\testdata\flttoshp.shp'
    outGeoJsonPath = r'E:\PycharmProject\gdalpython2\testdata\out\shpToGeoJson.json'
    exportShpToGeoJson(shpPath, outGeoJsonPath)