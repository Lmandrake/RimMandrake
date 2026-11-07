# Writing a proof that Lightspeed can run (no LLM)

Read this before writing a `live-proof` line, a mod's proof script, or a validation row.
Lightspeed is the testq lane (`src/RimMandrake/Utils/testq/testq.py`, worker
`infrastructure/stevedesktop/worker.py`) that runs proofs with no model in the loop.
93% of test units (4,844 of 5,225) need no LLM (census 2026-11-05,
`design/RimMandrake/lightspeed_2026-11-06.md`). A proof only lands in that 93% if it is
written for it. Each rule below says why and where it comes from.
"PLANNED (item X)" means the tool does not exist in `src/` yet. Use the rule marked
"today" until it does.

## 1. The verdict is data, not prose

- **Exit 0 = PASS, 1 = FAIL, 2 = UNMEASURED.** The reason: `worker.py run_proofs` reads
  exit 0 as PASS, 1 as FAIL and anything else as UNMEASURED. A proof that exits 1
  because the site was dirty or the bridge dropped files a FAIL against a healthy mod.
  Known defect: `proof_all.py` returns 1 for both FAIL and UNMEASURED. It should return
  2 when nothing FAILed. That fix is owed. Do not copy its exit code.
- **One deterministic row per criterion**: id, verdict, measured value, bar. Print the
  verdict last. The reason: `relentless_live.py` takes the verdict from the LAST verdict
  line. The repro-miss verdicts are spelled exactly `NOT REPRODUCED` and `NOT SHARED`.
- **An UNMEASURED line names its reason on the same line** (`UNMEASURED: water within 2
  cells of the pit`). The reason: `relentless_live.exit_reason` skips a bare
  `UNMEASURED` and groups repeats by that reason. With no reason given, every stop on
  that proof shares one cause key and turns into a RELOAD request. Keep paths, numbers
  and times out of the leading words, so that two runs stopped by the same thing share
  the key.
- **ROWS_JSON results.** PLANNED (item LIGHTSPEED_WIRE_GSS_FIRST_NO_LLM_PATH). The worker
  contract (print `ROWS_JSON <path>`, and the worker maps the rows) is not built.
  Today: write your rows to a JSON file anyway and print the plain row table. The exit
  code alone carries the verdict.
- **No verdict from judgement.** If a row needs eyes (art, "looks right"), it is class C.
  Say so in the criterion, and do not fake a numeric bar for it.

## 2. A proof line the runner will accept

Format (`relentless_live_round.py` docstring, `relentless_game.py` BRIEF):
`live-proof A2: <cmd>` in `infrastructure/state/live_proofs/<ID>.txt`, plus
`live-mods:`, `live-deploy:`, `live-tier [A1]: <tier>` and `live-site <CID>: <cmd>`.
The criteria go in `<ID>.criteria` as `A2 L1: what is observed`.
`relentless_live.py` (`owed()`, `refused_proof()`) refuses the following, so writing
any of them wastes the round:

| Refused | Reason |
|---|---|
| `$`, backticks, `eval`, `{a,b}`, a backslash line-continuation. The one exception is a whole-word `$(wslpath -w <literal path>)` | The command must be the literal text that runs, with no shell building it. A `$`-built command cannot be replayed or audited. |
| `modlist_swap`, `modcheck run`, `deploy_custom_mods.py ... --apply`, `game UP/DOWN/...` | A proof is read-only. It must not load, restart, swap or mutate the game. |
| Flyer words (fly, flight, wings, airborne, take off...), unless it is a vehicle | Flight is never live-tested unattended (CLAUDE.md). See §5. |
| Reading `OWNER.jsonl` | A proof measures the game, not the owner's ledger. |
| A criterion cut at 160 chars (`model.CRITERION_TEXT_MAX`) with no prose holding the rest, or a re-tiered one | A truncated criterion is a different test. Keep each criterion ≤160 chars, or put the full text in the item prose. |
| A `live-site` that is not `python.exe src/RimMandrake/Utils/live_site.py <plain args>` | `SITE_CMD`: there is one site builder, and only plain arguments are accepted. |

An exit 1 whose output matches a known harness pattern is read as a harness failure,
not a mod FAIL. Do not rely on that. Exit 2 yourself (§1).

## 3. Advancing time: never write advance-read-repeat

- **Today**: advance with `B.ticks(n)` (`validation_core._BridgeBase.ticks`). It routes
  through `clockgate.advance_chunk`, which prefers `jawa/safe_advance`, and safe_advance
  runs many ticks per frame (chunks of 60 inside a 40 ms frame budget,
  `JawaBenchVitals.cs` SA.Frame). Plain `rimworld/step_game_ticks` advances only **one
  tick per frame**. 259 lines in 139 files still call it directly.
- **Do not write a loop of "advance a few ticks, read, repeat".** The reason: every
  round trip costs ~53 ms. TheSump `prove_glasswalk_speed.py walk_exact` makes 4 calls
  per 2 ticks, which is ~2,000 calls for one row. To read an end state, advance the
  whole window in one call, then read once. When the event time matters, bound it from
  two reads (before and after the window) and the design's contract.
