#!/usr/bin/env python3
"""gen_races_mod.py reproduces the committed StarWarsRaces mod, and a refused run
writes NOTHING.

Why this test exists (RACES_GEN_REPAIR_STOP_SHREDDING_FIRST, 2026-10-18)
=======================================================================
The generator refused every run with "331 genes would be LOST" -- and it had
already overwritten SW_Genes, SW_HeadTypes, SW_Support, SW_Categories,
SW_NameMakers and About.xml when it refused. Root cause: the three-tier rename
(aa759446e4) rewrote the OUTPUT's defNames to RSW_ but not the generator's
prefixes, so every species missed its shipped self and was rebuilt from donors.
Meanwhile hand edits piled up in the output that no run could reproduce, so the
owner's rulings (gene removals, the Sith Kissai rename, the skin-shader heads,
the tattoo filter, the SandP nickname cut) lived ONLY in the committed XML.

What it asserts
===============
1. REPRODUCTION: `gen_races_mod.py --no-textures --check` stages every output in
   memory and finds ZERO files that differ from the committed mod. A failure
   means someone edited the generated XML by hand (fold the edit into the
   generator's tables) or changed the generator without regenerating.
2. ATOMICITY: on a scratch copy of the mod whose xenotype file carries one gene
   the generator cannot rebuild, the run REFUSES (exit != 0, "REFUSING TO WRITE")
   and every file in the copy is byte-identical afterwards.

Needs the donor mods and the def dump on the Windows drive; without them it prints
the UNMEASURED phrase rather than passing.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GEN = os.path.join(HERE, "gen_races_mod.py")
MOD = os.path.join(REPO, "src", "RimStarWars", "StarWarsRaces")
UNMEASURED = "UNMEASURED, not a pass or a fail"

sys.path.insert(0, HERE)


def inputs_present():
    try:
        from game_paths import DEF_DUMP, WORKSHOP
    except Exception as e:                      # noqa: BLE001
        return "game_paths: %s" % e
    for p in (os.path.join(DEF_DUMP, "defs", "XenotypeDef.json"),
              os.path.join(WORKSHOP, "2915192253"), os.path.join(WORKSHOP, "2980427615"),
              os.path.join(WORKSHOP, "3458153185", "BTD_Data")):
        if not os.path.exists(p):
            return "missing %s" % p
    return None


def run(out, *args):
    env = dict(os.environ, RACES_GEN_OUT=out)
    return subprocess.run([sys.executable, GEN, "--no-textures"] + list(args),
                          env=env, capture_output=True, text=True, timeout=600)


def snapshot(root):
    h = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            h[os.path.relpath(p, root)] = hashlib.sha1(open(p, "rb").read()).hexdigest()
    return h


def main():
    why = inputs_present()
    if why:
        print("%s -- generator inputs absent (%s)" % (UNMEASURED, why))
        return 0
    fails = []

    # 1. reproduction, against the real mod, writing nothing
    r = run(MOD, "--check")
    tail = (r.stdout + r.stderr).strip().splitlines()[-12:]
    if r.returncode != 0 or "--check: 0 staged file(s) differ" not in r.stdout:
        fails.append("regeneration differs from committed (exit %d):\n    %s"
                     % (r.returncode, "\n    ".join(tail)))
    else:
        print("PASS regeneration == committed (0 staged files differ)")

    # 2. a refused run writes nothing
    tmp = tempfile.mkdtemp(prefix="selftest_gen_races_")
    try:
        out = os.path.join(tmp, "StarWarsRaces")
        shutil.copytree(MOD, out, ignore=shutil.ignore_patterns("Textures", "Sounds"))
        xp = os.path.join(out, "Defs", "XenotypeDefs", "RimMandrakeXenotypes.xml")
        t = open(xp, encoding="utf-8").read()
        phantom = ("  <XenotypeDef>\n    <defName>RSW_SelftestPhantom</defName>\n"
                   "    <genes>\n      <li>Robust</li>\n    </genes>\n  </XenotypeDef>\n")
        open(xp, "w", encoding="utf-8").write(t.replace("</Defs>", phantom + "</Defs>"))
        before = snapshot(out)
        r = run(out)
        after = snapshot(out)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if r.returncode == 0 or "REFUSING TO WRITE" not in (r.stdout + r.stderr):
            fails.append("phantom gene did not trigger the refusal (exit %d)" % r.returncode)
        elif changed:
            fails.append("refused run still wrote %d file(s): %s" % (len(changed), changed[:8]))
        else:
            print("PASS refused run wrote nothing (%d files unchanged)" % len(before))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print("FAIL " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
