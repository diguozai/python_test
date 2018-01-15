# -*- coding:utf-8 -*-
import sys
import os
from constdata import const,ThreeState
from itchat.itchat import itchat
import json
from protocal import protocal
import copy

from tlrobot import TlRobot
class Session(object):
    def __init__(self,userid,httpObj):
        self.__userid = userid
        self.__httpObj = httpObj
        self.__state = ThreeState.INIT
    def GetUserId(self):
        return self.__userid

    def Start(self):

        self.__state = ThreeState.START
        statusStorageDir = const.PKL_DIR + "/" + self.__userid + ".pkl"
        picDir = const.QRCODE_IMG_DIR + "/" + self.__userid + ".png"
        try:
            os.makedirs(os.path.dirname(statusStorageDir))
        except:
            pass
        try:
            os.makedirs(os.path.dirname(picDir))
        except:
            pass

        def QRCodeDownFinishCallBack(status):
            qrCodeResponse = copy.deepcopy(protocal.qrCodeResponse)
            qrCodeResponse["ok"] = status
            responseStr = json.dumps(qrCodeResponse)
            self.__httpObj.Send(responseStr)

        itInstance = itchat()
        itInstance.auto_login(True,statusStorageDir,False,picDir,QRCodeDownFinishCallBack)
        friends_dict = itInstance.get_friends()
        mps_dict = itInstance.get_mps()
        chatrooms_dict = itInstance.get_chatrooms()


        itInstance.run(True,False)


    def Stop(self):
        self.__state = ThreeState.STOP




