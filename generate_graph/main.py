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

    # Creating a Parser object named c17
    c17 = vmParser.Parser(filepath)

    # Parsing c17.vm
    c17.Parse()

