# Missing North Facings — Vanilla Gravship Expanded — validation walk
subject: src/RimMandrake/GravshipAstronautFix  (packageId `mandrake.rm.gravshipastronautfix`)
deps: `vanillaexpanded.gravship` (Vanilla Gravship Expanded - Chapter 1, third-party, hard modDependency)
list: minimal+vanillaexpanded.gravship
status-hint: pure loose-texture supply mod, no defs and no code — ships the donor's own north-facing bytes at the CORRECT filenames its PawnKindDef already asks for (donor's files are misspelled "Astrronaut"), plus a baked 180-rotated north for the gravship gene bank the donor never shipped at all

## must be true
- This mod has no ThingDef, no PawnKindDef, no C# assembly, no Harmony patch — it is three loose PNGs at exact texPaths the DONOR's own defs already declare. There is nothing here for a patch or a def-read-back to check; the entire correctness claim is "the right bytes exist at the right path and this mod loads after the donor".
- `Things/Pawns/Mechanoid/Astronaut/MechAncient_Astronaut_north.png` must exist, 256x256.
- `Things/Pawns/Mechanoid/Astronaut/Allegiance_Mech_Astronaut_north.png` must exist, 256x256 (the shared allegiance mask used by BOTH astronaut life stages).
- `Things/Structures/GravshipGenebank/GravshipGenebank_north.png` must exist, 128x128, and must NOT be pixel-identical to `GravshipGenebank_south.png` (the whole point — the donor's own unrotated south substitution would be).
- LOAD ORDER: this mod must load AFTER `vanillaexpanded.gravship` (declared in `loadAfter`), because it overrides loose files at paths the donor also ships, and RimWorld resolves loose-file collisions by load order.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.gravshipastronautfix" (trivially true — no defs to error) and no "Failed to find any textures at" naming `MechAncient_Astronaut` or `GravshipGenebank`   # load-time
2. [D] confirm this mod is present and ordered AFTER `vanillaexpanded.gravship` in the live `ModsConfig.xml` activeMods list — the correctness of every fix here depends entirely on this ordering, and it is the one thing an automated check CAN assert without a screenshot
3. [D] file check (not a def read-back — no def exists): the three PNGs above exist under the deployed mod's `Textures/` folder at the exact paths named, with the dimensions given (measure with an image tool, never `wc`/`file` alone per the measuring-large-artifacts skill if any doubt)
4. [B] jawa/pawn_atlas or jawa/pawn_portrait on a live `VGE_Astronaut` pawn (life stage 2, ancient) rotated to face `Rot4.North` → confirm the returned texture is NOT a mirrored south view (this is the one runtime signal available; full visual confirmation is [S] below)

## [S]
The actual visual correctness of the north-facing astronaut (both life stages) and the gene bank's back view, walking the pawn/rotating the building in-game and looking at it, is the human-pass concern this mod exists to satisfy (MOD_HUMAN_EXPLORATION_PASS_1) — the whole defect ("Failed to find any textures" never fires for one missing direction) means no automated log signal can prove the fix beyond step 4's rotation check.
