
from flask import request,g,jsonify,current_app
from ihome.utils.response_code import RET
from . import api
from ihome.models import User
from ihome import db

@api.route("/users/avatar",methods=["POST"])
def set_user_avatar():
    """
    设置用户的个人图像
    :return:
    """
    # 1.获取用户ID
    user_id = g.user_id

    # 2.获取图片
    image_file = request.files.get("avatar")

    # 3.判断图片的上传
    if image_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg="未上传图片")

    # 4,进行图片的存储操作,C:\Users\zhaohui.li\Desktop\IHOME\ihome_python04\ihome\static\images\home01.jpg
    image_data = image_file.read()

    # 4.1 设置图片存储的路径
    avatar_url = r"C:\Users\zhaohui.li\Desktop\IHOME\ihome_python04\ihome\static\images\avatar"+"\\"+user_id+".png"
    with open(avatar_url, 'wb') as f:
        f.write()

    # 4.2 保存用户图像地址到数据库中
    try:
        User.query.filter_by(id=user_id).update({"avatar_url":avatar_url})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="保存用户图像地址失败")

    return jsonify(errno=RET.OK,errmsg="保存图片成功",data={"avatar_url":avatar_url})
