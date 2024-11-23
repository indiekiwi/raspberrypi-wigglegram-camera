#!/bin/bash

devices=("/dev/video0" "/dev/video2" "/dev/video4")
fragments=("A" "B" "C")

timestamp=$(date +%s)
start_time=$(date +%s%3N)
start_time_pretty=$(date +"%T.%N")

# Capture images in parallel
for i in "${!devices[@]}"; do
    ffmpeg -loglevel error -f video4linux2 -i "${devices[$i]}" -frames:v 1 -s 1920x1080 "images/${timestamp}_${fragments[$i]}.jpg" &
done
wait

# Calculate elapsed time
end_time=$(date +%s%3N)
elapsed=$((end_time - start_time))

# Count the captured images
captured_count=$(ls images/"${timestamp}"_* 2>/dev/null | wc -l)
expected_count=${#fragments[@]}

# Print the results
echo ""
printf "Start time:                %s\n" "$start_time_pretty"
ls -lh --time-style=full-iso images/"${timestamp}"_* | awk '{print "--", $9, $7}'
printf "Elapsed time:              %d ms\n" "$elapsed"

if [ "$captured_count" -ne "$expected_count" ]; then
    printf "Error: Captured %d instead of %d\n" "$captured_count" "$expected_count"
fi
echo ""
