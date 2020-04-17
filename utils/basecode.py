import base64
import json
import os
import re
import shutil
import zipfile
from datetime import datetime
import time

from flask import request
from flask_restful import Resource
from dateutil import parser

from config import Config
from models import db
from fdfs_client.client import Fdfs_client

class BaseView(Resource):
    Error_code = 1
    Right_code = 0

    def jscode(self, code=Right_code, msg='', num=0, data='', datainfo=None):
        if data is '':
            data = {}
        if datainfo:
            data = {'cd': code, 'msg': msg, 'num': len(data), 'data': data}
        else:
            data = {'cd': code, 'msg': msg, 'data': data}
        if datainfo:
            data['datainfo'] = datainfo
        return data

    @classmethod
    def totime(cls, *args):
        time_obj = [parser.parse(i) for i in args]
        return time_obj

    def timetotime(self, date):
        try:
            timeStamp = (date) / 1000
        except:
            return 0
        timeArray = time.gmtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        date = datetime.strptime(otherStyleTime, "%Y-%m-%d")
        return date


class RequestSelf(object):
    def __init__(self):
        self.savepath = Config.BASE_DIR + '/file'
        self.client = Fdfs_client('./utils/client.conf')
        self.fastdfs = '''http://10.225.136.172:8889/'''
    def getargs(self):
        args = request.args.to_dict()
        return args

    def getbody(self):
        data = request.data.decode()
        return data

    def getjson(self):
        try:
            data = request.json
        except:
            data = {}
        return data
    def all_path(self, dirname):
        result = []
        for maindir, subdir, file_name_list in os.walk(dirname):
            for filename in file_name_list:
                if not filename.endswith('py'):
                    continue
                apath = os.path.join(maindir, filename)
                result.append(apath)
        return result

    def savefile(self, path, content):
        content = base64.b64decode(content.encode())
        os.makedirs(os.path.dirname(path), exist_ok=True)
        savepath = os.path.join(path)
        with open(savepath, 'wb') as f:
            f.write(content)
        return savepath

    def create(self, obj):
        try:
            obj.createTime = datetime.now()
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            print(str(e))
            db.session.rollback()

    def update(self, obj):
        try:
            try:
                obj.updateTime = datetime.now()
                db.session.commit()
            except:
                db.session.commit()
        except Exception as e:
            print(str(e))
            db.session.rollback()

    def upload(self, path):
        res = self.client.upload_by_filename(path)
        return res
    def download(self,localpath,file_id):
        res = self.client.download_to_file(local_filename=localpath,remote_file_id=file_id)
        return res
    def verip(self,ip):
        try:
            ip,port = ip.split(":")
        except:
            return False
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if not p.match(ip):
            return False
        try:
            port = int(port)
        except:
            return False
        if port>65535 or port < 1000:
            return False
        return True
    @staticmethod
    def _fileback(uid,name,file):
        file_dir = os.path.join('./file', str(uid),name)
        shutil.copy(file, file_dir)

    @staticmethod
    def zipDir(dirpath, outFullName):

        """
        压缩指定文件夹
        :param dirpath: 目标文件夹路径
        :param outFullName: 压缩文件保存路径+xxxx.zip
        :return: 无
        """
        zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(dirpath):
            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
            fpath = path.replace(dirpath, '')
            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()



