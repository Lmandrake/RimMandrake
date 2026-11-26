# BOUNDARY: a lane proofs job runs each clause's site before its proof, Design Version 0.1.0

Code: `infrastructure/stevedesktop/worker.py` (`proof_site`, `SITE_ANY_AGE`, the site step of `Attempt.run_proofs`).
Item: `PLAYER_START_SITE_1`, written 2026-11-26 by work bundle WB-game-campaign-20261126-183947. Each promise has a test
of its name in `infrastructure/stevedesktop/selftest_steve_worker_proof_site.py`. This page covers only these parts of
worker.py; the rest of the file has its own pages.

The fault: J20261126T185703Z-949b32 (PLAYER_START_SITE_1 A1) loaded tier `warlab` exactly, the game stayed on the main
menu, and `zeddos_yard_live_proof.py A1`, which reads a map, recorded FAIL: a verdict on the mod from a game with no map.
The retired live stage ran each clause's site first (`src/RimMandrake/rimflow/proof_lines.py` `site_for`); the lane's worker
did not.

## ACCEPTS (the only inputs this is built for)

- **a-proofs-file.** An item's `infrastructure/state/live_proofs/<ID>.txt` at the job's source sha, read by
  `proof_lines.site_for`: `live-proof`, `live-site`, `live-menu`, `live-toggle` and `live-deploy` lines.

## DOES NOT SURVIVE (not promised)

- **a-pinned-tree-without-proof-lines.** A job pinned to a sha whose tree has no `rimflow/proof_lines.py` runs no site.
- **a-site-that-lies.** A site command that exits 0 without making its scene; the proof then reads what is there.

## PROMISES (each one is owed a test of the same name)

- **default-site-lifts-the-colony-guard.** A clause with no `live-site` line, in a file with no `live-menu`,
  `live-toggle` or `live-deploy` line, gets `live_site.py --game` with `--max-ticks` lifted: on the lane every game is
  a test game, so a long-kept test map is used, not refused as a colony.
- **own-site-line-wins.** A clause's own `live-site` line is its site.
- **menu-file-takes-no-site.** A file whose proofs want the main menu (or a load pair, or only a deploy) gets no site.
- **site-runs-before-its-proof-and-a-failed-site-runs-no-proof.** On the worker's harness each clause's site runs
  before its proof; a site that exits non-zero runs no proof, and the clause reads UNMEASURED with the reason.

## LIMITS

None. `SITE_ANY_AGE` is not a limit: it lifts `live_site.py`'s colony guard, the same lift as
`testq/stage6_checks.FRESH`.
