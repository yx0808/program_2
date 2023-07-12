# 该模块用于处理项目中的绝对路径

import os

# 项目根目录的绝对路径(根据文件所在层数决定)
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)

# 用例数据所在目录:
DATA_DIR=os.path.join(BASE_DIR,"datas")
# print(DATA_DIR)

# 配置文件所在目录
CONF_DIR=os.path.join(BASE_DIR,"conf")

# 日志文件所在目录
LOG_DIR=os.path.join(BASE_DIR,"logs")

# 报告文件所在目录
REPORT_DIR=os.path.join(BASE_DIR,"reports")

# 用例模块所在目录
CASES_DIR=os.path.join(BASE_DIR,"testcases")