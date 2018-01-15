# -*- coding:utf-8 -*-
from Singleton import Singleton
from SockServer import SockServer
from urlparse import urlparse
import socket
from GlobalFunc import GlobalFunc
import threading
from Lock import Lock,AutoLock
from constdata import Error
import time
from Lock import AutoLock,Lock
class HttpTask(object):
    g_id = 0
    STATE = {"init":0,"run":1,"stop":2}
    def __init__(self,manager,url,urlparam,headerDict,postData,method,OnRecvCallBack,OnErrorCallBack,funcParam,timeout):
        self.id = HttpTask.g_id
        HttpTask.g_id += 1
        self.__OnRecvCallBack = OnRecvCallBack
        self.__OnErrorCallBack = OnErrorCallBack
        self.url = url
        self.param = urlparam
        self.postData = postData
        self.method = method
        self.dataCache = ""
        self.dataLen = -1
        self.header = ""
        self.body = None
        self.headerDict = {}
        self.manager = manager
        self.funcParam = funcParam
        self.bRecvCalled = False
        self.timeout = timeout
        self.sock = None
        self.startTick = None
        self.headerDict = headerDict

        self.state = HttpTask.STATE.init

        print "Create Http Task(%d) url:(%s)" %(self.id,self.url)
    def __del__(self):
        print "Destroy Http Task(%d)" %(self.id)
        self.CloseSock()

    def SetStartTick(self,startTick):
        self.startTick = startTick
        pass


    def JumpUrl(self,url,paramsFunc,referUrl):
        headerDict = {"Referer" : referUrl}
        self.manager.CreateTask(url,None,headerDict,None,"GET",self.__OnRecvCallBack,self.__OnErrorCallBack,paramsFunc,self.timeout)

    def CloseSock(self):
        if self.sock:
            try:
                self.sock.close()
                self.sock = None
            except Exception as e:
                pass
    def OnRecv(self,param):
        print "HttpTask Recv %d" % (self.id)
        if self.bRecvCalled:
            return
        data = param.data
        self.__AppendData(data)
        if self.__IsDataRecvFinish():
            self.bRecvCalled = True
            if self.headerDict["status"] == '302':
                referUrl = GlobalFunc.GetFullUrl(self.url,self.param)
                self.JumpUrl(self.headerDict["Location"],self.funcParam,referUrl)
                self.manager.RemoveTask(self)
                return


            param.status = self.headerDict["status"]
            param.url = self.url
            param.param = self.funcParam
            param.data = self.body

            self.__OnRecvCallBack(param)
            self.manager.RemoveTask(self)

    def Start(self):
        if self.IsRun():
            return
        self.state = HttpTask.STATE.ing

        fullUrl = GlobalFunc.GetFullUrl(self.url,self.param)
        urlObj= urlparse(fullUrl)
        data = self.GetHttpInfo(self.headerDict,urlObj,self.postData,self.method)
        #print data
        addr = self.GetAddrByUrl(urlObj)

        print "CreateTask %d %s" % (self.id,data)
        sendnum,sock = SockServer().Send2Addr(self.addr,data,self.OnRecv,self.OnError,self.timeout)
        self.sock = sock

    def GetState(self):
        return self.state


    def OnError(self,param):
        errorCode = param.error.code
        errorMsg  = param.error.msg
        sock = param.sock
        print "HttpTask Remove (%s,%s)" % (errorCode,errorMsg)
        self.manager.RemoveTask(self)

    def __AppendData(self,data):
        self.dataCache += data
        if data == "":
            self.__RecvEnd()
        else:
            self.__DecodeData()




    def __DecodeHeader(self,header):
        self.headerDict = GlobalFunc.GetHeaderDict(header)


    def __DecodeData(self):
        if self.header == "":
            pos1 = self.dataCache.find("\r\n\r\n")
            if pos1 != -1:
                self.header = self.dataCache[0:pos1]
                self.dataCache = self.dataCache[pos1+4:]
                self.__DecodeHeader(self.header)
            else:
                return False
        if self.headerDict.get("Content-Length"):
            self.dataLen = int(self.headerDict["Content-Length"])
        else:
            pass

        if self.dataLen != -1:
            if len(self.dataCache) == self.dataLen:
                self.body = self.dataCache
                return True
        return False

    def __RecvEnd(self):
        if self.body == None:
            self.body = self.dataCache
        self.manager.RemoveTask(self)


    def __IsDataRecvFinish(self):
        if self.body != None:
            return True
        else:
            return False

    def IsTimeout(self):
        if time.clock()<=self.startTick:
            return True
        return False

    def IsRun(self):
        return self.state != HttpTask.state.init

    def IsStop(self):
        return self.state == HttpTask.state.stop



