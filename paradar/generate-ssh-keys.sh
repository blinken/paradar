#!/bin/sh

/bin/dd if=/dev/hwrng of=/dev/urandom count=1 bs=4096
mkdir -p /storage/etc/ssh
chown root:root /storage/etc/ssh
chmod 0700 /storage/etc/ssh
/usr/bin/ssh-keygen -A -v -f /storage

