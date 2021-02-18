'''
Main module
'''

# Importing the parser library
import vmParser 

import os

if __name__ == '__main__':

    # Relative path 
    relativePath = '/test_cases/vm_files/c17.vm'

    # Absolute file path
    filepath = os.getcwd() + relativePath
    print(filepath)

    # Creating a Parser object named c17
    c1355 = vmParser.Parser(filepath)

    # Parsing c17.vm
    c1355.Parse()
    [c1355.graph.printCfgBlcks()]

    # simulate
    print('***Simulation test***')
    c17.graph.simulate(['N1', 'N2', 'N3', 'N6', 'N7'], '11010')
    print(10*'-')
    c17.graph.printPrimeIos(True)
    print(10*'-')
    c17.graph.printCfgBlcks(True)