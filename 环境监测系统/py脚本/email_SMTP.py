﻿# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
#mailto_list=['774832389@qq.com']           #收件人(列表)
mail_host="smtp.163.com"            #使用的邮箱的smtp服务器地址，这里是163的smtp地址
mail_user='17865191779'                           #用户名
mail_pass='jxt17865191779'                             #密码
mail_postfix="163.com"                     #邮箱的后缀，网易就是163.com
def send_mail(to_list,sub,content):
    me="17865191779"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)                #将收件人列表以‘；’分隔
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)                            #连接服务器
        server.login(mail_user,mail_pass)               #登录操作
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False

'''
total_content = "This is a Email test" + str(int(1))

for i in range(1):                             #发送1封，上面的列表是几个人，这个就填几
    if send_mail(mailto_list,"这是一封测试邮件",total_content ):  #邮件主题和邮件内容
        #这是最好写点中文，如果随便写，可能会被网易当做垃圾邮件退信
        print("done!")
    else:
        print("failed!")
'''
