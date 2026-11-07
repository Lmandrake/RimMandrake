#!/usr/bin/env python3
"""selftest_gss_shock_outlives_wire_binding.py: the live binding of GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE, offline.

Run 2026-11-06T15:01Z measured nothing: no site line made a map, so AerialProbe (serviced only when Find.CurrentMap is its map)
timed out, and the line exited 1, which reads as the mod's FAIL. This test reads the committed line and RUNS it, with a stub in
place of the game script, so each way the live run can end must give its own exit: 0 M20e PASS, 1 M20e FAIL, 2 UNMEASURED.

Section 5 proves this test can go red: each mutant of the binding or the verdict script, the pre-fix line among them, must fail
it. BINDING_FILE / VERDICT_FILE point a nested run at a mutant. Exit 0 = all pass.
"""
import json
import os
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

ITEM = "GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE"
REAL_BINDING = os.path.join(REPO, "infrastructure", "state", "live_proofs", ITEM + ".txt")
REAL_VERDICT = os.path.join(HERE, "prove_shock_outlives_wire_verdict.py")
BINDING = os.environ.get("BINDING_FILE") or REAL_BINDING
VERDICT = os.environ.get("VERDICT_FILE") or REAL_VERDICT
ROW = "M20e_shock_cells_die_with_wire"
GAME = "python.exe src/RimMandrake/GimmeSomeSlack/validation_aerial.py"
VERDICT_REL = "src/RimMandrake/GimmeSomeSlack/prove_shock_outlives_wire_verdict.py"
WSL_DIR = "/mnt/d/ClaudeWork/rimmandrake/scratch/gss_shock_outlives_wire"
WIN_DIR = "D:/ClaudeWork/rimmandrake/scratch/gss_shock_outlives_wire"
FAILS = []


def check(name, ok, why=""):
    print(("PASS  " if ok else "FAIL  ") + name + (("  [%s]" % why) if why and not ok else ""))
    if not ok:
        FAILS.append(name)


with open(BINDING, encoding="utf-8") as f:
    text = f.read()
proof = RR.proof_lines(text).get("A1") or ""
with open(VERDICT, encoding="utf-8") as f:
    verdict_src = f.read()

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
check("1 the proof runs --flips and ends on the verdict script", (GAME + " --flips") in proof and VERDICT_REL in proof.rsplit(";", 1)[-1])
check("1 --out and the verdict read the same file",
      ("--out " + WIN_DIR + "/flips.json") in proof and proof.endswith(VERDICT_REL + " " + WSL_DIR + "/flips.json"))
with open(os.path.join(os.path.dirname(REAL_BINDING), ITEM + ".criteria"), encoding="utf-8") as f:
    check("1 the criterion names the row", ROW in f.read())
check("1 the verdict script reads that row", ('ROW = "%s"' % ROW) in verdict_src)

STUB = r'''
import json, os, sys
mode = os.environ["STUB_MODE"]
out = sys.argv[sys.argv.index("--out") + 1]
if mode == "crash":
    sys.exit(1)
if mode == "aborted":
    rows, extra = [{"id": "A_probe_channel", "status": "FAIL", "class": "HARNESS", "detail": {}}], {"aborted": "aerial probe dead"}
elif mode == "other_rows":
    rows, extra = [{"id": "M20a_x", "status": "PASS"}], {}
elif mode == "scene_failed":
    rows, extra = [{"id": "M20_flip_scene_built", "status": "FAIL", "class": "SITE", "detail": {}}], {}
else:
    rows, extra = [{"id": "M20e_shock_cells_die_with_wire", "status": mode, "class": "MOD", "detail": {"tip": [1, 2]}}], {}
text = json.dumps(dict({"rows": rows}, **extra))
if mode == "truncated":
    text = "{truncated"
elif mode == "truncated_brace":                    # cut inside a row: ends in } and is still no JSON
    text = '{"rows": [{"id": "M20a_x", "status": "PASS"}'
elif mode == "not_a_dict":
    text = "[1]"
with open(out, "w", encoding="utf-8") as f:        # as validation_aerial does: a missing folder is its crash
    f.write(text)
'''


def run_line(tmp, mode):
    """The committed line with the game script stubbed, the scratch folder under tmp and the verdict script absolute."""
    run_dir = os.path.join(tmp, "run")
    cmd = (proof.replace(GAME, "python3 " + shlex.quote(os.path.join(tmp, "stub.py")))
           .replace(VERDICT_REL, shlex.quote(VERDICT)).replace(WSL_DIR, run_dir).replace(WIN_DIR, run_dir))
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


GREEN = {"rows": [{"id": ROW, "status": "PASS", "class": "MOD", "detail": {}}]}

