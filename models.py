from peewee import *
import datetime

#db = MySQLDatabase(host="localhost", database="pay", user="root", passwd="cdc")
db = SqliteDatabase('app.db')

def db_init():
    db.connect()
    try:
        db.create_tables([User, Card, Transaction, Session,])
        print('Creating tables...')
    except (OperationalError, InternalError):
        pass
    db.close()

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    first_name = CharField(null=False)
    last_name = CharField(null=False)
    email = CharField(null=False)
    balance = DecimalField(default=0)
    password = CharField()

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

class Session(BaseModel):
	user = ForeignKeyField(User, null=True)
	session_id = CharField()
	active = BooleanField(default=True)

class Card(BaseModel):
	name = CharField(null=False)
	user = ForeignKeyField(User)
	number = CharField(null=False)
	pin = CharField(null=False)
	expires = DateTimeField(default=datetime.datetime.now()+datetime.timedelta(days=600))

class Transaction(BaseModel):
    user = ForeignKeyField(User)
    dest = CharField()
    txid = CharField()
    amount = DecimalField(default=0)
    paid = BooleanField(default=False)
    date = DateTimeField(default=datetime.datetime.now())
