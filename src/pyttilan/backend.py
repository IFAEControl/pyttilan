#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'David Roman'
__copyright__ = 'Copyright 2020'
__date__ = '26/11/20'
__credits__ = ['David Roman', 'Otger Ballester', ]
__license__ = 'CC0 1.0 Universal'
__version__ = '0.1'
__maintainer__ = 'IFAE Control Department'
__email__ = 'ifae-control@ifae.es'

import socket
import logging
from threading import Lock
from pyttilan.commands import Commands, TTiPLCommands, TTiCPxCommands
import re
from warnings import deprecated

log = logging.getLogger(__name__)


class TTiBackendExc(Exception):
    pass


class SockCommand:
    def __init__(self, ip, port=9221, valid_commands=Commands()):
        self._ip = ip
        self._port = port
        self._sock = None
        self._sock_file = None
        self.valid_commands = valid_commands

    def connect(self, ip=None, port=None):
        if ip:
            self._ip = ip
        if port:
            self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._ip, self._port))
        self._sock_file = self._sock.makefile()

    def disconnect(self):
        if self._sock:
            self._sock.shutdown(socket.SHUT_RDWR)
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
            raise TTiBackendExc("Client not connected")

    def execute_command(self, command):
        if self.valid_commands.validate_command(command) is None:
            msg = "INVALID COMMAND: {}".format(command)
            log.error(msg)
            raise TTiBackendExc(msg)
        self._sock_send(str.encode(command))

    def read_response(self):
        return self._sock_file.readline()[:-1]


class SlaveModes:
    tracking = 2
    independent = 0


class TTiBackend:
    def __init__(self, valid_commands=Commands(), num_outputs=1):
        self.sock = None
        self._valid_commands = valid_commands
        self.n_outputs = num_outputs
        self._lock = Lock()
        self.last_rx = None
        self.last_tx = None
        self.last_eer = None
        self.last_esr = None
        # Helper function that executes a command and reads the response

    def check_if_error(self):
        self.sock.execute_command("*ESR?")
        err = int(self.sock.read_response())
        self.last_esr = err
        if err != 0:
            if err & (1 << 5):
                msg = "Command error detected"
                log.error(msg)
                raise TTiBackendExc(msg)

            if err & (1 << 4):
                self.sock.execute_command("EER?")
                exe_err = int(self.sock.read_response())
                self.last_eer = exe_err
                if 1 <= exe_err <= 9:
                    msg = "[Execution error] Internal hardware error"
                    log.error(msg)
                    raise TTiBackendExc(msg)
                elif exe_err == 100:
                    msg = "[Execution error] Range error"
                    log.error(msg)
                    raise TTiBackendExc(msg)
                elif exe_err == 101:
                    msg = "[Execution error] Corrupted data"
                    log.error(msg)
                    raise TTiBackendExc(msg)
                elif exe_err == 102:
                    msg = "[Execution error] There are no data"
                    log.error(msg)
                    raise TTiBackendExc(msg)
                elif exe_err == 103:
                    msg = "[Execution error] Second output not available"
                    log.error(msg)
                    raise TTiBackendExc(msg)
                elif exe_err == 104:
                    msg = "[Execution error] Command not valid with output on"
                    log.error(msg)
                    raise TTiBackendExc(msg)
                elif exe_err == 200:
                    msg = "[Execution error] Cannot write (read only)"
                    log.error(msg)
                    raise TTiBackendExc(msg)

            if err & (1 << 3):
                msg = "Verify timeout detected"
                log.error(msg)
                raise TTiBackendExc(msg)
            if err & (1 << 2):
                msg = "Query error detected"
                log.error(msg)
                raise TTiBackendExc(msg)

    def _clear_lasts(self):
        self.last_rx = ''
        self.last_tx = ''
        self.last_eer = ''
        self.last_esr = ''

    # this function only should be used with commands that returns a response
    def _process_command(self, cmd):
        with self._lock:
            self._clear_lasts()
            log.info("Processing " + cmd)

            # If an error happens with socket it will raise an exception or if
            # it is not conn
            self.sock.execute_command(cmd)
            self.last_tx = cmd
            data = self.sock.read_response()
            self.last_rx = data
            self.check_if_error()  # if there is an error it raises TTiCPXExc
            return data

    def _execute_command(self, cmd):
        with self._lock:
            self._clear_lasts()
            log.info("Executing " + cmd)
            # If an error happens with socket it will raise an exception or if
            # it is not conn
            self.sock.execute_command(cmd)
            self.last_tx = cmd
            self.check_if_error()  # if there is an error it raises TTiCPXExc

    def _check_output(self, output):
        output = int(output)  # can raise ValueError

        if output not in range(1, self.n_outputs + 1):
            raise TTiBackendExc(f"Only valid values for output are "
                                f"{','.join([str(l) for l in range(1, self.n_outputs + 1)])}")
        return output

    def connect(self, ip, port=9221):
        if self.sock is None:
            self.sock = SockCommand(ip=ip, port=port, valid_commands=self._valid_commands)
        self.sock.connect(ip, port)

    def disconnect(self):
        self.sock.disconnect()


