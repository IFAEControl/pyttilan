#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" A simple python script

"""
__author__ = 'Otger Ballester'
__copyright__ = 'Copyright 2020'
__date__ = '27/11/20'
__credits__ = ['Otger Ballester', ]
__license__ = 'CC0 1.0 Universal'
__version__ = '0.1'
__maintainer__ = 'Otger Ballester'
__email__ = 'otger@ifae.es'


IP = '172.16.7.253'

from pyttilan.backend import PLBackend, TTiBackendExc, IRangeValues
from pyttilan.commands import TTiPLCommands


def write_to_file(fp, backend, comment):
    fp.write(f"{backend.last_tx}, {backend.last_rx}, {backend.last_esr}, {backend.last_eer}, {comment}\n")


pl = PLBackend(valid_commands=TTiPLCommands(), num_outputs=1)
pl.connect(IP)
with open('raw_output.txt', 'w') as fp:
    fp.write("Sent, Received, ESR, EER, Meaning\n")

    pl.set_voltage(1, 1.35)
    write_to_file(fp, pl, "Set output 1 voltage to 1.35V")

#    pl.set_voltage_verify(1, 2.35)
#    write_to_file(fp, pl, "Set output 1 voltage to 1.35V with verify")

    pl.set_OVP(1, 4)
    write_to_file(fp, pl, "Set output 1 over voltage protection to 4V")

    pl.set_current_limit(1, 0.100)
    write_to_file(fp, pl, "Set current limit of output 1 to 0.1A")

    pl.set_OCP(1, 2.2)
    write_to_file(fp, pl, "Set overcurrent protection for output 1 at 2.2A")

    print(pl.get_configured_voltage(1))
    write_to_file(fp, pl, "Get configured voltage for output 1")

    print(pl.get_current_limit(1))
    write_to_file(fp, pl, "Get configured current limit for output 1")

    print(pl.get_OVP(1))
    write_to_file(fp, pl, "Get voltage trip setting for output 1 in Volts")

    print(pl.get_OCP(1))
    write_to_file(fp, pl, "Get current trip setting for output 1 in Amperes")

    print(pl.read_voltage(1))
    write_to_file(fp, pl, "Read output 1 voltage")

    print(pl.read_current(1))
    write_to_file(fp, pl, "Read output 1 current")

    pl.set_irange(1, IRangeValues.low)
    write_to_file(fp, pl, "Set current range of output 1 to high values")

    pl.set_irange(1, IRangeValues.high)
    write_to_file(fp, pl, "Set current range of output 1 to low values")

    print(pl.get_irange(1) == IRangeValues.high)
    write_to_file(fp, pl, "Get current range of output 1")


pl.disconnect()
