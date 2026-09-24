# KOTOR_CRYSTAL_GENSTEP_DRIFT_1 — deployed crystal genstep scattered only Stygium

## the original defect

Live game only ever scattered `KOTOR_StygiumCrystal` from `KOTOR_CrystalFormation`.
Root cause (2026-09-09, subagent-verified): the repo's absorbed copy
(`Absorbed_KotorCore_CrystalMapGenerator.xml`) already listed all 11 variants
ungated, but was held undeployed (`src/DEPLOY_HOLD.txt`) because the donor
`guy762.mm.kotorcore` was still active — deploying would have created a duplicate
`KOTOR_CrystalFormation` defName, and the LIVE game was instead loading the
donor's own copy, which gates 10 of 11 variants behind
`MayRequire=guy762.KotORWeapons` (a mod already absent), leaving only the
ungated Stygium entry surviving.

Blocked `on=DROID_DONOR_PATCH_GATE_1` — the wrong item to cite in hindsight (that
one only patched the ABF/Synstructs sites, not this hold), but the real-world
condition it was actually waiting on — `guy762.mm.kotorcore` retiring — happened
via a different item.

## FOUNDRY, 2026-09-24: stale block found and cleared; fix confirmed already shipped

Found while sweeping the queue for stale blockers. `DEPLOY_HOLD.txt`'s own record
shows the hold on `Armoury/Defs/Absorbed_KotorCore/*` was lifted **2026-09-19**
by `WEAPONS_DONOR_RETIREMENT_1`: `guy762.mm.kotorcore` was removed from both
`ModsConfig.xml` and `ModsConfig.FULL.LATEST.xml`, its `<li>` dropped from
Armoury's `About.xml`, and the whole absorbed folder deployed in the same
change — five days before this item's block note was last touched, and never
revisited.

**Verified this pass, structurally**:
- `guy762.mm.kotorcore` confirmed absent from the live `ModsConfig.xml` right now.
- The DEPLOYED copy of `Absorbed_KotorCore_CrystalMapGenerator.xml`
  (`Mods/Armoury/Defs/Absorbed_KotorCore/ThingDefs_Resources/`) is
  **byte-identical** to the repo copy — `diff` clean.
- That file carries **zero** `MayRequire` gates and lists all 11 crystal variants
  ungated (7 `KOTOR_SmallCrystal_*`, 3 `KOTOR_MediumCrystal_*`,
  `KOTOR_StygiumCrystal`) in one `GenStepDef`'s scatter group. (Note: Stygium's
  weight was hand-bumped from a commented-out `0.0833` to `0.15` at some point —
  pre-existing in both copies, not touched this pass, not part of this defect.)
- The currently-running game process post-dates the fix: `Player.log` mtime
  (2026-09-23 22:05) is days after the 2026-09-19 deploy, so this session's own
  load has the fixed, ungated version — not the stale donor copy.

**Not directly observed**: an actual in-game cave/ruin generating with more than
one crystal color. The mechanism (`CrystalFormations.GenStep_ScatterLightsaberCrystals`
from the already-active `JawaArmoury.dll`) is a stable, previously-proven class
carrying only data (a scatter-group weight table) — there is no code path left
that would still gate 10 of 11 variants now that the donor's own
`MayRequire`-gated copy is gone. Closing on the structural proof; if a future
cave visit ever shows only Stygium again, that would be a NEW regression, not
this one recurring.

## verify
Repo vs. deployed byte-identical, zero `MayRequire` gates, donor absent from
live `ModsConfig.xml`, live process post-dates the deploy. All four confirmed
2026-09-24.

## criteria
Met: the deployed genstep is the repo's ungated 11-variant version, and nothing
in the live mod set can still load the donor's gated copy instead.
