import json
import os
import shutil
import sys
import uuid

import paramiko
import re
import tempfile
import time
import uuid as tooluid

import requests
from flask import make_response, send_from_directory
from sqlalchemy import or_

from config import Config
from models import Project, ScriptInfo, History, ProjectUser, User
from utils.basecode import RequestSelf, DingDingBot
from utils.make_token import verproject


class CheckServcie(RequestSelf):
    def testapi(self):
        data = self.getjson()
        if not data:
            return 1
        repos_url = data.get('repos_url', '')
        fc = data.get('files_changed', '')
        log = data.get('log', 0)
        author = data.get('author', '')
        date = data.get('date', '')
        changed = data.get('changed', '')
        dirs_changed = data.get('dirs_changed', '')
        uuid = data.get('uuid', '')
        youngest_revision = data.get('youngest_revision', '')
        checkjson = json.dumps({'author': author, 'log': log,
                                'changed': changed, 'dirs_changed': dirs_changed})
        if not all([repos_url]):#判空,根据url确定属于哪个项目
            return 1
        project = Project.query.filter_by(repos_url=repos_url, isDelete=False).first()
        if not project:
            return 2
        swtich = project.swtich#脚本开关
        if swtich:
            return 5
        fileuid = str(tooluid.uuid1())
        jsonpath = os.path.join('./file', project.pname, fileuid)
        os.makedirs(jsonpath, exist_ok=True)
        with open(os.path.join(jsonpath, 'detail.json'), 'w') as f:
            f.write(checkjson)
        for i in fc:
            content = i.get('content', '')
            filepath = i.get('filepath', '')
            # dirname = i.get('dirname', '')
            if not all([filepath]):
                return 1
            path = os.path.join('./file', project.pname, fileuid, filepath)
            self.savefile(path, content)
        data = self.runscr(project=project, uid=fileuid, pname=project.pname)
        shutil.rmtree(jsonpath)
        his = History()
        his.projectId = project.id
        his.log = log
        his.author = author
        his.date = date
        his.changed = json.dumps(changed)
        his.dirsChanged = json.dumps(dirs_changed)
        his.youngest_revision = youngest_revision
        his.result = json.dumps(data)
        his.uuid = uuid
        self.create(his)
        if not data:
            return 4
        return data, his.id

    def runscr(self, project, uid, pname):
        scr = ScriptInfo.query.filter_by(isTiming=False, isDelete=False, projectId=project.id,isPost=False).all()
        if not scr:
            return False
        dirlsit = [i.name for i in scr]
        msglist = []
        for i in dirlsit:
            if not i.endswith('py'):#筛选掉json文件
                continue
            from utils.run import TestScript
            path = os.path.join('./file', pname, i)
            conm = TestScript(path, uid, i).run()
            msglist.append({"scrname": i.rsplit('____', maxsplit=1)[-1], 'msg': [_ for _ in conm],
                            'syserror': ''})
        return msglist

    def posttapi(self):
        data = self.getjson()
        if not data:
            return 1
        repos_url = data.get('repos_url', '')#同pre-commit
        if not all([repos_url]):
            return 1
        project = Project.query.filter_by(repos_url=repos_url, isDelete=False).first()
        if not project:
            return 2
        swtich = project.swtich#判断项目的开关
        if swtich:
            return 5
        data = self.postrunscr(project=project, pname=project.pname, jsonargs=json.dumps(data))
        if not data:
            return 4
        return data

    def postrunscr(self, project, pname, jsonargs):
        scr = ScriptInfo.query.filter_by(isTiming=False, isDelete=False, projectId=project.id, isPost=True).all()
        if not scr:
            return False
        dirlsit = [i.name for i in scr]
        for i in dirlsit:
            if not i.endswith('py'):#筛选掉json文件
                continue
            from utils.run import TestScript
            path = os.path.join('./file', pname, i)
            conm = TestScript(path, i).postrun(jsonargs)
            if not conm:
                return False
        else:
            return True


