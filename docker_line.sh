#!/usr/bin/env bash
docker build -t waynedd/cithub-test-casa:1.0 .
docker run -d -p 8888:5000 --name cithub-test-casa waynedd/cithub-test-casa:1.0
