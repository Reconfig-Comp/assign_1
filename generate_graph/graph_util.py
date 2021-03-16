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
            Dictionary storing the graph. Three types of nodes:
            - prime_io node : 
                {'primeIo_id': 'io_type', 1|0}
            - cfg_blck node : 
                {'cfgBlck_id': [('ip0', 'ip1', 'ip3'), ['op', 1|0], 'cfg_string']}
            - ari_blck node:
                {'ariBlck_id': [('A', 'B', 'C', 'D', 'FCI'), [['Y', 1|0], ['S', 1|0], ['FCO', 1|0]], 'cfg_string']}
        __prime_ip : list
            list of primary inputs in the VerilogGraph. Private attribute used to
            better process the blcks
        __prime_op : list
            list of primary outputs in the VerilogGraph. Private attribute used to
            better process blcks

        Methods
        -------
            Public:
                Graph creation methods
                    * addPrimeIo(io_type, io_id)
                    * addCfgBlck(inputs, output, config)
                    * addAriBlck(inputs, outputs, config)
                    * listPrimeIos()
                    * listCfgBlcks()
                    * listAriBlcks()
                    * printPrimeIos()
                    * printCfgBlcks()
                    * printAriBlcks()
                Graph simulation methods
                    * setIpValue()
                    * simulate(inputs, bit_str)

            Private:
                    * __init__()
                Graph creation methods
                    * __convertToBinaryStr(hex_str)
                Graph simulation methods
                    * __charToBool(char)
                    * __boolToChar(boolean)
                    * __simSetup()
                    * __processCgfBlck()
                    * __processAriBlck()
                    * __processBlcks()

    """

    def __init__(self):
        """
            Constructor

            Instantiates an empty dictionary.
        """
        self.dGrph = {}
        self.__prime_ip = []
        self.__prime_op = []
    
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
        if len(hex_str) == 1 or len(bi_str)%4 == 0:
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

        if io_type == 'o':
            self.__prime_op.append(io_id) 

    def addCfgBlck(self, cfg_id, inputs, output, config):
        """
            Adds a node of type cfg_blck to the graph.
            Note: For faster simulation, the 'config' is stored in the reverse format
            of what is given as input. But while using function: printCfgBlcks(), 
            the actual 'config' is shown.


            Parameters
            ----------
            cfg_id : str
                Identifier for the cfgBlck_io node.
            inputs : list/tuple
                n-sized list/tuple of string identifiers representing input
                to the cfg_blck.
            output : str
                String identifier for the output.
            config : str
                String of length {if n>2: 2**(n-2); else 1} representing configuration in hexadecimal
                of the cfg_blck.
            

            Example usage
            -------------
            addCfgBlck('blck1', ['ip1', 'ip2', 'ip3'], 'out_1', '1c')
        """
        # Eliminating basic outlier conditions
        if (len(inputs) == 1 and len(config) == 1):
            self.dGrph[cfg_id] = [tuple(inputs), [output, None], self.__convertToBinaryStr(config)[::-1]]
            return
        if (len(inputs) <= 2 and len(config) != 1) or (len(config) != 2**(len(inputs) - 2)):
            print('Configuration string and number of inputs do not match. No node added.')
            return
        if cfg_id in self.dGrph:
            print('cfg_id already exists. No node added.')
            return
        
        self.dGrph[cfg_id] = [tuple(inputs), [output, None], self.__convertToBinaryStr(config)[::-1]]
    
    def addAriBlck(self, ari_id, inputs, outputs, config):
        """
            Adds a node of type ari_blck to the graph.
            Note: For faster simulation, the 'config' is stored in the reverse format
            of what is given as input. But while using function: printAriBlcks(), 
            the actual 'config' is shown.


            Parameters
            ----------
            ari_id : str
                Identifier for the ari_blck node.
            inputs : list/tuple
                5-sized list/tuple of string identifiers representing inputs
                to the ari_blck in the sequence: ['A', 'B', 'C', 'D', 'FCI'].
            outputs : set
                3-sized set of string identifiers representing outputs
                from the ari_blck in the sequence: ['Y', 'S', 'FCO'].
            config : str
                String of length 5 representing configuration in hexadecimal
                of the ari_blck.
            

            Example usage
            -------------
            addAriBlck('ariBlck1', ['ipA', 'ipB', 'ipC', 'ipD', 'ipFci'], ['opY', 'opS', 'opFco'], '01d1c')
        """
        # Eliminating basic outlier conditions
        if(len(inputs) != 5):
            print('Invalid number of inputs. No node added.')
            return
        if(len(outputs) != 3):
            print('Invalid number of outputs. No node added.')
            return
        if(len(config) != 5):
            print('Invalid length of configuration string. No node added.')
            return

        self.dGrph[ari_id] = [tuple(inputs), [[outputs[0], None], [outputs[1], None], [outputs[2], None]], self.__convertToBinaryStr(config)[::-1]]

    def listPrimeIos(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value (0 | 1) for each of the node.
            Returns
            -------
            default: List of tuples in format (prime_io-node-IDs, io_type).
            if show_bit_value is True: List of tuples in format (prime_io-node-IDs, io_type, [1 | 0]).
        """
        lst = []
        if show_bit_value:
            for key in self.dGrph:
                if len(self.dGrph[key]) == 2:
                    lst.append((key, self.dGrph[key][0], self.dGrph[key][1]))    
        else:
            for key in self.dGrph:
                if len(self.dGrph[key]) == 2:
                    lst.append((key, self.dGrph[key][0]))
        return lst

    def printPrimeIos(self, show_bit_value = False):
        """
            Prints the list of prime_io nodes in the graph.

            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also prints bit value of each node.
        """
        prime_ios = self.listPrimeIos(show_bit_value = show_bit_value)
        if show_bit_value:
            print('Node ID --- IO Type --- BitValue')
            for node in prime_ios:
                print(node[0], ' --- ', node[1], ' --- ', node[2])
        else:
            print('Node ID ---- IO Type')
            for node in prime_ios:
                print(node[0], '----', node[1])

    def listCfgBlcks(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value of the output for each of the node.
            Returns
            -------
            default: List of tuples in format 
                (cfg_blck-node-IDs, cfg-string, tuple-of-ips, output_id).
            if show_bit_value is True: List of tuples in format
                (cfg_blck-node-IDs, cfg-string, tuple-of-ips, (output_id, [1 | 0])).
        """
        lst = []
        if show_bit_value:
            for key in self.dGrph:
                # eliminating prime_ios node
                if len(self.dGrph[key]) != 2:
                    # eliminating ari_blck node 
                    if len(self.dGrph[key][1]) == 2:
                        lst.append((key, self.dGrph[key][2], self.dGrph[key][0], self.dGrph[key][1])) 
        else:
            for key in self.dGrph:
                if len(self.dGrph[key]) != 2:
                    if len(self.dGrph[key][1]) == 2:
                        lst.append((key, self.dGrph[key][2], self.dGrph[key][0], (self.dGrph[key][1][0])))
        return lst

    def printCfgBlcks(self, show_bit_value = False):
        """
            Prints the list of cfg_blcks nodes in the graph.
            Note: For faster simulation, the 'config' is stored in the reverse format
            of what is given as input. But while using function: printCfgBlcks(), 
            the actual 'config' is shown.

            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also prints bit value of the output for each of the node.
        """
        cfg_blcks = self.listCfgBlcks(show_bit_value = show_bit_value)
        if show_bit_value:
            print('Node ID - Config - Inputs - Output - OutputValue')
            for node in cfg_blcks:
                print(node[0], ' - ', node[1][::-1], ' - ', node[2], ' - ', node[3][0], ' - ', node[3][1])
        else:
            print('Node ID - Config - Inputs - Output')
            for node in cfg_blcks:
                print(node[0], ' - ', node[1][::-1], ' - ', node[2], ' - ', node[3][0])

    def listAriBlcks(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value of the output for each of the node.

            Returns
            -------
            default: List of tuples in format 
                (ari_blck-node-IDs, cfg-string, tuple-of-ips, list-of-ops).
            if show_bit_value is True: List of tuples in format
                (ari_blck-node-IDs, cfg-string, tuple-of-ips, [[op1, [1 | 0]], ...]).
        """
        lst = []
        if show_bit_value:
            for key in self.dGrph:
                # eliminating prime_ios node
                if len(self.dGrph[key]) != 2:
                    # eliminating cfg_blck node 
                    if len(self.dGrph[key][1]) == 3:
                        lst.append((key, self.dGrph[key][2], self.dGrph[key][0], self.dGrph[key][1]))    
        else:
            for key in self.dGrph:
                if len(self.dGrph[key]) != 2:
                    if len(self.dGrph[key][1]) == 3:
                        lst.append((key, self.dGrph[key][2], self.dGrph[key][0], [op for op in self.dGrph[key][1]]))
        return lst

    def printAriBlcks(self, show_bit_value = False):
        """
            Prints the list of ari_blcks nodes in the graph.
            Note: For faster simulation, the 'config' is stored in the reverse format
            of what is given as input. But while using function: printAriBlcks(), 
            the actual 'config' is shown.

            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also prints bit value of the output for each of the node.
        """
        ari_blcks = self.listAriBlcks(show_bit_value = show_bit_value)
        if show_bit_value:
            print('Node ID - Config - Inputs - Outputs - OutputValues')
            for node in ari_blcks:
                print(node[0], ' - ', node[1][::-1], ' - ', node[2], ' - ', [op[0] for op in node[3]], ' - ', [op[1] for op in node[3]])
        else:
            print('Node ID - Config - Inputs - Outputs')
            for node in ari_blcks:
                print(node[0], ' - ', node[1][::-1], ' - ', node[2], ' - ', [op[0] for op in node[3]])

    def listIntermediateOps(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value of the intermediate output.

            Returns
            -------
            default: List of tuples in format 
                (inter_op, blck_of_origin).
            if show_bit_value is True: List of tuples in format
                (inter_op, blck_of_origin, [1|0]).
        """
        lst = []
        prime_ios = [io[0] for io in self.listPrimeIos() if io[1] == 'i']

        # obtaining intermediate outputs of each configuration block
        cfg_blcks = self.listCfgBlcks(show_bit_value)
        for cfg in cfg_blcks:
            if cfg[3][0] not in prime_ios:
                if show_bit_value:
                    lst.append((cfg[3][0], cfg[0], cfg[3][1]))
                else:
                    lst.append((cfg[3][0], cfg[0]))
        
        # obtaining intermediate outputs of each ari block
        ari_blcks = self.listAriBlcks(show_bit_value)
        for ari in ari_blcks:
            for ari_op in ari[3]:
                if ari_op[0] not in prime_ios:
                    if show_bit_value:
                        lst.append((ari_op[0], ari[0], ari_op[1]))
                    else:
                        lst.append((ari_op[0], ari[0]))
        
        return lst

    def setIpValue(self, ip_id, value):
        """
            Sets the input value of the 'ip_id' as given 'value'.
            Note: if value >= 1, then it is considered as 1;
                  else it is considered as 0.

            Parameters
            ----------
            ip_id : str
                Input node identifier
            value : int [1|0]
                Value of the node
        """ 
        v = value
        # Eliminating basic outliers
        if ip_id not in self.dGrph:
            print(ip_id, ' does not exist in graph. Value not set.')
            return
        if ip_id in self.dGrph:
            if self.dGrph[ip_id][0] != 'i':
                print('Cannot set value of any other node. Value not set.')
                return
        
        if value >= 1:
            v = 1
        else:
            v = 0
        
        self.dGrph[ip_id][1] = v
    
    def __charToBool(self, char):
        """
            Converts '1' to True and '0' to False

            Parameters
            ----------
            char : str
                Either '1' or '0'
            
            Returns
            -------
            True, if char == '1' ; False, if char == '0'
        """

        if char == '1':
            return True
        elif char == '0':
            return False
    
    def __boolToChar(self, boolean):
        """
            Converts True to '1' and False to '0'

            Parameters
            ----------
            boolean : bool
            
            Returns
            -------
            '1', if boolean == True ; '0', if boolean == False
        """

        if boolean:
            return '1'
        else:
            return '0'

    def __simSetup(self):
        """
            Performs pre-requisites before simulation.
        """
        self.__prime_ip = [(io[0], '$', io[2]) for io in self.listPrimeIos(True) if io[1] == 'i']

        # setting primary output values to None
        for prime_op in self.__prime_op:
            self.dGrph[prime_op][1] = None

        # setting cfg_blck output values to None
        cfg_blck_ids = [blck[0] for blck in self.listCfgBlcks()]
        for cfg_id in cfg_blck_ids:
            self.dGrph[cfg_id][1][1] = None
        
        # setting ari_blck output values to None
        ari_blck_ids = [blck[0] for blck in self.listAriBlcks()]
        for ari_id in ari_blck_ids:
            self.dGrph[ari_id][1][0][1] =  None
            self.dGrph[ari_id][1][1][1] =  None
            self.dGrph[ari_id][1][2][1] =  None

    def __processCfgBlck(self, blck_id, ip_str):
        """
            Processes the CFG blocks and sets the values of each output node.
            Note: This function should only be called from __processBlcks()

            Parameters
            ----------
            blck_id : str
                Identifier of the block
            ip_str : str
                String of input values
        """
        self.dGrph[blck_id][1][1] = self.dGrph[blck_id][2][int(ip_str, 2)]

        # update primary output if current block's output is primary output
        if self.dGrph[blck_id][1][0] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][1][0]][1] = self.dGrph[blck_id][1][1]

    def __processAriBlck(self, blck_id, ip_str):
        """
            Processes the ARI blocks and sets the values of each output node.
            Note: This function should only be called from __processBlcks()

            Parameters
            ----------
            blck_id : str
                Identifier of the block
            ip_str : str
                String of input values
        """
        # temp input variables to the block
        A = ip_str[0]
        B = ip_str[1]
        C = ip_str[2]
        D = ip_str[3]
        FCI = self.__charToBool(ip_str[4])
        INIT = self.dGrph[blck_id][2]   # config bit string
        INIT16 = self.__charToBool(INIT[16])
        INIT17 = self.__charToBool(INIT[17])

        # intermediataries for calculating output
        F0 = self.__charToBool(INIT[int('0' + B + C + D, 2)])
        F1 = self.__charToBool(INIT[int('1' + B + C + D, 2)])
        P = self.__charToBool(INIT[19]) | (~self.__charToBool(INIT[19]) & self.__charToBool(INIT[18]))
        G = (F0 & INIT16 & INIT17) | (INIT17 & ~INIT16) | (F1 & INIT16 & INIT17)

        # outputs
        Y = self.__charToBool(INIT[int(A + B + C + D, 2)])
        S = Y ^ FCI
        FCO = (~P & G) | (P & FCI)
        self.dGrph[blck_id][1][0][1] = self.__boolToChar(Y)
        self.dGrph[blck_id][1][1][1] = self.__boolToChar(S)
        self.dGrph[blck_id][1][2][1] = self.__boolToChar(FCO)

        # update primary output if current block's output is primary output
        if self.dGrph[blck_id][1][0][0] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][1][0][0]][1] = self.dGrph[blck_id][1][0][1]
        
        if self.dGrph[blck_id][1][1][0] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][1][1][0]][1] = self.dGrph[blck_id][1][1][1]
        
        if self.dGrph[blck_id][1][2][0] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][1][2][0]][1] = self.dGrph[blck_id][1][2][1]

        pass  

    def __processBlcks(self, blck_id):
        """
            Processes the blocks and sets the values of each output node.

            Parameters
            ----------
            blck_id : str
                Identifier of the block
        """
        # Eliminating basic outliers
        if blck_id not in self.dGrph:
            print(blck_id, ' does not exist in the graph. Cannot process.')
            return
        
        # Constructing a string of inputs to a given block

        # Find the input and retrieve it's value
        # Tuple format: (io_id, io_source, io_value)
        # In io_source,'$' indicates prime_io, else it 
        # is replaced by the blck of origin.

        ip_str = ''     # string storing all inputs
        all_ios = self.__prime_ip + self.listIntermediateOps(True)
        abort_processing = False
        for ip in self.dGrph[blck_id][0]:    
            found = False
            for i in range(0, len(all_ios)):
                if ip == all_ios[i][0]:
                    found = True
                    if all_ios[i][2] is not None:
                        ip_str += str(all_ios[i][2])
                    else:
                        if all_ios[i][1] == '$':
                            print('Primary input: ', ip, ' is not entered. Aborting processing blcks...')
                            abort_processing = True
                        else:
                            print('Input: ', ip, ' is not entered. Processing blck: ', all_ios[i][1])
                            # process the blck to get input
                            if(self.__processBlcks(all_ios[i][1])):
                                ip_str += str(self.dGrph[all_ios[i][1]][1][1])
                            else:
                                print('Couldn\'t process blck: ', all_ios[i][1], '. Aborting processing blcks...')
                                abort_processing = True
                    break
            if not found:
                print('Could not find input: ', ip, ' for blck: ', blck_id, '. Aborting processing blcks...')
                abort_processing = True
            if abort_processing:
                return False

        # sanity check
        # print('For: ', blck_id, ' ip_str: ', ip_str)
        if len(ip_str) != len(self.dGrph[blck_id][0]):
            print('It\'s a bug! ip_str: ', ip_str)
            return False
    
        # Calculating output
        # Differentiating between types of blocks
        if len(self.dGrph[blck_id][1]) == 3:    # ari block
            self.__processAriBlck(blck_id, ip_str)
        elif len(self.dGrph[blck_id][1]) == 2:  # cfg block
            self.__processCfgBlck(blck_id, ip_str)
        
        return True

    def simulate(self, inputs = None, bit_str = None):
        """
            Simulates the hardware circuit described by the VerilogGraph.

            Parameters
            ----------
            inputs : List (default: None)
                List of primary input IDs.
            bit_str : str (default: None)
                String of 0s and 1s representing the primary 'inputs' set.
            Eg: To simulate circuit with primary inputs ip1, ip2, ip3 as 0, 1, 0 respectively, execute
            simulate(['ip1', 'ip2', 'ip3'], '010')
        """
        # Eliminating basic outlier conditions
        if (inputs is None and bit_str is not None) or (inputs is not None and bit_str is None):
            print('Please enter both inputs and bit_str. Exiting simulation...')
            return
        if inputs is not None and bit_str is not None:
            if len(inputs) != len(bit_str):
                print('inputs and bit_str not of same length. Exiting simulation...')
                return
            # setting primary inputs
            for i in range(0, len(inputs)):
                self.setIpValue(inputs[i], int(bit_str[i]))
            
        self.__simSetup()

        # iterating all cfg_blcks
        blck_ids = [blck[0] for blck in self.listCfgBlcks()]

        for cfg_id in blck_ids:
            if self.dGrph[cfg_id][1][1] == None:
                if(self.__processBlcks(cfg_id)):
                    print('Processed cfg_blck: ', cfg_id)
                else:
                    print('Some error in processing cfg_blck: ', cfg_id)
        
        # iterating all ari_blcks
        blck_ids = [blck[0] for blck in self.listAriBlcks()]

        for ari_id in blck_ids:
            # checking if one output is None because all outputs are set simultaneously
            if self.dGrph[ari_id][1][0][1] == None:
                if(self.__processBlcks(ari_id)):
                    print('Processed ari_blck: ', ari_id)
                else:
                    print('Some error in processing ari_blck: ', ari_id)

# for unit testing this module
if __name__ == '__main__':
    vg = VerilogGraph()
    # Creating graph
    # inputs
    vg.addPrimeIo('i_1', 'i')
    vg.addPrimeIo('i_2', 'i')
    vg.addPrimeIo('i_3', 'i')
    vg.addPrimeIo('i_4', 'i')
    vg.addPrimeIo('i_5', 'i')

    # outputs
    vg.addPrimeIo('o_1', 'o')
    vg.addPrimeIo('o_2', 'o')
    
    # connections to cfg blcks
    vg.addCfgBlck('cfg1', ('i_1', 'i_2', 'i_3'), 'cfg1_o', 'c2')
    vg.addCfgBlck('cfg2', ('i_4', 'cfg1_o', 'i_5'), 'cfg2_o', '57')

    vg.addAriBlck('ari1', ['i_1', 'cfg1_o', 'i_4', 'cfg1_o', 'cfg2_o'], ['ari1_y', 'ari1_s', 'o_2'], 'A5D21')
    vg.addAriBlck('ari2', ['i_2', 'cfg2_o', 'i_5', 'i_3', 'i_4'], ['ari2_y', 'o_1', 'ari2_fco'], 'EC9B5')

    # setting input values
    vg.setIpValue('i_1', 1)
    vg.setIpValue('i_2', 0)
    vg.setIpValue('i_3', 1)
    vg.setIpValue('i_4', 0)
    vg.setIpValue('i_5', 0)
    
    # simulation - test 1
    vg.simulate()

    # printing
    print('Simulation test 1')
    vg.printPrimeIos(True)
    print(10*'-')
    vg.printCfgBlcks(True)
    print(10*'-')
    vg.printAriBlcks(True)

    # simulation - test 2
    vg.simulate(['i_1', 'i_2', 'i_3', 'i_4', 'i_5'], '01010')

    # printing
    print('Simulation test 2')
    vg.printPrimeIos(True)
    print(10*'-')
    vg.printCfgBlcks(True)
    print(10*'-')
    vg.printAriBlcks(True)

    # simulation - test 3
    vg.simulate(['i_1', 'i_2', 'i_3', 'i_4', 'i_5'], '11010')

    # printing
    print('Simulation test 3')
    vg.printPrimeIos(True)
    print(10*'-')
    vg.printCfgBlcks(True)
    print(10*'-')
    vg.printAriBlcks(True)

    pass
