#!/bin/sh

pid=$(ps -A | grep bin/acts_cmd_2.92.jar | awk '{print $1}' | head -n 1)
kill -9 $pid
