#!/usr/bin/env python3
"""Every `live-mods:` / `live-deploy:` name in infrastructure/state/live_proofs/*.txt resolves the way modlist_swap
will read it, and a dotted mod FOLDER is enabled as a folder, never as a packageId.

OPS_CHURN_DIAGNOSE_TITANIC_WYZE_DMPL (2026-11-05): TITANIC_BODYSIZE_TEST_RACE_1 landed and passed offline, then sat held in
the game phase because a rider of the same load (WATER_DEPTH_RESKIN_HE_LOOKS_FIRST) wrote `live-mods: RimMandrake.FlowWorks`:
the dot made it packageId 'rimmandrake.flowworks' (installed nowhere) and modlist_swap refused the whole batch. The
composed game folder RimMandrake.Biomes, named on nine lines, carries a dot too.
Offline and deterministic: the repo's mod folders and compose manifest only; no game folder is read."""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import relentless_live_round as R  # noqa: E402
import modlist_swap as M  # noqa: E402
import deploy_custom_mods as D  # noqa: E402

fails = []
n_ok = 0


def ok(cond, what):
    global n_ok
    if cond:
        n_ok += 1
    else:
        fails.append(what)


dirs = set(D.mod_dirs())
fold = D.folded()
targets = {t for t, _k in fold.values()}
ours = dirs | set(fold) | targets
low = {d.lower() for d in dirs | set(fold)}
import xml.etree.ElementTree as ET  # noqa: E402
pids = set()        # the packageIds our own mods ship: a line may name one (it is loaded, not planned)
for _n, _d in list(D.mod_dirs().items()):
    try:
        pids.add((ET.parse(os.path.join(_d, "About", "About.xml")).getroot().findtext("packageId") or "").strip().lower())
    except (OSError, ET.ParseError):
        pass
ok(len(dirs) > 20 and "FlowWorks" in dirs and "HugeThings" in dirs, "sanity: the repo's mod folders are visible (%d)" % len(dirs))
ok("RimMandrake.Biomes" in targets, "sanity: the composed target RimMandrake.Biomes is visible: %s" % sorted(targets))

# 1. the instrument sees the defect it guards: the 2026-11-05 spelling is refused, the right ones pass
def verdict(name):
    """-> None when the name is fine, else why it is not."""
    if "." not in name:
        return None if name in ours else "%s is no repo mod folder" % name
    if name in targets or name.lower() in pids:
        return None
    tail = name.rsplit(".", 1)[-1].lower()
    if tail in low:
        return "%s reads as a packageId; the repo mod folder is %s" % (name, [d for d in dirs | set(fold) if d.lower() == tail][0])
    return None


ok(verdict("RimMandrake.FlowWorks") is not None, "lint refuses RimMandrake.FlowWorks")
ok(verdict("FlowWorks") is None, "lint passes FlowWorks")
ok(verdict("RimMandrake.Biomes") is None, "lint passes the composed RimMandrake.Biomes")
ok(verdict("neku.largepawns") is None, "lint passes a workshop packageId")
ok(verdict("mandrake.rm.flowworks") is None and "mandrake.rm.flowworks" in pids, "lint passes our own packageId")
ok(verdict("NoSuchModHere") is not None, "lint refuses an unknown folder")

# 2. every live_proofs line in the repo
files = sorted(glob.glob(os.path.join(REPO, "infrastructure", "state", "live_proofs", "*.txt")))
ok(len(files) > 20, "sanity: live_proofs files visible (%d)" % len(files))
seen = 0
for f in files:
    text = open(f, encoding="utf-8").read()
    for name in R.live_mods(text) + [m for m in R.live_mods(text, R.LIVE_DEPLOY)]:
        seen += 1
        v = verdict(name)
        ok(v is None, "%s: %s" % (os.path.basename(f), v))
ok(seen > 20, "sanity: live-mods names read (%d)" % seen)

# 3. modlist_swap splits a dotted folder as a folder
folder = lambda n: n in ours  # noqa: E731
p, d = M.split_names(["RimMandrake.Biomes", "neku.largepawns", "FlowWorks", "Ferny.WorldBuilder"], folder)
ok(p == ["neku.largepawns", "ferny.worldbuilder"], "packages split: %s" % p)
ok(d == ["RimMandrake.Biomes", "FlowWorks"], "folders split: %s" % d)
ok(M.split_names(["RimMandrake.Biomes"])[1] == ["RimMandrake.Biomes"], "default is_mod_folder knows the composed target")

for f in fails:
    print("FAIL", f)
print("%d/%d PASS" % (n_ok, n_ok + len(fails)))
sys.exit(1 if fails else 0)
