# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 10:52:10 2018

@author: spy
"""
import re
from structure import *
from ESSAConstraintGraph import *


class RangeAna:
    def __init__(self, c):
        self.ConstraintGraph = c
    
    #获得所有叶节点
    def getAllLeaves(self):
        result = []
        for myNode in self.ConstraintGraph.MyNodes:
            if myNode.type == 'leaf':
                result.append(myNode)
        return result
    
    #初始化所有叶节点
    def initializeLeafs(self):
        LeafNodes = self.getAllLeaves()
        for node in LeafNodes:
            node.size = 'float'
            node.setRange(float(node.name), float(node.name), "float")
        for statement in self.ConstraintGraph.cfg.Blocks[0].Stmts:
            statement = statement.strip(';')
            size = statement.split()[0]
            name = statement.split()[1]
            for node in self.ConstraintGraph.MyNodes:
                if node.name.startswith(name):
                    node.Range.lowBound.size = size
                    node.Range.highBound.size = size
        for var in self.ConstraintGraph.cfg.Arguments:
            var_size = var.split()[0]
            var_name = var.split()[1]
            var1, var2 = input("Enter Range For " + var_name + ": ").split()
            for node in self.ConstraintGraph.MyNodes:
                if node.name.startswith(var_name):
                    node.Range.lowBound.size = var_size
                    node.Range.highBound.size = var_size
                    node.Range.lowBound.value = var1
                    node.Range.highBound.value = var2
            
   
    
    #Widen Operation
    def WidenOP(self, node):
        if node.name == '+':
            result = self.add(node.args[0].Range, node.args[1].Range)
        if node.name == '-':
            result = self.minus(node.args[0].Range, node.args[1].Range)
        if node.name == '*':
            result = self.multi(node.args[0].Range, node.args[1].Range)
        if node.name == '/':
            result = self.div(node.args[0].Range, node.args[1].Range)
        if node.name == 'PHI':
            result = self.phi(node.args[0].Range, node.args[1].Range)

        if node.Range.lowBound.value == 'None' and node.Range.highBound.value == 'None':
            return node.setByRange(result)
        
        if float(result.lowBound.value) < float(node.Range.lowBound.value) \
         and float(result.highBound.value) > float(node.Range.highBound.value):
            return node.setRange('-inf', 'inf', result.lowBound.size)
        if float(result.lowBound.value) < float(node.Range.lowBound.value):
            return node.setRange('-inf', node.Range.highBound.value, result.lowBound.size)
        if float(result.highBound.value) > float(node.Range.highBound.value):
            return node.setRange(node.Range.lowBound.value, 'inf', result.lowBound.size)

    def NarrowOP(self, node):
        if node.name == '+':
            result = self.add(node.args[0].Range, node.args[1].Range)
        if node.name == '-':
            result = self.minus(node.args[0].Range, node.args[1].Range)
        if node.name == '*':
            result = self.multi(node.args[0].Range, node.args[1].Range)
        if node.name == '/':
            result = self.div(node.args[0].Range, node.args[1].Range)
        if node.name == 'PHI':
            result = self.phi(node.args[0].Range, node.args[1].Range)

        if node.Range.lowBound.value == '-inf' and result.lowBound.value != '-inf':
            return node.setRange(result.lowBound.value, node.Range.highBound.value, node.Range.lowBound.size)
        if node.Range.highBound.value == 'inf' and result.highBound.value != 'inf':
            return node.setRange(node.Range.lowBound.value, result.highBound.value, node.Range.lowBound.size)
        if float(node.Range.lowBound.value) > float(result.lowBound.value):
            return node.setRange(result.lowBound.value, node.Range.highBound.value, result.lowBound.size) 
        if float(node.Range.highBound.value) < float(result.highBound.value):
            return node.setRange(node.Range.lowBound.value, result.highBound.value, node.Range.lowBound.size)

    def ConditionHandle(self, ininode):
        #考虑每一个参数都有可能和Condition有关
        resultRange = Range()
        resultRange.copyRange(ininode.Range)
        for node in ininode.args:

            if len(ininode.Conditions) == 0:
                return False

            for con in ininode.Conditions:
                myCondition = self.ConstraintGraph.getConditionByIndex(con[0])
                #myCondition = self.ConstraintGraph.MyConditions[con[0]]
                tf = con[1]
                tempRange = '0'
                if tf == 0:
                    if node.name == myCondition.arg1:
                        if self.ConstraintGraph.getNodeByName(myCondition.arg2) == None:
                            arg2 = re.sub("#.*", "", myCondition.arg2)
                            if myCondition.op == '<':
                                if node.Range.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg2) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg2), 'float')
                            if myCondition.op == '<=':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(arg2), resultRange.lowBound.size)
                            if myCondition.op == '>':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg2) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg2), 'inf', 'float')
                            if myCondition.op == '>=':
                                tempRange = Range()
                                tempRange.setByValue(float(arg2), 'inf', resultRange.lowBound.size)
                            if myCondition.op == '==':
                                tempRange = Range()
                                tempRange.setByValue(float(arg2), float(arg2), resultRange.lowBound.size)
                        else:
                            if myCondition.op == '<':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value), 'float')
                            if myCondition.op == '<=':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value),resultRange.lowBound.size)
                            if myCondition.op == '>':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value), 'inf', 'float')
                            if myCondition.op == '>=':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value), 'inf',resultRange.lowBound.size)
                            if myCondition.op == '==':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value), float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value), resultRange.lowBound.size)
                        #交的范围
                        if not tempRange == '0' and not resultRange.highBound.value == 'Not Exists': 
                            resultRange = self.intersect(tempRange, resultRange)
                        #if myCondition.op == '!=':

                    if node.name == myCondition.arg2:
                        if self.ConstraintGraph.getNodeByName(myCondition.arg1) == None:
                            arg1 = re.sub("#.*", "", myCondition.arg1)
                            if myCondition.op == '<':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg1) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg1), 'inf', 'float')
                            if myCondition.op == '<=':
                                tempRange = Range()
                                tempRange.setByValue(float(arg1),'inf', resultRange.lowBound.size)
                            if myCondition.op == '>':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg1) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg1), 'float')
                            if myCondition.op == '>=':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(arg1), resultRange.lowBound.size)
                            if myCondition.op == '==':
                                tempRange = Range()
                                tempRange.setByValue(float(arg1), float(arg1), resultRange.lowBound.size)
                        else:
                            if myCondition.op == '<':
                                if node.Range.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value), 'inf', 'float')
                            if myCondition.op == '<=':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value),'inf', node.Range.lowBound.size)
                            if myCondition.op == '>':
                                if node.Range.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value), 'float')
                            if myCondition.op == '>=':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value),node.Range.lowBound.size)
                            if myCondition.op == '==':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value), float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value), node.Range.lowBound.size)

                        #交的范围
                        if not tempRange == '0' and not resultRange.highBound.value == 'Not Exists': 
                            resultRange = self.intersect(tempRange, resultRange)
                        #if myCondition.op == '!=':
                else:
                    if node.name == myCondition.arg1:
                        if self.ConstraintGraph.getNodeByName(myCondition.arg2) == None:
                            arg2 = re.sub("#.*", "", myCondition.arg2)
                            if myCondition.op == '>=':
                                if node.Range.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg2) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg2), 'float')
                            if myCondition.op == '>':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(arg2), resultRange.lowBound.size)
                            if myCondition.op == '<=':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg2) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg2), 'inf', 'float')
                            if myCondition.op == '<':
                                tempRange = Range()
                                tempRange.setByValue(float(arg2), 'inf', resultRange.lowBound.size)
                            if myCondition.op == '!=':
                                tempRange = Range()
                                tempRange.setByValue(float(arg2), float(arg2), resultRange.lowBound.size)
                        else:
                            if myCondition.op == '>=':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value), 'float')
                            if myCondition.op == '>':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value),resultRange.lowBound.size)
                            if myCondition.op == '<=':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value), 'inf', 'float')
                            if myCondition.op == '<':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value), 'inf',resultRange.lowBound.size)
                            if myCondition.op == '!=':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.lowBound.value), float(self.ConstraintGraph.getNodeByName(myCondition.arg2).Range.highBound.value), resultRange.lowBound.size)
                        #交的范围
                        if not tempRange == '0' and not resultRange.highBound.value == 'Not Exists': 
                            resultRange = self.intersect(tempRange, resultRange)
                        #if myCondition.op == '!=':

                    if node.name == myCondition.arg2:
                        if self.ConstraintGraph.getNodeByName(myCondition.arg1) == None:
                            arg1 = re.sub("#.*", "", myCondition.arg1)
                            if myCondition.op == '>=':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg1) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(arg1), 'inf', 'float')
                            if myCondition.op == '>':
                                tempRange = Range()
                                tempRange.setByValue(float(arg1),'inf', resultRange.lowBound.size)
                            if myCondition.op == '<=':
                                if resultRange.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg1) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(arg1), 'float')
                            if myCondition.op == '<':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(arg1), resultRange.lowBound.size)
                            if myCondition.op == '!=':
                                tempRange = Range()
                                tempRange.setByValue(float(arg1), float(arg1), resultRange.lowBound.size)
                        else:
                            if myCondition.op == '>=':
                                if node.Range.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value) + 1, 'inf', 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value), 'inf', 'float')
                            if myCondition.op == '>':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value),'inf', node.Range.lowBound.size)
                            if myCondition.op == '<=':
                                if node.Range.lowBound.size == 'int':
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value) - 1, 'int')
                                else:
                                    tempRange = Range()
                                    tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value), 'float')
                            if myCondition.op == '<':
                                tempRange = Range()
                                tempRange.setByValue('-inf', float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value),node.Range.lowBound.size)
                            if myCondition.op == '!=':
                                tempRange = Range()
                                tempRange.setByValue(float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.lowBound.value), float(self.ConstraintGraph.getNodeByName(myCondition.arg1).Range.highBound.value), node.Range.lowBound.size)

                        #交的范围
                        if not tempRange == '0'  and not resultRange.highBound.value == 'Not Exists': 
                            resultRange = self.intersect(tempRange, resultRange)
                        #if myCondition.op == '!=':
        ininode.setByRange(resultRange)

    #三部曲第一步：Widen过程
    def Widen(self):
        #self.initializeLeafs() #对叶节点的范围进行赋值，并对节点类型进行赋值e)
        change = True

        while(change == True):
            change = False
            #因为设置是从叶节点开始创建节点的，所以遍历顺序和创建顺序保持一致就没用什么大问题
            for node in self.ConstraintGraph.MyNodes:
                #检查所有参数的范围都已经求出，如果没有全部求出，就跳过
                check_all_range_set = True
                for no in node.args:
                    if no.checkRange() == False:
                        check_all_range_set = False
                        break
                if check_all_range_set == False:
                    if node.name == 'PHI':
                        for no in node.args:
                            if no.checkRange() == True:
                                node.copyRange(no)                        
                    continue
                if node.type == 'op':
                    ###运算范围
                    change = change or self.WidenOP(node)
                    #self.ConditionHandle(node)
                if node.type == 'var':  #如果是var节点，那么一定只有一个右节点
                    if (len(node.args) > 0):
                        #var_name = re.sub("_.*", "", node.name).strip()
                        ###运算范围
                        change = change or node.copyRange(node.args[0])

                        
                    

    def futureResolve(self):
        change = True
        k = 4
        while(k > 0):
            k = k - 1
            change = False
            for node in self.ConstraintGraph.MyNodes:
                self.ConditionHandle(node)

    def Narrow(self):
        change = True
        while(change == True):
            change = False
            for node in self.ConstraintGraph.MyNodes:
                check_all_range_set = True
                for no in node.args:
                    if no.checkRange() == False:
                        check_all_range_set = False
                        break
                if check_all_range_set == False:
                    if node.name == 'PHI':
                        for no in node.args:
                            if no.checkRange() == True:
                                node.copyRange(no)                        
                    continue
                if node.type == 'op':
                    ###运算范围
                    change = change or self.NarrowOP(node)
                if node.type == 'var':  #如果是var节点，那么一定只有一个右节点
                    var_name = re.sub("_.*", "", node.name).strip()
                    ###运算范围
                    change = change or node.copyRange(node.args[0])


    def checklowSize(self, Rangea, Rangeb):

        if Rangea.lowBound.size == 'int' or Rangeb.lowBound.size == 'int':
            return 'int'
        return 'float'
    
    def checkhighSize(self, Rangea, Rangeb):
        if Rangea.highBound.size == 'int' or Rangeb.highBound.size == 'int':
            return 'int'
        return 'float'
        
    def phi(self, Rangea, Rangeb):
        result = Range()            
        result.lowBound.value = min(float(Rangea.lowBound.value), float(Rangeb.lowBound.value))
        result.highBound.value = max(float(Rangea.highBound.value), float(Rangeb.highBound.value))
        result.lowBound.size = self.checklowSize(Rangea, Rangeb)
        result.highBound.size = self.checkhighSize(Rangea, Rangeb)
        return result

    def add(self, Rangea, Rangeb):
        result = Range()
        result.lowBound.value = float(Rangea.lowBound.value) + float(Rangeb.lowBound.value)
        result.highBound.value = float(Rangea.highBound.value) + float(Rangeb.highBound.value)
        result.lowBound.size = self.checklowSize(Rangea, Rangeb)
        result.highBound.size = self.checkhighSize(Rangea, Rangeb)
        return result
    
    def minus(self, Rangea, Rangeb):
        result = Range()
        result.lowBound.value = float(Rangea.lowBound.value) - float(Rangeb.lowBound.value)
        result.highBound.value = float(Rangea.highBound.value) - float(Rangeb.highBound.value)
        result.lowBound.size = self.checklowSize(Rangea, Rangeb)
        result.highBound.size = self.checkhighSize(Rangea, Rangeb)
        return result

    def multi(self, Rangea, Rangeb):
        result = Range()
        L = [float(Rangea.lowBound.value) * float(Rangeb.lowBound.value),
             float(Rangea.lowBound.value) * float(Rangeb.highBound.value),
             float(Rangea.highBound.value) * float(Rangeb.lowBound.value),
             float(Rangea.highBound.value) * float(Rangeb.highBound.value)]
        result.lowBound.value = min(L)
        result.highBound.value = max(L)
        result.lowBound.size = self.checklowSize(Rangea, Rangeb)
        result.highBound.size = self.checkhighSize(Rangea, Rangeb)
        return result
    
    def div(self, Rangea, Rangeb):
        result = Range()
        L = [float(Rangea.lowBound.value) / float(Rangeb.lowBound.value),
             float(Rangea.lowBound.value) / float(Rangeb.highBound.value),
             float(Rangea.highBound.value) / float(Rangeb.lowBound.value),
             float(Rangea.highBound.value) / float(Rangeb.highBound.value)]
        result.lowBound.value = min(L)
        result.highBound.value = max(L)
        result.lowBound.size = self.checklowSize(Rangea, Rangeb)
        result.highBound.size = self.checkhighSize(Rangea, Rangeb)
        return result
    
    def intersect(self, Rangea, Rangeb):
        result = Range()
        result.lowBound.size = self.checklowSize(Rangea, Rangeb)
        result.highBound.size = self.checkhighSize(Rangea, Rangeb)
        if (float(Rangea.lowBound.value) <= float(Rangeb.lowBound.value)\
         and float(Rangeb.lowBound.value) <= float(Rangea.highBound.value))\
         or (float(Rangeb.lowBound.value) <= float(Rangea.lowBound.value)\
         and float(Rangea.lowBound.value) <= float(Rangeb.highBound.value)):
            result.lowBound.value = max(float(Rangea.lowBound.value), float(Rangeb.lowBound.value))
            result.highBound.value = min(float(Rangea.highBound.value), float(Rangeb.highBound.value))
        else:
            result.lowBound.value = 'Not Exists'
            result.highBound.value = 'Not Exists'
        return result

    def printRange(self):
        for node in self.ConstraintGraph.MyNodes:
            print(node.name,end = ' ')
            print(node.Range.lowBound.size, end = ' ')
            print(node.Range.highBound.size, end = ' ' )
            print("|",end = " ")
            node.printRange()
        
    def finalAnswer(self):
        for node in self.ConstraintGraph.MyNodes:
            if node.name == self.ConstraintGraph.returnName:
                print(node.name,end = ' ')
                print(node.Range.lowBound.size, end = ' ')
                print(node.Range.highBound.size, end = ' ' )
                print("|",end = " ")
                node.printRange()
                return

if __name__ == '__main__':
    
    c = CFGConstructor("C:\\Users\\spy\\Desktop\\RangeAnalysis\\benchmark\\t5.ssa")
    m = ConstraintConstructor(c)
    m.combineGraph()
    g = m.OnlyGraph
    Graph = ConstraintGraph(None)
    for graph in m.FinalConstraintGraphs:
        for node in graph.MyNodes:
            Graph.MyNodes.append(node)
        for condi in graph.MyConditions:
            Graph.MyConditions.append(condi)
        if graph.cfg.name == 'foo':
            Graph.returnName = graph.returnName
    r = RangeAna(Graph)
    r.Widen()
    r.printRange()
    r.futureResolve()
    r.printRange()
    r.finalAnswer()
    '''
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\RangeAnalysis\\benchmark\\t10.ssa")
    c = ConstraintGraph(cfg)
    c.construct(cfg)
    c.essaConstruct(cfg)
    c.printGraph()
    print("Start Widen")
    r = RangeAna(c)
    r.Widen()
    r.printRange()
    print("Start Future Resolve")
    r.futureResolve()
    r.printRange()
    #print("Start Narrow")
    #r.Narrow()
    #r.printRange()
    '''