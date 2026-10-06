#!/usr/bin/env python3
"""Selftest for block_hand_edited_sheet.py."""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("block_hand_edited_sheet.py")
S = "Transient/biome_ffar/abyss_sheet_2026-10-04.html"
CASES = [
    ({"tool_name": "Write", "tool_input": {"file_path": "/home/mandrake/rm/bench/" + S, "content": "x"}}, True),
    ({"tool_name": "Edit", "tool_input": {"file_path": "/home/mandrake/rm/bench/" + S}}, True),
    ({"tool_name": "Write", "tool_input": {"file_path": "/home/mandrake/rm/bench/Transient/biome_ffar/notes.md"}}, False),
    ({"tool_name": "Write", "tool_input": {"file_path": "/home/mandrake/rm/bench/Transient/biome_ffar/abyss_sheet_2026-10-04.decisions.json"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": f"sed -i 's/a/b/' {S}"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": f"echo hi > {S}"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": f"python3 -c \"open('{S}','w').write('x')\""}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": f"cp /tmp/x.html {S}"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": f"rm {S}"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": f"grep -c scale_ {S}"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": f"git commit {S} -F -"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": f"python3 src/RimMandrake/Utils/art/scaled_review_gate.py check {S} --stamp"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": "python3 src/RimMandrake/Utils/art/art_sheet.py --biome RM_Abyss > Transient/biome_ffar/abyss_sheet_2026-10-04.html"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": "python3 ~/.claude/skills/review-sheets/assets/serve_sheet.py --no-open --sheet x_sheet_2026-10-05.html"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": "python3 ~/.claude/skills/review-sheets/assets/serve_sheet.py --decisions d.json --status"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": "python3 src/RimMandrake/Utils/art/serve_gated.py --no-open --sheet x_sheet_2026-10-05.html"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": "ls Transient/biome_ffar"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": f"cd /home/mandrake/rm/bench && md5sum {S} > /tmp/m"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": f"cd /home/mandrake/rm/bench && rm {S}"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": f"cat x | tee {S}"}}, True),
]
fails = 0
for payload, want in CASES:
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)
    denied = '"deny"' in p.stdout
    ok = p.returncode == 0 and denied == want
    fails += not ok
    print(("PASS" if ok else "FAIL"), "deny" if want else "allow", json.dumps(payload["tool_input"])[:90])
p = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True)
ok = p.returncode == 0 and p.stdout == ""
fails += not ok
print(("PASS" if ok else "FAIL"), "unreadable input fails open")
n = len(CASES) + 1
print(f"{n - fails}/{n} passed")
sys.exit(1 if fails else 0)
