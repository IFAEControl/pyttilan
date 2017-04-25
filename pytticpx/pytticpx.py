import socket
import logging
from threading import Lock

class TTiCPXExc(Exception):
    pass


class CPXBackend(object):
    def __init__(self):
        self._sock = None
        self._sock_file = None

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
        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._ip, self._port))
        self._sock_file = self._sock.makefile()

    def disconnect(self):
        if self._sock:
            self._sock.shutdown()
            self._sock.close()
            self._sock = None
            self._sock_file = None

    def _sock_send(self, s):
        if self._sock:
            try:
                self._sock.sendall(s)
            except:
                self.disconnect()
                self.connect(self._ip, self._port)
                raise
        else:
            raise TTiCPXExc("Client not connected")

    def execute_command(self, command):
        if command.split()[0] not in self.valid_commands:
            msg = "INVALID COMMAND: {}".format(command)
            logging.error(msg)
            raise Exception(msg)
        self._sock_send(str.encode(command))

    def read_response(self):
        return self._sock_file.readline()[:-1]

    def check_if_error(self):
        self.execute_command("*ESR?")
        err = int(self.read_response())
        if err != 0:
            if err & (1 << 5):
                msg = "Command error detected"
                logging.error(msg)
                raise TTiCPXExc(msg)

            if err & (1 << 4):
                self.execute_command("EER?")
                exe_err = int(self.read_response())
                if 1 <= exe_err <= 9:
                    msg = "[Execution error] Internal hardware error"
                    logging.error(msg)
                    raise TTiCPXExc(msg)
                elif exe_err == 100:
                    msg = "[Execution error] Range error"
                    logging.error(msg)
                    raise TTiCPXExc(msg)
                elif exe_err == 101:
                    msg = "[Execution error] Corrupted data"
                    logging.error(msg)
                    raise TTiCPXExc(msg)
                elif exe_err == 102:
                    msg = "[Execution error] There are no data"
                    logging.error(msg)
                    raise TTiCPXExc(msg)
                elif exe_err == 103:
                    msg = "[Execution error] Second output not available"
                    logging.error(msg)
                    raise TTiCPXExc(msg)
                elif exe_err == 104:
                    msg = "[Execution error] Command not valid with output on"
                    logging.error(msg)
                    raise TTiCPXExc(msg)
                elif exe_err == 200:
                    msg = "[Execution error] Cannot write (read only)"
                    logging.error(msg)
                    raise TTiCPXExc(msg)

            if err & (1 << 3):
                msg = "Verify timeout detected"
                logging.error(msg)
                raise TTiCPXExc(msg)
            if err & (1 << 2):
                msg = "Query error detected"
                logging.error(msg)
                raise TTiCPXExc(msg)


class CPXModes(object):
    tracking = 2
    independent = 0