class ProjectServer(RequestSelf):
    def getproject(self):
        iddict = self.getargs()
        try:
            id = int(iddict.get('id', 0))
        except:
            return 1
        if id == 0:#id为0获取全部项目
            projectobj = Project.query.filter_by(isDelete=False).all()
        else:
            projectobj = Project.query.filter_by(id=id, isDelete=False).all()
        if not projectobj:
            return 2
        data = [i.serializes() for i in projectobj]
        for i in data:
            projectId = i['id']
            i['token'] = json.loads(i['token'])#目前钉钉token只取一个，后续有需求可以增加
            if len(i['token']) == 1:#目前钉钉token只取一个，后续有需求可以增加
                i['token'] = i['token'][0]
            sobj = ScriptInfo.query.filter_by(projectId=projectId, isDelete=False)
            sdata = [s.serializes() for s in sobj if s]
            i['scriptList'] = []
            for s in sdata:
                user = User.query.filter_by(isDelete=False, id=s['userId']).first()
                s.pop('userId')
                s['username'] = user.name if user else ''

                s['url'] = 'http://10.225.136.204:10016/files/' + s['name']
                s['name'] = s['name'].split('____')[-1]
                #s['url'] = self.fastdfs + str(s.pop('file_id'))

                kswitch = False
                for k in i['scriptList']:
                    skey = k.get('other', False)
                    if skey == s['other']:#取备注
                        kswitch = True
                if not kswitch:#备注
                    i['scriptList'].append({"other": s['other'], "data": []})
                for m in i['scriptList']:
                    skey = m.get('other', False)
                    if skey == s['other']:
                        m['data'].append(s)
        return data

    def addproject(self, user):
        body = self.getjson()
        name = body.get('name', '')
        pname = body.get('pname', '')
        token = body.get('token', [])
        isGit = body.get('isGit', 0)
        groupId = body.get('groupId', 0)
        groupName = body.get('groupName', '')
        if type(token) is str:
            token = [token]
        res = [i for i in pname if not (97 <= ord(i) <= 122 or 65 <= ord(i) <= 90)]
        if res:
            return 2
        repos_url = body.get('repos_url', '')
        ip = body.get('ip', '')
        # startip = body.get('startip', '')备用 统一更新启动
        # flag = self.verip(ip)
        # if not flag or not ip:
        #     return 5
        # flag = self.verip(startip)
        # if not flag or not startip:
        #  return 5
        msg = body.get('msg', '')
        if not all([name, repos_url, token]):
            return 1
        project = Project.query.filter(or_(Project.repos_url == repos_url, Project.pname == pname),
                                       Project.isDelete == False).first()
        userId = user.get('userId', 0)
        if not userId:
            return 4
        if project:
            return 3
        pobj = Project()
        pobj.name = name
        pobj.pname = pname
        pobj.repos_url = repos_url
        pobj.ip = ip
        # pobj.startip = startip
        pobj.msg = msg
        pobj.token = json.dumps(token)
        pobj.groupId = 0
        self.create(pobj)
        if isGit:
            pobj.groupId = pobj.id
        if groupId:
            pobj.groupId = groupId
        if groupName:
            pobj.groupName = groupName
        self.update(pobj)
        pu = ProjectUser()
        pu.projectid = pobj.id
        pu.userid = userId
        pu.isAdmin = 1
        self.create(pu)
        data = {"name": name, "id": pobj.id, "pname": pname, "repos_url": repos_url,
                "ip": ip, "msg": msg, "token": token}
        return data

    def putproject(self, judge):
        body = self.getjson()
        try:
            id = int(body.get('id', 0))
        except:
            return 2
        if not id:
            return 1
        name = body.get('name', '')
        pname = body.get('pname', '')
        token = body.get('token', [])
        groupName = body.get('groupName', '')
        if type(token) is str:
            token = [token]
        res = [i for i in pname if not (97 <= ord(i) <= 122 or 65 <= ord(i) <= 90)]
        if res:
            return 4
        repos_url = body.get('repos_url', '')
        pobj = Project.query.filter_by(isDelete=False, id=id).first()
        project = Project.query.filter(or_(Project.repos_url == repos_url, Project.pname == pname),
                                       Project.isDelete == False).first()
        if not pobj:
            return 3
        if project and project.id != id:
            return 5
        f = verproject(judge, pobj.id)
        if not f:
            return 6
        msg = body.get('msg', '')
        if name:
            pobj.name = name
        if pname:
            try:
                os.rename('./file/%s' % pobj.pname, './file/%s' % pname)
            except:
                pass
            pobj.pname = pname
        if repos_url:
            pobj.repos_url = repos_url
        if msg:
            pobj.msg = msg
        if token:
            pobj.token = json.dumps(token)
        self.update(pobj)
        if groupName:#字段取消，原为分组使用
            gobj = Project.query.filter_by(isDelete=False, id=pobj.id).all()
            if gobj:
                for i in gobj:
                    i.groupName = groupName
                    self.update(i)
        return

    def delproject(self, judge):
        body = self.getjson()
        try:
            id = int(body.get('id', 0))
        except:
            return 2
        if not id:
            return 1
        pobj = Project.query.filter_by(isDelete=False, id=id).first()
        if not pobj:
            return 3
        f = verproject(judge, pobj.id)
        if not f:
            return 4
        pobj.isDelete = 1
        script = ScriptInfo.query.filter_by(isDelete=False, projectId=id).all()
        if script:
            for i in script:
                i.isDelete = 1
                self.update(i)
        self.update(pobj)
        return

    def getuser(self, user):
        userId = user.get('userId', 0)
        if not userId:
            return 1
        user = User.query.filter_by(isDelete=False, id=userId).first()
        if not user:
            return 2
        userid = user.id
        if user.power == 1:#判断是否为admin
            userlist = [i for i in User.query.filter_by(isDelete=False).all() if i]
        else:
            userlist = [user]
        pulist = []
        for i in userlist:
            if i.power == 1:#admin为全部项目
                pu = [{"userid": user.id, "isAdmin": 1,
                       "project": p} for p in Project.query.filter_by(isDelete=False).all() if p]
            else:
                pu = [s for s in ProjectUser.query.filter_by(isDelete=False, userid=i.id).all()]
                pu = [{"userid": p.userid, "isAdmin": p.isAdmin,
                       "project": Project.query.filter_by(isDelete=False, id=p.projectid).first()} for p in pu]

            datalist = []
            for p in pu:
                if p['project']:#序列化project信息
                    data = p['project'].serializes()
                    data['isAdmin'] = 1 if p['isAdmin'] else 0
                    datalist.append(data)
            try:
                pulist.append({'id': i.id, 'name': i.name, "project": datalist, 'power': i.power})
            except:
                pulist.append({'id': i.id, 'name': i.name, "project": [], 'power': i.power})
        for i in pulist:
            i['isSelf'] = 0
            if i['id'] == userid:
                i['isSelf'] = 1
        return pulist

    def addpu(self, user):
        userId = user.get('userId', 0)
        if not userId:
            return 4
        user = User.query.filter_by(isDelete=False, id=userId).first()
        flag = True if user.power == 1 else False
        if not user:
            return 5
        data = self.getjson()
        try:
            userid = int(data.get('id', 0))
            projectid = int(data.get('projectid'))
            isAdmin = int(data.get('isAdmin', 0))
        except:
            return 2
        if not all([userid, projectid]):
            return 1
        puadmin = ProjectUser.query.filter_by(isDelete=False, userid=user.id, projectid=projectid).first()
        if not puadmin and not flag:#判断权限
            return 5
        if not puadmin.isAdmin and not flag:#判断权限
            return 5
        pu = ProjectUser.query.filter_by(isDelete=False, userid=userid, projectid=projectid).first()
        if pu:
            return 3
        pu = ProjectUser()
        pu.userid = userid
        pu.projectid = projectid
        pu.isAdmin = isAdmin
        self.create(pu)
        return 3

    def delpu(self, user):
        userId = user.get('userId', 0)
        if not userId:
            return 4
        user = User.query.filter_by(isDelete=False, id=userId).first()
        flag = True if user.power == 1 else False
        if not user:
            return 5
        data = self.getjson()
        try:
            userid = data.get('id', 0)
            projectid = data.get('projectid')
        except:
            return 2
        if not all([userid, projectid]):
            return 1
        puadmin = ProjectUser.query.filter_by(isDelete=False, userid=user.id, projectid=projectid).first()
        if not puadmin and not flag:#判断权限
            return 5
        if not puadmin.isAdmin and not flag:#判断权限
            return 5
        pu = ProjectUser.query.filter_by(isDelete=False, userid=userid, projectid=projectid).first()
        if not pu:
            return 3
        pu.isDelete = 1
        self.update(pu)
        return 4


