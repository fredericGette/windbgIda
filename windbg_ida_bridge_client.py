# >>> import runpy
# >>> runpy.run_path("E:\\windbgIda\\windbg_ida_bridge_client.py")

import pykd
import socket
import struct

IDA_BRIGE_IP = '127.0.0.1'
IDA_BRIDGE_PORT = 60000

socket.setdefaulttimeout(0.1)

def get_pc():
    val = pykd.reg("pc")
    return val
    
def print_current_position():
    multiline_string = pykd.dbgCommand("r")
    lines = multiline_string.splitlines()
    last_two_lines = lines[-2:]
    new_string = "\n".join(last_two_lines)
    print(new_string)
    
def compute_offset(address):
    module = pykd.module(address)
    offset = pykd.addr64(address) - module.begin()
    return offset
    
def tell_ida(offset):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((IDA_BRIGE_IP, IDA_BRIDGE_PORT))
    except Exception as e:
        pykd.dprintln(f"couldn't connect to IDA bridge: {str(e)}")
        return

    s.send(struct.pack("<Q", offset))
    s.close()    

previous_user_input = ""
while True:
    pykd.setStatusMessage("'quit' to exit windbg_ida_bridge_client");    
    print_current_position()
    
    current_address = get_pc()
    
    offset = compute_offset(current_address)
    
    tell_ida(offset)

    user_input = input("windbg_ida_bridge_client> ")

    if user_input.lower() == 'quit':
        break  # This exits the loop
    elif user_input == '':
        user_input = previous_user_input
    else:
        previous_user_input = user_input
        
    try:
        result = pykd.dbgCommand(user_input, suppressOutput=False)
        if result is not None:
            pykd.dprintln(result)
    except Exception as e:
        pykd.dprintln(f"An unexpected error occurred: {e}")

pykd.dprintln("Program finished.")
pykd.setStatusMessage(" ");