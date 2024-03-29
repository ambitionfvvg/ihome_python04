# -*- coding: UTF-8 -*-

from ihome.libs.yuntongxun.CCPRestSDK import REST
# from .CCPRestSDK import REST
import configparser

# 主帐号
accountSid = '8a216da867e881cb016804d98cf31097'

# 主帐号Token
accountToken = '35ead590cfaa4d0e889381cb78ca014d'

# 应用Id
appId = '8a216da867e881cb016804d98d44109d'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id


class CCP(object):
    """自己封装的发送短信的辅助类"""
    # 用来保存对象的类属性
    instance = None

    def __new__(cls):
        # 判断CCP类有没有创建好的对象，如果没有，创建一个对象，如果有，直接返回
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # 初始化REST yuntongxun
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj
        return cls.instance

    def sendTemplateSMS(self, to, datas, temp_Id):

        result = self.rest.sendTemplateSMS(to,datas,temp_Id)
        # for k,v in result.items():
        #
        #     if k == 'templateSMS':
        #             for k, s in v.items():
        #                 print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))
        # statusCode:     000000
        # smsMessageSid:  54987cxxxxxxxxxxxxxxe7ac93aa
        # dateCreated:    20190811193012
        status_code = result.get('statusCode')
        if status_code == '000000':
            return 0  # 000000表示发送成功
        return -1  # 发送失败

# if __name__ == '__main__':
#     ccp = CCP()
#     ret = ccp.sendTemplateSMS('18211528060', ["123", "456"], 1)
#     print(ret)
   
#sendTemplateSMS(手机号码,内容数据,模板Id)
# 示例
# 【云通讯】您使用的是云通讯短信模板，您的验证码是123，请于456分钟内正确输入
