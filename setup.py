#!/usr/bin/env python
"""Minimal shim setup.py for legacy tooling.

Metadata is provided in `pyproject.toml` (PEP 621). This file exists to
allow older tools that still import `setup.py` to work. Modern build tools
use PEP 517/518 and will read metadata from `pyproject.toml`.
"""
from setuptools import setup

# Delegate metadata to `pyproject.toml` (PEP 517). Keeping a minimal
# setup.py helps compatibility with some tools and environments.
setup()
