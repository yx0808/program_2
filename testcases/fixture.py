# 前置模块

#

import requests

from jsonpath import jsonpath
from common.handle_conf import conf


# 定义一个类，用来接收保存的类属性
class BaseTest:

    @classmethod
    # 获得：admin_headers（管理员登录的请求头，包含token）
    #      admin_member_id（管理员账户id）
    # 1.管理员登录前置
    def admin_login(cls):
        # 1.请求数据（管理员）
        # 请求地址：基本地址+登录地址
        url = conf.get('env', 'base_url') + '/member/login'
        params = {
            # 从配置文件模块读取
            'mobile_phone': conf.get('test_data', 'admin_mobile'),
            'pwd': conf.get('test_data', 'admin_pwd')
        }
        headers = eval(conf.get('env', 'headers'))
        # 发送请求
        response = requests.post(url=url, json=params, headers=headers)
        res = response.json()
        # 2.提取token
        admin_token = jsonpath(res, '$..token')[0]
        cls.admin_token = admin_token
        # 保存请求头:Bearer+空格+token 到 Authorization 中
        headers['Authorization'] = 'Bearer ' + admin_token
        cls.admin_headers = headers
        # print(cls.headers)
        # 3.提取用户id（回写到测试数据中）
        cls.admin_member_id = jsonpath(res, '$..id')[0]

    @classmethod
    # 获得：headers（普通用户登录的请求头，包含token）
    #      member_id（普通用户账户id）
    # 普通用户登录
    def user_login(cls):
        '''用例类的前置方法：登录获取token'''
        # 1.请求登录，登录成功
        # 请求地址：基本地址+登录地址
        url=conf.get('env','base_url')+'/member/login'
        # 请求参数，测试账号（账号多变，可放入配置文件进行调用）
        params={
            # 登录电话号，从配置文件模块读取[test_data]配置块中的mobile
            'mobile_phone':conf.get('test_data','mobile'),
            # 登录电话号，从配置文件模块读取[test_data]配置块中的pwd
            'pwd':conf.get('test_data','pwd')
        }
        # 请求头，字典从ini文件中读出为字符串，需转为字典
        headers=eval(conf.get('env','headers'))
        # 2.使用requests发送请求,携带URL、请求参数、请求头
        response=requests.post(url=url,json=params,headers=headers)
        # 保存返回数据
        res=response.json()

        # 3.提取token
        # jsonpath提取出的数据为列表，可通过索引进行取值（虽然该列表只有一个数据，但也需要索引，因为索引出来的为字符串，符合使用要求）
        token=jsonpath(res,'$..token')[0]
        cls.token=token
        print('token-1:',token)
        # 保存请求头:Bearer+空格+token 到 Authorization 中(作为键值对保存)
        headers['Authorization']='Bearer ' + token
        # print(cls.token)
        # 保存含有Token的请求头为类属性
        cls.headers = headers
        # print(cls.headers)

        # 3.提取用户id给充值接口使用（回写到测试数据中/所以此member_id名称的设置需与用例表中需要替换的参数名（#member_id#）一致）
        # [0]：通过索引方法转换为字符串
        # cls.：设置为类属性
        cls.member_id=jsonpath(res,'$..id')[0]

    @classmethod
    # 依赖user_login()
    # 获得:loan_id(创建项目的id)
    # 项目创建
    def add_project(cls):
        url = conf.get('env', 'base_url') + '/loan/add'
        # 参数
        params = {
            # 用户id（普通用户）
            "member_id": cls.member_id,
            # 项目标题
            "title": "实现财富自由",
            # 借款金额
            "amount": "200",
            # 年利率（%）
            "loan_rate": "10",
            # 借款期限
            "loan_term": "6",
            # 周期类型（1：月，2：天）
            "loan_date_type": "1",
            # 竞标天数
            "bidding_days": "5"
        }

        # 请求添加项目的接口
        response = requests.post(url=url, json=params, headers=cls.headers)
        res = response.json()

        # 提取项目id
        # 使用类名保存项目ID，保存为类属性
        cls.loan_id = jsonpath(res, '$..id')[0]

    @classmethod
    # 依赖add_project()和admin_login()
    # 不需要返回数据，项目审核通过即可
    # 审核项目
    def audit(cls):
        url = conf.get('env', 'base_url') + '/loan/audit'
        # 参数
        params = {
            # 项目id
            "loan_id": cls.loan_id,
            # 是否通过true/false
            "approved_or_not": True
        }
        # 请求审核项目的接口
        res=requests.patch(url=url, json=params, headers=cls.admin_headers)
        print(res)










