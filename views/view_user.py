from datetime import datetime

from services.services_info import ProjectServer, ScriptService, HistoryService, SwtichServer, MasterServer
from services.services_user import UserService
from utils.basecode import BaseView
from utils.make_token import verify, verproject


class UserView(BaseView):
    """
    @api {get} user/login 登录
    @apiName login
    @apiGroup User
    @apiSuccessExample {json} Success-Response:
         {
          'cd': code, 'msg': msg, 'data': {"power":"pwoer为1为超级管理员2普通管理员0普通用户"}
         }
    @apiErrorExample {json} Error-Response:
       {
          'cd': code, 'msg': msg, 'data': {}
         }

    """

    def get(self):
        us = UserService()
        data = us.login()
        if data == 1:
            return self.jscode(1, '验证失败')
        elif data == 2:
            return self.jscode(1, '与验证服务器通信失败，请重新尝试')
        return self.jscode(data=data)


class HistoryView(BaseView):
    """
    @api {get} history 获取历史记录
    @apiName history
    @apiGroup Project
    @apiParam {int} id 查询参数（项目id)
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": [{"id":"项目Id","author":"提交人","date":"提交日期",
          "log":"提交信息","changed":"文件更改信息","dirsChanged":"目录更改信息",
          "youngest_revision":"上个版本号"]}
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """

    def get(self):
        data = HistoryService().getdata()
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='缺少参数')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='未找到项目')
        elif data == 4:
            return self.jscode(msg='该项目无历史记录', data=[])
        else:
            return self.jscode(data=data)


class ProjectView(BaseView):
    """
    @api {get} projects 获取项目
    @apiName projectlist
    @apiGroup Project
    @apiParam {int} id 查询参数（项目id，填0获取所有项目)
    @apiParam {int} ip 查询参数（ip:端口，标识服务器)
    @apiParam {int} startip 查询参数（ip:端口，启动地址)
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": [{"id":"项目Id","svn":"svn路径","name":"项目名称",[{"id":"脚本id","scriptName":"正在使用的脚本名称","isTiming":"临时取消"}]}]
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """
    @api {post} project 添加项目
    @apiName addproject
    @apiGroup Project
    @apiParam {str} name 项目名称
    @apiParam {str} pname 项目简称（全部英文字母例如：wolf，sgs）
    @apiParam {str} repos_url 项目svn,git路径
    @apiParam {str} ip 服务器地址
    @apiParam {str} isGit 1是0svn
    @apiParam {str} groupName 
    @apiParam {list} token [1,2]钉钉机器人token
    @apiParam {str} msg 备注
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": [{"id":"项目Id","svn":"svn路径","name":"项目名称",[{"id":"脚本id","scriptName":"正在使用的脚本名称","isTiming":"临时取消"}]}]
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """
    @api {put} project 修改项目
    @apiName putproject
    @apiGroup Project
    @apiParam {int} id 项目id
    @apiParam {str} name 项目名称
    @apiParam {str} repos_url 项目svn,git路径
    @apiParam {str} groupName 修改名称所在组全部生效
    @apiParam {list} token [1,2]钉钉机器人token
    @apiParam {str} msg 备注
    @apiSuccessExample {json} Success-Response:
         {"cd": 0, "msg": "msg", "data": {}}
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """
    @api {del} project 删除项目
    @apiName delproject
    @apiGroup Project
    @apiParam {int} id 项目id
    @apiSuccessExample {json} Success-Response:
         {"cd": 0, "msg": "msg", "data": {}
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """

    def get(self):
        data = ProjectServer().getproject()
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='未查询到项目')
        else:
            return self.jscode(data=data)

    @verify(2)
    def post(self):
        data = ProjectServer().addproject(self.judge)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='项目简称只能为英文')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='项目路径或项目简称不能重复')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='用户登陆信息错误')
        elif data == 5:
            return self.jscode(code=self.Error_code, msg='ip地址填写错误，或未填写')
        else:
            return self.jscode(data=data)

    @verify()
    def put(self):
        data = ProjectServer().putproject(self.judge)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='未查询到项目')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='项目简称只能为英文')
        elif data == 5:
            return self.jscode(code=self.Error_code, msg='该项目路径已存在，请检查')
        elif data == 6:
            return self.jscode(code=self.Error_code, msg='权限不足')
        elif data == 6:
            return self.jscode(code=self.Error_code, msg='ip地址填写错误，或未填写')
        else:
            return self.jscode()

    @verify()
    def delete(self):
        data = ProjectServer().delproject(self.judge)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='未查询到项目')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='权限不足')
        else:
            return self.jscode()


class ScriptView(BaseView):
    """
    @api {get} script 下载项目脚本
    @apiName dwscript
    @apiGroup Project
    @apiParam {int} id 查询参数（脚本id)
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": {"name":"脚本名称","id":"","content":"base64转码"}
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """
    @api {post} project/script 添加项目脚本
    @apiName addscript
    @apiGroup Project
    @apiParam {int} id（项目id) *
    @apiParam {str} script 脚本文件 [{"name":"脚本文件名","content":"文件内容base64转码","msg":"备注","other":"自己想填什么就填什么吧"},{}] 
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": [{"id":"脚本id","name":"脚本名称"}]
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """
    @api {put} project/script 修改项目脚本
    @apiName putscript
    @apiGroup Project
    @apiParam {int} id（脚本id) *
    @apiParam {str} msg 备注
    @apiParam {str} other 自己想填什么就填什么吧 
   
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": [{"id":"项目Id","svn":"svn路径","name":"项目名称"}]
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """ 
    @apiParam {str} msg 备注
    @api {del} project/script 删除项目脚本
    @apiName delscript
    @apiGroup Project
    @apiParam {int} id（脚本id) *
    @apiParam {int} isTiming 临时删除（可恢复，填0彻底删除） 
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": [{"id":"项目Id","svn":"svn路径","name":"项目名称"}]
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """

    def get(self):
        data = ScriptService().getscript()
        if type(data) not in (int,dict):
            return data
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='未查询到脚本')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='本地脚本文件缺失')
        else:
            return self.jscode(data=data)

    @verify()
    def post(self):
        data = ScriptService().addscript(self.judge)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='未查询到项目')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='脚本名格式错误')
        elif data == 5:
            return self.jscode(code=self.Error_code, msg='与服务器连接失败')
        elif data == 6:
            return self.jscode(code=self.Error_code, msg='权限不足')
        elif data == 7:
            return self.jscode(code=self.Error_code, msg='备注字数过多')
        return self.jscode()

    @verify()
    def put(self):
        data = ScriptService().putscript(self.judge)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='无此脚本')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='备注字数过多')
        else:
            return self.jscode()

    @verify()
    def delete(self):
        data = ScriptService().delscript(self.judge)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='无此脚本')
        else:
            return self.jscode()


