from django_redis import get_redis_connection
import json
import os
import uuid

DEFAULT_INFO_KEY = 'oscar:userinfo'
DEFAULT_TOKEN = 'oscar:token:'
DEFAULT_INVOICE_NUM = 'oscar:invoice:num'

DEFAULT_BASKET = 'oscar:basket'


con = get_redis_connection("default")


def add_student_info(ssid, name, email, passward):
    info = {
        'ssid' : ssid,
        'name' : name,
        'email' : email,
        'passward' : passward,
    }
    con.hset(DEFAULT_INFO_KEY, ssid, json.dumps(info))

def get_student_info(ssid):
    rs = con.hget(DEFAULT_INFO_KEY, ssid)
    if rs is not None:
        infos = json.loads(rs)
        return infos['name'], infos['email'], infos['passward']
    else:
        return []

def gen_token():
    return uuid.uuid4().hex

def get_token(ssid):
    token = gen_token()
    con.set(DEFAULT_TOKEN + ssid, token)
    con.expire(DEFAULT_TOKEN + ssid, 3600 * 2)
    return token
    
def verify_token(ssid, token):
    save_token = con.get(DEFAULT_TOKEN + ssid).decode('utf-8')
    if save_token == None or len(save_token) == 0:
        return False
    else:
        return token == save_token

def get_invoice_num():
    return con.incr(DEFAULT_INVOICE_NUM)

def can_new_basket():
    num = get_basket_num()
    if num == 0:
        return True
    else:
        return False

def get_basket_num():
    return int(con.get(DEFAULT_BASKET))

def record_basket_num(num):
    con.set(DEFAULT_BASKET, num)
