#!/bin/bash

# add extra sleep, because first results are 0
sleep 30

max_attempts=60
current_attempt=0
while [ $current_attempt -lt $max_attempts ]; do
    result=$(sleep 10 && pgrep -c -f "/var/lib/cloud/instance/scripts/part-001")
    echo "$result"
    if [ "$result" -eq 0 ] || [ $current_attempt -eq $max_attempts ]; then
        break
    else
        ((current_attempt++))
    fi
done
