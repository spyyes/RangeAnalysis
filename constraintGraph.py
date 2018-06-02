# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 16:46:57 2018

@author: spy
"""
from rangeAnalysis import *
from CFG_Constructor import *
import re
class ConstraintGraph:
    def __init__(self, constraints, Var_Classes):
        self.constraints = constraints
        self.Var_Classes = Var_Classes
    def construct(self):
        for val_init_name in self.Var_Classes:
            val_class = self.Var_Classes[val_init_name]
            for constraint in self.constraints:
                def_initial_name = re.sub("_.*", "", constraint.define).strip()
                def_name = constraint.define.strip()
                #需要添加进var_class
                if def_initial_name == val_init_name:
                    if not def_name in val_class.Names:
                        val_class.addName(def_name)
                    val_class.addConstraint(constraint)
        return self.Var_Classes
                    
    def test(self):
        for val in self.Var_Classes:
            valclass = self.Var_Classes[val]
            for n in valclass.Constraints:
                n.print_test()

class Widen:
    def __init__(self, Var_Classes):
        self.Var_Classes = Var_Classes
    def widen_entrance(self):
        for val_init_name in self.Var_Classes:
            val_class = self.Var_Classes[val_init_name]
            widening(val_class)
    def grow_op(self, Variable, range_down, rdc, range_up, ruc):
    	if Variable.range_up == 'undefined':
    		Variable.range_up = range_up
    		Variable.range_up_closure = ruc
    	else:
    		
    	if Variable.range_down == 'undefined':
    		Variable.range_down = range_down
    		Variable.range_down_closure = rdc

        
    def widening(self, valClass):
        for constraint in valClass.Constraints:
            if constraint.operator == "Set":
                con
            



if __name__ == '__main__':

    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\t1.ssa")


    ec = ExtractConstraints(cfg)
    constraints = ec.getConstraints()
    VariableClasses = ec.VarClasses
    cg = ConstraintGraph(constraints, VariableClasses)
    cg.construct()
    cg.test()