class CommonBackend(TTiBackend):
    """
    This Backend has been verified against a PL068 power supply.

    CommonBackend contains the commands that are common to CPx and PL power supplies. For each power supply series a new
    class that inherits from this one must be created.

    For commands that return values, parsing is implemented to return the value as a float or integer. I fear that not
    all power supply models will follow same templates on returning values. If you are using another model or series and
    the parsing fails, do not change it on this class. On its own class for the series, overwrite the methods that are
    wrongly parsed

    For commands that returns information instead of values, no parsing is done

    """

    def _get_status(self, output):
        cmd = "OP{}?".format(self._check_output(output))
        return self._process_command(cmd)

    def _set_mode(self, mode):
        m = int(mode)
        if m not in (0, 2):
            raise TTiBackendExc(
                "Only valid modes are 0 (independent) and 2 (tracking))")
        cmd = "CONFIG {}".format(mode)
        return self._execute_command(cmd)

    def _get_mode(self):
        return self._process_command("CONFIG?")

    # COMMANDS

    def set_mode_independent(self):
        self._set_mode(SlaveModes.independent)

    def set_mode_tracking(self):
        self._set_mode(SlaveModes.tracking)

    def is_independent_mode(self):
        return int(self._get_mode()) == SlaveModes.independent

    def is_tracking_mode(self):
        return int(self._get_mode()) == SlaveModes.tracking

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

    @deprecated("Use enable_output_channel or enable_output_all instead.")
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

    @deprecated("Use disable_output_channel or disable_output_all instead.")
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

    def enable_output_channel(self, output):
        cmd = "OP{} 1".format(self._check_output(output))
        self._execute_command(cmd)

    def disable_output_channel(self, output):
        cmd = "OP{} 0".format(self._check_output(output))
        self._execute_command(cmd)

    def enable_output_all(self):
        cmd = "OPALL 1"
        self._execute_command(cmd)

    def disable_output_all(self):
        cmd = "OPALL 0"
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
    def get_configured_voltage(self, output):
        """
        Return the output configured voltage value
        """
        cmd = "V{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            match = re.match(f"V{output} ([0-9,\.,\-,e]*)", data)
            if match:
                return float(match.groups()[0])
        raise TTiBackendExc("Command did not return a valid string. Received: {}".format(data))

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
        raise TTiBackendExc("Command returned {}".format(data))

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
        raise TTiBackendExc("Command returned {}".format(data))

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
        """
        Return the output configured voltage value
        """
        cmd = "I{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            match = re.match(fr"I{output} ([0-9,\.,\-,e]*)", data)
            if match:
                return float(match.groups()[0])
        raise TTiBackendExc("Command did not return a valid string. Received: {}".format(data))

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
        raise TTiBackendExc("Command returned {}".format(data))

    def set_delta_current_limit(self, output, amps):
        cmd = "DELTAI{} {}".format(self._check_output(output), float(amps))
        self._execute_command(cmd)

    def get_delta_current(self, output):
        cmd = "DELTAI{}?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            return data.split()[1]
        raise TTiBackendExc("Command returned {}".format(data))

    def inc_current_limit(self, output):
        cmd = "INCI{}".format(self._check_output(output))
        self._execute_command(cmd)

    def dec_current(self, output):
        cmd = "DECI{}".format(self._check_output(output))
        self._execute_command(cmd)


class CPxBackend(CommonBackend):
    """
    There are no differences between common and CPx
    """
    def __init__(self, num_outputs=1):
        super().__init__(valid_commands=TTiCPxCommands(), num_outputs=num_outputs)


class IRangeValues:
    low = 1  # (500/800mA for PL series)
    high = 2


class PLBackend(CommonBackend):

    def __init__(self, num_outputs=1):
        super().__init__(valid_commands=TTiPLCommands(), num_outputs=num_outputs)

    def set_irange(self, output, value):
        if int(value) not in (1, 2):
            raise TTiBackendExc('irange can only be set to 1 or 2. 1 means low range (500/800 mA) - 2 means High range')
        cmd = f"IRANGE{self._check_output(output)} {value}"
        self._execute_command(cmd)

    def get_irange(self, output):
        cmd = f"IRANGE{self._check_output(output)}?"
        return int(self._process_command(cmd))

    def get_ipaddr(self):
        cmd = "IPADDR?"
        return self._process_command(cmd)

    def get_netmask(self):
        cmd = "NETMASK?"
        return self._process_command(cmd)

    def get_netconfig(self):
        cmd = "NETCONFIG?"
        return self._process_command(cmd)

    def get_OVP(self, output):
        """
        Over Voltage Protection
        We overwrite common function because PL068 model does not return VP<N> <NR2><RMT> as said on the specs,
        it simply returns the value in Volts
        """
        cmd = "OVP{}?".format(self._check_output(output))
        return float(self._process_command(cmd))

    def get_OCP(self, output):
        """
        Over Current Protection setting
        We overwrite common function because PL068 model does not return CP<N> <NR2><RMT> as said on the specs,
        it simply returns the value in Amperes
        """
        cmd = "OCP{}?".format(self._check_output(output))
        return float(self._process_command(cmd))

    def read_voltage(self, output):
        """
        Reads output voltage
        We overwrite common function to parse value and return it. We receive from Power Supply: <NR2>V<RMT>
        :param output: output to readback the voltage
        :return: voltage value, float
        """
        cmd = "V{}O?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            match = re.match(r"([0-9,\.,e,\-]*)V", data)
            if match:
                return float(match.groups()[0])
        raise TTiBackendExc(f"Data received not valid. Received: {data}")

    def read_current(self, output):
        """
        Reads output current
        We overwrite common function to parse value and return it. We receive from Power Supply: <NR2>A<RMT>
        :param output: output to readback the voltage
        :return: voltage value, float
        """
        cmd = "I{}O?".format(self._check_output(output))
        data = self._process_command(cmd)
        if data:
            match = re.match(r"([0-9,\.,e,\-]*)A", data)
            if match:
                return float(match.groups()[0])
        raise TTiBackendExc(f"Data received not valid. Received: {data}")
