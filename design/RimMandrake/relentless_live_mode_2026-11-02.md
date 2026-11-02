# Relentless live mode: one agent, two modes (2026-11-02)

Item `RELENTLESS_LIVE_BUILD_ONE_AGENT_TWO_MODES`. Owner, 2026-11-02: *"I gut says equip the same agent to understand
appropriate use of resources."* Conductor's ruling: ONE Relentless, two modes. The worker works offline first. The
supervisor leases the bridge, which is scarce, to one live user at a time. An item goes live only when its offline
proof is green and a clause truly needs the game.

## What already existed (audit)

| piece | what it does | what it lacks |
|---|---|---|
| `src/RimMandrake/rimflow/relentless_live.py` | One live criterion of a **built/validated** item, proved on the running game. It refuses flyers and forbidden proofs, checks the deploy plan and that the game started after the deploy, takes the bridge with `--idle-ok` and releases it at once, then records `rimflow verify --criterion` on the built sha. | Nothing feeds it. It never deploys or restarts. |
| `src/RimMandrake/rimflow/relentless_live_round.py` + `live_tick` | Every 30 min while the game runs, it sweeps every built item that has a `live-proof <crit>:` line in `infrastructure/state/live_proofs/<ID>.txt`. | Last round (2026-11-02 05:18Z): 0 eligible, **819 "no proof"**. Nobody writes the lines. |
| `relentless.py` pool (`eligible`) | Enrols `pool_needs: ["offline"]` only. | Live-game items (`needs` deploy / game-up / bridge) never reach a worker. The comparison doc: 0 vs FOUNDRY's 10. |
| worker brief | Names `live-debugging-proof-harness` and `rimbridge`. | It does not teach the offline-first rule, and it gives no way to say "this clause needs the game". |
| blind PASS → `rimflow close` | Closes the item. | If the item owes live criteria, `close` refuses with "has not earned its close", and the item ends `close_refused`. |
| item `RELENTLESS_LIVE_BUILD_ONE_BUILT_LEAF` (closed 2026-11-01) | Proved one leaf through `relentless_live.py`. | — |
| scratch clone `/home/mandrake/rm/scratch/BENCH/RELENTLESS_LIVE` | Holds no unlanded work. Its two dirty shards contain the same lines in a different order, and it is 268 commits behind. | — |

FOUNDRY's rule (`infrastructure/agents/FOUNDRY.md`, plus the owner's memo *geometry solved offline in Python first*,
2026-10-24): verify only what LIES, and do it cheapest level first: L0 offline, then L1 reads in one minimal-list
sitting, then L2 on one quicktest map, then GREEN. A live check is owed only to a mechanism nobody has seen run.
Geometry is swept in Python, and the game is used only for the final look.

## Gaps built here

1. **Pool.** `rules.game.pool_needs` (deploy, game-up, bridge) enrols live-game items into the same pool. Each one
   starts in the offline phase like any other item.
2. **Contract.** `relentless.py contract ... --game "A2,B3" --game-why "<why the game is needed>"` names the clauses
   that need the game. `--no-offline "<why>"` states that no offline proof is possible. Each named clause needs a
   `live-proof <crit>: <cmd>` line in `infrastructure/state/live_proofs/<ID>.txt`, the format the live round already
   reads.
3. **Brief.** The worker brief now carries the resource rule (`relentless_game.BRIEF`): offline first; live only for
   clauses that need it; batch live checks; never a flyer's flight; never fullscreen or focus the game; the minimal
   mod list when it is enough. The checker brief tells the checker to read a WEAK when a live-proof line would stay
   green while its clause was broken.
4. **Offline PASS does not close a game item.** After a blind PASS, an item whose contract names game clauses goes to
   `rimflow implemented --sha` (those clauses owed at their levels) and to supervisor status `game`. The offline
   PASS on that sha is the green offline proof, and it is recorded in `st.game.offline_green`.
5. **Supervisor lease** (`relentless_game.step`). At most one item is in a bridge phase at a time. Before a lease,
   four things must hold: offline green on the **same sha** as the build, or a `--no-offline` reason; a proof line
   for every clause; no flyer; and `rimflow bridge idle` says TAKEABLE (his OWNER hold and `./bridge` override are
   enforced there). The proving run is a detached `relentless_game.py prove --item`, which calls
   `relentless_live.run` for each clause: take with `--idle-ok`, release at once. That is the **blind live check**:
   the supervisor reruns the proof lines on the deployed build, with no worker notes. All PASS and the ledger's last
   `verify` moves the item to done. Any FAIL returns the item to an offline worker carrying the live finding.
   UNMEASURED with a stale deploy or no running game starts the **staging** step.
6. **Staging.** This is the only step that changes the game. One pilot-agent worker gets the bridge (`take --idle-ok`)
   and a brief. It deploys the item's mods, brings the game up or down with `./game --idle-ok --why`, chooses the
   minimal list when it is enough, and reports `relentless.py game-ready`. The supervisor releases the bridge as
   soon as staging ends, however it ends. A staging worker is never launched while another game-phase item is live.

Not built here: a supervisor-side game launcher. `./game` only stamps the state. The launch itself is the staging
worker's job, done under the lease with the `rimworld-load-round` skill, as FOUNDRY does it.
