import datetime, random

def num(s):
    try:
        return int(s)
    except ValueError:
        return None

def generate_session_id():
	return str(random.randint(1,2000)) + 'test'

def get_salted_password(password):
	return password + 'sajd134kj2rv423J2z3@$#mnfmdj3m2Dn3ehfjdnklm$@#REKGlhjkJFDcdsjkh'
