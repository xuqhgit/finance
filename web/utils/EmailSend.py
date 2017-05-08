# -*- coding: utf-8 -*-
# author: apple
# createTime: 16/10/6
import smtplib
from email.mime.text import MIMEText

config = {
    'host': 'smtp.gogohou.com',  # 设置服务器
    'user': 'finance@gogohou.com',  # 用户名
    'password': '123@anchor'  # 口令
}


def send_txt(content, sub, to_list=['294797097@qq.com']):
    """
    发送文本邮件 默认为294797097邮箱
    :param content: 发送内容
    :param sub: 发送主题
    :param to_list: 发送对象 list
    :return: 成功返回True 失败返回False
    """
    me = "A-Finance" + "<" + config['user'] + ">"
    # _subtype='html' 为发送html格式
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(config['host'])
        server.login(config['user'], config['password'])
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


if __name__ == '__main__':
    send_txt("test", "finance")
