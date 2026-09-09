#!/usr/bin/env python3
"""Generate BiomeFishTypes_Ashkarr.xml — BiomeDef.fishTypes patches for waters
FISH_BY_BIOME_1 ruled fish=YES that are NOT already covered by another window's
sand-fishing work (src/RimUtinni/UtinniPatches/Patches/SandFishing_CrackedLands.xml,
read-only reconciliation input, never edited/generated here).

Reads  design/Jawa/worldbuilding/biomes/rosters/_fish_candidates.json  (the census:
       confident/secondary donor candidates per ruled-yes water, MEASURED fish
       ThingDef inventory, and the fishTypes mechanics — four buckets:
       freshwater_Common/Uncommon, saltwater_Common/Uncommon)
Writes src/RimUtinni/UtinniPatches/Patches/BiomeFishTypes_Ashkarr.xml

Scope, decided by reconciliation (see FISH_BY_BIOME_1.md progress note):
  - weeping_stones / ZBiome_DesertOasis: WRITTEN. 4 confident swfish_ donors
    (Common) + 4 secondary VCEF_ donors (Uncommon), replacing the vanilla
    Earth-named Fish_Tilapia/Fish_Piranha the donor mod ships by default.
  - the_cracked_lands / ZBiome_Badlands: SKIPPED. The other window's
    SandFishing_CrackedLands.xml already replaces both freshwater buckets and
    the rareCatchesSetMaker on this exact def — left entirely to them.
  - the_greentide / BiomeCypreJungle: SKIPPED. Not written here even though
    the roster claims it is "already assigned" — verified against the live def
    (RUT_Greentide.xml, no fishTypes block at all) and the donor XML
    (BiomeCast_Ashkarr.xml): RSW_Mee/Faa/Laa are wired into a *wildAnimals*
    bucket on a DIFFERENT biome (RUT_Miasma / AB_MiasmicMangrove), not into
    BiomeCypreJungle's/RUT_Greentide's fishTypes. The roster's claim does not
    hold; flagged in the item note as a real gap, not fixed here (out of this
    pass's instructed scope).

Species -> donor packageId (MayRequire) is a small fixed table below: the
census's own "mod" field carries human-readable mod names, not packageIds, and
one of them (VCEF_) is misleading — those defs are ParentName="AB_RawFishBase",
shipped BY Alpha Biomes (sarg.alphabiomes), not by a separate "Vanilla Fishing
Expanded" package, confirmed by reading the live donor XML on disk (workshop
id 1841354677, About.xml packageId sarg.alphabiomes) rather than trusting the
census's "unresolved" note.

Shape verified against live Core/Odyssey BiomeDef XML (never guessed):
Data/Core/Defs/BiomeDefs/Biomes_Cold.xml, Data/Odyssey/Defs/BiomeDefs/Glowforest.xml
-- <fishTypes MayRequire="Ludeon.RimWorld.Odyssey"> wrapping freshwater_Common/
freshwater_Uncommon/saltwater_Common/saltwater_Uncommon/rareCatchesSetMaker,
each bucket a flat dict of {defName: weight} with weight typically 1 (the
bucket, not the weight, carries the rarity tier -- confirmed again by reading
the live ZBiome_DesertOasis.xml, which ships exactly this shape already,
populated with Earth-named vanilla fish this pass replaces).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CANDIDATES = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biomes', 'rosters', '_fish_candidates.json')
OUT = os.path.join(ROOT, 'src', 'RimUtinni', 'UtinniPatches', 'Patches', 'BiomeFishTypes_Ashkarr.xml')

# donor defName -> MayRequire packageId, verified against each donor's live
# About.xml on disk (never guessed from the census's mod-name strings).
DONOR_PACKAGE_ID = {
    'swfish_Burra': 'mlie.starwarsanimalcollection',
    'swfish_Daggert': 'mlie.starwarsanimalcollection',
    'swfish_Nyork': 'mlie.starwarsanimalcollection',
    'swfish_See': 'mlie.starwarsanimalcollection',
    'VCEF_FrigidSwimmer': 'sarg.alphabiomes',
    'VCEF_Slimefish': 'sarg.alphabiomes',
    'VCEF_Spinyfish': 'sarg.alphabiomes',
    'VCEF_OcularFish': 'sarg.alphabiomes',
}

# water key -> (biome defName, owning-mod name for PatchOperationFindMod)
WATERS = {
    'weeping_stones': ('ZBiome_DesertOasis', 'More Vanilla Biomes'),
}


def _split_defs(raw):
    # the census sometimes packs several defNames into one candidate's "def"
    # field as a "/"-separated string (its own secondary-PASS rows) rather
    # than one row per def -- split defensively instead of assuming 1:1.
    return [d.strip() for d in raw.split('/') if d.strip()]


def confident_and_secondary(candidates):
    confident, secondary = [], []
    for c in candidates:
        verdict = c.get('verdict')
        if verdict == 'PASS':
            confident.extend(_split_defs(c['def']))
        elif verdict == 'secondary PASS':
            secondary.extend(_split_defs(c['def']))
    return confident, secondary


def bucket_xml(bucket_name, defnames, indent):
    pad = ' ' * indent
    lines = [f'{pad}<{bucket_name}>']
    for d in defnames:
        pkg = DONOR_PACKAGE_ID[d]
        lines.append(f'{pad}  <{d} MayRequire="{pkg}">1</{d}>')
    lines.append(f'{pad}</{bucket_name}>')
    return '\n'.join(lines)


def conditional_replace_op(biome_def, bucket_name, defnames, indent=8):
    pad = ' ' * indent
    xpath = f'/Defs/BiomeDef[defName="{biome_def}"]/fishTypes/{bucket_name}'
    inner = bucket_xml(bucket_name, defnames, indent + 6)
    return (
        f'{pad}<li Class="PatchOperationConditional" MayRequire="Ludeon.RimWorld.Odyssey">\n'
        f'{pad}  <xpath>{xpath}</xpath>\n'
        f'{pad}  <match Class="PatchOperationReplace">\n'
        f'{pad}    <xpath>{xpath}</xpath>\n'
        f'{pad}    <value>\n'
        f'{inner}\n'
        f'{pad}    </value>\n'
        f'{pad}  </match>\n'
        f'{pad}</li>'
    )


def generate():
    with open(CANDIDATES, encoding='utf-8') as f:
        census = json.load(f)

    ops = []
    covered = []
    for water_key, (biome_def, mod_name) in WATERS.items():
        water = census['per_water'][water_key]
        confident, secondary = confident_and_secondary(water['candidates'])
        ops.append(conditional_replace_op(biome_def, 'freshwater_Common', confident))
        ops.append(conditional_replace_op(biome_def, 'freshwater_Uncommon', secondary))
        covered.append((water_key, biome_def, mod_name, confident, secondary))

    assert len(covered) == 1, 'this pass writes exactly one water; extend WATERS deliberately, not silently'
    _, biome_def, mod_name, confident, secondary = covered[0]

    ops_xml = '\n\n'.join(ops)

    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  FISH_BY_BIOME_1 === biome wiring: sets `{biome_def}` (weeping_stones, the true
  pools) fishTypes to recognizability-clean analogs, replacing the vanilla
  Earth-named Fish_Tilapia/Fish_Piranha the donor mod (More Vanilla Biomes)
  ships by default on this def.

  GENERATED by design/Jawa/mods/gen_fish_types.py from the FISH_BY_BIOME_1
  census (design/Jawa/worldbuilding/biomes/rosters/_fish_candidates.json).
  Do not hand-edit; rerun the generator.

  Donors: freshwater_Common gets the 4 confident swfish_ analogs (Star Wars
  Animal Collection; invented names, no Earth root, clear the sheet's own
  bans on pollution/ambush flavor for a sacred oasis pool). freshwater_Uncommon
  gets the 4 secondary VCEF_-prefixed picks, which are actually shipped BY
  Alpha Biomes (ParentName="AB_RawFishBase", packageId sarg.alphabiomes;
  verified on the live donor XML, not the census's "unresolved" mod field).
  Both buckets use flat weight 1, matching vanilla's own convention where the
  bucket, not the weight, carries the rarity tier.

  Only freshwater is touched. `{biome_def}` also carries saltwater_Common/
  Uncommon in the donor's own default def; weeping_stones' roster ruling is a
  standing fresh-water pool with no sea, so saltwater is left as the donor
  mod's own default, untouched, same as the sibling SandFishing_CrackedLands.xml
  pattern (freshwater only) for `ZBiome_Badlands`.

  Wrapped in PatchOperationConditional (checking the target bucket xpath
  exists) rather than a bare PatchOperationReplace, so a shape change in the
  donor def fails the conditional instead of silently matching nothing;
  confirm with validate_patch.py's live-dump and defs-dir checks, since PatchOperationConditional
  and PatchOperationFindMod both report success even on a false condition
  (CLAUDE.md's own warning); the conditional is a defensive shape check, not a
  substitute for validating the actual applied result.

  the_cracked_lands / ZBiome_Badlands is deliberately NOT touched here; the
  other window's SandFishing_CrackedLands.xml already replaces both freshwater
  buckets and rareCatchesSetMaker on that exact def. the_greentide /
  BiomeCypreJungle is also NOT touched; the roster's "already assigned"
  claim for RSW_Mee/Faa/Laa did not hold on inspection (they are wired into a
  wildAnimals bucket on a different biome, RUT_Miasma, not into this biome's
  fishTypes); that gap is recorded in the item note, not fixed in this pass.
-->
<Patch>

  <Operation Class="PatchOperationFindMod">
    <mods>
      <li>{mod_name}</li>
    </mods>
    <match Class="PatchOperationSequence">
      <success>Always</success>
      <operations>

{ops_xml}

      </operations>
    </match>
  </Operation>

</Patch>
'''

    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(xml)

    print(f'wrote {OUT}')
    print(f'  {biome_def} freshwater_Common <- {confident}')
    print(f'  {biome_def} freshwater_Uncommon <- {secondary}')


if __name__ == '__main__':
    generate()
