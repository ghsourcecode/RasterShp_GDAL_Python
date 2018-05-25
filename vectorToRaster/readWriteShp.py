# -*- coding: cp936 -*-
try:
    from osgeo import gdal
    from osgeo import ogr
    import os
    import osr
except ImportError:
    import gdal
    import ogr
####################################################################################
# �� shp
####################################################################################
def readVectorFile():
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    currentFolder = os.getcwd()
    parentFolder = os.path.dirname(currentFolder)
    strVectorFile = parentFolder + "/testdata/flttoshp.shp"
    print(strVectorFile)

    # ע�����е�����
    ogr.RegisterAll()

    # ������
    dataSource = ogr.Open(strVectorFile, 0)
    if dataSource == None:
        print("���ļ���%s��ʧ�ܣ�", strVectorFile)
        return

    print("���ļ���%s���ɹ���", strVectorFile)

    # ��ȡ������Դ�е�ͼ�������һ��shp����ͼ��ֻ��һ���������mdb��dxf��ͼ��ͻ��ж��
    iLayerCount = dataSource.GetLayerCount()

    # ��ȡ��һ��ͼ��
    oLayer = dataSource.GetLayerByIndex(0)
    if oLayer == None:
        print("��ȡ��%d��ͼ��ʧ�ܣ�\n", 0)
        return

    # ��ͼ����г�ʼ���������ͼ������˹��˲�����ִ������֮ǰ�Ĺ���ȫ�����
    oLayer.ResetReading()

    # ͨ�����Ա��SQL����ͼ���е�Ҫ�ؽ���ɸѡ���ⲿ����ϸ�ο�SQL��ѯ�½�����
    # oLayer.SetAttributeFilter("\"NAME99\"LIKE \"��������Ͻ��\"")

    # ͨ��ָ���ļ��ζ����ͼ���е�Ҫ�ؽ���ɸѡ
    # oLayer.SetSpatialFilter()

    # ͨ��ָ����������Χ��ͼ���е�Ҫ�ؽ���ɸѡ
    # oLayer.SetSpatialFilterRect()

    # ��ȡͼ���е����Ա��ͷ�����
    print("���Ա�ṹ��Ϣ��")
    oDefn = oLayer.GetLayerDefn()
    iFieldCount = oDefn.GetFieldCount()
    for iAttr in range(iFieldCount):
        oField = oDefn.GetFieldDefn(iAttr)
        print("%s: %s(%d.%d)" % ( oField.GetNameRef(), oField.GetFieldTypeName(oField.GetType()), oField.GetWidth(), oField.GetPrecision()))

        # ���ͼ���е�Ҫ�ظ���
    print("Ҫ�ظ��� = %d", oLayer.GetFeatureCount(0))

    oFeature = oLayer.GetNextFeature()
    # ���濪ʼ����ͼ���е�Ҫ��
    while oFeature is not None:
        print("��ǰ�����%d��: \n����ֵ��", oFeature.GetFID())
        # ��ȡҪ���е����Ա�����
        for iField in range(iFieldCount):
            oFieldDefn = oDefn.GetFieldDefn(iField)
            line = " %s (%s) = " % (oFieldDefn.GetNameRef(), ogr.GetFieldTypeName(oFieldDefn.GetType()))

            if oFeature.IsFieldSet(iField):
                line = line + "%s" % (oFeature.GetFieldAsString(iField))
        else:
            line = line + "(null)"

        print(line)

        # ��ȡҪ���еļ�����
        oGeometry = oFeature.GetGeometryRef()

        # Ϊ����ʾ��ֻ���һ��Ҫ����Ϣ
        break

    # �ͷ��ڴ�
    oFeature.Destroy()
    # �ر�����Դ���൱���ļ�ϵͳ�����еĹر��ļ�
    dataSource.Destroy()
    print("���ݼ��رգ�")

