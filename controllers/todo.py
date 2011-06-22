#-*- coding: utf8 -*-
import logging
from gluon.contrib import simplejson
from datetime import datetime

logger = logging.getLogger("[todo]")

@auth.requires_login()
def index(): 
    logger.log(32, auth.user_id)
    return dict()

def _to_datetime(s):
    logger.log(32, s)
    import re
    t = [int(x) for x in re.findall(r"(.*)-(.*)-([0-9]*) (.*):(.*):([0-9]*)", s)[0] \
         if len(x) > 0]
    return datetime(*t)

def _insert_welcome_todos():
    welcome_todos = [ {'text': "<p><i>Welcome to</i></p><h2>Taskboard 10k</h2>", 
               'type': 'white', 'marginTop': 0.0916, 'marginLeft': 0.1054 },
        {'text': "Need a new card? Just grab it from a deck on the left",
               'type': 'yellow', 'marginTop': 0.2122, 'marginLeft': 0.13125 },
        {'text': "<p><b>Have fun!</b></p>",
               'type': 'green', 'marginTop': 0.3328, 'marginLeft': 0.2008  }]
    import uuid
    for t in welcome_todos:
        t['uuid'] = uuid.uuid4()
        db.todo.insert(**t)

def _fetch_all_json():
    logger.log(32, 'fetching items')

    todo_count = db(db.todo.user_id==auth.user_id).count()
    if todo_count  == 0:
        logger.log(32, 'insert welcome todos')
        _insert_welcome_todos()

    logger.log(32, "fetch user\'s todos")
    query = (db.todo.isDeleted==False)&(db.todo.user_id==auth.user_id)
    todos = db(query).select()
    json = []
    for t in todos:
        json += [{
            'uuid': t.uuid,
            'lastUpdate': t.lastUpdate.strftime("%Y-%m-%d %H:%M:%S"),
            'state': 'updated',
            'type': t.type,
            'marginTop': t.marginTop,
            'marginLeft': t.marginLeft,
            'text': t.text
        }]
    return simplejson.dumps(json) 

def _update_todo(c):
    query = (db.todo.uuid==c['uuid'])&(db.todo.user_id==auth.user_id)
    t = db(query).select().first()
    c['lastUpdate'] = _to_datetime(c['lastUpdate'])
    if t is None:
        db.todo.insert(**c)
        logger.log(32, 'item inserted ' + c['text'])
    elif c['lastUpdate'] >= t.lastUpdate:   # in case 'todo' was updated from diff places
        t.update_record(**c)
        logger.log(32, 'item updated ' + c['text'])

def _delete_todo(c):
    query = (db.todo.uuid==c['uuid'])&(db.todo.user_id==auth.user_id)
    t = db(query).select().first()
    if not t is None:
        c['lastUpdate'] = _to_datetime(c['lastUpdate'])
        c['isDeleted'] = True
        t.update_record(**c)
        logger.log(32, 'item delted ' + c['text'])

def _do_merge(cards):
    cards = filter(lambda c: c.has_key('uuid') and c['state'] != 'updated', cards)
    changed_todos = filter(lambda x: x['state'] == 'changed', cards)
    deleted_todos = filter(lambda x: x['state'] == 'deleted', cards)

    def _delete_state(todo):
        del todo['state']
    map(_delete_state, cards)
    map(_update_todo, changed_todos)
    map(_delete_todo, deleted_todos)

def _merge(isFetch=False):
    logger.log(32, 'start merging')
    json = request.vars.json 
    cards = json and simplejson.loads(request.vars.json);
    cards is None or _do_merge(cards)
    return isFetch and _fetch_all_json()

@auth.requires_login()
def fetch():
    logger.log(32, 'user %d login, fetching data')
    return _merge(True)

@auth.requires_login()
def update():
    logger.log(32, 'update data')
    _merge()
    
