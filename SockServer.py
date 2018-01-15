# -*- coding:utf-8 -*-
import socket
import threading
import select
from Lock import Lock,AutoLock
from constdata import const,ThreeState,Error
from Singleton import Singleton
import errno
import time


class ISockServerDelegate(object):
    def SetSockServer(self,sockServer):
        pass
    def OnRecv(self,sock,data):
        pass
    def OnAccept(self,sock,addr):
        pass
    def OnClose(self,sock):
        pass
    def OnError(self,param):
        pass

class RecvParam(object):
    def __init__(self,data,sock):
        self.data = data
        self.sock = sock

class ErrorParam(object):
    def __init__(self,sock,errorCode,errorMsg):
        self.error = {"code":errorCode,"msg":errorMsg}
        self.sock = sock

class ClientObj(object):
    def __init__(self,sock,addr,OnRecvCallBack=None,onErrorCallBack=None,timeout=None):
        self.sock = sock
        self.addr = addr
        self.OnRecvCallBack = OnRecvCallBack
        self.timeout = timeout
        self.startTick = -1
        self.onErrorCallBack = onErrorCallBack
    def SetStartTick(self):
        self.startTick = time.clock()

    def IsTimeout(self):
        if self.startTick != -1 and time.clock() - self.startTick>=self.timeout*1000:
            return True
        return False
    def IsCheckTimeout(self):
        if self.startTick == -1:
            return False
        return True

    def OnRecv(self,data):
        #if self.IsCheckTimeout():
        #    self.startTick = time.clock()
        if self.OnRecvCallBack:
            param = RecvParam(data,self.sock)
            self.OnRecvCallBack(param)
        if self.IsCheckTimeout():
            self.startTick = time.clock()

    def OnError(self,errorCode,errorMsg):
        if self.onErrorCallBack:
            param = ErrorParam(self.sock,errorCode,errorMsg)
            self.onErrorCallBack(param)



