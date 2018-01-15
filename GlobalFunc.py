# -*- coding: utf-8 -*-
class GlobalFunc(object):

    @staticmethod
    def GetHttpHeader(headerDict,uri,body,method):
        headerStr = ""
        if method.upper() == "GET":
            headerStr = "GET %s HTTP/1.1\r\n" % (uri)
        else:
            headerStr = "POST %s HTTP/1.1\r\n" % (uri)

        if headerDict != None:
            for key in headerDict:
                headerStr += ("%s: %s\r\n" % (key,headerDict[key]))

        headerStr += ("\r\n%s" % (body)  )

        return headerStr


    @staticmethod
    def WriteFile(path,data):
        f = open(path,"wb")
        f.write(data)
        f.close()
    @staticmethod
    def ReadFile(self,path):
        f = open(path,"rb")
        data = f.read()
        f.close()
        return data
    @staticmethod
    def GetHeaderDict(headerStr):
        headerDict = {}
        lineArray = headerStr.split("\r\n")
        if len(lineArray)<=0:
            return headerDict
        for i in range(len(lineArray)):
            line = lineArray[i]
            if i == 0:
                statusArray = line.split(" ")
                headerDict["status"] = statusArray[1]
            else:
                posline = line.find(":")
                key = ""
                value = ""
                if posline == -1:
                    continue
                key = line[0:posline]
                if len(line)>posline+1:
                    value = line[posline+1:]

                key = key.strip()
                value = value.strip()
                headerDict[key] = value
        return headerDict
    @staticmethod
    def GetFullUrl(url,data):
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
                oneItem = key+"="+str(data[key])
                if hasQuestionChar == False:
                    realUrl = realUrl + "?" + oneItem
                    hasQuestionChar = True
                else:
                    realUrl = realUrl + "&" + oneItem
            return realUrl

        raise Exception( "http param \'data\' type %s not support", type(data).__name__)




