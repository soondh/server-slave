import pymysql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

pymysql.install_as_MySQLdb()
db = SQLAlchemy()


class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)
    createTime = db.Column(db.DateTime, default=datetime.now())
    updateTime = db.Column(db.DateTime, default=datetime.now())
    isDelete = db.Column(db.Boolean, default=False)
    base_fields = ['id', ]  # 基类默认序列化处理的字段
    default = []  # 默认返回字段

    @classmethod
    def __ser_fields(cls, fields=None, excldu=None, default_fields=None):
        '''此方法处理需要序列的字段,fields为需要序列化的,excldu为不需要的,同时输入
        以excldu为准,都不输入为default
        '''
        if not default_fields:
            default_fields = cls.default + cls.base_fields
        if excldu:
            fields = [i for i in default_fields if i not in excldu]
            return fields
        elif fields:
            return fields
        else:
            return default_fields

    @classmethod
    def serialize_data(cls, fields=None, excldu=None):
        '''
        :param fields: 包括字段
        :param excldu: 排除字段
        此方法通过调用__ser_fields方法设置需要序列化的字段
        '''

        if not fields:
            fields = []
        if not excldu:
            excldu = []
        __default_fields = cls.default + cls.base_fields
        fields_list = cls.__ser_fields(fields, excldu, __default_fields)
        return fields_list

    def serializes(self, fields_list=None):
        '''
        :return: {'name': 5, 'online_situation': 5, 'version': 5, 'version_show': 5,
         'operation_accidents': 4, 'bad_bug': 3,
         'online_bug': 2, 'operation_activity': 1,
         'community_feedback': 1, 'author_id': 0, 'project_id': 5,
         'content': 6, 'is_online': 7, 'is_send': 8}
        '''
        if not fields_list:
            fields_list = self.default + self.base_fields
        data = {i: str(getattr(self, i)) for i in fields_list}
        for i in data:
            if data[i].isdecimal():
                data[i] = int(data[i])
            if data[i] == 'None':
                data[i] = ''
        return data


class History(db.Model, BaseModel):
    __tablename__ = 'history'
    userId = db.Column(db.Integer, default=0, comment='用户id')
    projectId = db.Column(db.Integer, comment='项目Id')
    author = db.Column(db.String(50), comment='提交人')
    date = db.Column(db.String(50), default='', comment='提交日期')
    log = db.Column(db.Text(), default='', comment='提交信息')
    changed = db.Column(db.Text(), default='', comment='文件更改信息')
    dirsChanged = db.Column(db.Text(), default='', comment='目录更改信息')
    youngest_revision = db.Column(db.String(50), default='', comment='上个版本号')
    dingmsg = db.Column(db.Text(), default='', comment='钉钉消息')
    result = db.Column(db.Text(), default='', comment='脚本执行结果')
    dingMsgCode = db.Column(db.Integer, default=0, comment='dingMsgCode')
    uuid = db.Column(db.String(100), default='', comment='uuid')
    default = ['projectId', 'author', 'date', 'log',
               'changed', 'dirsChanged', 'youngest_revision', 'result','dingmsg','dingMsgCode']


class User(db.Model, BaseModel):
    __tablename__ = 'user'
    name = db.Column(db.String(50), comment='用户名')
    power = db.Column(db.Integer, default=0, comment='权限')
    email = db.Column(db.String(50), unique=True, comment='邮箱')
    default = ['name', 'id']


class Project(db.Model, BaseModel):
    __tablename__ = 'project'
    name = db.Column(db.String(50), comment='项目名称')
    pname = db.Column(db.String(50), comment='项目简称')
    repos_url = db.Column(db.String(50), comment='repos_url')
    ip = db.Column(db.String(50), comment='脚本服务器地址')
    startip = db.Column(db.String(50), comment='服务器启动地址')
    groupId = db.Column(db.Integer, default=0, comment='组id')
    isGit = db.Column(db.Integer, default=0, comment='是否是git')
    msg = db.Column(db.String(50), default='', comment='备注')
    token = db.Column(db.String(255), default='', comment='钉钉token')
    groupName = db.Column(db.String(50), default='', comment='组名称')
    dingSwtich = db.Column(db.Integer, default=0, comment='钉钉开关')
    swtich = db.Column(db.Integer, default=0, comment='脚本开关')
    default = ['name', 'repos_url', 'msg',
               'id', 'pname','ip','token',
               'groupName','groupId','isGit',
               'dingSwtich','swtich','startip']


class ProjectUser(db.Model, BaseModel):
    __tablename__ = 'projectuser'
    projectid = db.Column(db.Integer, default=0, comment='项目id')
    userid = db.Column(db.Integer, default=0, comment='人员id')
    isAdmin = db.Column(db.Integer, default=0, comment='项目管理员')

class ScriptInfo(db.Model, BaseModel):
    __tablename__ = 'script'
    name = db.Column(db.String(50), comment='脚本名称')
    isTiming = db.Column(db.Integer, default=0, comment='临时删除')
    projectId = db.Column(db.Integer, default=0, comment='所属项目')
    userId = db.Column(db.Integer, default=0, comment='所属人员')
    file_id = db.Column(db.String(150), default=0, comment='Remote file_id')
    msg = db.Column(db.String(50), default='', comment='备注')
    other = db.Column(db.String(50), default='', comment='other')
    isPost = db.Column(db.Integer, default=0, comment='是否post')
    default = ['name', 'isTiming', 'id','createTime','msg','userId','other','file_id','isPost']
