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

    for host in ['vyos_r1', 'vyos_r2']:
        console = pexpect.spawn(f'sudo virsh console {host}')
        console.expect(r'password for.*:')
        console.send(passwd)
        console.send('\n')
        console.send('\n')
        console.expect('Connected to domain')
        console.send('\n')
        console.expect('login:')
        console.send('vyos\n')
        console.expect('Password:')
        console.send('vyos\n')
        with open(f'{host}.log', 'wb') as f:
            console.logfile = f
            console.expect(r'$')
            console.send('\n')
            console.expect(r'$')
            console.send('configure\n')
            console.expect(r'#')
            console.send('set interfaces ethernet eth0 address dhcp\n')
            console.expect(r'#')
            console.send('set service ssh port 22\n')
            console.expect(r'#')
            console.send("commit\n")
            console.expect(r'#')
            console.send('save\n')
            console.expect(r'#')
            console.send('exit\n')
            console.expect(r'$')
            console.send('mkdir -p ~/.ssh\n')
            console.expect(r'$')
            console.send('chmod 700 .ssh\n')
            console.expect(r'$')
            console.send(f'echo "{key}" >> .ssh/authorized_keys\n')
            console.expect(r'$')
            console.send('chmod 600 .ssh/authorized_keys\n')
            console.expect(r'$')
            console.send('exit\n')
            #console.interact()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


