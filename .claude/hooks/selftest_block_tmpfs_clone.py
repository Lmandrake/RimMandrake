#!/usr/bin/env python3
"""Selftest for block_tmpfs_clone.py (invokes the hook script with PreToolUse JSON on stdin)."""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("block_tmpfs_clone.py")
URL = "git@github.com:Lmandrake/RimMandrake.git"
CWD = "/home/mandrake/rm/bench"

CASES = [  # (command, cwd, want_refused)
    ("git clone . /tmp/x", CWD, True),
    (f"cd /tmp && git clone {URL}", CWD, True),
    (f"git clone --reference /home/mandrake/rm/bench {URL} /dev/shm/y", CWD, True),
    ("cp -a /home/mandrake/rm/bench /tmp/z", CWD, True),
    ("rsync -a /home/mandrake/rm/bench/ /tmp/claude-1000/r/", CWD, True),
    (f"git clone {URL} $TMPDIR/q", CWD, True),
    (f"d=$(mktemp -d) && git clone {URL} $d/c", CWD, True),
    ("git worktree add /tmp/claude-1000/merge-a origin/main", CWD, True),
    (f"git init /tmp/i && git -C /tmp/i fetch {URL}", CWD, True),
    (f"git clone {URL}", "/tmp", True),
    (f"git clone {URL} /home/mandrake/rm/scratch/BENCH/a", CWD, False),
    ("echo hi > /tmp/f", CWD, False),
    ("python3 x.py --out /tmp/out.json", CWD, False),
    ("mktemp -d", CWD, False),
    ("cp -r notes /tmp/notes", CWD, False),
    ("cp a.txt /tmp/a.txt", CWD, False),
    ("echo git clone x /tmp/x", CWD, False),
    ("git init /home/mandrake/rm/scratch/BENCH/n", CWD, False),
]

fails = 0
for cmd, cwd, want in CASES:
    p = subprocess.run([sys.executable, str(HOOK)], capture_output=True, text=True,
                       input=json.dumps({"tool_name": "Bash", "cwd": cwd, "tool_input": {"command": cmd}}))
    refused = p.returncode == 2 and "RAM disk" in p.stderr
    ok = refused == want and p.returncode in (0, 2)
    fails += not ok
    print("PASS" if ok else "FAIL", "refuse" if want else "allow ", cmd[:70])
print(f"{len(CASES) - fails}/{len(CASES)} passed")
sys.exit(1 if fails else 0)
