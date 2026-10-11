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
# content-based (owner card 2026-10-11): a hand-written review sheet of game art is refused anywhere, decided by its pictures
import base64, tempfile  # noqa: E401,E402
from io import BytesIO  # noqa: E402
from PIL import Image  # noqa: E402
_td = Path(tempfile.mkdtemp())
_spr = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
_spr.paste((180, 120, 60, 255), (16, 16, 48, 48))
_spr.save(_td / "a1b2c3.png")                          # a content-hashed name: only the pixels say it is a sprite
Image.new("RGB", (64, 64), (90, 90, 90)).save(_td / "chart.png")
_art = '<html><head></head><body><script id="ITEMS" type="application/json">[{"id":"x","img":"a1b2c3.png"}]</script></body></html>'
_chart = _art.replace("a1b2c3.png", "chart.png")
_stamped = _td / "stamped.html"
_stamped.write_text('<html><head><meta name="scaled-review-gate" content="v1 sha256:00"></head><body></body></html>')
_old = _td / "handmade_art.html"
_old.write_text(_art)
CASES += [
    ({"tool_name": "Write", "tool_input": {"file_path": str(_td / "new_sheet.html"), "content": _art}}, True),
    ({"tool_name": "Write", "tool_input": {"file_path": str(_td / "new_sheet.html"),
                                           "content": _art.replace("<head>", '<head><meta name="sheet-kind" content="non-art">')}}, True),
    ({"tool_name": "Write", "tool_input": {"file_path": str(_td / "chart_sheet.html"), "content": _chart}}, False),
    ({"tool_name": "Write", "tool_input": {"file_path": str(_td / "page.html"), "content": "<p>no sheet</p>"}}, False),
    ({"tool_name": "Edit", "tool_input": {"file_path": str(_stamped)}}, True),
    ({"tool_name": "Edit", "tool_input": {"file_path": str(_old)}}, True),
    ({"tool_name": "Edit", "tool_input": {"file_path": str(_td / "missing.html")}}, False),
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
