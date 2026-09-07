<!-- status: PROPOSAL, authored by CODEX (a different AI, not Claude), 2026-09-06.
     NOT ruled, NOT validated, NOT implemented (its own "Status:" line below
     says the executable controller does not exist yet). The owner asked for
     this pushed with rich annotation for deep introspection before anyone
     treats it as a plan. Renamed from CLAUDE_CODEX_GRAPHICS_WORKFLOW.md to
     CODEX_PROPOSAL_GRAPHICS_WORKFLOW.md. Companion: CODEX_PROPOSAL_ART_WORKER.md
     (the worker contract this doc assumes) and
     CODEX_PROPOSAL_GENERATING_IMAGES_SKILL_DRAFT.md (the skill rewrite CODEX
     drafted alongside this -- REVERTED from the live
     skills/generating-images/SKILL.md, which still runs the original working
     one-shot pipeline unchanged, per "do not harm the current CODEX pipeline,
     since it works," owner, 2026-09-06). -->

# Claude Code ↔ Codex Graphics Workflow — Complete Handoff (PROPOSAL, unvalidated)

Status: design complete; worker/controller specifications written; executable
controller not yet implemented. Last consolidated: 2026-09-06.

This document records the complete outcome of the design conversation and the
additional information Claude Code needs to invoke Codex efficiently. It is a
decision record and implementation handoff, not a verbatim transcript.

## The essential answer

Claude Code should own the Codex worker lifecycle. The user should normally ask
Claude for a graphic; Claude should publish a queue request, start or resume a
local Codex thread through a thin controller, steer or interrupt it when needed,
read its manifest, and shut it down.

A Codex desktop conversation is not a background listener. Starting a task in
the desktop app does not create an endpoint that Claude can later reach merely
by writing a file. File controls are observed only while a Codex turn is active
and checking them. Therefore:

- the recommended path is a Claude-owned Codex SDK/app-server controller;
- the manual path is Claude queues first, then the user starts a Codex task for
  that exact job ID;
- a persistent unattended worker must be an explicit controller process, not a
  chat left open in the desktop app;
- never poll or claim unrelated queue work automatically.

## Existing project state

The following files now exist:

- `infrastructure/agents/CODEX_ART_WORKER.md` — canonical Codex worker role,
  request/control/log/artifact/manifest contract, and recovery policy.
- `skills/generating-images/SKILL.md` — token-efficient Claude controller skill.
- `.claude/skills/generating-images` — existing Claude skill wiring/reparse
  directory for the skill above.
- `infrastructure/agents/CLAUDE_CODEX_GRAPHICS_WORKFLOW.md` — this handoff.

The canonical machine-local queue is intended to be:

```text
Windows: C:\Users\Mandrake\AppData\Local\RimworldCodexArtQueue
WSL:     /mnt/c/Users/Mandrake/AppData/Local/RimworldCodexArtQueue
```

Respect `RIMWORLD_CODEX_ART_QUEUE` when set. At the time of this handoff, the
default queue does not exist and no job has been claimed or processed.

There is currently no implementation using `openai-codex`,
`@openai/codex-sdk`, or `codex app-server` in this repository. The existing
`skills/generating-images/scripts/codex_image.py` is a legacy one-shot wrapper,
not the persistent controller described here.

## Why this workflow exists

The project previously had Claude prepare examples and prompts, call Codex in
one-shot CLI mode, then inspect results back in Claude. The desired improvement
is a durable graphics worker that can:

- accept a text-only request or text plus exemplar images;
- let Codex produce the actual image-model prompt;
- preserve, inspect, and score every returned image;
- self-iterate only when a concrete improvement is available;
- obey a request-specific maximum image-iteration count;
- accept live feedback such as “stop and shut down” or “the subject is only
  half as large as requested”;
- log every material action for an external monitor;
- distinguish intermediate, selected, and delivered images;
- survive controller disconnection and ambiguous timeouts;
- expose usage and reset information without inventing an image count;
- support safe parallelism across independent asset families.

Nothing in this workflow authorizes BENCH, FOUNDRY, RimFlow, or another agent
queue. The Codex art worker processes only explicitly named graphics job IDs.
It must not scan for work, pull automatic items, or modify unrelated project
files.

## Architecture

```text
User
  │ asks for graphic / gives feedback
  ▼
Claude Code + generating-images skill
  ├─ writes immutable request and controls ──► durable file queue
  ├─ starts/steers/stops ────────────────────► Codex controller
  └─ reads manifest/artifacts ◄─────────────── durable file queue
                                                  ▲
                                                  │ logs/results
                                          Codex graphics thread
                                          + image-generation skill
```

Use two communication planes:

1. Live control: Codex SDK or app-server over local stdio. This supplies thread
   creation/resume, streaming events, steering, interruption, and account-limit
   reads.
2. Durable data: the filesystem queue. This supplies immutable requests,
   sequenced controls, append-only logs, images, evaluations, and manifests.

The official Codex SDK is the preferred automation wrapper. The Python SDK
controls a local app-server over JSON-RPC; the TypeScript SDK can start,
continue, and resume local Codex threads. Direct app-server use is appropriate
for the richer custom-client features required here. References:

- https://learn.chatgpt.com/docs/codex-sdk
- https://learn.chatgpt.com/docs/app-server
- https://learn.chatgpt.com/docs/image-generation
- https://learn.chatgpt.com/docs/pricing

## Ownership

Claude owns:

- interpreting project/canon context;
- the visible goal, intended use, measurable delivery requirements, and maximum
  iterations;
- verifying and labelling reference files;
- atomically publishing immutable requests;
- scheduling and concurrency from live usage;
- starting, resuming, steering, interrupting, and stopping workers;
- owner feedback and any final selection assigned to Claude/the owner;
- reading the terminal manifest and evaluating the finished work.

Codex owns:

- the final image-generation/edit prompt;
- interpreting references according to declared roles;
- calling built-in image generation/editing;
- preserving every returned artifact;
- visual inspection and deterministic validation;
- one targeted improvement per permitted retry;
- final conformance, delivery, append-only events, and terminal manifest.

The controller owns transport; it must not dictate art through shell flags. The
worker owns rendering decisions; it must not expand scope or iteration budget.

## Correct normal invocation after the controller exists

The user should ask Claude naturally or invoke the project skill if available:

```text
/generating-images

Create a north-facing Jawa worktable sprite.
References: <absolute paths or none>
Output: <absolute Windows path>
Transparent PNG, 512×512.
Maximum 4 image iterations.
Let Codex select the best passing result.
```

Claude then performs this sequence without asking the user to open Codex:

1. Validate the goal, references, output path, acceptance criteria, and budget.
2. Read live Codex usage.
3. Atomically publish `requests/pending/<job_id>.json`.
4. Start the local controller, or connect to its existing initialized process.
5. Start a fresh Codex thread for an independent asset family, or resume the
   thread assigned to the same identity-sensitive family.
6. Send only the queue root and job ID. Do not paste the full request into chat.
7. Stream status and tool events; persist thread and turn IDs.
8. Send feedback as a small sequenced control plus `turn/steer` when active.
9. Send urgent stop with `turn/interrupt`, then checkpoint if needed.
10. Read the terminal manifest and artifacts, report the outcome, and stop or
    archive the worker as policy requires.

## Missing executable controller

Claude needs to implement one thin local program. A reasonable project command
surface is:

```text
codex-art run <JOB_ID>
codex-art status <JOB_ID>
codex-art steer <JOB_ID> <CONTROL_JSON>
codex-art stop <JOB_ID>
codex-art usage
```

Names are not sacred, but the semantics are. The controller should:

- use Python 3.10+ `openai-codex` unless repository conventions strongly favor
  the TypeScript SDK;
- use the SDK-pinned runtime by default; specify a local Codex binary only when
  deliberately testing that binary;
- use app-server stdio/JSONL, not WebSocket, unless a separate requirement
  justifies the experimental WebSocket transport;
- initialize once per process with a clear `clientInfo.name`, then reuse the
  process;
- keep stderr separate from JSONL stdout;
- persist worker ID, process identity, thread ID, turn ID, job ID, last event
  sequence, and timestamps;
- kill only a verified process ID owned by the controller, never all processes
  matching “codex”;
- use saved Codex/ChatGPT authentication; do not request an API key for the
  signed-in-account path;
- use `workspaceWrite` with only the queue and declared delivery parents
  writable; the repository and external references may be read-only;
- never use full-access or approval-bypass flags automatically;
- feature-detect methods against the installed SDK/app-server version;
- preserve exact JSON-RPC and provider errors in logs.

Core app-server lifecycle:

```text
start process: codex app-server              # stdio is the default transport
initialize → initialized                     # exactly once per connection
account/rateLimits/read                      # before batch, after each job
skills/list                                  # worker bootstrap, not each job
thread/start                                 # clean independent context
thread/resume                                # same asset-family context
turn/start                                   # process queue job
turn/steer                                   # live correction, expectedTurnId
turn/interrupt                               # urgent stop
thread/compact/start                         # preserve same-family context compactly
thread/archive                               # optional after durable completion
```

Include `$imagegen` and the resolved image-generation skill input item on the
worker's initial image turn when supported. Do not guess a cached system-skill
path; resolve it during bootstrap.

## Context lifecycle and token efficiency

Claude can functionally “clear Codex context” by starting a new thread. A text
message saying “forget everything” does not erase history. Use:

- `thread/start` for a genuinely independent job/family;
- `thread/resume` for another turn on the same job or closely related family;
- `thread/compact/start` when same-family history remains useful but has grown;
- not `thread/fork` for clearing, because a fork copies history.

Starting a new thread clears conversation history but does not reset the
account's five-hour or weekly usage windows.

Token-efficient rules:

- keep specifications, images, logs, and recovery state in files;
- pass paths and hashes, never base64 images;
- read `CODEX_ART_WORKER.md` once per worker thread, not once per image call;
- send job IDs and control deltas, not repeated protocol prose;
- use low main-model reasoning for ordinary dispatch/rendering;
- use medium only for difficult visual comparison/reference reconciliation;
- tail logs from the last sequence; never reread them from the beginning;
- do not repeat human status while state is unchanged;
- let Codex review intermediates; Claude opens them only when selection or an
  unresolved judgment requires it;
- group identity-sensitive variants in one thread, but do not carry unrelated
  visual history into a new family;
- do not research account pricing during routine usage polling;
- do repeat identity/edit invariants in image-edit prompts: that token cost is
  necessary for fidelity.

The Claude skill was reduced during this design from roughly 3,995 words to
about 1,610 words. The full worker contract is deliberately cold-path material.

## Manual handshake before the controller exists

The order is Claude first, Codex second. Do not start a desktop worker and leave
it waiting.

Ask Claude:

```text
Use the existing project skill `generating-images`.

For this first manual handshake, do not call the legacy `codex_image.py`
generation wrapper and do not attempt to start Codex.

Create the canonical Codex art queue directories and publish one valid request:

Goal: <describe the image>
References: <absolute paths, or none>
Output: <absolute Windows output path>
Maximum image iterations: 1
Selection authority: Codex worker

Return the job ID and exact pending-request path.
```

After Claude confirms that
`C:\Users\Mandrake\AppData\Local\RimworldCodexArtQueue\requests\pending\<JOB_ID>.json`
exists, create a fresh Codex task in the existing Rimworld project, using the
same local checkout rather than a new project/worktree, and send:

```text
Assume D:\Luke\dev\Rimworld\infrastructure\agents\CODEX_ART_WORKER.md.

This is an explicitly authorized manual graphics-worker run.
Worker ID: codex-art-manual-01
Queue root: C:\Users\Mandrake\AppData\Local\RimworldCodexArtQueue
Process only job <JOB_ID>.
Maximum jobs this run: 1.
Do not claim any other queued job.
Exit when this job reaches a terminal state.
```

When the Codex task finishes, ask Claude:

```text
Evaluate Codex art job <JOB_ID>. Read its terminal manifest, event log,
evaluations, intermediates, and selected output. Report whether the original
acceptance criteria passed.
```

This manual bridge validates the durable queue. It does not prove automated
start/steer/stop; that requires the controller.

## Queue and claim protocol

```text
<queue>/
  requests/
    pending/<job_id>.json
    claimed/<job_id>.<worker_id>.json
    accepted/<job_id>.json
    needs_review/<job_id>.json
    needs_control/<job_id>.json
    failed/<job_id>.json
    refused/<job_id>.json
    stopped/<job_id>.json
  jobs/<job_id>/
    events.jsonl
    controls/inbox/<sequence>.json
    controls/processed/<sequence>.json
    artifacts/iteration-NNN/
      source_intermediate.<ext>
      preview_intermediate.png
      delivery_intermediate.png
      evaluation.json
    manifest.json
  workers/<worker_id>/
    state.json
    usage.jsonl
```

Publish requests through a flushed temporary sibling followed by atomic rename.
Claim by atomic rename from `pending` to `claimed`. Never edit a published or
claimed request. A resumed job keeps the original request, event sequence, and
iteration count. Never clean/truncate another job's directory.

The worker processes only job IDs supplied by the owner/controller. It is not a
watcher daemon and must have a positive `max_jobs_this_run`.

## Request API

The canonical full schema is in `CODEX_ART_WORKER.md`; the hot-path compact form
is in `skills/generating-images/SKILL.md`. A request must at least establish:

```json
{
  "protocol": "rimworld.codex-art/v1",
  "job_id": "ASSET_FAMILY_VARIANT_001",
  "created_at": "<ISO-8601 with offset>",
  "created_by": "claude-code",
  "mode": "generate",
  "goal": "<visible result and intended use>",
  "intended_use": "<consumer and viewing scale>",
  "references": [],
  "visual_spec": {
    "subject": "<what is depicted>",
    "view": "<camera/facing>",
    "composition": "<framing and subject footprint>",
    "style_medium": "<visual language>",
    "palette": "<palette>",
    "desired_state": [],
    "avoid": []
  },
  "invariants": [],
  "generation": {
    "background": {"kind": "transparent"},
    "target_aspect_ratio": "1:1",
    "self_iterate": true,
    "max_iterations": 4,
    "selection_authority": "worker",
    "preserve_all_iterations": true
  },
  "delivery": {
    "outputs": [{
      "path": "<absolute Windows path>",
      "width": 512,
      "height": 512,
      "format": "png",
      "alpha": "required"
    }],
    "subject_footprint": {
      "min_canvas_fraction": 0.45,
      "max_canvas_fraction": 0.82
    },
    "overwrite": false
  },
  "acceptance": [{
    "id": "primary_read",
    "kind": "visual",
    "severity": "must",
    "criterion": "<observable pass condition>"
  }],
  "authority": {
    "may_normalize_prompt": true,
    "may_add_unrequested_subjects": false,
    "may_change_references": false,
    "may_use_chroma_fallback": false,
    "requires_human_acceptance": false
  }
}
```

For text-only work, `references` is empty. For exemplars, each reference has an
absolute Windows path, optional/required hash, one primary role, explicit details
to transfer, details to avoid, and priority. Roles are `identity`, `edit_target`,
`style`, `composition`, `palette`, `silhouette`, and `avoid`. An edit has exactly
one `edit_target`.

Useful directives describe the visible goal. Improper directives prescribe
transport implementation (“run this flag,” “copy the newest generated file,”
“retry forever”) or confuse delivery dimensions with the model's internal
canvas. Put hard facts in invariants, measurable outcomes in `delivery`, and
observable judgments in acceptance criteria.

Default image-call ceilings are four for new art, three for constrained edits,
and one for plumbing/human-led tests. Every submitted image generation/edit call
counts, including a refused or outcome-ambiguous call. Stop early when the goal
is met. Never silently increase the ceiling.

## Live controls

Controls are sequenced and immutable. Supported commands:

- `feedback` — one observable correction; preserve named invariants;
- `amend` — overlay a structured request patch without editing the original;
- `set_max_iterations` — change the absolute ceiling; only authorized owner or
  controller may increase it;
- `pause` / `resume` — checkpoint without a new image call / continue;
- `status` — return a concise checkpoint with no image iteration;
- `report_next_tier` — run the on-demand plan-report skill with no image
  iteration;
- `accept` / `reject` — select or reject a preserved iteration;
- `stop` — start no new call, preserve returned work, checkpoint, and exit.

Human language is valid. Log both the original message and normalized meaning.
“The subject is half as large as requested” normally amends subject footprint,
not PNG dimensions. Ask one targeted question if the meaning is genuinely
ambiguous.

For active turns, write the durable control and use `turn/steer` with the current
`expectedTurnId`. For urgent stop, use `turn/interrupt`; a file alone cannot
interrupt an image tool already running. If interruption prevents the turn from
writing its checkpoint, run one checkpoint-only recovery turn that may harvest
an already returned image but may not generate another.

## Logging and monitoring

`jobs/<job_id>/events.jsonl` is authoritative. Append one compact UTF-8 JSON
object per line, flush it, and never rewrite/truncate. Log before and after every
material action: claim, usage read, validation, reference inspection, prompt
decision, generation dispatch/return, copy, evaluation, validation, control,
selection, delivery, manifest, transition, and shutdown.

Each event includes protocol, monotonic sequence, timestamp, worker/job,
iteration, event, phase, status, short message, paths, metrics, and exact error.
Never place base64 images, full request bodies, entire transcripts, or repeated
policy prose in events.

Update `workers/<worker_id>/state.json` at startup, before/after long image calls,
and shutdown. External monitors tail by sequence and speak only on change.

Every image is preserved. Each iteration has raw source, preview, conformed
candidate, and evaluation. Intermediates are labelled `intermediate`; only a
selected validated candidate is copied to the declared final output.

## Visual review and delivery

Codex inspects actual pixels after every image call. It checks:

- primary visible read at intended display size;
- every required reference detail;
- composition, facing, silhouette, palette, materials, and subject footprint;
- edit/identity invariants;
- exact text when requested;
- alpha on checkerboard plus deterministic alpha measurements;
- final dimensions and overwrite behavior;
- failed criterion and one proposed targeted change.

Native transparency is preferred. Chroma-key removal is repair-only and requires
explicit authority. Built-in generation size is not a delivery guarantee;
preserve raw output and conform deterministically. Do not spend a new image call
merely to chase exact pixel dimensions.

Relevant deterministic tools include:

- `skills/generating-rimworld-sprites/scripts/conform_sprite.py`
- `skills/generating-rimworld-sprites/scripts/validate_sprite.py`
- `skills/generating-images/scripts/preview_alpha.py`
- `skills/editing-images/scripts/compare_images.py`

Validators prove file/geometry facts, not artistic taste. Claude or the owner
still reviews subjective acceptance when assigned that authority.

## Usage, reset times, and scheduling

Before each batch and after each completed job, call
`account/rateLimits/read`. Prefer `rateLimitsByLimitId.codex`, falling back to
`rateLimits`. `usedPercent` means consumed percentage; remaining is
`100-usedPercent`. `resetsAt` is Unix seconds. Null means unknown, never zero.

The account interface does not expose a reliable number of “images remaining.”
Do not convert percentages into a promised image count. Image generation shares
general Codex usage and can also be independently throttled.

For every returned usage window, logs preserve Unix, UTC, and Pacific-local reset
time. Human reports always include the full Pacific date/time and the correct
seasonal suffix, `PST` or `PDT`. Use `America/Los_Angeles`; do not label a
daylight-saving timestamp `PST` merely because the owner used “PST” generically.

Scheduler policy, using the most restrictive matching row:

| Signal | Policy |
|---|---|
| Both windows under 70%, no throttle | Up to 4 calibrated independent workers |
| Weekly 70–79% | At most 2; no unbounded overnight batch |
| Weekly 80–89% or primary 70–89% | Warn once; at most 1; new jobs max 2 iterations |
| Weekly ≥90% or primary ≥90% | No new image calls; checkpoint and wait |
| Weekly ≥97% | Preserve returned work and stop the pool |
| Rate/usage-limit error | Stop global dispatch; do not probe with another image |
| Unknown limit field | At most 1 until clarified |

Parallelize independent families only. Multiple facings or identity-sensitive
variants should remain in one thread unless each worker receives the identical
identity pack and invariants. No two workers may write the same output path.

Reset credits are owner-controlled. Report their count but never redeem one
without explicit authorization and an idempotency key.

### Historical observations from this conversation

These are evidence, not configuration, and are stale immediately:

- First 2026-09-06 read: Plus; five-hour window 30% used; weekly 75% used.
- Later 2026-09-06 read: Plus; five-hour 53% used / 47% remaining, resetting
  2026-09-06 6:16:24 PM PDT; weekly 78% used / 22% remaining, resetting
  2026-09-06 8:05:28 PM PDT.
- Purchased credits were absent with balance 0; three earned full-reset credits
  were available; `individualLimit` was null and spend control was not reached.
- One past project burst appeared to consume roughly 0.3 primary-window
  percentage point per image. This is not a quota formula.

Always replace these figures with a live read.

## On-demand next-tier report

Routine usage polling must not research or explain pricing. When weekly usage is
at least 75%, either window is at least 80%, or a usage/rate-limit error occurs,
set only `next_tier_report_recommended: true`.

Only explicit owner text or `report_next_tier` invokes the OpenAI product-docs
skill. That bounded request must refresh usage, verify current plan names,
prices, and allowances from official OpenAI sources, distinguish allowance from
image count/latency/throughput/concurrency/throttling, append one
`upgrade_report` with source URLs and `checked_at`, then stop. It consumes no
image iteration and must not repeat per poll or queued job.

During this conversation, official documentation reported Plus at $20/month,
Pro $100 at 5× Plus Codex usage, and Pro $200 at 20×. Those values were supplied
to the owner once, then deliberately removed as runtime constants. They must be
verified on demand, not repeated from this document as current pricing.

## Error interpretation

| Signal | Required action |
|---|---|
| `UsageLimitExceeded`, `TooManyRequests`, HTTP 429, image rate-limited | Stop dispatch; log live usage/reset; do not probe or redeem a reset |
| `ContextWindowExceeded` | Checkpoint bounded state; fresh thread; no image iteration to rebuild context |
| Stream disconnect or outer process timeout | Outcome unknown; reconnect and inspect events/artifacts before retry |
| HTTP 5xx / `InternalServerError` | Harvest completed artifacts; otherwise one delayed retry if limits/budget allow |
| HTTP 400 / `BadRequest` | Correct one exact mechanical payload defect; otherwise `needs_control` |
| 401/403 / `Unauthorized` | Stop and request restored Codex authentication |
| `ResponseTooManyFailedAttempts` | Stop job; no immediate outer retry loop |
| `SandboxError` | Correct path/declared roots; never broaden permissions automatically |
| Moderation/refusal | Preserve exact refusal; retry once only for harmless clarification |
| `turn/completed: interrupted` | Treat as stopped; harvest anything returned before interruption |
| Successful turn with no output | Search tool events/artifacts before another generation |
| Wrong generated dimensions | Preserve raw and conform; regenerate only for content/composition |
| Opaque result for transparent request | One targeted edit if budget remains; chroma only if authorized |
| No events plus stale worker state | Verify recorded process/thread ID; never kill by name/pattern |

The old one-shot wrapper has known hazards: it may time out after an image was
generated, may raise before its harvest path, repeated `-i` consumes following
arguments unless `--` separates the prompt, shared `CODEX_HOME` workers may
interfere, Windows Codex cannot read WSL-only paths, and generated dimensions
are not guaranteed. A process exit code is never the art verdict.

## Controller implementation checklist for Claude

Claude should read this document, `CODEX_ART_WORKER.md`, and the existing
`generating-images` skill once, then implement—not redesign—the missing bridge.

Required deliverables:

1. A thin controller executable/library with run, status, steer, stop, and usage
   operations.
2. SDK/app-server initialization and version/capability checks.
3. Persistent controller/worker state with exact process, thread, and turn IDs.
4. Atomic queue publish/claim/control helpers.
5. Structured event streaming and exact error preservation.
6. Fresh-thread/resume/compact policy by asset-family identity.
7. Usage scheduler and Pacific reset-time rendering.
8. Safe interruption plus checkpoint-only recovery.
9. Tests using a fake app-server/event stream; no real image generation in
   ordinary tests.
10. One explicitly authorized one-iteration real smoke test only after dry tests
    pass.

Do not automatically install dependencies, spend image quota, consume reset
credits, start queue jobs, or rewrite the two canonical contracts merely while
reviewing this handoff. Ask the owner before the real smoke test.

## Definition of done

The integration is complete when the owner can ask Claude for a graphic and
Claude can, without manual Codex UI steps:

- create a valid bounded request;
- start a clean or appropriate resumed Codex worker;
- observe and log progress;
- deliver live feedback and urgent stop;
- preserve all artifacts and ambiguous outcomes;
- receive a valid terminal manifest;
- inspect/select the result according to declared authority;
- report usage with Pacific reset datetimes;
- stop/archive the worker cleanly;
- leave unrelated project and queue work untouched.

Until the controller is implemented, use the manual handshake above.

## Conversation decision record

The design evolved through these decisions:

1. Codex first inspected the Claude-oriented project in read-only mode and was
   explicitly forbidden from taking automatic items or changing files.
2. The existing Claude→one-shot-Codex image workflow was evaluated. Durable
   queues and persistent control were judged better for recovery, iteration,
   monitoring, and limited safe parallelism.
3. The owner authorized exactly two initial files: a Codex receiving-agent
   contract and a Claude skill. Those became `CODEX_ART_WORKER.md` and
   `skills/generating-images/SKILL.md`.
4. The protocol was designed for text or text-plus-references, bounded
   self-iteration, intermediate preservation, live feedback, shutdown, and an
   external append-only monitor log.
5. Account usage reporting was added. Exact image-count promises were rejected
   because the account interface exposes shared percentages rather than an
   image-specific maximum.
6. Upgrade pricing was initially included in every near-limit report, then
   corrected: it is now an explicit on-demand skill request to avoid recurring
   token cost and stale constants.
7. The Claude skill was compressed substantially. Full protocol text became
   cold-path documentation; ordinary dispatch uses compact file contracts and
   job IDs.
8. Reset reports were required to show full Pacific date/time with correct
   `PST`/`PDT` daylight rules.
9. It was clarified that a fresh Codex thread, not a new project and not a
   “forget” message, is the reliable way to clear unrelated context. Compaction
   preserves a summary and is appropriate only when related context remains
   useful.
10. It was clarified that a desktop Codex task is not a listener Claude can
    reach later. The missing controller must own start/resume/steer/interrupt/
    shutdown. The manual sequence remains Claude queues first, user starts the
    exact Codex job second.
