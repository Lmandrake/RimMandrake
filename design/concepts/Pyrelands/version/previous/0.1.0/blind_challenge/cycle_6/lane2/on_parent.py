#!/usr/bin/env python3
"""on_parent.py <sha> <file>[,<file>] -- CMD: put those files as they stood at <sha> in the tree, run CMD, restore byte for byte; exit = CMD's rc."""
import signal, subprocess, sys
sha, files, cmd = sys.argv[1], sys.argv[2].split(","), sys.argv[sys.argv.index("--") + 1:]
keep = {f: open(f, "rb").read() for f in files}
def back(*_):
    for f, b in keep.items(): open(f, "wb").write(b)
    if _: sys.exit(3)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP): signal.signal(s, back)
try:
    for f in files: open(f, "wb").write(subprocess.run(["git", "show", sha + ":" + f], capture_output=True, check=True).stdout)
    rc = subprocess.run(cmd).returncode
finally: back()
sys.exit(rc)
