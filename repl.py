# -*- coding: utf-8 -*-
import logging
import sys

from code import InteractiveConsole
import ulisp


class REPL():

    def __init__(self, locals=None, prompt=None, stdin=None, stderr=None):
        self.prompt = prompt or 'ULISP> '
        self.stdin = stdin or sys.stdin
        self.stderr = stderr or sys.stderr

    def interact(self, banner=None):
        old_ps1 = getattr(sys, 'ps1', '')
        old_ps2 = getattr(sys, 'ps2', '')
        sys.ps1 = self.prompt
        sys.ps2 = ''
        stdin, stdout, stderr = (sys.stdin, sys.stdout, sys.stderr)
        sys.stdin, sys.stdout, sys.stderr = (self.stdin, self.stderr, self.stderr)
        # logging.debug(self.locals)
        # InteractiveConsole.interact(self, banner=banner);
        logging.info('Entering repl loop')
        while True:
            code = ''
            while code == '':
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
                code = sys.stdin.readline().strip()
            logging.debug('REPL code: "%s"', code)
            ulisp.send(code+'\n')
            ulisp.receive_line()              # consume the echoed input
            # read lines and display them until the prompt is read
            while True:
                while not ulisp.is_input_waiting():
                    pass
                prefix = ulisp.receive_until_space()
                logging.debug('read prefix: %s', prefix)
                if prefix[-2:] == '> ':
                    # check for lines before the prompt
                    for l in [x for x in prefix[:-2].split('\r\n') if len(x) > 0]:
                        sys.stdout.write(l)
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                    break
                rest_of_line = ulisp.receive_line()   # read the rest of the line
                logging.debug('Read rest of line: %s', rest_of_line)
                sys.stdout.write(prefix + rest_of_line)
                sys.stdout.write('\n')
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
    shell.interact('REPL started')


if __name__ == '__main__':
    repl(prompt='ULISP> ')
