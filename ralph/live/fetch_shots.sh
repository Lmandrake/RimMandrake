#!/bin/bash
# Bring every shot with this prefix back from Steve's shots folder, in one tar. bash ralph/live/fetch_shots.sh PREFIX
P=$1
ralph/steve.sh run "cd /mnt/d/ClaudeWork/rimmandrake/ralph_gss/shots && tar cf /mnt/d/ClaudeWork/rimmandrake/ralph_gss/$P.tar $P*" >/dev/null 2>&1
T=$(mktemp -d)
ralph/steve.sh fetch "D:\\ClaudeWork\\rimmandrake\\ralph_gss\\$P.tar" "$T" >/dev/null 2>&1
tar xf "$T/$P.tar" -C /mnt/d/ClaudeWork/rimmandrake/ralph_gss/shots/ && ls /mnt/d/ClaudeWork/rimmandrake/ralph_gss/shots/ | grep -c "^$P"
rm -rf "$T"
