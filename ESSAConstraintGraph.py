# -*- coding: utf-8 -*-
"""
Created on Thu May 31 15:45:56 2018

@author: spy
"""


##Attention! 只处理了一个函数，还有两个函数的场景

import re
from structure import *

'''
    用于构建CFG
'''
class CFGConstructor:
    def __init__(self, ssaFile):
        f_ssa = open(ssaFile, "r")
        ssa_lines =  f_ssa.readlines()
        f_ssa.close()

        self.CFG_SSAs = []
        self.CFGs = []
        cfg_index = -1
        cfgLines = []

        #以;;为分隔符分割methods
        for line in ssa_lines:
            if line.startswith(";;"):
                cfg_index = cfg_index + 1
                if cfg_index != 0:  #提交上一个
                    self.CFG_SSAs.append(cfgLines)
                    cfgLines = []
            else:
                cfgLines.append(line)
        self.CFG_SSAs.append(cfgLines)  #提交最后一个
        cfgLines = []
        
        
        self.name_ssa = {}

        for cfgssa in self.CFG_SSAs:
            s = SSA2CFG()
            s.construct(cfgssa)
            self.CFGs.append(s.cfg)
            self.name_ssa[s.cfg.name] = cfgssa


'''
    用于构建Constraint Graph
'''
class ConstraintConstructor:
    def __init__(self, CFGConstructor):
        self.CFGConstructor = CFGConstructor
        self.ConstraintGraphs = []
        self.FinalConstraintGraphs = []
        self.OnlyGraph = ConstraintGraph("")
        for cfg in CFGConstructor.CFGs:
            c = ConstraintGraph(cfg)
            c.construct(cfg)
            c.essaConstruct(cfg)
            c.initializeLeafs()
            self.ConstraintGraphs.append(c)
            
    def copyGraph(self, name0, name1):
        s = SSA2CFG()
        s.construct(self.CFGConstructor.name_ssa[name0])
        graph = ConstraintGraph(s.cfg)
        graph.construct(s.cfg)
        graph.essaConstruct(s.cfg)
        graph.initializeLeafs()
        graph.cfg.name = name1
        graph.initializeChildArguments()
        for node in graph.MyNodes:
            if node.type == 'var':
                node.name = node.name + "#" + graph.cfg.name
            for condi in node.Conditions:
                condi[0] = str(condi[0]) + "#" + graph.cfg.name
        for condi in graph.MyConditions:
            condi.condition = condi.condition + "#" + graph.cfg.name
            condi.arg1 = condi.arg1 + "#" + graph.cfg.name
            condi.arg2 = condi.arg2 + "#" + graph.cfg.name
            condi.index = str(condi.index) + "#" + graph.cfg.name
        for index in range(0, len(graph.Arguments)):
            name = graph.Arguments[index]
            name = name + "#" + graph.cfg.name
            graph.Arguments[index] = name
        graph.returnName = graph.returnName + "#" + graph.cfg.name
        return graph
        

    def combineGraph(self):
        #把除了foo函数之外的所有函数变量重命名
        for graph in self.ConstraintGraphs:
            if graph.cfg.name == 'foo':
                graph.initializeArguments()
                continue
            graph.initializeChildArguments()
            for node in graph.MyNodes:
                if node.type == 'var':
                    node.name = node.name + "#" + graph.cfg.name
                for condi in node.Conditions:
                    condi[0] = str(condi[0]) + "#" + graph.cfg.name
            for condi in graph.MyConditions:
                condi.condition = condi.condition + "#" + graph.cfg.name
                condi.arg1 = condi.arg1 + "#" + graph.cfg.name
                condi.arg2 = condi.arg2 + "#" + graph.cfg.name
                condi.index = str(condi.index) + "#" + graph.cfg.name
            for index in range(0, len(graph.Arguments)):
                name = graph.Arguments[index]
                name = name + "#" + graph.cfg.name
                graph.Arguments[index] = name
            graph.returnName = graph.returnName + "#" + graph.cfg.name
  
        #以foo函数作为入口，把所有的函数连成同一个graph
        entrance = self.getGraphByName('foo')
        self.FinalConstraintGraphs.append(entrance)

        #entrance.initializeArguments()
        for node in entrance.MyNodes:
            if node.type == 'call':
                method_name = node.name
                method_name_ini = re.sub("\$.*", "", method_name)
                self.FinalConstraintGraphs.append(self.copyGraph(method_name_ini, method_name)) 
                method_graph = self.getFinalGraphByName(method_name)
                for index in range(0, len(node.args)):
                    rightNode = node.args[index]
                    method_arg = method_graph.Arguments[index]
                    leftNode = method_graph.getNode(name = method_arg, args = [], result = [], fromBlock = '', Statement = '')
                    leftNode.addArgument(rightNode)
                    rightNode.addResult(leftNode)
                    for node in method_graph.MyNodes:
                        node_name = re.sub("#.*", "", node.name)
                        method_arg_name = re.sub("#.*", "", method_arg)
                        if node_name.startswith(method_arg_name):
                            node.addArgument(rightNode)
                            rightNode.addResult(node)
            if node.type == 'ret':
                method_name = node.name
                method_graph = self.getFinalGraphByName(method_name)
                returnNode = method_graph.getNode(name = method_graph.returnName, args = [], result = [], fromBlock = '', Statement = '')
                #node.addArgument(returnNode)
                resultNode = node.result[0]
                resultNode.addArgument(returnNode)
                returnNode.addResult(resultNode)
                resultNode.args.remove(node)




    def getGraphByName(self, name):
        for graph in self.ConstraintGraphs:
            if graph.cfg.name == name:
                return graph
            
    def getFinalGraphByName(self, name):
        for graph in self.FinalConstraintGraphs:
            if graph.cfg.name == name:
                return graph
        
