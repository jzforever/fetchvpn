import httplib
import urllib2
import numpy
from cv2 import imshow,imdecode,CV_LOAD_IMAGE_COLOR,destroyWindow,waitKey
GAEPROXY={'http':'127.0.0.1:8000'}
COOKIE={}
DOMIN_SUFFIX="leet.la"
SERVER={'horikita':'','tephany':'','taccola':'','belle':'','blanche':'','bonvila':'','dabon':'','masse':'','mace':'','maria':'','brigit':'','orlene':''}
KEY = ''
OPENVPNSVR=["horikita","tephany","taccola"]
CAPTCHA = ''
STR_USERS = u"伺服使用量"
STR_LTIME = u"大約"
STR_RTIME = u"分鐘後失效"
def findk(line):
    pos=line.find('var k =')
    if pos>-1:
        sline=line[pos+3:]
        fline=sline[:sline.index(';')]
        n,k=fline.split('=')
        k=k[k.index('"')+1:]
        k=k[:k.index('"')]
        #get rid off the 16th char
        k=k[:15]+k[16:]
        return k
    return False
def setProxy():
    global GAEPROXY
    proxy_handler=urllib2.ProxyHandler(GAEPROXY)
    opener=urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
def getLeftTime(servername='horikita',newcap = False):
    global CAPTCHA,KEY
    servername+='.leet.la'
    if not KEY:
        KEY=getKey()
    if (not CAPTCHA) or newcap:
        resp = doRequest('http://tenacy.leet.la/wp-content/themes/Tenacy-3/captcha/captcha.php')
        imgdata = resp.read()
        resp.close()
        npimg = numpy.fromstring(imgdata,numpy.uint8)
        cvimg = imdecode(npimg,CV_LOAD_IMAGE_COLOR)
        imshow('captcha',cvimg)
        waitKey()
        CAPTCHA = raw_input("captcha:\n")
        destroyWindow('captcha')
    resp = doRequest("http://tenacy.leet.la/async-public?k=%s&c=%s"%(KEY,CAPTCHA))
    data = resp.read()
    resp.close()
    #find usage and left time
    re={}
    udata=data.decode('utf-8')
    #return udata
    _spos = udata.find(servername)
    if _spos == -1:
        return None
    _ps = udata.find(STR_USERS,_spos)+len(STR_USERS)+1
    if _ps < len(STR_USERS)+1:
        return None
    _pn = udata.find('<',_ps)
    _sub1 = udata[_ps:_pn]
    _sub1 = _sub1.strip()
    #print _sub1
    _u,_a = _sub1.split('/')
    re['usage'] = (int(_u),int(_a))
    
    _ps = udata.find(STR_LTIME,_spos)+len(STR_LTIME)
    _pn = udata.find(STR_RTIME,_ps)
    _sub2 = udata[_ps:_pn]
    re['ltime'] = int(_sub2)
    #return data
    #print data
    return re
def doRequest(url,data=None,headers=None):
    global COOKIE
    request=urllib2.Request(url)
    #data
    #headers
    if headers:
        for h in headers:
            request.add_header(h,headers[h])
    request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11')
    request.add_header('Accept-Charset','utf-8;q=0.7,*;q=0.3')
    cookie=''
    for key in COOKIE:
        cookie+='%s=%s'%(key,COOKIE[key])
    if cookie:
        request.add_header('Cookie',cookie)
    return urllib2.urlopen(request)
def getKey():
    global COOKIE,KEY
    resp=doRequest('http://tenacy.leet.la')
    msg=resp.info()
    scl=msg.getallmatchingheaders('set-cookie')
    #print scl
    for sc in scl:
        l=sc
        l=l[l.find(':')+1:l.find(';')]
        l.strip()
        print l
        if l.find('=')>-1:
            k,v=l.split('=')
            COOKIE[k]=v

    data=resp.read()
    resp.close()
    k=findk(data)
    #for line in lines:
    #    k=findk(line)
    #   if k:
    #        print k
    #        break
    if not k:
        print 'not found!'
    KEY = k
    return k
def getPWD(svr):
    global KEY
    if not KEY:
        KEY = getKey()
    headers={'Referer':'http://tenacy.leet.la/','Host':'tenacy.leet.la'}
    resp=doRequest('http://tenacy.leet.la/free-password?svr=%s&k=%s'%(svr,KEY))
    obj=resp.read()
    #print obj
    resp.close()
    fobj=open(svr+'.png','wb')
    fobj.write(obj)
    fobj.close()
    npImg = numpy.fromstring(obj,numpy.uint8)
    cvImg = imdecode(npImg,CV_LOAD_IMAGE_COLOR)
    return cvImg

def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial
    return inner

httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)
def fetchall(newcon=False):
    global KEY,OPENVPNSVR,COOKIE
    if newcon:
        COOKIE={}
        KEY=''
    svrnames=sorted(SERVER)
    re = []
    if not KEY:
        KEY=getKey()
    for svr in svrnames:
        pwdimg=getPWD(svr)
        re.append((svr,pwdimg))
    return re    
def fetchOpenvpn(svrname='',newcon=False):
    global KEY,OPENVPNSVR,COOKIE
    if newcon :
        COOKIE={}
        KEY=''
    re=[]
    if not KEY:
        KEY=getKey()
    if svrname == '':
        for svr in OPENVPNSVR:
            pwdimg=getPWD(svr)
            re.append((svr,pwdimg))
    else:
        pwdimg=getPWD(svrname)
        re.append((svrname,pwdimg))
    return re
if __name__=='__main__':
    fetchall()
    #getKey()
    #data = getLeftTime()
    #pass