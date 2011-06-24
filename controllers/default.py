# -*- coding: utf-8 -*-

def index():
    return dict(form=auth())

def register():
    return dict(form=auth.register())

def user():
    return dict(form=auth())

