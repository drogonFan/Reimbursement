import time
import threading
import _thread
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.header import Header
from getpass         import getpass
from smtplib         import SMTP_SSL

# 第三方 SMTP 服务
DEFAULT_MAIL_HOST="smtp.163.com"                # 设置服务器
DEFAULT_MAIL_USER="daenerystargaryen8"          # 用户名
DEFAULT_MAIL_PASS="NPGEUZIZWHHGNMXL"            # 口令

DEFAULT_SENDER = 'daenerystargaryen8@163.com'   # 发件人邮箱(最好写全, 不然会失败)
DEFAULT_SENDER_NAME = 'admin'
DEFAULT_TITLE = 'oscar发票报销系统注册验证'       # 邮件主题

DEFAULT_OSCAR_LOGO = './static/img/oscar_logo.gif'
DEFAULT_UP_PNG = './static/img/top.png'
DEFAULT_MAIL_HTML = './templates/email.htm'

# 邮件服务
class Email163(object):
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Email163, '_instance'):
            with Email163._instance_lock:   # 保证线程安全
                if not hasattr(Email163, '_instance'):
                    Email163._instance = Email163(*args, **kwargs)
        return Email163._instance

    def sendEmail(self, receivers, link):
        with open(DEFAULT_MAIL_HTML, 'r', encoding='utf-8') as f:
            mail_body = f.read()

        msg = MIMEMultipart('related')
        msg['To'] = receivers
        msg['Subject'] = DEFAULT_TITLE

        msgText = MIMEText(mail_body.replace('verification_link', link), _subtype='html', _charset='utf-8')
        msg.attach(msgText)

        # 添加图片
        with open(DEFAULT_OSCAR_LOGO, 'rb') as f:
            img_data = f.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', '<234>')
            msg.attach(img)

        with open(DEFAULT_UP_PNG, 'rb') as f:
            img_data = f.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', '<123>')
            msg.attach(img)
        try:
            pass
            smtpObj = smtplib.SMTP_SSL(DEFAULT_MAIL_HOST, 465)  # 启用SSL发信, 端口一般是465
            smtpObj.login(DEFAULT_MAIL_USER, DEFAULT_MAIL_PASS)  # 登录验证
            smtpObj.sendmail(DEFAULT_SENDER, receivers, msg.as_string())  # 发送
        except smtplib.SMTPException as e:
            print(e)