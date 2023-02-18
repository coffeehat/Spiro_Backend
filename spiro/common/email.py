import smtplib

from email.mime.text import MIMEText
from multiprocessing import Queue, Process
from time import sleep

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

class EmailSenderWorker:
  def __init__(self):
    self.q = Queue()
    self.em_sender = EmailSender()

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

  def send(self, to_mail, user, content):
    self.q.put({
      'to_mail': to_mail,
      'user': user,
      'content': content 
    })

  def _work(self):
    while True:
      msg = self.q.get()
      print(f"Get work to do {msg}")
      self.em_sender.send_reply(msg['to_mail'], msg['user'], msg['content'])

email_sender_worker = EmailSenderWorker()

if __name__ == "__main__":
  worker = EmailSenderWorker()
  worker.run()
  worker.send("test@yopmail.com", "test", "output")
  print("Finished")