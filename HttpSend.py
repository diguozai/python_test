# -*- coding: utf-8 -*-
import urllib2
import logging
import json
proxy_ip = {
    "http":"dev-proxy.oa.com:8080",
    "https":"dev-proxy.oa.com:8080"
}
proxy_ip = None

class HttpSend:
    def __init__(self):
        pass

    def post(self,url,header,data,proxy=proxy_ip):

        data = self.__getHtmlData(url,{'Content-Type':'application/json'},data,"POST",proxy)
        return data
    def get(self,url,header,data,proxy=proxy_ip):
        data = self.__getHtmlData(url,header,data,"GET",proxy)
        pass

    def __getFullUrl(self,url,data):
        if data == None or data == '':
            return url
        if isinstance(data,(str,unicode)):
            hasQuestionChar = False
            if url.find('?') != -1:
                hasQuestionChar = True

            if hasQuestionChar:
                if len(data)>0:
                    if data[0] == '&' or data[0] == '?':
                        data = data[1,len(data)-1]
            else:
                if len(data)>0:
                    if data[0] == '&':
                        data[0] = '?'
                    elif data[0] == '?':
                        pass
                    else:
                        data = '?'+data

            return url + data
        elif isinstance(data,dict):
            hasQuestionChar = False
            realUrl = url
            if realUrl.find('?',0) != -1:
                hasQuestionChar = True
            for key in data:
                oneItem = key+"="+data[key]
                if hasQuestionChar == False:
                    realUrl = realUrl + "?" + oneItem
                    hasQuestionChar = True
                else:
                    realUrl = realUrl + "&" + oneItem
            return realUrl

        raise Exception( "http param \'data\' type %s not support", type(data).__name__)

    def __getHtmlData(self,url,headers,data,method,proxy=None):
        realUrl = url
        urlLen = len(url)
        if (urlLen>=4 and realUrl[0:4]=="http") or (urlLen>=5 and realUrl[0:5]=="https"):
            pass
        else:
            realUrl = "http://" + realUrl
        try:
            if method == 'GET':
                realUrl = self.getFullUrl(realUrl,data)
                data= None
            elif method == 'POST':
                pass
                if isinstance(data,dict):
                    data = json.dumps(data)

            if headers is None:
                headers = {}

            handlers = urllib2.ProxyHandler(proxy)
            opener =  urllib2.build_opener(handlers)

            req = urllib2.Request(realUrl, data,headers=headers)
            for key in headers:
                req.add_header(key,headers[key])
            response = opener.open(req)
            resData  = response.read()


        except Exception as e:
            logging.error(e.message)
            return ""
        return resData

