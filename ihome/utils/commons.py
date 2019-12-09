# coding:utf-8

from werkzeug.routing import BaseConverter


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# xrange
def xrange(start, end=None, step=1):
    if end is None:
        end = start
        start = 0
    if step > 0:
        while start < end:
            yield start
            start += step
    elif step < 0:
        while start > end:
            yield start
            start += step
    else:
        return 'step can not be zero'
