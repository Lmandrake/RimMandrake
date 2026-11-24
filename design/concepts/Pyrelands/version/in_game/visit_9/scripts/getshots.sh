# usage: getshots.sh <log> : copies each "SHOT name (..) path" to Transient/pv9/close/<name>.png
mkdir -p Transient/pv9/close
grep '^SHOT' $1 | while read -r a n rest; do p=$(echo "$rest" | sed 's/.*) //' | tr -d '\r'); u=$(wslpath -u "$p"); cp "$u" Transient/pv9/close/$n.png; done; ls Transient/pv9/close
