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

def _fetch_all_json():
    logger.log(32, 'fetching items')
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

@auth.requires_login()
def merge():
    logger.log(32, 'start merging')
    cards = simplejson.loads(request.vars.json);
    cards is None or _do_merge(cards)
    return _fetch_all_json()
  
def _add_defaut_tips():
    tip_count = db(db.tip.user_id==auth.user_id).count()
    if tip_count == 0: 
        logger.log(32, 'add defaut tips for user %s' % auth.user.email)
        default_tips = db(db.meta_tip.expired_date < datetime(3,3,3)).select()
        db.tip.bulk_insert([{'meta_tip_id': t.id} for t in default_tips])

def _add_new_tips():
    query = (db.meta_tip.expired_date > datetime.now()) & (db.tip.user_id == auth.user_id) \
                & (db.tip.meta_tip_id == db.meta_tip.id)
    
    added_tip_ids = map(lambda t: t.id, db(query).select(db.meta_tip.id))
    unexpried_tips = db(db.meta_tip.expired_date > datetime.now()).select(db.meta_tip.ALL)
    fresh_tips = filter(lambda t: not t.id in added_tip_ids, unexpried_tips)
    db.tip.bulk_insert([{'meta_tip_id': t.id} for t in fresh_tips])

