#!/bin/bash
# one colony per look on a fresh generated map: played, then shot with colonists under a span, then blasted and shot again. Run on Steve from the clone.
TAG=$1; shift
for L in "$@"; do
  echo "== $L"
  python.exe ralph/live/lived_in.py build --look $L --fresh-map 2>&1 | grep -a -E "^map|NOTES|Traceback" | cut -c1-200
  python.exe ralph/live/lived_in.py play --ticks 2000 2>&1 | tail -n 1 | cut -c1-120
  python.exe ralph/live/lived_in.py spanpawn 2>&1 | tail -n 1 | cut -c1-120
  python.exe ralph/live/lived_in.py shots $TAG --frames spanpawn,house,work,yard 2>&1 | tail -n 1 | cut -c1-160
  python.exe ralph/live/lived_in.py blast 2>&1 | tail -n 1 | cut -c1-200
  python.exe ralph/live/lived_in.py shots $TAG --frames all,cutspan 2>&1 | tail -n 1 | cut -c1-160
  python.exe ralph/live/lived_probe.py 2>&1 | head -n 1 | cut -c1-200
done