class SockServer(Singleton):
    def init(self,addr,delegate):
        self.__addr = addr
        self.__delegate = delegate
        if delegate.SetSockServer:
            delegate.SetSockServer(self)

        self.__clientObj = []
        self.__listenSock = None
        self.__eventSendSock = None

        self.__eventClient = None
        self.__threadEvent = threading.Event()
        self.__threadState = ThreeState.INIT
        self.__tmpClientObj = []        #上锁
        self.__lock = Lock()
    def CreateEventSock(self):
        eventSock = socket.socket()
        try:
            eventSock.connect(("127.0.0.1",9999))
        except Exception as e:
            return
        self.__eventSendSock = eventSock
        self.__listenSock.setblocking(True)
        recvsock, addr = self.__listenSock.accept()
        print "Event sock ",format(addr)
        self.__listenSock.setblocking(False)
        recvsock.setblocking(False)
        eventClient = ClientObj(recvsock,addr,None)
        self.__eventClient = eventClient
        self.__clientObj.append(eventClient)

    def SignSelect(self):
        if self.__eventSendSock:
            self.__eventSendSock.send("sign sock")

    def Send2Addr(self,host,data,OnRecv,OnError,timeout = None):
        sock = socket.socket()
        if timeout != None:
            sock.settimeout(timeout)
        try:
            sock.connect(host)
        except Exception as e:
            if hasattr(e,"message") and e.message == "timed out":
                if OnError:
                    OnError(ErrorParam(sock,Error.TIMEOUT,e))
                return 0,sock
        if timeout != None:
            sock.settimeout(None)

        sock.setblocking(False)
        sendnum = sock.send(data)
        c = ClientObj(sock,host,OnRecv,OnError,timeout)
        self.PushTmpClient(c)
        #self.__clientObj.append(c)
        if OnRecv:
            self.SignSelect()
        return sendnum,sock

    def PushTmpClient(self,c):
        AutoLock(self.__lock)
        self.__tmpClientObj.append(c)
    def SwapTmp2WorkClient(self):
        if len(self.__tmpClientObj) == 0:
            return
        AutoLock(self.__lock)
        self.__clientObj += self.__tmpClientObj
        self.__tmpClientObj = []

    def GetSockArray(self):
        sockArray = []
        checkTimeout = False
        for c in self.__clientObj:
            sockArray.append(c.sock)
            if c.IsCheckTimeout():
                checkTimeout = True
        return sockArray,checkTimeout

    def Start(self):
        listsock = socket.socket()
        listsock.bind(self.__addr)
        listsock.listen(10)
        # 设置为非阻塞
        listsock.setblocking(False)
        self.__listenSock = listsock
        # 初始化将服务端加入监听列表
        self.__clientObj.append(ClientObj(listsock,self.__addr,self.__OnRecv))
        #self.__socketList.append(listsock)
        self.CreateEventSock()
        thread = threading.Thread(target = SockServer.ThreadFunc, args = (self,),name = "jysockThread")
        thread.start()



    def GetClientBySock(self,sock):
        for c in self.__clientObj:
            if c.sock == sock:
                return c
        return None
    def Stop(self):
        if self.__threadState == ThreeState.STOP:
            return


        if self.__delegate:
            self.__delegate.SetSockServer(None)
            self.__delegate = None

        if self.__threadState == ThreeState.START:
            self.__threadEvent.wait()
            self.__threadEvent.clear()
        self.__threadState = ThreeState.STOP



    def __OnAccept(self,sock,addr):
        self.__clientObj.append(ClientObj(sock,addr,self.__OnRecv))
        if self.__delegate.OnAccept:
            self.__delegate.OnAccept(sock,addr)

    def __OnRecv(self,param):
        sock = param.sock
        data = param.data
        if self.__delegate.OnRecv:
            self.__delegate.OnRecv(sock,data)

    def __OnClose(self,sock):
        self.RemoveClientBySock(sock)


    def __GetClient(self,sock):
        for i in range(len(self.__clientObj)):
            if self.__clientObj[i].sock == sock:
                return self.__clientObj[i]
        return None

    def __RemoveClient(self,client):
        if client:
            self.__clientObj.remove(client)
            sock = client.sock
            try:
                sock.close()
            except Exception as e:
                pass
            print("Client {0} disconnect! ".format(client.addr))
            if self.__delegate.OnClose:
                self.__delegate.OnClose(sock)

    def RemoveClientBySock(self,sock):
        client = self.__GetClient(sock)
        self.__RemoveClient(client)

    def CheckTimeout(self):
        for c in self.__clientObj:
            if c.IsTimeout():
                c.OnError(Error.TIMEOUT,"")
                self.__RemoveClient(c)
    def ThreadFunc(self):
        if self.__threadState == ThreeState.START:
            return
        self.__threadState = ThreeState.START
        while True:
            self.SwapTmp2WorkClient()
            sockArray,checkTimeout = self.GetSockArray()
            # 开始 select 监听,对input_list中的服务端server进行监听
            stdinput, stdoutput, stderr = select.select(sockArray, [],[], const.SOCK_TIMEOUT)
            if checkTimeout:
                if len(stdinput) == 0 and len(stdoutput) ==0 and len(stderr) == 0:
                    self.CheckTimeout()
                    continue

            for sock in stderr:
                self.RemoveClientBySock(sock)
                continue
            # 循环判断是否有客户端连接进来,当有客户端连接进来时select将触发
            for sock in stdinput:
                # 判断当前触发的是不是服务端对象, 当触发的对象是服务端对象时,说明有新客户端连接进来了
                if sock == self.__listenSock:
                    # 接收客户端的连接, 获取客户端对象和客户端地址信息
                    recvsock, addr = sock.accept()
                    recvsock.setblocking(False)
                    print("Client {0} connected! ".format(addr))
                    # 将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
                    self.__OnAccept(recvsock,addr)

                else:
                    # 由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(input_list)，客户端发送消息将触发
                    # 所以判断是否是客户端对象触发

                    #新的sock添加到select里来
                    try:
                        print "sock recv ..." + format(sock.getpeername())

                        recvdata = sock.recv(const.RECV_DATA_LEN)
                        print recvdata
                        print "sock recv OK"
                        c = self.GetClientBySock(sock)
                        if c and hasattr(c,"OnRecv"):
                            if c.OnRecv:
                                c.OnRecv(recvdata)

                        if len(recvdata)==0:
                            self.__OnClose(sock)
                            break

                    except Exception as e:
                        if hasattr(e,"errno") and e.errno ==  errno.EWOULDBLOCK:
                            pass
                        c = self.GetClientBySock(sock)
                        if c and hasattr(c,"OnError"):
                            if c.OnError:
                                c.OnError(Error.OTHER_ERROR,e.message)

                        self.__OnClose(sock)
                        print "sock recv " + e.message
                    #except ConnectionResetError:
                        # 客户端断开连接了，将客户端的监听从input列表中移除
                        #self.__OnClose(sock)
        self.__RemoveAllClient()
        self.__threadEvent.set()

    def Send(self,sock,data):
        ret = 0
        try:
            if sock:
                ret = sock.send(data)
        except Exception as e:
            pass
        return ret

    def __RemoveAllClient(self):
        for i in range(len(self.__clientObj)):
            self.__RemoveClient(self.__clientObj[i])
