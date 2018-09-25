#!/usr/bin/env python
# encoding: utf-8
'''
读取shp文件，导入mongodb
@author: DaiH
@date: 2018/7/10 16:35
'''

import shapefile
import pymongo
from pymongo import MongoClient


def readSHPPoint(append):
    '''

    :param append: boolean值，是否追加
    :return:
    '''
    fileP = r'E:\Data\temp\idw_points.shp'
    sf = shapefile.Reader(fileP)
    shapeRecs = sf.shapeRecords()

    mongodb_server = '127.0.0.1'
    mongodb_port = 27017
    mongodb_collection = 'supermarket'
    mongodb_db = 'gisdb'
    connection = MongoClient(host=mongodb_server, port=mongodb_port)
    print('Getting database %s' % mongodb_db)
    db = connection[mongodb_db]
    print('Getting the collection %s' % mongodb_collection)
    collection = db[mongodb_collection]
    if append == False:
        print('Removing features from the collection...')
        collection.remove({})
    print('Starting loading features...')

    for shaperec in shapeRecs:
        mongofeat = {}
        # '{x='',y=''}'
        strX = "%.3f" % shaperec.shape.points[0][0]
        strY = "%.3f" % shaperec.shape.points[0][1]
        mongogeom = '{x="' + strX + '",y="' + strY + '"}'
        print(mongogeom)
        mongofeat['geom'] = mongogeom
        # mongofeat['name'] = shaperec.record[1].decode('GB2312').encode('utf-8')
        collection.insert(mongofeat)
    # create 2d index
    collection.create_index([("geom", pymongo.GEO2D)])


if __name__ == "__main__":
    readSHPPoint(False)