# IIS-AMP-Monitor
通IIS API监控IIS站点性能，单个站点或者应用池的CPU\MEM\CACHE\DISK\REQUESTS\NETWORK

##版本说明
    v1.1(2017年11月09日)
        初期版本,基于Python2.6开发
        需要python额外支持组件，BeautifulSoup 、ntlm 
        
    v2.1(2017年12月22日)
        基于python3.6进行更改，舍弃NTML认证
        需要python额外支持组件，requests
    
    v2.2(2017年12月23日)
        为了安全，重新加入NTML认证,并进行了一部分代码风格优化
        需要python额外支持组件，requests,requests_ntlm    
    

##安装说明
   **在windows上**
   
    可以通过以下连接进行下载使用,不需要python环境，
    不需要python依赖包,下载后可直接使用
    https://github.com/dcl-lily/IIS-AMP-Monitor/release
    
   **在Linux上**
    
    #yum install git
    #git clone https://github.com/dcl-lily/IIS-AMP-Monitor
    #cd IIS-AMP-Monitor/
    #chmod 700 check_iis.py 
    #./check_iis.py
    
   > 注意：
        需要python3.0以上版本，和 requests模块
        
   **客户端设置，IIS服务器设置**
   
    软件安装参考 https://www.qnjslm.com/ITHelp/629.html
    不推荐使用直接使用管理员账号进行连接，推荐使用普通账号，设置参考如下
    https://www.qnjslm.com/ITHelp/645.html
        
##使用方法

获取帮助:`check_iis.exe -h`
    
    usage: check_iis.exe [-h] [-H HOST] [-P PORT] [-t TOKEN]
                        [-m {GetPoolsName,GetSitesName,GetPoolMonit,GetSitesMonit,GetAll}]
                        [-i ID] [-n NAME] [-r RES] [-o OK] [-c CRITICAL]
                        [-w WARNING]


    Monitoring the operation performance IIS through IIS API -r Option reference URL 
    -m GetAll https://www.qnjslm.com/ITHelp/467.html 
    -m GetSitesMonit https://www.qnjslm.com/ITHelp/471.html 
    -m GetPoolMonit https://www.qnjslm.com/ITHelp/469.html

    optional arguments:
      -h, --help            show this help message and exit
      -H HOST, --host HOST  IIS Host Address or FQDN
      -P PORT, --port PORT  IIS API Manager Port default is 55539
      -t TOKEN, --token TOKEN
                            API Token, Please use the API WEB Manager page to
                            create
      -m {GetPoolsName,GetSitesName,GetPoolMonit,GetSitesMonit,GetAll}, --mode {GetPoolsName,GetSitesName,GetPoolMonit,GetSitesMonit,GetAll}
                            option select
      -i ID, --id ID        Pool id or Sites id When used GetPoolMonit
                            GetSitesMonit ,id or name Choose one
      -n NAME, --name NAME  site name or pool name when used GetPoolMonit
                            GetSitesMonit, id or name Choose one
      -r RES, --res RES     Resources Name ,default requests:active
      -o OK, --ok OK        OK threshold, priority matching Example[:1 lt 1,1: gt
                            1,:1: eq 1,2~5 region]
      -c CRITICAL, --critical CRITICAL
                            Critical threshold,Example[:1 lt 1,1: gt 1,:1: eq
                            1,2~5 region]
      -w WARNING, --warning WARNING
                            Warning threshold,Example[:1 lt 1,1: gt 1,:1: eq 1,2~5
                            region]
   
##example,示例

- 获取站点列表，其中的id是我们需要的

    `check_iis.exe -H win.qnjslm.com -t {token} -m GetSitesName`
    
        Site_Name  Site_Status  Site_ID 
        Default Web Site  started  csqZ4fqinXCrReD-UQA4og
        
 
- 获取应用程序池名，ID是我们需要的

    `check_iis.exe -H win.qnjslm.com -t {token} -m GetpoolsName`
    
        Pool_Name                     Pool_Status         Pool_ID
        DefaultAppPool                started             y1nelK4FGdutrCX7rYgL-Q 
        
- 获取站点的当前的连接数

    `check_iis.exe -H win.qnjslm.com -t {token} -m GetSitesMonit -i csqZ4fqinXCrReD-UQA4og -r requests:active`  
    
        OK-Resources active  vlaue is 0 |active=0 
        
- 获取应用当前进程状态

    `check_iis.exe -H win.qnjslm.com -t {token} -m GetPoolMonit -i y1nelK4FGdutrCX7rYgL-Q -r cpu:threads`
    
        OK-Resources threads  vlaue is 0 |threads=0
        
- 告警阈值设置非常灵活，参考说明

    `check_iis.exe -H win.qnjslm.com -t {token} -m GetPoolMonit -i y1nelK4FGdutrCX7rYgL-Q -r cpu:threads --ok=1`
    
    `check_iis.exe -H win.qnjslm.com -t {token} -m GetPoolMonit -i y1nelK4FGdutrCX7rYgL-Q -r cpu:threads --ok=1~5`
    
    `check_iis.exe -H win.qnjslm.com -t {token} -m GetPoolMonit -i y1nelK4FGdutrCX7rYgL-Q -r cpu:threads --ok=:1`
    
    `check_iis.exe -H win.qnjslm.com -t {token} -m GetPoolMonit -i y1nelK4FGdutrCX7rYgL-Q -r cpu:threads -w 8 -c 15`
    
    `check_iis.exe -H win.qnjslm.com -t {token} -m GetPoolMonit -i y1nelK4FGdutrCX7rYgL-Q -r cpu:threads -w :8 -c :15`
    
    