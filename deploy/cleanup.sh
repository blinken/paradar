#!/bin/bash

if [ `id -u` -ne 0 ]; then
  echo "Must be run as root."
  exit 1
fi

echo "=> Entering r/w mode"
/bin/rw

echo "=> apt dist-upgrade and clean"
apt-get update
apt-get -y dist-upgrade
apt-get -y autoremove
apt-get clean

echo "=> Updating /opt/paradar"
cd /opt/paradar
git pull --rebase -X ours --depth=1 origin release-1.5-rc1

if [ $? -ne 0 ]; then
  echo "Rebase failed - aborting."
  exit 1
fi

cd /home/blinken

echo "=> Removing history files"
rm -rvf {/root,/home/blinken}/{.bash_history,.viminfo,.lesshst,.ssh/known_hosts}

echo "=> Emptying /storage"
rm -rvf /storage/*

echo "=> zeroing /boot"
rm -f /boot/zerofile
dd if=/dev/zero of=/boot/zerofile bs=1M
rm -f /boot/zerofile

echo "=> entering r/o mode"
/bin/ro

echo "=> zerofree /"
zerofree -v /dev/mmcblk0p2

echo "=> remount /storage ro"
sudo mount -o remount,ro /dev/mmcblk0p3

echo "=> zerofree /storage"
zerofree -v /dev/mmcblk0p3

echo "=> remount /storage rw"
sudo mount -o remount,rw /dev/mmcblk0p3


