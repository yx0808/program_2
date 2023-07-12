# 该模块用于操作数据库
# 注意，该模块方法未使用with,执行SQL后不会自动提交，需另使用commit提交事务（已在模块中备注）
# 此方法仅适用只连接一个数据库，如需调用多个数据库，方法见笔记syx/py2_interface_test/dy_pymysql连接数据库.py/第7条

# 导入pymysql数据库操作模块
import pymysql
# 导入定义的配置文件操作方法conf
from common.handle_conf import conf


# 定义类
class HandleDB:

# 定义连接数据库方法
    def __init__(self):
        # 连接数据库
        con = pymysql.connect(host=conf.get('mysql','host'),
                          # 从配置文件中读取的为字符串，但port需要int类型，所以使用getint
                          port=conf.getint('mysql','port'),
                          user=conf.get('mysql','user'),
                          password=conf.get('mysql','password'),
                          charset='utf8',
                          # 设置游标返回结果格式
                          # cursorclass=pymysql.cursors.DictCursor
                          )
        # 添加实例属性，方便调用
        self.con = con


# 定义SQL查询方法（查询第一条数据）
    def find_one(self, sql):
        # 使用self调用__int__中的con作为连接结果，调用cursor()创建游标cur
        cur = self.con.cursor()
        # 执行SQL
        cur.execute(sql)
        # 提交事务
        self.con.commit()
        # 查询第一条数据
        res=cur.fetchone()
        # 关闭游标
        cur.close()
        # 返回结果
        return res

# 定义SQL查询方法（查询全部数据）
    def find_all(self, sql):
        # 使用self调用__int__中的con作为连接结果，调用cursor()创建游标cur
        cur = self.con.cursor()
        # 执行SQL
        cur.execute(sql)
        # 提交事务
        self.con.commit()
        # 查询全部数据
        res = cur.fetchall()
        # 关闭游标
        cur.close()
        # 返回结果
        return res

# 定义查询sql结果条数方法
    def find_count(self,sql):
        cur = self.con.cursor()
        res = cur.execute(sql)
        # 提交事务
        self.con.commit()
        # 关闭游标
        cur.close()
        # 返回结果
        return res

# 定义析构魔术方法：执行完成后自动执行一次
    def __del__(self):
        # 关闭连接对象（游标的关闭最好设置在使用后，及时关闭，未关闭不会报错但会占用内存）
        self.con.close()
