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
