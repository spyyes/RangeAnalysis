# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:45:56 2018

@author: spy
"""

'''
    实际上就是e-ssa
    CFG 结构：
    block存储：[]列表存储
    每个statement ： 从i_5中提取i，
    抽取所有变量，每个变量有一个范围
    抽取所有constraint,对每个变量构建constaint graph
    最终需要的是变量之间的关系
    所以应该不需要语句block之间的关系，对吗？
    但是block之间有关系，需要从block中找到statement之间的关系
    要遍历block，构建constraint graph.
    
    
'''



##Attention! 只处理了一个函数，还有两个函数的场景

import re

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
            if has_method_declaration == False: #函数声明行
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
                
                
                
            #block声明 <>
            #if语句
            #else语句
            #goto 语句
            #函数声明
            #PHI语句
            
            #声明变量
            #简单赋值语句 + - * /
            #变量赋值语句 + - * /          
            
            #
            #
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

class Edge:
    def __init__(self, block_fm_num, block_to_num, condition):
        self.block_fm_num = block_fm_num
        self.block_to_num = block_to_num
        self.condition = condition
        
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
           
    def getBlockOutEdges(self, num):
        result = []
        for edge in self.Edges:
            if edge.block_fm_num == num:
                result.append(edge)
        return result
    def getRootBlock(self):
        return self.getBlockByNum(1)
    
        
if __name__ == '__main__':
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\t1.ssa")
    #ssa2cfg.check()
    #print(len(cfg.Edges))
    #print(cfg.getBlockByNum(2))

    