# LONGSHADE_DESIGN_SITTING_1 — the Long Shade design sitting (bedazzle to full-mod status)

Picked 2026-09-27 as the next biome sitting, on the owner's word ("continue
bedazzling any unserviced biome sheets for full mod status"). Rationale:
`LONGSHADE_RM_MOD_BUILD_1` is the only `_RM_MOD_BUILD_1` still open — every
step OWED, built from scratch, no design input yet — and
`BIOME_ENRICHMENT_DESERT_WASTELAND_1` is stalled on exactly this gap
("desert.md names zero RimWorld defNames"). Precedent shape:
`SUMP_DESIGN_SITTING_1` → `WEEPING_STONES_DESIGN_SITTING_1` →
`NIGHTSIDE_ICE_DESIGN_SITTING_1` → `BLUEDESERT_DESIGN_SITTING_1` (all closed).

Feeds `LONGSHADE_RM_MOD_BUILD_1` (FOUNDRY): this sitting is the design input
that item is waiting on.

## Inputs — read before the sitting, do not re-invent

- `design/Jawa/worldbuilding/biomes/desert.md` — the FROZEN sheet; §6 hard
  bans are linter-checkable law; §7 Uniquely available + §8 Inhabited objects
  are the reward/experience kit.
- `design/Jawa/worldbuilding/biomes/rosters/desert.json` — 2026-09-09 proxy
  roster (fauna/evictions/confidence flags; several CONFLICT rows held for
  owner).
- `design/Jawa/worldbuilding/biomes/noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md`
  — Desert names: batch 2 (DesertPort sixteen) is RULED AND APPLIED
  (`32ecbc8cb`); the Desert accent (dry fricatives, clipped) is established.
  Ruled names are kept, never re-coined.
- `infrastructure/state/items/LONGSHADE_RM_MOD_BUILD_1.md` §2 — the def as it
  stands (305-line `RUT_Desert.xml`, 53 fauna + 9 flora rows, vanilla
  weather/terrain/diseases, ~50 `RSW_` rows routing to the Utinni layer per
  Q11/Q11a).

## spec

A backgrounded Fable design pass writes
`design/Jawa/worldbuilding/biomes/long_shade_bedazzle_2026-09-27.md`
(proposal: RM_ cast partition + holes filled, flora, marquee
rewards/experiences ranked, weather/mechanics feasibility, ship-contribution
row, and a numbered card agenda). BENCH then cards the open rulings to the
owner; rulings land on the sheet/rosters/this item.

## verify

Every open design question either ruled (recorded by card or typed word) or
explicitly re-ticketed; roster updated; sitting closed with the commit hash of
the applied rulings.

## criteria

`LONGSHADE_RM_MOD_BUILD_1` can be claimed by FOUNDRY with no design question
left open — same bar Blue Desert met.
