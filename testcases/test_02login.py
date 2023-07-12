# 登录模块用例

# 导入os模块(官方库)，用于拼接路径
import os
# 导入unittest模块(官方库)
import unittest
# 导入请求接口模块
import requests
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
# 导入tools模块，使用正则方法替换用例中需要替换的参数
from common.tools import replace_data


# 在测试类前@ddt
@ddt
# 定义一个登录测试类(TestLogin),继承unittest的TestCase
class TestLogin(unittest.TestCase):
    # 创建一个操作excel的对象（excel），用于传输用例文件路径（绝对路径）、表单名称
    excel=HandleExcel(os.path.join(DATA_DIR,'apicase.xlsx'),"login")
    # 读取excel用例数据(调用raed_data方法)
    cases=excel.read_data()
    # （第一步：1.）使用所写handle_conf模块中的conf读取配置文件中的接口地址
    base_url=conf.get('env','base_url')
    # （第一步：3.）从配置文件获取请求头，但读取后为列表，需要转化为字典
    headers=eval(conf.get('env','headers'))

    # 定义一个字典成员运算的逻辑assertDictin，用于判断实际返回结果中是否有预期结果中的内容
    # 封装该方法
    def assertDictin(self, res, expected):
        # 在预计结果中使用k,v遍历，遍历结果为键和值
        for k, v in expected.items():
            # 判断实际结果中是否能找到该键，且该键对应的值是否与遍历的v相等
            if res.get(k) == v:
                # 此处写等于的处理
                pass
                # 结果不等时
            else:
                # 抛出异常:{实际结果}不等于{预期结果}
                raise AssertionError("{} [k,v] not in {}".format(res, expected))

    # 在方法前@list_data(),括号内放用例数据
    @list_data(cases)
    # 定义一个用例方法(test_login)来写用例执行逻辑,定义item用于接收用例数据cases
    def test_login(self,item):
        # 第一步：准备用例数据
        # 1.接口地址
        # (在此处读取base_url会读取13次，放入类属性中读取一次即可)
        # 在实例方法中使用self调用类属性,并接入Excel中的具体接口
        url=self.base_url+item['url']

        # 2.接口请求参数
        # ①原方法：登录账号密码直接写在表中，直接从表获取
        # params=eval(item['data'])
        # ②高级方法：将表中需要登录的账号密码使用正则方法替换为配置文件中的账号密码
        # 注意：表格中需要替换的数据标识名需与配置文件中名称一致（pwd、mobile）
        item['data']=replace_data(item['data'],TestLogin)
        # 字典格式从excel中读取出来均为列表，需要转化为字典
        params = eval(item['data'])

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
        print("预期结果：",expected)
        print("实际结果：",res)
        # 如需回写测试结果，则增加该参数，用于识别用例对应的行
        row = item["case_id"] + 1

        # 第三步：断言
        try:
            # 调用封装好的assertDictin方法对比实际结果与预期结果
            self.assertDictin(res,expected)
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
