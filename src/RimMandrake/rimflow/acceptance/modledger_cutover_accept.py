#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY (plan
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 4; spec §3.2, §3.8 step 4). Written by the filing seat;
the builder does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py ExplosiveKnockback GimmeSomeSlack FlowWorks

THE CONTRACT, per mod named. Each old hand-written store, `stage.json`, `journal.md` and `version/stage_record.json`
(relative to design/concepts/<Mod>/), is either
  (a) a generated view: a text file whose first line holds "modledger view, generated", or a JSON object with a
      top-level "_view" key, which `modledger.py lint --mod <Mod>` checks like the views under ledger/views/; or
  (b) gone from its place, with its last content kept read-only at archive_pre_ledger/<same relative path> (no write
      bit for anyone).
And no writer is left: every .py under src/RimMandrake/ (selftests, acceptance tests and modledger*.py excepted) that
names one of those three files AND writes a file (open(...,"w"/"a"), .write_text(, json.dump(, os.replace() must import
modledger. The mod's ledger lints clean against origin/main.
Exit 0 with "PASS n/n" only when all pass (expected 3 mods x 4 checks + 1 writer check = 13).
"""
import glob
import json
import os
import re
import stat
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import modledger as M                                            # noqa: E402

ROOT = M.REPO_ROOT
OLD = ("stage.json", "journal.md", os.path.join("version", "stage_record.json"))
res = []


def check(name, ok, detail=""):
    res.append(ok)
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))


def is_view(p):
    try:
        text = open(p, encoding="utf-8").read()
    except OSError:
        return False
    if p.endswith(".json"):
        try:
            return "_view" in json.loads(text)
        except ValueError:
            return False
    return "modledger view, generated" in text.split("\n", 1)[0]


def archived(c, rel):
    a = os.path.join(c, "archive_pre_ledger", rel)
    return os.path.exists(a) and not (os.stat(a).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


for mod in sys.argv[1:] or ["ExplosiveKnockback", "GimmeSomeSlack", "FlowWorks"]:
    c = os.path.join(ROOT, "design", "concepts", mod)
    for rel in OLD:
        p = os.path.join(c, rel)
        ok = is_view(p) or (not os.path.exists(p) and archived(c, rel))
        check("%s: %s is a generated view or archived read-only" % (mod, rel), ok,
              "still a hand-written file" if os.path.exists(p) else "gone, no read-only archive")
    findings, _ = M.lint(ROOT, mod, base="origin/main")
    check("%s: the mod ledger lints clean" % mod, bool(M.read(ROOT, mod)) and findings == [], findings[:3])
WRITE = re.compile(r"open\([^)]*['\"][wa]b?['\"]|\.write_text\(|json\.dump\(|os\.replace\(")
names = re.compile(r"stage_record\.json|journal\.md|['\"/]stage\.json")
left = []
for py in glob.glob(os.path.join(ROOT, "src", "RimMandrake", "**", "*.py"), recursive=True):
    b = os.path.basename(py)
    if b.startswith("selftest_") or b.startswith("modledger") or "/acceptance/" in py:
        continue
    try:
        s = open(py, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        continue
    if names.search(s) and WRITE.search(s) and not re.search(r"^\s*(import|from)\s+\S*modledger", s, re.M):
        left.append(os.path.relpath(py, ROOT))
check("no writer of the old stores is left outside modledger (%d candidates)" % len(left), not left, sorted(left)[:12])
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
