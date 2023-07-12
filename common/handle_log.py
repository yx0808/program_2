# 该模块用于记录运行日志

import logging
import os.path

from common.handle_conf import conf
from common.handle_path import LOG_DIR

def create_log(name='mylog',level='DEBUG',filename='log.log',sh_level='DEBUG',fh_level='DEBUG'):
    log = logging.getLogger(name)
    log.setLevel(level)

    fh = logging.FileHandler(filename, encoding='utf-8')
    fh.setLevel(fh_level)
    log.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(sh_level)
    log.addHandler(sh)

    formats = '%(asctime)s-[%(filename)s-->line:%(lineno)d]-%(levelname)s:%(message)s'
    log_format1 = logging.Formatter(formats)
    log_format2 = logging.Formatter(formats)

    fh.setFormatter(log_format1)
    sh.setFormatter(log_format2)

    return log


my_log=create_log(
    name=conf.get('logging','name'),
    level=conf.get('logging','level'),
    filename=os.path.join(LOG_DIR,conf.get('logging','filename')),
    # 日志文件所在文件
    fh_level=conf.get('logging','fh_level'),
    sh_level=conf.get('logging','sh_level')
)