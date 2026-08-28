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

def _cherry_picker_cuts():
    """defNames the owner has cut with Cherry Picker, or None if UNREADABLE.

    ⛔ Returns None - never an empty set - when the settings file cannot be read.
    An empty set would silently mean "nothing is cut" and the generator would go
    back to emitting dead entries with no sign anything was skipped.
    """
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FA)))
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
    import cherrypicker
    try:
        cuts = cherrypicker.load()
    except IOError as exc:
        print(f"⚠️ Cherry Picker settings unreadable ({exc}); cut animals will be "
              f"emitted as live entries and will silently never spawn.")
        return None
    print(cuts.provenance())
    return cuts.names


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



def _animal_side_biomes():
    """biome -> {animal defName} taken from each RACE's own wildBiomes, off DISK.

    🔴 WHY THIS EXISTS. BiomeDef.CommonalityOfAnimal (BiomeDef.cs:341) builds
    cachedAnimalCommonalities with two plain .Add() calls and no overwrite check. An
    animal reaches a biome from two directions - the BIOME's wildAnimals (which this
    generator REPLACES) and the ANIMAL's own race/wildBiomes. Same animal, same biome,
    both directions => ArgumentException.

    ⚠️ AND THE DAMAGE OUTLIVES THE EXCEPTION. The cache field is assigned BEFORE the
    loops that fill it, so when loop 2 throws it is left non-null and half-built and
    the `== null` guard never rebuilds it. Every animal that would have registered via
    wildBiomes after the collision point returns commonality 0 and NEVER SPAWNS WILD in
    that biome, for the rest of the session, with no further error. Choose Wild Animal
    Spawns dies outright; Biome Compatibility Project aborts the rest of the post-load
    queue.

    This generator caused exactly that on 2026-08-22 by picking purely on the biome
    side. 30 pairs, measured 2026-08-23.

    🔴 CORRECTED 2026-08-26. This used to say the def dump "cannot help, because it
    does not serialise wildBiomes at all". IT DOES: a capture carries
    ThingDef.fields.race.wildBiomes, measured against
    captures/2026-08-26T14-20-04Z. That wrong sentence is why the disk-only scan
    shipped as sufficient, and it cost 27 live collisions - 22 Alpha Animals, 3
    Megafauna, 2 Jurassic Rimworld - every one of them created by a PatchOperation
    and therefore invisible to the walk below. Choose Wild Animal Spawns died at
    startup and 181 of 744 cast weights read 0.

    So this now reads BOTH: the disk walk (which sees mods whose XML declares it)
    and the newest capture (which sees the post-patch truth, including entries no
    file declares). The union is the answer; either alone is a floor.

    🔴 THE CAPTURE HALF IS SELF-ERASING, AND THIS IS THE TRAP THAT WILL BITE NEXT.
    Measured 2026-08-26: this run found 56 pairs, against the 61 already shipped by
    AnimalBiomeDuplicates_Fix.xml + AnimalBiomeDuplicates_Generated.xml. All 56 were
    in the shipped set - but FIVE shipped pairs were NOT in the 56:

        AridShrubland x Armadillo · Desert x Armadillo · Scarlands x AA_CrystallineCaracal
        TropicalSwamp x Titan     · ZBiome_DesertOasis x TYR_KangarooRat

    They are missing because OUR OWN REMOVAL ALREADY WORKED. The capture is taken
    after every PatchOperation, so a pair we have already fixed is invisible in it -
    the fix hides its own evidence.

    ⇒ ⛔ NEVER let this section REPLACE the shipped de-dup files. It is a floor, not a
    roster: regenerating over them would drop those five removals and the five pairs
    would come straight back on the next load, with nothing in any log naming them.
    ✅ The shipped de-dup must always be the UNION of every pair ever found. That is
    why src/Jawa/Jawa_Patches/Patches/BiomeCast_Ashkarr.xml carries the CAST SECTION
    ONLY, and the de-dup lives in its own accumulating files.
    """
    import re
    roots = ['/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100',
             '/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods',
             '/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data']
    out = collections.defaultdict(set)
    pat = re.compile(r'<ThingDef\b.*?</ThingDef>', re.S)
    wb = re.compile(r'<wildBiomes>(.*?)</wildBiomes>', re.S)
    dn = re.compile(r'<defName>([^<]+)</defName>')
    # ⚠️ PRUNE, DO NOT GLOB. A recursive glob over the 1,254 workshop mods on this
    # mount ran past seven minutes and had to be killed. Walking with the art and
    # audio trees pruned takes seconds, because those directories hold the
    # overwhelming majority of the files and none of the defs.
    SKIP = {'Textures', 'Sounds', 'Languages', 'Assemblies', 'About',
            'News', 'Source', 'Materials', '.git'}
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dp, dnames, fnames in os.walk(root):
            dnames[:] = [d for d in dnames if d not in SKIP]
            for fn in fnames:
                if not fn.endswith('.xml'):
                    continue
                try:
                    txt = open(os.path.join(dp, fn), encoding='utf-8-sig',
                               errors='replace').read()
                except OSError:
                    continue
                if '<wildBiomes>' not in txt:
                    continue
                for m in pat.finditer(txt):
                    blk = m.group(0)
                    w, d = wb.search(blk), dn.search(blk)
                    if not w or not d:
                        continue
                    for b in re.findall(r'<([A-Za-z0-9_]+)>[^<]*</\1>', w.group(1)):
                        out[b].add(d.group(1))

    # ---- and the post-patch half, from the newest capture --------------------
    # A collision a PatchOperation creates exists in no def file. The capture is
    # taken from the running game after every patch has applied, so it is the only
    # offline source that can see one.
    for cap in captures_newest_first():
        f = os.path.join(cap, 'defs', 'ThingDef.json')
        if not os.path.isfile(f):
            continue
        try:
            td = json.load(open(f, encoding='utf-8'))
        except (OSError, ValueError):
            continue
        td = td if isinstance(td, list) else td.get('defs') or []
        added = 0
        for t in td:
            if not isinstance(t, dict):
                continue
            race = (t.get('fields') or {}).get('race')
            if not isinstance(race, dict):
                continue
            wbio = race.get('wildBiomes')
            if not wbio:
                continue
            biomes = wbio.keys() if isinstance(wbio, dict) else [
                x.get('biome') for x in wbio if isinstance(x, dict)]
            for b in biomes:
                if b and t.get('defName') and t['defName'] not in out[b]:
                    out[b].add(t['defName'])
                    added += 1
        print(f"   animal-side: +{added} pair(s) only the capture could see "
              f"({os.path.basename(cap)})")
        break          # newest capture only; older ones describe a different mod set
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

    # 🔴 WHAT THE OWNER ALREADY CUT. Measured 2026-08-26 and it explains 167 of the
    # 168 animals that read commonality 0 in the live game.
    #
    # Cherry Picker (owlchemist.cherrypicker) removes a def by the OWNER'S OWN
    # selection, saved in Config/Mod_3521312241_Mod_CherryPicker.xml - the count
    # grows every review pass, so `cherrypicker.load().provenance()` above prints
    # the CURRENT one rather than a number that goes stale in this comment.
    # ⚠️ Its cuts are INVISIBLE TO THE DEF DUMP: all nine of the animals it cut
    # out of TemperateForest are still PRESENT as ThingDef and PawnKindDef in the
    # capture. What changes is the biome record's commonality, which becomes 0 - and
    # `BiomeDef.AllWildAnimals` only yields kinds above 0, so the animal can never be
    # chosen.
    #
    # Validated across the whole population, not on a sample: 167 of 168 always-off
    # animals are in this list, and 0 of 414 always-alive animals are. The single
    # exception, CorellianHound, is zeroed only in biomes this file does not write.
    #
    # ⇒ Casting one of these writes an entry that CANNOT SPAWN, and nothing reports
    # it. They are commented out below rather than emitted, which is functionally
    # identical - the live commonality is 0 either way - and makes the loss visible.
    CUT = _cherry_picker_cuts()

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
    cut_rows = []

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
            if CUT is not None and r['defName'] in CUT:
                # Cut by the owner. Emitting it would write an entry the engine
                # resolves to commonality 0 - registered and unspawnable.
                cut_rows.append((b, r['defName']))
                parts.append(f'          <!-- CUT {r["defName"]} - {r["label"]}:'
                             f' removed by Cherry Picker, would read commonality 0 -->')
                continue
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
    # ================================================================
    # THE DE-DUP, EMITTED WITH THE CAST SO THE TWO CANNOT DRIFT
    # ================================================================
    # 🔑 This used to live in a hand-maintained AnimalBiomeDuplicates_Fix.xml, and
    # that is exactly how the 2026-08-22 regression happened: the cast was
    # regenerated, the hand file was not, and 30 collisions shipped. Generating both
    # from one run means a regeneration can never reintroduce them.
    #
    # DIRECTION: always remove the ANIMAL-side wildBiomes entry, never our roster.
    # Nothing is lost in play - our own roster still spawns the animal in that biome,
    # at the commonality we chose.
    aside = _animal_side_biomes()
    dups = []
    for b in sorted(byb):
        cast_here = {r['defName'] for r in byb[b] if r['defName'] in PAWNKINDS}
        for a in sorted(cast_here & aside.get(b, set())):
            dups.append((b, a))
    if dups:
        parts.append('  <!-- ============================================================')
        parts.append('       DE-DUP: the animal-side wildBiomes entries our own roster')
        parts.append('       collides with. Generated WITH the cast above, deliberately -')
        parts.append('       a hand-maintained copy is what let 30 of these ship on')
        parts.append('       2026-08-22. BIOME_CAST_DUPLICATE_ANIMALS_1.')
        parts.append('')
        parts.append('       Same animal reaching one biome from BOTH directions throws')
        parts.append('       ArgumentException in BiomeDef.CommonalityOfAnimal, and the')
        parts.append('       half-built cache it leaves behind silently zeroes every')
        parts.append('       animal that would have registered after it - for the rest')
        parts.append('       of the session, with no further error.')
        parts.append(f'       {len(dups)} pair(s) this run. Sourced from the mod XML on disk')
        parts.append('       AND from the newest def dump capture, because a collision a')
        parts.append('       PatchOperation creates exists in no def file at all - which is')
        parts.append('       how 27 of them shipped on 2026-08-26 against a disk-only scan.')
        parts.append('')
        parts.append('       🔴 THIS LIST IS A FLOOR, NOT A ROSTER. The capture is taken AFTER')
        parts.append('       every PatchOperation, so a pair our own removal ALREADY FIXED is')
        parts.append('       invisible here - the fix hides its own evidence. Measured')
        parts.append('       2026-08-26: 56 found, 61 shipped, and the 5 absent ones were all')
        parts.append('       already-working removals. ⛔ Never let this section REPLACE the')
        parts.append('       shipped de-dup files; the shipped set must be the UNION of every')
        parts.append('       pair ever found. That is why the deployed cast patch carries the')
        parts.append('       CAST SECTION ONLY.')
        parts.append('       ============================================================ -->')
        parts.append('')
        for b, a in dups:
            xp = f'/Defs/ThingDef[defName="{a}"]/race/wildBiomes/{b}'
            parts.append('  <Operation Class="PatchOperationConditional">'
                         f'   <!-- {a} x {b} -->')
            parts.append(f'    <xpath>{xp}</xpath>')
            parts.append('    <match Class="PatchOperationRemove">')
            parts.append(f'      <xpath>{xp}</xpath>')
            parts.append('    </match>')
            parts.append('  </Operation>')
        parts.append('')
    parts.append('</Patch>')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(parts))
    print(f"wrote {OUT}: {len(byb)} biomes, {len(rows)} records, "
          f"{len(dups)} duplicate pair(s) de-duped")
    nomay = [b for b in byb if not PKG.get(b)]
    if nomay:
        print(f"⚠️ no packageId resolved for: {nomay} - BUILD must confirm the MayRequire")
    # 🔴 COVERAGE, REPORTED EVERY RUN. BiomeCypreJungle (191 tiles) and
    # COMIGO_GreaterSwamp_Tropical (60) sat on Ash'karr with NO cast at all until
    # 2026-08-26, so both kept their mod-default rosters - ten Earth animals each,
    # raccoon included - while every count in this pipeline read as healthy. A biome
    # this file does not write is a biome somebody else's defaults own.
    try:
        import csv as _csv, collections as _c
        _root = os.path.normpath(os.path.join(FA, '..', '..', '..'))
        _t = _c.Counter(r['biome'] for r in _csv.DictReader(
            open(os.path.join(_root, 'world', 'ASHKARR_WORLDMAP_tiles.csv'), encoding='utf-8')))
        _ash = {b: n for b, n in _t.items() if b not in ('Ocean', 'Lake')}
        _missing = {b: n for b, n in _ash.items() if b not in byb}
        if _missing:
            print(f"\n🔴 {len(_missing)} Ash'karr biome(s) get NO cast from this file and keep "
                  f"whatever their mod ships:")
            for b, n in sorted(_missing.items(), key=lambda kv: -kv[1]):
                print(f"     {b:34s} {n:5d} tiles")
            print("   ⇒ Run refill_cast.py; it fills a missing biome's whole pyramid.")
        else:
            print(f"\n✅ coverage: all {len(_ash)} Ash'karr biomes are cast by this file.")
    except Exception as _e:
        print(f"⚠️ UNMEASURED: could not check Ash'karr biome coverage ({_e}). A biome with "
              f"no cast would be invisible in this run.")

    if cut_rows:
        by_animal = {}
        for b, d in cut_rows:
            by_animal.setdefault(d, []).append(b)
        print(f"\n🔴 {len(cut_rows)} cast entries CUT BY CHERRY PICKER across "
              f"{len(by_animal)} animal(s) - the owner removed these, so an emitted "
              f"entry would read commonality 0 and never spawn:")
        for d in sorted(by_animal):
            print(f"     {d:34s} {', '.join(sorted(by_animal[d]))}")
        print("   ⇒ Those biomes are now that many animals lighter. Replacing them is a "
              "CONTENT call: CAST_NAMES_UNSPAWNABLE_ANIMALS_1.")

    if skipped:
        print(f"⚠️ {len(skipped)} cast entries SKIPPED - not PawnKindDefs, so wildAnimals "
              f"could not resolve them:")
        for b, d in skipped:
            print(f"     {b:<30} {d}")

if __name__ == '__main__':
    main()
