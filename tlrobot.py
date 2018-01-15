# -*- coding: utf-8 -*-
import json
from HttpSend import HttpSend

class TlRobot:
    def __init__(self):
        self.apikey = 'f3c79dd7a0114ebe97a78500c44f16a3'
        self.apiurl = 'http://www.tuling123.com/openapi/api'
        self.userid = '1111'
        self.httpObj = HttpSend()
    def chat(self,conversition):
        retData = self.httpObj.post(self.apiurl,None,self.__getDataDict(conversition))
        if isinstance(retData,basestring):
            retDataDict = json.loads(retData)
            return retDataDict
        return None

    def __getDataDict(self,conversition):
        return {"key":self.apikey,"info":conversition,"userid":self.userid}

