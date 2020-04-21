import json

import requests
from flask import request

from models import User
from utils.basecode import RequestSelf
from utils.make_token import Token_info


class UserService(RequestSelf):
    def login(self):
        QASESSIONID = request.cookies.get('QASESSIONID')
        try:#与账号中心通信
            data = requests.get('http://10.225.136.151:33102/sso/checkLogin?needJsonp=False',
                                cookies={'QASESSIONID': QASESSIONID})
        except:
            return 2
        judge = data.content.decode()
        judge = json.loads(judge)
        cd = judge.get('cd', False)
        if cd:#根据账号中心返回的code进行判断
            return 1
        try:
            name = judge['data']['username']
            email = judge['data']['email']
        except:
            return 1
        try:
            user = User.query.filter_by(isDelete=False, name=name).first()
        except:
            user = False
        if not user:
            user = User()
            user.name = name
            user.email = email
            self.create(user)
        try:
            power = user.power
            userId = user.id
        except:
            power = 2
            userId = 0
        info = str({'userId': userId, 'name': name, 'power': power})
        # pk为sso验证获得的用户id
        # userId为用户在本项目中的ID
        data = {'token': Token_info.get_encrypt(info), 'userId': userId, 'name': name, 'power': power}
        return data