class CPX(object):
    def __init__(self):
        self.cpx = CPXBackend()
        self._lock = Lock()
        # Helper function that executes a command and reads the response

    # this function only should be used with commands that returns a response
    def _process_command(self, cmd):
        with self._lock:
            logging.info("Processing " + cmd)

            self.cpx.execute_command(cmd)  # If an error happens with socket it will raise an exception or if it is not conn

            data = self.cpx.read_response()
            self.cpx.check_if_error()  # if there is an error it raises TTiCPXExc
            return data

    def _execute_command(self, cmd):
        with self._lock:
            logging.info("Executing " + cmd)
            self.cpx.execute_command(cmd)  # If an error happens with socket it will raise an exception or if it is not conn
            self.cpx.check_if_error()  # if there is an error it raises TTiCPXExc

    @staticmethod
    def _check_output(output):
        output = int(output)  ## can raise ValueError
        if output not in (1, 2):
            raise TTiCPXExc("Only valid values for output are 1 and 2")
        return output

    def _get_status(self, output):
        cmd = "OP{}?".format(self._check_output(output))
        return self._process_command(cmd)

    def _set_mode(self, mode):
        m = int(mode)
        if m not in (0, 2):
            raise TTiCPXExc("Only valid modes are 0 (independent) and 2 (tracking))")
        cmd = "CONFIG {}".format(mode)
        return self._execute_command(cmd)

    def _get_mode(self):
        return self._process_command("CONFIG?")

    def connect(self, ip, port):
        self.cpx.connect(ip, port)

    def disconnect(self):
        self.cpx.disconnect()

    # COMMANDS 

    def set_mode_independent(self):
        self._set_mode(CPXModes.independent)

    def set_mode_tracking(self):
        self._set_mode(CPXModes.tracking)

    def is_independent_mode(self):
        return int(self._get_mode()) == CPXModes.independent

    def is_tracking_mode(self):
        return int(self._get_mode()) == CPXModes.tracking

    # Not exposed as it should only be read from check_error
    # def read_register_standard_event_status(self):
    #     return self._process_command("*ESR?")

    def read_register_limit_event_status(self, output):
        cmd = "LSR{}?".format(self._check_output(output))
        return self._process_command(cmd)

    def read_register_execution_error(self):
        return self._process_command("EER?")

    def get_identifier(self):
        return self._process_command("*IDN?")

    def get_address(self):
        return self._process_command("ADDRESS?")

    def clear_status(self):
        self._execute_command("*CLS")

    def reset(self):
        self._execute_command("*RST")

    def clear_trip(self):
        self._execute_command("TRIPRST")

    def local(self):
        self._execute_command("LOCAL")

    def lock(self):
        return self._process_command("IFLOCK")

    def is_lock(self):
        return self._process_command("IFLOCK?")

    def unlock(self):
        return self._process_command("IFUNLOCK")

    def is_IST(self):
        return self._process_command("*IST?") == "1"

    def get_register_query_error(self):
        return self._process_command("QER?")

    def get_register_status_byte(self):
        return self._process_command("*STB?")

    def set_register_service_request(self, value):
        cmd = "*SRE {}".format(float(value))
        self._execute_command(cmd)

    def get_register_service_request(self):
        return self._process_command("*SRE?")

    def set_register_parallel_poll(self, value):
        cmd = "*PRE {}".format(value)
        self._execute_command(cmd)

    def get_register_parallel_poll(self):
        return self._process_command("*PRE?")

    def set_register_event_status(self, value):
        cmd = "*ESE {}".format(value)
        self._execute_command(cmd)

    def get_register_event_status(self):
        return self._process_command("*ESE?")

    def set_register_limit_event_status(self, output, value):
        cmd = "*LSE{} {}".format(output, value)
        self._execute_command(cmd)

    def get_register_limit_event_status(self, output):
        cmd = "*LSE{}?".format(output)
        return self._process_command(cmd)

    def save(self, output, store):
        cmd = "SAV{} {}".format(output, store)
        self._execute_command(cmd)

    def recall(self, output, store):
        cmd = "RCL{} {}".format(output, store)
        self._execute_command(cmd)

    def set_ratio(self, value):
        cmd = "RATIO {}".format(value)
        self._execute_command(cmd)

    def get_ratio(self):
        return self._process_command("RATIO?")

    def enable_output(self, output_1=False, output_2=False):
        if output_1:
            if output_2:
                cmd = "OPALL 1"
            else:
                cmd = "OP1 1"
        elif output_2:
            cmd = "OP2 1"
        else:
            return

        self._execute_command(cmd)

    def disable_output(self, output_1=False, output_2=False):
        if output_1:
            if output_2:
                cmd = "OPALL 0"
            else:
                cmd = "OP1 0"
        elif output_2:
            cmd = "OP2 0"
        else:
            return

        self._execute_command(cmd)

    def is_enabled(self, output):
        return int(self._get_status(self._check_output(output))) == 1

    def is_disabled(self, output):
        return int(self._get_status(self._check_output(output))) == 0

    def set_voltage(self, output, volts):
        cmd = "V{} {}".format(self._check_output(output), float(volts))
        self._execute_command(cmd)

    def set_voltage_verify(self, output, volts):
        cmd = "V{}V {}".format(self._check_output(output), float(volts))
        self._execute_command(cmd)

    # Returns the configured voltage
    def get_voltage(self, output):
        cmd = "V{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiCPXExc("Command returned {}".format(data))

    # Reads the voltage of an output
    def read_voltage(self, output):
        cmd = "V{}O?".format(self._check_output(output))
        return self._process_command(cmd)

    def get_OVP(self, output):
        """
        Over Voltage Protection
        """
        cmd = "OVP{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiCPXExc("Command returned {}".format(data))

    def set_OVP(self, output, volts):
        cmd = "OVP{} {}".format(self._check_output(output), float(volts))
        self._execute_command(cmd)

    def set_delta_voltage(self, output, volts):
        cmd = "DELTAV{} {}".format(self._check_output(output), float(volts))
        self._execute_command(cmd)

    def get_delta_voltage(self, output):
        cmd = "DELTAV{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiCPXExc("Command returned {}".format(data))

    def inc_voltage(self, output):
        """
        Increases voltage of output by a delta value, defined by set_delta_voltage
        :param output: which output of the power supply will be affected
        :return:
        """
        cmd = "INCV{}".format(self._check_output(output))
        self._execute_command(cmd)

    def inc_voltage_verify(self, output):
        cmd = "INCV{}V".format(self._check_output(output))
        self._execute_command(cmd)

    def dec_voltage(self, output):
        cmd = "DECV{}".format(self._check_output(output))
        self._execute_command(cmd)

    def dec_voltage_verify(self, output):
        cmd = "DECV{}V".format(self._check_output(output))
        self._execute_command(cmd)

    def set_current_limit(self, output, amps):
        cmd = "I{} {}".format(self._check_output(output), float(amps))
        self._execute_command(cmd)

    # Returns the configured current
    def get_current_limit(self, output):
        cmd = "I{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiCPXExc("Command returned {}".format(data))

    # Reads the current of an output
    def read_current(self, output):
        cmd = "I{}O?".format(self._check_output(output))
        return self._process_command(cmd)

    def set_OCP(self, output, amps):
        cmd = "OCP{} {}".format(self._check_output(output), float(amps))
        self._execute_command(cmd)

    def get_OCP(self, output):
        cmd = "OCP{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiCPXExc("Command returned {}".format(data))

    def set_delta_current_limit(self, output, amps):
        cmd = "DELTAI{} {}".format(self._check_output(output), float(amps))
        self._execute_command(cmd)

    def get_delta_current(self, output):
        cmd = "DELTAI{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiCPXExc("Command returned {}".format(data))

    def inc_current_limit(self, output):
        cmd = "INCI{}".format(self._check_output(output))
        self._execute_command(cmd)

    def dec_current(self, output):
        cmd = "DECI{}".format(self._check_output(output))
        self._execute_command(cmd)
