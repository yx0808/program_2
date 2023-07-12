# 投资接口测试模块
# 前置操作：
#        1.普通用户登录（类级别）
#        2.管理员登录（类级别）
#        3.添加项目（类级别）
#        4.审核项目（类级别）
#
# 数据校验：
#     用户表：用户的余额投资前后会变化（投前金额-投后金额=投资金额）
#     流水记录表：投资成功会新增一条流水记录（投后用户流水记录数量-投前=1）
#     投资表：投资成功会新增一条投资记录（投后用户的记录数量-投前=1）
#
# 扩展：投资满标后（可投为0），会生成回款计划（投后查询回款计划表）
#     1.先查询该项目的投资记录中，所有投资者的id
#     2.根据每个ID查是否生成回款计划表
#
import unittest
import os
import requests

from unittestreport import ddt,list_data
from common.handle_excel import HandleExcel
from common.handle_log import my_log
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from jsonpath import jsonpath
# 导入封装的前置条件模块中的BaseTest类，用于测试类继承相关类属性
from testcases.fixture import BaseTest
from common.tools import replace_data
from common.handle_mysql import HandleDB


@ddt
# 定义测试类(继承TestCase和BaseTest)
class TestInvest(unittest.TestCase,BaseTest):
    # 读取表单
    excel=HandleExcel(os.path.join(DATA_DIR,'apicase.xlsx'),'invest')
    # 读取数据
    cases=excel.read_data()
    # 连接数据库
    db=HandleDB()

    # 用例前置
    @classmethod

    # 类级别前置
    def setUpClass(cls) -> None:
        # 1、管理员登录
        cls.admin_login()
        # 2、普通用户登录
        cls.user_login()
        # 3、添加项目
        cls.add_project()
        # 4、审核项目
        cls.audit()

    # 如需定义用例级别前置，则定义setUp(self)并调用BaseTest中的参数即可
    # 注意：此时应使用self调用

    @list_data(cases)
    # 定义用例方法
    def test_invest(self,item):
        # 一、准备用例数据
        url=conf.get('env','base_url')+item['url']
        item['data']=replace_data(item['data'],TestInvest)
        params=eval(item['data'])
        expected=eval(item['expected'])
        method=item['method']

        # --------投资前查询：判断是否就要校验数据库-------
        # 1.查用户表，用户余额（此表的id即用户ID）
        sql1 = 'SELECT leave_amount FROM future.member WHERE id="{}"'.format(self.member_id)
        # 2.查投资记录表中该用户的投资记录(查询数据条数)
        sql2 = 'SELECT id FROM future.invest WHERE member_id="{}"'.format(self.member_id)
        # financlog:资金流水记录表  py_member_id:支付用户的ID
        # 3.查询支付用户流水数据条数
        sql3 = 'SELECT * FROM future.financelog WHERE  pay_member_id="{}"'.format(self.member_id)

        if item['check_sql']:
            s_amount=self.db.find_one(sql1)[0]
            s_invest=self.db.find_count(sql2)
            s_financelog=self.db.find_count(sql3)

        # 二、发送请求
        respons=requests.request(method=method,url=url,json=params,headers=self.headers)
        res=respons.json()
        print("预期结果：", expected)
        print("实际结果：", res)
        row = item["case_id"] + 1

        # ------投资后查询数据库--------
        if item['check_sql']:
            l_amount=self.db.find_one(sql1)[0]
            l_invest=self.db.find_count(sql2)
            l_financelog=self.db.find_count(sql3)


        # 三、断言
        # 在用例中用户余额控制可通过执行sql语句修改数据库中的数据实现
        try:
            self.assertEqual(expected['code'],res['code'])
            # 成员断言，断言预期结果是否包含在实际结果中
            # （因为实际返回中会返回余额数，但仅需验证有“该标可投金额不足”即可）
            self.assertIn(expected['msg'],res['msg'])
            # 数据库校验结果断言
            if item['check_sql']:
                # 断言用户余额(预期，实际)
                self.assertEqual(float(params['amount']), float(s_amount-l_amount))
                # 断言投资记录
                self.assertEqual(1, float(l_invest-s_invest))
                # 断言流水记录
                self.assertEqual(1, float(l_financelog - s_financelog))

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