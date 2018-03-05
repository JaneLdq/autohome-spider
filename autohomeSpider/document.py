# -*- coding:utf-8 -*-
"""模拟Document对象和window对象"""
import PyV8

class Element():
    def __init__(self):
        self.sheet = ""
class Head(object):
    def appendChild(self, *args, **kwargs):
        return "sheet"

class v8Doc(PyV8.JSClass):
    def createElement(self,  *args, **kwargs):
        return Element()
    def getElementsByTagName(self, *args, **kwargs):
        head = Head()
        list = [head]
        return list
    def getComputedStyle(self, *args, **kwargs):
        return None
    def decodeURIComponent(self, *args, **kwargs):
        return args
    def querySelectorAll(self, *args, **kwargs):
        return None

class Global(PyV8.JSClass):
    def __init__(self):
        self.document = v8Doc()
        self.window = v8Doc()
