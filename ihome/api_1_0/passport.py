


from flask import request,jsonify
from ihome.models import User
from . import api
from ihome.utils.response_code import RET


@api.route("/users",method=["POST"])
def register():
    """
    用户注册
    参数：mobile,sms_code , password,password2
    参数格式：json
    :return:
    """

    # 1.获取参数,获取请求的json数据，到字典中
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 2.校验参数的完整性
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="请求的参数不完整")

    # 3.
