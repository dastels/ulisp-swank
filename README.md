ulisp-swank

This is a SWANK server written in Python that sits between slime (running in
Emacs) and ulisp (running on a microcontroller board connected via a serial
port - usually using a USB<->serial convertor)

Install slime.

Add to your init.el:

> (setq inferior-lisp-program "python3 path_to-server.py -p 4005 -b board_name")

E.g.;

> (setq inferior-lisp-program "python3 ~/ulisp-swank/server.py -p 4005 -b \\"Adafruit Feather M4\\"")

You can find values for the board name by connecting your board and running the
fiollowing in Python.:

> >>> import serial.tools.list_ports
> >>> ports = serial.tools.list_ports.comports()
>
>>> [p.description for p in ports]

For example, this could result in:

> ['ttyS0', 'USB-Serial Controller', 'Adafruit Feather M4']

Use the appropriate board name in your init.el file (as shown above).

You will also need to make syre _printfreespace_ is not defined as the swank server depends on a simple _>_ prompt.
