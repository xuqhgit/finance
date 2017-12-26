# coding:utf-8
# @author:apple
# @date:16/1/28
import top.api

top.setDefaultAppInfo("23304926", "895d3a46def9d59563ccc246c8148d3a")


def send():
    req = top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.extend = "123456"
    req.sms_type = "normal"
    req.sms_free_sign_name = "活动验证"
    req.sms_param = "{'code':'金鑫','product':'test','item':'支付宝邀请好友红包活动'}"
    req.rec_num = "13168033213"
    req.sms_template_code = "SMS_4995237"
    try:
        resp = req.getResponse()
        print(resp)
    except Exception, e:
        print(e)


def query():
    req = top.api.AlibabaAliqinFcSmsNumQueryRequest()
    req.biz_id = "1234^1234"
    req.rec_num = "13000000000"
    req.query_date = "20151215"
    req.current_page = 1
    req.page_size = 10
    try:
        resp = req.getResponse()
        print(resp)
    except Exception, e:
        print(e)


if __name__ == '__main__':
    send()
