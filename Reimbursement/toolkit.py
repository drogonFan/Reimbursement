import hashlib

def password_hash(password):
    '''
    To ensure security, use a hash value to store passwords.
    '''
    hash = hashlib.md5()                    #使用md5
    hash.update(password.encode('utf-8'))   #计算密码hash值
    return hash.hexdigest()                 #返回密码的hash值

def validate_password(password, w_hash):
    '''
    Verify that the password is correct
    '''
    return w_hash == password_hash(password) #判断当前输入值与密码的hash值是否匹配