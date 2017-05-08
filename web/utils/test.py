# coding:utf-8

# @author:apple
# @date:16/1/18
import top.api

'''
这边可以设置一个默认的appkey和secret，当然也可以不设置
注意：默认的只需要设置一次就可以了

'''
top.setDefaultAppInfo("23304926", "895d3a46def9d59563ccc246c8148d3a")
# top.setDefaultAppInfo("1023304926", "sandbox6def9d59563ccc246c8148d
# 3a")

'''
使用自定义的域名和端口（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com",80)

使用自定义的域名（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com")

使用默认的配置（调用线上环境）
a = top.api.UserGetRequest()

'''


# req = top.api.UserGetRequest()


def testQuery():
    req = top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.extend = "123456"
    req.sms_type = "normal"
    req.sms_free_sign_name = "身份验证"
    req.sms_param = "{'code':'金鑫','product':'支付宝'}"
    req.rec_num = "13767079690"
    req.sms_template_code = "SMS_4995241"
    try:
        resp = req.getResponse()
        print(resp)
    except Exception, e:
        print(e)


if __name__ == '__main__':
    testQuery()
