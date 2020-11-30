from pyttilan.backend import PLBackend, TTiBackendExc

import time 
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Example of use of pyttilan library on a PL068 model")
    parser.add_argument('ip', help="IP of the power supply to connect to")

    args = parser.parse_args()

    ttipl = PLBackend(num_outputs=1)
    ttipl.connect(ip=args.ip)
    print(ttipl.get_identifier())

    print("\nRunning setVoltage commands")
    ttipl.set_voltage(1, 3.30)
    try:
        ttipl.set_voltage(0, 10)  # It reports an error
    except TTiBackendExc:
        print("Correctly raised an exception because output 0 does not exist")
    else:
        print("This is an error! It should have raised an exception")

    try:
        ttipl.set_voltage(1, 900)  # IT reports an error
    except TTiBackendExc:
        print("Correctly rised an exception because we have asked for a too high value")
    else:
        print("This is an error!! It should have raised an exception")

    print("\nRunning getVoltage commands")
    print(ttipl.get_configured_voltage(1))

    print("\nRunning read voltage command")
    print(ttipl.read_voltage(1))

    print("\nRunning setCurrent commands")
    ttipl.set_current_limit(1, 0.5)

    try:
        ttipl.set_current_limit(3, 8) # It reports an error
    except TTiBackendExc:
        print("Correctly rised an exception because we have asked for an incorrect output")
    else:
        print("This is an error!! It should have raised an exception")

    try:
        ttipl.set_current_limit(1, -1)
    except TTiBackendExc:
        print("Correctly rised an exception because we have asked for a negative current value")
    else:
        print("This is an error!! It should have raised an exception")

    print("\nRunning getCurrent commands")
    print(ttipl.get_current_limit(1))

    print("\nRunning readCurrent command")
    print(ttipl.read_current(1))

    print(ttipl.local())

    ttipl.disconnect()

    # this should fail
    try:
        print(ttipl.local())
    except TTiBackendExc:
        print("Correctly rised an exception because client is not connected anymore")
    else:
        print("This is an error!! It should have raised an exception")
