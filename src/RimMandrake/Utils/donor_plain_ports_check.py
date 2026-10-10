#!/usr/bin/env python3
"""donor_plain_ports_check.py -- offline script for DONOR_CODE_PLAIN_PORTS_1.

The owner picked "Port plain" for seven Alpha Animals creatures on
Transient/donor_code_creatures_sheet_2026-10-09 ("copy the creature into our own defs and drop or
swap the donor class (no new C#)"). Each port lives in the biome mod whose roster carries it. This
script is the item's first script: it proves, from the files alone, that each ported creature

  1. exists as our ThingDef + PawnKindDef in that mod,
  2. carries no donor-assembly class (AlphaBehavioursAndEvents.*, the AA_Alternates render tree),
  3. names no donor def except a texPath explicitly listed as a temporary art placeholder,
  4. guards every VEF.* comp/extension with the VEF MayRequire (a framework we keep, not the donor),
  5. resolves every RM_ def it references (ability, projectile, product item) inside its own file,
  6. is what the biome roster names -- the roster no longer names the donor's defName.

Placeholder texPaths are reported as ART OWED, never as a pass of the art bar.
NOT PROVEN HERE (needs a load): that the defs load clean and the creature spawns in its biome.

Run: python3 src/RimMandrake/Utils/donor_plain_ports_check.py      (exit 1 on any failure)
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))   # src/RimMandrake
VANILLA_TEX = {  # vanilla/DLC texPaths a port may borrow (read from RimSage, 2026-10-09)
    "Things/Pawn/Animal/Yak/Dessicated_YakMale", "Things/Pawn/Animal/Yak/Dessicated_YakFemale",
    "Things/Pawn/Animal/Megaspider/Dessicated_Megaspider", "Things/Item/Resource/Uranium",
    "Things/Projectile/LauncherShot", "Things/Pawn/Animal/Bear/Dessicated_Bear",
    "Things/Pawn/Animal/Elephant/Dessicated_Elephant", "Things/Pawn/Animal/Thrumbo/Dessicated_Thrumbo",
    "Things/Pawn/Animal/Warg/Dessicated_Warg", "Things/Pawn/Animal/Iguana/Dessicated_Iguana",
}
VEF_GUARD = 'MayRequire="OskarPotocki.VanillaFactionsExpanded.Core"'

# one row per port: mod folder, def file, our defName, donor defName, roster file, donor-path art placeholders
PORTS = [
    {"mod": "Cauldron", "file": "Defs/ThingDefs_Races/RM_Radyak.xml", "ours": "RM_Radyak", "donor": "AA_Radyak",
     "roster": "Defs/BiomeDefs/RM_Cauldron.xml",
     "placeholder_tex": {"Things/Pawn/Animal/AA_Radyak/AA_Radyak_baby", "Things/Pawn/Animal/AA_Radyak/AA_Radyak_male",
                         "Things/Pawn/Animal/AA_Radyak/AA_Radyak_female"}},
    {"mod": "Miasma", "file": "Defs/ThingDefs_Races/RM_Thermadon.xml", "ours": "RM_Thermadon", "donor": "AA_Thermadon",
     "roster": "Defs/BiomeDefs/RM_Miasma.xml", "placeholder_tex": set()},
    {"mod": "TheRot", "file": "Defs/Fauna/RM_AgariPorts.xml", "ours": "RM_Agaripawn", "donor": "AA_Agaripawn",
     "roster": "Defs/BiomeDefs/RM_TheRot_Biome.xml", "placeholder_tex": set()},
    {"mod": "TheRot", "file": "Defs/Fauna/RM_AgariPorts.xml", "ours": "RM_Agaripod", "donor": "AA_Agaripod",
     "roster": "Defs/BiomeDefs/RM_TheRot_Biome.xml", "placeholder_tex": set()},
    {"mod": "TheRot", "file": "Defs/Fauna/RM_AgariPorts.xml", "ours": "RM_MycoidColossus", "donor": "AA_MycoidColossus",
     "roster": "Defs/BiomeDefs/RM_TheRot_Biome.xml", "placeholder_tex": set()},
]


def _strip_comments(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def check_port(p):
    """-> (failures, notes) for one port."""
    bad, notes = [], []
    mod = os.path.join(ROOT, p["mod"])
    path = os.path.join(mod, p["file"])
    if not os.path.exists(path):
        return ["%s: def file %s missing" % (p["ours"], p["file"])], notes
    body = _strip_comments(open(path, encoding="utf-8").read())
    defined = set(re.findall(r"<defName>([^<]+)</defName>", body))
    for kind in ("ThingDef", "PawnKindDef"):
        if not re.search(r"<%s\b[^>]*>\s*<defName>%s</defName>" % (kind, p["ours"]), body):
            bad.append("%s: no %s %s" % (p["ours"], kind, p["ours"]))
    for donor_class in ("AlphaBehavioursAndEvents", "AA_Alternates", "AnimalStatExtension"):
        if donor_class in body:
            bad.append("%s: still carries donor class/def %s" % (p["ours"], donor_class))
    tex = set(re.findall(r"<texPath>([^<]+)</texPath>", body))
    for t in sorted(tex):
        if t in p["placeholder_tex"]:
            notes.append("%s: ART OWED - %s is a donor-path placeholder" % (p["ours"], t))
            continue
        if t in VANILLA_TEX:
            continue
        hits = [os.path.join(mod, "Textures", *(t + sfx).split("/")) for sfx in ("_south.png", ".png")]
        if not any(os.path.exists(h) for h in hits):
            bad.append("%s: texPath %s resolves to nothing in %s/Textures" % (p["ours"], t, p["mod"]))
    no_tex = re.sub(r"<texPath>[^<]*</texPath>", "", body)
    for ref in sorted(set(re.findall(r"\b(AA_\w+)", no_tex))):
        bad.append("%s: names donor def %s" % (p["ours"], ref))
    for m in re.finditer(r"<li\b[^>]*Class=\"VEF\.[^\"]+\"[^>]*>", body):
        if VEF_GUARD not in m.group(0):
            bad.append("%s: VEF comp without the VEF MayRequire guard: %s" % (p["ours"], m.group(0)))
    refs = set(re.findall(r"<(?:resourceDef|initialAbility|defaultProjectile|li)>(RM_\w+)</", body))
    for r in sorted(refs - defined):
        bad.append("%s: references %s, which its file does not define" % (p["ours"], r))
    roster = _strip_comments(open(os.path.join(mod, p["roster"]), encoding="utf-8").read())
    if not re.search(r"<%s\b[^>]*>[\d.]+</%s>" % (p["ours"], p["ours"]), roster):
        bad.append("%s: roster %s does not name it" % (p["ours"], p["roster"]))
    if re.search(r"<%s\b" % p["donor"], roster):
        bad.append("%s: roster %s still names the donor %s" % (p["ours"], p["roster"], p["donor"]))
    return bad, notes


def static_checks(mod=None):
    """Failures for every port (or only the ports living in `mod`), for a mod's validation.py."""
    bad = []
    for p in PORTS:
        if mod is None or p["mod"] == mod:
            bad += check_port(p)[0]
    return bad


def main():
    # sanity probe: the checker must be able to SEE a failure -- a port pointed at a missing file must fail
    probe_bad, _ = check_port(dict(PORTS[0], file="Defs/ThingDefs_Races/__no_such_file__.xml"))
    if not probe_bad:
        print("SANITY PROBE FAILED: a missing def file did not fail -- the checker is blind")
        return 2
    total = 0
    for p in PORTS:
        bad, notes = check_port(p)
        print("%-14s %-10s %s" % (p["ours"], p["mod"], "FAIL" if bad else "PASS"))
        for b in bad:
            print("   FAIL " + b)
        for n in notes:
            print("   " + n)
        total += len(bad)
    print("%d port(s), %d failure(s)" % (len(PORTS), total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
