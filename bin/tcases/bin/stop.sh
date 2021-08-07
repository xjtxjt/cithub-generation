#!/bin/sh
ps -A | grep org.cornutum.tcases.TcasesCommand | awk '{print $1}' | while read pid
do
  # echo kill -9 $pid
  kill -9 $pid
done
