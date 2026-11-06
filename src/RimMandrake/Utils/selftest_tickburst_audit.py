"""TICKBURST_PROVE_MANY_TICKS_ONE_FRAME acceptance 4 and 5 offline: the guard audit table covers G1-G11, each row with a
file:line and a sim or visual class; the *Update override census lists CompDissolutionEffect_Goodwill and _Pollution (the
probe that the census can see); the census script finds both again when the decompile is reachable; the continuous-
checkpoint bounds file parses and every rule compiles."""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = os.path.join(REPO, "design", "RimMandrake", "tickburst_2026-11-06")
DECOMP = os.environ.get("TICKBURST_DECOMP", "/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all")
fails = []


def check(ok, name, why=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        fails.append(name)


text = open(os.path.join(D, "guard_audit.md"), encoding="utf-8").read()
rows = [l for l in text.splitlines() if re.match(r"^\|\s*G\d+\s*\|", l)]
ids = [re.match(r"^\|\s*(G\d+)", l).group(1) for l in rows]
check(ids == ["G%d" % i for i in range(1, 12)], "audit_rows_g1_to_g11_in_order", str(ids))
for l in rows:
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    gid = cells[0]
    check(len(cells) == 6, "audit_%s_six_cells" % gid, str(len(cells)))
    if len(cells) != 6:
        continue
    check(re.search(r"[\w./-]+\.cs:\d+", cells[2]) is not None, "audit_%s_cites_file_line" % gid, cells[2][:80])
    check(cells[3] in ("sim", "visual"), "audit_%s_class_sim_or_visual" % gid, cells[3])
    check(bool(cells[5]), "audit_%s_has_check" % gid)
cen = json.load(open(os.path.join(D, "update_census.json"), encoding="utf-8"))
classes = {h.get("class") for h in cen.get("hits", [])}
check({"CompDissolutionEffect_Goodwill", "CompDissolutionEffect_Pollution"} <= classes, "census_sees_both_dissolution_classes")
check(cen.get("count") == len(cen.get("hits", [])), "census_count_matches_hits", str(cen.get("count")))
check("CompDissolutionEffect_Goodwill" in text and "CompDissolutionEffect_Pollution" in text, "audit_lists_both_dissolution")
if os.path.isdir(DECOMP):
    out = os.path.join(tempfile.mkdtemp(prefix="tb_census_"), "c.json")
    p = subprocess.run([sys.executable, os.path.join(HERE, "tickburst_guard_census.py"), "rw16=" + DECOMP, "--out", out],
                       capture_output=True, text=True, timeout=300)
    again = json.load(open(out)) if p.returncode == 0 and os.path.exists(out) else {"hits": []}
    got = {h.get("class") for h in again["hits"]}
    check({"CompDissolutionEffect_Goodwill", "CompDissolutionEffect_Pollution"} <= got, "census_rerun_on_decompile_sees_both",
          p.stderr[-300:])
else:
    print("skip census_rerun_on_decompile (no decompile at %s; the committed census was checked above)" % DECOMP)
b = json.load(open(os.path.join(D, "bounds.json"), encoding="utf-8"))
check(bool(b.get("continuous")), "bounds_has_continuous_rules")
try:
    for c in b["continuous"]:
        re.compile(c["key"])
        float(c.get("abs", 0)); float(c.get("rel", 0))
    for pat in b.get("ignore", []):
        re.compile(pat)
    check(True, "bounds_rules_compile")
except (re.error, KeyError, ValueError) as e:
    check(False, "bounds_rules_compile", str(e))
print("RESULT: %s" % ("PASS" if not fails else "FAIL %d" % len(fails)))
sys.exit(1 if fails else 0)
