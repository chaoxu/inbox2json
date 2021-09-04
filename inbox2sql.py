import email
import mailparser
import traceback
import sys
import imapclient
import json
import datetime
from collections.abc import Callable
from typing import Any

class Mail:
  def __init__(self, subject, date, source, receiver, body, message_id):
    self.id = message_id
    self.subject = subject
    self.date = date
    self.source = source
    self.receiver = receiver
    self.body = body


def sql_insert(cur, mail: Mail):
  # id, date, source, receiver, subject, body, status, last_update_time
  cur.execute("insert into mail values (?, ?, ?, ?, ?, ?, ?, ?)",
              (mail.id, mail.date, mail.source, mail.receiver, mail.subject, mail.body,
               'new', datetime.datetime.utcnow()))
  cur.commit()


def json_output(mail: Mail):
  d = mail.__dict__.copy()
  d['date'] = d['date'].strftime("%Y-%m-%dT%H:%M:%S")
  print(json.dumps(d))


def read_html_email(bytes: bytes):
  # fallback method to read the mail
  email_msg = email.message_from_bytes(bytes)  # email.message_from_string(data[0][1])

  # If message is multi part we only want the text version of the body, this walks the message and gets the body.
  if email_msg.is_multipart():
    for part in email_msg.walk():
      if part.get_content_type() == "text/html":
        body = part.get_payload(
          decode=True)  # to control automatic email-style MIME decoding (e.g., Base64, uuencode, quoted-printable)
        body = body.decode()
  return body


def parse_email(bytes: bytes):
  message = mailparser.parse_from_bytes(bytes)
  subject = message.subject
  if len(message.from_)>0:
    source = message.from_[0][1]
  else:
    source = ''
  if len(message.to)>0:
    receiver = message.to[0][1]
  else:
    receiver = ''
  message_id = message.message_id
  date = message.date
  if message.text_html:
    body = message.text_html[0]
  else:
    try:
      body = read_html_email(bytes)
    except Exception as e:
      body = message.text_plain[0]

  return Mail(subject, date, source, receiver, body, message_id)


class Mailbox:
  def __init__(self,
               host: str,
               port: int,
               username: str,
               password: str,
               inbox: str = 'Inbox',
               archive: str = 'Archive',
               move_to_archive: bool = True):
    self.inbox_folder = inbox  # this is the default inbox we work with
    self.username = username
    self.password = password
    self.archive_folder = archive
    self.client = imapclient.IMAPClient(host=host, port=port, use_uid=True, ssl=True)
    self.move_to_archive = move_to_archive
    self.mail_processor = None

  def __exit__(self, exc_type, exc_value, traceback):
    self.client.logout()

  def set_mail_processor(self, processor: Callable[[Mail], Any]):
    self.mail_processor = processor

  def init_client(self):
    self.client.login(self.username, self.password)
    self.client.select_folder(self.inbox_folder)

  def move_email(self, message_id, folder):
    try:
      if folder != self.inbox_folder:
        self.client.move([message_id], folder)
    except Exception as e:
      print(e)

  def process_emails(self, limit: int):
    messages = self.client.search(['NOT', 'DELETED'])
    response = self.client.fetch(messages, ['BODY.PEEK[]'])
    count = 0
    success_count = 0
    for message_id, data in response.items():
      count += 1
      if count > limit:
        count -= 1
        break
      try:
        # convert to mail
        d = parse_email(data[b'BODY[]'])
        self.mail_processor(d)
        if self.move_to_archive:
          self.move_email(message_id, self.archive_folder)
        success_count += 1
      except Exception as e:
        traceback.print_exc(file=sys.stdout)
    print("# processed: " + str(count))
    print("# success: " + str(success_count))

  def run(self, limit=1000000):
    self.run_batch(limit)

  # batch mode, go into mailbox, process all emails and close connection
  def run_batch(self, limit):
    print("Initialize Connection")
    self.init_client()
    print("Start Processing Email")
    self.process_emails(limit)
    print("Logout")
    self.client.logout()
