from peewee import *
import datetime

#db = MySQLDatabase(host="localhost", database="pay", user="root", passwd="cdc")
db = SqliteDatabase('app.db')

def db_init():
    db.connect()
    try:
        db.create_tables([User, Card, Transaction])
        print('Creating tables...')
    except OperationalError:
        pass
    db.close()

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    first_name = CharField(null=False)
    last_name = CharField(null=False)
    email = CharField(null=False)
    balance = IntegerField(default=0)
    password = CharField()

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

class Card(BaseModel):
    user = ForeignKeyField(User, related_name='card')
    number = CharField(null=False)
    pin = CharField(null=False)

class Transaction(BaseModel):
    user = ForeignKeyField(User, related_name='transaction')
    txid = CharField()
    amount = IntegerField(default=0)
    paid = BooleanField(default=False)
