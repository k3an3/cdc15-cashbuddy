from models import *
from utils import *

db_init()
u = User.create(first_name="Tester", last_name="Test", email="test@test.com", password=get_hashed_password(get_salted_password('test')), balance=10000)
c = Card.create(name="Visa", user=u, number="8675-3098-2857-3298", pin="123")
c1 = Card.create(name="Discover", user=u, number="7390-2571-9385-7193", pin="249")
t = Transaction.create(user=u, amount=9.99, dest="Loogle", paid=True, txid="43rtgfb")
t1 = Transaction.create(user=u, amount=500, dest="Safari LLC", paid=True, txid="sfadf23")
t2 = Transaction.create(user=u, amount=17.67, dest="Coldway Bakery", paid=False, txid="wereufvn")
Catchphrase.create(text="The freedom to pay anywhere without worry. We've got you covered.")
Catchphrase.create(text="If it's not CashBuddy, it's not secure.")
Catchphrase.create(text="If it's not secure, it's not CashBuddy.")
Catchphrase.create(text="Security is our middle name.")
Catchphrase.create(text="Making it easier to pay, everyday.")
s = Session.create(user=u, session_id="1590test")
