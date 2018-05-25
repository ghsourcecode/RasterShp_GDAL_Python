#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/18 16:12
'''

import ast
import numpy

if __name__ == '__main__':
    strTwoArray = '[(1, 2, 3),(21,22,34)]'

    strToList = ast.literal_eval(strTwoArray)  # 转为list
    listtoarray = numpy.array(strToList)    # list 转为 array
    print(type(listtoarray))
    print(listtoarray[0])
    print(listtoarray[0][0])

    strOneArray = '[1, 2, 3]'
    tolist = ast.literal_eval(strOneArray)
    toarray = numpy.array(tolist)
    print(type(toarray))
    print(toarray[0])

