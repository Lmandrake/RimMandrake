# DESERT_FAMILY_PORT_EXECUTION_1 — SWAC batch B report

Batch: `Transient/desert_port_batches/SWAC_B.json` (30 fauna + 4 flora, all
Star Wars Animal Collection / mlie).

## verdict

**34 / 34 species ported** (30 fauna + 4 flora) — CONFIRMED. Full reference
closure done: 18 custom BodyDefs + 9 custom BodyPartDefs, 15 leather + 13 meat
ThingDefs (deduped, shared across species), 24 egg ThingDefs, 4 raw-food
ThingDefs. Written to
`/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/`:

- `RSW_DesertPortB_Races.xml` — 30 ThingDef+PawnKindDef pairs
- `RSW_DesertPortB_Bodies.xml` — 18 BodyDefs + 9 BodyPartDefs
- `RSW_DesertPortB_Materials.xml` — 15 leather + 13 meat ThingDefs
- `RSW_DesertPortB_Eggs.xml` — 24 egg ThingDefs
- `RSW_DesertPortB_Plants.xml` — 4 flora ThingDefs (base+wild flattened) + 4
  raw-food ThingDefs

Copied the `BMT_FAUNA_ABSORPTION_1` precedent (read its header comment in
`RSW_BiomesTeamPort_Races.xml` first): reference closure so nothing dangles,
donor-framework `modExtensions` dropped (`NocturnalAnimals.ExtendedRaceProperties`
and `PathfindingFramework.MovementExtension`, both `MayRequire` an inactive
mod — 2 species each), `ADogSaidBody` donor attribute dropped, custom
`nameGenerator`/`nameGeneratorFemale` dropped (donor RulePack not ported —
falls back to default animal naming; noted as a content loss, not a defect).
Vanilla comps kept as-is: `CompProperties_EggLayer`, `CompProperties_Milkable`,
`CompProperties_Shearable`, `CompProperties_WakeUpDormant`,
`CompProperties_CanBeDormant` — all Core, no closure needed.

**Flight preserved per the standing flyer rule**: Uvak (flying reptavian,
`MaxFlightTime`/`FlightCooldown`/`flightStartChanceOnJobStart`/
`canFlyIntoMap`/`canLeaveMapFlying` + `flyingAnimationFramePathPrefix`/
`flyingAnimationFrameCount` all carried through unchanged).

**ONE DEPARTURE honoured**: texPaths point at the donor's own literal texture
path (e.g. `swanimals/Uvak/Uvak`), each preceded by a loud
`<!-- TEMP PLACEHOLDER: donor SWAC texture, replace when the RSW_ art job
lands -->` comment, per the item's explicit instruction — works today because
`mlie.starwarsanimalcollection` is still active; CONFIRMED resolving with 0
errors once `validate_patch.py` was pointed at the real Mods/Data/Workshop
roots (see below).

**Could not port (documented, not silently dropped):**
- Per-species `soundWounded`/`soundDeath`/`soundCall`/`soundAngry` (e.g.
  `Pawn_Uvak_Wounded`) — donor audio ships inside an AssetBundle
  (`vendor/mod_sources/StarWarsAnimalCollection_src` has no loose `Sounds/`
  folder), not extractable this pass. Dropped cleanly (no dangling ref);
  generic `soundMeleeHitPawn`/`HitBuilding`/`Miss`/`soundEating` ARE vanilla
  Core SoundDefs (confirmed 0 matches for those names in the donor's own
  `SoundDefs/Sounds_SWanimals.xml`) and were kept unchanged.
- Custom naming RulePacks (`SWAnimalNamerMale/Female`) — dropped, not ported.
- `GreaterKraytDragon`'s dessicated-stage texPath carries a donor-side typo
  (`swanimals/KGreaterKraytDragon/...`, extra leading `K`) — reproduced
  verbatim as-is since it's the donor's own data, flagged by the validator as
  a WARN, harmless (dessicated art rarely seen).

## canon vs drafted

**0 drafted renames — all 34 species keep their donor names.** Every fauna and
flora name in this batch (Uvak, Varactyl, Zeer, Falumpaset, Grank, Jakobeast,
Nerf, Qormot, Shaak, Strill, TeeMuss, WarWyrm, Cannok, KraytDragon,
Whisperbird, Bolotaur, Clodhopper, FeralGrazer, GraniteSlug, Krykna, Pikobis,
Runyip, Convor, Vulptex, Voorpak, FeralNerf, Porg, Horax,
KowakianMonkeyLizard, GreaterKraytDragon, chak-root, nysillin, hubba gourd,
bloddle) is a real Wookieepedia-sourced Star Wars species/crop name, not a
donor invention — SWAC's own design only includes named-in-canon creatures.
Item text itself lists `Varactyl` and `KraytDragon` as canon examples. UNCERTAIN
only in the sense that most of these 30 don't have an entry in
`design/RimStarWars/canon_references/` (137-entry library covers 45
creatures/69 species/23 droids, not the whole SW bestiary) — absence of a
canon-reference entry is not evidence of non-canon per
`NONCANON_BEAST_RENAME_1`'s own design ("agent drafts, owner reacts" only
applies when a name is NOT already a real SW name). No renames were drafted.

## art jobs filed

**94 jobs filed to `infrastructure/artpipe/pending/`** via `fill_queue.py`
only (never hand-written), 0 duplicates, 0 row errors. 30×3 facings
(south/east/north) for fauna + 4 single-view for flora. `id` prefix
`desertportb_<defname-lower>[_facing]`, `rimflow_item_id` =
`DESERT_FAMILY_PORT_EXECUTION_1`. Canvas computed via the project's own
`artpipe/common.canvas_for_cells()` (drawSize×128, next power of two, clamped
[256, 1024]) — e.g. Uvak/Varactyl/Zeer/Falumpaset/Jakobeast/Bolotaur 512,
WarWyrm/KraytDragon/Horax/GreaterKraytDragon 1024 (clamped, not 2048), small
species (Voorpak, GraniteSlug, Porg, etc.) 256. Prompts built from each
species' real donor description text, painterly-vanilla-RimWorld style
boilerplate, no `reference=` set (avoids triggering reskin-validate per the
known trap).

## validate_patch.py result

**0 errors, 8 warnings, all 5 files.** First run without `--defs` gave 15
false ERRORs (texPath-not-found under `swanimals/`) — expected, since
`--defs` wasn't pointed at the live Mods/Data/Workshop roots yet and the tool
can only see this mod's own `Textures/`. Re-run with
`--defs "/mnt/c/.../RimWorld/Mods" --defs "/mnt/c/.../RimWorld/Data" --defs
"/mnt/c/.../workshop/content/294100" --live <latest DefDump capture>
--mods-config infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`
resolved cleanly: `RSW_DesertPortB_Bodies.xml` 0/0, `Materials.xml` 0/0,
`Eggs.xml` 0/0, `Plants.xml` 0 err/8 warn, `Races.xml` 0 err/1 warn. Remaining
warnings are all "texPath not found under any scanned loose-file root" for
paths that live inside SWAC's AssetBundle (the documented AssetBundle-only
trap) — not dangling references, confirmed functional since the donor mod is
still active.

## absolute paths

- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Races.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Bodies.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Materials.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Eggs.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml`
- `/mnt/d/Luke/dev/Rimworld/infrastructure/artpipe/pending/desertportb_*.json` (94 files)
- Donor source read from `/mnt/d/Luke/dev/Rimworld/vendor/mod_sources/StarWarsAnimalCollection_src/`

Not committed, not deployed, bridge untouched — parent does both, per the
brief.
