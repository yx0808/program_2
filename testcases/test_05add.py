'''
添加项目模块

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
# 导入数据库处理模块
from common.handle_mysql import HandleDB
# 导入tools模块，使用正则方法替换用例中需要替换的参数
from common.tools import replace_data
# 导入封装的前置条件模块中的BaseTest类，用于测试类继承相关类属性
from testcases.fixture import BaseTest


# 在测试类前@ddt
@ddt
# 定义一个提现测试类(TestAdd),继承unittest的TestCase
class TestAdd(unittest.TestCase,BaseTest):
    # 创建操作Excel的对象，传'Excel的完整路径+文件名‘+表单名称
    excel=HandleExcel(os.path.join(DATA_DIR,'apicase.xlsx'),'add')
    # 读取数据，调用excel的read_data方法读取数据
    cases=excel.read_data()
    # 读取配置文件中的base_url
    base_url=conf.get('env','base_url')
    # 设置数据库操作对象db
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
    def test_add(self,item):
        # 第一步：准备数据
        # 1.请求地址
        # self.xxx：可通过实例对象获取类属性（self为实例对象,cls为类本身）
        url=self.base_url+item['url']
        # 2.请求数据
        # ****************************
        # 动态处理需要替换的参数（将用户ID使用#member_id#在用例文件中进行了站位）

        # ①原方法：使用replace进行替换（应为通过item[]提取的字典，提取后为列表形式，所以需要使用replace，该方法两个参数均需为字符串类型，使用str转化）
        # 注意；替换完后需再赋值给原来的参数
        # item['data']=item['data'].replace('#member_id#',str(self.member_id))
                                         #   替换对象   ，   替换进去的值

        # ②高级方法：正则替换
        # 使用tools封装的方法：replace_data(需要替换的数据，用例类)
        item['data']=replace_data(item['data'],TestAdd)
        # 字典格式从excel中读取出来均为列表，需要转化为字典
        params=eval(item['data'])
        # ****************************

        # 3.预期结果
        expected=eval(item['expected'])

        # 4.请求方法
        method=item['method'].lower()

        # 发请求前查询数据库该账户有多少个项目****************************************
        sql='SELECT * FROM future.loan WHERE member_id="{}"'.format(self.member_id)
        start_num=self.db.find_count(sql)
        print('请求前项目数：', start_num)

        # 第二步：发送请求，获取实际返回结果
        # 调用requests方法
        respons=requests.request(method=method,url=url,json=params,headers=self.headers)
        res=respons.json()
        print("预期结果：",expected)
        print("实际结果：",res)
        # 如需回写测试结果，则增加该参数，用于识别用例对应的行
        row = item["case_id"] + 1

        # 发请求后查询数据库该账户有多少个项目*********************************
        sql='SELECT * FROM future.loan WHERE member_id="{}"'.format(self.member_id)
        end_num=self.db.find_count(sql)
        print('请求后项目数：', end_num)

        # 第三步: 断言
        try:
            self.assertEqual(expected['code'],res['code'])
            self.assertEqual(expected['msg'],res['msg'])
            # 若数据执行成功，执行判断，数量差为1
            if res['msg']=='OK':
                self.assertEqual(end_num-start_num,1)
            # 若未创建成功，则判断数量差为0
            else:
                self.assertEqual(end_num-start_num,0)

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
