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
        self.int_down = -2147483648
        self.int_up = 2147483647
        self.float_down = sys.float_info.min
        self.float_up = sys.float_info.max
        self.undefined_down = "-infinity"
        self.undefined_up = "infinity"
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
    def condition_Constraint(self, op1, opr, op2):
        op1_name = re.sub("_.*", "", op1)
        op2_name = re.sub("_.*", "", op2)
        type1 = self.Vars[op1_name]
        type2 = self.Vars[op2_name]
        returnList = []
        if(opr == "<"):
            if type1 == 'int':
                returnList.append(Constraint(op1, None, None, self.int_down, 0, op2 + '-1' , 0 ))
            else:
                returnList.append(Constraint(op1, None, None, self.float_down, 1, op2, 1 ))
            
            if type2 == 'int':
                returnList.append(Constraint(op2, None, None, op1 + "+1", 0, self.int_up, 0 ))
            else:
                returnList.append(Constraint(op2, None, None, op1, 1, self.float_up, 1 ))
        if(opr == '>'):
            if type1 == 'int':
                returnList.append(Constraint(op1, None, None, op2 + "+1", 0, self.int_up, 0 ))
            else:
                returnList.append(Constraint(op1, None, None, op2, 1, self.float_up, 1))
            
            if type2 == 'int':
                returnList.append(Constraint(op2, None, None, self.int_down, 0, op1 + "-1", 0 ))
            else:
                returnList.append(Constraint(op2, None, None, self.float_down, 1, op1, 1 ))
        if(opr == '<='):
            if type1 == 'int':
                returnList.append(Constraint(op1, None, None, self.int_down, 0, op2 + '-1' , 0 ))
            else:
                returnList.append(Constraint(op1, None, None, self.float_down, 1, op2, 1 ))
            
            if type2 == 'int':
                returnList.append(Constraint(op2, None, None, op1 + "+1", 0, self.int_up, 0 ))
            else:
                returnList.append(Constraint(op2, None, None, op1, 1, self.float_up, 1 ))
    
    def getConstraints(self):
        #rootBlock = self.cfg.getRootBlock()
        rootBlock = self.cfg.getBlockByNum('5')
        
        for stmt in rootBlock.Stmts:
            if re.search("int \w+;", stmt):
                variable_name = re.sub("int ", "", stmt.strip())
                variable_name = re.sub(";", "", variable_name)
                self.Constraints.append(Constraint(variable_name, None, None, "Set", self.int_down, 0, self.int_up, 0))
                self.Vars[variable_name] = 'int'
                continue
            if re.search("float \w+;", stmt):
                variable_name = re.sub("float ", "", stmt.strip())
                variable_name = re.sub(";", "", variable_name)             
                self.Constraints.append(Constraint(variable_name, None, None, "Set", self.float_down, 1, self.float_up, 1))
                self.Vars[variable_name] = 'float'
                continue
            if re.search("\w+\s=\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name = stmt.split("=")[1].strip(';').strip()
                self.Constraints.append(Constraint(def_name, None, None, "Set", use_name, 0, use_name, 0))
            
            if re.search("\w+\s=\s\S+\s\+\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('+')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('+')[1].strip()
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None))
            
            if re.search("\w+\s=\s\S+\s\-\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('-')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('-')[1].strip()
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None))
                
            if re.search("\w+\s=\s\S+\s\*\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('*')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('*')[1].strip()
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None))
                
            if re.search("\w+\s=\s\S+\s\/\s\S+",stmt):
                def_name = stmt.split("=")[0].strip()
                use_name1 = stmt.split("=")[1].strip(';').split('/')[0].strip()
                use_name2 = stmt.split("=")[1].strip(';').split('/')[1].strip()
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "+", None, None, None, None))
                
            if re.search("# \S+ = PHI <\S+, \S+>", stmt):
                def_name = stmt.split("=")[0].strip("#").strip()
                use_name1 = stmt.split("<")[1].split(",")[0].strip()
                use_name1 = re.sub("\(.*\)","", use_name1)
                use_name2 = stmt.split("<")[1].split(",")[1].strip(">").strip()
                use_name2 = re.sub("\(.*\)","", use_name2)
                self.Constraints.append(Constraint(def_name, use_name1, use_name2, "PHI", None, None, None, None))
            
            if re.search("if .* goto .*", stmt):
                condition = re.search("\(.*\)", stmt).group().strip("(").strip(")").strip()
                
                if("not" in condition):
                    condition = re.sub("not", "", stmt).strip()
                    op1 = condition.split()[0].strip()
                    opr = self.trans_OP(condition.split()[1].strip())
                    op2 = condition.split()[2].strip()
                else:
                    op1 = condition.split()[0].strip()
                    opr = condition.split()[1].strip()
                    op2 = condition.split()[2].strip()
                print(ops)
                #self.Constraints.append(Constraint())
                
                
                
        
class Constraint:
    def __init__(self, define, use1, use2, operator, range_down, rdc, range_up, ruc):
        self.define = define
        self.use1 = use1
        self.use2 = use2
        self.operator = operator
        self.range_down = range_down
        self.range_down_closure = rdc 
        self.range_up = range_up
        self.range_up_closure = ruc
        
    
    

if __name__ == '__main__':
    
    
    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\t1.ssa")
    ec = ExtractConstraints(cfg)
    ec.getConstraints()
    #print(len(cfg.Edges))
    