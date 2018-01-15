# -*- coding:utf-8 -*-

from SessionManager import SessionManager

class IHttpRecvDelegate(object):
    def __init__(self):
        pass
    def OnHttpRecv(self,httpRecvObj):
        pass

class WXMsgObj(IHttpRecvDelegate):
    def __init__(self):
        super(WXMsgObj,self).__init__()
        pass

    def OnHttpRecv(self,httpObj):
        if httpObj.header["method"] == "GET":
            action = httpObj.urlParamDict.get("action")
            if action  == "user_new":
                userId = httpObj.urlParamDict.get("userid")
                s = SessionManager().CreateSession(userId,httpObj)
                if s:
                    s.Start()
            elif action == "user_close":
                userId = httpObj.urlParamDict.get("userid")
                SessionManager().StopSession(userId)

                #itchat.auto_login()


        if httpObj.header["method"] == "POST":
            pass