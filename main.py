from flask import Flask, request, abort, render_template, redirect, make_response
from functools import wraps

from utils import *
from models import *


app = Flask(__name__)

def get_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session = None
        user = None
        try:
                session = Session.get(session_id=request.cookies.get('session_id'))
                user = session.user
        except Session.DoesNotExist:
                pass
        return f(user=user, session=session, *args, **kwargs)
    return decorated_function


@app.route("/", methods=['GET'])
@get_user
def index(*args, **kwargs):
    user = kwargs.get('user')
    try:
        catchphrase = Catchphrase.select()[random.randint(
            0, Catchphrase.select().count() - 1)]
    except ValueError:
        catchphrase = ""
    return render_template('index.html', **locals())

@app.route("/begin_transaction", methods=['GET', 'POST'])
@get_user
def begin_transaction(*args, **kwargs):
    # Get data from cookie if user just logged in
    t = request.cookies.get('transaction')
    if t:
        t = t.split('&')
        txid = t[0].split('=')[1]
        postback = t[1].split('=')[1]
        amount = num(t[2].split('=')[1])
    # Get data normally; user was already logged in
    else:
        txid = request.form.get('txid')
        postback = request.form.get('postback')
        amount = num(request.form.get('amount'))
    user = kwargs.get('user') or request.form.get('user')
    if not user:
        next_page = '/begin_transaction'
        error = "You need to sign in before you can pay."
        return render_template('login.html', **locals())
    dest = postback.split('/')[0]
    debug = request.form.get('debug')
    payment_options = Card.select().where(Card.user == user)
    response = make_response(render_template('pay.html', **locals()))
    response.set_cookie('transaction', '')
    return response

@app.route("/transaction", methods=['POST'])
@get_user
def do_transaction(*args, **kwargs):
    user = kwargs.get('user')
    txid = request.form.get('txid')
    postback = request.form.get('postback')
    amount = num(request.form.get('amount'))
    if txid and postback and amount:
        if user.balance - amount >= 0:
            user.balance -= amount
            user.save()
            Transaction.create(user=user, dest=postback.split('/')[0], txid=txid,
                    amount=amount, paid=True,
                    )
    error = "Something went wrong. Please try again. \
            If you continue to encounter issues, contact our support."
    success = True
    return render_template('pay.html', **locals())

@app.route("/validate_transaction", methods=['GET'])
def validate_transaction():
    try:
        txid = Transaction.get(txid=request.form.get('txid'))
    except Transaction.DoesNotExist:
        return 'FALSE'
    return 'TRUE' if txid.paid else 'FALSE'

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.select().where(User.username == request.form.get('username'))[0]
            password = request.form.get('password')
            if user.password == get_hashed_password(get_salted_password(password)):
                session_id = request.cookies.get('session_id', generate_session_id())
                session = Session(user=user, session_id=session_id)
                session.save()
                next_page = request.form.get('next_page')
                redir = next_page if not str(next_page) == 'None' else '/account'
                response = make_response(redirect(redir))
                response.set_cookie('session_id', session_id)
                if next_page:
                    response.set_cookie('transaction', 'txid={0}&postback={1}&amount={2}'.format(
                        request.form.get('txid'), request.form.get('postback'),
                                request.form.get('amount')))
                return response
            error = "The password is incorrect."
        except (User.DoesNotExist, IndexError):
            error = "The user doesn't exist."
    if request.args.get('registered'):
        message = "Registration complete! You may now login."
    next_page = request.args.get('next_page')
    return render_template('login.html', **locals())

@app.route("/logout", methods=['GET'])
@get_user
def logout(*args, **kwargs):
    user = kwargs.get('user')
    session = kwargs.get('session')
    session.active = False
    response = make_response(redirect('/?logout=true'))
    response.set_cookie('session_id', '', expires=0)
    return response

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = get_salted_password(request.form.get('password'))
        User.create(username=username, password=password)
        return redirect('/login?registered=true')
    return render_template('register.html', **locals())

@app.route("/account")
@get_user
def account(*args, **kwargs):
    user = kwargs.get('user')
    recent_transactions = Transaction.select().where(
        Transaction.date.day + 3 >= datetime.datetime.now().day and
        Transaction.user == user).order_by(
            Transaction.date.desc())[:6]
    cards = Card.select().where(Card.user == user)
    return render_template('account.html', **locals())

@app.route("/account/<page>", methods=['GET', 'POST'])
@get_user
def settings(*args, **kwargs):
    page = kwargs.get('page')
    user = kwargs.get('user')
    if request.args.get('delete'):
        try:
            card = Card.get(number=request.args['delete'])
        except Card.DoesNotExist:
            card = None
        if card:
            card.delete_instance()
    if request.args.get('card') == 'new':
        card = 'new'
    elif request.args.get('card'):
        try:
            card = Card.get(number=request.args['card'])
        except Card.DoesNotExist:
            card = None
    if request.method == 'POST':
        if page == 'settings':
            user.username = request.form.get('username') or user.username
            user.password = get_hashed_password(get_salted_password(request.form.get('password'))) or user.password
            user.save()
            message = 'Account details successfully updated.'
        if page == 'payment_methods':
            if card == 'new':
                card = Card.create(number=request.form.get('card_number').replace('-', ''),
                                   expires=datetime.datetime.strptime(
                                       request.form.get('expires'),'%m-%y'), user=user)
            else:
                card.number = request.form.get('card_number') or card.number
                card.expires = datetime.datetime.strptime(request.form.get('expires'),'%m-%y') or card.expires
                card.save()
            message = 'Payment methods successfully updated.'
        if page == 'send':
            rcpt_user = None
            try:
                rcpt_user = User.get(username=request.form.get('username'))
            except User.DoesNotExist:
                error = 'User not found!'
            amount = num(request.form.get('amount'))
            if rcpt_user and amount:
                rcpt_user.balance += amount
                user.balance -= amount
                rcpt_user.save()
                user.save()
                Transaction.create(user=user, dest=rcpt_user.username, txid='internal', amount=amount, paid=True)
                Transaction.create(user=rcpt_user, dest="From " + user.username, txid='internal', amount=amount, paid=True)
                message = 'Money was sent successfully and deducted from your account.'
    cards = Card.select().where(Card.user == user)
    return render_template('account.html', **locals())

@app.route("/about/<path:page>")
@get_user
def homepage(**kwargs):
    user = kwargs.get('user')
    page = kwargs.get('page')
    comments = Comment.select()
    return render_template(page + '.html', **locals())

@app.route('/post_testimonial', methods=['POST'])
def post_testominial():
    if request.form.get('comment'):
        return str(Comment.create(text=request.form.get('comment')))

@app.route("/test_postback", methods=["POST"])
def test_postback():
    return request.form.get('txid') + ' ' + request.form.get('paid')

@app.route('/debug')
def shell():
    return None

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    db.connect()

# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


if __name__ == "__main__":
    app.debug = True
    db_init()
    app.run(host='0.0.0.0')
