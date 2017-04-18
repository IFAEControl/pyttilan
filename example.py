import pytticpx

import time 
import logging

logging.basicConfig(level=logging.DEBUG)

cpx = pytticpx.CPX()
cpx.connect("172.16.17.55", 9221)

print(cpx.get_identifier())

print("\nRunning setVoltage commands")
cpx.set_voltage(1, 12)
cpx.set_voltage(2, 30)
try:
    cpx.set_voltage(0, 10) # It reports an error
except pytticpx.TTiCPXExc:
    print("Raised an exception as it should")
try:
    cpx.set_voltage(1, 900) # IT reports an error
except pytticpx.TTiCPXExc:
    print("Raised an exception as it should")


print("\nRunning getVoltage commands")
print(cpx.get_voltage(1))
print(cpx.get_voltage(2))

print("\nRunning readVoltatge command")
print(cpx.read_voltage(1))
print(cpx.read_voltage(2))

print("\nRunning setCurrent commands")
cpx.set_current_limit(1, 8)
cpx.set_current_limit(2, 13)
try:
    cpx.set_current_limit(3, 8) # It reports an error
    cpx.set_current_limit(1, -1) # IT reports an error
except pytticpx.TTiCPXExc:
    pass

print("\nRunning getCurrent commands")
print(cpx.get_current_limit(1))
print(cpx.get_current_limit(2))

print("\nRunning readCurrent command")
print(cpx.read_current(1))
print(cpx.read_current(2))
print(cpx.read_current(10))

cpx.set_delta_current_limit(1, 5)
cpx.set_delta_voltage(2, 10)

print(cpx.get_delta_current(1))
print(cpx.get_delta_current(2))
print(cpx.get_delta_voltage(2))

print(cpx.get_current_limit(1))
print(cpx.inc_current_limit(1))
print(cpx.get_current_limit(1))

print(cpx.get_voltage(2))
print(cpx.inc_voltage(2))
print(cpx.get_voltage(2))

print(cpx.local())

cpx.disconnect()

# this should fail
print(cpx.local())
