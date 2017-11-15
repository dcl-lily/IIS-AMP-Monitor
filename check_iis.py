#!/usr/bin/env python
#_*_ coding:utf-8 _*_
'''
Created on 2017年11月09日

@author: Alex
@version: 1.1
@copyright: 青鸟技术联盟.
@license: GPLv3
'''

import urllib2,ssl,sys,argparse
from bs4 import BeautifulSoup
#NTLM 认证
from ntlm import HTTPNtlmAuthHandler
#全局SSL
ssl._create_default_https_context = ssl._create_unverified_context

class IIS_APM_Monitor:
    def __init__(self,dic):
        self.User_Name=dic.user
        self.User_Password=dic.password
        self.IIS_API_Host=dic.host
        self.IIS_API_Port=str(dic.port)
        self.IIS_API_Token=dic.token
        self.IIS_Monit_Mode=dic.mode
        self.IIS_Moint_ID=dic.id
        self.IIS_Moint_Name=dic.name
        self.IIS_Monit_OK=dic.ok
        self.IIS_Monit_Critical=dic.critical
        self.IIS_Moint_Warning=dic.warning
        self.IIS_Moint_Res=dic.res
        self.Nagios_OK=0
        self.Nagios_Warning=1
        self.Nagios_Critical=2
        self.Nagios_Unknown=3
        self.IIS_API_Url="https://%s:%s"%(self.IIS_API_Host,self.IIS_API_Port)
        self.__Auth_IIS_API()
        if not self.IIS_Moint_ID:
            self.__GET_ID()
    def IIS_APM_Main(self):
        '''
        类主函数，根据-m选项执行不同的操作
        :return: 状态值以及消息内容
        '''
        if self.IIS_Monit_Mode == 'GetPoolsName':
            return  self.Nagios_Unknown,self.Get_IIS_Pools()
        elif self.IIS_Monit_Mode =='GetSitesName':
            return  self.Nagios_Unknown,self.Get_IIS_Sites()
        elif self.IIS_Monit_Mode == 'GetPoolMonit':
            return self.Res_Monitoring('/api/webserver/application-pools/monitoring/')
        elif self.IIS_Monit_Mode == 'GetSitesMonit':
            return self.Res_Monitoring('/api/webserver/websites/monitoring/')
        elif self.IIS_Monit_Mode == 'GetAll':
            return self.Res_Monitoring('/api/webserver/monitoring/',False)
        else:
            return self.Nagios_Unknown," Unknown options "
    def __Auth_IIS_API(self):
        '''
        通过用户名和密码进行页面认证
        :return: 无返回值
        '''
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.IIS_API_Url, self.User_Name, self.User_Password)
        auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
        opener = urllib2.build_opener(auth_NTLM)
        urllib2.install_opener(opener)
        try:
            response=urllib2.urlopen(self.IIS_API_Url)
        except Exception,e:
            print "Host or URL cannot access,Please check the host and port configuration And  Firewall configuration"
            print e
            sys.exit(self.Nagios_Unknown)
        if response.code == 401:
            print "401-Authentication failure,Please check your username or password"
            sys.exit(self.Nagios_Unknown)
        if not self.Get_XSRF_TOKEN(response.read()):
            print " Unable to obtain authentication information, Please contact the administrator to process "
            sys.exit(self.Nagios_Critical)
        self.__Set_Header_Info()
    def Get_XSRF_TOKEN(self,message):
        '''
        获取认证后的XSRF值
        :param message:html认证页面内容
        :return: 如果找到返回true否者返回false
        '''
        soup = BeautifulSoup(message,"html.parser")
        for token in soup.findAll('input'):
            temp=token.get('name')
            if "XSRF-TOKEN" in str(temp):
                self.XSRF_TOKEN=token.get('value')
                return True
        return False
    def __Set_Header_Info(self):
        '''
        设置API请求的头部信息
        :return:
        '''
        self.headers={
        "Host": self.IIS_API_Host + ":" + self.IIS_API_Port,
        "User-Agent": "Nagios IIS API Per Check",
        "Accept": "application/hal+json",
        "Accept-Language": "en-US,en;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Access-Token": "Bearer " + self.IIS_API_Token,
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": "XSRF-TOKEN=" + self.XSRF_TOKEN,
        "Connection": "keep-alive"
        }
    def __Get_API_Message(self,API):
        '''
        获取指定API返回的内容
        :param API: API路径
        :return: 消息内容
        '''
        request = urllib2.Request(self.IIS_API_Url + API,headers=self.headers)
        response = urllib2.urlopen(request)
        if response.code != 200:
            print "Failed to read API information. Please contact the administrator"
            sys.exit(self.Nagios_Unknown)
        return eval(response.read())
    def __GET_ID(self):
        '''
        通过站点名或者资源池名称获取对应的ID信息
        :return: 对象的ID
        '''
        if self.IIS_Monit_Mode =='GetPoolsName' or self.IIS_Monit_Mode =='GetSitesName' or self.IIS_Monit_Mode =='GetAll' : return
        if self.IIS_Monit_Mode=='GetSitesMonit':
            rus=self.__Get_API_Message("/api/webserver/websites")['websites']
            for key in rus:
                if key['name'] == self.IIS_Moint_Name:
                    self.IIS_Moint_ID=key['id']
                    return
        elif self.IIS_Monit_Mode=='GetPoolMonit':
            rus = self.__Get_API_Message("/api/webserver/application-pools")['app_pools']
            for key in rus:
                if key['name'] == self.IIS_Moint_Name:
                    self.IIS_Moint_ID = key['id']
                    return
        print "The site\pool name was not found, Please enter the  site\pool name  or ID "
        sys.exit(self.Nagios_Unknown)
    def myAlign(self,string, length=0):
        '''
        格式化输出对其
        :param string: 需要显示的字符串
        :param length: 长度，字符串不购长，会使用空格填充
        :return: 格式化后的字符串　
        '''
        if length == 0 : return string
        slen = len(string)
        placeholder= ' ' if isinstance(string, str) else u'　'
        while slen < length:
            string += placeholder
            slen += 1
        return string
    def Get_IIS_Pools(self):
        '''
        放回资源池的状态信息
        :return:  资源池列表
        '''
        rus=self.__Get_API_Message("/api/webserver/application-pools")['app_pools']
        msg = self.myAlign('Pool_Name',30) + self.myAlign('Pool_Status',20) +'Pool_ID'
        for key in rus:
            msg +="\r\n" + self.myAlign(key['name'],30) + self.myAlign(key['status'],20) + key['id']
        return msg
    def Get_IIS_Sites(self):
        '''
        返回站点信息列表
        :return: 站点列表
        '''
        rus = self.__Get_API_Message("/api/webserver/websites")['websites']
        msg= self.myAlign('Site_Name', 30) + self.myAlign('Site_Status', 20) + 'Site_ID'
        for key in rus:
            msg += "\r\n" + self.myAlign(key['name'], 30) + self.myAlign(key['status'], 20) + key['id']
        return msg
    def Res_Monitoring(self,api,id=True):
        '''
        应用资源池健康状态，
        :return:
        '''
        Res=self.__Get_Monitoring_Message(api,id)
        self.__Manager_Option()
        try:
            ResObj=Res[self.__Object]
            if ResObj:
                if self.__Option:
                    val=ResObj[self.__Option]
                    return self.__Mon_Return_Mes(val)
                else:
                    return self.Nagios_OK,self.__Get_All_Res(ResObj)
        except KeyError:
            print "No resources found,Please specify the resources that need to be monitored,example:requests:active"
            sys.exit(self.Nagios_Unknown)
    def __Mon_Return_Mes(self,val):
        '''
        对阈值判断进行返回
        :param val: 值
        :return:
        '''
        comcode = self.CompareValue(val)
        if comcode == self.Nagios_Critical:
            status="Critical"
            code=self.Nagios_Critical
        elif comcode == self.Nagios_Warning:
            status = "Warning"
            code = self.Nagios_Warning
        elif comcode == self.Nagios_OK:
            status = "OK"
            code = self.Nagios_OK
        else:
            status = "Unknown"
            code = self.Nagios_OK
        return code,"%s-Resources %s  vlaue is %s |%s=%s" % (status,self.__Option,val,self.__Option,val)
    def __Get_All_Res(self,ResObj):
        '''
        查看指定父资源下面的说有子资源
        :param ResObj: 资源DIC
        :return:
        '''
        msg = "OK-All Resources"
        per = ''
        for key in ResObj:
            msg += ", %s is %s" % (key, ResObj[key])
            per += "%s=%s "% (key, ResObj[key])
        return  msg + '|' + per
    def __Get_Monitoring_Message(self,path,id=True):
        '''
        /api/webserver/application-pools/monitoring/     Message pool Status
        /api/webserver/websites/monitoring/
        :param path: API 路径
        :param id:  对象的ID
        :return:
        '''
        if id:
            if self.IIS_Moint_ID is None:
                print " Object ID must be specified "
                sys.exit(self.Nagios_Unknown)
        else:
            self.IIS_Moint_ID = '' if self.IIS_Moint_ID is None else self.IIS_Moint_ID
        return self.__Get_API_Message(path + self.IIS_Moint_ID)
    def __Manager_Option(self):
        '''
        对父资源以及子资源进行拆分
        example：
         -r requests:active
         self.__Object=requests
         self.__Option=active
         如果子资源没有指定
         self.__Option=False
        :return:
        '''
        if ':' in self.IIS_Moint_Res:
            self.__Object=self.IIS_Moint_Res.split(':')[0]
            self.__Option=self.IIS_Moint_Res.split(':')[1]
        else:
            self.__Object=self.IIS_Moint_Res
            self.__Option=False
    def CompareSymbol(self, value):
        '''
        判断方式拆分
        example:
        :1:  等于
        :1   小于
        1:   大于
        1~5  大于1小于5
        :param value: 阈值
        :return:  比较方式
        '''
        if str(value).count(':') >= 2:
            return "eq"
        elif value[-1:] == ':':
            return "gt"
        elif str(value).count('~') == 1:
            return "rg"
        elif value[:1] == ':':
            return "lt"
        else:
            if str(value).isdigit():
                return "gt"
            else:
                return "un"
    def CompareValue(self, value):
        war_code = False
        cri_code = False
        try:
            if not self.IIS_Monit_OK is None:
                ok_code = self.compare_check(value, self.IIS_Monit_OK)
                if ok_code == 'un':
                    return self.Nagios_Unknown
                else:
                    return self.Nagios_OK if ok_code else self.Nagios_Critical
            if not self.IIS_Moint_Warning is None:
                war_code = self.compare_check(value, self.IIS_Moint_Warning)

            if not self.IIS_Monit_Critical is None:
                cri_code = self.compare_check(value, self.IIS_Monit_Critical)

            if cri_code == 'un' or war_code == 'un': return self.Nagios_Unknown
            if cri_code:
                return self.Nagios_Critical
            elif war_code:
                return self.Nagios_Warning
            else:
                return self.Nagios_OK
        except:
            return self.Nagios_Unknown
    def compare_check(self, value, val):
        return self.Compare(value, val, self.CompareSymbol(val))
    def Compare(self, value, threshold, Compare='gt'):
        '''
        阈值比较，返回是否匹配
        :param value: 需要比较的值
        :param threshold: 阈值指定
        :param Compare: 比较方法
        :return: 返回True或者False
        '''
        threshold = str(threshold).strip(':')
        try:
            if Compare == 'un':
                return 'un'
            elif Compare == 'rg':
                tmplist = threshold.split('~')
                num0 = tmplist[0]
                num1 = tmplist[1]
                if str(value).isdigit():
                    value = int(value)
                    num0 = int(num0)
                    num1 = int(num1)
                if num0 < value and num1 > value:
                    return True
                else:
                    return False
            elif Compare == 'gt':
                if int(value) > int(threshold):
                    return True
                else:
                    return False
            elif Compare == 'lt':
                if int(value) < int(threshold):
                    return True
                else:
                    return False
            else:
                if len(value) == len(threshold):
                    if value in threshold:
                        return True
                    else:
                        return False
                else:
                    return False
        except:
            return 'un'
