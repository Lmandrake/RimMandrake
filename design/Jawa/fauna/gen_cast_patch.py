#!/usr/bin/env python3
"""Turn cast_assignment.csv into a RimWorld PatchOperation XML that BUILD can validate.

⚠️ DECIDE produces the DATA. BUILD owns whether and how it is patched and deployed - this
file is a proposal artifact under design/, not a deployed mod file.

Each biome's `wildAnimals` list is REPLACED wholesale. The shipped lists carry ~1,024
BiomeAnimalRecords of which almost all sit at commonality 0; replacing with the ~29 that
were actually cast is both the intent and far easier to read.
"""
import csv, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dumppath import defs_dir, captures_newest_first

FA = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(FA, 'BiomeCast_Ashkarr.xml')

def _vanilla_biomes():
    """defNames of every BiomeDef Core or a DLC DEFINES, read from the game's Data tree.

    Returns an empty set if the tree cannot be read; the caller then falls back to
    the old packageId behaviour rather than silently dropping every MayRequire.
    """
    import glob
    import xml.etree.ElementTree as ET
    # ⚠️ The Windows form of this path does not exist under WSL, and a bare
    # `from game_paths import GAME_DATA` does not resolve from this directory.
    # Both were true in the first cut of this fix and it silently returned an
    # empty set, which the caller reads as "nothing is vanilla" - the failure
    # mode this whole function exists to prevent. Try the repo resolver first,
    # then both spellings, and say so if none is readable.
    root = None
    try:
        import sys as _sys
        _u = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", "..", "src", "RimMandrake", "Utils")
        _sys.path.insert(0, os.path.normpath(_u))
        from game_paths import GAME_DATA          # noqa: E402
        root = GAME_DATA
    except Exception:
        for cand in ("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
                     r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data"):
            if os.path.isdir(cand):
                root = cand
                break
    if not root or not os.path.isdir(root):
        print("⚠️ cannot read the game Data tree - MayRequire falls back to the "
              "dump's packageId, which credits the LAST PATCHER. Check the three "
              "Core desert biomes by hand before deploying.")
        return set()
    out = set()
    for fp in glob.glob(os.path.join(root, "**", "*.xml"), recursive=True):
        if "/Defs/" not in fp.replace("\\", "/"):
            continue
        try:
            r = ET.parse(fp).getroot()
        except Exception:
            continue
        for el in r.iter("BiomeDef"):
            dn = el.findtext("defName")
            if dn:
                out.add(dn)
    return out


def main():
    # ⚠️ Resolve packageId across EVERY capture, newest first, not just the newest.
    # A capture taken during a load that discarded biomes holds 54 of them instead
    # of 80, and reading only that one drops MayRequire from exactly the biomes
    # this patch exists to fix - silently, because a missing packageId only emits
    # a warning. Any capture that ever saw the biome is good enough for its owner.
    PKG = {}
    for cap in captures_newest_first():
        f = os.path.join(cap, 'defs', 'BiomeDef.json')
        if not os.path.isfile(f):
            continue
        bl = json.load(open(f, encoding='utf-8'))
        bl = bl if isinstance(bl, list) else bl.get('defs')
        for x in bl:
            if isinstance(x, dict):
                PKG.setdefault(x['defName'], x.get('packageId'))

    # 🔴 packageId IN THE DUMP CREDITS WHOEVER PATCHED THE DEF LAST, NOT WHOEVER
    # DEFINED IT. MAYREQUIRE_NAMES_THE_PATCHER_1, measured 2026-08-23: `Desert`,
    # `ExtremeDesert` and `AridShrubland` are Core biomes, and the dump attributes
    # all three to `grimterra.terrainretexturemod` because GRiNDTerra Terrain
    # Retexture patched them. Emitting that as MayRequire gates three VANILLA
    # biomes on a retexture mod: remove it and the cast silently stops applying to
    # biomes that are still perfectly present, with no error to show for it.
    #
    # ⚠️ THE DUMP CANNOT ANSWER THIS ABOUT ITSELF - a check that reads modName or
    # packageId from the capture is circular and returns a confident 0. The
    # independent source is the GAME'S OWN Data TREE: whatever Core and the DLCs
    # define there needs no MayRequire, whoever touched it afterwards.
    VANILLA = _vanilla_biomes()

    # wildAnimals takes a PawnKindDef. Read the roster so a ThingDef-only name is
    # caught here rather than as a cross-reference error on the next cold load.
    PAWNKINDS = set()
    for cap in captures_newest_first():
        f = os.path.join(cap, 'defs', 'PawnKindDef.json')
        if not os.path.isfile(f):
            continue
        pl = json.load(open(f, encoding='utf-8'))
        pl = pl if isinstance(pl, list) else pl.get('defs')
        PAWNKINDS |= {x['defName'] for x in pl if isinstance(x, dict)}
        break
    if not PAWNKINDS:
        sys.exit('no PawnKindDef.json in any capture - refusing to emit a cast that '
                 'cannot be checked against the pawnkind roster')
    skipped = []

    rows = list(csv.DictReader(open(os.path.join(FA, 'cast_assignment.csv'), encoding='utf-8')))
    byb = collections.defaultdict(list)
    for r in rows:
        byb[r['biome']].append(r)

    parts = ['<?xml version="1.0" encoding="utf-8"?>',
             '<Patch>',
             '  <!-- GENERATED by design/Jawa/fauna/gen_cast_patch.py - do not hand-edit.',
             '       Source: cast_assignment.csv. Regenerate rather than patching this file.',
             '',
             '       Owner\'s brief 2026-08-22: many small, some medium, a few large, ONE',
             '       super-huge rare per biome; appearance matches the biome where it can;',
             '       creatures unique to a biome as far as possible.',
             '',
             '       Each biome\'s wildAnimals is REPLACED. The shipped lists hold ~1024 records',
             '       almost all at commonality 0. -->', '']
    for b in sorted(byb, key=lambda x: -len(byb[x])):
        pkg = PKG.get(b)
        # A biome Core/DLC DEFINES never gets a MayRequire, however many mods have
        # since patched it. See _vanilla_biomes() and the block above.
        if VANILLA and b in VANILLA:
            req = ''
        else:
            req = f' MayRequire="{pkg}"' if pkg and not str(pkg).startswith('ludeon.rimworld') else ''
        # 🔴 WRAPPED IN A CONDITIONAL, NOT A BARE REPLACE - BIOME_CAST_APPLY_1, BUILD.
        # A PatchOperationReplace whose xpath matches nothing is a RED ERROR every
        # launch, not a silent no-op, and 25 bare ones is 25 errors.
        # ⚠️ MayRequire is NOT enough on its own and that is this project's own rule:
        # it checks that the MOD is present, never that the DEF still is. A biome
        # renamed or removed upstream leaves MayRequire passing and the Replace
        # erroring. The conditional tests the wildAnimals node itself - reality
        # rather than intent - so it degrades to doing nothing.
        # 🔑 There is deliberately NO <nomatch>: if the biome is absent we want the
        # cast absent too, not added to something that was never cast.
        xp = f'/Defs/BiomeDef[defName="{b}"]/wildAnimals'
        parts.append(f'  <Operation Class="PatchOperationConditional"{req}>')
        parts.append(f'    <xpath>{xp}</xpath>')
        parts.append('    <match Class="PatchOperationReplace">')
        parts.append(f'      <xpath>{xp}</xpath>')
        parts.append('      <value>')
        parts.append('        <wildAnimals>')
        for r in sorted(byb[b], key=lambda r: (-float(r['commonality']), r['defName'])):
            note = f"{r['band']}, {r['status']}"
            if r['defName'] not in PAWNKINDS:
                # wildAnimals resolves a PawnKindDef. A ThingDef name here is a
                # dangling cross-reference, not a fallback. Named, never dropped
                # in silence.
                skipped.append((b, r['defName']))
                parts.append(f'          <!-- SKIPPED {r["defName"]} - {r["label"]}:'
                             f' not a PawnKindDef; wildAnimals cannot resolve it -->')
                continue
            # 🔴 THE NODE NAME IS THE ANIMAL AND THE NODE TEXT IS THE COMMONALITY.
            # BiomeAnimalRecord.LoadDataFromXmlCustom is
            #     commonality = ParseHelper.FromString<float>(xmlRoot.FirstChild.Value)
            # so `<li><animal>X</animal><commonality>N</commonality></li>` makes
            # FirstChild an ELEMENT whose .Value is null -> ArgumentNullException
            # -> RimWorld discards the ENTIRE BiomeDef, silently, and the patch
            # reports success. That shipped on 2026-08-22 and cost all 26 biomes
            # this file touches; see MAP_BIOMES_REMOVED_LIVE_1. The rule was
            # already written in Jawa_Patches/Patches/Ikee_Rename.xml lines 37-46.
            parts.append(f'          <{r["defName"]}>{r["commonality"]}</{r["defName"]}>'
                         f' <!-- {r["label"]} - {note} -->')
        parts.append('        </wildAnimals>')
        parts.append('      </value>')
        parts.append('    </match>')
        parts.append('  </Operation>')
        parts.append('')
    parts.append('</Patch>')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(parts))
    print(f"wrote {OUT}: {len(byb)} biomes, {len(rows)} records")
    nomay = [b for b in byb if not PKG.get(b)]
    if nomay:
        print(f"⚠️ no packageId resolved for: {nomay} - BUILD must confirm the MayRequire")
    if skipped:
        print(f"⚠️ {len(skipped)} cast entries SKIPPED - not PawnKindDefs, so wildAnimals "
              f"could not resolve them:")
        for b, d in skipped:
            print(f"     {b:<30} {d}")

if __name__ == '__main__':
    main()
