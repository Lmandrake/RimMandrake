#!/usr/bin/env bash
# usage: ek_rb.sh TOOL 'JSON'   -> a bridge call on SteveDesktop's game (runner clone, Windows python)
T=$1; J=${2:-{\}}
timeout ${RB_TIMEOUT:-300} ssh -o BatchMode=yes mandrake@stevedesktop-wsl "cd ~/rm/runner && export RM_HOST_GUARD_GEN=2026 && python.exe src/RimMandrake/Utils/rimbridge_client.py --yes-i-know-this-is-live --call $T --json '$J'" 2>&1
