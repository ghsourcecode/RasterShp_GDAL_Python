#!/usr/bin/env python
# encoding: utf-8
'''
@author: DaiH
@date: 2018/5/23 10:56
'''

import os


if __name__ == '__main__':
    source = 'abceddfsadef'
    lia = source.find('a')
    ria = source.rfind('a')
    lif = source.find('f')
    rif = source.rfind('f')
    print('lia:' + str(lia) + '; ' + 'ria:' + str(ria) + '; ' + 'lif:' +str(lif) + '; ' + 'rif:' + str(rif))

    print(source[lia:ria])

    root = os.getcwd()
    folder = '/../testdata/testexist/dkw.tif'
    path = root + folder
    path = path.replace('\\', '/')
    path = path[0 : path.rfind('/')]
    if not os.path.exists(path):
        os.makedirs(path)
