from flt import classify as classifier, flttotif, polygonize

'''
分级：
0 0.013435 1
0.013435 0.037422 2;0.037422 0.080247 3
0.080247 0.156709 4;0.156709 0.293223 5
0.293223 0.536956 6;0.536956 0.972118 7
0.972118 1.749056 8;1.749056 3.136204 9
3.136204 5.612822 10
'''

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

def fltWithoutPrjToShpTest(fltpath, shppath):
    fltToTifpath = '../testdata/out/flttotif.tif'
    classifyTifPath = '../testdata/out/classified.tif'
    maskTifPath = '../testdata/out/mask.tif'

    flttotif.fltWithoutPrjToTiff(fltpath, fltToTifpath)
    classifier.produceClassifyTif(fltToTifpath, classifyTifPath, None)
    classifier.produceMaskTif(fltToTifpath, maskTifPath)

    polygonize.polygonize(classifyTifPath, maskTifPath, shppath)


if __name__ == '__main__':
    fltpath = '../testdata/rain_2016.flt'
    fltshppath = '../testdata/out/flttoshp.shp'
    fltWithoutPrjToShpTest(fltpath, fltshppath)