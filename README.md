# Range Analysis

> 编译原理 大作业 简单C++程序的范围分析

## 1. 实验说明

**作业要求：**针对静态单赋值（SSA）形式的函数中间代码输入，输出函数返回值的范围。

**实现思路：** 基本根据 2013年在CGO会议上提出的“三步法”范围分析法加以实现，求得各个变量的范围。

**算法优势：**空间复杂度和时间复杂度都是$O(n)​$，效率高。

**算法瓶颈：** “三步法”的功能存在较大局限，它只能分析各个变量的最大范围，对活跃变量只做了最简单的考虑，因此最终得到的范围比较不准确，往往只能得到范围的一个界。

## 2. 算法原理

**简单概括：**采用三步法

**具体介绍：** 我将算法原理整理成了一份PPT，详见`/docs/*.ppt`

### 2.1 构建CFG 

**代码见：`\eSSAConstraintGraph.py; \structure.py`**

功能：解析SSA，构建CFG。

由于函数之间存在调用关系，因此首先把SSA划分成不同的函数的SSA，再分别构建CFG。CFG中保留了每一个函数的语句、Block之间的关系，为下一步构建Constraint Graph打基础。

CFG的结构如下：

```python
#CFG类      
class CFG:
    def __init__(self):
        self.name = ''
        self.Blocks = []
        self.Edges = []
        self.Arguments = []
```

### 2.2 构建Constraint Graph

三步法的前提是构建Constraint Graph。数据结构如下。在这一步中，我用自己定义的数据类型`MyNode`来表示一条`Constraint`。

```python
#Constraint Graph类      
class ConstraintGraph:
    def __init__(self, cfg):
        self.MyNodes = []			#基本节点，每一个节点是一个Constraint
        self.MyConditions = []		#用于后面E-SSA Constraint Graph补充条件
        self.cfg = cfg			 
        self.Arguments = []			#输入参数
        self.returnName = ''		#输出参数
#MyNode : Constraint Graph的节点
class MyNode:
    def __init__(self, t= "", name = "",  args = [], result = [], fromBlock = 0, Statement = ''):
        self.type = t 			#节点类型：leave 叶节点存放范围和值 #op运算符 #var变量名
        self.name = name.strip()  #节点名称：运算名称，或变量名称
        self.args = args	#参数，一个节点是另一个节点的argument，意味着二者之间有边相连
        self.result = result        #被用到哪，一个节点是另一个节点的result，意味着二者之间有边相连
        self.Conditions = []        #约束条件， 在后面E-SSA Constraint Graph中补充条件
        self.fromBlock = fromBlock  #在CFG的哪个Block中定义的
        self.Statement = Statement  #在SSA中的哪条Statement中
        self.Range = Range()		#节点范围
        self.size = ''
        self.input = False
# Range由两个Bound组成 
class Range:
    def __init__(self ):
        self.lowBound = Bound()
        self.highBound = Bound()
#Bound由值和类型组成
class Bound:
    def __init__(self):
        self.value = 'None'      # inf 最大值 ； -inf 最小值; None 未设置； Not Exists 不存在
        self.size = 'None'       #边界是 int or float
```

需要注意的是，在解决两个函数之间的调用关系时，将被调用的函数**内联进原函数**。我将被调用的函数的所有变量名都加入相应的后缀，比如`foo`调用`bar`函数，那么`bar`中的变量`i_1`将被更名保存为`i_1#bar$1`，其中#是变量原名和后缀分割符，$是函数名和一个随机数的分割符，\$的作用是为了区分多次调用同一个函数的情况。

### 2.3 构建E-SSA Constraint Graph

这一步用于解决条件的添加。诸如`if (i_2 < j_3)`这样的条件。在MyNode节点类型中，我设置了Conditions结构用于保存条件。Condition的数据结构如下：

```python
#Class Description : Constraint Graph中的条件，附加在MyNode中
class MyCondition:
    def __init__(self, condition, index):
        self.condition = condition
        self.arg1 = re.sub("\(.*\)", "",condition.split()[0].strip())
        self.arg2 = re.sub("\(.*\)", "",condition.split()[2].strip())
        self.op = condition.split()[1].strip()
        self.index = index
```

其中，`arg1`和`arg2`分别表示条件的两个参数，`op`表示条件的比较运算符。在`Future Resolution`这一步会进行比较，进行范围的约束。

以`t7.ssa`为例，得到的E-SSA Constraint Graph如下：

