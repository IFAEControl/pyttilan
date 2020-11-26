#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from pyttilan.commands import TTiPLCommands, Commands
import re

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


def test_validate_re_commands():
    TTiPLCommands.validate_re_commands()
    with pytest.raises(re.error) as e:
        class FailRe(Commands):
            _valid_commands_re = [r'*Incorrectre']
        FailRe.validate_re_commands()


def test_validate_command():
    plc = TTiPLCommands()
    assert isinstance(plc.validate_command("V1 3.25"), re.Match) is True
    assert isinstance(plc.validate_command("V1 0.325e-1"), re.Match) is True
    assert plc.validate_command("V0 0.2") is None
