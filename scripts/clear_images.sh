#!/bin/bash

# Rather than accidentally running rm * in the wrong directory, this script helps reset the image directory by prompting the number of images to be deleted.

BASE_DIR=$(dirname "$(realpath "$0")")/..

if [ ! -d "$BASE_DIR/images" ]; then
  echo "Error: no images dir"
  exit 1
fi

image_count=$(ls "$BASE_DIR/images"/*.jpg 2>/dev/null | wc -l)
if [ "$image_count" -eq 0 ]; then
  echo "Error: no jpg in images dir"
  exit 0
fi

echo "There are $image_count images in the 'images/' directory."
read -p "Are you sure you want to delete them? (Y/N): " confirmation

if [[ "$confirmation" == [Yy] ]]; then
  rm -f "$BASE_DIR/images"/*.jpg
  echo "Images deleted."
else
  echo "Cancelled."
fi