class ScriptService(RequestSelf):
    def getssh(self, ip, username):
        a, b, c = self.__getsftp(ip, username)
        return a, b, c

    def addscript(self, judge):
        body = self.getjson()
        try:
            pid = int(body.get('id', 0))
        except:
            return 1
        scriptlist = body.get('script', '')
        if not all([scriptlist, pid]):
            return 2
        if not type(scriptlist) is list:
            return 1
        for i in scriptlist:
            if not type(i) is dict:
                return 1
        project = Project.query.filter_by(isDelete=False, id=pid).first()
        if not project:
            return 3
        f = verproject(judge, project.id)
        if not f:
            return 6
        localpath = os.path.join('./file', project.pname)
        userId = judge.get('userId', 0)
        for i in scriptlist:
            sname = i.get('name', False)
            other = i.get('other', False)
            content = i.get('content', False)
            msg = i.get('msg', '')
            isPost = i.get('isPost', 0)
            if not all([sname, content, msg]):
                return 2
            if len(msg) > 50:
                return 7
            sname = self.__checkname(sname)
            if not sname:
                return 4
            sp = os.path.join(localpath, sname)
            file = self.savefile(sp, i['content'])
            # try:
            #     res = self.upload(file)
            # except Exception as e:
            #     print(str(e))
            #     return 5
            st = ScriptInfo()
            st.name = sname
            st.localpath = localpath
            st.projectId = pid
            st.msg = msg
            st.other = other
            st.isPost = isPost
            st.userId = userId
            st.file_id = ''
            self.create(st)

    def __checkname(self, name):
        timestr = str(time.time()).replace('.', '*')
        flag = name.find('/')
        if not flag == -1:
            return False
        flag = name.find("\\")
        if not flag == -1:
            return False
        if name.endswith('.json'):
            return name
        if not name.endswith('.py'):
            return False
        newname = ''.join([timestr, '____', name])
        return newname

    def __getsftp(self, ip, username):
        key = paramiko.RSAKey.from_private_key_file('./id_rsa')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, username=username, pkey=key, timeout=15)
        except:
            return False
        t = ssh.get_transport()
        sftp = paramiko.SFTPClient.from_transport(t)
        return sftp, t, ssh

    def delscript(self, judge):
        body = self.getjson()
        try:
            idlist = body.get('id', 0)
            isTiming = int(body.get('isTiming', 0))
        except:
            return 1
        if not idlist:
            return 2
        for id in idlist:
            try:
                id = int(id)
            except:
                return 1
            st = ScriptInfo.query.filter_by(isDelete=False, id=id).first()
            f = verproject(judge, st.projectId)
            if not f:
                return 3
            if not st:
                return 2
            if isTiming == 2:
                st.isTiming = 1
            elif isTiming == 1:
                st.isTiming = 0
            else:
                st.isDelete = 1
            self.update(st)

    def getscript(self):
        try:
            id = int(self.getargs().get('id', 0))
            other = self.getargs().get('other', 0)
            stream = self.getargs().get('stream', 0)
        except:
            return 1
        if other:#根据other下载post还是pre的插件
            st = ScriptInfo.query.filter_by(isDelete=False, other=other).all()
            pname = Project.query.filter_by(isDelete=False, id=st[0].projectId).first().pname
            if not st:
                return 3
            other = "all"#返回文件的名称
            namelist = [i.name for i in st]
            uid = str(uuid.uuid1())
            path = os.path.join('./file', uid)
            patha = os.path.join('./file', uid + 'a')
            os.makedirs(path, exist_ok=True)
            os.makedirs(patha, exist_ok=True)
            for i in namelist:
                name = i.split('____')[-1]
                self._fileback(uid, name, './file/{}/{}'.format(pname, i))
            self.zipDir('./file/{}'.format(uid), './file/{}{}/{}{}'.format(uid, 'a', other, '.zip'))
            res = make_response(
                send_from_directory(directory='./file/{}{}'.format(uid, 'a'), filename='{}{}'.format(other, '.zip'),
                                    as_attachment=True))
            shutil.rmtree(path)
            shutil.rmtree(patha)
            return res
        else:
            st = ScriptInfo.query.filter_by(isDelete=False, id=id).first()
            pname = Project.query.filter_by(isDelete=False, id=st[0].projectId).first().pname
            if not st:
                return 3
            name = st.name
            name = name.split('____')[-1]
            if stream:
                res = make_response(
                    send_from_directory(directory='./file/{}'.format(pname), filename='{}'.format(name),
                                        as_attachment=True))
                return res
            #url = self.fastdfs + str(st.file_id)
            url = ''.join(['http://10.225.136.204:17256/files/',name])
            data = {'name': name, 'url': url}
            return data

    def putscript(self, judge):
        body = self.getjson()
        try:
            id = int(body.get('id', 0))
            msg = body.get('msg', '')
        except:
            return 1
        if not all([id, msg]):
            return 2
        if len(msg) > 50:
            return 4
        st = ScriptInfo.query.filter_by(isDelete=False, id=id).first()
        f = verproject(judge, st.projectId)
        if not f:
            return 3
        if not st:
            return 2
        st.msg = msg
        self.update(st)


