'''
os.getcwd() 脚本执行目录
sys.path[0] 当前执行脚本所在目录
__file__ 按相对路径执行脚本时，会得到相对路径，以绝对路径执行，得到脚本绝对路径
sys.argv[0]  按相对路径执行脚本时，会得到相对路径，以绝对路径执行，得到脚本绝对路径
'''

import os,sys

if __name__=="__main__":

    print("1：__file__=%s" % __file__)

    print("2：os.path.realpath(__file__)=%s" % os.path.realpath(__file__))

    print("3：os.path.dirname(os.path.realpath(__file__))=%s" % os.path.dirname(os.path.realpath(__file__)))

    print("4：os.path.split(os.path.realpath(__file__))=%s" % os.path.split(os.path.realpath(__file__))[0])

    print("5：os.path.abspath(__file__)=%s" % os.path.abspath(__file__))

    print("6：os.getcwd()=%s" % os.getcwd())

    print("7：sys.path[0]=%s" % sys.path[0])

    print("9：sys.argv[0]=%s" % sys.argv[0])

    # 以下2句，若按相对路径执行，得到的是相对路径，若按绝对路径执行，得到的是绝对路径
    print('10：' + sys.argv[0])
    print('11：' + __file__)
    # 以下4句能够确保得到的是绝对路径
    print('12：' + os.path.abspath(sys.argv[0]))
    print('13：' + os.path.realpath(sys.argv[0]))
    print('14：' + os.path.abspath(__file__))
    print('15：' + os.path.realpath(__file__))

