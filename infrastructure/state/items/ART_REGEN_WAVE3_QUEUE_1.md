## spec
Standing owner instruction: "always have at least one background sub agent
working on art regeneration" / "keep the graphics going, don't stop full
belt." Wave 2 (`ART_REGEN_WAVE2_QUEUE_1`) just finished (`AA_Frostmite`,
`GR_Spidercat`, `Insectomorph`, `VAEWaste_Megatardi` — 12/12 jobs, all in
`infrastructure/artpipe/done/`) and `infrastructure/artpipe/pending/` is
empty again. This item's job was to find and queue wave 3 from the same
authority, `design/Jawa/worldbuilding/review/round2/decisions_propagated.json`
(the fauna source; `round2/flora_decisions_propagated.json` for flora).

**Finding: the eligible pool is exhausted. Zero new jobs filed.**

The fauna file's 34 `art: "redo"` rows are now fully accounted for:
- **15 rows / 11 distinct creatures, `decision: "in"`** — Kreetle (5 biome
  rows), Horax, AA_ShadowCharger, AA_Thunderox, Fambaa (2 rows), Dragonsnake,
  Zakkeg, AA_Frostmite, GR_Spidercat, VAEWaste_Megatardi, Insectomorph — **all
  11 already done**, 7 in wave 1, 4 in wave 2.
- **14 rows, `decision: "move"`** (biome reassignment / rename / open design
  call — excluded per the standing carve-out, unchanged from wave 1/2's
  list): `AA_Radyak`, `AA_ShockGoat`, `Aiwha`, `BMT_CrystalCrab`,
  `BMT_SandPillar`, `DA_BeardedTroll`, `GR_Chickenhorse`, `GR_Chickenlizard`,
  `GR_Chickenspider`, `GR_Needlechicken`, `GR_Rabbitchicken`, `Gundark`,
  `JRWBeelzebufo`, and `fauna:the_miasma:Kreetle` (note: Kreetle's OTHER
  4 biome rows are `decision: "in"` and already drawn — this row alone is
  the miasma placement, still unresolved).
- **5 rows, `decision: "out"`** (cut for real) — `BMT_BiliousVarog`,
  `BMT_ShatterjawBeetle`, `GR_FleshFlies`, `GR_Mechachicken`,
  `GR_Squirralope`.

11 + 14 + 5 = 34. Nothing left in the "in" bucket.

The flora file (`round2/flora_decisions_propagated.json`, 288 rows) has
exactly **one** `art: "redo"` row (`flora:wasteland:PoisonPlantBush`) and its
decision is `"out"` — nothing eligible there either.

**Sibling files checked and found superseded, not additive:**
`design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json`
(828 rows, saved 2026-09-10T07:02) is a strict subset of
`round2/decisions_propagated.json` (833 rows) — the 5 extra round2 rows are
newer rulings, and the two `redo`+`in` rows that differ between the files
(`GR_FleshFlies`, `GR_Squirralope`) are exactly the ones the later
disposition sitting moved to `decision: "out"`. Confirms round2 is the live,
later version; the older file adds nothing.
`design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json`
is byte-identical in content to `round2/flora_decisions_propagated.json`
(same 288 keys, same values) — zero `redo`+`in` rows either way.

Also checked whether other `review/*.decisions.json` registers
(`plant_register`, `weapon_register`, `vehicle_register`,
`furniture_register`, `turret_register`) carry an `art` field the daemon
could draw on: none do — those are keep/cut curation registers only
(`{decision, prefill, prio, note}` or, for turrets, a balance-rework
register), not art-redo trackers. Not a legitimate source.

## verify
N/A — no art jobs were filed this wave. `infrastructure/artpipe/pending/`
and `active/` were empty before and after; `done/` count unchanged (80
files) other than by this item's own inspection (read-only).

## criteria
Honest report that the well is dry for the specific, owner-scoped criterion
("art: redo, decision: in, no rename/biome-move/design-call needed"). The
belt does NOT restart on this criterion until one of:
1. BENCH/the owner rules on the 14 `move` rows above (biome placement,
   mostly Helix-territory chicken-family creatures, plus Aiwha, Gundark,
   AA_ShockGoat, the three BMT/DA homeless creatures, and JRWBeelzebufo's
   rename+redefine) — any that come back with a firm biome/name and no
   further design call become art-eligible next wave.
2. The owner explicitly authorizes drawing from the `art: "improve"` bucket
   (338 rows, unexamined for eligibility — a materially different, much
   larger scope than `redo` and outside this item's authorization) or from
   a different asset class (weapons/vehicles/furniture/plants have no `art`
   field at all, so that would need a fresh decision pass, not a queue
   pull).
3. A new decisions file / sitting supersedes `round2/decisions_propagated.json`
   with more `redo` rows.

Daemon (`pgrep -f artpiped.py`, PID 378727) confirmed still running,
`pending/`+`active/` confirmed empty — left as-is, no jobs to feed it this
wave.
