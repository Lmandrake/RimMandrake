# Sites, map persistence, timing windows and save fixtures

## The map is not calm on the full list

- **Wild animals respawn** after a one-off non-colonist sweep. A predator stabbed two
  colonists down mid-run on 2026-10-11. So re-calm before **each** block
  (`jawa/destroy_bulk filter=nonColonists dryRun=false`). For the general staging
  method, see `rimworld-live-review` §1.
- **Idle colonists wander fast into sites**: draft every colonist the block is not
  using. The `reveal` helper drafts the colonist it borrows for the same reason.
- **Map-gen hostile structures** keep the world uncalm. An insect hive (BetterInfestations)
  throws its own NREs.
- **Don't let the suite kill its own fixtures.** modcheck's "everyone is dead" floods were
  `Session.sweep` killing the suite's own test colonists (Bomb 99999), plus explosion
  tests placed at the map centre where the colony spawns. Register fixtures with the
  situational Watch, and anchor destructive tests away from colonists.
- **`jawa/damage` skips player pawns** unless `allowColonists=true`. A pawn's
  `Thing.HitPoints` is ~0, so `CompExplosive` detonates on ANY damage unless
  `requiredDamageTypeToExplode` is set. `restore_needs` verifies by percentage
  (Food max is 0.9).

## Clearing a site, and reading it back

`validation_core.prepare_site(B, rect, rows, rid)` destroys everything, lays Soil,
unfogs, removes the roof, reveals the area with a colonist's sight, then **reads back**
roof and things. Anything left in the rect gives `UNMEASURED/SITE` and returns False.

- **Giants on `RM_TheRot`.** Full-list quicktest maps on the current tile are RM_TheRot.
  Giant fungi with Huge Things footprints cover them: 5,000+ `RM_HugeTrunkBlocker`
  cells in 215 16-cell tiles on one map. `MapComponent_HugeFootprints` re-plans any
  blocker that vanishes while its plant stands (`Notify_BlockerGone`). That means a
  giant **outside** the rect re-blocks a site you cleared. →
  `validation_core.clear_huge_plants(B)` before every block. It removes every plant
  within 6 cells of a blocker, which is cheap on a test map.
- **Fog.** `jawa/set_fog unfog` did not stop "Can't place in undiscovered area" for
  designator-placed builds on the 550-mod list. A colonist standing there did
  (`validation_core.reveal`).
- **Geometry the mod enforces.** Sites need margin for the real operation. A hose reel
  needs room for its ~4.4-cell straight lead-out, so prepare 6 extra cells on the
  lead-out side. Aim a hose at the relay's real footprint cell (RL3 aims onto B's SW
  footprint cell), not at a cell beside it.
- **Blocks need disjoint sites**, and a block that tears down map-wide (the GSS matrix)
  runs first.

## Which world, which map

- **Use a bland world for the full list's quicktests.** The campaign world has no vanilla
  Desert or AridShrubland tile, so a quicktest map carries Sheen/Terminator-front fires
  and roof collapses. `--bland-world` uses `ZBiome_Grasslands`. Test lists drop
  `mlie.nwnrealfogofwar`: destroying map-gen ruins on a 2nd map makes RealFoW throw
  every Update, and `step_game_ticks` then fails on every map.
- **A map with no player pawn is culled.** A `jawa/world_tile_map_generate`'d map, or a
  generated side map with no colonist, is auto-culled once it stops being current, and
  culled on save. Found a player settlement (`colony_found`), or anchor with a colonist
  first, if the map must survive a sequence of calls.
- **Regenerate Current Map wipes the colonists.** Test on the home map and respawn
  colonists with `src/RimMandrake/bridgetools/spawn_test_colonists.py`.
- **Load saves from the main menu, once.** A paused site no-ops an `ordered_job`
  `waitTicks`. `step_game_ticks` needs `timeoutMs`.
- **Prove a quicktest world reaches Playing:**
  `python.exe src/RimMandrake/bridgetools/prove_quicktest_world.py` (exit 0 = Playing
  with a world).

## Timing windows

- **Take the window from the design's contract, one half at a time.** On 2026-10-11 the
  NS_hose_carries_real_units row used a flat 260-tick window from the lay, which was
  shorter than the design's own contract. FINAL §3.6 says discover ≤ 60 ticks, then
  transfer by the NEXT 250-tick pump cycle, which is up to 310. In the same run the
  netLink was present at +260 with 0 units, and the hose plumped at +350. The fixed bar
  reads discovery (≤ 60, stepped 5), then units within one cycle (≤ 260) **of
  discovery**. Each half is stricter than the old window, not looser.
- **Wait for the precondition, then start the clock.** A freshly built powered consumer
  beside a just-charged battery reads `PowerOn=false` for ~100–170 ticks (measured
  140 / 100 / 170). Vanilla's power net switches it on later, not at spawn. The fix is
  `_powered()`, which waits for the pump, plus a recorded `pumpPoweredAfterTicks`.
  Any machine cycle timed from its build has the same trap.
- **To trace a mechanism the window says is broken, poll it.** Re-stage by hand on a
  spare plot and read the machine every 10 ticks. That turned "relay chain carries
  nothing" into "the pump had no power yet". The chain itself worked.
- Tick-keyed caches, a stepper that overshoots short states, load-call races:
  `skills/rimbridge/references/traps.md`, "Bridge time is TICKS".

## A simplified model passes what the real operation refuses

An install precheck that judged a taut route with no nozzle lead-out
(`HoseMath.CheckInstall`) accepted orders that the real lay then refused, and the
colonist carried the hose out to nothing. An offline selftest that modelled the reel
as 1×1 with no outlet stayed green while 7 live rows went red. Where the real
operation's trial run is cheap, gate on that trial run. When a ruling changes the real
geometry, re-check every live scene built before it. For example, the owner refused a
straight lead-out on 2026-10-06 rather than lay it without one. See
`deciding-and-superseding`, "A stale belief hides…".

## Pre-port save fixtures (old build, mid-job)

Use these when a port moves a class, job driver or def between mods, renames a type,
or changes what a save holds. They prove that a player's existing save survives.

1. **Before deploying the port**, with the OLD build loaded, back up the keepers
   (`CANONICAL_ASHKARR_START`, `BLAND_NORTHSTAR_BASE`, `ASHKARR_*`, `FOUNDER_*`, …), then
   stat every file in Saves.
2. **Stage the job and save it mid-flight.** Name it so it reads as a fixture:
   `RM_PREPORT_<THING>_MID<JOB>_<date>.rws`. Record the state at the save: the job,
   the toil, the carrier, the order, and the old class names that appear in the save
   (`grep` the class with `<def>`-style care; see `rimworld-savegame`).
3. **Make sure the job outlives your read.** On the full list "Out of Combat ReBoost"
   walks a colonist at ~2 ticks/cell, so a 24-cell carry finishes inside the proof's
   60 post-load ticks. Slow the carrier with BadBack + Frail (`jawa/pawn_health`),
   which gives ~8 ticks/cell and ~180 ticks of carry after the save point. Mud and
   shallow water did not help, because the path avoided them.
4. **Stat-diff Saves**: exactly the new files, 0 changed. `rimworld/save_game` has written
   the current slot instead of `saveName` before.
5. **After the port**: `proof_hose.py --live --preport-save NAME1,NAME2`. PASS needs all
   of these: the load completes (17–28 s), no "Cleaning up invalid job state", no
   unresolved class, and the colonist is **still on the job 60 ticks after load**
   (the old driver class aliased onto the new mod).
6. **Keep the fixtures** in Saves until the owner says delete. They are the regression
   test for the next port.
