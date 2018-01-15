# -*- coding:utf-8 -*-

from SockServer import ISockServerDelegate

class LocalMsgObj(ISockServerDelegate):
    def __init__(self,httpRecvDelegate):
        super(LocalMsgObj,self).__init__()
        self.httpDelegate = httpRecvDelegate
        self.sockServer = None
        self.header = {}
        self.body = ""
        self.remoteIp = None
        self.remotePort = None
        self.urlParamDict = {}
        self.uri = ""
        self.sock = None

    def OnRecv(self,sock,data):
        self.sock = sock
        self.remoteIp,self.remotePort  = self.sock.getpeername()
        if self.__DecodeData(data) == False:
            return
        if self.httpDelegate and hasattr(self.httpDelegate,"OnHttpRecv"):
            self.httpDelegate.OnHttpRecv(self)
    def OnError(self,param):
        error = param.error
        errorCode = error.code
        errorMsg  = error.msg

        pass

    def SetSockServer(self,sockServer):
        self.sockServer = sockServer

    def __GetHttpResponseContent(self,data):
        return '''HTTP/1.0 200 OK\r\nAccess-Control-Allow-Credentials:true\r\nAccess-Control-Allow-Origin:*\r\nConnection: close\r\nAccept-Ranges:byte\r\nContent-Length:%d\r\nContent-Type:application/json\r\nServer:Apache/2.4.23 (Win32) OpenSSL/1.0.2h PHP/5.6.28\r\n\r\n%s''' % (len(data),data)

    def Send(self,data):
        responseContent = self.__GetHttpResponseContent(data)
        if self.sockServer:
            self.sockServer.Send(self.sock,responseContent)

    def __DecodeData(self,data):
        pos1 = data.find("\r\n\r\n")
        if pos1 == -1:
            return False
        headerstr = data[0:pos1]
        lineArray = headerstr.split("\r\n")
        if len(lineArray)<=0:
            return False

        firstArray = lineArray[0].split(" ")
        if len(firstArray) != 3:
            return False

        self.header["method"] = firstArray[0]
        uri = firstArray[1]
        pos = uri.find("?")
        urlEnd = ""
        if pos != -1:
            paramArrayStr = uri[pos+1:]
            paramArray = paramArrayStr.split("&")
            for paramStr in paramArray:
                keyValue = paramStr.split("=")
                if len(keyValue) == 2:
                    self.urlParamDict[keyValue[0]] = keyValue[1]
                elif len(keyValue) == 1:
                    self.urlParamDict[keyValue[0]] = ""
            self.uri = uri[0:pos]
        else:
            self.uri = uri



        self.header["httptype"] = firstArray[2]
        for i in range(1,len(lineArray)):
            posline = lineArray[i].find(":")
            key = ""
            value = ""
            if posline == -1:
                return False
            key = lineArray[i][0:posline]
            if len(lineArray[i])>posline+1:
                value = lineArray[i][posline+1:]

            key = key.strip()
            value = value.strip()
            self.header[key] = value

        if pos1+4<len(data):
            self.body = data[pos1+4:]

    def Stop(self):
        if self.sockServer:
            self.sockServer.RemoveClientBySock(self.sock)
            self.sock = None
        self.sockServer = None
