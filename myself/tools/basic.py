import logging

import qlib
from myself.tools.const import qlib_combine_path
from qlib.constant import REG_CN


def init_my_qlib():
    qlib.init(
        provider_uri=qlib_combine_path,  # 数据存储路径
        region=REG_CN,  # 市场区域，REG_CN 表示中国市场
        redis_host='127.0.0.1',
        redis_port=6379,
        redis_task_db=1,  # Redis 数据库编号
        logging_level=logging.INFO,
    )
