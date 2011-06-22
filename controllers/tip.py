

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

@auth.requires_login()
def fetch():
    _add_defaut_tips()
    _add_new_tips()

    query = (db.tip.user_id == auth.user_id) & (db.tip.meta_tip_id == db.meta_tip.id) \
                & (db.tip.has_viewed == False)
    fresh_tips = db(query).select()
    json = [{
        'id': row.meta_tip.id,
        'text': row.meta_tip.text
    } for row in fresh_tips]
    return simplejson.dumps(json)


