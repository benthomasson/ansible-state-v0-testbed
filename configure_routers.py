#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    configure_routers [options]

Options:
    -h, --help        Show this page
    --debug            Show debug logging
    --verbose        Show verbose logging
"""
from docopt import docopt
import logging
import os
import sys
import pexpect
import yaml
from getpass import getpass

logger = logging.getLogger('configure_routers')


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    passwd = getpass()

    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
        key = f.read()

    script = '''
---
command: "sudo virsh console {host}"
script:
    - expect: "password for.*:"
    - send: "{passwd}"
    - send: "\\n"
    - send: "\\n"
    - expect: "Connected to domain"
    - send: "\\n"
    - expect: "login:"
    - send: "vyos\\n"
    - expect: "Password:"
    - send: "vyos\\n"
    - logfile: "{host}.log"
    - expect: "$"
    - send: "\\n"
    - expect: "$"
    - send: "configure\\n"
    - expect: "#"
    - send: "set interfaces ethernet eth0 address dhcp\\n"
    - expect: "#"
    - send: "set service ssh port 22\\n"
    - expect: "#"
    - send: "commit\\n"
    - expect: "#"
    - send: "save\\n"
    - expect: "#"
    - send: "exit\\n"
    - expect: "$"
    - send: "mkdir -p ~/.ssh\\n"
    - expect: "$"
    - send: "chmod 700 .ssh\\n"
    - expect: "$"
    - send: "echo '{key}' >> .ssh/authorized_keys\\n"
    - expect: "$"
    - send: "chmod 600 .ssh/authorized_keys\\n"
    - expect: "$"
    - send: "exit\\n"
...
    '''

    for host in ['vyos_r1', 'vyos_r2']:
        loaded_script = yaml.safe_load(script.format(key=key, host=host, passwd=passwd))
        console = pexpect.spawn(loaded_script['command'])

        logfile = None

        for line in loaded_script['script']:
            line_type, line_value = list(line.items())[0]
            print(line_type, line_value)
            if line_type == "logfile":
                logfile = open(line_value, 'wb')
                console.logfile = logfile
            elif line_type == "expect":
                console.expect(line_value)
            elif line_type == "send":
                console.send(line_value)
            elif line_type == "interact":
                console.interact()

        if logfile:
            logfile.flush()
            logfile.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