# 2. every ending of the run, on a machine where the output folder has never existed
if proof:
    rc, out = scene("PASS")
    check("2 a PASS row in a folder that did not exist reads exit 0", rc == 0, "rc=%s %s" % (rc, out[-200:]))
    check("2 the lane reads a PASS as the last verdict line", RL.VERDICT_LINE.match(out.splitlines()[-1] if out.strip() else "") is not None, out[-200:])
    rc, out = scene("FAIL")
    check("2 a FAIL row reads exit 1", rc == 1, "rc=%s %s" % (rc, out[-200:]))
    check("2 the lane reads the FAIL as charged to the mod", RL.MOD_ROW.match(out.splitlines()[-1] if out.strip() else "") is not None, out[-200:])
    for mode, label in (("UNMEASURED", "an UNMEASURED row"), ("aborted", "a dead probe channel (15:01Z, no map)"),
                        ("other_rows", "a run without the row"), ("scene_failed", "a scene that never built"),
                        ("crash", "a script that wrote nothing"), ("truncated", "a half-written JSON"),
                        ("truncated_brace", "a half-written JSON ending in a brace"), ("not_a_dict", "a JSON that is no result")):
        rc, out = scene(mode)
        check("2 %s reads exit 2 with an UNMEASURED line" % label, rc == 2 and says_unmeasured(out), "rc=%s %s" % (rc, out[-200:]))

    # 3. an earlier green run is not this run's verdict
    rc, out = scene("crash", earlier=GREEN)
    check("3 a crash after an earlier PASS is not a PASS", rc == 2 and says_unmeasured(out), "rc=%s %s" % (rc, out[-200:]))

# 4. the verdict step alone: an old file is no file, even if nothing removed it
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, "flips.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(GREEN, f)
    old = time.time() - 3600
    os.utime(p, (old, old))
    r = subprocess.run([sys.executable, VERDICT, p], capture_output=True, text=True, timeout=60)
    check("4 a JSON an hour old reads exit 2", r.returncode == 2, "rc=%s" % r.returncode)

# 5. the test goes red when the binding or the verdict breaks (top-level run only)
PRE_FIX = """live-mods: GimmeSomeSlack
live-proof A1: python.exe src/RimMandrake/GimmeSomeSlack/validation_aerial.py --flips --out D:/ClaudeWork/rimmandrake/scratch/gss_shock_outlives_wire/flips.json < /dev/null; python3 -c "import json,sys,os,time; p='/mnt/d/ClaudeWork/rimmandrake/scratch/gss_shock_outlives_wire/flips.json'; ok=os.path.exists(p) and time.time()-os.path.getmtime(p)<1800; r=[x for x in (json.load(open(p))['rows'] if ok else []) if x.get('id')=='M20e_shock_cells_die_with_wire']; print(r[0] if r else 'M20e row missing'); sys.exit(0 if r and r[0].get('status')=='PASS' else 1)"
"""


def drop(s, needle):
    assert needle in s, needle
    return s.replace(needle, "")


def swap(s, a, b):
    assert a in s, a
    return s.replace(a, b)


if not os.environ.get("BINDING_FILE") and not os.environ.get("VERDICT_FILE"):
    site_line = next(x for x in text.splitlines(True) if x.startswith("live-site A1:"))
    bindings = {
        "the pre-fix line": PRE_FIX,
        "no site line (the 15:01Z run)": drop(text, site_line),
        "a site with no map": swap(text, "live_site.py --game", "live_site.py --menu-dwell 20"),
        "no mkdir: the folder may not exist": swap(text, "mkdir -p %s && " % WSL_DIR, ""),
        "no removal of the old JSON": swap(text, " && rm -f %s/flips.json" % WSL_DIR, ""),
        "--out and the verdict on different files": swap(text, "--out %s/flips.json" % WIN_DIR, "--out %s/other.json" % WIN_DIR),
        "--flips dropped": swap(text, "validation_aerial.py --flips", "validation_aerial.py --live"),
    }
    verdicts = {
        "an unmeasured run exits 1": swap(verdict_src, "    return 2\n", "    return 1\n"),
        "a FAIL row exits 0": swap(verdict_src, 'return 0 if status == "PASS" else 1', "return 0"),
        "another row's verdict": swap(verdict_src, 'ROW = "%s"' % ROW, 'ROW = "M20a_x"'),
        "any status passes": swap(verdict_src, 'if status not in ("PASS", "FAIL"):', "if False:"),
        "a parse error is not caught": swap(verdict_src, "except (OSError, ValueError) as ex:", "except OSError as ex:"),
        "no freshness check": swap(verdict_src, "if age >= FRESH_S:", "if False:"),
    }
    with tempfile.TemporaryDirectory() as tmp:
        for kind, cases, key in (("binding", bindings, "BINDING_FILE"), ("verdict", verdicts, "VERDICT_FILE")):
            for label, body in cases.items():
                mp = os.path.join(tmp, "mutant.txt" if key == "BINDING_FILE" else "mutant.py")
                with open(mp, "w", encoding="utf-8") as f:
                    f.write(body)
                r = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True, text=True, timeout=120,
                                   env=dict(os.environ, **{key: mp}))
                red = [x for x in r.stdout.splitlines() if x.startswith("FAIL  ")]
                check("5 mutant (%s): %s goes red" % (kind, label), r.returncode == 1 and bool(red),
                      "rc=%s %s" % (r.returncode, (r.stderr or "")[-200:]))
                print("      red by: " + (red[0][6:90] if red else "nothing"))

print("\nALL PASS" if not FAILS else "\n%d FAILED: %s" % (len(FAILS), FAILS))
sys.exit(1 if FAILS else 0)
