"""
Utility module providing the graph data structure, designed for simulating Verilog netlists.
The member functions aid in building, modifying, and simulating the graph.
"""

class VerilogGraph:
    """
        A class to describe a graph for Verilog netlists and allied functionalities

        Attributes
        ----------
        dGrph : dictionary
            Dictionary storing the graph. Two types of nodes:
            - prime_io node : 
                {'primeIo_id': 'io_type', 1|0}
            - cfg_blck node : 
                {'cfgBlck_id': [('ip0', 'ip1', 'ip3'), ('op', 1|0), 'cfg_string']}

        Methods
        -------
            Public:
                * addPrimeIo(io_type, io_id)
                * addCfgBlck(inputs, output, config)
                * listPrimeIos()
                * listCfgBlcks()
                * printPrimeIos()
                * printCfgBlcks()
            Private:
                * __init__()
                * __convertToBinaryStr(hex_str)
    """

    def __init__(self):
        """
            Constructor

            Instantiates an empty dictionary.
        """
        self.dGrph = {}
    
    def __convertToBinaryStr(self, hex_str):
        """
            Converts a hexadecimal string of n length to binary string of 4*n length

            Parameters
            ----------
            hex_str : str
                Hexadecimal string. Eg: '1ab' or '1AB'

            Returns
            -------
            Binary string of length 4*n. Eg: '000110101011'
        """
        bi_str = bin(int(hex_str, 16))[2:]
        if len(hex_str) == 1:
            return bi_str
        else:
            return (4 - len(bi_str)%4)*'0' + bi_str

    def addPrimeIo(self, io_id, io_type):
        """
            Adds a node of type prime_io to the graph.

            Parameters
            ----------
            io_id : str
                Identifier for the prime_io node.
            io_type : char
                Should be either 'i' (for input) or 'o' (for output)
        """
        # Eliminating basic outlier conditions
        if(io_type not in ['i', 'o']):
            print('Invalid io_type. No node added.')
            return
        if io_id in self.dGrph:
            print('io_id already exists. No node added.')
            return
        
        self.dGrph[io_id] = [io_type, None]

    def addCfgBlck(self, cfg_id, inputs, output, config):
        """
            Adds a node of type cfg_blck to the graph.


            Parameters
            ----------
            cfg_id : str
                Identifier for the prime_io node.
            inputs : tuple
                n-sized tuple of string identifiers representing input
                to the cfg_blck.
            output : str
                String identifier for the output.
            config : str
                String of length {if n>2: 2**(n-2); else 1} representing configuration in hexadecimal
                of the cfg_blck.
            

            Example usage
            -------------
            addCfgBlck('blck1', {'ip1', 'ip2', 'ip3'}, 'out_1', '1c')
        """
        # Eliminating basic outlier conditions
        if (len(inputs) <= 2 and len(config) != 1) or (len(config) != 2**(len(inputs) - 2)):
            print('Configuration string and number of inputs do not match. No node added.')
            return
        if cfg_id in self.dGrph:
            print('cfg_id already exists. No node added.')
            return
        
        self.dGrph[cfg_id] = [inputs, (output, None), self.__convertToBinaryStr(config)]

    def listPrimeIos(self, showBitValue = False):
        """
            Parameters
            ----------
            showBitValue : boolean (default: False)
                If set True, also returns bit value (0 | 1) for each of the node.
            Returns
            -------
            default: List of tuples in format (prime_io-node-IDs, io_type).
            if showBitValue is True: List of tuples in format (prime_io-node-IDs, io_type, [1 | 0]).
        """
        lst = []
        if showBitValue:
            for key in self.dGrph:
                if len(self.dGrph[key]) == 2:
                    lst.append((key, self.dGrph[key][0], self.dGrph[key][1]))    
        else:
            for key in self.dGrph:
                if len(self.dGrph[key]) == 2:
                    lst.append((key, self.dGrph[key][0]))
        return lst

    def printPrimeIos(self, showBitValue = False):
        """
            Prints the list of prime_io nodes in the graph.

            Parameters
            ----------
            showBitValue : boolean (default: False)
                If set True, also prints bit value of each node.
        """
        prime_ios = self.listPrimeIos(showBitValue = showBitValue)
        if showBitValue:
            print('Node ID --- IO Type --- BitValue')
            for node in prime_ios:
                print(node[0], ' --- ', node[1], ' --- ', node[2])
        else:
            print('Node ID ---- IO Type')
            for node in prime_ios:
                print(node[0], '----', node[1])

    def listCfgBlcks(self, showBitValue = False):
        """
            Parameters
            ----------
            showBitValue : boolean (default: False)
                If set True, also returns bit value of the output for each of the node.
            Returns
            -------
            default: List of tuples in format 
                (cfg_blck-node-IDs, cfg-string, tuple-of-ips, (output_id)).
            if showBitValue is True: List of tuples in format
                (cfg_blck-node-IDs, cfg-string, tuple-of-ips, (output_id, [1 | 0])).
        """
        lst = []
        if showBitValue:
            for key in self.dGrph:
                if len(self.dGrph[key]) != 2:
                    lst.append((key, self.dGrph[key][2], self.dGrph[key][0], self.dGrph[key][1]))    
        else:
            for key in self.dGrph:
                if len(self.dGrph[key]) != 2:
                    lst.append((key, self.dGrph[key][2], self.dGrph[key][0], (self.dGrph[key][1][0])))
        return lst

    def printCfgBlcks(self, showBitValue = False):
        """
            Prints the list of cfg_blcks nodes in the graph.

            Parameters
            ----------
            showBitValue : boolean (default: False)
                If set True, also prints bit value of the output for each of the node.
        """
        cfg_blcks = self.listCfgBlcks(showBitValue = showBitValue)
        if showBitValue:
            print('Node ID - Config - Inputs - Output - OutputValue')
            for node in cfg_blcks:
                print(node[0], ' - ', node[1], ' - ', node[2], ' - ', node[3][0], ' - ', node[3][1])
        else:
            print('Node ID - Config - Inputs - Output')
            for node in cfg_blcks:
                print(node[0], ' - ', node[1], ' - ', node[2], ' - ', node[3][0])

# for unit testing this module
if __name__ == '__main__':
    vg = VerilogGraph()
    vg.addPrimeIo('ip1', 'o')
    vg.addPrimeIo('ip2', 'i')
    
    vg.addCfgBlck('cfg1', ('ip1', 'ip2'), 'out1', 'b')

    vg.printPrimeIos(True)
    print(10*'-')
    vg.printCfgBlcks(True)
    pass