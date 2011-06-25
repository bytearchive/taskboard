from gluon.contrib import simplejson
from datetime import datetime

@auth.requires_login()
def fetch():
    query = (db.meta_tip.expired_date > datetime.now()) & (db.meta_tip.id == db.viewed_tip.meta_tip_id) \
            & (db.viewed_tip.user_id == auth.user_id) 
    unexpried_viewed_ids = map(lambda t: t.id, db(query).select(db.meta_tip.id))
    unexpried_tips = db(db.meta_tip.expired_date > datetime.now()).select(db.meta_tip.ALL)
    fresh_tips = filter(lambda t: not t.id in unexpried_viewed_ids, unexpried_tips)
    json = [{
        'id': t.id,     # meta_tip's id
        'text': t.text, 
    } for t in fresh_tips]
    return simplejson.dumps(json)

@auth.requires_login()
def delete():
    meta_tip_id = int(request.args(0))
    db.viewed_tip.insert(meta_tip_id=meta_tip_id)
    logger.info('tip [%d]: deleted', meta_tip_id)

