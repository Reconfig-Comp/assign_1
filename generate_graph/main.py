'''
Main module
'''

# Importing the parser library
import vmParser 

import os

if __name__ == '__main__':

    # Relative path 
    relativePath = '/../test_cases/vm_files/c17.vm'

    # Absolute file path
    filepath = os.getcwd() + relativePath
    print(filepath)

    # Creating a Parser object named c17
    c1355 = vmParser.Parser(filepath)

    # Parsing c17.vm
    c1355.Parse()
    [c1355.graph.printCfgBlcks()]

