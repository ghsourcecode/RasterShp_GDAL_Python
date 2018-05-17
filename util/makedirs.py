import sys
import os.path
import os
'''
该函数类似java中的 java file mkdirs()
'''
def mkdir(path):
    # 去除首位空格
    path = path.strip()

    if os.path.isabs(path):
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
            return True
    else:
        # 获取当前Py文件所在路径
        currentPath = os.getcwd()
        # 去除尾部 \ 符号
        path = currentPath + '/' + path.rstrip("\\|/")
        os.makedirs(path)


#############################################################
# main 方法
############################################################
if __name__ == '__main__':
    # 定义要创建的目录
    path = 'E:/pythontest/python_gdal_testdata/shp/'
    path = 'testdata/testdir/'
    # 调用函数
    mkdir(path)