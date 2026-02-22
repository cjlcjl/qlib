from myself.tools.basic import init_my_qlib
from qlib.contrib.data.handler import Alpha158


def trytry():
    # 初始化 QLib
    init_my_qlib()

    # 使用内置的 Alpha158 特征集
    handler = Alpha158(
        start_time='2010-01-01',
        end_time='2020-12-31',
        fit_start_time='2010-01-01',
        fit_end_time='2015-12-31',
        instruments='all'
    )

    # 获取特征数据
    features = handler.fetch(col_set='feature')
    # 获取标签数据
    labels = handler.fetch(col_set='label')

    print('特征数据形状:', features.shape)
    print('标签数据形状:', labels.shape)


if __name__ == '__main__':
    trytry()
