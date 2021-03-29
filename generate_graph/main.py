'''
Main module
'''

# Importing the parser library
import vmParser 

import os

if __name__ == '__main__':

    # Relative path 
    relativePath = '/../test_cases/vm_files/c6288.vm'

    # Absolute file path
    filepath = os.getcwd() + relativePath
    print(filepath)

    circuit = vmParser.Parser(filepath)

    circuit.Parse()
    circuit.graph.setRandomInputs()
    [circuit.graph.printPrimeIos(True)]
    [circuit.graph.printCfgBlcks(True)]
    circuit.graph.simulate()
    print(20*'*')
    [circuit.graph.printPrimeIos(True)]
    [circuit.graph.printCfgBlcks(True)] 
    
