from . import mail
from flask import render_template
from flask_mail import Message

#function to send confirmation email
def send_mail(sender, to, templates, **kwargs):
    msg = Message('Registration confirmation', sender=sender, recipients=[to])
    msg.body = render_template(templates + '.txt', **kwargs)
    msg.html = render_template(templates + '.html', **kwargs)
    mail.send(msg)