# 注册模块用例
'''
优化方法：
    生成随机手机号并回写用例表
'''
# 导入os模块(官方库)，用于拼接路径
import os
# 导入unittest模块(官方库)
import unittest
# 导入请求接口模块
import requests
# 导入随机数模块(用于注册手机号随机生成)
import random
# 导入ddt、list_data
from unittestreport import ddt,list_data
# 导入处理表格的模块，需要操作表格的功能
from common.handle_excel import HandleExcel
# 导入处理路径的模块,需要数据路径DATA_DIR
from common.handle_path import DATA_DIR
# 导入处理配置文件模块，需要通过conf(配置文件解析器)读取配置文件
from common.handle_conf import conf
# 导入日志模块，需要输出日志
from common.handle_log import my_log
# 导入数据库操作模块
from common.handle_mysql import HandleDB


# 在测试类前@ddt
@ddt
# 定义一个注册测试类(TestRegister),继承unittest的TestCase
class TestRegister(unittest.TestCase):
    # 创建一个操作excel的对象（excel），用于传输用例文件路径（绝对路径）、表单名称
    excel=HandleExcel(os.path.join(DATA_DIR,'apicase.xlsx'),"register")
    # 读取excel用例数据(调用raed_data方法)
    cases=excel.read_data()
    # （第一步：1.）使用所写handle_conf模块中的conf读取配置文件中的接口地址
    base_url=conf.get('env','base_url')
    # （第一步：3.）从配置文件获取请求头，但读取后为列表，需要转化为字典
    headers=eval(conf.get('env','headers'))
    # 创建操作数据库的对象db
    db=HandleDB()

    # 定义方法，使注册手机号能随机生成
    def random_mobile(self):
        # 生成区间内的整数型随机数(生成的为int类型)，并转换为字符串(替换时只能用str类型)
        phone=str(random.randint(13300000000,13399999999))
        return phone
        # 或：
        # mobile='133'
        # for i in range(8):  //生成8位
        #     n=str(random.randint(0,9))
        #     mobile += n


    # 在方法前@list_data(),括号内放用例数据
    @list_data(cases)
    # 定义一个用例方法(test_register)来写用例执行逻辑,定义item用于接收用例数据cases
    def test_register(self,item):
        # 第一步：准备用例数据
        # 1.接口地址
        # (在此处读取base_url会读取13次，放入类属性中读取一次即可)
        # 在实例方法中使用self调用类属性,并接入Excel中的具体接口
        url=self.base_url+item['url']

        # 2.接口请求参数
        # 加判断，有需要生成随机字符串时再生成，无需重复生成
        if '#mobile#' in item['data']:
            # 调用上面封装的random_mobile()方法，随机生成手机号
            phone=self.random_mobile()
            # 将apicase文件中需要变化的电话号写为#mobile#，并替换
            item['data']=item['data'].replace('#mobile#',phone)
            # 若要使用封装的正则替换，需要将生成的手机号保存为类属性（使用setattr动态添加类属性）
            # 即 phone=self.random_mobile()修改为：
            # setattr(TestRegister,'mobile',self.random_mobile())
            # 此时保存的参数名必须为   'mobile' ，不能再为phone，否则无法与表中的#mobile#对应

        # 字典格式从excel中读取出来均为列表，需要转化为字典
        params=eval(item['data'])

        # 3.请求头（handers）
        # 可放入配置文件，方便修改，放入类属性进行调用。

        # 4.请求方法
        # 原本即为字符串，所以不用转换（字母、数字Excel可识别，所以不需要转化）
        # 需转换为小写，以便第二步中使用
        method=item['method'].lower()

        # 5.预期结果
        expected=eval(item['expected'])

        # 第二步：请求接口，获取实际返回结果
        # requests.post()此仅能发送post请求，使用request()可发送任何请求
        response=requests.request(method,url,json=params,headers=self.headers)
        res=response.json()
        # 可在报告上体现出实际结果和预期结果
        print("预期结果：",expected)
        print("实际结果：",res)
        # 如需回写测试结果，则增加该参数，用于识别用例对应的行
        row = item["case_id"] + 1

        # *******************数据库校验是否注册成功**********************
        # 查询数据库中该手机号对应的账号数(查询手机号从用例数据中获取，有则返回手机号，无则返回空字符串，所以使用get方法)
        # sql='SELECT * FROM future.member WHERE mobile_phone="{}"'.format(params.get('mobile_phone',''))
        # count=self.db.find_count(sql)
        # 或将SQL语句写在用例表中
        if item['check_sql']:
            sql = item['check_sql'].format(params.get('mobile_phone', ''))
            count = self.db.find_count(sql)
        # 仅校验注册成功的用例，失败不校验（判断写在以下断言中）

        # 第三步：断言
        # 用预期与实际返回的code、msg对比
        try:
            self.assertEqual(expected['code'],res['code'])
            self.assertEqual(expected['msg'], res['msg'])
            # 判断是否需要执行判断：
            # 仅判断执行成功的用例，数据是否在数据库中（在用例表中增加check_sql栏，用1标识执行通过的用例）
            # 若check_sql非空，执行判断
            if item['check_sql']:
                print('数据库中查询的数量为：',count)
                # 判断预期结果1是否与查询结果count一致
                self.assertEqual(1,count)

        # 如果断言错误，则捕获异常
        except AssertionError as e:
        # 处理异常：
            # 记录日志
            my_log.error("用例--【{}】--执行失败".format(item['title']))
            # 记录失败原因
            # 也可用my_log.error(e)，但没有exception详细
            my_log.exception(e)
            # 回写结果到excel（不太建议，比较耗时）
            self.excel.write_data(row=row, column=8, value='不通过')
            # 然后必须抛出异常
            raise e
        # 结果正确处理：
        else:
            # 记录日志
            my_log.info("用例--【{}】--执行成功".format(item['title']))
            # 回写结果到excel（不太建议，比较耗时）
            self.excel.write_data(row=row, column=8, value='通过')
