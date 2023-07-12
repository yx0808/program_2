# 此为程序的入口函数

import unittest
# 导入生成时间的函数
from time import strftime
from unittestreport import TestRunner


# 配置路径模块，导入用例加载路径、报告生成路径
from common.handle_path import CASES_DIR,REPORT_DIR

# 导入发送邮件功能模块SendEmail（自定义邮件名称）
from unittestreport.core.resultPush import SendEmail


# 对run进行封装
# 定义方法
def main():
    suite=unittest.defaultTestLoader.discover(CASES_DIR)
                                             # 用例路径
    # filename写在runer=TestRunner()外是为了写邮件时方便调用filename，若文件名称固定不变则可写死
    filename='py{}.html'.format(strftime("%Y%m%d-%H%M%S"))

    runer=TestRunner(suite,
                     filename=filename,
                     # 报告文件名称（在pycharm列表中显示，不可有中文）
                     report_dir=REPORT_DIR,
                     # 报告生成路径
                     title='二期多模块-测试报告',
                     # 报告标题
                     tester='史沂鑫',
                     # 测试人员
                     desc='此为柠檬班投资测试的测试报告',
                     # 报告描述信息
                     templates=1
                     # 测试报告版式
                     )

    runer.run()

    # em=SendEmail(host='smtp.qq.com',
    #               port=465,
    #               user='634625692@qq.com',
    #               password='eslnowyoikfqbedg')
    # em.send_email(subject='测试报告',
    #               content='请查收',
    #               filename=r'D:\Pycharm_Program\Template_Files\program\program_2\reports\{}'.format(filename),
    #               to_addrs=['shiyixin009@163.com','634625692@qq.com'])


    # # ------------------------将测试结果发送邮箱----------------------------------------
    # runer.send_email(host='smtp.qq.com',
    #                  port=465,
    #                  user='634625692@qq.com',
    #                  password='eslnowyoikfqbedg',
    #                  to_addrs=['shiyixin009@163.com','634625692@qq.com'],
    #                  is_file=True)
     # 参数说明：
     # host：str类型（smtp服务器地址）（不同邮箱不一样,如：smtp.qq.com/smtp.163.com）
     # port：str类型（smtp服务器地址端口）（qq的端口是465）
     # user：str类型（邮箱账号）
     # password: str类型（此处填授权码）
     # to_adders：str（单个收件人） or list（多收件人列表）


# 调用：
#     main（）
if __name__ == '__main__':
    main()
