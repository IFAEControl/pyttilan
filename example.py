import pytticpx

import time 
import logging

logging.basicConfig(level=logging.DEBUG)

cpx = pytticpx.CPX()
cpx.connect("172.16.17.55", 9221)

print(cpx.getIdentifier())

print("\nRunning setVoltage commands")
cpx.setVoltage(1, 12)
cpx.setVoltage(2, 30)
cpx.setVoltage(0, 10) # It reports an error
cpx.setVoltage(1, 900) # IT reports an error

print("\nRunning getVoltage commands")
print(cpx.getVoltage(1))
print(cpx.getVoltage(2))

print("\nRunning readVoltatge command")
print(cpx.readVoltatge(1))
print(cpx.readVoltatge(2))

print("\nRunning setCurrent commands")
cpx.setCurrent(1, 8)
cpx.setCurrent(2, 13)
cpx.setCurrent(3, 8) # It reports an error
cpx.setCurrent(1, -1) # IT reports an error

print("\nRunning getCurrent commands")
print(cpx.getCurrent(1))
print(cpx.getCurrent(2))

print("\nRunning readCurrent command")
print(cpx.readCurrent(1))
print(cpx.readCurrent(2))
print(cpx.readCurrent(10))

cpx.setDeltaCurrent(1, 5)
cpx.setDeltaVoltage(2, 10)

print(cpx.getDeltaCurrent(1))
print(cpx.getDeltaCurrent(2))
print(cpx.getDeltaVoltage(2))

print(cpx.getCurrent(1))
print(cpx.incCurrent(1))
print(cpx.getCurrent(1))

print(cpx.getVoltage(2))
print(cpx.incVoltage(2))
print(cpx.getVoltage(2))

print(cpx.local())

cpx.disconnect()