```
call bar$1  in 2 : |Arguments: i_2,|Result: |Conditions: 
var i_2  in 2 : |Arguments: |Result: bar$1,i#bar$1,i_2#bar$1,|Conditions: 
var j_4  in 2 : |Arguments: _1#bar$1,|Result: bar$2,i#bar$2,i_2#bar$2,|Conditions: 
ret bar$1  in 2 : |Arguments: |Result: j_4,|Conditions: 
call bar$2  in 2 : |Arguments: j_4,|Result: |Conditions: 
var k_6  in 2 : |Arguments: _1#bar$2,|Result: _7,|Conditions: 
ret bar$2  in 2 : |Arguments: |Result: k_6,|Conditions: 
var _7  in 2 : |Arguments: k_6,|Result: |Conditions: 
var i_2#bar$1  in 3 : |Arguments: i_2,|Result: +,-,|Conditions: 0#bar$1 0|
leaf 10  in 3 : |Arguments: |Result: +,|Conditions: 
op +  in 3 : |Arguments: i_2#bar$1,10,|Result: _3#bar$1,|Conditions: 0#bar$1 0|
var _3#bar$1  in 3 : |Arguments: +,|Result: PHI,|Conditions: 0#bar$1 0|
leaf 5  in 4 : |Arguments: |Result: -,|Conditions: 
op -  in 4 : |Arguments: 5,i_2#bar$1,|Result: _4#bar$1,|Conditions: 0#bar$1 1|
var _4#bar$1  in 4 : |Arguments: -,|Result: PHI,|Conditions: 0#bar$1 1|
op PHI  in 4 : |Arguments: _3#bar$1,_4#bar$1,|Result: _1#bar$1,|Conditions: 0#bar$1 1|
var _1#bar$1  in 4 : |Arguments: PHI,|Result: j_4,|Conditions: 0#bar$1 1|
leaf i#bar$1  in  : |Arguments: i_2,|Result: |Conditions: 
var i_2#bar$2  in 3 : |Arguments: j_4,|Result: +,-,|Conditions: 0#bar$2 0|
leaf 10  in 3 : |Arguments: |Result: +,|Conditions: 
op +  in 3 : |Arguments: i_2#bar$2,10,|Result: _3#bar$2,|Conditions: 0#bar$2 0|
var _3#bar$2  in 3 : |Arguments: +,|Result: PHI,|Conditions: 0#bar$2 0|
leaf 5  in 4 : |Arguments: |Result: -,|Conditions: 
op -  in 4 : |Arguments: 5,i_2#bar$2,|Result: _4#bar$2,|Conditions: 0#bar$2 1|
var _4#bar$2  in 4 : |Arguments: -,|Result: PHI,|Conditions: 0#bar$2 1|
op PHI  in 4 : |Arguments: _3#bar$2,_4#bar$2,|Result: _1#bar$2,|Conditions: 0#bar$2 1|
var _1#bar$2  in 4 : |Arguments: PHI,|Result: k_6,|Conditions: 0#bar$2 1|
leaf i#bar$2  in  : |Arguments: j_4,|Result: |Conditions: 

Conditions:
i_2(D) >= 0#bar$1 0#bar$1,i_2(D) >= 0#bar$2 0#bar$2,
```

### 2.3 三步法

#### 2.3.1 Widen

#### 2.3.2 Future Resolution

#### 2.3.3 Narrow



## 3. 项目使用

`python main.py` （ssa文件路径在main.py中设置）

不需要安装任何库。

## 4. 实验结果

```sh
#t1.SSA
Reference Range:[100, 100]
Output Range: [100, +inf]
#t2.SSA
Reference Range:[200, 300]
Output Range: [200, +inf]
#t3.SSA
Reference Range:[20, 50]
Output Range: [20, +inf]
#t4.SSA
Reference Range:[0, +inf]
Output Range: [0, +inf]
#t5.SSA
Reference Range:[210, 210]
Output Range: [0, +inf]
#t6.SSA
Reference Range:[-9, 10]
Output Range: [-9, 10]
#t7.SSA
Reference Range:[16, 30]
Output Range: [5, 30]
#t8.SSA
Reference Range:[-3.2192308, 5.94230769]
Output Range: [-0.41923075526423315, 14.700000286102295]
#t9.SSA
Reference Range:[9791, 9791]
Output Range: [-10, +inf]
#t10.SSA
Reference Range:[-10, 40]
Output Range: [1, 1]
```