####################################################################################
# д shp
####################################################################################
def writeVectorFile():
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    currentFolder = os.getcwd()
    parentFolder = os.path.dirname(currentFolder)
    strVectorFile = parentFolder + "/testdata/TestPolygon.shp"

    # ע�����е�����
    ogr.RegisterAll()

    # �������ݣ������Դ���ESRI��shp�ļ�Ϊ��
    strDriverName = "ESRI Shapefile"
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s ���������ã�\n", strDriverName)
        return

    # ��������Դ
    oDS = oDriver.CreateDataSource(strVectorFile)
    if oDS == None:
        print("�����ļ���%s��ʧ�ܣ�", strVectorFile)
        return

    # ����ͼ�㣬����һ�������ͼ�㣬ָ���ռ�ο����������Ҫ����ͶӰ�����Խ�srs������ΪNone
    srs = osr.SpatialReference();
    srs.ImportFromEPSG(4326)
    papszLCO = []
    oLayer = oDS.CreateLayer("TestPolygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("ͼ�㴴��ʧ�ܣ�\n")
        return

    # ���洴�����Ա�
    # �ȴ���һ����FieldID����������
    oFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)
    oLayer.CreateField(oFieldID, 1)

    # �ٴ���һ����FeatureName���ַ������ԣ��ַ�����Ϊ50
    oFieldName = ogr.FieldDefn("FieldName", ogr.OFTString)
    oFieldName.SetWidth(100)
    oLayer.CreateField(oFieldName, 1)

    #��layer�ж�ȡ��Ӧ��feature���ͣ�������feature
    oDefn = oLayer.GetLayerDefn()

    # # ����������Ҫ��
    # oFeatureTriangle = ogr.Feature(oDefn)
    # oFeatureTriangle.SetField(0, 0)
    # oFeatureTriangle.SetField(1, "������")
    # geomTriangle = ogr.CreateGeometryFromWkt("POLYGON ((0 0,20 0,10 15,0 0))")
    # oFeatureTriangle.SetGeometry(geomTriangle)
    # oLayer.CreateFeature(oFeatureTriangle)
    #
    # # ��������Ҫ��
    # oFeatureRectangle = ogr.Feature(oDefn)
    # oFeatureRectangle.SetField(0, 1)
    # oFeatureRectangle.SetField(1, "����")
    # geomRectangle = ogr.CreateGeometryFromWkt("POLYGON ((30 0,60 0,60 30,30 30,30 0))")
    # oFeatureRectangle.SetGeometry(geomRectangle)
    # oLayer.CreateFeature(oFeatureRectangle)

    oFeaturePentagon = ogr.Feature(oDefn)
    oFeaturePentagon.SetField(0, 0)
    oFeaturePentagon.SetField(1, "������")
    geomTriangle = ogr.CreateGeometryFromWkt("POLYGON ((0 0,20 0,10 15,0 0))")
    oFeaturePentagon.SetGeometry(geomTriangle)
    oLayer.CreateFeature(oFeaturePentagon)
    # ���������Ҫ��
    oFeaturePentagon = ogr.Feature(oDefn)
    oFeaturePentagon.SetField(0, 2)
    oFeaturePentagon.SetField(1, "�����")
    geomPentagon = ogr.CreateGeometryFromWkt("POLYGON ((70 0,85 0,90 15,80 30,65 15,700))")
    oFeaturePentagon.SetGeometry(geomPentagon)
    oLayer.CreateFeature(oFeaturePentagon)

    oDS.Destroy()
    print("���ݼ�������ɣ�\n")

####################################################################################
# ɾ��ʸ��
####################################################################################
def deleteVector(strVectorFile):
    # ע�����е�����
    ogr.RegisterAll()

    # ��ʸ��
    oDS = ogr.Open(strVectorFile, 0)
    if oDS == None:
        return
    oDriver = oDS.GetDriver()

    # ��Ҫ���˴���Ҫ�ر�����Դ��������رգ��ᵼ��ɾ��shpʱ���޷���ȫɾ��shp�ļ�
    oDS.Destroy()

    if oDriver == None:
        os.remove(strVectorFile)
        return
    if oDriver.DeleteDataSource(strVectorFile) == ogr.OGRERR_NONE:
        return
    else:
        os.remove(strVectorFile)

####################################################################################
# ������ʸ��, ������shp, geojson
####################################################################################
def renameVector(strOldFile, strNewFile):
    # ע�����е�����
    ogr.RegisterAll()

    # ��ʸ��
    oDS = ogr.Open(strOldFile, 0)
    if oDS == None:
        return

    oDriver = oDS.GetDriver()

    if oDriver == None:
        return

    oDDS = oDriver.CopyDataSource(oDS, strNewFile, [])
    oDDS.Destroy()
    # ��Ҫ���˴���Ҫ�ر�����Դ��������رգ��ᵼ��ɾ��shpʱ���޷���ȫɾ��shp�ļ�
    oDS.Destroy()

    if oDDS == None:
        os.rename(strOldFile, strNewFile)

    if oDriver.DeleteDataSource(strOldFile) == ogr.OGRERR_NONE:
        return
    else:
        os.rename(strOldFile, strNewFile)

def copyDataSource(fromLocation, toLocation):
    '''
    ����ʸ���ļ�
    :param fromLocation:
    :param toLocation:
    :return:
    '''

    ogr.RegisterAll()

    sourceDatasource = ogr.Open(fromLocation)
    if sourceDatasource == None:
        print('�ļ�������')

    driver = sourceDatasource.GetDriver()
    if driver == None:
        return

    targetDatasource = driver.CopyDataSource(sourceDatasource, toLocation, [])
    sourceDatasource.Destroy()
    targetDatasource.Destroy()

if __name__ == '__main__':
    readVectorFile()
    writeVectorFile()

    currentParentFolder = os.path.dirname(os.getcwd())
    oldShpName = currentParentFolder + '/testdata/TestPolygon.shp'
    newShpName = currentParentFolder + '/testdata/TestPolygonnew.shp'

    # copyDataSource(oldShpName, newShpName)

    renameVector(oldShpName, newShpName)
    deleteVector(newShpName)

