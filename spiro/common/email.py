import smtplib

from email.mime.text import MIMEText
from multiprocessing import Queue, Process
from time import sleep

from ..config import SpiroConfig

comment_hint_template = "{user}评论了您的文章，评论内容为：\n\n{content}\n\n\n----------------------\n请点击：\n{link}\n以了解详情"
reply_hint_template = "{user}回复了您的评论，回复内容为：\n\n{content}\n\n\n----------------------\n请点击：\n{link}\n以了解详情"
verify_hint_template = "{user}你好，感谢您注册{website}, 请点击：\n\n{link}\n\n以验证你的邮箱"

email_sender_worker = None

def init_email_worker():
  global email_sender_worker
  email_sender_worker = _EmailSenderWorker()
  return email_sender_worker

def get_email_worker():
  global email_sender_worker
  return email_sender_worker

class _EmailSender:
  def send_mail(self, to_email, msg):
    self.server = smtplib.SMTP(SpiroConfig.email.smtp_server, SpiroConfig.email.port)
    self.server.login(SpiroConfig.email.send_addr, SpiroConfig.email.password)
    self.server.sendmail(SpiroConfig.email.send_addr, to_email, msg.as_string())

class _EmailSenderWorker:
  def __init__(self):
    self.q = Queue()
    self.em_sender = _EmailSender()

  def run(self):
    self.p = Process(target=self._work)
    self.p.start()

  def terminate(self):
    while True:
      if self.q.empty():
        print("Sleep 10s to send the remaining email")
        sleep(10)
        self.p.terminate()
        self.q.close()

  def send_comment_hint(self, to_mail, user, reply_content, url):
    content = MIMEText(reply_hint_template.format(user=user, content=reply_content, link=url))
    content["Subject"] = f"[{SpiroConfig.website_name}] 您有新的评论"
    content["From"] = SpiroConfig.email.send_addr
    content["To"] = to_mail
    self.q.put({
      "to": to_mail,
      "content": content
    })

  def send_reply_hint(self, to_mail, user, reply_content, url):
    content = MIMEText(reply_hint_template.format(user=user, content=reply_content, link=url))
    content["Subject"] = f"[{SpiroConfig.website_name}] 您有新的回复"
    content["From"] = SpiroConfig.email.send_addr
    content["To"] = to_mail
    self.q.put({
      "to": to_mail,
      "content": content
    })

  def send_email_verify(self, to_mail, user, link):
    content = MIMEText(verify_hint_template.format(
      user=user, website=SpiroConfig.website_name, link=link
    ))
    content["Subject"] = f"[{SpiroConfig.website_name}] 邮箱验证"
    content["From"] = SpiroConfig.email.send_addr
    content["To"] = to_mail
    self.q.put({
      "to": to_mail,
      "content": content
    })

  def _work(self):
    while True:
      msg = self.q.get()
      self.em_sender.send_mail(msg["to"], msg["content"])

if __name__ == "__main__":
  worker = _EmailSenderWorker()
  worker.run()
  worker.send("test@yopmail.com", "test", "output")
  print("Finished")