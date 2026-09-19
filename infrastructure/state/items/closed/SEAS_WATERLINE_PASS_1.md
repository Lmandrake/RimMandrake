# SEAS_WATERLINE_PASS_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/Jawa/worldbuilding/the_seas.md` Lane 1 only (patch-only, buildable
now): give the seven misplaced/unspawned SW aquatics and five license-
cleared borrowed fauna (per `DEPTHS_ODYSSEY_VERIFY_1` §6) their first
Ocean/Lake `wildBiomes` commonality, and correct KwazelMaw's ExtremeDesert
and Mott's LavaField placement. Odyssey fishing tile mutators on Ash'karr's
actual sea tiles are explicitly OUT of scope for this item — that's a live
world-tile edit on the frozen map (bridge + `world_commit`, Opus-tier per
`Agent_Policy.md`), not a def patch. Filed as a follow-up rather than
attempted here.

Alpha Animals' "coastal amphibians" (mentioned in the_seas.md's prose but
without a defName) are also out of scope — no specific defName was given
and guessing one would violate "never guess a defName" (`CLAUDE.md`).

## verify

- Live def dump (`DefDump/captures/2026-08-31T08-41-34Z/animals.json`,
  `biomeAnimals`): confirmed all 14 target defNames currently have ZERO
  Ocean/Lake entries, and confirmed KwazelMaw ExtremeDesert=0.35 / Mott
  LavaField=0.70 are real and current (not stale census artifacts —
  read from the live game, not `the_seas.md`'s own citation).
- `validate_patch.py --defs` (both RimWorld Data and the full Workshop
  content root): 0 errors. Its cross-mod scan additionally named Alpha
  Biomes / More Vanilla Biomes / Alpha Animals as mods whose own patches
  touch `wildBiomes` broadly — likely the actual source of the fire-desert
  placement (neither KwazelMaw nor Mott declares those biomes in the SW
  Animal Collection's own file). Added all three to `loadAfter` alongside
  the four direct donor mods, and positioned the mod at the very end of
  `ModsConfig.xml` to win the override race regardless of which of the
  seven upstream mods actually set it.
- Not yet observed applying live — same as `BEAST_DANGER_NORMALIZATION_1`,
  defs parse once at startup and no restart has happened since deploy.
  When the next load happens: `jawa/get_def` or a `Lake`/`Ocean` quicktest
  spawn on the new wildAnimals table for 2-3 of the fourteen, plus confirm
  KwazelMaw no longer reads ExtremeDesert=0.35.

## criteria

- `mandrake.rsw.seaswaterline` deployed, patches all 14 target defNames'
  Ocean and Lake commonality via a manifest-driven, add-if-missing-safe
  patch (not hand-authored per-def).
- KwazelMaw/Mott's fire-desert entries zeroed via the same safe pattern.
- Fishing-mutator world-tile work and the unnamed "coastal amphibians"
  are explicitly deferred, not silently dropped.

## Manifest

`design/Jawa/worldbuilding/data/seas_waterline_manifest.csv` — Lake/Ocean
targets are `existing_max_commonality * 0.75` / `* 0.4` per animal (a
simple, defensible scale-down from each creature's best swamp-tier
presence; a design register call, not a technical one — revisit with
BENCH if the ratio reads wrong once seen in play).

## CLOSED 2026-08-31 (FOUNDRY)
