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
    
    #初始化所有节点
    def initAllNodes(self):
        for myNode in c.MyNodes:
            myNode.setInitialRange()
    
    #获得所有叶节点
    def getAllLeaves(self):
        result = []
        for myNode in self.ConstraintGraph.MyNodes:
            if myNode.type == 'leaf':
                result.append(myNode)
        return result
    
    #两个范围的比较函数
    def compare2Bound(self, Bound1, Bound2):
        if Bound1.value == 'inf' and Bound2.value == 'inf' \
        or Bound1.value == '-inf' and Bound2.value == '-inf' :
            return 0
        if Bound1.value == 'inf' or Bound2.value == '-inf':# 前者比后者大 返回1
            return 1
        if Bound1.value == '-inf' or Bound2.value == 'inf':
            return -1
        if Bound1.value > Bound2.value:
            return 1
        if Bound1.value == Bound2.value:
            return 0
        if Bound1.value < Bound2.value:
            return -1
    
    
    #Widen的Operation
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

        if self.compare2Bound(node.Range.lowBound, result.lowBound) > 0\
         and self.compare2Bound(node.Range.highBound, result.highBound) < 0:
            return node.setRange('-inf', 'inf', result.lowBound.size)
        if self.compare2Bound(node.Range.lowBound, result.lowBound) > 0:
            return node.setRange('-inf', node.Range.highBound.value, result.lowBound.size)
        if self.compare2Bound(node.Range.highBound, result.highBound) < 0:
            return node.setRange(node.Range.lowBound.value, 'inf', result.lowBound.size)
        
   
    #三部曲第一步：Widen过程
    def Widen(self):
        self.initAllNodes()
        LeafNodes = self.getAllLeaves()
        for node in LeafNodes:
            #对叶节点的范围进行赋值，并对节点类型进行赋值
            if 'e' in node.name:
                #科学计数法
                continue    
            else:
                if '.' in node.name:
                    node.size = 'float'
                    node.setRange(float(node.name), float(node.name), "float")
                else:
                    node.size = 'int'
                    node.setRange(int(node.name), int(node.name), "int")
        change = True
        while(change == True):
            change = False
            #因为设置是从叶节点开始创建节点的，所以遍历顺序和创建顺序保持一致就没用什么大问题
            for node in self.ConstraintGraph.MyNodes:
                print(node.name, end = " ")
                for arg in node.args:
                    print(arg.name, end = " ")
                node.printRange()
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
                
                #检查运算只发生在相同 var节点上
                if node.type == 'op':
                    check_only_var = 'None'
                    for no in node.args:
                        if no.type == 'var':
                            no_var_name = re.sub("_.*", "", no.name).strip()
                            if check_only_var == 'None':
                                check_only_var = no_var_name
                            else:
                                if no_var_name.strip() != check_only_var:
                                    check_only_var = False
                                    break
                    #需要不同的var，需要future resolve
                    if check_only_var == False:
                        continue
                    ###运算范围
                    change = change or self.WidenOP(node)
                        
                if node.type == 'var':
                    var_name = re.sub("_.*", "", node.name).strip()
                    #检查所需参数是不是都是相同的var
                    check_only_var = True
                    for no in node.args:
                        if no.type == 'var':
                            no_var_name = re.sub("_.*", "", no.name).strip()
                            if no_var_name != var_name:
                                check_only_var = False
                                break
                    #需要不同的var，需要future resolve
                    if check_only_var == False:
                        continue
                    ###运算范围
                    #如果是var节点，那么一定只有一个右节点
                    change = change or node.copyRange(node.args[0])
    
        
        
    def phi(self, Rangea, Rangeb):
        result = Range()            
        result.lowBound.value = min(float(Rangea.lowBound.value), float(Rangeb.lowBound.value))
        result.highBound.value = max(float(Rangea.highBound.value), float(Rangeb.highBound.value))
        result.lowBound.size = Rangea.lowBound.size
        result.highBound.size = Rangea.highBound.size
        return result

    def add(self, Rangea, Rangeb):
        result = Range()
        result.lowBound.value = float(Rangea.lowBound.value) + float(Rangeb.lowBound.value)
        result.highBound.value = float(Rangea.highBound.value) + float(Rangeb.highBound.value)
        result.lowBound.size = Rangea.lowBound.size
        result.highBound.size = Rangea.highBound.size
        return result
    
    def minus(self, Rangea, Rangeb):
        result = Range()
        result.lowBound.value = float(Rangea.lowBound.value) - float(Rangeb.lowBound.value)
        result.highBound.value = float(Rangea.highBound.value) - float(Rangeb.highBound.value)
        result.lowBound.size = Rangea.lowBound.size
        result.highBound.size = Rangea.highBound.size
        return result

    def multi(self, Rangea, Rangeb):
        result = Range()
        L = [float(Rangea.lowBound.value) * float(Rangeb.lowBound.value),
             float(Rangea.lowBound.value) * float(Rangeb.highBound.value),
             float(Rangea.highBound.value) * float(Rangeb.lowBound.value),
             float(Rangea.highBound.value) * float(Rangeb.highBound.value)]
        result.lowBound.value = min(L)
        result.highBound.value = max(L)
        result.lowBound.size = Rangea.lowBound.size
        result.highBound.size = Rangea.highBound.size 
        return result
    
    def div(self, Rangea, Rangeb):
        result = Range()
        L = [float(Rangea.lowBound.value) / float(Rangeb.lowBound.value),
             float(Rangea.lowBound.value) / float(Rangeb.highBound.value),
             float(Rangea.highBound.value) / float(Rangeb.lowBound.value),
             float(Rangea.highBound.value) / float(Rangeb.highBound.value)]
        result.lowBound.value = min(L)
        result.highBound.value = max(L)
        result.lowBound.size = Rangea.lowBound.size
        result.highBound.size = Rangea.highBound.size 
        return result
    
    def intersect(self, Rangea, Rangeb):
        result = Range()
        result.lowBound.size = Rangea.lowBound.size
        result.highBound.size = Rangea.highBound.size
        if (Rangea.lowBound.value <= Rangeb.lowBound.value\
         and Rangeb.lowBound.value <= Rangea.highBound.value)\
         or (Rangeb.lowBound.value <= Rangea.lowBound.value\
         and Rangea.lowBound.value <= Rangeb.highBound.value):
            result.lowBound.value = max(Rangea.lowBound.value, Rangeb.lowBound.value)
            result.highBound.value = min(Rangea.highBound.value, Rangeb.highBound.value)
        else:
            result.lowBound.value = 'Not Exists'
            result.highBound.value = 'Not Exists'
        return result


        
        
        
        
    

if __name__ == '__main__':
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\RangeAnalysis\\benchmark\\t1.ssa")
    c = ConstraintGraph()
    c.construct(cfg)
    c.essaConstruct(cfg)
    c.printGraph()
    r = RangeAna(c)
    r.Widen()
    