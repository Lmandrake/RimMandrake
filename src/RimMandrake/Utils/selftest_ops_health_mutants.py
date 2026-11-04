#!/usr/bin/env python3
"""Does selftest_ops_health.py go red when a clause of OPS_ERROR_BUDGET_DIAGNOSE_CIRG is broken? Each mutant is one edit to a
private copy of the code, rules or fixture; the proof must exit non-zero on it, with the real tree untouched. A mutant whose
text is gone from the source is itself a failure: the list went stale, and a stale mutant proves nothing."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OW, RU, HE, SF = "ops_watch.py", "ops_watch_rules.json", "ops_health.py", "testdata/ops_health_nightly_series.jsonl"
COPIED = (OW, RU, HE, "selftest_ops_health.py")
OLD_UNIT = "nightly reds not on the known-red list, and entries past their age"
PH = 'M(len(v["drifted"]), "SLIs whose point changed unit under them", said=", ".join(v["drifted"]))'
MUTANTS = [
    # GAP 1: the shipped rule's key or unit moves off what the collector emits
    (RU, '"unit": "%"', '"unit": "banana"', "rules: infra_share unit"),
    (RU, '"unit": "GB free on /tmp"', '"unit": "GB free on /nowhere"', "rules: tmp unit"),
    (RU, '"unit": "GB free on /"', '"unit": "GB free on /mnt/x"', "rules: root unit"),
    (RU, '"unit": "GB the pool holds (cap 70.0)"', '"unit": "GB the pool holds (cap 99)"', "rules: pool unit"),
    (RU, '"unit": "nightly reds no known-red entry parks"', '"unit": "nightly reds"', "rules: nightly_reds unit"),
    (RU, '"key": "disk.tmp_free_gb", "unit"', '"key": "disk.nope_free_gb", "unit"', "rules: tmp key"),
    (RU, '"key": "disk.pool_gb", "unit"', '"key": "disk.pool_nope", "unit"', "rules: pool key"),
    (RU, '"key": "relentless.live_measured_pct", "unit"', '"key": "relentless.nope_pct", "unit"', "rules: infra_share key"),
    (RU, '"key": "testing.nightly_unparked_reds", "unit"', '"key": "testing.nightly_news", "unit"', "rules: the blind key back"),
    # GAP 1: the collector moves off the shipped rule
    (OW, 'M(pct, "%", **got)', 'M(pct, "share", **got)', "collector: infra_share unit"),
    (OW, '"GB free on %s" % mnt', '"free GB %s" % mnt', "collector: free GB unit"),
    (OW, '"GB the pool holds (cap %s)" % pr["max_gb"]', '"GB in pool"', "collector: pool unit"),
    (OW, '"nightly reds no known-red entry parks"', '"nightly reds nothing parks"', "collector: unparked unit"),
    (OW, 'out["disk.%s_free_gb" % name] = M(', 'out["disk.%s_gone_gb" % name] = M(', "collector: free key"),
    (OW, 'pts["relentless.live_measured_pct"] = U(got, "%") if', 'pts["relentless.nope_pct"] = U(got, "%") if', "collector: infra_share key"),
    (OW, '    out.update(nightly_news(now, ctx))\n', '', "collector: c_testing stops calling nightly_news"),
    # GAP 2: publish_health
    (OW, PH, PH.replace('len(v["drifted"])', "0"), "publish_health: count 0"),
    (OW, PH, PH.replace('", ".join(v["drifted"])', '""'), "publish_health: names nobody"),
    (OW, PH, "M(0)", "publish_health: whole point zero"),
    (OW, '"health.drifted_slis": U(why),\n', "\n", "publish_health: failure branch loses the point"),
    (OW, '\n                "health.incident_slis": U(why)}', "}", "publish_health: failure branch loses the incident point"),
    (OW, '"health.spent_slis": U(why), ', "", "publish_health: failure branch loses the spent point"),
    # was: the record of what the old collector wrote
    (RU, '"unit": "%s"' % OLD_UNIT, '"unit": "a was nobody wrote"', "rules: was unit"),
    (RU, '"was": [', '"was_": [', "rules: was dropped"),
    (SF, OLD_UNIT, "a record edited to agree", "fixture: the old unit"),
    # the alarm
    (RU, '"tag": "SLI_DRIFT", "name": "OPS_SLI_DRIFT_DIAGNOSE"', '"tag": "SLI_DRIFT", "name": "OPS_SOMETHING_ELSE"', "rules: drift alarm name"),
    (RU, '{"key": "health.drifted_slis", "op": ">", "value": 0,', '{"key": "health.drifted_slis", "op": ">", "value": 9,', "rules: drift alarm line"),
]


def tree(root):
    """A copy of what the proof reads, the rest linked: the .git link keeps the object store in reach for its history check."""
    u = root / "src" / "RimMandrake" / "Utils"
    u.mkdir(parents=True)
    (root / ".git").symlink_to(REPO / ".git")
    (root / "src" / "RimMandrake" / "rimflow").symlink_to(HERE.parent / "rimflow")
    for e in HERE.iterdir():
        if e.name in COPIED:
            shutil.copy2(e, u / e.name)
        elif e.name == "testdata":
            (u / "testdata").mkdir()
            shutil.copy2(HERE / SF, u / SF)
        elif e.name != "__pycache__":
            (u / e.name).symlink_to(e)
    return u


def run(root, u):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(root), PYTHONPATH="")
    r = subprocess.run([sys.executable, str(u / "selftest_ops_health.py")], env=env, capture_output=True, text=True, errors="replace", timeout=120)
    return r.returncode, r.stdout + r.stderr


base = Path(tempfile.mkdtemp(prefix="ops_health_mut_"))
fails = []
try:
    u = tree(base / "clean")
    rc, out = run(base / "clean", u)
    if rc:
        fails.append("the clean copy is red: " + out[-300:])
    print(("PASS " if not rc else "FAIL ") + "the unmutated copy is green")
    for i, (f, old, new, name) in enumerate(MUTANTS):
        root = base / ("m%d" % i)
        u = tree(root)
        text = (u / f).read_text(encoding="utf-8")
        if old not in text:
            fails.append("%s: stale, text gone from %s" % (name, f))
            print("FAIL %s: text gone from %s" % (name, f))
            continue
        (u / f).write_text(text.replace(old, new), encoding="utf-8")
        rc, out = run(root, u)
        red = [x[5:80] for x in out.splitlines() if x.startswith("FAIL ")] or [out.strip().splitlines()[-1][:80] if out.strip() else "no output"]
        print(("PASS " if rc else "FAIL ") + "%s -> %s" % (name, "red: " + red[0] if rc else "STAYED GREEN"))
        if not rc:
            fails.append(name)
        shutil.rmtree(root, ignore_errors=True)
finally:
    shutil.rmtree(base, ignore_errors=True)
print("selftest_ops_health_mutants: " + ("PASS (%d mutants)" % len(MUTANTS) if not fails else "RED: " + "; ".join(fails)))
sys.exit(1 if fails else 0)
