from dsf.connections import CommandConnection
import usb.core
import usb.util
import sys


def send_simple_code():
    command_connection = CommandConnection(debug=True)
    command_connection.connect()

    try:
        # Perform a simple command and wait for its output
        res = command_connection.perform_simple_code("M115")
        print("M115 is telling us:", res)
    finally:
        command_connection.close()

if __name__ == "__main__":

    dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)
    if dev is None:
        raise ValueError('Device not found')
    else:
        print("device found")
    
    for cfg in dev:
        sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
    for intf in cfg:
        sys.stdout.write('\t' + \
                         str(intf.bInterfaceNumber) + \
                         ',' + \
                         str(intf.bAlternateSetting) + \
                         '\n')
        for ep in intf:
            sys.stdout.write('\t\t' + \
                             str(ep.bEndpointAddress) + \
                             '\n')

    #dev.set_configuration()
    
    send_simple_code()