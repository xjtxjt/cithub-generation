#!/bin/sh
ps -aux | grep org.cornutum.tcases.TcasesCommand | awk '{print $2}' | while read pid
do
  kill -9 $pid
done
