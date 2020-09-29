#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""
Usage:
    configure_hosts [options]

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

logger = logging.getLogger('configure_hosts')


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

    for host in ['host1', 'host2']:
        console = pexpect.spawn(f'sudo virsh console {host}')
        console.expect(r'password for.*:')
        console.send(passwd)
        console.send('\n')
        console.send('\n')
        console.expect('Connected to domain')
        console.send('\n')
        console.expect('login:')
        console.send('root\n')
        #console.expect('Password:')
        #console.send('1234\n')
        with open(f'{host}.log', 'wb') as f:
            console.logfile = f
            console.expect(r'#')
            console.send('\n')
            console.expect(r'#')
            console.send('echo "auto lo\niface lo inet loopback\nauto eth0\niface eth0 inet dhcp\n" > /etc/network/interfaces\n')
            console.expect(r'#')
            console.send('apk add openssh\n')
            console.expect(r'#')
            #console.send('passwd\n')
            #console.expect(r'New password:')
            #console.send('1234\n')
            #console.expect(r'Retype password:')
            #console.send('1234\n')
            #console.expect(r'#')
            console.send("echo 'PermitRootLogin yes' >>  /etc/ssh/sshd_config\n")
            console.expect(r'#')
            console.send('/etc/init.d/sshd start\n')
            console.expect(r'#')
            console.send('/etc/init.d/networking restart\n')
            console.expect(r'#')
            console.send('mkdir -p ~/.ssh\n')
            console.expect(r'#')
            console.send('chmod 700 .ssh\n')
            console.expect(r'#')
            console.send(f'echo "{key}" >> .ssh/authorized_keys\n')
            console.expect(r'#')
            console.send('chmod 600 .ssh/authorized_keys\n')
            console.expect(r'#')
            console.send("echo 'http://nl.alpinelinux.org/alpine/v3.12/main/' >> /etc/apk/repositories\n")
            console.expect(r'#')
            console.send("apk update\n")
            console.expect(r'#')
            console.send("apk add python3\n")
            console.expect(r'#')
            console.send('exit')
            #console.interact()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

