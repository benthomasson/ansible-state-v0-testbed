

# v0 testbed for ansible-state


Initialization:

	cd ansible-state
	git checkout v0
	pipenv install --dev
	pipenv shell
	cd ../ansible-state-v0-testbed
	./run
	<Enter sudo password at prompt>




# Manual steps

    1. Download and copy vyos and alpine linux to /var/lib/libvirt/images/vyos.iso and /var/lib/libvirt/images/alpine.iso
    2. virsh define host1.xml
    3. virsh define host2.xml
    4. virsh define vyos1.xml
    5. virsh define vyos2.xml
    6. add this config to host1 and host2:
        /etc/network/interfaces
        auto lo
        iface lo inet loopback
        auto eth0
        iface eth0 inet dhcp
    7. Install sshd on host1 and host2:
        apk add openssh
    8. Set root password
        passwd
    9. allow root ssh
        echo 'PermitRootLogin yes' >>  /etc/ssh/sshd_config
    10. start ssh server
        /etc/init.d/sshd start
    11. restart networking
        /etc/init.d/networking restart
    12. Configure dhcp on vyos1 and vyo2 and enable ssh
        config
        set interfaces ethernet eth0 address dhcp
        set service ssh port 22
        commit
        save
        exit

    13. Add repository for alpine to host1 and host2
        echo 'http://nl.alpinelinux.org/alpine/v3.12/main/' >> /etc/apk/repositories
        apk update
        apk add python3

    14. Add public key to hosts
        scp ~/.ssh/id_rsa.pub ...
        ssh ...
        mkdir -p .ssh
        chmod 700 .ssh
        cat id_rsa.pub >> .ssh/authorized_keys
        chmod 600 .ssh/authorized_keys

    15. Ping everything
        ansible -i inventory.yml -m ping all
    