class RespAdapter(object):

    @classmethod
    def make_resp_for_client(cls, original_resp_dict):
        """
        original_resp_dict such as:
{
    'cd': 0,
    'msg': '',
    'data': {
        'result': [
            {
                'msg': [
                    {'msg': '', 'cd': 1, 'error': ''},
                    {'msg': '', 'cd': 1, 'error': ''},
                    {'msg': '', 'cd': 0, 'error': "name 'fg' is not defined"},
                    {'msg': '', 'cd': 0, 'error': "name 'fg' is not defined"}
                ],
                'scrname': 'test.py',
                'syserror': ''
            }
        ],
        'snapshot': {
        }
    }
}
        """
        resp = original_resp_dict  # here pay attention # 浅拷贝，会修改原始的 original_resp_dict

        # master 是否允许通过
        master_permit = True if resp['cd'] == 0 else False
        master_msg = resp['msg']

        # 在执行py文件时，是否存在任何脚本异常
        any_py_error = False
        msg_py_error = ''
        for each_py_result in resp['data']['result']:
            if each_py_result['syserror'] != '':  # 这表明：slave执行该py文件时发生异常（亦即 stderr 标准错误流中有输出）
                any_py_error = True
                temp = '%s %s \n' % (each_py_result['scrname'], each_py_result['syserror'])
                msg_py_error = msg_py_error + temp

        # 在try-catch执行py文件中的每个testfunc函数时，是否捕获到任何异常
        any_py_func_error = False
        msg_py_func_error = ''
        for each_py_result in resp['data']['result']:
            if each_py_result['syserror'] == '':  # 这表明：slave执行该py文件正常
                temp = ''
                for i in range(0, len(each_py_result['msg'])):
                    if each_py_result['msg'][i]['error'] != '':  # 这表明：slave执行该py文件正常，但是testfunc函数执行时try-catch捕获到异常
                        any_py_func_error = True
                        temp = temp + ">>" + each_py_result['msg'][i]['error'] + '   ' + '\n'
                temp = temp.strip()
                if temp != '':
                    temp = '%s \n' % (temp)
                    msg_py_func_error = msg_py_func_error + temp

        # py文件中的每个testfunc函数，是否全部允许通过
        all_py_func_permit = True
        msg_py_func_permit = ''
        msg_py_func_permit_list = []
        for each_py_result in resp['data']['result']:
            if each_py_result['syserror'] == '':  # 这表明：slave执行该py文件正常
                for i in range(0, len(each_py_result['msg'])):
                    if each_py_result['msg'][i]['cd'] != 0:  # 这表明：slave执行该py文件正常，但是该testfunc函数认为： 不允许通过
                        all_py_func_permit = False
                        if each_py_result['msg'][i]['msg'] != '':
                            msg_py_func_permit_list.append(each_py_result['msg'][i]['msg'])
        for item in msg_py_func_permit_list:
            msg_py_func_permit = msg_py_func_permit + item + '\n'
        msg_py_func_permit = msg_py_func_permit.strip()

        resp['data']['snapshot'] = {}
        resp['data']['snapshot']['master_permit'] = master_permit
        resp['data']['snapshot']['any_py_error'] = any_py_error
        resp['data']['snapshot']['any_py_func_error'] = any_py_func_error
        resp['data']['snapshot']['all_py_func_permit'] = all_py_func_permit
        if not master_permit:
            resp['data']['snapshot']['permit'] = False
            resp['data']['snapshot']['info'] = master_msg
        elif any_py_error:
            resp['data']['snapshot']['permit'] = False
            resp['data']['snapshot']['info'] = msg_py_error
        elif any_py_func_error:
            resp['data']['snapshot']['permit'] = False
            resp['data']['snapshot']['info'] = msg_py_func_error
        else:
            if all_py_func_permit:
                resp['data']['snapshot']['permit'] = True
                resp['data']['snapshot']['info'] = str(msg_py_func_permit_list).replace(' ', '')
            else:
                resp['data']['snapshot']['permit'] = False
                resp['data']['snapshot']['info'] = str(msg_py_func_permit_list).replace(' ', '')
        return resp


import requests
class DingDingBot(object):
    def __init__(self):
        self.url = "https://oapi.dingtalk.com/robot/send"
    def __send(self,at_mobiles,post_string,token):
        data = {
            'msgtype': 'markdown',
            "markdown": {"title":"检查平台",
                'text': '%s' % post_string
            },
            "at": {"atMobiles": at_mobiles, "isAtAll": 'false'}
        }
        params = {'access_token':token}
        data = requests.post(self.url,json=data,params=params)
    def run(self,post_string,token, at_mobiles=False):
        at_mobiles = []
        self.__send(at_mobiles,post_string,token)

