#!/usr/bin/env python3
"""Repack skill folders into installable .skill archives.

🔑 The FOLDER is what git tracks; the .skill ZIP is what actually gets installed
in Claude Code. Editing the folder alone leaves anyone who installs from the
archive with the old text. .skill files are gitignored (derived), so this is
safe to re-run any time.

    python3 skills/repack.py                 # every skill folder
    python3 skills/repack.py rimbridge ...   # named ones
"""
import os, sys, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
names = sys.argv[1:] or sorted(
    d for d in os.listdir(ROOT)
    if os.path.isdir(os.path.join(ROOT, d)) and os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))

for n in names:
    src = os.path.join(ROOT, n)
    out = os.path.join(ROOT, n + ".skill")
    files = []
    for r, _, fs in os.walk(src):
        if os.sep + ".git" in r:
            continue
        for f in fs:
            if f.endswith((".pyc",)):
                continue
            files.append(os.path.relpath(os.path.join(r, f), ROOT))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(os.path.join(ROOT, p), p)
    print("%-30s %3d files -> %s" % (n, len(files), os.path.basename(out)))
