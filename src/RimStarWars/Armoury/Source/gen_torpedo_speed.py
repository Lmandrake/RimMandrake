"""Slow every warhead in the galaxy: the torpedo rule (L13c).

Measured: missile/rocket projectiles travel at speed 50 -- exactly the speed of
a blaster bolt, and the median of all 537 projectiles. A warhead indistinguish-
able from a bullet is the hypersonic missile L13b says this galaxy never built.

Slowing them is what makes them fit:
  * slow enough to pass a deflector screen  (L6: screens stop FAST things)
  * slow enough to see, dodge, or shoot down -- the counterplay that makes a
    weapon with no hard counter (L13) tolerable
  * so only worth firing at something that CANNOT dodge: vehicles, emplacements,
    shield generators, VAST creatures

A colonist moves ~4.6 cells/sec. At speed 50 a warhead crosses 20 cells in 0.4s
-- no reaction possible. At 14 it takes 1.4s and the target can cover ~6 cells.
That is the difference between a cutscene and a decision.

Blast values are deliberately NOT touched. Explosions are meant to stay
devastating against every form of protection (L13); what was wrong was the
delivery, not the warhead.
"""
import collections
import io
import os
import sys

# Resolved from this file, not hardcoded: the repo moved G: -> D: on 2026-08-12
# and is reached by different paths from Windows Python and WSL.
# Walk UP until the repo root announces itself, rather than counting "..".
# 🔴 Counting broke twice: the drive move made it look fragile, and the
# 2026-08-13 restructure changed this file's depth so the five ".." landed one
# directory ABOVE the repo. `from def_diff import ...` then raised
# ModuleNotFoundError, both generators died, and refresh.py --patches still
# exited 0 — a failure that regenerated nothing while reporting success.
# A marker file cannot miscount.
def _find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")) or \
           os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(
                "could not find the repo root above %s - no .git or CLAUDE.md "
                "on any parent. Refusing to guess." % start)
        d = parent


_REPO_ROOT = _find_repo_root(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src", "RimMandrake", "Utils"))
from def_diff import iter_live_defs
from def_inventory import build as build_offline, D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA

# Resolved per-platform, never a bare C:\ literal. A hardcoded Windows path
# here made this generator die under WSL python3 with a FileNotFoundError
# naming ThingDef.json - which reads as "take a fresh dump", when the dump
# was present and only the interpreter was wrong. refresh.py carries the
# same lesson in its own header; game_paths.LOCALLOW is the shared fix.
import game_paths as _GP
DUMP = os.path.join(_GP.DEF_DUMP, "defs", "ThingDef.json")
OUT = os.path.join(_REPO_ROOT, "src", "RimStarWars", "Armoury", "Patches",
                   "Armoury_TorpedoSpeed.xml")

MARKERS = ("rocket", "missile", "torpedo")
# Anything already this slow is left alone -- some mods (whistling birds,
# seekers) already got it right, and there is no reason to overwrite good work.
ALREADY_SLOW = 26
HEAVY = 12      # anti-vehicle / anti-emplacement: ponderous and unmistakable
LIGHT = 18      # personal launchers, wrist rockets: quicker but still duckable

targets = {}
for d in iter_live_defs(DUMP):
    f = d.get("fields") or {}
    pr = f.get("projectile")
    if not isinstance(pr, dict):
        continue
    dn = d.get("defName") or ""
    b = dn.lower()
    if not any(m in b for m in MARKERS):
        continue
    sp = pr.get("speed")
    if not isinstance(sp, (int, float)) or sp <= ALREADY_SLOW:
        continue
    rad = pr.get("explosionRadius") or 0
    # Big blast == heavy weapon == slowest. Small blast == personal == quicker.
    targets[dn] = (sp, HEAVY if rad >= 2.5 else LIGHT, d.get("modName") or "?")

print("warheads to slow: %d" % len(targets))

ds = build_offline(D_CONFIG, D_WORKSHOP, D_LOCAL, D_DATA, types=("ThingDef",))


def declarer(defname):
    """Patches hit raw XML before inheritance: aim at whoever declares speed."""
    rec = ds.get("ThingDef", defname)
    if rec is None:
        return None, None
    if rec.own.find("projectile/speed") is not None:
        return defname, "defName"
    seen, pn = set(), rec.parentName
    while pn and pn not in seen:
        seen.add(pn)
        pel = ds.by_name.get(pn)
        pel = getattr(pel, "own", pel)
        if pel is None:
            return None, None
        if pel.find("projectile/speed") is not None:
            return pn, "Name"
        pn = pel.get("ParentName")
    return None, None


NL = "\n"
by_mod, skipped = collections.defaultdict(list), []
for dn, (old, new, mod) in sorted(targets.items()):
    owner, attr = declarer(dn)
    if owner is None:
        skipped.append(dn)
        continue
    sel = '[defName="%s"]' % owner if attr == "defName" else '[@Name="%s"]' % owner
    by_mod[mod].append(
        '        <!-- %s : speed %s -> %d -->' % (dn, old, new) + NL +
        '        <li Class="PatchOperationReplace">' + NL +
        '          <xpath>/Defs/ThingDef' + sel + '/projectile/speed</xpath>' + NL +
        '          <value><speed>%d</speed></value>' % new + NL +
        '        </li>' + NL)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write('<?xml version="1.0" encoding="utf-8"?>' + NL)
    fh.write('<!-- Torpedoes: warheads drift, so they can be dodged (L13c).' + NL)
    fh.write('     GENERATED by src/RimStarWars/Armoury/Source/gen_torpedo_speed.py. Do not hand-edit.' + NL)
    fh.write('     Blast is deliberately untouched: explosions stay devastating' + NL)
    fh.write('     against every protection (L13). Only the delivery changes. -->' + NL)
    fh.write('<Patch>' + NL)
    for mod, ops in sorted(by_mod.items()):
        fh.write(NL + '  <Operation Class="PatchOperationFindMod">' + NL)
        fh.write('    <mods><li>' + mod + '</li></mods>' + NL)
        fh.write('    <match Class="PatchOperationSequence">' + NL)
        fh.write('      <operations>' + NL)
        for o in ops:
            fh.write(o)
        fh.write('      </operations>' + NL)
        fh.write('    </match>' + NL + '  </Operation>' + NL)
    fh.write(NL + '</Patch>' + NL)

print("ops %d across %d mods" % (sum(len(v) for v in by_mod.values()), len(by_mod)))
if skipped:
    print("skipped (speed not declared anywhere findable): %d %s"
          % (len(skipped), skipped[:5]))
for dn, (old, new, mod) in sorted(targets.items(), key=lambda kv: kv[1][1])[:12]:
    print("   %-40s %3s -> %2d   %s" % (dn[:40], old, new, mod[:22]))
