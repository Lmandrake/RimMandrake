# BOUNDARY: the deploy of a mod's game copy runs in its own unit, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`game_deploy_*`, `unit_active`, `deploy_stale`, the in-game
branches of `decide_ingame` and `execute`), `src/RimMandrake/rimflow/maturation.py` (`game_repair`, `deploy_paths`,
`launch_mod`'s `repaired`) and `src/RimMandrake/rimflow/maturation_autonomy.py` (the `autodeploy` act).
Item: `RIMMANDRAKE_RUN_VISIT_DEPLOY_OUTSIDE_TICK_HELD_IT_FOURTEEN_MIN`, written 2026-11-24.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_game_deploy_unit.py`.

Why: on 2026-11-24, 7:25 to 7:39 AM PST, the Dispatch tick ran a visit's deploy inside itself (a plan of 5 min, an
`--apply` of 4 min, a plan of 4 min). The tick took 998 s, and no other mod could start.

## ACCEPTS (the only inputs this is built for)

- **an-owed-visit.** A mod at in-game acceptance that owes a visit and passes every other launch check, with a free game.
- **a-stale-walk-build.** An ended visit whose one open reason is the stale walk folder.
- **a-result-file.** `game_deploy/<Mod>.json` in the Dispatch state folder, written only by `game_deploy_worker`.

## DOES NOT SURVIVE (not promised)

- **a-hand-launch.** `maturation.py launch` and `pilot-launch` still read and deploy in their own process. A
  `pilot-launch` at Stage 6 holds the state lock for that time, so a tick waits for it.
- **a-unit-killed-between-stop-and-start.** The game stays down; the next unit deploys and does not start it again.
- **a-hand-edit-of-the-game-folder-with-no-hold.** A copy changed after the deploy by something that took no hold of
  the game and no commit is not seen before the visit launches.

## PROMISES (each one is owed a check of the same name)

- **the-tick-never-waits-on-a-deploy.** A deploy of 60 s: the tick returns in under 10 s, with a second mod launched in
  the same tick.
- **the-mod-reads-live-until-the-deploy-ends.** The row reads `live` and names the unit; no second unit starts.
- **the-visit-launches-on-the-tick-after.** The tick after the deploy ends launches the visit, and reads no plan itself.
- **a-deploy-takes-no-run-slot.** The unit spends no tokens and takes no slot.
- **the-deploying-game-is-driven.** Until the unit ends, its game counts as driven for every other mod.
- **the-visit-goes-to-the-deployed-game.** The game that was deployed to is picked first.
- **a-failed-deploy-is-the-launch-refusal.** A failed deploy is booked as the visit launch's refusal with its cause, and
  is used once.
- **a-waiting-or-killed-deploy-starts-again.** A wait (a held game, a full clone pool) starts again and spends no try. A
  unit that ended with no result starts again within `launch_tries`, and is then the launch's refusal. A unit that
  systemd could not be asked about still runs.
- **a-stale-result-deploys-again.** A result older than a source change under its paths, or than another hold of its
  game, deploys again; the visit does not launch on it.
- **the-stale-reading.** An unrelated commit leaves a result fresh. A tree behind the deploy is fresh. A tree that git
  cannot read is stale.
- **a-stale-walk-build-deploys-in-the-unit.** The walk build's deploy uses the same unit; while it runs, no exit is read
  from the half-written copy; a failed one names its cause and pauses the mod.
- **the-unit-is-its-own.** The unit is admitted by `control.launch_unit` under family `game_deploy`.
- **the-worker-writes-the-result.** The unit runs `maturation.py game-repair` in a pool clone, one per game, and writes
  its verdict; no verdict is a fault named; a full pool is a wait.
- **the-lock-covers-the-plan-too.** The game's driver lock is held from before the first plan until the game is up again.

## LIMITS

- `DEPLOY_MAX_S` = 9980 s (`RuntimeMaxSec`). Danger: a hung deploy would hold the game's driver lock for good. Evidence:
  the one deploy measured ran 998 s; the limit is ten times that.
