# -*- coding: utf-8 -*-

def index():
    redirect('/todo/default/login')

def register():
    return dict(form=auth.register(), title='Sign Up')

def request_reset_password():
    return dict(form=auth.request_reset_password(), title='Request Reset Password')

def reset_password():
    return dict(form=auth.reset_password(), title='Reset Password')

def profile():
    return dict(form=auth.profile(), title='Profile')

def login():
    if auth.user != None:
        redirect('/todo/todo/index')
    return dict(form=auth.login())
