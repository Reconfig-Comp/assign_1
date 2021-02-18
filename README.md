# assign_1
 
### Objective
 To model the graph for the given any combinational input circuit and simulating it.
#### Authors
| Roll No. | Name |
| --- | --- |
| EDM18B037 | Mayank Navneet Mehta |
| EDM18B054 | Vishva Nilesh Bhate |

#### Directory Details
- `test_cases`: contains `.v` and `.vm` files in their respective folders. `.vm` files are given as input to the main program.
- `generate_graph`: python package containing source code.
- `multimedia`: contains images shown in this file

## Our approach to the problem
We have described a class called `VerilogGraph`. This class describes a graph that has two types nodes:
1. Primary I/O node
2. Configuration block node

At implementation level, each node is an entry in a dictionary `dGrph` (member variable of class `VerilogGraph`). The following image describes the node struture in a more elaborated manner:

![verilog_graph](./multimedia/verilog_graph.png)

### Example
![example_graph](./multimedia/example_graph.png)
- Each block - circle and rectangle represent a node.
- The label to each block is the string stored as key in the dictionary.
- The values written within the blocks are stored as value(s) for each key.
- During parsing, the [1|0] are stored as `None` type.
- During simulation, the [1|0] for the input are given by the user, and the simulation algorithm runs till the time every `None` type in the graph is converted into 1 or 0. 

### Simulation algorithm