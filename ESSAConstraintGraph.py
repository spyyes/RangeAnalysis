# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:45:56 2018

@author: spy
"""

'''
    
'''



##Attention! 只处理了一个函数，还有两个函数的场景

import re
from structure import *

class SSA2CFG:
    def __init__(self):
        self.cfg = CFG()

    def construct(self, ssaFile):
        #读入 ssa文件
        f_ssa = open(ssaFile, "r")
        ssa_lines = f_ssa.readlines()
        f_ssa.close()
        
        #记录当前 block id
        last_block_id = 1
        cur_block_id = 1
        
        has_method_declaration = False
        self.cfg.addBlock(Block(1))

        ssa_len = len(ssa_lines)
        
        index = 0
        while (index < ssa_len):
            ssa_line = ssa_lines[index]
            if ssa_line.strip() == '':
                index = index + 1
                continue
            if ssa_line.strip().startswith(";;"):
                index = index + 1
                continue

            if ssa_line.strip() == '{' or ssa_line.strip() =='}':
                index = index + 1
                continue
            #函数声明
            if re.search("^[a-z0-9A-Z_]*\s*\(.*\)$", ssa_line) \
            and has_method_declaration == False:
                arguments = re.search("\(.*\)", ssa_line).group(0)
                arguments = arguments[1:-1]
                if(arguments != ''):
                    arguments = arguments.split(",")
                    for argument in arguments:
                        self.cfg.addArgument(argument)
                has_method_declaration = True
                index = index + 1
                continue
                    
            #<bb id>
            if(re.search("^<bb \d+>", ssa_line.strip())):
                # 新建一个block
                group_id = re.search("\d+", ssa_line).group(0)
                last_block_id = cur_block_id
                cur_block_id = group_id #更新当前group id
                self.cfg.addBlock(Block(cur_block_id))
                #上一个block最后一句不是goto,所以添加默认边
                if self.cfg.getBlockByNum(last_block_id).checkLastGoto == False:
                    self.cfg.addEdge(Edge(last_block_id, cur_block_id, None))   
                    self.cfg.getBlockByNum(last_block_id).addStmt("goto <bb " + cur_block_id + ">")
                index = index + 1
                continue
            
            #if()
            if(re.search("^if \(", ssa_line.strip())):
                condition = re.sub("if \(", "", ssa_line.strip())
                condition = condition[0:-1] #去掉)
                next_ssa_line = ssa_lines[index + 1]
                if(re.search("goto <bb \d+>", next_ssa_line)):
                    goto_id = re.search("\d+", next_ssa_line).group(0)
                    self.cfg.addEdge(Edge(cur_block_id, goto_id, condition))
                    self.cfg.getBlockByNum(cur_block_id).addIfStmt(condition)
                    self.cfg.getBlockByNum(cur_block_id).addStmt(ssa_line.strip() + " " + next_ssa_line.strip())
                    index = index + 2
                else:
                    print("Error in IF statemnet! ")
                    index = index + 1
                continue
            
            #else
            if(re.search("^else", ssa_line.strip())):
                condition = "not " + self.cfg.getBlockByNum(cur_block_id).IfStmts[-1]
                next_ssa_line = ssa_lines[index + 1]
                if(re.search("goto <bb \d+>", next_ssa_line)):
                    goto_id = re.search("\d+", next_ssa_line).group(0)
                    self.cfg.addEdge(Edge(cur_block_id, goto_id, condition))
                    self.cfg.getBlockByNum(cur_block_id).addStmt("if (" + condition + ") " + next_ssa_line.strip())
                    index = index + 2
                else:
                    print("Error in ELSE statemnet! ")
                    index = index + 1
                continue
            
            #goto (不在if or else之后)
            if(re.search("^goto <bb \d+>", ssa_line.strip())):
                goto_id = re.search("\d+", ssa_line).group(0)
                self.cfg.addEdge(Edge(cur_block_id, goto_id, None))
                self.cfg.getBlockByNum(cur_block_id).addStmt(ssa_line.strip())
                index = index + 1
                continue
            
            self.cfg.getBlockByNum(cur_block_id).addStmt(ssa_line.strip())
            index = index + 1
        return self.cfg    
    
    def check(self):
        print(len(self.cfg.Blocks))
        for block in  self.cfg.Blocks:
            print(block.index)
            for stmt in block.Stmts:
                print(stmt)
        print("-----------------------------")
        print(len(self.cfg.Edges))
        for edge in self.cfg.Edges:
            print(edge.block_fm_num + " " + edge.block_to_num + " "+ edge.condition)


'''
    Contraint Graph Construct
'''
class ConstraintGraph:
    def __init__(self, cfg):
        self.MyNodes = []
        self.MyConditions = []
        self.cfg = cfg
        
    #从self.MyNodes中获取节点或新建节点
    def getNode(self, name = '', args = [], result = [], fromBlock = 0, Statement = ''):
        if "_" in name:
            newtype = 'var'
            for node in self.MyNodes:
                if node.name == name:
                    return node
            n = MyNode(t = newtype ,name = name, args = args, result = result, fromBlock = fromBlock, Statement = Statement)
            self.MyNodes.append(n)
            return n
        else:
            if name in ['+', '-', '*', '/', 'PHI']:
                newtype = 'op'
                n = MyNode(t = newtype, name = name, args = args, result = result, fromBlock = fromBlock, Statement = Statement)
            else:
                newtype ='leaf'
                n = MyNode(t = newtype, name = name, args = args, result = result, fromBlock = fromBlock, Statement = Statement)
            self.MyNodes.append(n)
            return n
    
    #从self.MyConditions中获取条件的序号
    def getConditionIndex(self, condition = ''):
        for c in self.MyConditions:
            if c.condition == condition.strip():
                return c.index

    #得到ssa中一条stmt对应的MyNode
    def getNodesByStmt(self, stmt):
        result = []
        stmt = stmt.strip(";")
        for myNode in self.MyNodes:
            if myNode.Statement.strip() == stmt.strip():
                result.append(myNode)
        return result
    
    def getNodeByName(self, name):
        for myNode in self.MyNodes:
            if myNode.name == name:
                return myNode

    #构建SSA的Constraint Graph
    def construct(self, cfg):
        for Block in cfg.Blocks:
            for stmt in Block.Stmts:
                stmt = stmt.strip(";")
                if "#" in stmt:
                    op = "PHI"
                    left = stmt.split("=")[0].strip("#").strip()
                    rights = stmt.split("=")[1].replace("PHI <" ,"").replace(">", "")
                    right1 = re.sub("\(.*\)", '', rights.split(",")[0].strip())
                    right2 = re.sub("\(.*\)", '', rights.split(",")[1].strip())
                    right1Node = self.getNode(name = right1, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    right2Node = self.getNode(name = right2, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    rightNode = self.getNode(name = op, args = [right1Node, right2Node], result = [], fromBlock = Block.index,  Statement = stmt)
                    right2Node.addResult(rightNode)
                    right1Node.addResult(rightNode)
                    leftNode = self.getNode(name = left, args = [rightNode], result = [], fromBlock = Block.index,  Statement = stmt)
                    leftNode.addArgument(rightNode)
                    rightNode.addResult(leftNode)
                    leftNode.fromBlock = Block.index
                    rightNode.fromBlock = Block.index
                    continue
                if "if" in stmt:    #在essaconstruct中处理条件节点
                    print(stmt)
                    continue
                if "=" in stmt:
                    left = stmt.split("=")[0].strip()
                    rights = stmt.split("=")[1].strip() 
                    if len(rights.split()) > 1:
                        right1 = rights.split()[0]   # argument1
                        op = rights.split()[1]       # op
                        right2 = rights.split()[2]   # argument2
                        right1Node = self.getNode(name = right1, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        right2Node = self.getNode(name = right2, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        rightNode = self.getNode(name = op, args = [right1Node, right2Node], result = [], fromBlock = Block.index,  Statement = stmt)
                        right2Node.addResult(rightNode)
                        right1Node.addResult(rightNode)
                        leftNode = self.getNode(name = left, args = [rightNode], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode.addArgument(rightNode)
                        rightNode.addResult(leftNode)
                        leftNode.fromBlock = Block.index
                        rightNode.fromBlock = Block.index
                    else:
                        right = rights
                        rightNode = self.getNode(name = right, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode = self.getNode(name = left, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode.addArgument(rightNode)
                        rightNode.addResult(leftNode)
                        leftNode.fromBlock = Block.index
    

    #构建E-SSA的Constraint Graph
    def essaConstruct(self, cfg):
        for Block in cfg.Blocks:
            for stmt in Block.Stmts:
                if 'if' in stmt:
                    condition = re.search("\(.*\)", stmt).group(0)[1:-1]
                    if 'not' in condition:
                        condition = re.sub("^not", '', condition)
                        index = self.getConditionIndex(condition)
                        self.addCondition(Block.index, stmt, index, cfg, 1)
                    else:
                        index =  len(self.MyConditions)
                        self.MyConditions.append(MyCondition(condition,index))
                        self.addCondition(Block.index, stmt, index, cfg, 0)

    
    #把一个条件关联到所以相关的node中
    #参数：block id , stmt_init, index(condition参数），cfg, tf
    def addCondition(self, index_init, stmt_init, index, cfg, tf):
        condition1 = self.MyConditions[index].arg1
        condition2 = self.MyConditions[index].arg2
        if(not "_" in condition1):
            condition1 = "CONST"
        if(not "_" in condition2):
            condition2 = "CONST"        
        gotostmt = re.sub(".*goto", "", stmt_init)
        goto_id = int(re.search("\d+", gotostmt).group(0).strip())
        GotoBlocks = [goto_id]
        checkedBlock = []
        while(len(GotoBlocks) != 0):
            goto_id = GotoBlocks[0]
            checkedBlock.append(goto_id)
            GotoBlocks.remove(goto_id)
            block =  cfg.getBlockByIndex(goto_id)
            for stmt in block.Stmts:
                #添加节点
                if 'goto' in stmt:
                    gotostmt = re.sub(".*goto", "", stmt)
                    goto_id_ = int(re.search("\d+", gotostmt).group(0).strip())
                    if goto_id_ in checkedBlock or goto_id_ == index_init or goto_id_ in GotoBlocks:
                        continue
                    else:
                        GotoBlocks.append(goto_id_)
                        continue
                if (not condition1 in stmt) and (not condition2 in stmt):   
                    continue
                    
                nodes = self.getNodesByStmt(stmt)
                
                for node in nodes:
                    #不在此定义的节点
                    if node.fromBlock !=  block.index:
                        continue
                    #常量节点
                    if node.type == 'leaf':
                        continue
                    if [index, 1 - tf] in node.Conditions:
                        node.Conditions.remove([index, 1 - tf])
                    else:
                        if [index, tf] in node.Conditions:
                            continue
                        else:
                            node.Conditions.append([index, tf])
            for goto_id_ in cfg.getBlockGotos(goto_id):
                if goto_id_ in checkedBlock or goto_id_ == index_init or goto_id_ in GotoBlocks:
                    continue
                else:
                    GotoBlocks.append(goto_id_)
                    continue
    #DEBUG
    def printGraph(self):
        for Node in self.MyNodes:
            print(Node.type + " "+ Node.name + " " + " in " + Node.fromBlock,end = ' : ' )
            print("|Arguments: ", end = '')
            for x in Node.args:
                print(x.name, end = ',')
            print("|Result: ", end = "")
            for x in Node.result:
                print(x.name, end = ',')
            print("|Conditions:", end = " ")
            for c in Node.Conditions:
                print(c[0], end = " ")
                print(c[1], end = "|")
            print()
            continue
            
        print("\nConditions:")
        for condition in self.MyConditions:
            print(condition.condition, end = " ")
            print(condition.index, end = ",")
        
                
        
        
        
if __name__ == '__main__':
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\RangeAnalysis\\benchmark\\t1.ssa")
    c = ConstraintGraph(cfg)
    c.construct(cfg)
    c.essaConstruct(cfg)
    c.printGraph()
    #ssa2cfg.check()
    #print(len(cfg.Edges))
    #print(cfg.getBlockByNum(2))

    