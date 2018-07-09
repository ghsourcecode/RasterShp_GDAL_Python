#!/usr/bin/env python
# encoding: utf-8
'''
测试导入瓦片到mongodb 4.0
导入分2种情况：
一是导入gridfs，一种是作为键值对导入
@author: DaiH
@date: 2018/7/2 14:34
'''

import os
import sys
import bson
import bson.binary as bbinary
from pymongo import MongoClient
from gridfs import *

def importMongoDBGridFS():
    '''导入到gridfs'''
    client = MongoClient(host='127.0.0.1', port=27017)  #连接mongodb
    db = client.TiledImgDB                              #连接数据库

    dirPath = 'D:/geowebcache/vectortileworkspace_county'
    datastore = os.path.basename(dirPath)               #如果dirPath以'/'结尾，则datastore为空str
    fs = GridFS(database=db, collection=datastore)
    levels = os.listdir(dirPath)
    for level in levels:
        levelPath = os.path.join(dirPath, level)
        if os.path.isdir(levelPath):
            rows = os.listdir(levelPath)
            for row in rows:
                rowPath = os.path.join(levelPath, row)
                images = os.listdir(rowPath)
                for image in images:
                    imagePath = os.path.join(rowPath, image)
                    col = os.path.basename(imagePath).split('.')[0]
                    imageData = open(imagePath, 'rb')
                    data = imageData.read()
                    args = {'level': level, 'row': row, 'col': col}
                    if not fs.find_one(args):
                        fs.put(data=data, **args)
    print('done gridfs record!')

def importTiledImagesToMongoDBKV():
    '''将瓦片导入mongodb，以单行记录存储'''
    client = MongoClient(host='127.0.0.1', port=27017)
    db = client.TiledImagesKV
    dirPath = 'D:/geowebcache/vectortileworkspace_county'
    datastore = os.path.basename(dirPath)  # 如果dirPath以'/'结尾，则datastore为空str
    collections = db.datastore
    levels = os.listdir(dirPath)
    for level in levels:
        levelPath = os.path.join(dirPath, level)
        if os.path.isdir(levelPath):
            rows = os.listdir(levelPath)
            for row in rows:
                rowPath = os.path.join(levelPath, row)
                images = os.listdir(rowPath)
                for image in images:
                    imagePath = os.path.join(rowPath, image)
                    col = os.path.basename(imagePath).split('.')[0]
                    imageData = open(imagePath, 'rb')
                    data = imageData.read()
                    record = {'level': level, 'row': row, 'col': col}
                    if not collections.find_one(record):
                        record['data'] = data
                        collections.insert(record)
    print('done kv record')




if __name__ == '__main__':
    # importMongoDBGridFS()
    importTiledImagesToMongoDBKV()






