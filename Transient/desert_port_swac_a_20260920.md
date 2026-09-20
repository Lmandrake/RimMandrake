# SWAC batch A desert port — 34 species — DONE (defs authored, art filed, validated)

Batch: `/mnt/d/Luke/dev/Rimworld/Transient/desert_port_batches/SWAC_A.json`
Precedent read: `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml` header (`BMT_FAUNA_ABSORPTION_1`).

## Files written (all under `src/RimStarWars/SWBestiary/Defs/DesertPort/`, `RSW_DesertPortA_` prefix)

- `RSW_DesertPortA_BodyParts.xml` — 7 BodyPartDef + 7 BodyPartGroupDef
- `RSW_DesertPortA_Bodies.xml` — 21 BodyDef
- `RSW_DesertPortA_Items.xml` — 56 resource ThingDefs (13 leather, 14 meat, 2 wool, 1 milk, 26 eggs)
- `RSW_DesertPortA_Sounds.xml` — 114 SoundDef
- `RSW_DesertPortA_Races.xml` — 34 ThingDef + 34 PawnKindDef (the species)

Generated via a Python/ElementTree script (not hand-typed) reading the vendored donor
source at `vendor/mod_sources/StarWarsAnimalCollection_src/1.6/Defs/` — reference
closure computed and measured, not guessed: bodies, body parts/groups, leather/meat/
wool/milk/egg ThingDefs and SoundDefs actually referenced by the 34 target ThingDefs
were extracted, everything already vanilla-Core (checked by presence/absence in the
donor's own files) was left as a bare reference, everything donor-defined was ported
and renamed `RSW_`. All 5 comp classes used by this batch (`CompProperties_Shearable`,
`_Milkable`, `_EggLayer`, `_CanBeDormant`, `_WakeUpDormant`) are vanilla Core classes —
nothing donor-framework-specific needed dropping.

## VERDICT — 34 of 34 species ported

Every species in SWAC_A.json got a full ThingDef + PawnKindDef (stats, comps, tools,
race block, life stages) with defName closure. CONFIRMED via the generation script's
own assertions (34 found in donor / 34 written) and `validate_patch.py`.

## Canon vs drafted — 0 drafted

All 34 are attested Star Wars canon creatures — the donor mod's own flavor text is
Wookieepedia-sourced canon lore for each (Bantha, Eopie, Ronto, Massiff, Shyrack,
Mynock, Gizka, Womp Rat and 27 others). None needed a `NONCANON_BEAST_RENAME_1` draft;
species names and defNames were kept, only `RSW_`-prefixed. CONFIRMED by reading each
description field (pulled straight from the donor XML) — they are all sourced lore,
not invented flavor text. 10 of the 34 also have a curated entry in
`design/RimStarWars/canon_references/`: anooba, bantha, corinathoth, eopie, gizka,
iriaz, kreetle, mudhorn, nuna, ronto — those 10 were graded against their `## Must
show` checklists for the art prompts; the other 24 have no curated entry yet but are
still real canon per the sourced description (UNCERTAIN whether any of those 24
deserve a canon_references entry of their own — not this item's job to author one).

## Art — 102 jobs filed (34 species × 3 facings)

`python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input
Transient/desert_port_batches/SWAC_A_artjobs.json` — 102 filed, 0 duplicates, 0 row
errors. CONFIRMED (`ls infrastructure/artpipe/pending | grep desert_swaca` = 102 at
filing time; some may already show as claimed/moved to `active/` by the daemon).
`rimflow_item_id: DESERT_FAMILY_PORT_EXECUTION_1` on every job. Canvas sized per the
artpipe README rule (`drawSize×128`, next power of two, floor 256) from each species'
own adult (last) lifeStage `bodyGraphicData.drawSize` — 32 of 34 came out at floor
256; the largest (Ronto, drawSize 7.0) and Mudhorn (4.5) landed higher.

Until renders land, every texPath in `RSW_DesertPortA_Races.xml` (and the item
files' icons) still points at the DONOR's own existing texture path
(`swanimals/...`) as a loudly-commented temporary placeholder — see the file-level
banner comment at the top of each generated file. This is NOT final art; the owner
ruled it must not be ("our own version of creature and art").

## `validate_patch.py` result

Command: `validate_patch.py <5 files> --defs "<Steam RimWorld>" --defs "<Workshop
294100>" --defs "<Steam RimWorld>/Mods" --defs src --live "<today's fresh DefDump
capture, 2026-09-20T15-42-42Z>" --mods-config
infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`

`BodyParts`, `Bodies`, `Items`, `Sounds` — **OK, 0 errors, 0 warnings** each.
`Races` — **FAIL, 4 errors**, all texPath-existence findings tied to the *donor's
own* texture set, not to the port:
- `RSW_Mynock`'s `Mynock_Dessicated` texPath (×3, one per facing lifeStage):
  the validator can't see it because it's AssetBundle-only donor art (the known
  `Star Wars Animal Collection ships AssetBundle-only art` trap) — CONFIRMED present
  in `observed/inventory/bundle_textures/mlie.starwarsanimalcollection/.../mynock_dessicated.png`.
  Not a real gap; the validator's loose-file scan just can't see into the bundle.
- `RSW_Igitz`'s `Igitz_j_Swimming` texPath: genuinely absent even from the donor's
  own extracted bundle cache (only adult `igitz_swimming_*` exists, no juvenile
  `igitz_j_swimming_*`) — a pre-existing donor-mod gap, carried over verbatim.
  CONFIRMED absent from `observed/inventory/bundle_textures`.

Both are placeholder-texPath findings that resolve automatically once each
species' own art job lands and its texPath is repointed — non-blocking for this
port. All other structural/reference checks (defName, ParentName resolution, Class
attributes, xpath) passed clean.

## Could NOT port — none

All 34 species in the batch were ported; nothing was skipped.

## Absolute paths written

- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_BodyParts.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Bodies.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Items.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Sounds.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Races.xml`
- `/mnt/d/Luke/dev/Rimworld/Transient/desert_port_batches/SWAC_A_artjobs.json` (fill_queue input, kept for provenance)
- 102 job files under `/mnt/d/Luke/dev/Rimworld/infrastructure/artpipe/pending/desert_swaca_*.json` (some may have moved to `active/` by now)

Not committed, not deployed, bridge untouched — per the brief, the parent handles that.
