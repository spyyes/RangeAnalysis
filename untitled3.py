# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:18:45 2018

@author: spy
"""

class Node2:
    def __init__(self, t= "", args = [], r = [], name = ""):
        self.type = t #leave 叶节点存放范围和值 #op运算符 #i变量名
        self.name = name  #用于变量的存储
        self.args = args
        self.result = r
    def addArgument(self, argument):
        self.args.append(argument)
    def addResult(self, r):
        self.result.append(r)

c = Node2('var', [1,2], [2], "6")