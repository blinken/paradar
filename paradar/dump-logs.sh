#!/bin/sh
#
# Called periodically by systemd - writes the last 100 lines of logs to
# permanent storage. Cleans up the oldest log files.

date=`date +%Y%m%d.%H%M%S`
journalctl | tail -n 200 | gzip > /storage/$date.log.gz

# Remove all but the last 500 files - https://stackoverflow.com/questions/25785/delete-all-but-the-most-recent-x-files-in-bash
ls -tp /storage/*.log.gz | grep -v '/$' | tail -n +500 | xargs -d '\n' -r rm --

