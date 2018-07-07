# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 00:19:15 2018

@author: spy
"""

import re
#Range由两个Bound组成，Bound是现在得到的界限，运算由节点之间的关系决定
# inf 最大值 ； -inf 最小值; None 未设置； Null 不存在 
class Range:
    def __init__(self ):
        self.lowBound = Bound()
        self.highBound = Bound()
        self.needFuture = False
    
    def setByValue(self, vl, vh, size):
        self.lowBound = Bound()
        self.lowBound.value = vl
        self.highBound = Bound()
        self.highBound.value = vh
        self.lowBound.size = size
        self.highBound.size = size
        self.needFuture = False
    
    def setFuture(self, tf):
        self.needFuture = tf

    def copyRange(self, rb):
        self.lowBound.value = rb.lowBound.value
        self.highBound.value = rb.highBound.value
        self.lowBound.size = rb.lowBound.size
        self.highBound.size = rb.highBound.size

    #RangeCheck真的需要吗？
    def RangeCheck(self):
        if self.lowBound.value == 'inf':
            if self.highBound.value != 'inf':
                self.highBound.value = 'NULL'
                self.lowBound.value = 'NULL'
        if self.highBound.value == '-inf':
            if self.highBound.value != '-inf':
                self.highBound.value = 'NULL'
                self.lowBound.value = 'NULL'
                

#Widen的时候需要考虑边界运算吗？
class Bound:
    def __init__(self):
        self.value = 'None'      #边界 Value
        self.size = 'None'       #边界是 int or float

'''
    Class Description : Constraint Graph的节点
'''
class MyNode:
    def __init__(self, t= "", name = "",  args = [], result = [], fromBlock = 0, Statement = ''):
        self.type = t #leave 叶节点存放范围和值 #op运算符 #i变量名
        self.name = name.strip()  #用于变量的存储
        self.args = args
        self.result = result        #被用到哪
        self.Conditions = []        #约束条件
        self.fromBlock = fromBlock  #在CFG的哪个Block中定义的
        self.Statement = Statement  #在SSA中的哪条Statement中
        self.Range = Range()
        self.size = ''
        self.input = False

        
    
    def addArgument(self, argument):
        if not argument in self.args:
            self.args.append(argument)

    def addResult(self, r):
        if not r in self.result:
            self.result.append(r)
    
    def addCondition(self, c):
        self.Conditions.append(c)
    
    def setRange(self, vl, vh, size):
        modify = False
        if self.Range.lowBound.value != vl\
         or self.Range.highBound.value != vh:
             modify = True         
        if self.Range.lowBound.size != 'int' and size == 'int':
            self.Range.lowBound.size = size
            modify = True
        if self.Range.highBound.size != 'int' and size == 'int':
            self.Range.highBound.size = size
            modify = True
        self.Range.lowBound.value = vl
        self.Range.highBound.value = vh
        return modify
    
    def setByRange(self, rb):
        vl = rb.lowBound.value
        vh = rb.highBound.value
        size = rb.lowBound.size
        return self.setRange(vl, vh, size)

    def checkRange(self):
        if self.Range.lowBound.value == 'None'\
        or self.Range.lowBound.value == 'Not Exists'\
        or self.Range.highBound.value == 'Not Exists':
            return False
        else:
            return True
    
    def copyRange(self, node2):
        vl = node2.Range.lowBound.value
        vh = node2.Range.highBound.value
        size = node2.Range.lowBound.size
        return self.setRange(vl, vh, size)

    def printRange(self):
        print("Range: " + str(self.Range.lowBound.value) + " " + str(self.Range.highBound.value)  )

        
'''
    Class Description : Constraint Graph中的条件，附加在MyNode中
'''
class MyCondition:
    def __init__(self, condition, index):
        self.condition = condition
        self.arg1 = re.sub("\(.*\)", "",condition.split()[0].strip())
        self.arg2 = re.sub("\(.*\)", "",condition.split()[2].strip())
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
        self.name = ''
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