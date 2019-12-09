
from flask import current_app,make_response,jsonify,request
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_store,constants
import random
from ihome.libs.yuntongxun.sms import CCP
from ihome.models import User


@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    生成图片验证码
    :image_code_id ：图片验证码编号
    :return: 如果出现异常，则返回异常，否则返回验证码图片
    """
    # 获取图片验证码
    # 名字，真实文本，验证码图片
    name, text, image_code = captcha.generate_captcha()

    try:
        redis_store.setex('image_code_%s'% image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="save image_code failed")

    resp = make_response(image_code)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GET /api/v1.0/sms_codes/<mobile>?image_code=xxxx&image_code_id=xxxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """
    发送短信验证码
    :mobile :手机号码
    :return:
    """
    # 1.获取图形验证码相关的参数，image_code,image_code_id
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 2.校验参数的完整性
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 3.校验图形验证码的准确性
    # 3.1 去redis中之前存的图形验证码进行对比，注意：1.对比验证码是否过期，2.对比验证码是否准确
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA,errmsg="redis 数据库异常")

    # 3.2 校验验证码是否过期
    if real_image_code is None:
        # 表示验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg="图形验证码，验证失败,IMAGE_CODE FAILDED")

    # 3.3删除redis中的验证码信息，防止用户用同一个验证码多次验证
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 3.4 对用户填写的验证码进行对比验证,全部转小写后进行对比
    real_image_code = real_image_code.decode()
    # print(image_code.lower())
    # print(real_image_code.lower())
    if image_code.lower() != real_image_code.lower():
        # 验证码对比不成功
        return jsonify(errno=RET.DATAERR,errmsg="验证码错误")

    # 3.5 判断该手机号是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno = RET.DATAEXIST, errmsg = "手机号已注册")


    # 4.验证用户是否在60秒内频繁操作，去redis中查询该手机号在60秒内是否有记录，如果有，则认为用户操作频繁
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(RET.DATAEXIST,errmsg = "手机号已存在，请勿频繁操作")

    # 5.发送短信验证码
    # 5.1 生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 5.2 保存短信验证码和手机号到redis中
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 设置保存验证码的时间,保存发送给这个手机号短信的记录，防止用户频繁发送短信的操作
        redis_store.setex("send_sms_code_%s" %mobile,constants.SEND_SMS_CODE_INTERVAL, 1)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg = "保存短信验证码异常")

    # 5.3 发送短信验证码
    try:
        ccp = CCP()
        result = ccp.sendTemplateSMS(mobile,[sms_code,int(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.THIRDERR, errmas = "发送短信验证码失败")

    # 验证返回值
    if result == 0:
        return jsonify(errno = RET.OK,errmsg = "发送短信验证码成功")
    else:
        return jsonify(errno = RET.THIRDERR, errmsg = "发送短信验证码失败")
















