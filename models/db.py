# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

db = DAL('sqlite://storage.sqlite')

from gluon.tools import Auth, Mail
auth = Auth(db)  
auth.settings.hmac_key = 'sha512:b868ae2b-9b73-4541-a54b-ce5e1a50f3b9' 
auth.define_tables()                          
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','reset_password')+'/%(key)s to reset your password'

auth.settings.login_next = URL('todo', 'index')
auth.settings.logout_next = URL('default', 'index')
auth.settings.register_next = URL('todo', 'index')

mail = Mail()
mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'some@mail.com'
mail.settings.login = 'username:passwd'
auth.settings.mailer = mail


db.define_table('todo',
                Field('uuid', 'string'),
                Field('created', 'datetime', default=request.now),
                Field('last_update', 'datetime', default=request.now),
                Field('type'),
                Field('margin_top', 'double', default=0.0),
                Field('margin_left', 'double', default=0.0),
                Field('text', 'text'),
                Field('deleted', 'boolean', default=False),
                Field('user_id', db.auth_user, default=auth.user_id),
                format=lambda x: x.text or '(empty)')

db.define_table('meta_tip',
                Field('text', 'text'),
                Field('expired_date', 'datetime', default=request.now+timedelta(1)),
                Field('created', 'datetime', default=request.now),
                format=lambda x: x.text or '[empty tip]')

db.define_table('viewed_tip',
                Field('meta_tip_id', db.meta_tip),
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('created', 'datetime', default=request.now))

db.todo.user_id.represent = lambda user_id: db.auth_user(user_id).email
db.viewed_tip.user_id.represent = lambda user_id: db.auth_user(user_id).email


meta_tip_count = db(db.meta_tip.id > 0).count()
if meta_tip_count == 0: 
    META_TIPS = [
        "Move cards around to arrange them in any way you want: todo list? kanban board?",
        "Double-click card to edit",
        "You can use hotkeys when editing text, just check <i>Ctrl+I</i> or <b>Ctrl+B</b>",
        "Every change is immediately saved",
        "You've already noticed #tags, didn't you?",
        "Just guess what <i>ESC</i> and <i>Ctrl+Enter</i> do", 
        "<i>Ctrl+H</i> makes a</p><h2>Heading</h2><p>and <i>Ctrl+G</i> turns text into a paragraph",
        "Oh, I forgot to tell you about HEX color tags #F5A"]
    db.meta_tip.bulk_insert([{'text': t, 'expired_date': datetime(9999, 1, 1)} for t in META_TIPS])

import logging
logger = logging.getLogger("[todo]")
logger.setLevel(-1)

def user_registration_notification(form):
    user = auth.user
    email_flag = mail.send(to=['aonther@mail.com'],
        subject='New User Registered',
        message='Hi, There is a new user named: %s %s, registerd, Congratuaion' % (user.first_name, \
              user.last_name))
    logger.info('new user email sent: %s' % str(email_flag))
auth.settings.register_onaccept = user_registration_notification

