'''
充值前提：登录-->获取token
unittest:
        用例级别的前置：setUp（每个类前都执行）
        测试类级别的前置setUpClass(所有类前执行一次)
           1.提取token，保存为类属性
           2.提取用户id，保存为类属性

        充值测试方法：
           1.动态替换参数中的用户ID（replace中使用的参数必须为syr类型）
'''

import unittest
# os模块，用于路径拼接
import os
# 导入requests模块用于发送请求
import requests

from unittestreport import ddt,list_data
# 导入封装的处理Excel模块中用于处理Excel的类HandleExcel
from common.handle_excel import HandleExcel
# 导入路径处理模块中,测试数据的绝对路径
from common.handle_path import DATA_DIR
# 读取配置文件，导入配置文件解析器
from common.handle_conf import conf
# 导入json提取工具，用于提取token
from jsonpath import jsonpath
# 导入处理日志的模块，导入处理对象my_log
from common.handle_log import my_log
# 导入数据库操作模块，用于校验充值金额变化
from common.handle_mysql import HandleDB
# 导入tools模块，使用正则方法替换用例中需要替换的参数
from common.tools import replace_data
# 导入封装的前置条件模块中的BaseTest类，用于测试类继承相关类属性
from testcases.fixture import BaseTest
from common.handle_sign import HandleSign


# 在测试类前@ddt
@ddt
# 定义一个充值测试类(TestRecharge),继承unittest的TestCase以及BaseTest
class TestRecharge(unittest.TestCase,BaseTest):
    # 创建操作Excel的对象，传'Excel的完整路径+文件名‘+表单名称
    excel=HandleExcel(os.path.join(DATA_DIR,'apicase.xlsx'),'recharge')
    # 读取数据，调用excel的read_data方法读取数据
    cases=excel.read_data()
    # 读取配置文件中的base_url
    base_url=conf.get('env','base_url')
    # 创建数据库操作对象
    db=HandleDB()

    # 定义类方法，放前置条件；定义时需@classmethod
    # cls代表类本身
    @classmethod
    def setUpClass(cls):
        '''用例类的前置方法：登录获取token'''
        cls.user_login()


    # 定义实例测试方法，测试方法前@list_data()，括号内放测试数据
    @list_data(cases)
    # self代表实例本身
    def test_recharge(self,item):
        # 第一步：准备数据
        # 1.请求地址
        # self.xxx：可通过实例对象获取类属性（self为实例对象,cls为类本身）
        url=self.base_url+item['url']

        # 2.请求数据
        # ****************************
        # 动态处理需要替换的参数（将用户ID使用#member_id#在用例文件中进行了站位）

        # 1.原方法：使用replace进行替换（应为通过item[]提取的字典，提取后为列表形式，所以需要使用replace，该方法两个参数均需为字符串类型，使用str转化）
        # 注意；替换完后需再赋值给原来的参数
        # item['data']=item['data'].replace('#member_id#',str(self.member_id))
                                         #   替换对象   ，   替换进去的值

        # 2.高级方法：使用正则替换replace_data(需要替换的数据，用例类)
        item['data']=replace_data(item['data'],TestRecharge)
        # 字典格式从excel中读取出来均为列表，需要转化为字典
        params=eval(item['data'])

        # 加密算法：请求头使用lemonban.v3时：
        # from common.handle_sign import HandleSign        # 开始部分：导入封装的加密算法模块
        # token=self.token
        # par_sign=HandleSign.generate_sign(token)    # 使用HandleSign中封装的generate_sign方法
        # print('token:',self.token)
        #                                 # self.token：token在user_login已保存为类属性，实例对象可通过self调用
        # params.update(par_sign)# 将par_sign加入到参数params中（字典添加，调用update方法）

        # ****************************

        # 3.预期结果
        expected=eval(item['expected'])

        # 4.请求方法
        method=item['method'].lower()

        # ******请求接口前查询用户余额（用于校验数据库中数值变化）******
        sql='SELECT leave_amount FROM future.member WHERE  mobile_phone="{}"'.format(conf.get('test_data','mobile'))
        # 类属性db通过self调用，使用创建的find_one方法执行SQL(执行后为元组类型，通过索引取值为INT)
        start_amount=self.db.find_one(sql)[0]
        print('用例执行前，用户余额：',start_amount)

        # 第二步：发送请求，获取实际返回结果
        # 调用requests方法
        respons=requests.request(method=method,url=url,json=params,headers=self.headers)   # self.headers：headers在user_login已保存为类属性，实例对象可通过self调用
        res=respons.json()
        print("预期结果：",expected)
        print("实际结果：",res)
        # 如需回写测试结果，则增加该参数，用于识别用例对应的行
        row = item["case_id"] + 1

        # ******请求接口后查询用户余额（用于校验数据库中数值变化）*******
        # 执行sql（执行find_one后为元组类型，通过索引取值为INT）
        end_amount=self.db.find_one(sql)[0]
        print('用例执行后，用户余额：', end_amount)

        # 第三步: 断言
        try:
            self.assertEqual(expected['code'],res['code']),
            self.assertEqual(expected['msg'],res['msg'])
            # ******校验数据库中用户余额的变化是否等于充值金额******
            # 1.因用例涉及小数，所以需要使用float将计算结果转化为浮点类型
            # 2.充值失败的应该校验差值为0，否则用例执行失败
            if res['msg'] == 'OK':
                # 充值成功，变化为充值金额
                self.assertEqual(float(end_amount - start_amount), float(params['amount']))
            else:
                # 充值失败，变化0
                self.assertEqual(float(end_amount - start_amount), float(0))

        # 如果断言失败，捕获异常并抛出异常
        except AssertionError as e:
            my_log.error('用例--【{}】--执行失败'.format(item['title']))
            # 显示失败原因
            my_log.exception(e)
            # 回写测试结果到表格
            self.excel.write_data(row=row, column=8, value='失败')
            # 抛出异常
            raise e
        else:
            my_log.info('用例--【{}】--执行通过'.format(item['title']))
            # 回写结果到excel（不太建议，比较耗时）
            self.excel.write_data(row=row, column=8, value='通过')
