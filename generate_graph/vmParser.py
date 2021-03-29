"""
Parser module can be used to parse any .vm file and store the information in the graph data structure
"""

# os module to obtain current working directory
import os

# Importing RegEx package to perform search operations in string
import re

# Importing graph_util package
import graph_util as gu

                
class Parser:
    '''
    This class has all the functions required to parse the given .vm file

    Public function(s):
        1. Parse(): Parses the file line by line

    Private function(s):
        1. __init__(): Initializes class with required variables
        2. __mapIO(): Maps the wire to their corresponding primary input/output (Buffer)
    '''
    
    def __init__(self, path):
        '''
        Constructor
        Inputs:
            1. path: Absolute path of file 

        Job:
            1. Reads the file from the file path specified.
            2. Creates a few variables
            2. Creates VerilogGraph object for creating the graph data structure
        '''
        
        # The entire file path
        self.filePath = path

        # Reading the file
        with open(self.filePath, "r") as self.vmFile:
            self.fData = self.vmFile.readlines()

        self.lines = len(self.fData)  # Number of lines in the file
        self.lineNo = 0          # Keeps a track of lineNo being read

        self.iobuf = {}          # Input buffer mapping (Primary Input : wire)
        self.CFGio = []          # Stores the configuration module details temporarily
        self.ARI1io = []          # Stores the ARI1 module details temporarily
        self.graph = gu.VerilogGraph() # VerilogGraph object


    def __mapIO(self, iobuf, cfgIO):
        '''
        Maps the wire to their corresponding primary input/output
        Inputs:
            1. iobuf: This is a dictionary which has key : value as wire : primary input/output
            2. cfgIO: This is the configuration module whose input/output needs to be mapped to primary input/output
        '''
        for key, value in self.iobuf.items():
            for j in range(len(cfgIO)):
                if key == cfgIO[j]:
                    cfgIO[j] = value


    def Parse(self):
        '''
        Parses the file line by line
        '''
        while 1:

            # if the end of the file is reached, break
            if self.lineNo >= self.lines:
                break

            # Splitting the current line into separate characters
            self.lineData = self.fData[self.lineNo].split()

            '''
            If the length of current line string is 0 or the first word in the line is '//'
            or 'endmodule' or '`timescale' or 'wire' then go to next line
            '''
            if (len(self.lineData) == 0 or self.lineData[0] == '//' or
                self.lineData[0] == 'endmodule' or self.lineData[0] == '`timescale'):
                self.lineNo += 1
                continue

            #if the first word of the line is input, then store the name of primary input variable in input list
            elif (self.lineData[0] == 'input' or (self.lineData[0] == 'wire' and 
                 (self.lineData[1] == 'GND' or self.lineData[1] == 'VCC'))):
                self.graph.addPrimeIo(self.lineData[1], 'i')

            # if the first word of the line is output, then store the name of primary output variable in output list   
            elif self.lineData[0] == 'output':
                self.graph.addPrimeIo(self.lineData[1], 'o')

            # if the first word of the line is INBUF, then store the name of wire and primary input as a pair in inbuf list
            elif self.lineData[0] == 'INBUF':
                # Reading the input and output of buffer from next 2 lines
                self.lineNo += 2
                self.lineData = re.split('[()]', self.fData[self.lineNo-1] + self.fData[self.lineNo])
                self.iobuf.update({self.lineData[1]: self.lineData[3]})

            # if the first word of the line is OUTBUF, then store the name of wire and primary output as a pair in outbuf list
            elif self.lineData[0] == 'OUTBUF':
                # Reading the input and output of buffer from next 2 lines
                self.lineNo += 2
                self.lineData = re.split('[()]', self.fData[self.lineNo-1] + self.fData[self.lineNo])
                self.iobuf.update({self.lineData[3]: self.lineData[1]})

            # if the first word of the line starts with 'CFG', then this is the configuration block used in the program
            elif re.match('^C+F+G', self.lineData[0]):
                self.module = self.lineData[1]     # Storing the module name
                self.lineNo += 1        
                while self.fData[self.lineNo] != ');\n':    # Until ');' keep reading the next line for inputs & outputs
                    self.lineData = re.split('[()]', self.fData[self.lineNo]) 
                    self.CFGio.append(self.lineData[1])
                    self.lineNo += 1
                    
                self.lineNo += 1
                self.lineData = re.split('[=h;\n]', self.fData[self.lineNo])
                self.__mapIO(self.iobuf, self.CFGio)
                #print(self.module, self.lineData[2])
                self.graph.addCfgBlck(self.module, [self.CFGio[i] for i in range(len(self.CFGio)-1)], self.CFGio[len(self.CFGio)-1], self.lineData[2])
                self.CFGio = []

            # if the first word of the line starts with 'ARI1', then this is the ARI1 module used in the program
            elif self.lineData[0] == 'ARI1':
                self.module = self.lineData[1]      # Storing the module name
                self.lineNo += 1        
                while self.fData[self.lineNo] != ');\n':    # Until ');' keep reading the next line for inputs & outputs
                    self.lineData = re.split('[()]', self.fData[self.lineNo]) 
                    self.ARI1io.append(self.lineData[1])
                    self.lineNo += 1

                self.lineNo += 1
                self.lineData = re.split('[=h;\n]', self.fData[self.lineNo])
                self.__mapIO(self.iobuf, self.ARI1io)
                self.graph.addAriBlck(self.module, [self.ARI1io[i] for i in range(3,8)], [self.ARI1io[i] for i in range(3)], self.lineData[2])
                self.ARI1io = []
                
            self.lineNo += 1 # Incrementing the lineNo to read next line


'''
Testing the class
'''

if __name__ == '__main__':
    
    path = os.getcwd() + '/../test_cases/vm_files/c2670.vm'
    c17 = Parser(path)
    c17.Parse()
    c17.graph.printPrimeIos()

    

