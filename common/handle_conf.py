# 该模块用于处理配置文件../conf/config.ini

import os
from configparser import ConfigParser
from common.handle_path import CONF_DIR

class Config(ConfigParser):
# 在创建对象时，直接加载配置文件中的内容
    def __init__(self,conf_file):
        super().__init__()
        self.read(conf_file,encoding='utf-8')

conf=Config(os.path.join(CONF_DIR,'config.ini'))