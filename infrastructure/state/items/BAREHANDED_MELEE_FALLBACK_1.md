# BAREHANDED_MELEE_FALLBACK_1 — 18 kinds whose weapon pools have no melee at all

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
