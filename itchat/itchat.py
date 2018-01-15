# -*- coding:utf-8 -*-

from .core import Core
from .config import VERSION
from .log import set_logging
from content import *
__version__ = VERSION

class itchat(object):
    def __init__(self):
        originInstance = Core()
        self.login                       = originInstance.login
        self.get_QRuuid                  = originInstance.get_QRuuid
        self.get_QR                      = originInstance.get_QR
        self.check_login                 = originInstance.check_login
        self.web_init                    = originInstance.web_init
        self.show_mobile_login           = originInstance.show_mobile_login
        self.start_receiving             = originInstance.start_receiving
        self.get_msg                     = originInstance.get_msg
        self.logout                      = originInstance.logout
        # components.contact
        self.update_chatroom             = originInstance.update_chatroom
        self.update_friend               = originInstance.update_friend
        self.get_contact                 = originInstance.get_contact
        self.get_friends                 = originInstance.get_friends
        self.get_chatrooms               = originInstance.get_chatrooms
        self.get_mps                     = originInstance.get_mps
        self.set_alias                   = originInstance.set_alias
        self.set_pinned                  = originInstance.set_pinned
        self.add_friend                  = originInstance.add_friend
        self.get_head_img                = originInstance.get_head_img
        self.create_chatroom             = originInstance.create_chatroom
        self.set_chatroom_name           = originInstance.set_chatroom_name
        self.delete_member_from_chatroom = originInstance.delete_member_from_chatroom
        self.add_member_into_chatroom    = originInstance.add_member_into_chatroom
        # components.messages
        self.send_raw_msg                = originInstance.send_raw_msg
        self.send_msg                    = originInstance.send_msg
        self.upload_file                 = originInstance.upload_file
        self.send_file                   = originInstance.send_file
        self.send_image                  = originInstance.send_image
        self.send_video                  = originInstance.send_video
        self.send                        = originInstance.send
        self.revoke                      = originInstance.revoke
        # components.hotreload
        self.dump_login_status           = originInstance.dump_login_status
        self.load_login_status           = originInstance.load_login_status
        # components.register
        self.auto_login                  = originInstance.auto_login
        self.configured_reply            = originInstance.configured_reply
        self.msg_register                = originInstance.msg_register
        self.run                         = originInstance.run
        # other functions
        self.search_friends              = originInstance.search_friends
        self.search_chatrooms            = originInstance.search_chatrooms
        self.search_mps                  = originInstance.search_mps
        self.set_logging                 = set_logging
        originInstance.msg_register([TEXT, MAP, CARD, NOTE, SHARING],itchat.text_reply)
        originInstance.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],itchat.download_files)

    @staticmethod
    def text_reply(msg):
        print '%s: %s' % (msg.type, msg.text)
        text = msg.text
        if isinstance(msg.text,unicode):
            text = msg.text.encode('utf-8')
        #if msg['User']['RemarkName'] == u'柏坤' or msg['User']['RemarkName'] == u'老婆':
        #    if msg['User']['UserName'] == msg['FromUserName']:
        #retDataDict = tlrobot.chat(text)
        #if retDataDict != None:
        #    msg.user.send('%s' %  retDataDict['text'])
        #msg.user.send('%s: %s' % (msg.type, msg.text))

    @staticmethod
    def download_files(msg):
        msg.download(msg.fileName)
        typeSymbol = {
            PICTURE: 'img',
            VIDEO: 'vid', }.get(msg.type, 'fil')
        return '@%s@%s' % (typeSymbol, msg.fileName)