class HistoryService(RequestSelf):
    def getdata(self):
        try:
            id = int(self.getargs().get('id', 0))
        except:
            return 1
        try:
            page = int(self.getargs().get('page', 0))
            pageSize = int(self.getargs().get('pageSize', 10))
        except:
            return 1
        if not id:
            return 2
        pj = Project.query.filter_by(isDelete=False, id=id).first()
        if not pj:
            return 3
        history = History.query.filter_by(isDelete=False, projectId=id).order_by(-History.id).all()
        total = len(history)
        if not history:
            return 4
        history = self.page(page, pageSize, history)
        data = [i.serializes() for i in history]
        for i in data:
            try:
                i['date'] = i['date'][:-6]
            except:
                i['date'] = ''
            try:
                i['changed'] = json.loads(i['changed'])
            except:
                i['changed'] = ''
            try:
                i['dirsChanged'] = json.loads(i['dirsChanged'])
            except:
                i['dirsChanged'] = ''
            try:
                i['result'] = json.loads(i['result'])
            except:
                i['result'] = ''

        pinfo = {'name': pj.name}
        sdata = [i.update(pinfo) for i in data]
        self.total = total
        return data


class DingServer(RequestSelf):
    def sendmsg(self):
        url = '''http://10.225.136.151:20008'''#跳转地址，配置为项目的地址
        data = self.getjson()
        content = data.get('dingmsg', '')  # 钉钉群消息
        dingMsgCode = data.get('dingMsgCode', 0)  # 钉钉群消息
        repos_url = data.get('repos_url', '')
        resutl = data.get('resutl', '')  # 数据库存储消息
        log = data.get('log', '')
        author = data.get('author', '')
        date = data.get('date', '')
        uuid = resutl.get("uuid", 0)
        msg = resutl.get("dbmsg", 0)
        try:
            content = eval(content)
        except:
            content = content
        if type(content) is list:
            content = [''.join([str(i + 1), '.', content[i], '    \n']) for i in range(len(content))]
            msg = ''.join([''.join([str(i + 1), '.', content[i], '\n']) for i in range(len(content))])
            contents = ''
            for i in range(len(content)):
                if i == 0:#第一个不拼接其余字符
                    contents = content[i]
                else:
                    contents = ''.join(
                        [contents, '&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;', content[i]])
            content = contents

        date = date[:-6]#取时间格式
        history = History.query.filter_by(isDelete=False, uuid=uuid).first()
        if not history:#对于出现问题没有历史记录的予以通过
            pass
        else:
            history.dingmsg = str(msg)
            history.dingMsgCode = dingMsgCode
            self.update(history)
        project = Project.query.filter_by(isDelete=False, repos_url=repos_url).first()
        if not project:#确保钉钉token不为空
            token = "b4bd796f437050897afde2155b7b401c368cdaec686aa22c7c8ef3e5fea10bbb"
        else:
            token = json.loads(project.token)[0]
            if not token:
                token = "b4bd796f437050897afde2155b7b401c368cdaec686aa22c7c8ef3e5fea10bbb"
        if dingMsgCode:
            info = "警告" if dingMsgCode == 1 else "错误"
            color = "#FFD39B" if dingMsgCode == 1 else "#ff0000"#根据状态选择颜色
            res = "提交已通过" if dingMsgCode == 1 else "提交没有通过"
            errormsg = "远程服务超时" if dingMsgCode == 1 else content
            post_string = '''&#8194;**<font color={}>[{}]</font>**<font color=#000000>{}</font>  
>结果:&#8194;&#8194;&#8194;&#8194;{}   
>提交人: &#8194;&#8194;{}   
>错误原因:&#8194;{}    
>提交时间:&#8194;{}     
>检查平台:&#8194;[点击查看详情]({}/checks?id={})  
'''.format(color, info, project.name, res, author, errormsg, date,url, project.id)
            dingSwtich = project.dingSwtich
            if dingSwtich:
                return
            ding = DingDingBot()
            ding.run(token=token, post_string=post_string)
            return

    def testmsg(self):
        url = '''http://10.225.136.204:10000'''
        content = "['权限不够，请联系相关人员','xml格式错误，请修正']"
        content = eval(content)
        content = [''.join([str(i + 1), '.', content[i], '    \n']) for i in range(len(content))]
        contents = ''
        for i in range(len(content)):
            if i == 0:
                contents = content[i]
            else:
                contents = ''.join([contents, '&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;', content[i]])
        #a = 'b4bd796f437050897afde2155b7b401c368cdaec686aa22c7c8ef3e5fea10bbb'
        token = 'b4bd796f437050897afde2155b7b401c368cdaec686aa22c7c8ef3e5fea10bbb'
        dingMsgCode = 2
        info = "警告" if dingMsgCode == 1 else "错误"
        color = "#FFD39B" if dingMsgCode == 1 else "#ff0000"
        res = "提交已通过" if dingMsgCode == 1 else "提交没有通过"
        errormsg = "远程服务超时" if dingMsgCode == 1 else contents
        post_string = '''&#8194;**<font color={}>[{}]</font>**<font color=#000000>{}</font>  
>结果:&#8194;&#8194;&#8194;&#8194;{}   
>提交人: &#8194;&#8194;{}   
>错误原因:&#8194;{} 
>提交时间:&#8194;{}  
>检查平台:   {}}/checks?id={}  
        '''.format(color, info, '狼人对决', res, 'robin', errormsg, '2019-08-16 15:47:05 +0800', url,'13')
        ding = DingDingBot()
        ding.run(token=token, post_string=post_string)
        return


