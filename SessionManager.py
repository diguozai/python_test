# -*- coding:utf-8 -*-
import sys
from Session import Session
from Singleton import Singleton
class SessionManager(Singleton):
    def __init__(self):
        self.sessionArray = []
    def __del__(self):
        pass
    def GetSession(self,userId):
        for i in range(len(self.sessionArray)):
            if self.sessionArray[i].GetUserId() == userId:
                return self.sessionArray[i]

        return None

    def CreateSession(self,userId,httpObj):
        s = Session(userId,httpObj)
        self.sessionArray.append(s)
        return s

    def StopSession(self,userId):
        s = self.GetSession(userId)
        if s:
            s.Stop()
