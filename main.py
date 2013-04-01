import Image,numpy
from StringIO import StringIO
import time,sched
import cv2
import autofetch as AF
import recognition as RG
PRECODE=''
OPENVPNSVR=AF.OPENVPNSVR
PWDFILE={}
RUNINFO={'errorn':1,'usages':(),'svrid':0,'u_error_count':0}
def run():
    global OPENVPNSVR,RUNINFO,PRECODE
    svrid = RUNINFO['svrid']
    sName,sImg=OPENVPNSVR[svrid],''
    #get usages
    if RUNINFO['u_error_count'] > 10:
        RUNINFO['usages'] = AF.getLeftTime(sName,1)
        RUNINFO['u_error_count'] = 0
    else:
        RUNINFO['usages'] = AF.getLeftTime(sName)
    if not (RUNINFO['errorn'] & 1<<4):
        return None
    # get pwd
    if RUNINFO['errorn'] &  1<<1:
        svrInfos = AF.fetchOpenvpn(sName,1)
        RUNINFO['errorn'] -= 1<<1
    else:
        svrInfos = AF.fetchOpenvpn(sName)
    for _s in svrInfos:
        if _s[0] == OPENVPNSVR[svrid]:
            sName,sImg = _s
    if sImg == '':
        #re-run
        RUNINFO['errorn'] += 1<<1
        return None
    #resolve the num
    imgPwd = RG.resolveNum(sImg)
    #write pwd
    if PRECODE != imgPwd :
        pwdFile = 'password.txt'
        fnObj = open(pwdFile,'w')
        fnObj.write('tenacy\n')
        fnObj.write(imgPwd)
        fnObj.close()
        #things all done
        RUNINFO['errorn'] += 1<<2
        PRECODE = imgPwd
    else:
        # wait
        RUNINFO['errorn'] += 1<<3
    RUNINFO['errorn'] -= 1<<4
if __name__ == '__main__':
    scheduler = sched.scheduler(time.time,time.sleep)
    RUNINFO['errorn'] += 1<<4
    run()
    while True:
        _u=RUNINFO['usages']
        _e=RUNINFO['errorn']
        _t=0
        if _e & 1<<1 :
            print 're-start'
            run()
            continue
        if _u and len(_u) > 1:
            print u"使用情况:",_u['usage']
            print u"剩余时间:",_u["ltime"]
            lt = _u["ltime"]
            if lt > 2:
                print u"等待%d秒更新密码"%((lt-1.5)*60),' curtime:',int(time.time())
                #scheduler.enter((lt-1.5)*60,1,run,())
                _t=(lt-1.5)*60
            elif lt >0 and lt < 2:
                print u"密码即将过期，30s后获取密码",' curtime:',int(time.time())
                #scheduler.enter(30,1,run,())
                _t=30
            else:
                print u"密码即将过期，15秒后获取密码",' curtime:',int(time.time())
                #scheduler.enter(15,1,run,())
                _t=15
            RUNINFO['errorn'] += 1<<4
            if RUNINFO['errorn'] & 1<<3: RUNINFO['errorn']-= 1<<3
            if RUNINFO['errorn'] & 1<<2: RUNINFO['errorn']-= 1<<2
            time.sleep(_t)
            run()
        else:
            RUNINFO['u_error_count'] += 1
            if _e & 1<<3:
                print u"未更新密码，等待15秒",'curtime:',int(time.time())
                #scheduler.enter(15,1,run,())
                _t=15
                RUNINFO['errorn'] += 1<<4
                RUNINFO['errorn']-= 1<<3
            if _e & 1<<2:
                print u"成功获取密码，等待30秒后获取使用情况",' curtime:',int(time.time())
                #scheduler.enter(30,1,run,())
                _t=30
                RUNINFO['errorn']-= 1<<2
            time.sleep(_t)
            run()
        #scheduler.run()   
