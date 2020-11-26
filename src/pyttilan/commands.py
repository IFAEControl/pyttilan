#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" A simple python script

"""
__author__ = 'Otger Ballester'
__copyright__ = 'Copyright 2020'
__date__ = '26/11/20'
__credits__ = ['Otger Ballester', ]
__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Otger Ballester'
__email__ = 'otger@ifae.es'

import re


class Commands:
    _valid_commands_re = []

    @classmethod
    def validate_re_commands(cls):
        for cmd in cls._valid_commands_re:
            re.compile(cmd)

    def __init__(self, num_channels=1):
        self.N = num_channels
        self._compiled = [re.compile(pattern) for pattern in self._valid_commands_re]

        # self._single_re = "(" + ")|(".join(self._valid_commands_re) + ")"
        # print(f"single_re: '{self._single_re}'")

    def validate_command(self, command):
        a = None
        for regex in self._compiled:
            a = regex.match(command)
            if a:
                break
        return a


class TTiCPxCommands(Commands):
    # Documentation http://resources.aimtti.com/manuals/CPX400DP_Instruction_Manual-Iss1.pdf
    _valid_commands_re = [
        r"V([1-3]) ([0-9,\.,e,\-]*)",  # set output voltage
        r"V([1-3])V ([0-9,\.,e,\-]*)",  # set output voltage with verify
        r"OVP([1-3]) ([0-9,\.,e,\-]*)",
        r"I([1-3]) ([0-9,\.,e,\-]*)",
        r"OCP([1-3]) ([0-9,\.,e,\-]*)",
        r"V([1-3])\?",
        r"I([1-3])\?",
        r"OVP([1-3])\?",
        r"OCP([1-3])\?",
        r"V([1-3])O\?",
        r"I([1-3])O\?",
        r"DELTAV([1-3]) ([0-9,\.,e,\-]*)",
        r"DELTAI([1-3]) ([0-9,\.,e,\-]*)",
        r"DELTAV([1-3])\?",
        r"DELTAI([1-3])\?",
        r"INCV([1-3])",
        r"INCV([1-3])V",
        r"DECV([1-3])",
        r"DECV([1-3])V",
        r"INCI([1-3])",
        r"DECI([1-3])",
        r"OP([1-3]) ([0-1])",
        r"OPALL ([0-1])",
        r"OP([1-3])\?",
        r"TRIPRST",
        r"LSR([1-3])\?",
        r"LSE([1-3]) ([0-9,\.,e,\-]*)",
        r"LSE([1-3])\?",
        r"SAV([1-3]) ([0-9])",
        r"RCL([1-3]) ([0-9])",
        r"RATIO ([0-9,\.,e,\-]*)",
        r"RATIO\?",
        r"\*CLS",
        r"EER\?",
        r"\*ESE ([0-9,\.,e,\-]*)",
        r"\*ESE\?",
        r"\*ESR\?",
        r"\*IST\?",
        r"\*OPC",
        r"\*OPC\?",
        r"\*PRE ([0-9,\.,e,\-]*)",
        r"\*PRE\?",
        r"QER\?",
        r"\*RST",
        r"\*SRE ([0-9,\.,e,\-]*)",
        r"\*SRE\?",
        r"\*STB\?",
        r"\*WAI",
        r"LOCAL",
        r"IFLOCK",
        r"IFLOCK\?",
        r"IFUNLOCK",
        r"ADDRESS\?",
        r"\*IDN\?",
        r"CONFIG\?",
        r"\*TST\?",
        r"\*TRG"
    ]


class TTiPLCommands(Commands):
    _valid_commands_re = [
        r"V([1-3]) ([0-9,\.,e,\-]*)",  # set output voltage
        r"V([1-3])V ([0-9,\.,e,\-]*)",  # set output voltage with verify
        r"OVP([1-3]) ([0-9,\.,e,\-]*)",
        r"I([1-3]) ([0-9,\.,e,\-]*)",
        r"OCP([1-3]) ([0-9,\.,e,\-]*)",
        r"V([1-3])\?",
        r"I([1-3])\?",
        r"OVP([1-3])\?",
        r"OCP([1-3])\?",
        r"V([1-3])O\?",
        r"I([1-3])O\?",
        r"IRANGE([1-3]) ([0-9,\.,e,\-]*)",
        r"IRANGE([1-3])\?",
        r"DELTAV([1-3]) ([0-9,\.,e,\-]*)",
        r"DELTAI([1-3]) ([0-9,\.,e,\-]*)",
        r"DELTAV([1-3])\?",
        r"DELTAI([1-3])\?",
        r"INCV([1-3])",
        r"INCV([1-3])V",
        r"DECV([1-3])",
        r"DECV([1-3])V",
        r"INCI([1-3])",
        r"DECI([1-3])",
        r"OP([1-3]) ([0-1])",
        r"OPALL ([0-1])",
        r"OP([1-3])\?",
        r"TRIPRST",
        r"LSR([1-3])\?",
        r"LSE([1-3]) ([0-9,\.,e,\-]*)",
        r"LSE([1-3])\?",
        r"SAV([1-3]) ([0-9])",
        r"RCL([1-3]) ([0-9])",
        r"RATIO ([0-9,\.,e,\-]*)",
        r"RATIO\?",
        r"\*CLS",
        r"EER\?",
        r"\*ESE ([0-9,\.,e,\-]*)",
        r"\*ESE\?",
        r"\*ESR\?",
        r"\*IST\?",
        r"\*OPC",
        r"\*OPC\?",
        r"\*PRE ([0-9,\.,e,\-]*)",
        r"\*PRE\?",
        r"QER\?",
        r"\*RST",
        r"\*SRE ([0-9,\.,e,\-]*)",
        r"\*SRE\?",
        r"\*STB\?",
        r"\*WAI",
        r"LOCAL",
        r"IFLOCK",
        r"IFLOCK\?",
        r"IFUNLOCK",
        r"ADDRESS\?",
        r"IPADDR\?",
        r"NETMASK\?",
        r"NETCONFIG\?",
        r"NETCONFIG (DHCP|AUTO|STATIC)",
        r"IPADDR (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        r"NETMASK (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        r"\*IDN\?",
        r"CONFIG\?",
        r"DAMPING([1-3]) ([0-9,\.,e,\-]*)",
        r"NOLANOK ([0-9,\.,e,\-]*)",
        r"\*TST\?",
        r"\*TRG"
    ]
