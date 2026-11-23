#!/bin/bash
# srun.sh <tag> <trench.py args...> : one trench.py run on Steve1 under the sitting's guard; copies the json back, prints rd.py
S=/mnt/d/ClaudeWork/rimmandrake/testpilot_pit_capture_faults; tag=$1; shift
ssh -o BatchMode=yes -o ConnectTimeout=8 -o LogLevel=ERROR -o ServerAliveInterval=15 mandrake@stevedesktop-wsl "export RIMFLOW_SEAT=BENCH RM_HOST_GUARD_GEN=${GEN:-2429} WSLENV=\$WSLENV:RM_HOST_GUARD_GEN:RIMFLOW_SEAT; cd ~/rm/runner; t0=\$(date +%s); timeout 400 python.exe -u \"\$(wslpath -w ~/tp_out/trench.py)\" \"\$(wslpath -w ~/tp_out/$tag.json)\" $* > ~/tp_out/$tag.log 2>&1; echo $tag rc=\$? secs=\$(( \$(date +%s) - t0 ))"
scp -q -o BatchMode=yes mandrake@stevedesktop-wsl:tp_out/$tag.json $S/$tag.json && python3 $S/rd.py $S/$tag.json ${RDN:-0}
