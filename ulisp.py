#pylint: disable=global-statement
import logging

import serial
import serial.tools.list_ports
import logconfig

logconfig.configure()
logger = logging.getLogger(__name__)

class NoPortFoundException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "No port found for <{0}>".format(self.message)


class MultiplePortsFound(Exception):
    pass

ulisp_port = None


def find_ulisp_port(board_name):
    ports = serial.tools.list_ports.comports()
    possible_ports = [p.device for p in ports if p.description == board_name]
    if len(possible_ports) == 0:          # no port found
        raise NoPortFoundException(board_name)
    elif len(possible_ports) > 1:         # too many ports found
        raise MultiplePortsFound([p.device for p in possible_ports])
    else:
        return possible_ports[0]


def open_ulisp_port(board_name):
    global ulisp_port
    port = find_ulisp_port(board_name)
    ulisp_port = serial.Serial(port,
                               baudrate=9600,
                               bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               timeout=0.5)



def send_to_ulisp(code):
    logger.debug('sending to ulisp: %s', code)
    ulisp_port.write(code.encode('utf-8'))


def receive_line_from_ulisp():
    result = ulisp_port.read_until(b'\r\n').decode('utf-8').rstrip()
    logger.debug('received from ulisp: %s', result)
    return result

def consume_from_ulisp(contents):
    ulisp_port.read(1)
    result = ulisp_port.read_until(contents).decode('utf-8')
