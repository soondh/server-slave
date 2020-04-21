from flask import render_template, make_response, send_from_directory, request

from services.services_info import CheckServcie, DingServer
from utils.basecode import BaseView, RespAdapter


class Check(BaseView):
    def post(self):
        #pre-commit
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
            #执行未出现问题时执行逻辑
            data = RespAdapter.make_resp_for_client(res)
            return data
        data, hid = data
        data = {"cd": 0, "msg": "", "data": {"result": data, "hid": hid}}
        data = RespAdapter.make_resp_for_client(data)
        return data


class DingDing(BaseView):
    def get(self):
        #测试消息，忽略
        data = DingServer().testmsg()
        return self.jscode()

    def post(self):
        data = DingServer().sendmsg()
        return self.jscode()
class Index(BaseView):
    def get(self):
        render_template('index.html')


class CheckLog(BaseView):
    def get(self):
        #查看204服务器时用的接口，可以忽略
        response = make_response(
            send_from_directory('./logs', 'uwsgi.log', as_attachment=True))
        return response


class PostCheck(BaseView):
    def post(self):
        #后置检查
        data = CheckServcie().posttapi()
        return self.jscode()
if __name__ == '__main__':
    DingDing().get()
