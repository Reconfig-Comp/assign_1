"""
Parser module: Can be used to parse any .vm file and store the information in a dictionary
which can be utilised for generating a graph.

Last updated: 14th February 2021
"""
# os module to obtain current working directory
import os

# Importing RegEx package to perform search operations in string
import re

# Importing graph_util package
import graph_util as gu


# Taking file path as input from the user
#filePath = input("Enter the path of file you wish to parse: ")
cwd = os.getcwd()
filePath = cwd + '/test_cases/vm_files/c17.vm'


# Reading the file via the file path specified
with open(filePath, "r") as vmFile:
    fData = vmFile.readlines()


lines = len(fData)                      # Number of lines in the file
lineNo = 0                              # Keeps a track of lineNo being read
ioData = {'input': [], 'output': []}    # Primary input & output

inbuf = {}    # Input buffer mapping (Primary Input : wire)
outbuf = {}   # Output buffer mapping (Primary Output : wire)
graph = gu.DirectedGraph() # Graph

while 1:

    # once end of the file is reached, break
    if lineNo >= lines:
        break

    # Splitting the current line into separate characters
    lineData = fData[lineNo].split()

    # If the length of current line string is 0 or the first word in the line is '//'
    # or 'endmodule' or '`timescale' or 'wire' then go to next line
    if len(lineData) == 0 or lineData[0] == '//' or lineData[0] == 'endmodule' or lineData[0] == '`timescale' or lineData[0] == 'wire':
        lineNo += 1
        continue

    # if the first word of the line is input, then store the name of primary input variable in input list
    elif lineData[0] == 'input':
        ioData["input"].append(lineData[1])

    # if the first word of the line is output, then store the name of primary output variable in output list   
    elif lineData[0] == 'output':
        ioData["output"].append(lineData[1])

    # if the first word of the line is INBUF, then store the name of wire and primary input as a pair in inbuf list
    elif lineData[0] == 'INBUF':
        # Reading the input and output of buffer from next 2 lines
        lineNo += 2
        lineData = re.split('[()]', fData[lineNo-1] + fData[lineNo])
        inbuf.update({lineData[3]: lineData[1]})

    # if the first word of the line is OUTBUF, then store the name of wire and primary output as a pair in outbuf list
    elif lineData[0] == 'OUTBUF':
        # Reading the input and output of buffer from next 2 lines
        lineNo += 2
        lineData = re.split('[()]', fData[lineNo-1] + fData[lineNo])
        outbuf.update({lineData[1]: lineData[3]})

    # if the first word of the line starts with 'CFG', then this is the module used in the program
    elif re.match('^C+F+G', lineData[0]):
        module = lineData[1]     # Storing the module name
        graph.addVertex(module)  # Adding module to graph as a vertex
        lineNo += 1        
        while fData[lineNo] != ');\n':    # Until ');' keep reading the next line for inputs & outputs
            lineData = re.split('[()]', fData[lineNo]) 
            graph.addEdge([module, lineData[1]])  
            lineNo += 1
            
    lineNo += 1