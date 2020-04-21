import importlib
import os

from importlib import util


class TestScript(object):
    def __init__(self, packpath, uid='', name=''):
        module_spec = importlib.util.spec_from_file_location(name, packpath)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        self.model = module
        self.uid = uid

    def trun(self, fun):
        # 请勿修改
        error = ''
        res = ''
        flag = False
        try:
            flag, res = fun()
        except Exception as e:
            error = str(e)
        flag = 0 if flag else 1
        return {'error': error, 'msg': res, 'cd': flag}

    def run(self):
        # 请勿修改
        try:
            self.model.uid = self.uid
            self.model.getpath, self.model.changed, self.model.author, self.model.log = self.model.Pathtool(
                uid=self.model.uid).getall(self.model.basepath)#对脚本中所需的路径进行赋值
            scrlist = [getattr(self.model, i) for i in dir(self.model) if i.startswith('test')]#匹配以test开头的函数执行
            data = [self.trun(i) for i in scrlist]
        except Exception as e:
            return {'error': '', 'msg': str(e), 'cd': 1}
        return data
    def postrun(self, jsonargs):
        # 请勿修改
        try:
            self.model.jsonargs = jsonargs#对执行脚本中的所需参数进行赋值
            scrlist = [getattr(self.model, i) for i in dir(self.model) if i.startswith('post')]#匹配以post开头的函数执行
            data = [self.trun(i) for i in scrlist]
        except Exception as e:
            print(e)
            return False
        return data
