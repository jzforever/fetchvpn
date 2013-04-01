import cv2,os
from numpy import *
from math import sqrt
from time import time
SERVER={'horikita':'','tephany':'','taccola':'','belle':'','blanche':'','bonvila':'','dabon':'','masse':'','mace':'','maria':'','brigit':'','orlene':''}
def genNum(srcimg,name='unnamed'):
    """the shape of srcimg is (30,220,3)
    @return 从图片中分离出的数字个数
    @remark 
    """
    gray=cv2.cvtColor(srcimg,cv2.COLOR_BGR2GRAY)
    #row,col=gray.shape
    resultNumImg=[]
    
    def findRow(subimg):
        row,col=subimg.shape
        _si=0
        _f=False
        for i in range(row):
            _countw=0
            for j in range(col):    
                if (not _f) and subimg[i][j] != 255:
                    _countw+=1
                    if _countw>2:
                        _si=i
                        _f=True
                        _countw=0
                if _f and subimg[i][j] == 255:
                    _countw+=1
                if _f and (_countw == col or i==row):
                    #find i
                    _i=i
                    if _precountw>col-3:
                        _i=i-1
                    return subimg[_si:_i]
            _precountw=_countw
        return None
    def findCol(subimg):
        row,col=subimg.shape
        _sj=0
        _f=False
        _offsetj=0
        for j in range(col):
            _countw=0
            for i in range(row):
                if (not _f) and subimg[i][j] != 255:
                    #start j
                    _countw+=1
                    if _countw>2:
                        _sj=j
                        _f=True
                        _countw=0
                if _f and subimg[i][j] ==255:
                    _countw+=1
                if _f and (_countw == row or j==col):
                    #find the end j,not include j
                    _j=j
                    if _precountw > row-3 and j-_sj>3:
                        _j=j-1
                    _simg1=arange(row*(_j-_sj)).reshape(row,_j-_sj)
                    for ii in range(row):
                        _simg1[ii]=subimg[ii][_sj:_j]
                    #return _simg1
                    _finimg=findRow(_simg1)
                    if _finimg is not None:
                        resultNumImg.append(_finimg)
                    _f=False
            _precountw=_countw
    findCol(gray)
    for i in range(len(resultNumImg)):
        cv2.imwrite("./sepnum/"+name+"_"+str(i)+'.png',resultNumImg[i])
    return resultNumImg
    
def genSamples():
    dir='test/'
    fns=os.listdir(dir)
    for fn in fns:
        if fn.find('.png')>-1:
            src=cv2.imread(dir+fn)
            genNum(src,fn[:fn.find('.')])

def fetchVec(srcimg):
    """ return a feature vector (_p1,_p2,_p3,_p4)"""
    gray=srcimg
    row,col=gray.shape
    _p1,_p2,_p3=0,0,0
    _pp1,_pp2,_pp3=0,0,0
    vr,vc = 1.0*row/2,1.0*col/2
    for i in range(row):
        for j in range(col):
            if gray[i][j] != 255:
                if i<row/2+1:
                    _p1+=1
                if j<col/2+1:
                    _p2+=1
                if i>row/2:
                    _pp1+=sqrt(pow(i-vr,2)+pow(j-vc,2))
                if j>col/2:
                    _pp2+=sqrt(pow(i-vr,2)+pow(j-vc,2))
    _p1=1.0*_p1/(row//2*col)
    _p2=1.0*_p2/(row*(col//2))
    if _p1*_p2==0:
        _p3=0
    else:
        _p3=_p1/_p2
    _pp1=_pp1/(col*(row-row//2))/col
    _pp2=_pp2/((col-col//2)*row)/col
    if _pp1*_pp2==0:
        _pp3=0
    else:
        _pp3=_pp1/_pp2
    return (_p1,_p2,_p3,_pp1,_pp2,_pp3)

def readFeatures():
    _f=[]
    for i in range(10):
        fobj=open("sepnum/features/%d_vecF.txt"%i,'r')
        l=fobj.readline()
        l.strip()
        v=[float(x) for x in l.split()]
        _f.append(tuple(v))
    return tuple(_f)

def nearestNum(obj,features):
    #欧拉距离
    f=features
    dis=[]
    for ind in range(10):
        _d=sqrt(sum([pow(f[ind][i]-obj[i],2) for i in range(6)]))
        dis.append((_d,ind))
    dis.sort(cmp=lambda x,y:cmp(x[0],y[0]))
    #print '========='
    #for i in dis:
    #    if i[0]-dis[0][0]>0.15:
    #        break
    #    if dis.index(i)>2:
    #        break
    #    print 'num:',i[1],'dis:',i[0],';',
    return dis[0][1]

def resolveNum(srcimg):
    f=readFeatures()
    #srcimg=cv2.imread(imgname)
    subimgs=genNum(srcimg,str(int(time())))
    code=[]
    for _img in subimgs:
        #check 1
        r,c=_img.shape
        if c<5:
            code.append('1')
            continue
        #check *
        if r<10:
            code.append('*')
            continue
        _v=fetchVec(_img)
        code.append(str(nearestNum(_v,f)))
    return ''.join(code)

def genFeatures():
    for i in range(10):
        genFeature(i)

def genFeature(num):
    vec=[]
    imgdir='sepnum/%d'%num
    fns=os.listdir(imgdir)
    for fn in fns:
        img=cv2.imread(imgdir+'/'+fn)
        if img is None:
            break
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        _v=fetchVec(gray)
        vec.append(_v)
    l=len(vec)
    v0=sum([v[0] for v in vec])/l
    v1=sum([v[1] for v in vec])/l
    v2=sum([v[2] for v in vec])/l
    v3=sum([v[3] for v in vec])/l
    v4=sum([v[4] for v in vec])/l
    v5=sum([v[5] for v in vec])/l
    fobj=open("sepnum/features/%d_vecF.txt"%num,'w')
    fobj.write("%s %s %s %s %s %s\n"%(v0,v1,v2,v3,v4,v5))
    fobj.close()
    print "%s %s %s %s %s %s"%(v0,v1,v2,v3,v4,v5)

if __name__=='__main__':
    #svrs=sorted(SERVER)
    #for s in svrs:
    #   testA(s+'.png')
    pass