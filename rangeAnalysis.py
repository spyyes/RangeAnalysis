# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 20:01:09 2018

@author: spy
"""
from CFG_Constructor import SSA2CFG
import re
import sys

class ExtractConstraints:
    def __init__(self, cfg):
        self.cfg = cfg
        self.Vars = {}
        self.Constraints = []
        self.VarClasses = {}
        self.int_down = "minint"
        self.int_up = "maxint"
        self.float_down = "minfloat"
        self.float_up = "maxfloat"
        self.undefined = "undefined"
    
    #专为 else设计的条件翻转
    def trans_OP(self, op):
        if(op == "<"):
            return ">="
        if(op == ">"):
            return "<="
        if(op == "<="):
            return ">"
        if(op == ">="):
            return "<"
        if(op == "=="):
            return "!="
        if(op == "!="):
            return "=="
    
    #条件语句的范围分析
    def condition_Constraint(self, op1, opr, op2):
        op1_name = re.sub("_.*", "", op1)
        op2_name = re.sub("_.*", "", op2)
        if(op1_name in self.Vars):
            type1 = self.Vars[op1_name]
        else:
            if("." in op1_name):
                type1 = "float"
            else:
                type1 = "int"
        if(op2_name in self.Vars):
            type2 = self.Vars[op2_name]
        else:
            if("." in op2_name):
                type2 = "float"
            else:
                type2 = "int"
        op1_future = []
        op2_future = []
        returnList = []
        if op1_name in self.Vars and op2_name in self.Vars and op1_name!= op2_name:
            op1_future = [op2]
            op2_future = [op1]
            if(opr == "<"):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", self.int_down, 0, op2 + '-1' , 0, op1_future))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", self.float_down, 1, op2, 1, op1_future ))
                
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", op1 + "+1", 0, self.int_up, 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", op1, 1, self.float_up, 1, op2_future))
            if(opr == '>'):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", op2 + "+1", 0, self.int_up, 0, op1_future ))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", op2, 1, self.float_up, 1, op1_future))
                
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", self.int_down, 0, op1 + "-1", 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", self.float_down, 1, op1, 1, op2_future ))
            if(opr == '<='):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", self.int_down, 0, op2 , 0, op1_future ))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", self.float_down, 1, op2, 0, op1_future ))
                
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", op1, 0, self.int_up, 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", op1, 0, self.float_up, 1, op2_future ))
            if(opr == '>='):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", op2, 0, self.int_up, 0, op1_future ))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", op2, 0, self.float_up, 1, op1_future))
                
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", self.int_down, 0, op1, 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", self.float_down, 1, op1, 0, op2_future ))   
            if(opr == '=='):
                returnList.append(Constraint(op1, None, None, "Set", op2, 0, op2, 0, op1_future))
                returnList.append(Constraint(op2, None, None, "Set", op1, 0, op1, 0, op2_future))
            if(opr == '!='):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", op2 + "+1", 0, self.int_up, 0, op1_future ))
                    returnList.append(Constraint(op1, None, None, "Set", self.int_down, 0, op2 + "-1", 0, op1_future))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", op2, 1, self.float_up, 1, op1_future ))
                    returnList.append(Constraint(op1, None, None, "Set", self.float_down, 1, op2, 1, op1_future))
                
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", op1 + "+1", 0, self.int_up, 0 , op2_future))
                    returnList.append(Constraint(op2, None, None, "Set", self.int_down, 0, op1 + "-1", 0, op2_future))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", op1, 1, self.float_up, 1, op2_future ))
                    returnList.append(Constraint(op2, None, None, "Set", self.float_down, 1, op1, 1, op2_future))
        elif op1_name in self.Vars and not op2_name in self.Vars:
            if(opr == "<"):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", self.int_down, 0, op2 + '-1' , 0, op1_future))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", self.float_down, 1, op2, 1, op1_future ))
            if(opr == '>'):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", op2 + "+1", 0, self.int_up, 0, op1_future ))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", op2, 1, self.float_up, 1, op1_future))
            if(opr == '<='):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", self.int_down, 0, op2 , 0, op1_future ))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", self.float_down, 1, op2, 0, op1_future ))
            if(opr == '>='):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", op2, 0, self.int_up, 0, op1_future ))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", op2, 0, self.float_up, 1, op1_future))
            if(opr == '=='):
                returnList.append(Constraint(op1, None, None, "Set", op2, 0, op2, 0, op1_future))
            if(opr == '!='):
                if type1 == 'int':
                    returnList.append(Constraint(op1, None, None, "Set", op2 + "+1", 0, self.int_up, 0, op1_future ))
                    returnList.append(Constraint(op1, None, None, "Set", self.int_down, 0, op2 + "-1", 0, op1_future))
                else:
                    returnList.append(Constraint(op1, None, None, "Set", op2, 1, self.float_up, 1, op1_future ))
                    returnList.append(Constraint(op1, None, None, "Set", self.float_down, 1, op2, 1, op1_future))
        elif op2_name in self.Vars and not op1_name in self.Vars:
            if(opr == "<"):
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", op1 + "+1", 0, self.int_up, 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", op1, 1, self.float_up, 1, op2_future))
            if(opr == '>'):
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", self.int_down, 0, op1 + "-1", 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", self.float_down, 1, op1, 1, op2_future ))
            if(opr == '<='):
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", op1, 0, self.int_up, 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", op1, 0, self.float_up, 1, op2_future ))
            if(opr == '>='):
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", self.int_down, 0, op1, 0, op2_future ))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", self.float_down, 1, op1, 0, op2_future ))   
            if(opr == '=='):
                returnList.append(Constraint(op2, None, None, "Set", op1, 0, op1, 0, op2_future))
            if(opr == '!='):
                if type2 == 'int':
                    returnList.append(Constraint(op2, None, None, "Set", op1 + "+1", 0, self.int_up, 0 , op2_future))
                    returnList.append(Constraint(op2, None, None, "Set", self.int_down, 0, op1 + "-1", 0, op2_future))
                else:
                    returnList.append(Constraint(op2, None, None, "Set", op1, 1, self.float_up, 1, op2_future ))
                    returnList.append(Constraint(op2, None, None, "Set", self.float_down, 1, op1, 1, op2_future))
        return returnList


            
    def getConstraints(self):
        #rootBlock = self.cfg.getRootBlock()
        #rootBlock = self.cfg.getBlockByNum('5')
        Stmts = []
        for block in self.cfg.Blocks:
            for stmt in block.Stmts:
                Stmts.append(stmt)
        
        for stmt in Stmts:
            #变量声明 int
            if re.search("^int \w+;", stmt):
                variable_name = re.sub("int ", "", stmt.strip())
                variable_name = re.sub(";", "", variable_name)
                self.Constraints.append(Constraint(variable_name, None, None, "Set", self.undefined, 0, self.undefined, 0, []))
                self.Vars[variable_name] = 'int'
                self.VarClasses[variable_name] = Variable_Class(variable_name, 'int')
                continue
            #变量声明 float
            if re.search("^float \w+;", stmt):
                variable_name = re.sub("float ", "", stmt.strip())
                variable_name = re.sub(";", "", variable_name)             
                self.Constraints.append(Constraint(variable_name, None, None, "Set", self.undefined, 1, self.undefined, 1, []))
                self.Vars[variable_name] = 'float'
                self.VarClasses[variable_name] = Variable_Class(variable_name, 'float')
                continue
            # 变量赋值 a = b
            if re.search("^\w+\s=\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name = stmt.split("=")[1].strip(';').strip()
                def_init = re.sub("_.*", "", def_name)
                use_init = re.sub("_.*", "", use_name)
                if re.search("[a-zA-Z]", use_name[0]) and def_init != use_init:
                    self.Constraints.append(Constraint(def_name, None, None, "Set", use_name, 0, use_name, 0, [use_name]))
                else:
                    self.Constraints.append(Constraint(def_name, None, None, "Set", use_name, 0, use_name, 0, []))
                continue
            # 变量计算 +
            if re.search("^\w+\s=\s\S+\s\+\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('+')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('+')[1].strip()
                future = []
                def_init = re.sub("_.*", "", def_name)
                use1_init = re.sub("_.*", "", use_name1)
                use2_init = re.sub("_.*", "", use_name2)
                if re.search("[a-zA-Z]", use_name1[0]) and def_init != use1_init:
                    future.append(use_name1)
                if re.search("[a-zA-Z]", use_name2[0]) and def_init != use2_init:
                    future.append(use_name2)
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None, future))
                continue
            # 变量计算 -
            if re.search("^\w+\s=\s\S+\s\-\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('-')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('-')[1].strip()
                future = []
                def_init = re.sub("_.*", "", def_name)
                use1_init = re.sub("_.*", "", use_name1)
                use2_init = re.sub("_.*", "", use_name2)
                if re.search("[a-zA-Z]", use_name1[0]) and def_init != use1_init:
                    future.append(use_name1)
                if re.search("[a-zA-Z]", use_name2[0]) and def_init != use2_init:
                    future.append(use_name2)
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None, future))
                continue
            # 变量计算 *
            if re.search("^\w+\s=\s\S+\s\*\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('*')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('*')[1].strip()
                future = []
                def_init = re.sub("_.*", "", def_name)
                use1_init = re.sub("_.*", "", use_name1)
                use2_init = re.sub("_.*", "", use_name2)
                if re.search("[a-zA-Z]", use_name1[0]) and def_init != use1_init:
                    future.append(use_name1)
                if re.search("[a-zA-Z]", use_name2[0]) and def_init != use2_init:
                    future.append(use_name2)
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None, future))
                continue
            # 变量计算 /
            if re.search("^\w+\s=\s\S+\s\/\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('/')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('/')[1].strip()
                future = []
                def_init = re.sub("_.*", "", def_name)
                use1_init = re.sub("_.*", "", use_name1)
                use2_init = re.sub("_.*", "", use_name2)
                if re.search("[a-zA-Z]", use_name1[0]) and def_init != use1_init:
                    future.append(use_name1)
                if re.search("[a-zA-Z]", use_name2[0]) and def_init != use2_init:
                    future.append(use_name2)
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None, future))
                continue
            # PHI语句
            if re.search("^# \S+ = PHI <\S+, \S+>", stmt):
                def_name = stmt.split("=")[0].strip("#").strip()
                use_name1 = stmt.split("<")[1].split(",")[0].strip()
                use_name1 = re.sub("\(.*\)","", use_name1)
                use_name2 = stmt.split("<")[1].split(",")[1].strip(">").strip()
                use_name2 = re.sub("\(.*\)","", use_name2)
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "PHI", None, None, None, None, []))
                continue
            if re.search("^if .* goto .*", stmt):
                condition = re.search("\(.*\)", stmt).group().strip("(").strip(")").strip()
                if("not" in condition):
                    condition = re.sub("not", "", condition).strip()
                    op1 = condition.split()[0].strip()
                    opr = self.trans_OP(condition.split()[1].strip())
                    op2 = condition.split()[2].strip()
                else:
                    op1 = condition.split()[0].strip()
                    opr = condition.split()[1].strip()
                    op2 = condition.split()[2].strip()
                for c in self.condition_Constraint(op1, opr, op2):
                    self.Constraints.append(c)
        return self.Constraints
class Variable:
    def __init__(self, name, var_type):
        self.name = name
        self.var_type = var_type
        self.range_down = ''
        self.range_down_closure = ''
        self.range_up = ''
        self.range_up_closure = ''
    def set_range_down(self, range_down, range_down_closure):
        self.range_down = range_down
        self.range_down_closure = range_down_closure
    def set_range_up(self, range_up, range_up_closure):
        self.range_up = range_up
        self.range_up_closure = range_up_closure
    

class Variable_Class:
    def __init__(self, initial_name, var_type):
        self.initial_name = initial_name
        self.var_type = var_type
        self.Names = {}
        self.Constraints = []
        self.Names[initial_name] = Variable(initial_name, var_type)
    def addName(self, add_name):
        self.Names[add_name] = Variable(add_name, self.var_type)
    def addConstraint(self, add_constraint):
        self.Constraints.append(add_constraint)
    def getVariableByName(self, name):
        for v in self.Names:
            if v == name:
                return self.Names[v]
        return None
        
    
        
class Constraint:
    def __init__(self, define, use1, use2, operator, range_down, rdc, range_up, ruc, need):
        self.define = define
        self.use1 = use1
        self.use2 = use2
        self.operator = operator
        self.range_down = range_down
        self.range_down_closure = rdc 
        self.range_up = range_up
        self.range_up_closure = ruc
        self.needFuture = need

    def print_test(self):
        print(self.define, end=" ")
        if(self.use1 == None):
            print("None", end = " ")
        else:
            print(self.use1, end = " ")
        if(self.use2 == None):
            print("None", end = " ")
        else:
            print(self.use2, end = " ")
        if(self.operator == None):
            print("None", end = " ")
        else:
            print(self.operator, end = " ")
        if(self.range_down == None):
            print("None", end = " ")
        else:
            print(self.range_down, end = " ")   
        if(self.range_down_closure == None):
            print("None", end = " ")
        else:
            print(self.range_down_closure, end = " ")   
        if(self.range_up == None):
            print("None", end = " ")
        else:
            print(self.range_up, end = " ")   
        if(self.range_up_closure == None):
            print("None", end = " ")
        else:
            print(self.range_up_closure, end = " ")   
        print("")
    
    

if __name__ == '__main__':
    
    
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\t1.ssa")
    
    

    ec = ExtractConstraints(cfg)
    constraints = ec.getConstraints()
    print(constraints)
    VariableClasses = ec.VarClasses
    for v in VariableClasses:
        v = VariableClasses[v]
        print(v.initial_name)
    
    
    
    #for c in ec.Constraints:
     #   c.print_test()

    #print(len(cfg.Edges))
    