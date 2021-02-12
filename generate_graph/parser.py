"""
Parser module: Can be used to parse any .vm file and store the information in a dictionary
which can be utilised for generating a graph.

Last updated: 11th February 2021
"""


# Creating a class for dictionary
class my_dictionary(dict):  
  
    # __init__ function  
    def __init__(self):  
        self = dict()  
          
    # Function to add key:value  
    def add(self, key, value):  
        self[key] = value


# Split line into words
def splitline(line):
    fData[lineNo] = fData[lineNo].replace(',', ' , ')
    fData[lineNo] = fData[lineNo].replace(';', ' ; ')
    fData[lineNo] = fData[lineNo].replace('(', ' ( ')
    fData[lineNo] = fData[lineNo].replace(')', ' ) ')
    lineData = fData[lineNo].split()
    return lineData


# Finding a character in a string
def findw(word, ch):
    for a in word:
        if a == ch:
            return True
    return False

        
# Taking file path as input from the user
filePath = input("Enter the path of file you wish to parse: ")
#filePath = '../test_cases/vm_files/c1355.vm'


# Reading the file via the file path specified
with open(filePath, "r") as vmFile:
    fData = vmFile.readlines()

lines = len(fData) # Number of lines in the file
lineNo = 0  # Keeps a track of lineNo being read
graph = my_dictionary() # Stores the graph info in dictionary
elt = []
key = 0


while 1:

    if lineNo == lines:
        break
    
    lineData = splitline(fData[lineNo])

    if len(lineData) == 0 or lineData[0] == '//' or lineData[0] == 'endmodule' or lineData[0] == '`timescale' or lineData[0] == 'input' or lineData[0] == 'output' or lineData[0] == 'wire':
        lineNo += 1
        continue
    elif lineData[0] == 'INBUF' or lineData[0] == 'OUTBUF':
        for a in lineData:
            if a != 'INBUF' and a != 'OUTBUF' and a != '(':
                key = a
                
        for i in range(2):
            lineNo += 1
            lineData = splitline(fData[lineNo])
            for a in lineData:
                if a != '.Y' and a != '(' and a != ')' and a != '.PAD' and a != ',' and a != '.D':
                    elt.append(a)
                    
        graph.add(key, elt)
        elt = []
    elif findw(lineData[0], 'C') and findw(lineData[0], 'F') and findw(lineData[0], 'G'):
        key = lineData[1]
                
        while findw(lineData, ';') == False:
            lineNo += 1
            lineData = splitline(fData[lineNo])
            for a in lineData:
                if a != '.Y' and a != '(' and a != ')' and a != '.A' and a != ',' and a != '.B' and a != '.C' and a != '.D' and a != ';':
                    elt.append(a)
        graph.add(key, elt)
        elt = []
    lineNo += 1
    
print(graph)

    

