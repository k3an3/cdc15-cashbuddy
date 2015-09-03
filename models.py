from peewee import *
import datetime

#db = MySQLDatabase(host="localhost", database="pay", user="root", passwd="cdc")
db = SqliteDatabase('app.db')

def db_init():
    db.connect()
    try:
        db.create_tables([User,
            Card,
            Transaction,
            Session,
            Comment,
            Catchphrase])
        print('Creating tables...')
    except (OperationalError, InternalError):
        pass
    db.close()

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(null=False)
    balance = IntegerField(default=0)
    password = CharField()

class Session(BaseModel):
	user = ForeignKeyField(User, null=True)
	session_id = CharField()
	active = BooleanField(default=True)

class Card(BaseModel):
	user = ForeignKeyField(User)
	number = CharField(null=False)
	expires = DateTimeField(default=datetime.datetime.now()+datetime.timedelta(days=600))

class Transaction(BaseModel):
    user = ForeignKeyField(User)
    dest = CharField()
    txid = CharField()
    amount = DecimalField(default=0)
    paid = BooleanField(default=False)
    date = DateTimeField(default=datetime.datetime.now())

class Comment(BaseModel):
    text = TextField()

class Catchphrase(BaseModel):
    text = TextField()
