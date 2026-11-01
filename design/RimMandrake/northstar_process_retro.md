# Northstar process retro: GimmeSomeSlack to its validated bar

Item `NORTHSTAR_PROCESS_RETRO_1`, written 2026-10-31. Owner's ask, 2026-10-05: review the process, not the mod; say what
worked and what did not, update the skills, and build the Python helpers that would have made it easier.

**The gate.** The item waited on GimmeSomeSlack GREEN. The owner took that off by card on 2026-10-20 ("Done after one live
pass", with the GSS checklist VALIDATED, 9/9 bars). `modcheck status` today reads GSS RED at a stale hash (FAIL 1, PASS 113,
UNMEASURED 5). That is the mod's own state and was not re-measured or changed here.

**Inputs.** Read: the 2026-10-05 FOUNDRY handoff, `debug_process.md`, the seeded north star, and the GSS lessons. Missing:
`Transient/gss_northstar_seed_notes.md` is in no clone, because Transient is untracked. The lesson
`20261005T155316Z-FOUNDRY-proof-run-goes-stale-when-any` is also gone: the handoff lists it as untracked. Its content
survives in the handoff, and its first half is in `live-debugging-proof-harness`. Its second half, SL4 flaking when a fresh map
yields under 2 free colonists, survives only in that handoff.

## What worked

- **One functional script per mod, ending in a recorded run.** The GSS proof reached 143 PASS + 1 SKIP on 2026-10-05, and
  each later regression had a named row to fail. Nothing here suggests changing it.
- **The hash-bound record.** A run cannot outlive the code it measured. Staleness annoyed the agents, but it was honest.
- **Seeding bars for him to cut.** Agents drafted 17 bars from his words; the checklist now validated has 9 lines. Drafting first made his review
  a cut, not a blank page.
- **Sharing review-map code early.** `modcheck/reviewmap.py` came out of the second builder (FlowWorks) and now carries
  `save_keeper`, `sweep_pawns` and the signs, so the rule "a save is OK only if exactly one new file appeared" lives once.

## What did not work

- **Friction lived in a handoff, not in code.** All five 2026-10-05 frictions were written down the day they bit, then the
  item sat blocked for 15 days. Blocking the fix on the mod going Green was the mistake: a tool fix needs no such gate.
- **Inputs left in Transient.** See above. An item must carry what it needs.
- **Status words with no vocabulary.** A `RECORD` row made a clean proof read RED and nothing said why.
- **"Unbuilt" read from documents.** On 2026-10-10, 4 of 7 "unworked" GSS pieces were already built; the sweep read a design
  doc rather than `git log -S` (lesson `20261011T064401Z`). This retro's own candidate list repeated the pattern: three of
  six helpers already existed.
- **Preflight gaps in the proof.** On 2026-10-29 an expired companion test profile cost a full `proof_all` an UNMEASURED row;
  `proof_all` does not check it up front the way `modcheck/runner.py` does (lesson `20261029T135922Z`). Not fixed here, see below.

## Helpers: the six candidates

| candidate | verdict | where |
|---|---|---|
| `game_cycle(tier)` | already exists | `src/RimMandrake/Utils/northstar_driver/live_session.py` does stop, tier, deploy, launch, wait, quicktest, run |
| `kill_hostiles(B)` | already exists | `sweep_pawns` in `src/RimMandrake/Utils/modcheck/reviewmap.py` |
| `save_keeper(B, name)` | already exists | same file |
| `literal_log_wait(token)` | **built** | `src/RimMandrake/Utils/logwait.py`, selftest `selftest_logwait.py`; `live_session.py` now uses it |
| proof-row status vocabulary check | **built** | `KNOWN_ROWS` and `unknown_statuses` in `src/RimMandrake/Utils/modcheck/record.py`, selftest `selftest_record.py` |
| `run_from_root()` | **replaced by a guard** | one live case; `--log` fixed, `src/RimMandrake/Utils/selftest_repo_cwd.py` stops the next one |

## What was NOT changed, and why

- **`proof_all.py` still requires `--live`.** A bare run prints usage on purpose, and the script has no cwd-relative path, so
  the handoff's "must run from the repo root" holds only for `human_review.py --log`, now fixed.
- **`GimmeSomeSlack/shader_sway_look.py` keeps its relative `--out`.** It sits in the hashed mod root, so editing it stales the
  mod's record for a dev-only flag. `selftest_repo_cwd.py` lists it as known, and fails if that goes stale.
- **Staleness on any mod-folder edit is kept.** It is the discipline, and `.hashignore` plus run manifests (`modcheck/reuse.py`)
  have since handled the false alarms.
- **Unknown statuses still read RED; they are not refused or made OK.** FlowWorks proofs emit `INFO` and `MEASURED` today.
  Whether those should count as OK loosens a bar, which is the owner's. Refusing would block recording a real FAIL.
- **The blind-scan hook is unchanged.** It was right; the missing piece was a tool for a wait.
- **`live_session.py` still refuses unless FOUNDRY holds the bridge.** Since the v3 cutover that matches who owns live proofs.
- **The `proof_all` test-profile preflight was not added.** It is a mod-proof change in FOUNDRY's lane, and editing the proof
  script could void a reusable GSS result. It is on file as lesson `20261029T135922Z`.
- **`stage_review.py`, `stage_xenotype_grid.py`, `scenes/scenelib.py` and `modcheck/helpers.py` keep their own `kill_hostiles`.** They
  are separate callers with different signatures, and merging them for tidiness carries risk with no bug behind it.
- **`debug_process.md` is unchanged.** No rule in it was shown wrong.