'''
    用于将一个Method构建CFG
'''
class SSA2CFG:
    def __init__(self):
        self.cfg = CFG()

    def construct(self, ssa_lines):
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
                method_name = re.sub("\(.*\)", '', ssa_line).strip()
                self.cfg.name = method_name
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
            if re.search("^<bb \d+>", ssa_line.strip()):
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
            
            if re.search("^<L\d+>", ssa_line.strip()):
                # 新建一个block
                group_id = re.search("\d+", ssa_line).group(0)
                group_id = "L" + group_id
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
                    if re.search("\(.*\)", next_ssa_line.strip()):
                        op_id = re.search("\(.*\)", next_ssa_line).group(0)[2:-2]
                        self.cfg.addEdge(Edge(cur_block_id, op_id, None))
                    index = index + 2
                else:
                    if(re.search("goto <L\d+>", next_ssa_line)):
                        goto_id = "L" + re.search("\d+", next_ssa_line).group(0)
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
                    if re.search("\(.*\)", next_ssa_line.strip()):
                        op_id = re.search("\(.*\)", next_ssa_line).group(0)[2:-2]
                        self.cfg.addEdge(Edge(cur_block_id, op_id, None))
                    index = index + 2
                else:
                    if(re.search("goto <L\d+>", next_ssa_line)):
                        goto_id = "L" + re.search("\d+", next_ssa_line).group(0)
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
                if re.search("\(.*\)", ssa_line.strip()):
                    op_id = re.search("\(.*\)", ssa_line).group(0)[2:-2]
                    self.cfg.addEdge(Edge(cur_block_id, op_id, None))
                continue
            #goto <L*> (不在if or else之后)
            if(re.search("^goto <L\d+>", ssa_line.strip())):
                goto_id = "L" + re.search("\d+", ssa_line).group(0)
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
    用于将一个CFG 构建Contraint Graph
