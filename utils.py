import datetime, random

def num(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0

def generate_session_id():
    return str(random.randint(1,2000)) + 'test'

def get_salted_password(password):
    if password:
        return password + 'sajd134kj2rv423J2z3@$#mnfmdj3m2Dn3ehfjdnklm$@#REKGlhjkJFDcdsjkh'
    return None

def get_hashed_password(password):
    if password:
        return '#' + password
    return None

def get_password(password):
    if password:
        return get_hashed_password(get_salted_password(password))
    return None
