########################################################################
# 将 tif 图分级
########################################################################
import gdal
import gdalnumeric
import numpy

def writeTiff(data, width, height, bands, geotransform, proj, noDataValue, outPath):
    if 'int8' in data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(data.shape) == 3:
        bands, height, width = data.shape
    elif len(data.shape) == 2:
        data = numpy.array([data])
    else:
        bands, (height, width) = 1, data.shape
    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(outPath, width, height, bands, datatype)
    dataset.GetRasterBand(1).SetNoDataValue(noDataValue)
    if (dataset != None):
        dataset.SetGeoTransform(geotransform)  # 写入仿射变换参数
        dataset.SetProjection(proj)  # 写入投影
    for i in range(bands):
        dataset.GetRasterBand(i + 1).WriteArray(data[i])
    del dataset

def produceClassifyTif(srcTifPath, outClassifyTifPath, grade):
    class_defs = [(0, 0, 0.013435),
                  (1, 0.013435, 0.037422),
                  (2, 0.037422, 0.080247),
                  (3, 0.080247, 0.156709),
                  (4, 0.156709, 0.293223),
                  (5, 0.293223, 0.536956),
                  (6, 0.536956, 0.972118),
                  (7, 0.972118, 1.749056),
                  (8, 1.749056, 3.136204),
                  (9, 3.136204, 5.612822)]

    dataset = gdal.Open(srcTifPath)
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    bands = dataset.RasterCount
    data = dataset.ReadAsArray(0, 0, width, height)
    geotransform = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    band = dataset.GetRasterBand(1)
    noDataValue = band.GetNoDataValue()

    src_image = gdalnumeric.LoadFile(srcTifPath)

    dst_image = numpy.zeros((height, width))

    for class_info in class_defs:
        class_id = class_info[0]
        class_start = class_info[1]
        class_end = class_info[2]

        class_value = numpy.ones((height, width)) * class_id

        mask = numpy.bitwise_and(
            numpy.greater_equal(src_image, class_start),
            numpy.less_equal(src_image, class_end))

        dst_image = numpy.choose(mask, (dst_image, class_value))

    writeTiff(dst_image, width, height, bands, geotransform, proj, noDataValue, outClassifyTifPath)

################################################################################
# 生成用于分类图像的蒙板，蒙板值为 0 的地方，不参与分类，值大于 0 的地方，参与分类，
# 需要与 produceClassifyTif 函数一起使用
################################################################################
def produceMaskTif(srcTifPath, maskTifPath):
    dataset = gdal.Open(srcTifPath)
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    bands = dataset.RasterCount
    srcArray = dataset.ReadAsArray(0, 0, width, height)
    geotransform = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    band = dataset.GetRasterBand(1)
    noDataValue = band.GetNoDataValue()

    src_image = gdalnumeric.LoadFile(srcTifPath)

    mask_image = numpy.zeros((height, width))
    for i in range(0, height):
        for j in range(0, width):
            if not srcArray[i][j] - noDataValue <= 1e-9:
                mask_image[i][j] = 1

    writeTiff(mask_image, width, height, bands, geotransform, proj, noDataValue, maskTifPath)

if __name__ == '__main__':
    tifpath = '../testdata/out/flttotif.tif'
    outCalssifyTifPath = '../testdata/out/classify.tif'
    classifyArray = produceClassifyTif(tifpath, outCalssifyTifPath, None)
