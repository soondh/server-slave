from flask import render_template

from services.services_info import CheckServcie, DingServer
from utils.basecode import BaseView, RespAdapter


class Check(BaseView):
    def post(self):
        data = CheckServcie().testapi()
        res = False
        if data == 1:
            res = {"cd": self.Error_code, "msg": "参数不全", "data": {"result": []}}
        elif data == 2:
            res = {"cd": self.Error_code, "msg": "无此项目", "data": {"result": []}}
        elif data == 3:
            res = {"cd": self.Error_code, "msg": "与脚本服务器通信失败", "data": {"result": []}}
        elif data == 4:
            res = {"cd": 0, "msg": "该项目无脚本", "data": {"result": []}}
        elif data == 5:
            res = {"cd":0, "msg": "脚本检验已全部关闭", "data": {"result": []}}
        if res:
            data = RespAdapter.make_resp_for_client(res)
            return data
        data, hid = data
        data = {"cd": 0, "msg": "", "data": {"result": data, "hid": hid}}
        data = RespAdapter.make_resp_for_client(data)
        return data


class DingDing(BaseView):
    def get(self):
        data = DingServer().testmsg()
        return self.jscode()

    def post(self):
        data = DingServer().sendmsg()
        return self.jscode()
class Index(BaseView):
    def get(self):
        render_template('index.html')