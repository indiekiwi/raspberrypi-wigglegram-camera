#!/bin/bash

BASE_DIR=$(dirname "$(realpath "$0")")/..

CONFIG_FILE="$BASE_DIR/resources/config.env"
IMAGE_DIR="$BASE_DIR/images"

if [ -f "$CONFIG_FILE" ]; then
    PHONE_ADDRESS=$(grep -oP '^PHONE_MAC_ADDRESS=\K.*' "$CONFIG_FILE")
else
    echo "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

if [ ! -d "$IMAGE_DIR" ]; then
    echo "Image directory not found: $IMAGE_DIR"
    exit 1
fi

obexftp --nopath --noconn --uuid none --bluetooth "$PHONE_ADDRESS" --channel 12 --put "$IMAGE_DIR/1733738792_merged.jpg"
