# 该模块测试审核功接口：管理员审核
#     前置条件：
#           1.管理员登录（登录一次即可，类级别的前置条件）
#           2.创建一个项目（执行每条用例前都需要一个新的项目，所以需要用例级别的前置）
#           3.若普通用户登录、创建项目（反向用例）
#             此时使用类级别前置登录普通用户，使用用例级别前置创建项目
#
#
import os.path
import unittest
import requests

from jsonpath import jsonpath
from unittestreport import ddt,list_data
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.tools import replace_data
from common.handle_log import my_log
from common.handle_mysql import HandleDB
# 导入封装的前置条件模块中的BaseTest类，用于测试类继承相关类属性
from testcases.fixture import BaseTest

@ddt
# 定义测试类
class TestAudit(unittest.TestCase,BaseTest):
    excel=HandleExcel(os.path.join(DATA_DIR,'apicase.xlsx'),'audit')
    case=excel.read_data()
    db=HandleDB()

    # 定义前置条件
    @classmethod
    # 定义类级别前置（登录）
    def setUpClass(cls) -> None:
        # ------------管理员登录------------
        cls.admin_login()
        # -----------普通用户登录-----------
        cls.user_login()

    # 定义用例级别前置方法（新建项目）
    def setUp(self) -> None:
        # 实例对象可以调用类方法（所以用例级别前置方法可直接调用类方法）
        self.add_project()


    @list_data(case)
    def test_audit(self,item):
        # print('执行当前用例,类属性中的项目ID：',self.loan_id)
        # 第一步：准备数据
        url=conf.get('env','base_url')+item['url']
        item['data']=replace_data(item['data'],TestAudit)
        params=eval(item['data'])
        method=item['method']
        expected=eval(item['expected'])
        # 第二步：请求接口
        # 此时请求头应为管理员账号的，审核只能管理员进行
        response=requests.request(method=method,url=url,json=params,headers=self.admin_headers)
        res=response.json()
        print("预期结果：", expected)
        print("实际结果：", res)
        row = item["case_id"] + 1
        # 判断用例是否是审核通过的用例，且审核成功，如果是则保存项目id为审核通过的项目id
        if res['msg'] == 'OK' and params['approved_or_not'] == 'true':
            TestAudit.pass_loan_id=self.loan_id

        # 第三步：断言
        try:
            self.assertEqual(expected['code'],res['code'])
            self.assertEqual(expected['msg'],res['msg'])
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

