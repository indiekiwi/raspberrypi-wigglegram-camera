#!/bin/bash

# This command gives info about attached webcams assuming they're named with a case insensitive "cam" string
v4l2-ctl --list-devices | grep -i -A 1 "cam"
