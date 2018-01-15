# -*- coding:utf-8 -*-
from SockServer import SockServer
from LocalMsgObj import LocalMsgObj
from WXMsgObj import WXMsgObj
import time
import sys
import time
from urlparse import urlparse
from itchat.itchat import itchat
from constdata import const
import os
#from tlrobot import TlRobot
from protocal import protocal
import json
import copy
from datetime import datetime

import requests
import threadpool
from Lock import Lock,AutoLock

l = Lock()
def M():
    AutoLock(l)

M()
def x(hh):
    #AutoLock(l)
    print "hello " + hh
pool = threadpool.ThreadPool(10)
args_list=[]
for i in range(0,100000):
    args_list.append(str(i))

requests = threadpool.makeRequests(x,args_list)
for req in requests:
    pool.putRequest(req)
pool.wait()

from GlobalFunc import GlobalFunc
from HttpTaskManager import HttpTaskManager
import httplib, ssl, urllib2, socket
class HTTPSConnectionV3(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        try:
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)
        except ssl.SSLError, e:
            print("Trying SSLv3.")
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)

class HTTPSHandlerV3(urllib2.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(HTTPSConnectionV3, req)
# install opener
urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))

if __name__ == "__main__":
    r = urllib2.urlopen("https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1515920588610&skey=%40crypt_2468677d_09ff77fd7e0bfe52d9e38ec198b83d01&sid=hlOBwuhDxNXqHwdD&uin=2635089432&deviceid=e379397915090996&synckey=1_655154874%7C2_655155160%7C3_655155145%7C1000_1515902882&_=1515920587836")
    print(r.read())

url = "http://127.0.0.1/thinkphp/index.php/Home/Index/wx"

x = requests.session().get("https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=1515920588610&skey=%40crypt_2468677d_09ff77fd7e0bfe52d9e38ec198b83d01&sid=hlOBwuhDxNXqHwdD&uin=2635089432&deviceid=e379397915090996&synckey=1_655154874%7C2_655155160%7C3_655155145%7C1000_1515902882&_=1515920587836")

m = 0
'''
def auto_login(self, hotReload=False, statusStorageDir='itchat.pkl',
               enableCmdQR=False, picDir=None, qrCallback=None,
               loginCallback=None, exitCallback=None):
'''




#tlrobot = TlRobot()
'''
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    print '%s: %s' % (msg.type, msg.text)
    text = msg.text
    if isinstance(msg.text,unicode):
        text = msg.text.encode('utf-8')
    if msg['User']['RemarkName'] == u'柏坤' or msg['User']['RemarkName'] == u'老婆':
        if msg['User']['UserName'] == msg['FromUserName']:
            retDataDict = tlrobot.chat(text)
            if retDataDict != None:
                msg.user.send('%s' %  retDataDict['text'])
    #msg.user.send('%s: %s' % (msg.type, msg.text))

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    if msg.isAt:
        str1 = u'@%s\u2005I received: %s' % (   msg.actualNickName, msg.text)
        print str1
        #msg.user.send(u'@%s\u2005I received: %s' % (
        #    msg.actualNickName, msg.text))
'''
import socket
if __name__ == '__main__':

    localMsgObj = LocalMsgObj(WXMsgObj())

    sockServer = SockServer()
    sockServer.init(("0.0.0.0", 9999), localMsgObj)
    sockServer.Start()
    def OnRecv(param):
        data = param.data
        url = param.url
        filename = os.path.basename(url)
        path = "c:/test/" + filename
        GlobalFunc.WriteFile(path,data)
        #print status
    def OnError(param):
        pass
    HttpTaskManager().init()

    #HttpTaskManager().CreateTask("http://www.baidu.com",None,None,None,"GET",OnRecv,None)
    #HttpTaskManager().CreateTask("http://127.0.0.1/1.php",None,None,None,"GET",OnRecv,OnError,None,None)
    #HttpTaskManager().CreateTask("http://127.0.0.1/ordersys.rar",None,None,None,"GET",OnRecv,OnError,None,None)
    #HttpTaskManager().CreateTask("http://127.0.0.1/TenVideoPlayer_V3.rar",None,None,None,"GET",OnRecv,OnError,None,None)
    #HttpTaskManager().CreateTask("http://127.0.0.1/QR.png",None,None,None,"GET",OnRecv,OnError,None,None)
    #HttpTaskManager().CreateTask("http://127.0.0.1/thinkphp.zip",None,None,None,"GET",OnRecv,OnError,None,None)

    #HttpTaskManager().CreateTask("http://www.runoob.com/python/att-list-count.html",None,None,"GET",OnRecv,OnError,None,None)
    '''
    itchat.auto_login(True)
    friends_dict = itchat.get_friends()
    mps_dict = itchat.get_mps()
    chatrooms_dict = itchat.get_chatrooms()
    itchat.run(True)
    '''
    time.sleep(100000)