class HttpTaskManager(Singleton):
    def __init__(self):
        pass

    def __SwapTmp2WorkTask(self):
        AutoLock(self.lock)
        self.taskManager += self.tmpTaskManger
        self.delayTaskManager += self.delayTmpTaskManager
        self.tmpTaskManger = []
        self.delayTaskManager = []

    def __PushTask2Tmp(self,task):
        AutoLock(self.lock)
        self.tmpTaskManger.append(task)

    def init(self):
        self.lock = Lock()
        self.taskManager = []
        self.tmpTaskManger = []
        self.delayTaskManager = []
        self.delayTmpTaskManager = []
        self.taskLock = Lock()
        self.thread = None
        self.stop = False
        self.Start()
    def Start(self):
        thread = threading.Thread(target = HttpTaskManager.Update, args = (self,),name = "jysockThread")
        thread.start()

    '''
    def OnRecv(self,id,data):
        #print data
        httpTask = self.GetHttpTask(id)
        if httpTask == None:
            return
        httpTask.AppendData(data)
    '''
    def Stop(self):
        self.stop = True


    def __CheckDelayTask(self):
        for delayTask in self.delayTaskManager:
            if self.IsTimeout():
                self.taskManager.append(delayTask)
    def __DealTask(self):
        removeTaskArray = []
        for task in self.taskManager:
            if not task.IsRun():
                task.Start()
            elif task.IsStop():
                removeTaskArray.append(task)

        for task in removeTaskArray:
            try:
                self.RemoveTask(task)
            except:
                pass



    def Update(self):
        while(self.stop == False):
            self.__SwapTmp2WorkTask()
            self.__CheckDelayTask()
            self.__DealTask()



    def GetHttpInfo(self,headerDict,urlObj,body,method):
        uri = ""
        if urlObj.query == "":
            uri = urlObj.scheme + "://" + urlObj.hostname + urlObj.path
        else:
            uri = urlObj.scheme + "://" + urlObj.hostname + urlObj.path + "?" + urlObj.query

        defaultHeaderDict = {
            "Host" : urlObj.hostname,
            "Accept": "*/*",
            "Accept-Language": "zh-CN",
            "Content-Type": "application/x-www-form-urlencoded",
            #"Content-Type": "text/html; charset=UTF-8",
            "Connection": "Close",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"
        }

        if headerDict != None:
            for key in headerDict:
                defaultHeaderDict[key] = headerDict[key]

        if method == "POST":
            defaultHeaderDict["Content-Length"] = len(body)

        return GlobalFunc.GetHttpHeader(defaultHeaderDict,uri,body,method)


    def GetAddrByUrl(self,urlObj):
        host = urlObj.hostname
        port = urlObj.port
        ip = socket.gethostbyname(host)
        if port == None:
            port = 80
        return (ip,port)



    def CreateTask(self,url,urlparam,header,body,method,OnRecvFunc,OnErrorFunc,funcParam=None,timeout=None):

        httpTask = HttpTask(self,url,urlparam,header,body,method,OnRecvFunc,OnErrorFunc,funcParam,timeout)
        self.AddTask(httpTask)

    def AddTask(self,httpTask):
        AutoLock(self.taskLock)
        print "Add task %d..." % (httpTask.id)
        self.taskManager.append(httpTask)
    def RemoveTask(self,httpTask):
        print "Remove task %d..." % (httpTask.id)
        AutoLock(self.taskLock)
        try:
            self.taskManager.remove(httpTask)
        except:
            pass




    def GetHttpTask(self,id):
        for httptask in self.taskManager:
            if httptask.id == id:
                return httptask
        return None






