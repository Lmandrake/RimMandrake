#!/usr/bin/env bash
for i in $(seq 1 90); do
  out=$(python.exe Transient/dwv_check_now.py 2>&1)
  if echo "$out" | grep -q '"success": true'; then
    echo "READY at $(date +%H:%M:%S): $out"
    exit 0
  fi
  sleep 20
done
echo "TIMEOUT after 30 min, last: $out"
exit 1
