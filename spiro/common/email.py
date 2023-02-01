import smtplib

from email.mime.text import MIMEText

from ..config import config

template = "{user}回复了您的评论，回复内容为：{content}"

class EmailSender:
  def __init__(self):
    self.server = smtplib.SMTP(config.email.smtp_server, config.email.port)
    self.server.login(config.email.addr, config.email.password)

  def send_reply(self, to_email, user, content):
    msg = MIMEText(template.format(user=user, content=content))
    msg["Subject"] = "您有新的回复"
    msg["From"] = config.email.addr
    msg["To"] = to_email
    
    self.server.sendmail(config.email.addr, to_email, msg.as_string())

emailSender = EmailSender()

