# coding:utf-8

from werkzeug.routing import BaseConverter
from flask import jsonify,session,g
from ihome.utils.response_code import RET
import functools


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


def login_required(view_func):
    """
    定义登录验证器
    :param view_func:
    :return:
    """
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 获取用户的登录状态
        user_id = session.get("user_id")
        # 如果用户已经登录，则执行视图函数
        if user_id is not None:
            # 将user_idｂ保存到ｇ对象中，在视图函数中科通过ｇ对象，获取用户ｉｄ
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.LOGINERR, errmsg="用户未登录")

        return wrapper

