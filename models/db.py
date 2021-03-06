db = DAL('sqlite://storage.sqlite')

from gluon.tools import *
auth = Auth(db)
crud = Crud(db)

#auth.settings.extra_fields['auth_user']= [Field('username', required=True, comment='(only your username is public)')] 

db.define_table('users',Field('username',required=True),Field('created_on','datetime',default=request.now),Field('bucks','integer',default=100))

db.define_table('bounties',Field('one_liner','text'),Field('description','text'),Field('creator_id','integer'),Field('community'),Field('subgroup1'),Field('subgroup2'),Field('created_on','datetime',default=request.now))

db.define_table(
    auth.settings.table_user_name,
    Field('first_name',default='x',readable=False,writable=False),
    Field('last_name',default='x',readable=False,writable=False),
    Field('username',length=128),
    Field('bucks','integer',default=100,readable=False,writable=False),
    Field('email', length=128, default='', unique=True), # required
    Field('password', 'password', length=512,            # required
          readable=False, label='Password'),
    Field('about','text'),
    Field('registration_key', length=512,                # required
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,              # required
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,                 # required
          writable=False, readable=False, default=''))

## do not forget validators
custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.password.requires = [IS_STRONG(), CRYPT()]
custom_auth_table.email.requires = [
  IS_EMAIL(error_message=auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table
db.define_table('tags',Field('tag',required=True),Field('creator_id',db.auth_user),Field('bounty_id','reference bounties'))

db.define_table('plugs',Field('bounty_id','reference bounties'),Field('comment',required=True),Field('link',required=True,requires=IS_URL()),Field('upvotes','integer',default=0),Field('creator_id',db.auth_user))

db.define_table('upvotes',Field('plug_id','reference plugs'),Field('bounty_id','reference bounties'),Field('user',db.auth_user),Field('created_on','datetime',default=request.now)) 
                                
auth.define_tables(username=True, signature=True, migrate=True)