class UserPView(BaseView):
    """
    @api {get} user 获取人员信息，admin获取全部用户信息
    @apiName getuser
    @apiGroup User
    @apiSuccessExample {json} Success-Response:
         {
          "cd": 0, "msg": "msg", "data": {"name":"","id":"","isSelf":"是否为当前用户","project":[{
                    "name": "狼人对决asdfasdfasdfasdfasfasfasdfasdf",
                    "repos_url": "https://10.225.136.30/svn/lrs",
                    "msg": "nihao",
                    "id": 1,
                    "pname": "wolf"
                }]}
         }
    @apiErrorExample {json} Error-Response:
       {
          "cd": 1, "msg": "msg", "data": {}
         }
    """
    """
    @api {post} user 添加用户与项目
    @apiName adduser
    @apiGroup User
    @apiParam {int} id（人员id) *
    @apiParam {int} projectid （项目id）*
    @apiParam {int} isAdmin （是否为该项目的管理员）*
    """
    """
       @api {post} user 添加用户与项目
       @apiName deluser
       @apiGroup User
       @apiParam {int} id（人员id) *
       @apiParam {int} projectid （项目id）*
   """

    @verify()
    def get(self):
        user = self.judge
        data = ProjectServer().getuser(user)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='无此人员')
        else:
            return self.jscode(data=data)

    @verify()
    def post(self):
        user = self.judge
        data = ProjectServer().addpu(user)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='未找到当前用户')
        elif data == 5:
            return self.jscode(code=self.Error_code, msg='无此权限')
        else:
            return self.jscode()

    @verify()
    def delete(self):
        user = self.judge
        data = ProjectServer().delpu(user)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='参数不全')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='参数类型错误')
        elif data == 3:
            return self.jscode(code=self.Error_code, msg='未查询到关系')
        elif data == 4:
            return self.jscode(code=self.Error_code, msg='未找到当前用户')
        elif data == 5:
            return self.jscode(code=self.Error_code, msg='无此权限')
        else:
            return self.jscode()


class SwtichView(BaseView):
    """
    @api {post} swtich 开关控制
    @apiName switch
    @apiGroup Script
    @apiParam {int} id（项目id) *
    @apiParam {int} groupId （项目组id填写此项责关闭该组下所有项目）
    @apiParam {int} dingSwtich （钉钉开关0使用1关闭）
    @apiParam {int} switch （脚本总开关，0使用1关闭）
    """

    @verify()
    def post(self):
        user = self.judge
        data = SwtichServer().putswtich(user)
        if data == 1:
            return self.jscode(code=self.Error_code, msg='未找到项目')
        elif data == 2:
            return self.jscode(code=self.Error_code, msg='无此权限')
        else:
            return self.jscode()

class MasterProjectView(BaseView):
    def get(self):
        data = MasterServer().getProject()
        return self.jscode(data=data)


class MasterHistoryView(BaseView):
    def post(self):
        data = MasterServer().getHistory()
        return self.jscode(data=data)