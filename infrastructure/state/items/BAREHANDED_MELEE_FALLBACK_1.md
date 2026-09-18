# BAREHANDED_MELEE_FALLBACK_1 — the last 3 Geonosian kinds, ranged-only, now fixed

## 2026-09-18 re-run (FOUNDRY, offline/BELT, no bridge) — 18 -> 3 -> 0 ranged-only
Re-ran `weapon_pool_join.py` fresh against today's live cut list (2289 defs, CherryPicker
snapshot 2026-09-13) rather than trust the "18 of 23" figure in the spec below: 15 of the
18 were **already fixed** at `1dd78b9cf` (2026-09-11). Only the 3 Geonosian kinds
(Grunt/Heavy/Specialist) were still ranged-only — confirmed unchanged from that commit's
own escalation, not new drift.

**Fix**: added `NeolithicMeleeDecent` to all three Geonosian kinds' `weaponTags` (both
`JawaFactionRoster.xml`, the deployed file, and `gen_pawnkind_roster.py`'s `KIT` table,
the source of truth — the generator's `RUT_` prefix gap noted in the 2026-09-11 commit is
still unfixed, so `gen_pawnkind_roster.py` was NOT re-run to regenerate the XML; confirmed
by diff that a fresh regen still emits bare `Jawa_*`/`Jawa_HuttCartel` names, which would
have silently reverted the whole file). Rationale: `SaV_geonosianmelee` (the literal
Geonosian electrostaff, `guy762_electrostaff_geonosian`) is the only Geonosian-NAMED melee
weapon and re-verified still priced 20950 against these kinds' 400-1200 budgets — never
reachable, confirming the 2026-09-11 escalation was correct and is still true today.
Rather than fall back to another culture's signature weapon (Deep Desert's gaderffii, the
other candidate the 09-11 pass found), found a better fit: `NeolithicMeleeDecent` carries
a cluster of creature/insect-part melee weapons (`BMT_PustuleHornetStinger` @100,
`BMT_CrystalMantisClaw`/`BMT_FungalMantisClaw` @150, `BMT_CaveSpiderHead`/
`BMT_RoyalRhinoHorn` @200, `BMT_BunkerClaw` @800, all `generateAllowChance` 1.0, all
verified live in the current cut) — hive-harvested trophy weapons, matching the
`ORChitinArmour`/`InsectJelly` identity this roster already writes for the Geonosian
kinds, and no other Jawa faction currently uses this tag. Cheapest carrier (100) sits
well under all three kinds' floors (400/800/1000), so each kind now ALWAYS arms even with
Shooting disabled. Re-run confirms **0/23 ranged-only** (was 18, then 3).
`validate_patch.py --live` on the edited XML: OK, 0 errors, 0 warnings.

**Still open — genuinely undiagnosed, needs bridge (out of scope this session, BELT/no-
bridge)**: the 5 kinds from the original diagnosis (Deepwater Leader/Specialist,
DeepDesert Heavy, Wildsteam Specialist, Junkers Grunt) re-checked today and are
UNCHANGED from the 2026-09-11 finding: every one has a fully affordable, **100%-melee**,
`generateAllowChance=1` within-budget pool (4-6 items each) — the kind-level static join
cannot explain their bare spawns, because by this analysis they should never spawn bare.
This is not a weapon-pool defect at all; it needs a live per-pawn trait/workTag join on a
bridge spawn batch (spawn MANY, per this repo's own doctrine — one pawn is RNG), which
this seat has no bridge access to run. Left `doing` and blocked on bridge access rather
than closed; the verify criterion below (`245-pawn regeneration sample`) cannot be met
offline. `Jawa_Junkers_Grunt`'s flagged dead cheapest item
(`BMT_ResourceBlueCrystal`, gac 0) was re-confirmed NOT the cause — the kind has 5 other
live, gac=1 melee items in-pool regardless.

---

## Original spec (2026-09-11, now partly stale — see re-run above)

## spec
Diagnosis pass 2026-09-11 (BENCH lane, sourced from
`infrastructure/state/facts/weapon_pool_join_2026-08-29.json` +
`PAWN_WEAPON_POOL_JOIN_TOOL_1`): of the 23 distinct kinds behind the 25/245
bare-handed pawns (ledger 2026-08-28), **18 share one structural gap — their
weaponTags resolve to an in-budget pool that is 100% ranged, zero melee
fallback**. A pawn of those kinds whose traits disable Shooting spawns with
nothing. Not a CherryPicker tag-emptying: no kind has an empty pool or a
money floor below the cheapest weapon (both earlier theories ruled out).

The 18 (all `Jawa_` kinds): Hutt Grunt/Heavy/Specialist; Empire
Grunt/Heavy/Specialist/Leader; Geonosian Grunt/Heavy/Specialist; Helix
Heavy/Leader; Homestead Leader/Specialist/DesertRanger; Wildsteam Leader;
DeepDesert Specialist; TradeMoot Heavy.

Plus: **Jawa_Junkers_Grunt** — its cheapest "eligible" item
(BMT_ResourceBlueCrystal) carries `generateAllowChance 0`, never rollable.
And **5 kinds undiagnosed** (Deepwater Leader/Specialist, DeepDesert Heavy,
Wildsteam Specialist have real melee in-pool and still spawned bare — needs a
per-pawn trait join, not another kind-level pass).

## the work, in order
1. 🔴 **Re-run the weapon-pool join against TODAY'S post-restore cut list
   first** — the 08-29 facts predate the 139-reversal restore; a restored
   melee weapon may already fix some of the 18. Never act on the stale join.
2. Add a melee fallback tag to each still-ranged-only kind's pool. Tag choice
   carries faction voice (a Tusken raider's gaderffii is not a Hutt enforcer's
   vibroblade) — draft per-faction, card the owner only where no obvious
   in-voice melee tag survives.
3. Fix or replace Jawa_Junkers_Grunt's dead cheapest-item.
4. The 5 undiagnosed: per-pawn trait/workTag join on a live spawn batch
   (spawn MANY — one pawn's result is RNG).

## verify
- [ ] A 245-pawn regeneration sample shows 0 unintended bare-handed spawns
      (MEASURED, live), or every remaining bare spawn is classified INTENDED.
