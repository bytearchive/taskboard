# -*- coding: utf-8 -*-

def index():
    redirect('/todo/default/user/login')

def register():
    return dict(form=auth.register())

def user():
    if request.args(0) == 'login' and auth.user != None:
        redirect('/todo/todo/index')
    return dict(form=auth())

