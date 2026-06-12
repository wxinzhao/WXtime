#!python3
# -*- coding: utf-8 -*-
"""
Patched version of wxauto to support new WeChat with Qt framework
"""
import uiautomation as uia
import win32gui, win32con
import win32clipboard as wc
import time
import os
import logging

logger = logging.getLogger(__name__)

class WxParam:
    SYS_TEXT_HEIGHT = 33
    TIME_TEXT_HEIGHT = 34
    RECALL_TEXT_HEIGHT = 45
    CHAT_TEXT_HEIGHT = 52
    CHAT_IMG_HEIGHT = 117
    SpecialTypes = ['[文件]', '[图片]', '[视频]', '[音乐]', '[链接]']

class WxUtils:
    def SplitMessage(MsgItem):
        try:
            uia.SetGlobalSearchTimeout(0)
            MsgItemName = MsgItem.Name
            if MsgItem.BoundingRectangle.height() == WxParam.SYS_TEXT_HEIGHT:
                Msg = ('SYS', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
            elif MsgItem.BoundingRectangle.height() == WxParam.TIME_TEXT_HEIGHT:
                Msg = ('Time', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
            elif MsgItem.BoundingRectangle.height() == WxParam.RECALL_TEXT_HEIGHT:
                if '撤回' in MsgItemName:
                    Msg = ('Recall', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
                else:
                    Msg = ('SYS', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
            else:
                Index = 1
                User = MsgItem.ButtonControl(foundIndex=Index)
                try:
                    while True:
                        if User.Name == '':
                            Index += 1
                            User = MsgItem.ButtonControl(foundIndex=Index)
                        else:
                            break
                    Msg = (User.Name, MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
                except LookupError:
                    Msg = ('SYS', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
        finally:
            uia.SetGlobalSearchTimeout(10.0)
        return Msg

    def SetClipboard(data, dtype='text'):
        if dtype.upper() == 'TEXT':
            type_data = win32con.CF_UNICODETEXT
            if not isinstance(data, str):
                data = str(data)
        elif dtype.upper() == 'IMAGE':
            from io import BytesIO
            type_data = win32con.CF_DIB
            output = BytesIO()
            data.save(output, 'BMP')
            data = output.getvalue()[14:]
        else:
            raise ValueError('param (dtype) only "text" or "image" supported')
        wc.OpenClipboard()
        wc.EmptyClipboard()
        wc.SetClipboardData(type_data, data)
        wc.CloseClipboard()

class WeChat:
    def __init__(self):
        try:
            self.UiaAPI = uia.WindowControl(ClassName='Qt51514QWindowIcon', Name='微信')
            logger.info('找到新版微信窗口 (Qt 框架)')
        except LookupError:
            try:
                self.UiaAPI = uia.WindowControl(ClassName='WeChatMainWndForPC')
                logger.info('找到旧版微信窗口 (MFC 框架)')
            except LookupError:
                self.UiaAPI = uia.WindowControl(Name='微信')
                logger.info('通过标题找到微信窗口')

        self.SessionList = None
        try:
            for name in ['会话', '联系人', '聊天']:
                try:
                    self.SessionList = self.UiaAPI.ListControl(Name=name)
                    logger.info('找到会话列表: %s', name)
                    break
                except LookupError:
                    continue
        except Exception as e:
            logger.warning('未找到会话列表控件: %s', e)

        self.EditMsg = None
        try:
            edit_controls = []
            for i in range(1, 10):
                try:
                    edit = self.UiaAPI.EditControl(foundIndex=i)
                    edit_controls.append(edit)
                    logger.info('找到编辑控件 %d', i)
                except LookupError:
                    break

            if edit_controls:
                self.EditMsg = edit_controls[0]
                logger.info('使用第一个编辑控件作为输入框')
            else:
                logger.warning('未找到编辑控件')
        except Exception as e:
            logger.warning('查找输入框失败: %s', e)

        self.SearchBox = None
        try:
            for name in ['搜索', '查找']:
                try:
                    self.SearchBox = self.UiaAPI.EditControl(Name=name)
                    logger.info('找到搜索框: %s', name)
                    break
                except LookupError:
                    continue
        except Exception as e:
            logger.warning('未找到搜索框: %s', e)

        self.SessionItemList = []

    def GetSessionList(self, reset=False):
        if not self.SessionList:
            return []

        try:
            self.SessionItem = self.SessionList.ListItemControl()
            SessionList = []
            if reset:
                self.SessionItemList = []
            for i in range(100):
                try:
                    name = self.SessionItem.Name
                except AttributeError:
                    break
                if name not in self.SessionItemList:
                    self.SessionItemList.append(name)
                if name not in SessionList:
                    SessionList.append(name)
                self.SessionItem = self.SessionItem.GetNextSiblingControl()
            return SessionList
        except LookupError as e:
            logger.warning('GetSessionList失败: %s', e)
            return []

    def Search(self, keyword):
        if not self.UiaAPI:
            return

        self.UiaAPI.SetFocus()
        time.sleep(0.3)

        self.UiaAPI.SendKeys('{Ctrl}f', waitTime=0.5)
        time.sleep(0.5)

        self.UiaAPI.SendKeys('{Ctrl}a', waitTime=0.2)
        self.UiaAPI.SendKeys('{Delete}', waitTime=0.2)

        for char in keyword:
            self.UiaAPI.SendKeys(char, waitTime=0.05)
        time.sleep(1)

    def ChatWith(self, who, RollTimes=None):
        if not self.UiaAPI:
            return 0

        self.UiaAPI.SwitchToThisWindow()
        time.sleep(0.5)

        self.Search(who)
        time.sleep(2)

        self.UiaAPI.SendKeys('{Enter}')
        time.sleep(1)

        return 1

    def SendMsg(self, msg, clear=True):
        if not self.UiaAPI:
            return

        self.UiaAPI.SwitchToThisWindow()
        time.sleep(2)

        if clear:
            self.UiaAPI.SendKeys('{Ctrl}a', waitTime=0.5)
            self.UiaAPI.SendKeys('{Delete}', waitTime=0.5)

        WxUtils.SetClipboard(msg, 'text')
        time.sleep(0.5)
        self.UiaAPI.SendKeys('{Ctrl}v', waitTime=0.5)
        time.sleep(1)

        self.UiaAPI.SendKeys('{Enter}', waitTime=0.5)
        logger.info('消息发送成功: %s', msg)
