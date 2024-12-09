#!/bin/bash

BASE_DIR=$(dirname "$(realpath "$0")")/..
PHONE_MAC_ADDRESS=$(grep "PHONE_MAC_ADDRESS" $BASE_DIR/resources/config.env | cut -d'=' -f2)

{
    echo "power on"
    sleep 1
    echo "agent on"
    sleep 1
    echo "default-agent"
    sleep 1
    echo "pair $PHONE_MAC_ADDRESS"
    sleep 1
    echo "trust $PHONE_MAC_ADDRESS"
    sleep 1
    echo "connect $PHONE_MAC_ADDRESS"
    sleep 1
    echo "quit"
} | bluetoothctl
