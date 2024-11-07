#!/bin/bash

timestamp=$(date +%s)
start_time=$(date +%s%3N)
start_time_pretty=$(date +"%T.%N")
devices=("/dev/video0" "/dev/video2" "/dev/video4" "/dev/video6")
fragments=("A" "B" "C" "D")

# Capture images in parallel
for i in "${!devices[@]}"; do
    ffmpeg -loglevel error -f video4linux2 -i "${devices[$i]}" -frames:v 1 -s 640x480 "images/${timestamp}_${fragments[$i]}.jpg" &
    sleep 0.1
done

# Wait for all background processes to finish
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

# Success/Error Message
if [ "$captured_count" -eq "$expected_count" ]; then
    printf "Success!\n"
else
    printf "Error: Captured %d instead of %d\n" "$captured_count" "$expected_count"
fi
echo ""
