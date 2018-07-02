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

#Constraint Graph Node
class MyNode:
    def __init__(self, t= "", name = "",  args = [], result = [], fromBlock = 0, Statement = ''):
        self.type = t #leave 叶节点存放范围和值 #op运算符 #i变量名
        self.name = name  #用于变量的存储
        self.args = args
        self.result = result
        self.Conditions = []
        self.fromBlock = fromBlock
        self.Statement = Statement
    
    def addArgument(self, argument):
        if not argument in self.args:
            self.args.append(argument)
            return
            

    def addResult(self, r):
        if not r in self.result:
            self.result.append(r)
    
    def addCondition(self, c):
        self.Conditions.append(c)

#Condition
class MyCondition:
    def __init__(self, condition, index):
        self.condition = condition
        self.arg1 = condition.split()[0].strip()
        self.arg2 = condition.split()[2].strip()
        self.op = condition.split()[1].strip()
        self.index = index



#Contraint Graph Construct
class ConstraintGraph:
    def __init__(self):
        self.MyNodes = []
        self.MyConditions = []
        
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
    
    def getCondition(self, condition = ''):
        for c in self.MyConditions:
            if c.condition == condition.strip():
                return c.index


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
                    continue
                if "if" in stmt:
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
                    else:
                        right = rights
                        rightNode = self.getNode(name = right, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode = self.getNode(name = left, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode.addArgument(rightNode)
                        rightNode.addResult(leftNode)
    
    #得到对应的stmt的MyNode
    def getNodesByStmt(self, stmt):
        result = []
        stmt = stmt.strip(";")
        for myNode in self.MyNodes:
            if myNode.Statement.strip() == stmt.strip():
                result.append(myNode)
        return result


    def getBlockByIndex(self, cfg, index):
        for block in cfg.Blocks:
            if str(block.index) == str(index):
                return block
    
    #参数：block id , stmt_init, index(condition参数），cfg, tf
    def addCondition(self, index_init, stmt_init, index, cfg, tf):
        gotostmt = re.sub(".*goto", "", stmt_init)
        goto_id = int(re.search("\d+", gotostmt).group(0).strip())
        GotoBlocks = [goto_id]
        checkedBlock = []
        while(len(GotoBlocks) != 0):
            goto_id = GotoBlocks[0]
            checkedBlock.append(goto_id)
            GotoBlocks.remove(goto_id)
            block =  self.getBlockByIndex(cfg, goto_id)
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
                    
                nodes = self.getNodesByStmt(stmt)
                
                for node in nodes:
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
                






    #添加e-ssa相关的Constraint Graph
    def essaConstruct(self, cfg):
        for Block in cfg.Blocks:
            for stmt in Block.Stmts:
                if 'if' in stmt:
                    condition = re.search("\(.*\)", stmt).group(0)[1:-1]
                    if 'not' in condition:
                        condition = re.sub("^not", '', condition)
                        index = self.getCondition(condition)

                        self.addCondition(Block.index, stmt, index, cfg, 1)
                    else:
                        index =  len(self.MyConditions)
                        self.MyConditions.append(MyCondition(condition,index ))
                        self.addCondition(Block.index, stmt, index, cfg, 0)


    #DEBUG
    def printGraph(self):
        for Node in self.MyNodes:
            print(Node.type + " "+ Node.name + " " + " in " + Node.fromBlock,end = ' : ' )
            print("Arguments: ", end = '')
            for x in Node.args:
                print(x.name, end = ',')
            print("Result: ", end = "")
            for x in Node.result:
                print(x.name, end = ',')
            print("Conditions:", end = " ")
            for c in Node.Conditions:
                print(c[0], end = " ")
            print()
            continue
            
        print("\nConditions:")
        for condition in self.MyConditions:
            print(condition.condition, end = " ")
            print(condition.index, end = ",")
        
                
        
        
        
if __name__ == '__main__':
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\t1.ssa")
    c = ConstraintGraph()
    c.construct(cfg)
    c.essaConstruct(cfg)
    c.printGraph()
    #ssa2cfg.check()
    #print(len(cfg.Edges))
    #print(cfg.getBlockByNum(2))

    