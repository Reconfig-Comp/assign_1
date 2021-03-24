# assign_1
 
### Objective
1. **Assignment 1:** Parse the VM file and generate a biparted graph.
2. **Assignment 2:** Simulate graph
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
We have described a class called `VerilogGraph`. This class describes a graph that has 4 types nodes:
1. Primary I/O node
2. Configuration block node
3. ARI block node
4. Tribuff node

At implementation level, each node is an entry in a dictionary `dGrph` (member variable of class `VerilogGraph`). More information about the class [here](./docs/on_VerilogGraph.md).