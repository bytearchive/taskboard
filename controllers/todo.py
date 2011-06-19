#-*- coding: utf8 -*-
import logging
from gluon.contrib import simplejson
from datetime import datetime

logger = logging.getLogger("[todo]")


def index(): 
    return dict()

def _to_datetime(s):
    logger.log(32, s)
    import re
    t = [int(x) for x in re.findall(r"(.*)-(.*)-([0-9]*) (.*):(.*):([0-9]*)", s)[0] \
         if len(x) > 0]
    return datetime(*t)

def _fetch_all_json():
    logger.log(32, 'fetching items')
    todos = db().select(db.todo.ALL)
    json = []
    for t in todos:
        json += [{
            'uuid': t.uuid,
            'lastUpdate': t.lastUpdate.strftime("%Y-%m-%d %H:%M:%S"),
            'state': 'updated',
            'type': t.type,
            'top': t.top,
            'left': t.left,
            'text': t.text
        }]
    return simplejson.dumps(json) 

def _update(cards):
    cards = filter(lambda c: c.has_key('uuid') and c['state'] != 'updated', cards)
    for c in cards:
        logger.log(32, c)
        state = c['state']
        del c['state']
        if state == 'changed':
            t = db.todo(uuid=c['uuid'])
            lastUpdate = _to_datetime(c['lastUpdate'])
            if t is None:
                c['lastUpdate'] = datetime.now()
                logger.info(32, 'insert')
                db.todo.insert(**c)
            elif lastUpdate >= t.lastUpdate:   # in case 'todo' was updated from diff places
                c['lastUpdate'] = lastUpdate
                t.update_record(**c)
    logger.log(32, 'items saved')

def merge():
    logger.log(32, 'start merging')
    cards = simplejson.loads(request.vars.json);
    cards is None or _update(cards)
    return db.todo.id.count() > 0 and _fetch_all_json() or dict()
    
def load():
    #a = {'type':'orange', 'top':50, 'left':100, 'text':'a note from server #server'}
    cards = [] 
    json = simplejson.dumps(cards)
    logger.log(32, 'item loaded')
    return json

