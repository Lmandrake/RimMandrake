#!/usr/bin/env python3
"""selftest_gss_shock_still_bites_binding.py: the live binding of GSS_FALLEN_WIRE_FIX_SHOCK_STILL_BITES, offline.

Run 2026-11-06T15:04Z measured nothing: no site was prepared, so AerialProbe (serviced only when Find.CurrentMap is its map)
timed out, and the --out folder did not exist, so validation_aerial crashed writing its JSON. The line then exited 1, which
reads as the mod's FAIL. This test reads the committed line and RUNS it, with a stub in place of the game script, so each way
the live run can end must give its own exit: 0 M20e PASS, 1 M20e FAIL, 2 UNMEASURED (the proof-line protocol).

Also pinned: a crash after an earlier green run must not read that run's JSON as this run's PASS. Exit 0 = all pass.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))

import relentless_live as RL  # noqa: E402
import relentless_live_round as RR  # noqa: E402

ITEM = "GSS_FALLEN_WIRE_FIX_SHOCK_STILL_BITES"
BINDING = os.environ.get("BINDING_FILE") or os.path.join(REPO, "infrastructure", "state", "live_proofs", ITEM + ".txt")
ROW = "M20e_shock_cells_die_with_wire"
GAME = "python.exe src/RimMandrake/GimmeSomeSlack/validation_aerial.py"
WSL_DIR = "/mnt/d/ClaudeWork/rimmandrake/scratch/gss_shock_still_bites"
WIN_DIR = "D:/ClaudeWork/rimmandrake/scratch/gss_shock_still_bites"
FAILS = []


def check(name, ok, why=""):
    print(("PASS  " if ok else "FAIL  ") + name + (("  [%s]" % why) if why and not ok else ""))
    if not ok:
        FAILS.append(name)


with open(BINDING, encoding="utf-8") as f:
    text = f.read()
proof = RR.proof_lines(text).get("A1") or ""

# 1. the line is one the live lane will run, on a site that has a current map
check("1 the binding has a live-proof A1", bool(proof))
own_site = RR.proof_lines(text, RR.SITE_LINE).get("A1") or ""
check("1 A1 has its own live-site line (AerialProbe answers only on Find.CurrentMap)", bool(own_site))
check("1 the site asks for a game with a map", "--game" in own_site.split())
check("1 the site command is one the lane accepts", bool(own_site) and RL.refused_site(own_site) is None)
check("1 site_for hands the lane that line", RR.site_for(text, "A1") == own_site)
check("1 GimmeSomeSlack is the deployed mod", "GimmeSomeSlack" in " ".join(
    m.group("mods") for m in map(RR.LIVE_MODS.match, text.splitlines()) if m))
with open(os.path.join(REPO, "src", "RimMandrake", "rimflow", "relentless_rules.json"), encoding="utf-8") as f:
    rules = json.load(f)
refused = RL.refused_proof(RL.live_rules(rules), ITEM, "", proof)
check("1 the lane does not refuse the proof", refused is None, str(refused))
check("1 the proof names the validation script and reads row M20e", GAME in proof and ROW in proof)
check("1 --out and the verdict read the same file",
      (WIN_DIR + "/flips.json") in proof and (WSL_DIR + "/flips.json") in proof)
with open(BINDING[:-len(".txt")] + ".criteria", encoding="utf-8") as f:
    check("1 the criterion names the row", ROW in f.read())

STUB = r'''
import json, os, sys
mode = os.environ["STUB_MODE"]
out = sys.argv[sys.argv.index("--out") + 1]
if mode == "crash":
    sys.exit(1)
if mode == "aborted":
    rows, extra = [{"id": "A_probe_channel", "status": "FAIL", "cls": "HARNESS"}], {"aborted": "aerial probe dead"}
elif mode == "other_rows":
    rows, extra = [{"id": "M20a_x", "status": "PASS"}], {}
else:
    rows, extra = [{"id": "M20e_shock_cells_die_with_wire", "status": mode, "cls": "MOD"}], {}
with open(out, "w", encoding="utf-8") as f:        # as validation_aerial does: a missing folder is its crash
    f.write("{truncated" if mode == "truncated" else json.dumps(dict({"rows": rows}, **extra)))
'''


def run_line(tmp, mode, line=proof):
    """The committed line with the game script stubbed and the scratch folder under tmp."""
    run_dir = os.path.join(tmp, "run")
    cmd = line.replace(GAME, "python3 " + shlex.quote(os.path.join(tmp, "stub.py"))).replace(WSL_DIR, run_dir).replace(WIN_DIR, run_dir)
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=60, cwd=tmp,
                       env=dict(os.environ, STUB_MODE=mode))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def scene(mode, earlier=None):
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "stub.py"), "w", encoding="utf-8") as f:
            f.write(STUB)
        if earlier is not None:
            os.makedirs(os.path.join(tmp, "run"))
            with open(os.path.join(tmp, "run", "flips.json"), "w", encoding="utf-8") as f:
                json.dump(earlier, f)
        return run_line(tmp, mode)


def says_unmeasured(out):
    lines = [x for x in out.splitlines() if x.strip()]
    return bool(lines) and lines[-1].startswith("UNMEASURED: ")


# 2. every ending of the run, on a machine where the output folder has never existed
if proof:
    rc, out = scene("PASS")
    check("2 a PASS row in a folder that did not exist reads exit 0", rc == 0, "rc=%s %s" % (rc, out[-200:]))
    rc, out = scene("FAIL")
    check("2 a FAIL row reads exit 1", rc == 1, "rc=%s %s" % (rc, out[-200:]))
    for mode, label in (("UNMEASURED", "an UNMEASURED row"), ("aborted", "a dead probe channel (15:04Z, no map)"),
                        ("other_rows", "a run without the row"), ("crash", "a script that wrote nothing"),
                        ("truncated", "a half-written JSON")):
        rc, out = scene(mode)
        check("2 %s reads exit 2 with an UNMEASURED line" % label, rc == 2 and says_unmeasured(out),
              "rc=%s %s" % (rc, out[-200:]))

    # 3. an earlier green run is not this run's verdict
    green = {"rows": [{"id": ROW, "status": "PASS"}]}
    rc, out = scene("crash", earlier=green)
    check("3 a crash after an earlier PASS is not a PASS", rc == 2 and says_unmeasured(out), "rc=%s %s" % (rc, out[-200:]))

    # 4. the verdict step alone: an old file is no file, even if nothing removed it
    m = re.search(r'python3 -c ".*"\s*$', proof)
    check("4 the verdict is the line's last step", bool(m))
    if m:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "run"))
            p = os.path.join(tmp, "run", "flips.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(green, f)
            old = time.time() - 3600
            os.utime(p, (old, old))
            r = subprocess.run(["bash", "-c", m.group(0).replace(WSL_DIR, os.path.join(tmp, "run"))],
                               capture_output=True, text=True, timeout=60)
            check("4 a JSON an hour old reads exit 2", r.returncode == 2, "rc=%s" % r.returncode)

print("\nALL PASS" if not FAILS else "\n%d FAILED: %s" % (len(FAILS), FAILS))
sys.exit(1 if FAILS else 0)