des="""
Monitoring the operation performance IIS through IIS API
-r Option reference URL
   -m GetAll   https://www.qnjslm.com/ITHelp/467.html
    -m GetSitesMonit https://www.qnjslm.com/ITHelp/471.html
    -m GetPoolMonit https://www.qnjslm.com/ITHelp/469.html
"""
parser = argparse.ArgumentParser(description=des,version='Check_IIS 2017.11.15 v1.1')
parser.add_argument('-H', '--host', help='IIS Host Address or FQDN',default="127.0.0.1")
parser.add_argument('-P', '--port', help='IIS API Manager Port default is 55539',type=int,default=55539)
parser.add_argument('-u', '--user', help='API management authentication user name,domain\username or username ,default administrator',default="administrator")
parser.add_argument('-p', '--password', help="Authentication Password")
parser.add_argument('-t', '--token', help='API Token, Please use the API WEB  Manager page to create ')
parser.add_argument('-m', '--mode', help='option select',default="GetSitesName",choices=['GetPoolsName','GetSitesName','GetPoolMonit','GetSitesMonit','GetAll'])
parser.add_argument('-i', '--id', help='Pool id or Sites id When used GetPoolMonit GetSitesMonit ,id or name Choose one')
parser.add_argument('-n','--name',help='site name or pool name when used GetPoolMonit GetSitesMonit, id or name Choose one',default="Default")
parser.add_argument('-r','--res',help='Resources Name ,default  requests:active ',default="requests:active")
parser.add_argument('-o','--ok',help='OK threshold, priority matching Example[:1 lt 1,1: gt 1,:1: eq 1,2~5 region]')
parser.add_argument('-c','--critical',help='Critical threshold,Example[:1 lt 1,1: gt 1,:1: eq 1,2~5 region]')
parser.add_argument('-w','--warning',help='Warning threshold,Example[:1 lt 1,1: gt 1,:1: eq 1,2~5 region]')
args = parser.parse_args()

if args.password is None:
    print " User authentication password must be specified,default user is administrator"
    sys.exit(3)
if args.token is None:
    print "IIS API token must be specified "
    sys.exit(3)

monitor=IIS_APM_Monitor(args)
(code,message)=monitor.IIS_APM_Main()
print message
sys.exit(code)