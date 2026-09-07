<!-- status: PROPOSAL, authored by CODEX (a different AI, not Claude), 2026-09-06.
     NOT the live skill. This is a captured snapshot of a rewrite CODEX made
     IN PLACE to the real skills/generating-images/SKILL.md; that file has
     been REVERTED to its original, working, one-shot-pipeline content
     (owner, 2026-09-06: "Do not harm the current CODEX pipeline, since it
     works"). This copy is preserved only so the design is not lost, and so
     an Opus review can compare it against the live skill and the
     CODEX_PROPOSAL_ART_WORKER.md / CODEX_PROPOSAL_GRAPHICS_WORKFLOW.md
     companion docs. The frontmatter `name:` below is left intact as
     evidence of what CODEX wrote, but this file lives outside `skills/` on
     purpose and is never loaded as a skill. Do not move this file into a
     `skills/` directory without an explicit owner ruling that this design
     is adopted. -->

---
name: generating-images-CODEX-PROPOSAL-DO-NOT-LOAD
description: Dispatch, supervise, steer, and evaluate raster generation or editing through the persistent Codex graphics worker. Use for raster images, textures, sprites, icons, mockups, transparent cutouts, and visual variants. Prefer the app-server plus durable queue; use the legacy one-shot wrapper only when explicitly requested.
---

# Codex graphics controller (PROPOSAL, unvalidated — captured draft, not live)

Claude owns project intent and dispatch. Codex owns prompting, rendering,
self-review, bounded iteration, and delivery. Use the durable file queue for
state and Codex app-server for live control.

The full worker contract is
`infrastructure/agents/CODEX_ART_WORKER.md`. It is cold-path documentation.
Read it when bootstrapping or recovering a worker, resolving a schema/version
question, or handling an error not covered here. Do not reread or paste it for
ordinary jobs. A persistent Codex worker reads it once and processes bounded
queue requests by ID.

## Token-efficient defaults

- Reuse one initialized app-server process and worker thread; send deltas and
  job IDs, not repeated policy or history.
- Put specifications and controls in files. Do not duplicate their bodies in
  chat prompts or app-server text.
- Pass reference paths and hashes, never base64 image data.
- Use low reasoning by default. Use medium only for genuinely difficult visual
  comparison or conflicting references.
- Poll structured state; emit human prose only on a state/threshold change,
  explicit `status`, required decision, failure, or completion.
- Keep one identity-sensitive asset family in one thread. Parallelize only
  independent families with distinct output paths.
- Never research pricing during normal dispatch or usage polling.

## Hot-path interface

Preferred transport is Codex app-server over stdio plus the queue. Resolve the
current executable once with:

```text
python3 skills/generating-images/scripts/codex_image.py probe
```

Start `<resolved-codex.exe> app-server --stdio`, complete
`initialize`/`initialized`, and retain the process. Windows paths cross the
protocol; do not send WSL-only paths. Use `workspaceWrite` limited to the queue
and declared delivery parents; references and the repository may be read-only.
Never use approval/sandbox bypass flags.

For each job:

1. Read live limits and apply the scheduler below.
2. Validate and atomically publish one request JSON.
3. Resume the persistent worker thread; start one only if none is valid.
4. Send only: `Process <JOB_ID> from <QUEUE>; stop at its terminal state.`
5. Monitor app-server events and append-only queue logs.
6. Steer with a short control delta. Interrupt only for urgent stop.
7. Verify the terminal manifest and selected artifact.

Resolve the installed image-generation skill during worker bootstrap, not per
job. Record thread/turn IDs. A disconnect or controller timeout does not prove
that generation failed; inspect persisted events and artifacts before retrying.

Queue root, unless `RIMWORLD_CODEX_ART_QUEUE` overrides it:

```text
C:\Users\Mandrake\AppData\Local\RimworldCodexArtQueue
```

For manual Codex desktop startup, publish the request and send:

```text
Assume D:\Luke\dev\Rimworld\infrastructure\agents\CODEX_ART_WORKER.md.
Worker id codex-art-01. Queue root C:\Users\Mandrake\AppData\Local\RimworldCodexArtQueue.
Process job <JOB_ID>; max jobs this run 1; exit at terminal state.
```

File-only control is allowed when app-server is unavailable, but it cannot
interrupt an image call already in flight.

## Compact request API

Publish immutable UTF-8 JSON to `requests/pending/<job_id>.json` by atomic
rename. Common request shape:

```json
{
  "protocol": "rimworld.codex-art/v1",
  "job_id": "ASSET_FAMILY_VARIANT_001",
  "created_at": "<ISO-8601 with offset>",
  "created_by": "claude-code",
  "mode": "generate",
  "goal": "<visible result and intended use>",
  "intended_use": "<consumer and viewing scale>",
  "references": [{"path":"<absolute Windows path>","sha256":"<hash>","role":"identity","take":["<detail>"],"avoid":[],"priority":"required"}],
  "visual_spec": {"subject":"<subject>","view":"<camera/facing>","composition":"<framing/footprint>","style_medium":"<visual language>","palette":"<palette>","desired_state":[],"avoid":[]},
  "invariants": ["<fact that must survive every edit>"],
  "generation": {"background":{"kind":"transparent"},"target_aspect_ratio":"1:1","self_iterate":true,"max_iterations":4,"selection_authority":"worker","preserve_all_iterations":true},
  "delivery": {"outputs":[{"path":"<absolute Windows path>","width":512,"height":512,"format":"png","alpha":"required"}],"subject_footprint":{"min_canvas_fraction":0.45,"max_canvas_fraction":0.82},"overwrite":false},
  "acceptance": [{"id":"primary_read","kind":"visual","severity":"must","criterion":"<observable pass condition>"}],
  "authority": {"may_normalize_prompt":true,"may_add_unrequested_subjects":false,"may_change_references":false,"may_use_chroma_fallback":false,"requires_human_acceptance":false}
}
```

Use `mode: edit` with exactly one `edit_target`. Reference roles are
`identity`, `edit_target`, `style`, `composition`, `palette`,
`silhouette`, or `avoid`. State what transfers; one unlabeled exemplar must
not silently define everything. Verify paths before publish and hash
identity/edit references.

Describe observable goals, invariants, intended scale, and measurable delivery
facts. Do not prescribe tool flags, internal canvas size, generated-image
storage, arbitrary retry loops, or “keep trying until perfect.” Final width,
height, alpha, footprint, and path belong in `delivery`, not the art prompt.

Default `max_iterations` is 4 for new art, 3 for constrained edits, and 1 for a
plumbing test or human-led choice. Every submitted generation/edit call counts,
including refused or outcome-ambiguous calls. Each retry needs one written
diagnosis and one targeted change. Never raise the ceiling without owner or
controller authority.

## Controls

Write sequenced controls to the durable inbox and send the same short delta by
`turn/steer` when the turn is active.

| Command | Effect |
|---|---|
| `feedback` | Add one observable correction while preserving named invariants |
| `amend` | Overlay a structured request patch; never edit the claimed request |
| `set_max_iterations` | Change the absolute ceiling; only authorized owner/controller may increase it |
| `pause` / `resume` | Checkpoint without a new image call / continue |
| `status` | Return a concise checkpoint; no image iteration |
| `report_next_tier` | Invoke the on-demand OpenAI-plan report below; no image iteration |
| `accept` / `reject` | Select or reject a named preserved iteration |
| `stop` | Start no new call, preserve returned work, checkpoint, and exit |

Use `turn/interrupt` for urgent stop. Natural-language controls are valid, but
log the original and normalized interpretation. “Half as large” normally means
subject footprint, not PNG dimensions; ask one question if context cannot tell.

## Usage and scheduling

Before a batch and after a completed job, call
`account/rateLimits/read`. Prefer `rateLimitsByLimitId.codex`, falling back to
`rateLimits`. `usedPercent` is consumed; remaining is `100-usedPercent`.
`resetsAt` is Unix seconds. For every non-null reset, preserve the Unix value
and record UTC plus Pacific local time using `America/Los_Angeles`. Every
user-facing usage statement includes the full Pacific date, time, and correct
seasonal suffix (`PST` or `PDT`); never emit an unlabeled time or call a
daylight-saving timestamp `PST`. Null means unknown, not zero. The interface
exposes no reliable images-remaining count, so never invent one.

Mechanically append `usage_read` and `usage_report` to
`workers/<worker_id>/usage.jsonl`; mirror them into an active job log. Omit
opaque account/reset-credit IDs. Record plan, windows, used/remaining, resets,
including `resets_at_utc` and `resets_at_pacific`, credit availability, limit
state, and scheduler result. Do not generate a prose report unless explicitly
requested or the effective policy changes.

Apply the most restrictive row:

| Signal | Policy |
|---|---|
| Both windows under 70%, no throttle | Up to 4 calibrated independent workers |
| Weekly 70–79% | At most 2; no unbounded overnight batch |
| Weekly 80–89% or primary 70–89% | Warn once; at most 1; new jobs max 2 iterations |
| Weekly ≥90% or primary ≥90% | No new image calls; checkpoint/wait |
| Weekly ≥97% | Preserve returned work and stop pool |
| Rate/usage-limit error | Stop global dispatch; do not probe with another image |
| Unknown limit field | At most 1 until clarified |

Set `next_tier_report_recommended: true` when weekly usage is at least 75%,
either window is at least 80%, or a limit error occurs. This boolean is not a
request and triggers no research or prose. Reset credits are owner-controlled;
report their count but never redeem one without explicit authorization.

### On-demand plan report

Only explicit owner text or `report_next_tier` triggers this cold path. Ask
Codex to invoke its current OpenAI product-documentation/self-knowledge skill
once. It must refresh account limits, verify current plan names/prices/allowances
from official OpenAI sources, distinguish allowance from image count, latency,
throughput, concurrency, and service throttling, then append one
`upgrade_report` with URLs and `checked_at`. If verification fails, omit
prices. Never use embedded constants, repeat the report per poll/job, or consume
an image iteration.

## Error actions

Always preserve exact code/message, HTTP status, job/thread/turn IDs, iteration,
and whether an artifact appeared.

| Signal | Action |
|---|---|
| `UsageLimitExceeded`, `TooManyRequests`, HTTP 429, image rate-limited | Stop dispatch; log limits/reset; do not probe or redeem a reset |
| Stream disconnect or outer timeout | Outcome unknown: reconnect and inspect events/artifacts before retry |
| HTTP 5xx / `InternalServerError` | Harvest any completed artifact; otherwise one delayed retry if limits and budget allow |
| HTTP 400 / `BadRequest` | Fix one exact mechanical payload defect; otherwise `needs_control` |
| 401/403 / `Unauthorized` | Stop and request restored authentication |
| `ContextWindowExceeded` | Checkpoint bounded state; continue in a fresh worker thread without spending an image iteration |
| `ResponseTooManyFailedAttempts` | Stop job; no outer immediate retry loop |
| `SandboxError` | Correct declared roots/path; never broaden permissions automatically |
| Moderation/refusal | Preserve refusal; retry once only for a harmless clarification |
| `turn/completed: interrupted` | Mark stopped; harvest anything returned before interruption |
| Success with no declared output | Search tool events/artifacts before another generation |
| Wrong dimensions | Preserve raw image and conform deterministically; regenerate only for composition/content |
| Opaque result for transparent request | One targeted edit if budget remains; chroma only if authorized |

For any unlisted or ambiguous failure, load the cold-path worker contract. Do
not convert a transport error into an art-direction change.

## Review, delivery, and completion

Codex reviews every returned image before selection: primary read at intended
scale, required reference details, composition/facing/silhouette/footprint,
edit invariants, exact text, alpha, dimensions, and non-overwrite behavior. A
retry names the failed criterion and changes one relevant thing.

Keep raw and intermediate artifacts. For deterministic conformance use the
repository tools when applicable:

- `skills/generating-rimworld-sprites/scripts/conform_sprite.py`
- `skills/generating-rimworld-sprites/scripts/validate_sprite.py`
- `skills/generating-images/scripts/preview_alpha.py`
- `skills/editing-images/scripts/compare_images.py`

Native alpha is preferred; chroma is repair-only. Validators prove geometry
and file facts, not artistic success. Never overwrite an existing final unless
the request permits it.

Accept completion only when the terminal manifest parses, every image call has
an artifact or exact failure, controls are accounted for, the selected delivery
exists and validates, criteria have evidence, usage is recorded, the claim is
in its matching terminal directory, and the worker is stopped or explicitly on
another job. Report status, selected path, iterations used/max, unresolved or
subjective criteria, each usage percentage with its Pacific reset datetime,
event log, and manifest—never merely a process exit code.

## Legacy fallback

Use `scripts/codex_image.py` one-shot only when explicitly requested. Then read
`references/codex-contract.md`. Its old transparency limitation is stale.
Known hazards: timeout can follow a completed generation; repeated `-i` needs
`--` before the prompt; shared `CODEX_HOME` workers can interfere; Windows
cannot read WSL-only paths; generated dimensions are not guaranteed. Prefer the
persistent app-server worker and queue.
