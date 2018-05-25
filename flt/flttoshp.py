import gdal, ogr
import os
from flt import classify as classifier, flttotif, polygonize
from util import reprojectShp

'''
分级：
0 0.013435 1
0.013435 0.037422 2;0.037422 0.080247 3
0.080247 0.156709 4;0.156709 0.293223 5
0.293223 0.536956 6;0.536956 0.972118 7
0.972118 1.749056 8;1.749056 3.136204 9
3.136204 5.612822 10
'''
classify = [(0, 0, 0.013435),
                (1, 0.013435, 0.037422),
                (2, 0.037422, 0.080247),
                (3, 0.080247, 0.156709),
                (4, 0.156709, 0.293223),
                (5, 0.293223, 0.536956),
                (6, 0.536956, 0.972118),
                (7, 0.972118, 1.749056),
                (8, 1.749056, 3.136204),
                (9, 3.136204, 5.612822)]

def fltToShp(fltPath, fltToTifPath, classify, classifyTifPath, maskTifPath, outShpPath):
    '''
    将flt转为shp
    :param fltPath:         flt路径
    :param fltToTifPath:    转为tif后的路径
    :param classify:      重分类标准
    :param classifyTifPath: 分类后的tif路径
    :param maskTifPath:     蒙版路径，根据flt转换的tif生成，作用：maskTifPath指示的tif图中，像素值为0的部分，不输出shp
    :param outShpPath:      输出的shp路径
    :return:
    '''
    flttotif.fltWithoutPrjToTiff(fltPath, fltToTifPath)
    classifier.produceClassifyTif(fltToTifPath, classify, classifyTifPath)
    classifier.produceMaskTif(fltToTifPath, maskTifPath)

    polygonize.polygonize(classifyTifPath, maskTifPath, outShpPath)

def calcShpArea(fromShpPath, toShpPath):
    '''
    计算shp面积，增加Shape_Area字段，保存EPSG:3857投影后的面积
    :param shpPath:
    :return:
    '''
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shpDataSource = driver.Open(fromShpPath)
    copyDataSource = ogr.GetDriverByName("Memory").CopyDataSource(shpDataSource, "")
    sourceLayer = copyDataSource.GetLayer(0)

    shpDataSource = None
    if os.path.exists(fromShpPath):
        driver.DeleteDataSource(fromShpPath)

    # 增加Shape_Area面积字段
    areaFieldName = 'Shape_Area'
    fieldDef = ogr.FieldDefn(areaFieldName, ogr.OFTReal)
    fieldDef.SetPrecision(2)
    # fieldDef.SetWidth(10)
    sourceLayer.CreateField(fieldDef)
    sourceLayerDef = sourceLayer.GetLayerDefn()
    areaFieldIndex = sourceLayerDef.GetFieldIndex(areaFieldName)

    # 测试计算面积
    for feature in sourceLayer:
        try:
            gridcodefield = feature.GetField('gridcode')
            geomref = feature.GetGeometryRef()
            area = geomref.GetArea()
            # length = geomref.Length()
            feature.SetField(areaFieldIndex, area)
            sourceLayer.SetFeature(feature)
        except Exception as e:
            print("异常的类型是:%s"%type(e))
            print("异常对象的内容是:%s"%e)
    # 将内存中的datasource复制到磁盘
    pt_cp = driver.CopyDataSource(copyDataSource, toShpPath)
    pt_cp.Release()

def fltWithoutPrjToShpTest(fltpath, shppath):
    fltToTifpath = '../testdata/out/flttotif.tif'
    classifyTifPath = '../testdata/out/classified.tif'
    maskTifPath = '../testdata/out/mask.tif'

    flttotif.fltWithoutPrjToTiff(fltpath, fltToTifpath)
    classifier.produceClassifyTif(fltToTifpath, classify, classifyTifPath)
    classifier.produceMaskTif(fltToTifpath, maskTifPath)

    polygonize.polygonize(classifyTifPath, maskTifPath, shppath)

    # 复制一份输出的shp图，并删除原来的，对复制后数据进行投影，输出到复制前的shp图
    copyShpPath = shppath[ : shppath.rfind('.')] + '_copy.' + shppath[shppath.rfind('.') + 1 : ]
    copyShpRePrjPath = shppath[ : shppath.rfind('.')] + '_copy_reproject.' + shppath[shppath.rfind('.') + 1 : ]
    driver = ogr.GetDriverByName('ESRI Shapefile')
    outShpDatasource = driver.Open(shppath)
    ptsr = driver.CopyDataSource(outShpDatasource, copyShpPath)
    ptsr.Release()
    outShpDatasource = None # 释放打开的shp资源
    if os.access(shppath, os.F_OK):
        driver.DeleteDataSource(shppath)
    reprojectShp.reproject(copyShpPath, 3857, copyShpRePrjPath)

if __name__ == '__main__':
    fltpath = '../testdata/rain_2016.flt'
    fltshppath = '../testdata/out/flttoshp.shp'

    fltWithoutPrjToShpTest(fltpath, fltshppath)
    calcShpArea(fltshppath)