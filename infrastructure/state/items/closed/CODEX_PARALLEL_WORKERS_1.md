# CODEX_PARALLEL_WORKERS_1 — N-worker codex exec queue with the receiving-agent prose

Owner's ask 2026-09-06: accelerate graphics generation with a receiving agent inside Codex.
Design + measurements: `design/RimMandrake/codex_receiving_agent_design.md` (Opus, same day).

## spec
- Architecture A from the design: a request-queue directory driven by N parallel one-shot
  `codex exec` workers, each carrying the `AGENTS.md` receiving-agent prose contract and
  returning a schema-validated manifest via `--output-schema` + `-o` (both exist on this
  install, neither used today).
- 🔴 Each worker gets its OWN `CODEX_HOME` (openai/codex #11435: parallel instances
  cross-talk through a shared one).
- Expected ~3–4× at N=4 (UNMEASURED); ~1.8× already demonstrated (4 concurrent sessions
  observed; 102 img/h burst vs ~58 serial). The batching ban in `generating-images` was
  the orchestrator's ceiling, not the API's — lesson to LESSONS_INBOX.
- Build the grumpiness detector from the addendum's six-row table: read
  `rate_limits.primary/.secondary used_percent` + `resets_at` from each session's rollout
  JSONL (the `--json` stream does not carry it; `thread.started` gives the thread_id that
  names the file). Top rule: **a timeout is never evidence of throttling — harvest first.**
  Throttle on a ChatGPT login arrives as a fast explicit `TooManyRequests` (no
  retry-after) and can fire while meters show headroom — treat `used_percent` as a budget
  gauge, not a predictor. The binding budget is the WEEKLY token-metered window (read
  65%→70% in 47 min this morning), so reasoning effort moves it more than image count.
- Depends on `CODEX_WRAPPER_HARVEST_FIX_1` landing first.

## verify
Four workers drain a 12-request queue with per-request manifests; wall-clock vs serial
measured and written down; the detector logs both meters per request.

## FOUNDRY, 2026-09-07: dependency satisfied; per-worker CODEX_HOME done; queue architecture re-litigated, not resolved

`CODEX_WRAPPER_HARVEST_FIX_1` closed today (`814d4223`) — this item's own stated
dependency is now satisfied.

**Already done, as a side effect of that fix, not this item**: per-worker `CODEX_HOME`
(`--codex-home DIR` on `codex_image.py generate/edit/probe`, auto-seeded from the shared
home, with the WSLENV propagation fix this item's own spec anticipated almost verbatim —
"a WSL process does not pass a bare env var to a Windows child" was independently
measured twice today). `gen_sea_facings.py`'s 3 concurrent workers already use it.

**Separately, today**: an owner-requested Opus review of a much heavier proposed
architecture (a persistent app-server worker + durable filesystem job queue — a
DIFFERENT design than this item's "N one-shot `codex exec` workers draining a request
queue," but overlapping in spirit) concluded that architecture is not warranted at this
project's actual scale (13 callers, 3 batch drivers, runs of 9-25 images; in-process
concurrency already measured at 102 img/h vs 58 serial). Full verdict:
`infrastructure/agents/OPUS_REVIEW_codex_graphics_second_pipeline.md`. That review's
ONE recommended-but-undone piece overlaps this item's "grumpiness detector" directly:
reading `account/rateLimits/read` before batching, which nothing does today (weekly
usage read at 82% during that same review). The reviewer deliberately did not wire it
in because it changes pathway 1's default batching behavior — an owner call, not
FOUNDRY's to make solo.

**Not built this pass**: the N-worker request-queue + `AGENTS.md` receiving-agent prose
+ `--output-schema`/`-o` manifest validation, and the grumpiness detector itself (reading
`rate_limits.primary/.secondary` from rollout JSONL). Left `doing`/blocked rather than
closed — real scope remains, but building it without a ruling on queue-vs-no-queue (see
the Opus review) risks the same over-build the review just argued against for the
sibling architecture. Flagging for the owner: is the lighter "just read rate limits
before batching, no queue" version worth building on its own?
