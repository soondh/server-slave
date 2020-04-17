import base64
import json
from functools import wraps

import requests
import rsa
from flask import request, jsonify

from models import User, ProjectUser


class Token_info(object):
    @classmethod
    def get_encrypt(cls, info, pubfile='./utils/public.pem'):
        '''
            公钥加密，返回密文，顺便可以保存到文件
        '''
        info = info.encode()
        with open(pubfile, 'rb') as f:
            content = f.read()
        pubkey = rsa.PublicKey.load_pkcs1(content)
        s_encrypt = rsa.encrypt(info, pubkey)
        s_encrypt = base64.b64encode(s_encrypt).decode()
        return s_encrypt

    @classmethod
    def get_decrypt(cls, info, prifile='./utils/private.pem'):
        '''
            私钥解密，返回明文
        '''
        try:
            info = base64.b64decode(info.encode())
            with open(prifile, 'rb') as f:
                content = f.read()
            prikey = rsa.PrivateKey.load_pkcs1(content)
            s_decrypt = rsa.decrypt(info, prikey).decode()
        except:
            return False
        return eval(s_decrypt)


# 权限验证

def verify(index=0):
    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            try:
                token = request.headers['token']
                flag = Token_info.get_decrypt(token)
                QASESSIONID = request.cookies.get('QASESSIONID', None)
                if not QASESSIONID:
                    return jsonify({'cd': 1, 'msg': '登录失败，请重新登录', 'data': {}})
                try:
                    data = requests.get('http://10.225.136.151:33102/sso/checkLogin?needJsonp=False',
                                        cookies={'QASESSIONID': QASESSIONID})
                except:
                    return jsonify({'cd': 1, 'msg': '与服务器通信失败请重新尝试', 'data': {}})
                judge = data.content.decode()
                judge = json.loads(judge)
                cd = int(judge.get('cd', 1))
                if cd:
                    return jsonify({'cd': 1, 'msg': 'sso验证失败', 'data': {}})
                if not flag:
                    return jsonify({'cd': 1, 'msg': 'token失效', 'data': {}})
            except:
                return jsonify({'cd': 1, 'msg': 'token失效', 'data': {}})
            self.judge = flag
            if index:
                use = User.query.filter_by(name=flag['name']).first()
                if not use:
                    return jsonify({'cd': 1, 'msg': '用户不存在', 'data': {}})
                if use.power != index and use.power != 1:
                    return jsonify({'cd': 1, 'msg': '权限不足', 'data': {}})
            return func(self, *args, **kwargs)

        return inner

    return wrapper


def verproject(judge, projectid,flag=False):
    userId = judge.get('userId', 0)
    if not userId:
        return False
    user = User.query.filter_by(isDelete=False, id=userId).first()
    if not user:
        return False
    userid = user.id
    if flag:
        if user.power == 1 or user.power == 2:
            return True
    else:
        if user.power == 1:
            return True
    try:
        flag = ProjectUser.query.filter_by(isDelete=False, projectid=projectid, userid=userid).first().isAdmin
    except:
        return False
    if not flag:
        return False
    return True

# 创建公钥与私钥的方法
# (pubkey, privkey) = rsa.newkeys(1024)
#
# pub = pubkey.save_pkcs1()
# pubfile = open('public.pem','wb')
# pubfile.write(pub)
# pubfile.close()
#
# pri = privkey.save_pkcs1()
# prifile = open('private.pem','wb')
# prifile.write(pri)
# prifile.close()
