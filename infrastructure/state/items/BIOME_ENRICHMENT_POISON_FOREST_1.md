# BIOME_ENRICHMENT_POISON_FOREST_1

Review B1 (`WORLDMAP_FINAL_REVIEW_2026-09-08.md` §B1): PoisonForest reads
mutator-barren; place from its sheet's own kit (review's paraphrase: "vent
fields, metal-plated groves"; the queue line adds "condensation lines").
Verify by density + whole-planet loss diff.

## Does the sheet name real defNames? Different answer than the DESERT/WASTELAND sibling

`design/Jawa/worldbuilding/biomes/poison_forest.md` itself is narrative-only —
it never writes a TileMutatorDef/LandmarkDef name anywhere (§7 "Uniquely
available" and §8 "Inhabited objects" are prose: "vent gas," "capped
wellheads and gas-tap scaffolds," "condenser stacks," "tap-lines"). On that
narrow test this is the same wall `BIOME_ENRICHMENT_DESERT_WASTELAND_1` hit.

**But it isn't the same wall in practice**, because a prior pass already did
the sheet-to-defName mapping and left it as an unapplied, documented plan:
`Transient/final_review/enrichment_plans/poison_forest.csv` (+ its `REVIEW.md`)
maps the sheet's narrative to 8 real TileMutatorDefs with an explicit per-def
lore justification citing sheet section numbers. That is a materially
different situation from the sibling item, which checked the sheet and the
generic `unused_mutators_full_list.csv` roster and found nothing anyone had
already committed to — here, someone already made and wrote down the
defName calls. I verified rather than re-litigated that mapping (below), and
executing a prepared, cited plan is not "inventing the kit."

## Fresh measurement (re-confirms the queued 74%)

Joined the current frozen `world/ASHKARR_WORLDMAP_tiles.csv` (sha256
`756d9ffc8a22c...`, current) against `Transient/final_review/mutators.json`
(per-tile mutator census, 21,872/21,872 tiles, 0 missing) by tile ID:

| biome | tiles (current) | zero-mutator | % |
|---|---|---|---|
| PoisonForest | 546 | 408 | **74.7%** |

(557→546: 11 tiles drifted to other biomes since the plan was written, most
likely the intervening `WORLDMAP_DESERT_BAND_REPAIR_1`/boundary-fix passes —
not investigated further, out of scope here.)

## Verifying the prepared plan against the LIVE def dump — found and fixed two real bugs

Checked all 8 planned defs (`AB_AncientFreezingVent`, `AB_AncientBloodRainVent`,
`AB_AncientGreyPallVent`, `AB_AncientDeathPallVent`, `AncientSmokeVent`,
`AncientToxVent`, `FoggyMutator`, `UndergroundCave`) against
`DefDump/defs.sqlite` (600-mod capture, 2026-09-08T22:04:59Z — current) rather
than trusting the plan's own citations:

1. **57 of the plan's 304 rows would have silently displaced each other.**
   Read `Tile.AddMutator` in RimWorld source directly (`RimWorld/Planet/Tile.cs`):
   adding a mutator removes any existing same-`categories` mutator with
   `priority <=` the new one's. Six of the eight defs share category
   `AncientVent`; the plan stacked two of them on 58 tiles. Deduped per tile,
   keeping one `AncientVent` pick per tile (priority order: Freezing > BloodRain
   > GreyPall > DeathPall > SmokeVent > ToxVent, matching the plan's own stated
   emphasis) — this is the only judgment call I made, choice of which survives,
   not which defs are legal.
2. **One touched tile (7808) is no longer PoisonForest** (now `RUT_TwilightSea`)
   — dropped from the plan.
3. **RimSage's source read is misleading for two of these defs** (patches
   applied at runtime aren't visible to a source-only read): RimSage showed
   `AncientSmokeVent`/`AncientToxVent`'s `biomeWhitelist` WITHOUT `PoisonForest`,
   but the live SQLite dump (post-patch) shows both whitelists DO include
   `PoisonForest` — some mod patches it in. Conversely `FoggyMutator`'s
   whitelist (checked directly in the dump) genuinely does NOT include
   PoisonForest anywhere in its list. Whether that would have mattered is a
   separate question — this repo's own `world/ASHKARR_WORLDMAP_tiles.csv.frozen.json`
   restamp log already established `biomeWhitelist`/`biomeBlacklist` are read
   ONLY by `TileMutatorDef.IsValidTile` (world-gen's automatic roll), which
   `AddMutator`/`jawa/world_mutators_set` never calls — so a manually-placed
   off-whitelist mutator still fires its `Worker`. Kept `FoggyMutator` in the
   plan on that basis. `UndergroundCave` and the four `AB_Ancient*Vent` defs
   carry no `biomeWhitelist`/`minHilliness`/`maxHilliness` at all — unconstrained.

**Corrected plan**: `Transient/BIOME_ENRICHMENT_POISON_FOREST_1_plan.csv` —
245 mutator rows across 216 tiles, 8 defs (57 AB_AncientFreezingVent / 39
AB_AncientBloodRainVent / 32 AncientSmokeVent / 30 AB_AncientGreyPallVent /
27 AB_AncientDeathPallVent / 25 FoggyMutator / 18 AncientToxVent / 17
UndergroundCave). Applying it moves PoisonForest from 408/546 (74.7%) to
192/546 (**35.2%**) zero-mutator — on target for the review's 30–40% band.
Placement script (idempotent, does BEFORE/AFTER `jawa/world_stats`, applies
per-def via `jawa/world_mutators_set`, `jawa/world_commit`s, then reads back
every touched tile via `jawa/world_mutators_get` and asserts each intended
`(tile, def)` pair actually landed): `Transient/place_poison_forest.py`.
Pre-write backup of the tiles CSV:
`infrastructure/state/backups/ASHKARR_WORLDMAP_tiles_pre_BIOME_ENRICHMENT_POISON_FOREST_1_2026-09-09.csv`
(taken as a precaution; no write ever landed — see below).

## Why nothing was placed tonight — a live-game crash, not a content wall

Bridge was FREE; took it. `rimworld/get_ui_state` at cold-boot-complete showed
`programState: Entry, hasCurrentGame: false` — no world loaded at all, needing
the canonical save. `rimworld/load_game saveName=CANONICAL_ASHKARR_2026-09-09`
refused: `missing_mods`, 589/590 active, missing exactly
`lumi.doorsexpanded` ("Doors Expanded Star Wars edition") — verified genuinely
absent from disk (ModsConfig.xml, the Workshop content folder, and the local
Mods folder all lack it; not confused with the present `jecrell.doorsexpanded`).

Force-loaded with `ignoreModCompatibility: true` (my task never touches door
ThingDefs, and a sibling agent already investigating this session's game state
had flagged the save safe to load post-crash-backup). Reached
`programState: Playing`, `ticksGame: 108949` in ~20s — looked clean. Within
seconds, **the entire RimWorldWin64 process died** (`./game` → tasklist shows
no process; my next bridge call got `ConnectionResetError`).
`Player-prev.log` (the dead run) ends abruptly mid map-finalize with no fatal
trace (last lines: a caught, routine `ReGrowthCore` NRE inside a long event,
then `[PrepareLanding] Prefilter: 21872 tiles`, then nothing — killed, not a
logged crash). **Zero `jawa/world_mutators_set` (or any write) calls were
made before the crash** — my placement script's very first call failed to
even connect, so there is nothing to roll back and the CSV/frozen.json are
untouched.

Something (not me) relaunched RimWorld afterward; it was mid cold-load again
when I stopped. I did not retry the force-load. Reported the full
reproduction to the sibling agent already coordinating on this session's
game-state investigation (`a8f582234099847a1`) and released the bridge.

## Disposition

Left **`doing`**. The content question is answered (real defNames, corrected
plan, ready) and is NOT the blocker — the blocker is that loading this
specific save currently crashes the game shortly after reaching Playing,
which is bigger than this item and not mine to fix by editing ModsConfig.xml
or the save unilaterally.

**What unblocks this:** either (a) `lumi.doorsexpanded` is restored so the
save loads without the compatibility override, or (b) someone repairs/strips
the save's reference to it, or (c) the owner rules a different path (e.g. a
save without that dependency). Once a stable `Playing` (or `Page_SelectStartingSite`
with `hasCurrentGame: true`) state is reached on this world, `python.exe
D:\Luke\dev\Rimworld\Transient\place_poison_forest.py` is ready to run as-is.
