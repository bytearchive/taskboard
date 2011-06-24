# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

db = DAL('sqlite://storage.sqlite')

from gluon.tools import Auth
auth = Auth(db)  
auth.settings.hmac_key = 'sha512:b868ae2b-9b73-4541-a54b-ce5e1a50f3b9' 
auth.define_tables()                          
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False

auth.settings.login_next = URL('todo', 'index')
auth.settings.logout_next = URL('index')

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

db.define_table('tip',
                Field('meta_tip_id', db.meta_tip),
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('has_viewed', 'boolean', default=False),
                Field('created', 'datetime', default=request.now))

db.todo.user_id.represent = lambda user_id: db.auth_user(user_id).email
db.tip.user_id.represent = lambda user_id: db.auth_user(user_id).email


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
    db.meta_tip.bulk_insert([{'text': t, 'expired_date': datetime(2, 2, 2)} for t in META_TIPS])


import logging
logger = logging.getLogger("[todo]")
logger.setLevel(0)
