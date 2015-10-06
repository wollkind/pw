__author__ = 'steve'


import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

msg = MIMEText('test email')

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'The contents of'
msg['From'] = 'test@li1281-193.members.linode.com'
msg['To'] = 'wollkind@gmail.com'

# Send the message via our own SMTP server.
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()