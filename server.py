# -*- coding: utf-8 -*-
import logging
import socket
import sys
from threading import Thread

import logconfig
from lisp import LispReader
from protocol import SwankProtocol
from repl import repl
import ulisp

try:
    import SocketServer as socketserver
except ImportError:
    # Python 3 support
    import socketserver


__all__ = ['HEADER_LENGTH', 'SwankServerRequestHandler',
           'SwankServer', 'serve']


logconfig.configure()

HEADER_LENGTH = 6
PROMPT = "ULISP> "
LOCALS = {"__name__": "__console__", "__doc__": None}


class SwankServerRequestHandler(socketserver.BaseRequestHandler):
    """Request handler for the SwankServer.

    Handle protocol requests from swank client by dispatching received
    data to SwankProtocol.dispatch and returns to the client whatever
    it replies.

    """

    def __init__(self, request, client_address, server):
        encodings = {
            "iso-latin-1-unix": "latin-1",
            "iso-utf-8-unix": "utf-8"
        }
        self.encoding = encodings.get(server.encoding, "utf-8")
        self.protocol = SwankProtocol(
            server.socket, locals=LOCALS, prompt=PROMPT
        )
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        logging.debug('handle')
        first = True
        while True:
            try:
                raw = self.request.recv(HEADER_LENGTH)
                logging.debug('raw()->"%s"', raw)
                if raw:
                    length = int(raw, 16)
                else:
                    logging.error('Empty header received')
                    self.request.close()
                    break;
                data = self.request.recv(length)
                logging.debug('recv()->"%s"', data)

                if first:
                    ret = self.protocol.indentation_update()
                    ret = ret.encode(self.encoding)
                    logging.debug('send()->"%s"', ret)
                    self.request.send(ret)

                data = data.decode(self.encoding)
                logging.debug('dispatching -> %s', data)
                ret = self.protocol.dispatch(data)
                logging.debug('dispatch -> %s', str(ret))
                ret = ret.encode(self.encoding)
                self.request.send(ret)
                first = False
            except socket.timeout as e:
                logging.error('Socket error %s', str(e))
                break


class SwankServer(socketserver.TCPServer):
    """Good ol' TCPServer using SwankServerRequestHandler as handler."""

    def __init__(self, server_address, handler_class=SwankServerRequestHandler,
                 port_filename=None, encoding="utf-8"):
        self.port_filename = port_filename
        self.encoding = encoding
        server = socketserver.TCPServer.__init__(self, server_address, handler_class)
        ipaddr, port = self.server_address
        logging.info('Serving on: {0} ({1})'.format(ipaddr, port))
        if port_filename:
            with open(port_filename, 'w') as port_file:
                logging.debug('Writing port_file {0}'.format(port_filename))
                port_file.write("{0}".format(port))


def serve(ipaddr="127.0.0.1", port=0, port_filename=None, encoding="utf-8"):
    """Start a swank server on given port.

    If no port is provided then let the OS choose it.

    """
    server = SwankServer((ipaddr, port), port_filename=port_filename,
                         encoding=encoding)
    server.serve_forever()


def swank_process(ipaddr="127.0.0.1", port=0, port_filename=None, encoding="utf-8"):
    server = Thread(
        target=serve, args=(ipaddr, port, port_filename, encoding)
    )
    server.start()
    server.join(3)
    console = Thread(
        target=repl, kwargs=dict(prompt=PROMPT, locals=LOCALS,
                                 stdin=sys.stdin, stderr=sys.stderr)
    )
    console.start()
    console.join()


def main(read_input=False):
    """Main entry point.
pro

    Args: read_input: if True parses the setup using raw_input to
        detect port_file instead of reading commandline arguments.

    """
    ipaddr = "127.0.0.1"
    port = 0
    encoding = "utf-8"
    port_filename = None
    board = "Adafruit Feather M4"

    logging.info("Waiting for setup string...")
    try:
        # At startup slime sends setup code like this as raw input:
        # (progn
        #  (load "/home/user/.emacs.d/slime/swank-loader.lisp" :verbose t)
        #  (funcall (read-from-string "swank-loader:init"))
        #  (funcall (read-from-string "swank:start-server") "/tmp/slime.9999"))
        # This parses it and retrieves the port file to start the connection.
        try:
            setup = LispReader(raw_input()).read()
        except NameError:
            setup = LispReader(input()).read()
        if setup:
            port_filename = setup[-1][-1]
    except:
        logging.exception("Cannot parse setup from stdin. Parsing args...")

    if port_filename is None:
        logging.info("No setup string detected, parsing args...")
        try:
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("-b", "--board", help="name of the board to connect to")
            parser.add_argument("-a", "--ipaddr", help="bind address", default=ipaddr)
            parser.add_argument("-p", "--port", type=int, help="port", default=port)
            parser.add_argument("-f", "--port-filename")
            parser.add_argument("-e", "--encoding", default=encoding)
            args = parser.parse_args()
        except ImportError:
            import optparse
            parser = optparse.OptionParser()
            parser.add_option("-b", "--board", help="name of the board to connect to")
            parser.add_option("-a", "--ipaddr", help="bind address", default=ipaddr)
            parser.add_option("-p", "--port", type=int, help="port", default=port)
            parser.add_option("-f", "--port-filename")
            parser.add_option("-e", "--encoding", default=encoding)
            (args, _) = parser.parse_args()

        ipaddr = args.ipaddr
        port = args.port
        port_filename = args.port_filename
        encoding = args.encoding
        board = args.board

    logging.debug("%s", {
        'ipaddr': ipaddr,
        'port': port,
        'port_filename': port_filename,
        'encoding': encoding,
        'board': board
    })

    logging.info("Finding ulisp port")
    ulisp.open_port(board)

    swank_process(ipaddr, int(port), port_filename, encoding)


if __name__ == "__main__":
    main()
