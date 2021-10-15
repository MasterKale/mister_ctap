"""
Connects to each attached FIDO device, and:
    1. If the device supports CBOR commands, perform a getInfo command.
    2. If the device supports WINK, perform the wink command.
"""
from rich import print

from fido2.hid import CtapHidDevice, CAPABILITY
from fido2.ctap2 import CTAP2

try:
    from fido2.pcsc import CtapPcscDevice
except ImportError:
    CtapPcscDevice = None


def enumerate_devices():
    for dev in CtapHidDevice.list_devices():
        yield dev
    if CtapPcscDevice:
        for dev in CtapPcscDevice.list_devices():
            yield dev


for dev in enumerate_devices():
    print("CONNECT: %s" % dev)
    # print("Product name: %s" % dev.product_name)
    # print("Serial number: %s" % dev.serial_number)
    print("CTAPHID protocol version: %d" % dev.version)

    if dev.capabilities & CAPABILITY.CBOR:
        ctap2 = CTAP2(dev)
        info = ctap2.get_info()
        print("DEVICE INFO: %s" % info)
    else:
        print("Device does not support CBOR")

    if dev.capabilities & CAPABILITY.WINK:
        dev.wink()
        print("WINK sent!")
    else:
        print("Device does not support WINK")

    dev.close()
