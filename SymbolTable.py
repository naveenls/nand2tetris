# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 16:15:56 2019

@author: HP
"""

class SymbolTable:
    
    def __init__(self):
        self.field=0
        self.arg=0
        self.var=0
        self.static=0
        self.static_scope={}
        self.subroutine_scope={}
        self.field_scope={}
        
    def initSubroutine(self):
        self.subroutine_scope.clear()
        self.arg=0
        self.var=0
        
    def add(self,name,type,kind):
        if kind=="var":
            self.subroutine_scope[name]=[type,kind,self.var]
            self.var+=1
        elif kind=="arg":
            self.subroutine_scope[name]=[type,kind,self.arg]
            self.arg+=1
        elif kind=="field":
            self.field_scope[name]=[type,kind,self.field]
            self.field+=1
        else:
            self.static_scope[name]=[type,kind,self.static]
            self.static+=1
            
    def kind(self, name):
        if name in self.subroutine_scope.keys():
          return self.subroutine_scope[name][1]
        elif name in self.field_scope.keys():
          return self.field_scope[name][1]
        elif name in self.static_scope.keys():
          return self.static_scope[name][1]
        else:
          return None
    
    def type(self, name):
        if name in self.subroutine_scope.keys():
          return self.subroutine_scope[name][0]
        elif name in self.field_scope.keys():
          return self.field_scope[name][0]
        elif name in self.static_scope.keys():
          return self.static_scope[name][0]
        else:
          return None

    def index(self, name):
        if name in self.subroutine_scope.keys():
          return self.subroutine_scope[name][2]
        elif name in self.field_scope.keys():
          return self.field_scope[name][2]
        elif name in self.static_scope.keys():
          return self.static_scope[name][2]
        else:
          return None