# MLIE_ABSORPTION_BIOME_WIRING_1 — 98 live biome rows still name the bare donor for creatures we already ported

**CLOSED 2026-09-25.**

## re-measurement, 2026-09-25 — the 98/73 figure had already moved a lot

The 2026-09-23 measurement counted bare `mlie.starwarsanimalcollection` rows directly in the
11 RUT_ twin BiomeDef XMLs. By 2026-09-25 **all 11 of those twins are FROZEN** (their content
migrated to standalone `RM_` mods during this session's biome-split wave; two were renamed —
`AridShrubland`→`LeaningScrub`, `CrackedLands`→`FloodedCanyon`) — so the live wiring surface
moved entirely to the `WildAnimals_<Biome>.xml` Utinni patches that target the new `RM_`
defNames. Re-parsing those patches (not the frozen twins, which this item's own "Watch out"
forbids editing) found:

| figure | value |
|---|---|
| donor-gated rows across the 11 biomes' live patch layer (fresh scan) | 58 |
| already incidentally fixed before this pass (Greentide 20/20, TheForge, WeepingStones — clean) | confirmed 0 violations in those 3 |
| Webwork's 2 rows: CUT by `WEBWORK_FAUNA_ROSTER_1` mid-session (file now `<Patch></Patch>`, retired) — not fixed by this item, already moot |
| **genuine violations found and fixed this pass** | **55**, across 7 files: FeverWood(7), FloodedCanyon(5), LeaningScrub(31), Miasma(7), PoisonForest(3), Warscar(1), Wasteland(1) |
| no-port remainder (leave alone, no RSW_ port exists) | 3 — `Plant_HydenockTree_Wild`, `Plant_JoganTree_Wild` (FeverWood), `Plant_TookeTrap_Wild` (Webwork) |
| **violations remaining after this pass** | **0** |

Method: built the set of every `RSW_` `ThingDef`/`PawnKindDef` defName under `src/RimStarWars`
(927 ThingDef/PawnKindDef names), then for every donor-gated (`MayRequire` containing
`mlie.starwarsanimalcollection`) row in the 11 biomes' `WildAnimals_*.xml` patches (and the
`RM_` BiomeDef files themselves, inline), checked whether `RSW_<name>` (or
`RSW_Leather_<name>`) exists. A row is a genuine violation only when a port exists; a row with
no port is left untouched. Confirmed pairing for all 46 distinct animal names retargeted: every
one has **both** a `ThingDef` and a `PawnKindDef` (the silent-failure trap this item's own spec
warns about).

⚠️ **The tree changed under this pass** — `WildAnimals_Webwork.xml` went from 2 violations to
an empty, retired `<Patch></Patch>` between the first scan and the second, done by a concurrent
agent mid-session (confirmed: this item explicitly warned that could happen). Re-scanned fresh
immediately before each edit rather than trusting the first pass.

## what was fixed

For each of the 55 rows: retargeted from the bare donor defName (`MayRequire
="mlie.starwarsanimalcollection"`) to `RSW_<Name>` (`MayRequire="mandrake.rsw.swbestiary"`),
preserving commonality weight and inline comment. Where the file already had a separate
`mandrake.rsw.swbestiary`-gated Operation, the row moved into it; where a whole Operation
became empty as a result, it was deleted (FeverWood's donor wildAnimals Operation, LeaningScrub's,
PoisonForest's, Wasteland's donor Operation). One correction to false prose along the way:
`WildAnimals_FeverWood.xml`'s header claimed 6 creatures (Urusai, Gelagrub, Convor,
LongtailGorg, Whisperbird, Fambaa) had "no port yet" — false; all 6 already ship as full
ThingDef+PawnKindDef pairs in `src/RimStarWars/SWBestiary`. Corrected in the same edit
(correctness-outranks-seat-ownership).

Files changed (all Utinni patch files, none a frozen RUT_ twin):
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_FeverWood.xml` (6 animals + 1 plant)
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml` (5 animals, targets `RM_FloodedCanyon`)
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LeaningScrub.xml` (31 animals, targets `RM_LeaningScrub`)
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Miasma.xml` (7 animals)
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_PoisonForest.xml` (3 animals)
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Warscar.xml` (1 animal, targets `RM_Warscar`)
- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Wasteland.xml` (1 animal)

Not touched, correctly: `WildAnimals_Greentide.xml`, `WildAnimals_TheForge.xml`,
`WildAnimals_WeepingStones.xml` (already clean — 0 bare-donor rows with an existing port),
`WildAnimals_Webwork.xml` (already retired/emptied by a concurrent agent this session), and
all 11 `RUT_*.xml` frozen twins (untouched by design — `BIOME_PAINT_ONCE_AT_THE_END_1`).

## still genuinely owed (not this item's scope)

- **3 no-port rows** (Hydenock/Jogan trees, tooke-trap) — real canon plants with no RSW_ port
  yet, tracked under `DONOR_DEFS_PORT_TO_OURS_1`.
- **Live-load verification** — every sibling `WildAnimals_*.xml` in this folder already carries
  the standing caveat that an unmatched `PatchOperationAdd` is silent and a clean
  `validate_patch.py` static run is not proof a row lands. This pass ran `validate_patch.py`
  with **no `--defs`/`--live`** (UNMEASURABLE on this WSL machine — no local def dump, matching
  every other WSL/Mac agent this session) — static-only, 0 errors/warnings on all 7 edited
  files. A Desktop post-load def dump confirming all 55 retargeted rows resolve is owed, same
  as the pre-existing owed verification on every other `WildAnimals_*.xml` in this folder.
- `MLIE_FAUNA_ABSORPTION_1`'s "surviving unchecked line" (step 4 of this item's spec): that item
  is already closed (see this item's own opening line), so this is moot, not owed.

## criteria — met

Every biome cast row in the live wiring layer (the Utinni patches, since all 11 twins are now
frozen) names the RSW_ port we own where one exists; the only remaining donor-mod dependency is
for the 3 rows with no port; no ported creature among the 46 retargeted sits unused because
nothing spawns it — each is now wired into the live `RM_` biome it always belonged to.
