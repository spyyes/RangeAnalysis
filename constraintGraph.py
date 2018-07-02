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
        self.int_down = "minint"
        self.int_up = "maxint"
        self.float_down = "minfloat"
        self.float_up = "maxfloat"
        self.undefined = "undefined"
    def widen_entrance(self):
        for val_init_name in self.Var_Classes:
            val_class = self.Var_Classes[val_init_name]
            widening(val_class)
    #返回1：大于； 0：等于； -1 小于； 'future'未定义
    def compare(self, op1, op2):
        
    def grow_op(self, Variable, range_down, rdc, range_up, ruc):
        if Variable.range_up == 'undefined' and Variable.range_down == 'undefined':
            Variable.range_up = range_up
            Variable.range_up_closure = ruc
            Variable.range_down = range_down
            Variable.range_down_closure = rdc
            return
        if self.compare(range_down, Variable.range_down) == -1 and self.compare(range_up, Variable.range_up) == 1:
            if Variable.var_type == 'int':
                Variable.range_down = self.int_down
                Variable.range_down_closure = 0
                Variable.range_up = self.int_up
                Variable.range_up_closure = 0
            else:
                Variable.range_down = self.float_down
                Variable.range_down_closure = 1
                Variable.range_up = self.float_up
                Variable.range_up_closure = 1
            return
        if self.compare(range_down, Variable.range_down) == -1:
            if Variable.var_type == 'int':
                Variable.range_down = self.int_down
                Variable.range_down_closure = 0
            else:
                Variable.range_down = self.float_down
                Variable.range_down_closure = 1
            return
        if self.compare(range_up, Variable.range_up) == 1:
            if Variable.var_type == 'int':
                Variable.range_up = self.int_up
                Variable.range_up_closure = 0
            else:
                Variable.range_up = self.float_up
                Variable.range_up_closure = 1
            return  
        return
    #计算两个variable的加和
    def e_add(self, Va, Vb):
        a_down = Va.range_down
        a_up = Va.range_up
        b_down = Vb.range_down
        b_up = Vb.range_up
        adc = Va.range_down_closure
        auc = Va.range_up_closure
        bdc = Vb.range_down_closure
        buc = Vb.range_up_closure   
        result = []
        result_closure = []
        if a_down = 'undefined' or b_down = 'undefined':
            result = ['undefined', 'undefined']
            result_closure = [adc, auc]
            return [result, result_closure]
        if a.var_type == 'int':
            if a_down == self.int_down or b_down == self.int_down:
                result[0] = self.int_down
            else:
                result[0] = int(a_down) + int(b_down)
            if a_up == self.int_up or b_up == self.int_up:
                result[1] = self.int_up
            else:
                result[1] = int(a_up) + int(b_up)
        else:
            if a_down == self.float_down or b_down == self.float_down:
                result[0] = self.float_down
            else:
                result[0] = float(a_down) + float(b_down)
            if a_up == self.float_up or b_up == self.float_up:
                result[1] = self.float_up
            else:
                result[1] = float(a_up) + float(b_up)
        if adc == 1 or bdc == 1:
            result_closure[0] = 1
        else:
            result_closure[0] = 0
        if auc == 1 or buc == 1:
            result_closure[1] = 1
        else:
            result_closure[1] = 0
        return [result, result_closure]
    def e_add_val(self, Va, val):
        a_down = Va.range_down
        a_up = Va.range_up
        adc = Va.range_down_closure
        auc = Va.range_up_closure
        result = []
        result_closure = []
        if a_down = 'undefined' or b_down = 'undefined':
            result = ['undefined', 'undefined']
            result_closure = [adc, auc]
            return [result, result_closure]
        if a.var_type == 'int':
            if a_down == self.int_down:
                result[0] = self.int_down
            else:
                result[0] = int(a_down) + int(val)
            if a_up == self.int_up:
                result[1] = self.int_up
            else:
                result[1] = int(a_up) + int(val)
        else:
            if a_down == self.float_down:
                result[0] = self.float_down
            else:
                result[0] = float(a_down) + float(val)
            if a_up == self.float_up:
                result[1] = self.float_up
            else:
                result[1] = float(a_up) + float(val)
        result_closure[0] = adc
        result_closure[1] = auc
        return [result, result_closure]        
    
    #计算两个variable的相减
    def e_minus(self, Va, Vb):
        a_down = Va.range_down
        a_up = Va.range_up
        b_down = Vb.range_down
        b_up = Vb.range_up
        adc = Va.range_down_closure
        auc = Va.range_up_closure
        bdc = Vb.range_down_closure
        buc = Vb.range_up_closure   
        result = []
        result_closure = []
        if a_down = 'undefined' or b_down = 'undefined':
            result = ['undefined', 'undefined']
            result_closure = [adc, auc]
            return [result, result_closure]
        if a.var_type == 'int':
            if a_down == self.int_down or b_down == self.int_down:
                result[0] = self.int_down
            else:
                result[0] = int(a_down) - int(b_down)
            if a_up == self.int_up or b_up == self.int_up:
                result[1] = self.int_up
            else:
                result[1] = int(a_up) - int(b_up)
        else:
            if a_down == self.float_down or b_down == self.float_down:
                result[0] = self.float_down
            else:
                result[0] = float(a_down) - float(b_down)
            if a_up == self.float_up or b_up == self.float_up:
                result[1] = self.float_up
            else:
                result[1] = float(a_up) - float(b_up)
        if adc == 1 or bdc == 1:
            result_closure[0] = 1
        else:
            result_closure[0] = 0
        if auc == 1 or buc == 1:
            result_closure[1] = 1
        else:
            result_closure[1] = 0
        return [result, result_closure]
    
    def e_minus_val(self, Va, val):
        a_down = Va.range_down
        a_up = Va.range_up
        adc = Va.range_down_closure
        auc = Va.range_up_closure
        result = []
        result_closure = []
        if a_down = 'undefined' or b_down = 'undefined':
            result = ['undefined', 'undefined']
            result_closure = [adc, auc]
            return [result, result_closure]
        if a.var_type == 'int':
            if a_down == self.int_down:
                result[0] = self.int_down
            else:
                result[0] = int(a_down) - int(val)
            if a_up == self.int_up:
                result[1] = self.int_up
            else:
                result[1] = int(a_up) - int(val)
        else:
            if a_down == self.float_down:
                result[0] = self.float_down
            else:
                result[0] = float(a_down) - float(val)
            if a_up == self.float_up:
                result[1] = self.float_up
            else:
                result[1] = float(a_up) - float(val)
        result_closure[0] = adc
        result_closure[1] = auc
        return [result, result_closure] 
    def widening(self, valClass):
        for constraint in valClass.Constraints:
            if len(constraint.needFuture) == 0:
                continue
            if constraint.operator == "Set":
                defName = constraint.define.strip()
                self.grow_op(valClass.Names[defName], constraint.range_down, constraint.rdc, constraint.range_up, constraint.ruc)
            if constraint.operator == "PHI":
                defName = constraint.define.strip()
                use1 = constraint.use1.strip()
                use1_down = valClass.Names[use1].range_down
                use1_rdc = valClass.Names[use1].range_down_closure
                use1_up = valClass.Names[use1].
                use1_ruc = valClass.Names[use1].range_up_closure
                use2 = constraint.use2.strip()
                use2_down = valClass.Names[use2].range_down
                use2_rdc = valClass.Names[use2].range_down_closure
                use2_up = valClass.Names[use2].range_up 
                use2_ruc = valClass.Names[use2].range_up_closure
                self.grown_op(valClass.Names[defName], use1_down, use1_rdc, use1_up, use1_ruc )
                self.grown_op(valClass.Names[defName], use2_down, use2_rdc, use2_up, use2_ruc )
            if constraint.operator == "+":
                use1 = constraint.use1.strip()
                use2 = constraint.use2.strip()
                defName = constraint.define.strip()
                if not use2 in valClass.Names:
                    [[ed, eu], [edc, euc]] = self.e_add_val(valClass.Names[use1], use2)
                    self.grown_op(valClass.Names[defName], ed, edc, eu, euc)
                else:
                    [[ed, eu], [edc, euc]] = self.e_add(valClass.Names[use1], valClass.Names[use2])
                    self.grown_op(valClass.Names[defName], ed, edc, eu, euc)
            if constraint.operator == "-":
                use1 = constraint.use1.strip()
                use2 = constraint.use2.strip()
                defName = constraint.define.strip()
                if not use2 in valClass.Names:
                    [[ed, eu], [edc, euc]] = self.e_minus_val(valClass.Names[use1], use2)
                    self.grown_op(valClass.Names[defName], ed, edc, eu, euc)
                else:
                    [[ed, eu], [edc, euc]] = self.e_minus(valClass.Names[use1], valClass.Names[use2])
                    self.grown_op(valClass.Names[defName], ed, edc, eu, euc)     
                



if __name__ == '__main__':

    ssa2cfg = SSA2CFG()
    cfg = ssa2cfg.construct("C:\\Users\\spy\\Desktop\\t1.ssa")


    ec = ExtractConstraints(cfg)
    constraints = ec.getConstraints()
    VariableClasses = ec.VarClasses
    cg = ConstraintGraph(constraints, VariableClasses)
    cg.construct()
    cg.test()