- **Stop-on-condition**: PLANNED (items CONDCORE_BUILD_THREE_VALUED_TREES,
  CONDPROBES_WIRE_ENGINE_READS, ADVANCEUNTIL_WIRE_PER_TICK_STOP,
  CONDSDSL_WIRE_PYTHON_BUILDERS). That is `B.until(cond, max_ticks)` over
  a `cond_eval` tool, where an UNKNOWN probe maps to UNMEASURED and never to false.
  **Sampling across a window**: PLANNED (items CONDWATCH_BUILD_OWNED_RINGS,
  RINGPROBES_WIRE_EVENT_CURSORS), `B.watch`. A condition hit is evidence. The Python
  proof still makes the verdict.
- Do not migrate an existing direct `step_game_ticks` caller blind. Its verdicts must
  hold against the old run first (STEPCALLS_MIGRATE_WHERE_VERDICTS_HOLD). The flyer
  landing step (FLYER_LAND_TICKS) stays on step_game_ticks.
- Do not play unpaused (`play_for`, `scenelib.run` at speed 4) as a way to pass time in
  a proof (SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY). `rimworld/set_time_speed` has left the
  game paused before. Read the state back.
- **Ready waits**: PLANNED (item READYWAITS_UNIFY_ONE_HELPER, `await_lifecycle`).
  About 57 copy-pasted ready loops exist. Today: call `live_site.wait_ready` /
  `wait_state` (`src/RimMandrake/Utils/live_site.py`) and do not write a new loop.
- **Reads**: batch them. Use `get_terrain_batch`, the rect tools and `jawa/get_defs`,
  not one call per cell. FlowWorks v2 L_preflight made 371 read calls. Batch-read
  tools are PLANNED (item BATCHREADS_BUILD_ROUND_TRIP_CUT).
- The lint that would refuse poll loops is PLANNED (item POLLLOOPS_MIGRATE_TO_UNTIL,
  `lint_calls.py`), and so is the proof-line lint at filing (PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN).
  Today: you are the lint.
- **Condition node ids (`conds_dsl`) come from ONE counter across the `until` tree and every watch tree.** Read ids from the compiled canonical; never renumber. (`clockgate.resumable_stop` and `is_benign_stop` take dict triggers only; `conds_dsl.run_until` filters string triggers such as `('cond','unknown')` before calling.)

## 4. Validate the site before the proof, and name the UNMEASURED reason

- Clear the site and read it back (`validation_core.prepare_site`). See
  `sites-and-timing.md`.
- **Water and source margin**: check the footprint plus a 2-cell margin with
  `jawa/flowworks_excavation_rect` (`includeTerrain`) for `isSource` / water cells. The
  reason: a deep pit orthogonally beside river source cells filled by gravity. That
  was correct FlowWorks behaviour, but it spoiled the ladder-refusal row, because the
  pawn's refusal could no longer be attributed (lesson
  `skills/live-debugging-proof-harness/references/sites-and-timing.md`).
- If a check fails, exit 2 with a named reason, for example
  `UNMEASURED/SITE water within 2 cells at (x,z)`. Never PASS or FAIL on a bad site.
  A named reason is what lets the runner route it without an LLM
  (UNMEASURED_ROUTES_WIRE_NO_SIX_HOUR_NAPS).
- `order_pawn` with `waitTicks` ≤600, then reconcile and `pause_game`. The reason: a long
  wait hits the 30 s client timeout and leaves the game unpaused, with the outcome unknown.

## 5. Flyers are state reads only

Read a flyer's defs, comps, job and position state. Never prove its flight live: flight
needs the owner present (CLAUDE.md). Flyer-frame proofs are a joint session, item
FLYERFRAMES_PROVE_JOINT_SESSION (needs=owner). The runner refuses flyer words (§2).

## 6. Prefer the minimal list

Declare the smallest tier that holds the mod (`live-tier: <tier>`, run on SteveDesktop
through testq). Fall back to `live-mods:` only when no tier fits. The reason: an
exact-tier job is what Lightspeed can batch, a 13-mod list loads in 22 s, and the
owner's full list takes ~25 min (`rimworld-load-round`). The proof must not swap the
list itself (§2).
- **The `--minimal` modlist (26 mods) does NOT include `mandrake.rm.gimmesomeslack`:** `validation_aerial.py` on it fails `A_probe_channel` 'No loaded type RimMandrake.GimmeSomeSlack.Aerial...'. GSS live proofs need `modset_builder.py --tier gimmesomeslack` (10 mods); a brief saying 'minimal list' for GSS is wrong.

## 7. hot_reload_defs is not a speed path

`jawa/hot_reload_defs` is retired and unproven. It crashed a 589-mod game and left it
unable to generate pawns (HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1). Never count it in a time
estimate, and never use it to skip a load. Restart on the minimal list instead.

## 8. Owner-look scenes come from the proof script

A scene the owner will look at is built by the mod's own proof script (`prepare_site`,
the dry plot, the controls), never staged by hand. The reason: a hand-staged scene
proves nothing that the proof reproduces. Waiting for a screenshot to settle on a
paused game is PLANNED (item SHOTSETTLE_BUILD_PAUSED_BARRIER). Today: pause, then
read the state back before `take_screenshot`.

## Derive the needed live mods from the proof, not from the failure
Missing live-mods names are mostly invisible after the fact: 7 of 20 hand-repaired items (folded biome proofs, HEAVY_TEXTURES, HORRORS) never showed a mod-absence row, because envcause routes them `proof_or_site` ('MISSING', 'proof crashed', 'modcheck wrote no results'), and `mods_of(sha)` derives nothing for proof-only builds or folded sources. Derive the needs statically from the proof before the slot (script path plus folded map, fixture save header, `--mod` args, types and defNames), not from the build diff or failure text.
