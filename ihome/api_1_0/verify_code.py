
from flask import current_app,make_response,jsonify,request
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_store,constants


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













