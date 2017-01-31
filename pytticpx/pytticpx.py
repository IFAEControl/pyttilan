import socket
import logging

class CPXBackend:

    def __init__(self):
        self.sock = None
        self.sock_file = None

        # Documentation http://resources.aimtti.com/manuals/CPX400DP_Instruction_Manual-Iss1.pdf
        # Omitted commands "*TST?", "*TRG", "WAI", "*OPC", "*OPC?", 
        self.valid_commands = ["V1", "V2", "V1?", "V2?", "OVP1", "OVP2", "I1", "I2", 
                                    "V1V", "V2V", "OCP1", "OCP2", "I1?", "I2?", "OVP1?", 
                                    "OVP2?", "OCP1?", "OCP2?", "V1O?", "V2O?", "I1O?", "I2O?",
                                    "DELTAV1", "DELTAV2", "DELTAI1", "DELTAI2", "DELTAV1?", 
                                    "DELTAV2?", "DELTAI1?", "DELTAI2?", "INCV1", "INCV2", 
                                    "INCV1V", "INCV2V", "DECV1", "DECV2", "DECV1V", "DECV2V",
                                    "INCI1", "INCI2", "DECI1", "DECI2", "OP1", "OP2", "OPALL",
                                    "IFLOCK", "IFLOCK?", "IFUNLOCK", "LSR1?", "LSR2?", "LSE1",
                                    "LSE2", "LSE1?", "LSE2?", "SAV1", "SAV2", "RCL1", "RCL2", 
                                    "CONFIG", "CONFIG?", "RATIO", "RATIO?", "*CLS", "EER?", 
                                    "*ESE", "*ESE?", "*ESR?", "*IST?", "*PRE", "*STB?", 
                                    "*PRE?", "QER?", "*RST", "*SRE", "*SRE?", "*IDN?", 
                                    "ADDRESS?", "OP1?", "OP2?", "TRIPRST", "LOCAL",
                                    ]


    def connect(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock_file = self.sock.makefile()

    def disconnect(self):

        self.sock.close()   

    def executeCommand(self, command):
        if command.split()[0] not in self.valid_commands:
            logging.error("INVALID COMMAND: " + command)
            return 1
        else:
            self.sock.send(str.encode(command))
            return 0

    def readResponse(self):
        return self.sock_file.readline()[:-1]

    def checkIfError(self):
        self.executeCommand("*ESR?")
        err = int(self.readResponse())
        if err != 0:
            if err & (1<<5):
                logging.error("Command error detected")
            if err & (1<<4):
                self.executeCommand("EER?")
                exe_err = int(self.readResponse())
                if exe_err >= 1 and exe_err <= 9:
                    logging.error("[Execution error] Internal hardware error")
                elif exe_err == 100:
                    logging.error("[Execution error] Range error")
                elif exe_err == 101:
                    logging.error("[Execution error] Corrupted data")
                elif exe_err == 102:
                    logging.error("[Execution error] There are no data")
                elif exe_err == 103:
                    logging.error("[Execution error] Second output not available")
                elif exe_err == 104:
                    logging.error("[Execution error] Command not valid with output on")
                elif exe_err == 200:
                    logging.error("[Execution error] Cannot write (read only)")

            if err & (1<<3):
                logging.error("Verify timeout detected")
            if err & (1<<2):
                logging.error("Query error detected")
                
        return err



class CPX:
    def __init__(self):
        self.cpx = CPXBackend()  

    # Helper function that executes a command and reads the response
    # this function only should be used with commands that returns a response
    def _processCommand(self, cmd):
        logging.info("Processing " + cmd)
        if self.cpx.executeCommand(cmd) > 0:
            return None

        data = self.cpx.readResponse()
        err = self.cpx.checkIfError()
        if err == 0:
            return data
        else:
            return None

    def _executeCommand(self, cmd):
        logging.info("Executing " + cmd)
        err = self.cpx.executeCommand(cmd)
        if err > 0:
            return err
        return self.cpx.checkIfError()

    def _getStatus(self, output):
        cmd = "OP{}?".format(output)
        return self._processCommand(cmd)     

    def _setMode(self, mode):
        cmd = "CONFIG {}".format(mode)
        return self._executeCommand(cmd)

    def _getMode(self):
        return self._processCommand("CONFIG?")

    def connect(self, ip, port): 
        self.cpx.connect(ip, port)

    def disconnect(self): 
        self.cpx.disconnect()

    # COMMANDS 

    def readRegisterStandardEventStatus(self):
        return self._processCommand("*ESR?")

    def readRegisterLimitEventStatus(self, output):
        cmd = "LSR{}?".format(output)
        return self._processCommand(cmd)

    def readRegisterExecutionError(self):
        return self._processCommand("EER?")

    def getIdentifier(self):
        return self._processCommand("*IDN?")     

    def getAddress(self):
        return self._processCommand("ADDRESS?")

    def clearStatus(self):
        return self._executeCommand("*CLS")

    def reset(self):
        return self._executeCommand("*RST")

    def clearTrip(self): 
        return self._executeCommand("TRIPRST")

    def local(self):
        return self.cpx.executeCommand("LOCAL")

    def lock(self):
        return self._processCommand("IFLOCK")

    def isLock(self):
        return self._processCommand("IFLOCK?")

    def unlock(self):
        return self._processCommand("IFUNLOCK")

    def isIST(self):
        return self._processCommand("*IST?") == "1"

    def getRegisterQueryError(self):
        return self._processCommand("QER?")

    def getRegisterStatusByte(self):
        return self._processCommand("*STB?")

    def setRegisterServiceRequest(self, value):
        cmd = "*SRE {}".format(value)
        return self._executeCommand(cmd)

    def getRegisterServiceRequest(self):
        return self._processCommand("*SRE?")

    def setRegisterParallelPoll(self, value):
        cmd = "*PRE {}".format(value)
        return self._executeCommand(cmd)

    def getRegisterParallelPoll(self):
        return self._processCommand("*PRE?")

    def setRegisterEventStatus(self, value):
        cmd = "*ESE {}".format(value)
        return self._executeCommand(cmd)

    def getRegisterEventStatus(self):
        return self._processCommand("*ESE?")

    def setRegisterLimitEventStatus(self, output, value):
        cmd = "*LSE{} {}".format(output, value)
        return self._executeCommand(cmd)

    def getRegisterLimitEventStatus(self, output):
        cmd = "*LSE{}?".format(output)
        return self._processCommand(cmd)

    def save(self, output, store):
        cmd = "SAV{} {}".format(output, store)
        return self._executeCommand(cmd)

    def recall(self, output, store):
        cmd = "RCL{} {}".format(output, store)
        return self._executeCommand(cmd)

    def setRatio(self, value):
        cmd = "RATIO {}".format(value)
        return self._executeCommand(cmd)

    def getRatio(self):
        return self._processCommand("RATIO?")

    def setModeIndependent(self):
        return self._setMode(2)

    def setModeTracking(self):
        return self._setMode(0)

    def isModeIndependent(self):
        return self._getMode() == "2"

    def isModeTracking(self):
        return self._getMode() == "0"

    def setOn(self, *args):
        if len(args) == 0:
            cmd = "OPALL 1"
        else:
            cmd = "OP{} 1".format(args[0])

        return self._executeCommand(cmd)

    def setOff(self, *args):
        if len(args) == 0:
            cmd = "OPALL 0"
        else:
            cmd = "OP{} 0".format(args[0])

        return self._executeCommand(cmd)

    def isOn(self, output):
        return self._getStatus(output) == "1"

    def isOff(self, output):
        return self._getStatus(output) == "0"

    def setVoltage(self, output, value):
        cmd = "V{} {}".format(output, value)
        return self._executeCommand(cmd)

    def setVoltageVerify(self, output, value):
        cmd = "V{}V {}".format(output, value)
        return self._executeCommand(cmd)

    # Returns the configured voltage
    def getVoltage(self, output):
        cmd = "V{}?".format(output)
        data = self._processCommand(cmd)
        if not data:
            return data
        return data.split()[1]

    # Reads the voltage of an output
    def readVoltatge(self, output):
        cmd = "V{}O?".format(output)
        return self._processCommand(cmd)

    def getOVP(self, output):
        cmd = "OVP{}?".format(output)
        data = self._processCommand(cmd)
        if not data:
            return data
        return data.split()[1]

    def setOVP(self, output, value):
        cmd = "OVP{} {}".format(output, value)
        return self._executeCommand(cmd)

    def setDeltaVoltage(self, output, value):
        cmd = "DELTAV{} {}".format(output, value)
        return self._executeCommand(cmd)

    def getDeltaVoltage(self, output):
        cmd = "DELTAV{}?".format(output)
        data = self._processCommand(cmd)
        if not data:
            return data
        return data.split()[1]

    def incVoltage(self, output):
        cmd = "INCV{}".format(output)
        return self._executeCommand(cmd)

    def incVoltageVerify(self, output):
        cmd = "INCV{}V".format(output)
        return self._executeCommand(cmd)

    def decVoltage(self, output):
        cmd = "DECV{}".format(output)
        return self._executeCommand(cmd)

    def decVoltageVerify(self, output):
        cmd = "DECV{}V".format(output)
        return self._executeCommand(cmd)

    def setCurrent(self, output, value):
        cmd = "I{} {}".format(output, value)
        return self._executeCommand(cmd)

    # Returns the configured current
    def getCurrent(self, output):
        cmd = "I{}?".format(output)
        data = self._processCommand(cmd)
        if not data:
            return data
        return data.split()[1]

    # Reads the current of an output
    def readCurrent(self, output):
        cmd = "I{}O?".format(output)
        return self._processCommand(cmd)

    def setOCP(self, output, value):
        cmd = "OCP{} {}".format(output, value)
        return self._executeCommand(cmd)

    def getOCP(self, output):
        cmd = "OCP{}?".format(output)
        data = self._processCommand(cmd)
        if not data:
            return data
        return data.split()[1]

    def setDeltaCurrent(self, output, value):
        cmd = "DELTAI{} {}".format(output, value)
        return self._executeCommand(cmd)

    def getDeltaCurrent(self, output):
        cmd = "DELTAI{}?".format(output)
        data = self._processCommand(cmd)
        if not data:
            return data
        return data.split()[1]

    def incCurrent(self, output):
        cmd = "INCI{}".format(output)
        return self._executeCommand(cmd)

    def decCurrent(self, output):
        cmd = "DECI{}".format(output)
        return self._executeCommand(cmd)


