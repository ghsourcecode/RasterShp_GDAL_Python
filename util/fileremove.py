#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/18 9:07
删除文件和文件夹操作
'''

import os
import shutil



def removeFile(filePath):
    '''
    删除指定文件，如果文件是文件，则直接删除，如果是文件夹，则递归删除
    :param filePath:
    :return:
    '''
    if os.path.isfile(filePath):  # 路径是文件
        os.remove(filePath)
    elif os.path.isdir(filePath):
        files = os.listdir(filePath)
        for tempFilePath in files:
            tempFilePath = os.path.join(filePath, tempFilePath)
            removeFile(tempFilePath)


def removeFolder(folderPath):
    '''
    删除文件夹，分2种情况：
    1、文件夹不为空：
    不为空时，用shutil.rmtree(path)
    2、文件夹为空：
    os.rmdir(path)
    :param folderPath:
    :return:
    '''
    files = os.listdir(folderPath)
    if files == None:
        os.rmdir(folderPath)
    else:
        shutil.rmtree(folderPath)


if __name__ == '__main__':
    currentPyParent = os.path.dirname(os.getcwd());
