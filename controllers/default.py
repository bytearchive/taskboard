# -*- coding: utf-8 -*-

def index():
    redirect('/todo/default/user/login')

def register():
    return dict(form=auth.register(), title='Sign Up')

def request_reset_password():
    return dict(form=auth.request_reset_password(), title='Request Reset Password')

def reset_password():
    return dict(form=auth.reset_password(), title='Reset Password')

def user():
    arg = request.args(0)
    if arg == 'login' and auth.user != None:
        redirect('/todo/todo/index')
    return dict(form=auth())
#return dict(form=auth(), title='Sign Up')

