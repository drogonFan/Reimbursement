DEFAULT_STUDENT = {
    # 博士
    '11617006' : '刘东',
    '11617002' : '高国军',
    '11717007' : '唐艺璇',
    '11717010' : '周志德',
    '11917009' : '涂浩新',
    '12017014' : '王尊',
    # 研三
    '21817056' : '马钊',
    '21817053' : '董绍正',
    '21817047' : '陈昊',
    # 研二
    '21917053' : '范晓飞',
    '21917046' : '孙世伟',
    '31917084' : '王安琪',
    '21917054' : '郭亚琳',
    '21917057' : '李康乐',
    '31917043' : '赵栖栖',
    '41917049' : '邹鑫',
    # 研一
    '22017066' : '王栎',
    '32017060' : '王笑爽',
    '22017065' : '陈乐',
    '22017017' : '卢凌',
    '22017061' : '陈时非',

    '21592075' : '管理员',
}

DEFAULT_ADMINSTRATOR = ['21592075']

DEFAULT_SIGNUP_EMAIL_URL = 'www.oscar-lab.cn:9999/verify/?ssid='

def verify_student(ssid, name):
    if ssid is None or name is None:
        return 101, 'No permission to register'
    elif ssid not in DEFAULT_STUDENT.keys():
        return 102, 'Please check if the student ID is correct'
    elif name != DEFAULT_STUDENT[ssid]:
        return 103, 'Please check if the name is correct'
    else:
        return 0, 'Verified successfully' 