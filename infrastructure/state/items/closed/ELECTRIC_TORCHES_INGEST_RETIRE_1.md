# ELECTRIC_TORCHES_INGEST_RETIRE_1 — absorb the torches, then drop the mod

Owner, 2026-09-02: *"Maybe we should just ingest the electric torches. It's tiny. Then
retire it."*

## spec

`onimods.electrictorches` ("Onimods - Electric Torches and Braziers") is a permanent
line in the log harvest baseline: **2 defs silently discarded on every single load**,
because `ElectricTorches_DarkAgesCrypts_Thoughts.xml` references
`VanillaFurnitureExpanded.ThoughtGiverByProximityDefExtension`, a type that is not
present. `harvest_log.py` scores it `DEFS DISCARDED 2 = baseline 2` and calls it benign
— which it is, and that is the problem: a permanently raised baseline is how a real
regression hides.

**Ingest, do not just delete.** The content is wanted; only the broken dependency and
the third-party wrapper are not. Take the torch/brazier defs into one of our own tiers
under the three-tier naming grammar (`design/NAMING_SCHEME_PLAN.md`) — these are
generic RimWorld furniture with no Star Wars or campaign content, so **RimMandrake**
(`mandrake.rm.*`, prefix `RM_`) is the tier, not RimStarWars or RimUtinni.

- Drop the two defs that chase the missing VFE extension, or supply a real
  `ThoughtGiver` route if the by-proximity mood effect is actually wanted. Decide which
  by reading what those two defs do — do not carry a broken reference across.
- ⚠️ Do NOT rename anything the campaign save already references. If any torch is
  placed in `WORLDMAP_V1_original.rws` or the gravship save, a new defName is a
  `Could not load reference to` on the next load. Check the saves before choosing
  defNames (`skills/rimworld-savegame`, grep `<def>NAME</def>`, not the bare defName).
- Then remove `onimods.electrictorches` from the active list. That is a config change,
  so it needs no window (owner's ruling: config files never block on the game) — but it
  does need RimSort refreshed if it is open.

## verify
- The ingested torches resolve live: spawn one from the dev spawner and it is not
  magenta and not missing.
- `harvest_log.py` on the next full load reads `DEFS DISCARDED 0`, and the baseline
  comment naming "Onimods torches (benign)" is updated in the same pass — a baseline
  that still names a mod we removed is worse than one that is wrong.
- No `Could not load reference to` naming any torch def on a campaign load.

## criteria
The torches exist under our own tier, the log harvest baseline drops to 0 discarded
defs, and one more third-party mod is off the list without losing content the owner
wanted.
