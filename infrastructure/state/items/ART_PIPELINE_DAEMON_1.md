# ART_PIPELINE_DAEMON_1 — the constant background art-rendering pipeline

Owner's directive 2026-09-09 (verbatim ruling points): *"We absolutely will want
to leverage this as a constant ongoing art rendering pipeline at whatever
throughput it supports. We may even upgrade our plan if we show that's important
and productive... construct a robust pipeline that runs in the background and
just churns through the huge amount of art we want to regenerate... a dedicated
art pipeline agent... to keep it away from constantly churning bench and
foundry... project how long it would take us to reskin all the assets... If it's
too slow, we can consider elevating to Gemini. Or if the quality issues are too
low, such as unacceptable views... It may also be that our codex account at the
$20 was never even close to sufficient and would take months. Let's find out."*

Replaces CODEX_PARALLEL_WORKERS_1 (absorbs its N-worker queue + grumpiness
detector spec whole). Foundation: `design/RimMandrake/codex_receiving_agent_design.md`
Architecture A (ratified there; the calibration sweep it names is Phase 0 here).
The Opus review's "persistent architecture not warranted"
(`infrastructure/agents/OPUS_REVIEW_codex_graphics_second_pipeline.md`) was
scale-contingent on "runs of 9-25 images"; the owner has changed the scale
premise to the full reskin backlog, which supersedes that verdict.

## spec

**Division of labor (the design decision, incl. the ruled pushback):**
- **Orchestrator = dumb local Python daemon, no LLM.** Not a Codex agent: the
  weekly token window is the binding budget and orchestration reasoning would
  spend the very resource the pipeline exists to maximize; a long-lived Codex
  session is the design doc's Architecture B, whose "normal state is the wedge."
- **Per-job goal iteration = inside Codex.** Each worker is a one-shot
  `codex exec` carrying the receiving-agent AGENTS.md prose (design §3): it
  generates against the job's reference + constraints, runs
  `skills/generating-rimworld-sprites/scripts/validate_sprite.py` itself, and
  iterates ≤3 times on mechanical rejects before returning a manifest
  (`--output-schema` + `-o`).
- **Claude seats only fill the queue** — one JSON job file per sprite/facing,
  carrying provenance (rimflow item id, reference sprite path, canvas, facings,
  style notes, priority). The existing `codex_image.py` path stays for one-offs.
- **Judgment stays with the owner.** The daemon re-runs the validator on every
  returned file (a worker's self-report is never trusted) and rolls finished
  work into per-wave contact sheets; BENCH publishes them as review artifacts;
  rejected rows come back as new jobs with his notes.

**Components** (all under `src/RimMandrake/Utils/artpipe/`):
1. `queue/` layout at `infrastructure/artpipe/{pending,active,done,failed}/`
   (deliberately NOT under `infrastructure/state/` — that prefix is
   rimflow-only). Atomic claim = rename into `active/`. Job and manifest JSONs
   are committed provenance; generated PNGs land in `_artsrc` staging, wiring
   stays a separate concern.
2. `artpiped.py` — the daemon: claims jobs, runs ≤N workers (start N=3, each
   with its own `--codex-home`, the existing seeding machinery), enforces the
   grumpiness detector exactly as specced in the design addendum (6 rows:
   TooManyRequests hard-stop; weekly 80 warn/90 refuse/97 stop; 5h 70→N=1,
   90→sleep-to-reset; 2× wall-clock median → halve N; exit-0-no-manifest = fail
   the request not the account; 🔴 a timeout is NEVER throttle evidence —
   harvest generated_images/ first). Logs per-request: wall clock, meter
   deltas, validator verdict → `throughput.jsonl` (the projection's raw data).
   Runs detached (nohup/systemd-user), NOT inside a seat cgroup.
3. `AGENTS.md` + `manifest.schema.json` — the worker contract.
4. `fill_queue.py` — translates an art-list CSV/JSON (from verdict sheets) into
   job files.

**Phase 0 — calibration, FIRST (tonight, before the daemon exists):**
sweep N ∈ {1,2,4,6} over the same 8 real jobs (wrecked-machine facings, real
references), measuring img/h, failure rate per N, and %-of-weekly-window per
image (meters read from rollout JSONL; baseline today 13% weekly / 22% 5h at
12:22). Also settle the native-transparency question (design §2.3, one
generation) — if the built-in tool now emits real alpha, the chroma-key stage
is deleted from the worker contract before it is ever built.

**Phase 2 — projection (the owner's actual question):** backlog inventory
(tonight's flora NEW-ART ledger + creature regen verdicts + wrecked machines
×4 facings + the standing art-commission items) × measured %/image →
images/week ceiling at the $20 plan → calendar estimate. Escalation
thresholds, pre-agreed: too slow → plan upgrade or Gemini ($0.02-0.04/img,
key ready, billing NOT yet enabled — reconfirm with the owner before any
enable); unacceptable views/consistency → Gemini contrast batch
(GRAPHICS_GEMINI_BILLING_DECISION_1 holds that protocol).

## verify
- Calibration table exists with MEASURED img/h and %window/image for each N,
  and a written projection (weeks at $20) the owner has seen.
- Daemon drains a 12-job queue unattended with per-job manifests, correct
  detector behavior under a forced 429 (mocked), and a contact sheet at the
  end; kill -9 mid-run loses no job (pending/active reconciliation on start).
- A second seat files jobs while the daemon runs; nothing races.

## criteria
The owner can name any art item, a seat queues it, and finished validated
sprites with a review sheet appear without BENCH or FOUNDRY holding the work.

## traps
- Weekly window is shared with ALL Codex use — meters are a budget gauge, not
  a throttle predictor; throttle arrives as fast explicit TooManyRequests.
- `--` trap: exit 0 with no output is a no-op, not success.
- pkill -f matches your own wrapper (kill by PID); heavy children in a seat
  cgroup kill the window (run detached, own scope).
- Chroma-key has twice destroyed subjects — prefer native alpha if §2.3 tests
  true.
