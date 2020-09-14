from django_redis import get_redis_connection
import json

DEFAULT_INFO_KEY = 'oscar:userinfo'
DEFAULT_TOKEN = 'oscar:token'

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
        return rs['name'], rs['email'], rs['passward']
    else:
        return []