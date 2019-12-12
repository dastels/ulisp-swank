#pylint: disable=global-statement
import logging

import serial
import serial.tools.list_ports

lookahead = None

class NoPortFoundException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "No port found for <{0}>".format(self.message)


class MultiplePortsFound(Exception):
    pass

ulisp_port = None


def find_port(board_name):
    ports = serial.tools.list_ports.comports()
    possible_ports = [p.device for p in ports if p.description == board_name]
    if len(possible_ports) == 0:          # no port found
        raise NoPortFoundException(board_name)
    elif len(possible_ports) > 1:         # too many ports found
        raise MultiplePortsFound([p.device for p in possible_ports])
    else:
        return possible_ports[0]


def open_port(board_name):
    global ulisp_port
    port = find_port(board_name)
    ulisp_port = serial.Serial(port,
                               baudrate=9600,
                               bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               timeout=None)


def send(code):
    logging.debug('sending to ulisp: %s', code)
    ulisp_port.write(code.encode('utf-8'))


def get_a_char():
    global lookahead
    if lookahead is not None:
        temp = lookahead
        lookahead = None
        return temp
    return ulisp_port.read(1)


def push_back(c):
    global lookahead
    lookahead = c

def receive_line():
    line = ''
    while True:
        logging.debug('Reading from ulisp')
        char = get_a_char()
        logging.debug('Read char: %s', str(char))
        if (char == b'\r') or (char == b'\n'):
            while (char == b'\r') or (char == b'\n'):
                logging.debug('Consuming char: %s', str(char))
                char = get_a_char()
            logging.debug('Pushing back char: %s', str(char))
            push_back(char)
            result = line.rstrip()
            logging.debug('read line from ulisp: %s', result)
            return result
        else:
            line += chr(ord(char))


def receive_until_space():
    s = ''
    while True:
        ch = chr(ord(get_a_char()))
        s += ch
        if ch == ' ':
            return s


def is_input_waiting():
    return ulisp_port.in_waiting > 0
