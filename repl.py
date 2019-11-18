# -*- coding: utf-8 -*-
import logging
import sys

import logconfig
from code import InteractiveConsole
from ulisp import send_to_ulisp, receive_line_from_ulisp, consume_from_ulisp


logconfig.configure()
logger = logging.getLogger(__name__)


class REPL():

    def __init__(self, locals=None, prompt=None, stdin=None, stderr=None):
        """Closely emulate the behavior of the interactive Python interpreter.

        This class builds on InteractiveConsole and ignores sys.ps1
        and sys.ps2 to use some slime friendly values.

        """
        self.prompt = prompt or "ULISP> "
        self.stdin = stdin or sys.stdin
        self.stderr = stderr or sys.stderr

    def interact(self, banner=None):
        old_ps1 = getattr(sys, 'ps1', '')
        old_ps2 = getattr(sys, 'ps2', '')
        sys.ps1 = self.prompt
        sys.ps2 = ""
        stdin, stdout, stderr = (sys.stdin, sys.stdout, sys.stderr)
        sys.stdin, sys.stdout, sys.stderr = (self.stdin, self.stderr, self.stderr)
        # logger.debug(self.locals)
        # InteractiveConsole.interact(self, banner=banner);
        logger.info('Entering repl loop')
        while True:
            sys.stdout.write(self.prompt)
            sys.stdout.flush()
            code = sys.stdin.readline()
            # self.write('REPL code: %s' % (code))
            send_to_ulisp(code)
            receive_line_from_ulisp()
            response = receive_line_from_ulisp()   # read the result
            receive_line_from_ulisp()   # consume the empty line
            # self.write('REPL response: %s' % (response))
            sys.stdout.write(response)
            sys.stdout.write("\n")
            sys.stdout.flush()
        sys.stdin, sys.stdout, sys.stderr = (stdin, stdout, stderr)
        sys.ps1 = old_ps1
        sys.ps2 = old_ps2

    def write_out(self, string):
        for b in bytes(string, 'utf-8'):
            self.stderr.write(str(b) + ' ')
        self.write('\n')

    def write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subclass may
        replace this with a different implementation.

        """
        self.stderr.write(data)


def repl(**kwargs):
    shell = REPL(**kwargs)
    shell.interact("REPL started")


if __name__ == '__main__':
    repl(prompt="ULISP> ")
