def index():
    community = None
    subgroup1 = None
    subgroup2 = None
    query1 = query2 = query3 = None
    
    if request.args:
        if len(request.args)==1:
            query1 = db.bounties.community == request.args[0]
            if len(request.args)==2:
                query2 = db.bounties.subgroup1 = request.args[1]
                if len(request.args)==3:
                    query3 = db.bounties.subgroup2 = request.args[2]
        
    if query3: 
        bounties = db(query1 & query2 & query3).select(orderby=~db.bounties.created_on)
    elif query2:
        bounties = db(db.bounties.id>0 & query1 & query2).select(orderby=~db.bounties.created_on)
    elif query1:
        bounties = db(query1).select(orderby=~db.bounties.created_on)
    else:
        bounties = db(db.bounties.id>0).select(orderby=~db.bounties.created_on)
        
    return dict(bounties=bounties)

def delete():
    if not auth.user:
        redirect('index')
    
    bounty_id = None
    plug_id = None
    
    if 'bounty_id' in request.vars:
        bounty_id = request.vars.bounty_id
        bounty_record = db(db.bounties.id == bounty_id).select()[0]
            
    if 'plug_id' in request.vars:
        plug_id = request.vars.plug_id
        plug_record = db(db.plugs.id == plug_id).select()[0]
        
        if auth.user.id == plug_record.creator_id:
            db(db.plugs.id == plug_id).delete() 
            
        redirect(URL('spotlight',vars=dict(id=bounty_id)))          
        
    else:
        if auth.user.id == bounty_record.creator_id:
            db(db.bounties.id == bounty_id).delete()
    
    redirect(URL('index'))

    
def test():
    #db.plugs.drop()
    blah = 'blah'
    plug_record = db(db.plugs.id>0).select()[0]
    submitted_by = plug_record.creator_id
    bucks = submitted_by.bucks
               
    return dict(blah=bucks)

def upvote():
    bounty_id = request.vars.bounty_id
    plug_id = request.vars.plug_id
    user = request.vars.user
    bounty_record = db(db.bounties.id == bounty_id).select()[0]
    plug_record = db(db.plugs.id==plug_id).select()[0]
    upvotes = plug_record.upvotes
    
    # check if user has already upvoted a plug
    if (db( (db.upvotes.user==auth.user.id) & (db.upvotes.plug_id==plug_id) ).count() ==0) and (auth.user.id != plug_record.creator_id):
        plug_record.update_record(upvotes=upvotes+1)
        db.upvotes.validate_and_insert(plug_id=plug_id,bounty_id=bounty_id,user=auth.user.id)
        
        # give points to the person who submitted it, 
        submitted_by = plug_record.creator_id
        bucks = submitted_by.bucks
        submitted_by.update_record(bucks=bucks+100)
      
    upvotes = plug_record.upvotes
    
    return upvotes
    
def spotlight():
    
    if 'id' in request.vars:
        record_id = request.vars.id
        
        bounties = db(db.bounties.id==record_id).select()
    else:
        if db(db.bounties.id>0).count() ==0:
            redirect(URL('index'))
        else:
            bounties = db(db.bounties.id>0).select(limitby=(0,20),orderby=~db.bounties.created_on)
               
    form = SQLFORM.factory(Field('comment',requires=IS_NOT_EMPTY()),Field('link',requires=IS_NOT_EMPTY()),Field('record_id','integer',readable=False))        
    if form.process().accepted:
        
        if not auth.user:
            redirect(URL('user',args='login'))
        else:
            db.plugs.validate_and_insert(comment=form.vars.comment,link=form.vars.link,bounty_id=form.vars.record_id, creator_id=auth.user.id)
        if form.vars.record_id: 
            redirect(URL('spotlight',vars=dict(id=form.vars.record_id)))
        else:
            redirect(URL('spotlight'))
                                                                                                                   
    return dict(result=bounties,form=form)
        
def register():
     session.flash = "Hello, World!"
     return dict(form=auth.register())
    
@auth.requires_login()    
def submit():
    community = None
    subgroup1 = None
    subgroup2 = None
    
    if request.args:
        if len(request.args)>0: 
            community = request.args[0]
            if len(request.args)>1: 
                subgroup1 = request.args[1]
                if len(request.args)>2: 
                    subgroup2 = request.args[2]   
    
    tags = []
    form = SQLFORM.factory(Field('one_liner',requires=IS_NOT_EMPTY()))
        
    if form.process().accepted:
        ret = db.bounties.validate_and_insert(one_liner=form.vars.one_liner,description=form.vars.description,creator_id=auth.user.id,community=community,subgroup1=subgroup1,subgroup2=subgroup2)
        
        new_bounty_id = ret.id
        if form.vars.tags:
            for x in form.vars.tags.split(","):
                tags.append(x.strip())        
        
        if len(tags)>0:
            for t in tags:
                db.tags.validate_and_insert(tag=t,creator_id=auth.user.id,bounty_id=new_bounty_id)    
                
        redirect(URL('index'))

    return dict(form=form)
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
