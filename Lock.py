# -*- coding:utf-8 -*-
import threading
class Lock(object):
    def __init__(self):
        self.lock = threading.Lock()
    def Lock(self):
        self.lock.acquire()
    def UnLock(self):
        self.lock.release()

class AutoLock(object):
    def __init__(self,lock):
        self.lock = lock
        lock.Lock()
    def __del__(self):
        self.lock.UnLock()

