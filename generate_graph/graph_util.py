"""
Utility module providing the graph data structure, designed for simulating Verilog netlists.
The member functions aid in building, modifying, and simulating the graph.
"""
import random

class VerilogGraph:
    """
        A class to describe a graph for Verilog netlists and allied functionalities

        Attributes
        ----------
        dGrph : dictionary
            Dictionary storing the graph. Six types of nodes:
            - prime_io node : 
                {'primeIo_id': 'io_type', 1|0|Z}
            - cfg_blck node : 
                {'cfgBlck_id': [('ip0', 'ip1', 'ip3'), ['op', 1|0|Z], 'cfg_string']}
            - ari_blck node:
                {'ariBlck_id': [('A', 'B', 'C', 'D', 'FCI'), [['Y', 1|0|Z], ['S', 1|0|Z], ['FCO', 1|0|Z]], 'cfg_string']}
            - tribuf node:
                {'tribuf_id': [(input, ctrl), [ctrl], [output, 1|0|Z]] ([ctrl] is added to differentiate tribuf node from other nodes)
            - and_gate node:
                {'and_gate_id': [('ip0', 'ip1', 'ip3'), ['A', output, 1|0|Z]]
            - or_gate node:
                {'or_gate_id': [('ip0', 'ip1', 'ip3'), ['O', output, 1|0|Z]]
        __prime_ip : list
            list of primary inputs in the VerilogGraph. Private attribute used to
            better process the blcks
        __prime_op : list
            list of primary outputs in the VerilogGraph. Private attribute used to
            better process blcks
        __op_fanout : dictionary
            Key represents a driving output (from a node) and the value is a list of 
            size 'n' containing identifiers of fan out wires

        Methods
        -------
            Public:
                Graph creation methods
                    * addPrimeIo(io_type, io_id)
                    * addCfgBlck(blck_id, inputs, output, config)
                    * addAriBlck(blck_id, inputs, outputs, config)
                    * addTribuf(blck_id, input, ctrl, output)
                    * __addGate(blck_id, gate_type, input, output)
                    * triplicateBlck(blck_id)
                    * listPrimeIos()
                    * listCfgBlcks()
                    * listAriBlcks()
                    * listTribuf()
                    * listGates()
                    * listIntermediateOps()
                    * printPrimeIos()
                    * printCfgBlcks()
                    * printAriBlcks()
                    * printTribuf()
                    * printGates()
                Graph simulation methods
                    * setIpValue()
                    * setRandomInputs()
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
                    * __processTribuf()
                    * __processGates()
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
        self.__op_fanout = {}
    
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
        final_bi_str = ''
        for c in hex_str:
            bi_str = bin(int(c, 16))[2:]
            if len(bi_str) != 4:
                bi_str = (4 - len(bi_str)%4)*'0' + bi_str
            final_bi_str += bi_str
        
        # sanity check
        if not(len(final_bi_str)%4 == 0 and (len(hex_str)*4) == len(final_bi_str)):
            print('Problem in hex2bi conversion')
        
        return final_bi_str

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
        
        if io_id == 'VCC':
            self.dGrph[io_id] = [io_type, 1]
        elif io_id == 'GND':
            self.dGrph[io_id] = [io_type, 0]
        else:
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
            output : list
                List of identifiers for the output. The first element is the driving output and the rest of the elements
                are fan out wire identifiers.
            config : str
                String of length {if n>2: 2**(n-2); else 1} representing configuration in hexadecimal
                of the cfg_blck.
            

            Example usage
            -------------
            addCfgBlck('blck1', ['ip1', 'ip2', 'ip3'], 'out_1', '1c')
        """
        # Eliminating basic outlier conditions
        if not isinstance(output, (list)):
            print("Please enter the output identifier as a list.")
            return
        if (len(inputs) == 1 and len(config) == 1):
            self.dGrph[cfg_id] = [tuple(inputs), [output[0], None], self.__convertToBinaryStr(config)[::-1]]
            if len(output) != 1:
                if output[0] not in self.__op_fanout:
                    self.__op_fanout[output[0]] = output[1:]
                else:
                    print("Duplicate driving output")
            return
        if (len(inputs) <= 2 and len(config) != 1) or (len(config) != 2**(len(inputs) - 2)):
            print('Configuration string and number of inputs do not match. No node added.')
            return
        if cfg_id in self.dGrph:
            print('cfg_id already exists. No node added.')
            return
        
        self.dGrph[cfg_id] = [tuple(inputs), [output[0], None], self.__convertToBinaryStr(config)[::-1]]
        if len(output) != 1:
                if output[0] not in self.__op_fanout:
                    self.__op_fanout[output[0]] = output[1:]
                else:
                    print("Duplicate driving output")
    
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
        if ari_id in self.dGrph:
            print('ari_id already exists. No node added.')
            return

        self.dGrph[ari_id] = [tuple(inputs), [[outputs[0], None], [outputs[1], None], [outputs[2], None]], self.__convertToBinaryStr(config)[::-1]]
        # print(self.__convertToBinaryStr(config), ari_id)

    def addTribuf(self, tribuf_id, ip, ctrl, op):
        """
            Adds a node of type tribuf to the graph.

            Parameters
            ----------
            tribuf_id : str
                Identifier for the tribuf node.
            input : str
                Identifier for the input to tribuf node.
            ctrl : str
                Identifier for the ctrl input to tribuf node.
            output : str
            Identifier for the output to tribuf node.
        """
        # Eliminating basic outlier conditions
        if tribuf_id in self.dGrph:
            print('tribuf_id already exists. No node added.')
            return
            
        self.dGrph[tribuf_id] = [(ip, ctrl), [ctrl], [op, None]]

    def __addGate(self, gate_id, gate_type, inputs, output):
        """
            Adds a node of type:
                - and_gate to the graph if gate_type is 'A'
                - or_gate to the graph if gate_type is 'O'

            Parameters
            ----------
            gate_id : str
                Identifier for the gate node.
            gate_type : char
                Should be either 'A' (for and_gate) or 'O' (for or_gate)
            inputs : list/tuple
                n-sized list/tuple of string identifiers representing input
                to the gate.
            output : str
                String identifier of the output of the gate
        """
        # Eliminating basic outlier conditions
        if(gate_type not in ['A', 'O']):
            print('Invalid gate_type. No node added.')
            return
        if gate_id in self.dGrph:
            print('gate_id already exists. No node added.')
            return
        if not len(inputs) >= 2:
            print('Cannot add a gate with less than 2 inputs. No node added.')
            return
        
        self.dGrph[gate_id] = [tuple(inputs), [gate_type, output, None]]

    def triplicateBlck(self, blck_id):
        """
            Triplicates a given blck_id in accordance to TMR approach

            Parameters
            ----------
            blck_id : str
                String identifier of the blck to triplicate
        """
        # Eliminating basic outlier conditions
        if blck_id not in self.dGrph:
            print('blck_id: ', blck_id, ' does not exist. Triplication aborted.')
            return

        # identifying the type of block and triplicating
        test = len(self.dGrph[blck_id][1])
        if test == 3:    # ari block
            ip = self.dGrph[blck_id][0]
            config = self.dGrph[blck_id][2]
            new_ids = [blck_id+'_tripd780', blck_id+'_tripd781', blck_id+'_tripd782']
            new_ops = []
            for i in range(3):
                temp_op = []
                for original_op in self.dGrph[blck_id][1]:
                    temp_op.append([original_op[0]+'_trip728'+str(i), None])
                new_ops.append(temp_op)

            self.dGrph[new_ids[0]] = [ip, new_ops[0], config]
            self.dGrph[new_ids[1]] = [ip, new_ops[1], config]
            self.dGrph[new_ids[2]] = [ip, new_ops[2], config]

            # for first output
            self.__addGate(new_ids[0]+'_and0', 'A', [new_ops[0][0][0], new_ops[1][0][0]], new_ids[0]+'_and0_o')
            self.__addGate(new_ids[1]+'_and0', 'A', [new_ops[0][0][0], new_ops[2][0][0]], new_ids[1]+'_and0_o')
            self.__addGate(new_ids[2]+'_and0', 'A', [new_ops[1][0][0], new_ops[2][0][0]], new_ids[2]+'_and0_o')

            self.__addGate(new_ids[0]+'_or0', 'O', [new_ids[0]+'_and0_o', new_ids[1]+'_and0_o', new_ids[2]+'_and0_o'], self.dGrph[blck_id][1][0][0])

            # for second output
            self.__addGate(new_ids[0]+'_and1', 'A', [new_ops[0][1][0], new_ops[1][1][0]], new_ids[0]+'_and1_o')
            self.__addGate(new_ids[1]+'_and1', 'A', [new_ops[0][1][0], new_ops[2][1][0]], new_ids[1]+'_and1_o')
            self.__addGate(new_ids[2]+'_and1', 'A', [new_ops[1][1][0], new_ops[2][1][0]], new_ids[2]+'_and1_o')

            self.__addGate(new_ids[0]+'_or1', 'O', [new_ids[0]+'_and1_o', new_ids[1]+'_and1_o', new_ids[2]+'_and1_o'], self.dGrph[blck_id][1][1][0])

            # for third output
            self.__addGate(new_ids[0]+'_and2', 'A', [new_ops[0][2][0], new_ops[1][2][0]], new_ids[0]+'_and2_o')
            self.__addGate(new_ids[1]+'_and2', 'A', [new_ops[0][2][0], new_ops[2][2][0]], new_ids[1]+'_and2_o')
            self.__addGate(new_ids[2]+'_and2', 'A', [new_ops[1][2][0], new_ops[2][2][0]], new_ids[2]+'_and2_o')

            self.__addGate(new_ids[0]+'_or2', 'O', [new_ids[0]+'_and2_o', new_ids[1]+'_and2_o', new_ids[2]+'_and2_o'], self.dGrph[blck_id][1][2][0])

            del self.dGrph[blck_id]

        elif test == 2:  # cfg block
            ip = self.dGrph[blck_id][0]
            config = self.dGrph[blck_id][2]
            new_ids = [blck_id+'_tripd780', blck_id+'_tripd781', blck_id+'_tripd782']
            new_ops =  [[self.dGrph[blck_id][2][0] + '_trip7280', None], [self.dGrph[blck_id][2][0] + '_trip7281', None], [self.dGrph[blck_id][2][0] + '_trip7282', None]]

            self.dGrph[new_ids[0]] = [ip, new_ops[0], config]
            self.dGrph[new_ids[1]] = [ip, new_ops[1], config]
            self.dGrph[new_ids[2]] = [ip, new_ops[2], config]

            self.__addGate(new_ids[0]+'_and0', 'A', [new_ops[0][0], new_ops[1][0]], new_ids[0]+'_and0_o')
            self.__addGate(new_ids[1]+'_and0', 'A', [new_ops[0][0], new_ops[2][0]], new_ids[1]+'_and0_o')
            self.__addGate(new_ids[2]+'_and0', 'A', [new_ops[1][0], new_ops[2][0]], new_ids[2]+'_and0_o')

            self.__addGate(new_ids[0]+'_or0', 'O', [new_ids[0]+'_and0_o', new_ids[1]+'_and0_o', new_ids[2]+'_and0_o'], self.dGrph[blck_id][1][0])

            del self.dGrph[blck_id]

        elif test == 1:  # tribuf
            ip = self.dGrph[blck_id][0]
            new_ids = [blck_id+'_tripd780', blck_id+'_tripd781', blck_id+'_tripd782']
            new_ops =  [[self.dGrph[blck_id][2][0] + '_trip7280', None], [self.dGrph[blck_id][2][0] + '_trip7281', None], [self.dGrph[blck_id][2][0] + '_trip7282', None]]

            self.dGrph[new_ids[0]] = [ip, [ip[1]], new_ops[0]]
            self.dGrph[new_ids[1]] = [ip, [ip[1]], new_ops[1]]
            self.dGrph[new_ids[2]] = [ip, [ip[1]], new_ops[2]]

            self.__addGate(new_ids[0]+'_and0', 'A', [new_ops[0][0], new_ops[1][0]], new_ids[0]+'_and0_o')
            self.__addGate(new_ids[1]+'_and0', 'A', [new_ops[0][0], new_ops[2][0]], new_ids[1]+'_and0_o')
            self.__addGate(new_ids[2]+'_and0', 'A', [new_ops[1][0], new_ops[2][0]], new_ids[2]+'_and0_o')

            self.__addGate(new_ids[0]+'_or0', 'O', [new_ids[0]+'_and0_o', new_ids[1]+'_and0_o', new_ids[2]+'_and0_o'], self.dGrph[blck_id][1][0])

            del self.dGrph[blck_id]
        
        else:
            print('Unknown error!!!!!!\n')
            
    def listPrimeIos(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value (0 | 1) for each of the node.
            Returns
            -------
            default: List of tuples in format (prime_io-node-IDs, io_type).
            if show_bit_value is True: List of tuples in format (prime_io-node-IDs, io_type, [1 | 0 | Z]).
        """
        lst = []
        for key in self.dGrph:
            if len(self.dGrph[key]) == 2:
                # eliminating gate-nodes
                if len(self.dGrph[key][0]) == 1:
                    if show_bit_value:
                        lst.append((key, self.dGrph[key][0], self.dGrph[key][1]))
                    else:
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
        for key in self.dGrph:
            # eliminating prime_ios node
            if len(self.dGrph[key]) != 2:
                # eliminating other node
                if len(self.dGrph[key][1]) == 2:
                    if show_bit_value:
                        lst.append((key, self.dGrph[key][2], self.dGrph[key][0], self.dGrph[key][1]))
                    else:
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
                print(node[0], ' - ', node[1][::-1], ' - ', node[2], ' - ', node[3])

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
        for key in self.dGrph:
            # eliminating prime_ios node
            if len(self.dGrph[key]) != 2:
                # eliminating pther nodes
                if len(self.dGrph[key][1]) == 3:
                    if show_bit_value:
                        lst.append((key, self.dGrph[key][2], self.dGrph[key][0], self.dGrph[key][1]))
                    else:
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

    def listTribufs(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value of the output for each of the node.
            Returns
            -------
            default: List of tuples in format 
                (tribuf-node-IDs, tuple-of-ips, output_id).
            if show_bit_value is True: List of tuples in format
                (tribuf-node-IDs, tuple-of-ips, (output_id, 1|0|Z)).
        """
        lst = []
        for key in self.dGrph:
            # eliminating prime_ios node
            if len(self.dGrph[key]) != 2:
                # eliminating other blcks 
                if len(self.dGrph[key][1]) == 1:
                    if show_bit_value:
                        lst.append((key, self.dGrph[key][0], self.dGrph[key][2])) 
                    else:
                        lst.append((key, self.dGrph[key][0], self.dGrph[key][2][0]))                        
        return lst

    def printTribufs(self, show_bit_value = False):
        """
            Prints the list of tribuf nodes in the graph.

            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also prints bit value of the output for each of the node.
        """
        tribufs = self.listTribufs(show_bit_value = show_bit_value)
        if show_bit_value:
            print('Node ID - Input - Control - OutputID - OutputValue')
            for node in tribufs:
                print(node[0], ' - ', node[1][0], ' - ', node[1][1], ' - ', node[2][0], ' - ', node[2][1])
        else:
            print('Node ID - Input - Control - OutputID')
            for node in tribufs:
                print(node[0], ' - ', node[1][0], ' - ', node[1][1], ' - ', node[2])

    def listGates(self, show_bit_value = False):
        """
            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also returns bit value (0 | 1) for each of the node.
            Returns
            -------
            default: List of tuples in format (gate-ID, gate_type, gate-inputs, gate-output).
            if show_bit_value is True: List of tuples in format (gate-ID, gate_type, gate-inputs, gate-output, output-value: [1|0|Z]).
        """
        lst = []
        for key in self.dGrph:
            if len(self.dGrph[key]) == 2:
                # eliminating primeIo node
                if len(self.dGrph[key][0]) >= 2:
                    if show_bit_value:
                        lst.append((key, self.dGrph[key][1][0], self.dGrph[key][0], self.dGrph[key][1][1], self.dGrph[key][1][2]))
                    else:
                        lst.append((key, self.dGrph[key][1][0], self.dGrph[key][0], self.dGrph[key][1][1]))
        return lst

    def printGates(self, show_bit_value = False):
        """
            Prints the list of gate nodes in the graph.

            Parameters
            ----------
            show_bit_value : boolean (default: False)
                If set True, also prints bit value of each node.
        """
        gates = self.listGates(show_bit_value = show_bit_value)
        if show_bit_value:
            print('Node ID --- Gate Type --- Inputs --- Output --- OutputValue')
            for node in gates:
                print(node[0], ' --- ', node[1], ' --- ', node[2], ' --- ', node[3], ' --- ', node[4])
        else:
            print('Node ID --- Gate Type --- Inputs --- Output')
            for node in gates:
                print(node[0], ' --- ', node[1], ' --- ', node[2], ' --- ', node[3])

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
                (inter_op, blck_of_origin, [1|0|Z]).
        """
        lst = []
        prime_ips = [io[0] for io in self.listPrimeIos() if io[1] == 'i']

        # obtaining intermediate outputs of each configuration block
        cfg_blcks = self.listCfgBlcks(show_bit_value)
        for cfg in cfg_blcks:
            if cfg[3][0] not in prime_ips:
                if show_bit_value:
                    lst.append((cfg[3][0], cfg[0], cfg[3][1]))
                else:
                    lst.append((cfg[3][0], cfg[0]))
        
        # obtaining intermediate outputs of each ari block
        ari_blcks = self.listAriBlcks(show_bit_value)
        for ari in ari_blcks:
            for ari_op in ari[3]:
                if ari_op[0] not in prime_ips:
                    if show_bit_value:
                        lst.append((ari_op[0], ari[0], ari_op[1]))
                    else:
                        lst.append((ari_op[0], ari[0]))
        
        # obtaining intermediate outputs of each tribuf
        blcks = self.listTribufs(show_bit_value)
        for tri in blcks:
            if tri[2][0] not in prime_ips:
                if show_bit_value:
                    lst.append((tri[2][0], tri[0], tri[2][1]))
                else:
                    lst.append((tri[2][0], tri[0]))
        
        # obtaining intermediate outputs of each gate
        blcks = self.listGates(show_bit_value)
        for gate in blcks:
            if gate[3] not in prime_ips:
                if show_bit_value:
                    lst.append((gate[3], gate[0], gate[4]))
                else:
                    lst.append((gate[3], gate[0]))

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
    
    def setRandomInputs(self):
        """
            Sets random input values to all the primary inputs
        """
        prime_ips = [io[0] for io in self.listPrimeIos() if (io[1] == 'i' and (io[0] not in ['VCC', 'GND']))]
        bit_str = self.__randomStringGen(len(prime_ips))

        for idx, ip in enumerate(prime_ips):
            self.dGrph[ip][1] = int(bit_str[idx])

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
        blck_ids = [blck[0] for blck in self.listCfgBlcks()]
        for cfg_id in blck_ids:
            self.dGrph[cfg_id][1][1] = None
        
        # setting ari_blck output values to None
        blck_ids = [blck[0] for blck in self.listAriBlcks()]
        for ari_id in blck_ids:
            self.dGrph[ari_id][1][0][1] =  None
            self.dGrph[ari_id][1][1][1] =  None
            self.dGrph[ari_id][1][2][1] =  None
        
        # setting tribuf output values to None
        blck_ids = [blck[0] for blck in self.listTribufs()]
        for tri_id in blck_ids:
            self.dGrph[tri_id][2][1] = None
        
        # setting gate output values to None
        blck_ids = [blck[0] for blck in self.listGates()]
        for gate_id in blck_ids:
            self.dGrph[gate_id][1][2] = None

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
        # Outlier check for Z state in input string
        if 'Z' in ip_str:
            self.dGrph[blck_id][1][1] = 'Z'
        else:
            if len(ip_str) == 1:
                self.dGrph[blck_id][1][1] = int(ip_str, 2)
            else:
                self.dGrph[blck_id][1][1] = self.dGrph[blck_id][2][int(ip_str, 2)]

        # update primary output if current block's output is primary output
        if self.dGrph[blck_id][1][0] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][1][0]][1] = self.dGrph[blck_id][1][1]
        
        # update fan out outputs
        if self.dGrph[blck_id][1][0] in self.__op_fanout:
            for fanOp in self.__op_fanout[self.dGrph[blck_id][1][0]]:
                # sanity check
                if fanOp in self.__prime_op:
                    self.dGrph[fanOp][1] = self.dGrph[blck_id][1][1]
                else:
                    print("Sanity check failed.")

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
        # Outlier check for Z state in input string
        if 'Z' in ip_str:
            self.dGrph[blck_id][1][0][1] = 'Z'
            self.dGrph[blck_id][1][1][1] = 'Z'
            self.dGrph[blck_id][1][2][1] = 'Z'
        else:
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
    
    def __processTribuf(self, blck_id, ip_str):
        """
            Processes the tribuf blocks and sets the values of each output node.
            Note: This function should only be called from __processBlcks()

            Parameters
            ----------
            blck_id : str
                Identifier of the block
            ip_str : str
                String of input values
        """
        if ip_str[1] == '1':
            self.dGrph[blck_id][2][1] = ip_str[0]
        else:
            self.dGrph[blck_id][2][1] = 'Z'
        
        # update primary output if current block's output is primary output
        if self.dGrph[blck_id][2][0] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][2][0]][1] = self.dGrph[blck_id][2][1]

    def __processGates(self, blck_id, ip_str):
        """
            Processes the gate blocks and sets the values of each output node.
            Note: This function should only be called from __processBlcks()

            Parameters
            ----------
            blck_id : str
                Identifier of the block
            ip_str : str
                String of input values
        """
        # Outlier check for Z state in input string
        if 'Z' in ip_str:
            self.dGrph[blck_id][1][2] = 'Z'
        else:
            # converting input bit stream to boolean variables for processing
            ip_bool = []
            for ip in ip_str:
                ip_bool.append(self.__charToBool(ip))

            if self.dGrph[blck_id][1][0] == 'A':
                output = True
                for x in ip_bool:
                    output = output and x
                self.dGrph[blck_id][1][2] = self.__boolToChar(output)
            elif self.dGrph[blck_id][1][0] == 'O':
                output = False
                for x in ip_bool:
                    output = output or x
                self.dGrph[blck_id][1][2] = self.__boolToChar(output)

        # update primary output if current block's output is primary output
        if self.dGrph[blck_id][1][1] in self.__prime_op:
            self.dGrph[self.dGrph[blck_id][1][1]][1] = self.dGrph[blck_id][1][2]

    def __processBlcks(self, blck_id):
        """
            Processes the blocks and sets the values of each output node.
            Note: Should only be called by from simulate function and/or recursively.

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
                                if len(self.dGrph[all_ios[i][1]]) == 2: # gates
                                    ip_str += str(self.dGrph[all_ios[i][1]][1][2])
                                else:
                                    test = len(self.dGrph[all_ios[i][1]][1])
                                    if test == 1:   # tribuf
                                        ip_str += str(self.dGrph[all_ios[i][1]][2][1])
                                    elif test == 2: # cfg
                                        ip_str += str(self.dGrph[all_ios[i][1]][1][1])
                                    elif test == 3: # ari
                                        for op in self.dGrph[all_ios[i][1]][1]:
                                            if op[0] == ip:
                                                ip_str += str(op[1])
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
            print('It\'s a bug! ip_str: ', ip_str, ' blck: ', blck_id)
            return False
    
        # Calculating output
        # Differentiating between types of blocks
        if len(self.dGrph[blck_id]) == 2: # gates
            self.__processGates(blck_id, ip_str)
        else:
            test = len(self.dGrph[blck_id][1])
            if test == 3:    # ari block
                self.__processAriBlck(blck_id, ip_str)
            elif test == 2:  # cfg block
                self.__processCfgBlck(blck_id, ip_str)
            elif test == 1:  # tribuf
                self.__processTribuf(blck_id, ip_str)
            else:
                print('Unknown error!\n')
                return False

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
        
        # iterating all tribufs
        blck_ids = [blck[0] for blck in self.listTribufs()]

        for tri_id in blck_ids:
            if self.dGrph[tri_id][2][1] == None:
                if(self.__processBlcks(tri_id)):
                    print('Processed tribuf: ', tri_id)
                else:
                    print('Some error in processing tribuf: ', tri_id)
        
        # iterating all gates
        blck_ids = [blck[0] for blck in self.listGates()]

        for gate_id in blck_ids:
            if self.dGrph[gate_id][1][2] == None:
                if(self.__processBlcks(gate_id)):
                    print('Processed gate: ', gate_id)
                else:
                    print('Some error in processing gate: ', gate_id)

    def __randomStringGen(self, len):
        """
            Generates a binary string of input length
        """
        binString = ''
        for _ in range(len):
            binString = binString + str(random.randrange(100)%2)

        return binString


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

    vg.addCfgBlck('cfg1', ('i_1', 'i_2', 'i_3'), ['cfg1_o'], 'c2')
    vg.addCfgBlck('cfg2', ('i_4', 'cfg1_o', 'i_5'), ['cfg2_o'], '57')

    vg.addAriBlck('ari1', ['i_1', 'cfg1_o', 'tri1_op', 'cfg1_o', 'cfg2_o'], ['ari1_y', 'ari1_s', 'o_2'], 'A5D21')
    vg.addAriBlck('ari2', ['tri2_op', 'cfg2_o', 'i_5', 'i_3', 'i_4'], ['ari2_y', 'o_1', 'ari2_fco'], 'EC9B5')

    vg.addTribuf('tri1', 'i_4', 'i_1', 'tri1_op')
    vg.addTribuf('tri2', 'cfg2_o', 'i_3', 'tri2_op')
    vg.addTribuf('tri3', 'ari1_y', 'cfg1_o', 'o_3')

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
    print(10*'-')
    vg.printTribufs(True)

    # simulation - test 2
    vg.simulate(['i_1', 'i_2', 'i_3', 'i_4', 'i_5'], '01010')

    # printing
    print('Simulation test 2')
    vg.printPrimeIos(True)
    print(10*'-')
    vg.printCfgBlcks(True)
    print(10*'-')
    vg.printAriBlcks(True)
    print(10*'-')
    vg.printTribufs(True)

    # simulation - test 3
    vg.setRandomInputs()
    vg.simulate()

    # printing
    print('Simulation test 3')
    vg.printPrimeIos(True)
    print(10*'-')
    vg.printCfgBlcks(True)
    print(10*'-')
    vg.printAriBlcks(True)
    print(10*'-')
    vg.printTribufs(True)
