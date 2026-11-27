#!/bin/bash
# Acceptance test for RIMMANDRAKE_HUSH_DIVERGING_ASKS_ON_PASSED_AND_HELD_MODS. Exit 0 = pass, 1 = fail, 2 = could not look.
# Usage: bash <this file>
# maturation_convergence.needs_lines() must raise a DIVERGING "Needs the Conductor" line only for a mod that is
# neither passed (stage_record.json stage "passed") nor held (src/RimMandrake/rimflow/mod_owner_hold.json), and must
# still raise it for an advancing mod whose stage reads DIVERGING. Cases, all on a temp copy of the concept layout:
#   held mod, DIVERGING at stage 3            -> no line
#   passed mod, DIVERGING at stage 3          -> no line
#   advancing mod, DIVERGING at stage 3       -> one line (the line must survive the fix)
#   advancing mod with no stage_record.json   -> one line (an unreadable stage never hides an ask)
#   empty concepts folder                     -> no line, no crash
# Also the live repo: no line names ExplosiveKnockback (passed 0.2.0), Cauldron or Graffiti (held).
cd "$(dirname "$0")/../../.." || exit 2
exec python3 -I - <<'PY'
import json, os, sys, shutil, tempfile
sys.path.insert(0, "src/RimMandrake/Utils")
try:
    import maturation_convergence as MC
except Exception as e:
    print("COULD NOT LOOK: import maturation_convergence: %s" % e); sys.exit(2)

fails = []
def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok: fails.append(what)

def div_rows():
    # three measured rounds, open rising: DIVERGING under the verdict rule
    return [{"round": i + 1, "measured": True, "open": o, "new": n} for i, (o, n) in enumerate([(5, 5), (6, 4), (7, 4)])]

# 1. live repo
live = MC.needs_lines(MC.read_all("."))
for mod in ("ExplosiveKnockback", "Cauldron", "Graffiti"):
    check(not any(l.startswith(mod + " ") for l in live), "live repo: no DIVERGING ask names %s" % mod)

# 2. synthetic: needs_lines reads a read_all-shaped dict; the fix may need the root to read stage and hold.
#    The test builds a temp root and calls read_all on it with stage.json rounds patched through MC.stage3.
tmp = tempfile.mkdtemp()
try:
    cd = os.path.join(tmp, MC.CONCEPTS)
    os.makedirs(cd)
    hold_dir = os.path.join(tmp, "src/RimMandrake/rimflow"); os.makedirs(hold_dir)
    json.dump({"_doc": "test", "holds": [{"mod": "HeldMod"}]}, open(os.path.join(hold_dir, "mod_owner_hold.json"), "w"))
    for mod, stage in (("HeldMod", "offline_build"), ("PassedMod", "passed"), ("LiveMod", "offline_build"), ("NoRecordMod", None)):
        v = os.path.join(cd, mod, "version"); os.makedirs(v)
        if stage:
            json.dump({"mod": mod, "stage": stage}, open(os.path.join(v, "stage_record.json"), "w"))
    real3 = MC.stage3
    MC.stage3 = lambda d: (div_rows(), None)
    try:
        lines = MC.needs_lines(MC.read_all(tmp))
    finally:
        MC.stage3 = real3
    named = lambda m: [l for l in lines if l.startswith(m + " ")]
    check(named("HeldMod") == [], "held mod: no DIVERGING ask")
    check(named("PassedMod") == [], "passed mod: no DIVERGING ask")
    check(len(named("LiveMod")) == 1, "advancing mod: its DIVERGING ask survives")
    check(len(named("NoRecordMod")) == 1, "mod with no stage_record.json: its ask is not hidden")
    shutil.rmtree(cd); os.makedirs(cd)
    check(MC.needs_lines(MC.read_all(tmp)) == [], "empty concepts folder: no ask, no crash")
except Exception as e:
    print("FAIL synthetic cases raised %s: %s" % (e.__class__.__name__, e)); fails.append("raised")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("RESULT: %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
PY
