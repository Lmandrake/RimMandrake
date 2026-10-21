#!/usr/bin/env python3
"""flier_guard: each bbox-registering tool refuses a flier flip-book input by name; a non-flier input still passes."""
import json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
sys.path.insert(0, str(HERE))
import flier_guard as FG

assert FG.is_flier("Textures/Screecher_Flying_3_east.png") and FG.is_flier("RSW/Fauna/Strill/Strill_Flying_")
assert not FG.is_flier("Textures/Screecher_east.png") and not FG.is_flier(None)

def run(script, *args):
    r = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr

FL = "Mod/Textures/Strill_Flying_2_south.png"
OK = "Mod/Textures/Strill_south.png"
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    rows = td / "rows.json"
    rows.write_text(json.dumps([{"texPath": "Mod/Strill/Strill_Flying_"}]))
    cases = [
        ("facing_regen.py", HERE / "facing_regen.py", ["lint", "--row", "Strill_Flying_", "--out", str(td / "o"), "--rows", str(rows)]),
        ("facing_scale_lint.py reseat", HERE / "facing_scale_lint.py", ["reseat", FL, "--out", str(td / "m")]),
        ("facing_scale_lint.py fix", HERE / "facing_scale_lint.py", ["fix", "--json", str(rows), "--defs", "X", "--out", str(td / "m"), "--dry-run"]),
        ("facing_set_audit.py", UTILS / "artpipe" / "facing_set_audit.py", [FL, "Mod/Textures/Strill_Flying_2_east.png"]),
        ("head_facing_fix.py", HERE / "head_facing_fix.py", ["shift", FL, str(td / "o.png"), "--dy", "1"]),
        ("fit_head_canvas.py fit", HERE / "fit_head_canvas.py", ["fit", "--stem", "Strill_Flying_", "--out", str(td / "o"), FL, FL, FL]),
    ]
    for name, script, args in cases:
        rc, out = run(script, *args)
        assert rc != 0 and "REFUSED" in out and "flyer_lock" in out and "flier_frame_registration_audit" in out, (name, rc, out[-300:])
    # non-flier passes the guard (head_facing_fix reaches its own file check, not our refusal)
    rc, out = run(HERE / "head_facing_fix.py", "shift", OK, str(td / "o.png"), "--dy", "1")
    assert "REFUSED: head_facing_fix.py registers" not in out, out[-300:]
    rc, out = run(HERE / "head_facing_fix.py", "mask", OK, str(td / "o.png"))
    assert "flip-book" not in out, out[-300:]
    rc, out = run(HERE / "facing_regen.py", "lint", "--row", "Strill", "--out", str(td / "o2"), "--rows", str(rows))
    assert "flip-book" not in out, out[-300:]
print("selftest_flier_guard OK")
