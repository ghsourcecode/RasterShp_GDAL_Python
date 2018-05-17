from flt import classify, flttotif, polygonize

'''
分级：
0 0.013435 1
0.013435 0.037422 2;0.037422 0.080247 3
0.080247 0.156709 4;0.156709 0.293223 5
0.293223 0.536956 6;0.536956 0.972118 7
0.972118 1.749056 8;1.749056 3.136204 9
3.136204 5.612822 10
'''

def fltWithoutPrjToShp(fltpath, shppath):
    fltToTifpath = '../testdata/out/flttotif.tif'
    classifyTifPath = '../testdata/out/classified.tif'
    maskTifPath = '../testdata/out/mask.tif'

    flttotif.fltWithoutPrjToTiff(fltpath, fltToTifpath)
    classify.produceClassifyTif(fltToTifpath, classifyTifPath, None)
    classify.produceMaskTif(fltToTifpath, maskTifPath)

    polygonize.polygonize(classifyTifPath, maskTifPath, shppath)


if __name__ == '__main__':
    fltpath = '../testdata/rain_2016.flt'
    fltshppath = '../testdata/out/flttoshp.shp'
    fltWithoutPrjToShp(fltpath, fltshppath)