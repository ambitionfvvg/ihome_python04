
import re
from flask import request, jsonify, current_app, session
from . import api
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError
from ihome.constants import LOGIN_ERROR_MAX_TIMES,LOGIN_ERROR_FORBID_TIME


@api.route("/users", methods=["POST"])
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

    # 3.判断手机号的格式是否正确
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 4. 判断用户两次输入的密码是否一致
    if password2 != password:
        return jsonify(errno=RET.PARAMERR, errmsg="两次填写的密码不一致")

    # 5. 验证短信验证码，
    # 5.1 从redis中取出验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 5.2 判断验证码是否已过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="验证码已失效")

    # 5.3 判断用户填写的验证码是否正确
    real_sms_code = real_sms_code.decode()
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码不正确")

    # 6. 判断手机号是否已注册过
    user = User(name=mobile, mobile=mobile)

    user.password = password  # 密码加密

    # 7. 保存注册信息到数据库中，password 加密
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据操作错误回滚
        db.session.rollback()
        # 表示手机号已被注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已注册过")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 8. 保存登录信息到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 9.返回注册结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    参数：手机号和密码
    参数格式：json
    :return:
    """
    # 1.获取参数,格式：json
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 2.校验参数的完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 3.校验手机号码的格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号码格式不对")

    # 4.验证用户登录失败的次数
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) > LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.LOGINERR,errmsg="登录失败次数较多，请稍后再试")

    # 5.验证用户的密码
    # 5.1 从数据库中查询该手机号对应的用户数据
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户信息失败")

    # 5.2 进行密码验证
    if user is None or not user.check_password(password):
        # 如果验证失败，记录失败次数，返回错误信息
        try:
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="手机号或者密码错误")

    # 6 保存登录信息到session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK,errmsg="登录成功")


@api.route("/sessions",methods=["GET"])
def check_login():
    """
    检查登录状态
    :return:
    """

    # 1.获取用户名,name
    name = session.get("name")

    # 2.判断用户名是否存在，如果name 存在，则表示用户已登录，
    if name is not None:
        return jsonify(errno=RET.OK,errmsg="true",data={"name":name})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg="false")


@api.route("/sessions",methods=["DELETE"])
def logout():
    """
    登录退出
    :return:
    """
    # 清楚session数据
    session.clear()
    return jsonify(errno=RET.OK,errmsg="ok")