'''
class ConstraintGraph:
    def __init__(self, cfg):
        self.MyNodes = []
        self.MyConditions = []
        self.cfg = cfg
        self.Arguments = []
        self.returnName = ''
        
    def getConditionByIndex(self, index):
        for condition in self.MyConditions:
            if condition.index == index:
                return condition
        
    #从self.MyNodes中获取节点或新建节点
    def getNode(self, name = '', args = [], result = [], fromBlock = 0, Statement = ''):
        name = name.strip()
        if "call#" in name:
            newtype = 'call'
            name = re.sub("call#", '', name)
            n = MyNode(t = newtype ,name = name, args = args, result = result, fromBlock = fromBlock, Statement = Statement)
            self.MyNodes.append(n)
            return n
        if "ret#" in name:
            newtype = 'ret'
            name = re.sub("ret#", '', name)
            n = MyNode(t = newtype ,name = name, args = args, result = result, fromBlock = fromBlock, Statement = Statement)
            self.MyNodes.append(n)
            return n

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
    
    #由名字获得Node
    def getNodeByName(self, name):
        name = name.strip()
        for myNode in self.MyNodes:
            if myNode.name == name:
                return myNode

    #构建SSA的Constraint Graph
    def construct(self, cfg):
        method_index = 0
        for Block in cfg.Blocks:
            for stmt in Block.Stmts:
                stmt_init = stmt
                stmt = stmt.strip(";")
                if "#" in stmt:
                    op = "PHI"
                    left = re.sub("\(.*\)", "", stmt.split("=")[0].strip("#").strip())
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
                    continue
                if "=" in stmt\
                and not "(float)" in stmt\
                and not "(int)" in stmt\
                and not re.search("=\s*[a-z0-9A-Z_]*\s*\(.*\)\s*;", stmt_init):
                    left = re.sub("\(.*\)", "",stmt.split("=")[0].strip())
                    rights = stmt.split("=")[1].strip() 
                    if len(rights.split()) > 1:
                        right1 = re.sub("\(.*\)", "",rights.split()[0])   # argument1
                        op = rights.split()[1]       # op
                        right2 = re.sub("\(.*\)", "",rights.split()[2])   # argument2
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
                        right = re.sub("\(.*\)", "", right)
                        rightNode = self.getNode(name = right, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode = self.getNode(name = left, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        leftNode.addArgument(rightNode)
                        rightNode.addResult(leftNode)
                        leftNode.fromBlock = Block.index
                if "=" in stmt and "(float)" in stmt:
                    left = re.sub("\(.*\)", "",stmt.split("=")[0].strip())
                    rights = stmt.split("=")[1].strip()
                    right = re.sub("\(.*\)", "", rights)
                    rightNode = self.getNode(name = right, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    leftNode = self.getNode(name = left, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    leftNode.addArgument(rightNode)
                    rightNode.addResult(leftNode)
                    leftNode.fromBlock = Block.index
                    leftNode.Range.lowBound.size = 'float'
                    leftNode.Range.highBound.size = 'float'
                if "=" in stmt and "(int)" in stmt:
                    left = re.sub("\(.*\)", "",stmt.split("=")[0].strip())
                    rights = stmt.split("=")[1].strip()
                    right = re.sub("\(.*\)", "", rights)
                    rightNode = self.getNode(name = right, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    leftNode = self.getNode(name = left, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    leftNode.addArgument(rightNode)
                    rightNode.addResult(leftNode)
                    leftNode.fromBlock = Block.index
                    leftNode.Range.lowBound.size = 'int'
                    leftNode.Range.highBound.size = 'int'
                if "=" in stmt and not "(float)" in stmt\
                and not "(int)" in stmt\
                and re.search("=\s*[a-z0-9A-Z_]*\s*\(.*\)\s*;", stmt_init):
                    method_index = method_index + 1
                    left = stmt.split("=")[0].strip()
                    rights = stmt.split("=")[1].strip()
                    arguments = re.search("\(.*\)", stmt).group(0)[1:-1]
                    function = re.sub("\(.*\)", "", rights).strip()
                    function = function + "$" + str(method_index)
                    arguments = arguments.split(",")
                    arguNodes = []
                    callNode = self.getNode(name = "call#" + function, args = [], result = [],  fromBlock = Block.index,  Statement = stmt)
                    for argu in arguments:
                        argu = re.sub("\(.*\)", "", argu).strip()
                        arguNode = self.getNode(name = argu, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                        arguNode.addResult(callNode)
                        arguNodes.append(arguNode)
                    leftNode = self.getNode(name = left, args = [], result = [], fromBlock = Block.index,  Statement = stmt)
                    returnNode = self.getNode(name = "ret#" + function, args = [], result = [], fromBlock = Block.index, Statement = stmt)
                    leftNode.addArgument(returnNode)
                    returnNode.addResult(leftNode)
                    for node in arguNodes:
                        callNode.addArgument(node)
                if 'return' in stmt:
                    tmpstmt = re.sub('return', '', stmt)
                    tmpstmt = tmpstmt.strip(";").strip()
                    tmpstmt = re.sub("\(.*\)", '', tmpstmt)
                    self.returnName = tmpstmt
                    continue

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
                        index = len(self.MyConditions)
                        self.MyConditions.append(MyCondition(condition,index))
                        tmp = self.MyConditions[index]
                        if '_' in tmp.arg1:
                            if self.getNodeByName(tmp.arg1) == None:
                                n = MyNode(t = 'var' ,name = tmp.arg1, args = [], result = [], fromBlock = Block.index, Statement = stmt)
                                self.MyNodes.append(n)
                        if '_' in tmp.arg2:
                            if self.getNodeByName(tmp.arg2) == None:
                                n = MyNode(t = 'var' ,name = tmp.arg2, args = [], result = [], fromBlock = Block.index, Statement = stmt)
                                self.MyNodes.append(n)
                        self.addCondition(Block.index, stmt, index, cfg, 0)
    
    #获得所有叶节点
    def getAllLeaves(self):
        result = []
        for myNode in self.MyNodes:
            if myNode.type == 'leaf':
                result.append(myNode)
        return result
    
    #初始化所有叶节点和声明的变量类型
    def initializeLeafs(self):
        LeafNodes = self.getAllLeaves()
        for node in LeafNodes:
            node.size = 'float'
            node.setRange(float(node.name), float(node.name), "float")
        for statement in self.cfg.Blocks[0].Stmts:
            statement = statement.strip(';')
            size = statement.split()[0]
            name = statement.split()[1]
            for node in self.MyNodes:
                if node.name.startswith(name):
                    node.Range.lowBound.size = size
                    node.Range.highBound.size = size

    #初始化所有Arguments
    def initializeArguments(self):
        for var in self.cfg.Arguments:
            var_size = var.split()[0]
            var_name = var.split()[1]
            var1, var2 = input("Enter Range For " + var_name + ": ").split()
            self.Arguments.append(var_name)
            for node in self.MyNodes:
                if node.name.startswith(var_name):
                    node.Range.lowBound.size = var_size
                    node.Range.highBound.size = var_size
                    node.Range.lowBound.value = var1
                    node.Range.highBound.value = var2

    #初始化所有子函数的Arguments
    def initializeChildArguments(self):
        for var in self.cfg.Arguments:
            var_size = var.split()[0]
            var_name = var.split()[1]
            self.Arguments.append(var_name)
            for node in self.MyNodes:
                if node.name.startswith(var_name):
                    node.Range.lowBound.size = var_size
                    node.Range.highBound.size = var_size


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
            if block == None:
                continue
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
    c = CFGConstructor("C:\\Users\\spy\\Desktop\\RangeAnalysis\\benchmark\\t7.ssa")
    m = ConstraintConstructor(c)
    m.combineGraph()
    Graph = ConstraintGraph(None)
    for graph in m.FinalConstraintGraphs:
        for node in graph.MyNodes:
            Graph.MyNodes.append(node)
        for condi in graph.MyConditions:
            Graph.MyConditions.append(condi)
        if graph.cfg.name == 'foo':
            Graph.returnName = graph.returnName

    '''
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\RangeAnalysis\\benchmark\\t8.ssa")
    c = ConstraintGraph(cfg)
    c.construct(cfg)
    c.essaConstruct(cfg)
    c.printGraph()
    #ssa2cfg.check()
    #print(len(cfg.Edges))
    #print(cfg.getBlockByNum(2))
    '''
    