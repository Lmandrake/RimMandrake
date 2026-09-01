#!/usr/bin/env bash
for i in $(seq 1 40); do
  OUT=$(python3 src/RimMandrake/rimflow/cli.py bridge take --seat BENCH 2>&1 | tail -1)
  echo "$OUT" | grep -q "bridge taken" && { echo "ACQUIRED at $(date +%H:%M): $OUT"; exit 0; }
  sleep 180
done
echo "bridge still held after 2h"; exit 1
