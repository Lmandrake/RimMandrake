# BOUNDARY: a calm map in one call, Design Version 0.1.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCalmCore.cs` (all of it), `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCalm.cs` (all of it), `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchQuietSiteTools.cs` (actions `calm`, `reassert`, `read` and `release`).
Item: `RIMMANDRAKE_BUILD_BRIDGE_RECEIPT_CALM_AND_TAP_EITHER_WAY`; needs design
`design/specs/2026-11-23-bridge-v2/02_needs_design.md` §1 and §3. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_calm_core.py`. The live proof is `src/RimMandrake/bridgetools/prove_three_tools.py`.

`jawa/quiet_site` gets four actions. `calm` sets every control and reads each one back. `reassert` sets again what
drifted, with the arguments of the last `calm`, and names what was repaired and what could not be repaired. `read`
changes nothing. `release` restores the switches and proximity-letter flags changed by `calm`, ends the forced weather
condition it installed, and releases its incident, queue and spawner holds. The old actions (`status`, `apply`) are unchanged.

Each control reads HELD (its source is stopped, read back), CALM (looked, found none), EXCEPTED (the scene took it off),
NOT_CALM (each thing named) or COULD_NOT_READ (with the cause). The verdict is CALM only when no control reads NOT_CALM
or COULD_NOT_READ. The reply always lists `notCovered`: the influences that no control reads.

| control | set by `calm` | read back |
|---|---|---|
| storyteller, random_mental_states, random_diseases | the engine's own switches off | the switches |
| incident_gate | every `IncidentWorker.TryExecute` is held, except `allowIncidents` | a probe incident is sent through the real method and must be held |
| incident_queue | frozen, kept | a probe queue must be held; the queued incidents are listed |
| wild_spawner | `jawa/wild_spawner_block`'s own block | its patch, switch, policy and lease |
| weather | a forced weather (`weather`, default Clear), settled at once | current, forced, rain and snow rates |
| game_conditions, hostiles, predators, arrivals, threat_structures, fires | permanently removed only with `clear=true` | each one named |
| proximity_letters | unsent ones marked as sent until release or expiry | unsent ones named |
| mental_states, force_pause_windows | never changed | each one named |

## LIMITS

- **The lease: 30 minutes, at most 240** (`minutes`; the same lease as `jawa/wild_spawner_block`). Danger: a driver that
  dies leaves a game with no raids, weather or wild animals, and the next user tests a game that is not the real game.
  `wild_spawner_block` has had this lease since 2026-10-12 for that reason. When the lease ends, the same restoration
  runs on the next frame, even while paused. Explicit `minutes` on `reassert` renews the lease.
- **200 breach rows kept; the count is exact.** Danger: a mod that tries one incident each tick fills the memory.

## DOES NOT SURVIVE (not promised)

- **events-with-no-incident.** A mod that spawns pawns itself is not stopped. A pawn that appears in a game tick is named
  under `arrivals`; a pawn that a tool places outside a tick is counted as placed, not as an arrival.
- **an-allowed-incident-in-the-queue.** The queue stays frozen. A scene fires its allowed incident by a direct call.
- **a-queued-incident-that-became-due.** It fires on the first tick after the release.
- **a-load.** A calm belongs to one game. After a load `read` says NOT_CALM and `reassert` sets the calm again; the bridge
  does not do that by itself.
- **a-save-made-while-calm.** The forced weather condition is saved with the map. Release before you save.
- **another-map.** Weather, conditions, pawns, fires and structures are read on one map (`mapId`). Incidents, the queue,
  the switches and the wild spawner are held for the whole game.
- **a-campaign-game.** The companion refuses `jawa/quiet_site` while a canonical world save is loaded (campaign profile).

## PROMISES (each one is owed a test of the same name)

- **calm-only-when-every-control-was-read.** A control with no reading, a reading that threw, an unknown status and an
  empty profile each give a verdict that is not CALM.
- **each-thing-not-calm-is-named.** A NOT_CALM or COULD_NOT_READ control is named in the reply with its things.
- **not-calm-outranks-could-not-read.** With both, the verdict is NOT_CALM and both lists are filled.
- **an-exception-is-shown-and-checked.** An excepted control reads EXCEPTED and is listed; a name that is no control is
  refused, never ignored.
- **the-gate-holds-all-but-the-allowed.** With the calm on, an incident is held unless its def is allowed (any letter
  case); with the calm off, or ended, nothing is held.
- **every-breach-is-counted.** The count of held attempts and arrivals is exact past the kept rows, and the number of rows
  that were dropped is stated.
- **lease-expires-while-paused.** At expiry the storyteller switch is restored and the forced weather condition ends
  while the game tick stays fixed.
- **release-restores-proximity-letters.** On the same loaded map, release puts back the unsent flags that calm changed.
  Letters that had already been sent stay sent.
- **arm-tick-follows-game.** The arm tick belongs to the game that was armed. After a load `read` reports `-1` until
  the new game is armed, even if its map id matches the old one.
- **reassert-keeps-the-lease.** With no `minutes` argument, repairing an active calm on the same map preserves the calm
  deadline and any active wild spawner deadline, even if they differ. It restores a missing spawner block for the
  remaining calm time. Rearming uses the last `calm` duration. Explicit `minutes` sets a new deadline for both.

**LIVE PROOF** (2026-11-23): ArchSmall, all rows of `prove_three_tools.py` at 9d022c7087 PASS (45 of 45 with the other two tools); Steve1 testq `J20261124T011611Z-348324`, all calm rows PASS.

Later lists beside this page: `polish.md`, `next_version.md` (none yet).
