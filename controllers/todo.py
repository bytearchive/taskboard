#-*- coding: utf8 -*-
from gluon.contrib import simplejson
from datetime import datetime
from helper import str_to_datetime

@auth.requires_login()
def index(): 
    logger.info('welcome user %d', auth.user_id)
    return dict()

@auth.requires_login()
def fetch():
    logger.info('user %d login, fetching data', auth.user_id)
    return __merge(request.vars.json, True)

@auth.requires_login()
def update():
    logger.info('update data')
    __merge(request.vars.json)

def __insert_welcome_todos():
    logger.info('insert welcome todos')
    welcome_todos = [ {'text': "<p><i>Welcome to</i></p><h2>Taskboard 10k</h2>", 
               'type': 'white', 'margin_top': 0.0916, 'margin_left': 0.1054 },
        {'text': "Need a new card? Just grab it from a deck on the left",
               'type': 'yellow', 'margin_top': 0.2122, 'margin_left': 0.13125 },
        {'text': "<p><b>Have fun!</b></p>",
               'type': 'green', 'margin_top': 0.3328, 'margin_left': 0.2008  }]
    import uuid
    for t in welcome_todos:
        t['uuid'] = uuid.uuid4()
        db.todo.insert(**t)

def __fetch_all_json():
    todo_count = db(db.todo.user_id==auth.user_id).count()
    if todo_count  == 0:
        __insert_welcome_todos()

    logger.info("fetch user\'s todos")
    query = (db.todo.deleted==False)&(db.todo.user_id==auth.user_id)
    todos = db(query).select()
    json = []
    for t in todos:
        json += [{
            'uuid': t.uuid,
            'last_update': t.last_update.strftime("%Y-%m-%d %H:%M:%S"),
            'state': 'updated',
            'type': t.type,
            'margin_top': t.margin_top,
            'margin_left': t.margin_left,
            'text': t.text
        }]
    return simplejson.dumps(json) 

def __merge(json, isFetch=False):
    cards = json and simplejson.loads(json);
    cards is None or __do_merge(cards)
    return isFetch and __fetch_all_json()

def __update_todo(c):
    query = (db.todo.uuid==c['uuid'])&(db.todo.user_id==auth.user_id)
    t = db(query).select().first()
    c['last_update'] = str_to_datetime(c['last_update'])
    if t is None:
        db.todo.insert(**c)
        logger.info('item inserted ' + c['text'])
    elif c['last_update'] >= t.last_update:   # in case 'todo' was updated from diff places
        t.update_record(**c)
        logger.info('item updated ' + c['text'])

def __delete_todo(c):
    query = (db.todo.uuid==c['uuid'])&(db.todo.user_id==auth.user_id)
    t = db(query).select().first()
    if not t is None:
        c['last_update'] = str_to_datetime(c['last_update'])
        c['deleted'] = True
        t.update_record(**c)
        logger.info('item delted ' + c['text'])

def __do_merge(cards):
    cards = filter(lambda c: c.has_key('uuid') and c['state'] != 'updated', cards)
    changed_todos = filter(lambda x: x['state'] == 'changed', cards)
    deleted_todos = filter(lambda x: x['state'] == 'deleted', cards)

    def delete_state(todo):
        del todo['state']
    map(delete_state, cards)
    map(__update_todo, changed_todos)
    map(__delete_todo, deleted_todos)

