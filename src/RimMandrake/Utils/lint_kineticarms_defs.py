#!/usr/bin/env python3
"""Offline lint of the KineticArms mod (defs/patches vs C#): the generic lint (lint_mod_defs.py) plus data checks it cannot see:

  ka-weapons    every row of RimMandrakeKineticArmsMod.Weapons names a def that exists and a toggle that is a Scribed setting; the ruins
                rarity table (RM_KineticMath.RuinsWeights) has one weight per row (index-aligned: a ninth weapon silently gets weight 0)
  ka-carried    every looted-weapon row (RM_Patch_LootedKineticWeapons.Carried) names an existing def and a Scribed toggle
  ka-forces     every RM_Concussive_* / RM_Repulse_* DamageDef carries a knockback extension with force > 0 and maxThrowCells >= 1 (the
                strength slider scales these; a zero base force is a weapon that throws nothing at any setting)
  ka-cone       every RM_KineticBoltExtension cone is in (0, 180] degrees: the push-along-shot trick needs every thrown cell ahead of the centre
  ka-kernel     the kernel is Verse-free, listed in the mod csproj and called by the building / projectile / loot code
  ka-engine     the private engine field the power-draw setting reaches by name (CompProperties_Power.basePowerConsumption) still exists

    python3 src/RimMandrake/Utils/lint_kineticarms_defs.py [--mod-dir <dir>] [--quiet]
"""
import contextlib
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ENGINE = os.environ.get("RIMWORLD_DECOMPILED", "/mnt/d/Luke/dev/reference/rimworld-decompiled")


def rd(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


def extras(mod):
    errs = []
    E = lambda k, m: errs.append("ERROR ka-%s: %s" % (k, m))
    src = os.path.join(mod, "Source")
    cs = {os.path.basename(p): rd(p) for p in glob.glob(os.path.join(src, "*.cs"))}
    nocom = {k: re.sub(r"//[^\n]*", "", v) for k, v in cs.items()}
    defnames = set()
    knock = {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in root.iter():
            n = d.findtext("defName")
            if n:
                defnames.add(n)
                if d.tag == "DamageDef":
                    ext = None
                    for li in d.iter("li"):
                        if (li.get("Class") or "").endswith("RM_KnockbackExtension"):
                            ext = li
                    knock[n] = ext
    mod_cs = nocom.get("RM_KineticArmsMod.cs", "")
    settings_fields = set(re.findall(r'Scribe_Values\.Look\(ref (\w+), "\1"', mod_cs))
    weapons = re.findall(r'\("(\w+)",\s*"[^"]*",\s*"(\w+)"\)', mod_cs.split("Weapons =")[1].split("};")[0]) if "Weapons =" in mod_cs else []
    if len(weapons) < 8:
        E("weapons", "found %d rows in RimMandrakeKineticArmsMod.Weapons, expected the 8 shipped weapons (parser blind?)" % len(weapons))
    for field, d in weapons:
        if d not in defnames:
            E("weapons", "Weapons row %s names %s, which no def under Defs/ defines" % (field, d))
        if field not in settings_fields:
            E("weapons", "Weapons row toggle %s is not a Scribed setting" % field)
    kern = nocom.get("RM_KineticMath.cs", "")
    m = re.search(r"RuinsWeights\s*=\s*\{([^}]*)\}", kern)
    n_w = len([x for x in m.group(1).split(",") if x.strip()]) if m else -1
    if n_w != len(weapons):
        E("weapons", "RuinsWeights has %d entries but Weapons has %d rows (index-aligned)" % (n_w, len(weapons)))
    loot = nocom.get("RM_LootedKineticWeapons.cs", "")
    carried = re.findall(r'\("(\w+)",\s*"(\w+)",\s*(?:true|false)\)', loot)
    if len(carried) < 4:
        E("carried", "found %d Carried rows, expected the 5 looted weapons (parser blind?)" % len(carried))
    for field, d in carried:
        if d not in defnames:
            E("carried", "Carried row names %s, which no def defines" % d)
        if field not in settings_fields:
            E("carried", "Carried toggle %s is not a Scribed setting" % field)
    if len(knock) < 8:
        E("forces", "found %d RM_Concussive_/RM_Repulse_ DamageDefs, expected 8 (parser blind?)" % len([k for k in knock]))
    for n, ext in knock.items():
        if not (n.startswith("RM_Concussive_") or n.startswith("RM_Repulse_")):
            continue
        if ext is None:
            E("forces", "%s has no RM_KnockbackExtension" % n)
            continue
        try:
            f = float(ext.findtext("force") or "0")
            c = int(ext.findtext("maxThrowCells") or "0")
        except ValueError:
            E("forces", "%s: force/maxThrowCells do not parse" % n)
            continue
        if f <= 0:
            E("forces", "%s base force %s must be > 0 (a zero base throws nothing at any strength)" % (n, f))
        if c < 1:
            E("forces", "%s maxThrowCells %d must be >= 1" % (n, c))
    # cones
    n_cone = 0
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for li in root.iter("li"):
            if (li.get("Class") or "").endswith("RM_KineticBoltExtension"):
                n_cone += 1
                try:
                    c = float(li.findtext("coneDegrees") or "90")
                except ValueError:
                    E("cone", "%s: coneDegrees does not parse" % os.path.basename(p))
                    continue
                if not 0 < c <= 180:
                    E("cone", "%s: coneDegrees %s must be in (0,180]: past a half-turn the throw is no longer along the shot" % (os.path.basename(p), c))
    if n_cone < 5:
        E("cone", "found %d bolt extensions, expected the 5 shipped ones (parser blind?)" % n_cone)
    # kernel
    for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
        if bad in kern:
            E("kernel", "RM_KineticMath.cs contains '%s': the selftest compiles it on plain net8.0" % bad)
    csproj = next(iter(glob.glob(os.path.join(src, "*.csproj"))), None)
    if csproj is None or 'Include="RM_KineticMath.cs"' not in rd(csproj):
        E("kernel", "the mod csproj does not compile RM_KineticMath.cs")
    callers = "\n".join(v for k, v in nocom.items() if k != "RM_KineticMath.cs")
    for fn in ("Dir", "BackStep", "ConeCells", "Facing", "Recharge", "CanFire", "Spend", "ScaledForce", "PickRuins", "RuinsRollFor", "RuinsStack", "PickLooted", "LootMoney"):
        if "RM_KineticMath.%s(" % fn not in callers:
            E("kernel", "nothing calls RM_KineticMath.%s: the fuzz would be proving dead code" % fn)
    # engine field
    cp = os.path.join(ENGINE, "RimWorld", "CompProperties_Power.cs")
    if os.path.isfile(cp):
        if "basePowerConsumption" not in rd(cp):
            E("engine", "CompProperties_Power.basePowerConsumption is gone: the pulse cannon power-draw setting reaches it by name")
    return errs


def main(argv):
    mod = os.path.join(REPO, "src", "RimMandrake", "KineticArms")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("KineticArms", argv)
    out = buf.getvalue()
    errs = extras(mod)
    if "--quiet" not in argv:
        sys.stdout.write(out)
    else:
        for l in out.splitlines():
            if l.startswith("ERROR"):
                print(l)
    for e in errs:
        print(e)
    return rc if rc else (1 if errs else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
