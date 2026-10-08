#!/bin/sh
grep -E "^    \{" "$1" | python3 -c "
import sys,json,re
for l in sys.stdin:
    m=re.search(r'\"name\": \"([^\"]*)\".*?\"verdict\": \"(\w+)\", \"detail\": \"((?:[^\"\\\\]|\\\\.)*)\"',l)
    if m and m.group(2)!='PASS': print(m.group(2),m.group(1),m.group(3)[:300])
"; grep ALL_GREEN "$1"
