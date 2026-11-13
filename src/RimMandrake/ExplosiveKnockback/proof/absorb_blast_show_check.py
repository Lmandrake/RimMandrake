#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS (owner card 2026-11-12: Extra Explosion
Effects -> "Absorb the idea into Knockback"). Offline, structural; the LOOK is a judge agent's call, not this script's.

Not a selftest (it is red until the item is built, so it lives outside the selftest glob). Pass = exit 0, 6 checks.
  A1  EK ships at least 4 FleckDefs of its own (defName RM_KnockbackBlast*) in Defs/
  A2  every one of them has a texPath that resolves to a PNG under EK's own Textures/ (no donor art path)
  A3  EK's C# hooks the start of an explosion for visuals: a HarmonyPatch on Explosion.StartExplosion or
      GenExplosion.DoExplosion in Source/
  A4  a Mod Setting `blastShow` (bool, default true), saved in ExposeData and drawn in the settings window
  A5  a big-blast branch exists (a radius or damage threshold that adds the shockwave/quake) behind its own
      setting `blastShowBig`
  A6  nothing in EK names Keshash or ExtraExplosionEffects (no copied code or textures)

    python3 src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

EK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main():
    fails, flecks = [], {}
    for p in glob.glob(os.path.join(EK, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot().iter("FleckDef"):
            n = d.findtext("defName") or ""
            if n.startswith("RM_KnockbackBlast"):
                flecks[n] = d.findtext("graphicData/texPath") or ""
    if len(flecks) < 4:
        fails.append(f"A1 {len(flecks)} RM_KnockbackBlast* FleckDefs, want >= 4")
    for n, tex in sorted(flecks.items()):
        hits = glob.glob(os.path.join(EK, "Textures", tex + "*.png")) if tex else []
        if not hits:
            fails.append(f"A2 {n}: texPath {tex!r} resolves to no PNG under {EK}/Textures")
    src = "\n".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(EK, "Source", "*.cs")))
    if not re.search(r'HarmonyPatch\(\s*typeof\((Explosion|GenExplosion)\)\s*,\s*(nameof\([\w.]*(StartExplosion|DoExplosion)\)|"(StartExplosion|DoExplosion)")', src):
        fails.append("A3 no HarmonyPatch on Explosion.StartExplosion or GenExplosion.DoExplosion in Source/")
    for s in ("blastShow", "blastShowBig"):
        if not re.search(rf"public static bool {s}\s*=\s*true", src):
            fails.append(f"A4/A5 no `public static bool {s} = true` setting")
        elif not re.search(rf'Scribe_Values\.Look\(ref {s}, "{s}", true\)', src) or not re.search(rf"ref {s}\b[^;]*\)\s*;", src.split("DoWindowContents", 1)[-1]):
            fails.append(f"A4/A5 setting {s} is not both saved (ExposeData) and drawn (DoWindowContents)")
    for p in glob.glob(os.path.join(EK, "**", "*"), recursive=True):
        if os.path.isfile(p) and p.endswith((".cs", ".xml")) and os.path.abspath(p) != os.path.abspath(__file__):
            if re.search(r"Keshash|ExtraExplosionEffects", open(p, encoding="utf-8", errors="replace").read()):
                fails.append(f"A6 {os.path.relpath(p, EK)} names the donor mod")
    for f in fails:
        print("FAIL", f)
    print(f"{'PASS' if not fails else 'FAIL'} absorb blast show: {len(fails)} failing line(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
