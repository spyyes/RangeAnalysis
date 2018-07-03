# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 00:19:15 2018

@author: spy
"""

'''
    Class Description : Constraint Graph的节点
'''
class MyNode:
    def __init__(self, t= "", name = "",  args = [], result = [], fromBlock = 0, Statement = ''):
        self.type = t #leave 叶节点存放范围和值 #op运算符 #i变量名
        self.name = name  #用于变量的存储
        self.args = args
        self.result = result        #被用到哪
        self.Conditions = []        #约束条件
        self.fromBlock = fromBlock  #在CFG的哪个Block中定义的
        self.Statement = Statement  #在SSA中的哪条Statement中
    
    def addArgument(self, argument):
        if not argument in self.args:
            self.args.append(argument)
            return

    def addResult(self, r):
        if not r in self.result:
            self.result.append(r)
    
    def addCondition(self, c):
        self.Conditions.append(c)

'''
    Class Description : Constraint Graph中的条件，附加在MyNode中
'''
class MyCondition:
    def __init__(self, condition, index):
        self.condition = condition
        self.arg1 = condition.split()[0].strip()
        self.arg2 = condition.split()[2].strip()
        self.op = condition.split()[1].strip()
        self.index = index
        
        
#CFG的辅助类          
class Block:
    def __init__(self, num):
        self.Stmts = []
        self.GotoStmt = []
        self.IfStmts = []
        self.Edges = []
        self.index = num
    def getNum(self):
        return self.index
    def addStmt(self, stmt):
        self.Stmts.append(stmt)
    def addIfStmt(self, if_stmt):
        self.IfStmts.append(if_stmt)
    def checkLastGoto(self):
        last_stmt = self.Stmts[-1]
        if "goto" in last_stmt:
            return True
        else:
            return False
#CFG的辅助类
class Edge:
    def __init__(self, block_fm_num, block_to_num, condition):
        self.block_fm_num = block_fm_num
        self.block_to_num = block_to_num
        self.condition = condition
#CFG类      
class CFG:
    def __init__(self):
        self.Blocks = []
        self.Edges = []
        self.Arguments = []
    def addBlock(self, b):
        self.Blocks.append(b)
    def addEdge(self, e):
        self.Edges.append(e)
    def addArgument(self, a):
        self.Arguments.append(a)
    def getBlockByNum(self, num):
        for b in self.Blocks:
            if b.getNum() == num:
                return b
        return None
    def getBlockByIndex(self, index):
        for block in self.Blocks:
            if str(block.index) == str(index):
                return block
           
    def getBlockOutEdges(self, num):
        result = []
        for edge in self.Edges:
            if edge.block_fm_num == num:
                result.append(edge)
        return result
    def getBlockGotos(self, num):
        result = []
        for edge in self.Edges:
            if edge.block_fm_num == num:
                result.append(edge.block_to_num)
        return result
    def getRootBlock(self):
        return self.getBlockByNum(1)

class Range:
    def __init__(self):
        self.low = ''
        self.high = ''
