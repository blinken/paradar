#!/bin/bash
cd /opt/paradar
git pull --rebase -X ours --depth=1 origin release-1.5-rc1
