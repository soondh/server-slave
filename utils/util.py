import json


class Pathtool(object):
    def __init__(self, uid=False):
        self.uid = uid

    def getpath(self, basepath, path):
        if self.uid:
            if path.startswith('./'):
                res = ''.join([basepath, '/%s' % self.uid, path[1:]])
            elif path.startswith('/'):
                res = ''.join([basepath, '/%s' % self.uid, path])
            else:
                res = ''.join([basepath, '/%s/' % self.uid, path])
        else:
            if path.startswith('./'):
                res = ''.join([basepath, '/file/000000', path[1:]])
            elif path.startswith('/'):
                res = ''.join([basepath, '/file/000000', path])
            else:
                res = ''.join([basepath, '/file/000000', path])
        return res

    def getjson(self, path):
        try:
            if self.uid:
                detail_data = json.load(open(path + '/%s/detail.json' % self.uid, 'r'))
                changed = detail_data.get('changed')
                author = detail_data.get('author')
                log = detail_data.get('log')
                return changed, author, log
            else:
                detail_data = json.load(open(path + '/file/000000/detail.json', 'r'))
                changed = detail_data.get('changed')
                author = detail_data.get('author')
                log = detail_data.get('log')
                return changed, author, log
        except Exception as e:
            return e, e, e

    def getall(self, path):
        try:
            changed, author, log = self.getjson(path)
        except Exception as e:
            print(e)
            return 1, str(e), (e), (e)
        return self.getpath, changed, author, log


class Logging(object):
    def success(self, info=''):
        return True, info

    def error(self, info):
        return False, info
