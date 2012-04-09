#!/bin/bash
#
#log_found=`ps -ef|grep -v grep|grep main.py|awk '{print $8}'`
#
#if [ -s $log_found ]
#then
killall python
nohup python /var/crawler/main.py &
#fi
