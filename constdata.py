# -*- coding:utf-8 -*-
import const
import os

def get_dir(filename,num):
    dirname = filename
    while num:
        dirname = os.path.dirname(dirname)
        num -=1
    return dirname
const.SOCK_TIMEOUT = 0.5
const.RECV_DATA_LEN = 1024*64
const.BASE_STORAGE_DIR = get_dir(__file__,3)+"/Public"
const.QRCODE_IMG_DIR = const.BASE_STORAGE_DIR + "/img/qrcode"
const.PKL_DIR = const.BASE_STORAGE_DIR + "/pkl"

class ThreeState:
    INIT  = "uninit"
    START = "ing"
    STOP  = "stop"

class Error:
    NOERROR = "noerror"
    TIMEOUT = "timeout"
    OTHER_ERROR = "other_error"



