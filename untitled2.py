# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 13:27:17 2018

@author: spy
"""
#在构建essa的时候，需要对true 和false分支进行变量替换。其实相当于
# i_2 = i_2 U [1, 2]
class Constraint:
    def __init__(self):
        self.op = ''
        self.arg1 = ''
        self.arg2 = ''
        self.result = ''
    def setRange(self):
        
class Variable:
    #a = b + 1
    def __init__(self):
        self.low = ['', '']
        self.up = ['','']

#定义边界格式：可以是一个值；可以是其他变量范围的运算，需要未来处理。
#集合的运算是Variable范围的运算，如果已经有范围了又要赋值新的运算，
#就需要进行运算处理
class Bound:
    def __init__(self):
        self.property = ''
        self.value = ''
        self.op = ''