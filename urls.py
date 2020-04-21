# from utils.SQL import Testsql
from views import view_info, view_user


class Url_register(object):
    url = '/server/version'

    def __init__(self, api):
        self.url_svn_git(api)
        self.url_plug(api)
        self.url_index(api)

    def url_svn_git(self, api):
        api.add_resource(view_info.Check, self.url + '/check')
        api.add_resource(view_info.PostCheck, self.url + '/postcheck')
        api.add_resource(view_info.DingDing, self.url + '/dingding')

    def url_plug(self, api):
        api.add_resource(view_info.CheckLog, self.url + '/log')

    def url_index(self, api):
        api.add_resource(view_user.UserView, self.url + '/user/login')
        api.add_resource(view_user.UserPView, self.url + '/user')
        api.add_resource(view_user.ProjectView, self.url + '/projects', self.url + '/project')
        api.add_resource(view_user.ScriptView, self.url + '/project/script', self.url + '/script')
        api.add_resource(view_user.HistoryView, self.url + '/history')
        api.add_resource(view_user.SwtichView, self.url + '/swtich')
        #api.add_resource(view_user.MasterProjectView, self.url + '/master/project')
        #api.add_resource(view_user.MasterHistoryView, self.url + '/master/history')


