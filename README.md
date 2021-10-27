this is my work through of this [course](https://www.cs.cornell.edu/courses/cs6120/2020fa/). 
the programs written are mostly an academic exercise for me to learn more about how to think and reason about programs.
bril functions can be represented as json like:
```yaml
{"name": "<string>", "instrs": [<Instruction>, ...], "args": [<Argument>, ...], "type": <Type>}
```
for more [documentation](https://capra.cs.cornell.edu/bril/lang/syntax.html) on bril's json representation

### cfg 
contains a program that parses the json representation of bril programs and creates a control flow graph. returning a DOT representation of the input program

*make_labeled_blocks* chunks a program into basic blocks and assigns an label to each basic block, it uses the label for basic blocks if it comes with one

*make_cfg* creates a graph representing the control flow graph of a program

*print_graphviz* spits out the DOT representation of the cfg


### dce
contains some code to perform simple dead code elimination. returning a semantically equivalent bril json program with less dead code.
and example program of what what this does may look like:
```python3
a = 1
a = 2
b = 3
c = True
if c:
  a -= 1
d = 4
print(a+b)
```
transforms into the following equivalent program
```python3
a = 2
b = 3
c = True
if c:
  a -= 1
print(a+b)
```

*remove_reassigned_variables* checks within a basic block to remove any instructions where variables are reassigned

*remove_dead_code* performs a dead code elimination across the entire function, removing any unused code and iterating till convergence

### lvn
contains a program that performs value number within basic blocks (local value numbering). the idea is to disentangle variables from it's value. 
an example of a program that this technique could work on might be
```python3
a = 1
b = 1
c = a + b
b = 2
d = a + b
```
can be transformed into an semantically equivalent program
```python3
a = 1
b = a
c = a + a
b = 2
d = a + b
``` 
by associating a value number to each value and giving that value assigning it a variable, 
we can replace all instances where the redundant variables are used with the the variable associated with the value number. 
this is also dependent on the order of assignments, because reassignments can influence the values.

*local_ssa* performs static single assignment within a basic block, giving each assignment instruction a unique variable name

*lvn* performs local value numbering