class SwtichServer(RequestSelf):
    def putswtich(self, judge):
        args = self.getjson()
        groupId = args.get('groupId', 0)
        id = args.get('id', 0)
        dingSwtich = args.get('dingSwtich', False)
        switch = args.get('switch', False)
        if groupId:
            pobj = Project.query.filter_by(isDelete=False, groupId=groupId).all()
            if not pobj:
                return 1
            pobjlist = [i for i in pobj]
        else:
            pobj = Project.query.filter_by(isDelete=False, id=id).first()
            pobjlist = [pobj]
        for i in pobjlist:
            f = verproject(judge, i.id)
            if not f:
                return 2
        for i in pobjlist:
            if dingSwtich is not False:#修改开关状态
                i.dingSwtich = dingSwtich
            if switch is not False:
                i.swtich = switch
            self.update(i)


class MasterServer(RequestSelf):
    def getProject(self):
        args = self.getargs()
        id = args.get('id', 0)
        try:
            id = int(id)
        except:
            id = 0
        pobj = False
        if id:
            pobj = Project.query.filter_by(isDelete=False, id=id).all()
        if not id or not pobj:
            pobj = Project.query.filter_by(isDelete=False).all()

        data = [{"id": i.id, "name": i.name} for i in pobj]
        return data

    def getHistory(self):
        body = self.getjson()
        id = body.get('spid', 0)
        result = []
        succDate = ''
        erroDate = ''
        if not id:
            errohist = History.query.filter_by(isDelete=False, dingMsgCode=2).order_by(-History.id).first()
            succhist = History.query.filter_by(isDelete=False, dingMsgCode=0).order_by(-History.id).first()
            if errohist:
                erroDate = str(errohist.createTime)
            if succhist:
                succDate = str(succhist.createTime)
            data = {"spid": errohist.id, "erroDate": erroDate, "succDate": succDate}
            result.append(data)
        else:
            for i in id:
                errohist = History.query.filter_by(isDelete=False, projectId=i, dingMsgCode=2).order_by(
                    -History.id).first()
                succhist = History.query.filter_by(isDelete=False, projectId=i, dingMsgCode=0).order_by(
                    -History.id).first()
                if errohist:
                    erroDate = str(errohist.createTime)
                if succhist:
                    succDate = str(succhist.createTime)
                data = {"spid": i, "name": Project.query.get(i).name, "erroDate": erroDate, "succDate": succDate}
                result.append(data)
        return result
if __name__ == '__main__':
    DingServer().testmsg()
