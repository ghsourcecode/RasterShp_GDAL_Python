##################################################################################
# 输出为 shp 数据
##################################################################################
from osgeo import gdal, ogr, osr
import sys

def Usage():
    print("""
gdal_polygonize [-8] [-nomask] [-mask filename] raster_file [-b band]
                [-q] [-f ogr_format] out_file [layer] [fieldname]
""")

'''
tifPath: 要转为矢量的分级后的 tif 路径
maskPath: 用于矢量时的蒙板 tif 路径，可取值为： default, none, maskTifPath
outShpPath: 输出的 shp 路径
'''
def polygonize(tifPath, maskPath, outShpPath):
    if tifPath is None or outShpPath is None:
        Usage()
    format = 'ESRI Shapefile'   #该类型需要查找gdal可输出的矢量类型api
    options = ['8CONNECTED=8']
    quiet_flag = 0
    src_filename = tifPath
    src_band_n = 1

    dst_filename = outShpPath
    dst_layername = 'out'
    dst_fieldname = 'gridcode'
    dst_field = -1

    mask = 'default'

    gdal.AllRegister()

    # =============================================================================
    # 	Verify we have next gen bindings with the polygonize method.
    # =============================================================================
    try:
        gdal.Polygonize
    except:
        print('')
        print('gdal.Polygonize() not available.  You are likely using "old gen"')
        print('bindings or an older version of the next gen bindings.')
        print('')
        sys.exit(1)

    # =============================================================================
    #	Open source file
    # =============================================================================

    src_ds = gdal.Open(src_filename)

    if src_ds is None:
        print('Unable to open %s' % src_filename)
        sys.exit(1)

    srcband = src_ds.GetRasterBand(src_band_n)

    if maskPath is 'default':
        maskband = srcband.GetMaskBand()
    elif maskPath is 'none' or maskPath is None:
        maskband = None
    else:
        mask_ds = gdal.Open(maskPath)
        maskband = mask_ds.GetRasterBand(1)

    # =============================================================================
    #       Try opening the destination file as an existing file.
    # =============================================================================

    try:
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        dst_ds = ogr.Open(dst_filename, update=1)
        gdal.PopErrorHandler()
    except:
        dst_ds = None

    # =============================================================================
    # 	Create output file.
    # =============================================================================
    if dst_ds is None:
        drv = ogr.GetDriverByName(format)
        if not quiet_flag:
            print('Creating output %s of format %s.' % (dst_filename, format))
        dst_ds = drv.CreateDataSource(dst_filename)
    else:
        layerCount = dst_ds.GetLayerCount ()
        for index in range(0, layerCount):
            dst_ds.DeleteLayer(index)

    # =============================================================================
    #       Find or create destination layer.
    # =============================================================================
    try:
        dst_layer = dst_ds.GetLayerByName(dst_layername)
    except:
        dst_layer = None

    if dst_layer is None:

        srs = None
        if src_ds.GetProjectionRef() != '':
            srs = osr.SpatialReference()
            srs.ImportFromWkt(src_ds.GetProjectionRef())

        dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)

        if dst_fieldname is None:
            dst_fieldname = 'DN'

        fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
        dst_layer.CreateField(fd)
        dst_field = 0

    # =============================================================================
    #	Invoke algorithm.
    # =============================================================================

    if quiet_flag:
        prog_func = None
    else:
        prog_func = gdal.TermProgress

    result = gdal.Polygonize(srcband, maskband, dst_layer, dst_field, options, callback=prog_func)

    srcband = None
    src_ds = None
    dst_ds = None
    mask_ds = None

if __name__ == '__main__':
    classifyTifPath = '../testdata/out/classified.tif'
    maskTifPath = '../testdata/out/mask.tif'
    outshpPath = '../testdata/out/testout.shp'
    polygonize(classifyTifPath, None, outshpPath)