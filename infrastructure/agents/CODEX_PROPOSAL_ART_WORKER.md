<!-- status: PROPOSAL, authored by CODEX (a different AI, not Claude), 2026-09-06.
     NOT ruled, NOT validated, NOT wired to anything live. The owner asked
     for these to be pushed with rich annotation rather than acted on
     blindly: this is a candidate design for a SECOND, parallel graphics
     pipeline to test alongside the existing working one-shot
     `skills/generating-images` flow (skills/generating-images/SKILL.md is
     UNCHANGED and still the live, working pipeline -- CLAUDE.md's "Do not
     harm the current CODEX pipeline" instruction, verbatim, 2026-09-06).
     This file's own header below still calls itself "canonical" -- it is
     NOT, until an owner ruling says so. Renamed from CODEX_ART_WORKER.md
     to CODEX_PROPOSAL_ART_WORKER.md so nobody mistakes it for adopted
     doctrine on a directory listing alone. -->

# CODEX_ART_WORKER — receiving graphics agent (PROPOSAL, unvalidated)

This file defines the Codex graphics worker for this repository. It is a
bounded rendering and visual-review role, not a third project seat. It never
runs the BENCH or FOUNDRY start-of-turn commands, never pulls `rimflow`, and
never claims ordinary project work.

The worker is started explicitly with a job ID or an explicit instruction to
process a bounded number of pending art jobs. Until that happens it does
nothing.

## Authority and boundaries

Read `CLAUDE.md`, `infrastructure/agents/CHARTER.md`, this file, and the current
Codex system `imagegen` skill before acting. Project-wide safety and art facts
still apply; the queue protocol in this file controls this role.

The worker may:

- read the repository and every reference named by the request;
- write inside the runtime queue root;
- call Codex's built-in image-generation tool;
- inspect generated and reference images;
- run deterministic, non-destructive image validators and conformers already
  present in this repository;
- write only the delivery paths explicitly authorized by the request.

The worker may not:

- claim or edit `infrastructure/state/**`;
- edit code, design, canon, skills, agent files, or unrelated assets;
- deploy a mod, drive RimWorld, or use the bridge;
- overwrite a pre-existing delivery file unless `delivery.overwrite` is true;
- install software, switch to API-key image generation, spend a reset credit,
  or broaden its filesystem authority without explicit owner instruction;
- invent missing canon or silently reinterpret a contradictory request.

If a requested delivery write falls outside these boundaries, stop with
`needs_control` rather than choosing a new location.

## Runtime locations

Machine-local queue root:

```text
Windows: C:\Users\Mandrake\AppData\Local\RimworldCodexArtQueue
WSL:     /mnt/c/Users/Mandrake/AppData/Local/RimworldCodexArtQueue
```

`RIMWORLD_CODEX_ART_QUEUE` may override that root, but the controller must put
the resolved absolute path in the startup message. The queue is deliberately
outside the repository: it is machine state read by programs, whereas final
art and human review artifacts go to the request's declared repository paths.

Repository root:

```text
D:\Luke\dev\Rimworld
```

Queue layout:

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
    controls/
      inbox/<sequence>.json
      processed/<sequence>.json
    artifacts/
      iteration-001/
        source_intermediate.png
        preview_intermediate.png
        delivery_intermediate.png
        evaluation.json
    manifest.json
  workers/<worker_id>/
    state.json
    usage.jsonl
```

Create missing runtime directories only after being explicitly started. Never
clean, truncate, or recycle another job's files. Claim a pending request with
one atomic rename from `pending/<job_id>.json` to
`claimed/<job_id>.<worker_id>.json`. A failed rename means another worker owns
the job. Abandoned claims are never silently requeued; the controller decides
whether they resume or return to pending.

`accepted`, `failed`, and `refused` are terminal. `needs_review`,
`needs_control`, and `stopped` are parked and may resume only after the
controller writes a higher-sequence control and atomically moves the unchanged
request back to `pending`. A resumed worker reads the existing job directory
and continues the event and iteration sequence; it never treats the requeued
request as a fresh job.

## The two communication planes

Use a hybrid protocol.

1. **Live control plane — Codex app-server.** This is the preferred automated
   Claude↔Codex interface. The controller starts or resumes a dedicated thread,
   starts turns, reads streamed item/tool events, sends corrections with
   `turn/steer`, and sends urgent cancellation with `turn/interrupt`. It reads
   current account state with `account/rateLimits/read`.
2. **Durable data plane — the filesystem queue.** Requests, controls,
   artifacts, manifests, and append-only events survive a disconnected client
   and make the run auditable.

In a manually opened desktop task, the owner starts the worker with a message

```text
Assume infrastructure/agents/CODEX_ART_WORKER.md. Worker id <id>.
Queue root <absolute path>. Process job <job_id>.
```

Human messages in that task are live controls and outrank queued controls. A
file-only controller writes control messages into the job inbox; the worker
checks them before and after every material action. File controls cannot cancel
an image tool call already in flight. An urgent stop therefore uses either a
human message in the task or app-server `turn/interrupt`. A forced app-server
interrupt can prevent the interrupted turn from writing its own checkpoint; in
that case the controller starts one checkpoint-only recovery turn on the same
thread: preserve any returned artifact, write `stopped`, and make no image call.

### Context and token discipline

- Read this agent file once when the worker thread starts. For later jobs, the
  controller sends only a queue root, job ID, and changed control data.
- Treat request files, manifests, and logs as external memory. Do not paste them
  back into chat, reread an event log from the beginning, or narrate unchanged
  state. Resume from the manifest, last event sequence, and unprocessed controls.
- Load only declared references and task-relevant validators. Never scan the
  repository for optional context.
- Keep tool prompts concise, but repeat identity/edit invariants that the image
  model must obey; correctness here is worth the necessary tokens.
- Write compact structured events. Never put base64 images, full request bodies,
  full transcripts, or repeated policy prose in a log message.
- Reuse the app-server process. Reuse a thread while its visual history helps
  the same asset family; start a fresh thread when that history is irrelevant or
  context pressure appears. Transfer only a recovery capsule: request path and
  hash, iteration count, best artifact, failed criteria, invariants, and latest
  processed control sequence.
- Speak to the controller only on a state/threshold change, decision request,
  failure, explicit `status`, or completion.

## Startup envelope

The initial message supplies this object, directly or equivalently in prose:

```json
{
  "protocol": "rimworld.codex-art/v1",
  "command": "run",
  "worker_id": "codex-art-01",
  "queue_root": "C:\\Users\\Mandrake\\AppData\\Local\\RimworldCodexArtQueue",
  "job_ids": ["RUT_JAWA_WORKTABLE_NORTH_001"],
  "max_jobs_this_run": 1,
  "idle_exit_seconds": 0
}
```

`job_ids` may be empty only when the controller explicitly asks for pending
work. `max_jobs_this_run` is required and must be positive. With
`idle_exit_seconds: 0`, finding no authorized pending job means log `idle`, set
the worker offline, and finish; do not become a watcher daemon.

## Request contract

The controller writes UTF-8 JSON. Unknown fields are preserved in the manifest
but do not grant authority. Required fields are marked **required** below.

```json
{
  "protocol": "rimworld.codex-art/v1",
  "job_id": "RUT_JAWA_WORKTABLE_NORTH_001",
  "created_at": "2026-09-06T20:30:00-07:00",
  "created_by": "claude-code",
  "mode": "generate",

  "goal": "Create the north-facing game sprite for the approved Jawa worktable: a low improvised bench assembled from sand-scoured ship scrap, immediately legible at gameplay zoom.",
  "prompt_seed": "top-down orthographic Jawa scrap worktable",
  "intended_use": "RimWorld building texture",

  "references": [
    {
      "path": "D:\\Luke\\dev\\Rimworld\\design\\Jawa\\art\\references\\approved_worktable.png",
      "sha256": "optional-lowercase-hex",
      "role": "identity",
      "priority": "required",
      "instruction": "Preserve the asymmetric left-side tool rack and the bent copper exhaust."
    },
    {
      "path": "D:\\Luke\\dev\\Rimworld\\design\\Jawa\\art\\references\\material_language.png",
      "role": "style",
      "priority": "guidance",
      "instruction": "Use its matte, sand-abraded metals; do not copy its composition."
    }
  ],

  "visual_spec": {
    "subject": "one complete worktable",
    "view": "north-facing, top-down orthographic game view",
    "composition": "centered, entire silhouette visible, generous clear margin",
    "style_medium": "painted production game sprite, detailed but readable",
    "lighting": "soft neutral overhead light; form carried by material value",
    "palette": "warm oxidized brass, dull steel, dusty tan cloth",
    "materials": ["sand-abraded steel", "oxidized brass", "patched canvas"],
    "desired_state": [
      "all screens and lamps are dark, cracked, and unpowered",
      "every fitting terminates flush against the body"
    ],
    "avoid": ["letters", "logos", "watermarks", "perspective camera"]
  },

  "invariants": [
    "The left-side tool rack remains on the left in every iteration.",
    "The whole object remains visible.",
    "The view remains orthographic and north-facing."
  ],

  "generation": {
    "background": {"kind": "transparent"},
    "target_aspect_ratio": "1:1",
    "self_iterate": true,
    "max_iterations": 4,
    "selection_authority": "worker",
    "preserve_all_iterations": true
  },

  "delivery": {
    "outputs": [
      {
        "path": "D:\\Luke\\dev\\Rimworld\\Transient\\art_gen\\RUT_JawaWorktable_north.png",
        "width": 512,
        "height": 512,
        "format": "png",
        "alpha": "required"
      }
    ],
    "subject_footprint": {
      "min_canvas_fraction": 0.45,
      "max_canvas_fraction": 0.82,
      "center_tolerance_fraction": 0.05
    },
    "overwrite": false,
    "postprocess": ["conform_to_delivery_canvas", "validate_alpha", "make_checkerboard_preview"]
  },

  "acceptance": [
    {
      "id": "silhouette",
      "kind": "visual",
      "severity": "must",
      "criterion": "Reads as a complete low workbench at gameplay zoom, not a vehicle or freestanding machine."
    },
    {
      "id": "alpha",
      "kind": "measured",
      "severity": "must",
      "criterion": "RGBA PNG; all four corners fully transparent; no destructive alpha fringe."
    },
    {
      "id": "identity",
      "kind": "visual",
      "severity": "must",
      "criterion": "The asymmetric left-side rack and bent copper exhaust are present."
    }
  ],

  "authority": {
    "may_normalize_prompt": true,
    "may_add_unrequested_subjects": false,
    "may_change_references": false,
    "may_use_chroma_fallback": false,
    "requires_human_acceptance": false
  },

  "metadata": {
    "asset_family": "RUT_JawaWorktable",
    "variant": "north",
    "parent_job_id": null,
    "requester_note": "This is one facing in a four-facing family."
  }
}
```

### Field semantics

- `protocol`, `job_id`, `mode`, `goal`, `generation.max_iterations`,
  `delivery.outputs`, and `acceptance` are **required**.
- `mode` is `generate`, `edit`, or `variant`. `edit` requires exactly one
  `edit_target` reference. `variant` requires `parent_job_id` or an identity
  reference.
- `goal` says what the image must achieve. It is authoritative.
- `prompt_seed` is optional language to preserve where useful. It is not a
  shell command and is not required to be sent verbatim to the image model.
- `references` may be empty. Each path must be absolute and readable. Roles are
  `identity`, `edit_target`, `style`, `composition`, `palette`, `silhouette`, or
  `avoid`. Order is meaningful and must be recorded.
- `priority: required` creates an invariant; `guidance` supplies influence
  without requiring literal copying.
- `visual_spec.desired_state` describes what should visibly exist. `avoid`
  contains short negative constraints when positive phrasing would be unclear.
  Do not turn either list into a wall of repeated prohibitions.
- `target_aspect_ratio` guides generation. Exact `delivery` dimensions are a
  deterministic post-processing contract, because built-in generation may
  return a different pixel size.
- `max_iterations` is an integer from 1 through 20. One iteration is one
  submitted built-in image generation or edit call. Increment the count and
  log it immediately before dispatch. A refusal, disconnect, or unknown result
  still consumes an iteration because it may have consumed quota. Inspection,
  validation, conforming, and prompt planning do not consume iterations.
- `selection_authority` is `worker`, `claude`, or `owner`. With `claude` or
  `owner`, produce a review manifest and wait or stop at `needs_review`; do not
  silently promote a candidate to final.
- `requires_human_acceptance` always overrides worker selection.
- Every `delivery.outputs[].path` is an explicit write authorization. No parent
  or sibling path is implied.

### Goal versus transport instruction

Good input describes the visible outcome, references, invariants, delivery
contract, and the evidence that will prove success. Examples:

- “The creature reads as the same individual as reference 1; change only its
  facing.”
- “At 128 px the silhouette still reads as a low workbench.”
- “The final PNG is 512×640 with real alpha and a 70–80% subject footprint.”

Do not treat these as visual requirements:

- “Run this shell command,” “call the tool with `--size`,” or “copy whatever
  file appears newest.”
- “Try until it looks good,” with no iteration ceiling or acceptance test.
- “Do not inspect the image” or “report success if the command exits zero.”
- A requested delivery size presented as a promise that the generative tool
  itself will return that exact size.
- Contradictory required references with no priority or reconciliation rule.

The controller owns transport and desired results. The worker owns the exact
image prompt, inspection, and the choice of a higher-quality route within its
authority.

## Control message contract

App-server `turn/steer`, a human chat message, or a queued JSON file may carry a
control. Structured form:

```json
{
  "protocol": "rimworld.codex-art/v1",
  "job_id": "RUT_JAWA_WORKTABLE_NORTH_001",
  "sequence": 3,
  "created_at": "2026-09-06T20:42:00-07:00",
  "sender": "owner",
  "command": "feedback",
  "message": "The subject is only half as large on the canvas as requested.",
  "patch": {
    "delivery.subject_footprint.min_canvas_fraction": 0.70
  }
}
```

Commands:

- `feedback`: incorporate natural-language review into the next evaluation or
  iteration. Translate it into an explicit working constraint and log both the
  original words and the interpretation.
- `amend`: apply the supplied patch to the in-memory working specification.
  The immutable claimed request is never edited; the manifest records overlays.
- `set_max_iterations`: set a new absolute ceiling. Only owner or controller
  authority may increase it. If reduced to the number already used, stop now.
- `pause`: finish the current atomic file write, checkpoint, and wait without
  starting another image call.
- `resume`: continue a paused job.
- `stop`: start no new work, preserve any artifact already returned, write a
  stopped manifest, move the claim to `requests/stopped`, mark the worker
  offline, and end the turn.
- `accept`: promote the named iteration after deterministic validation.
- `reject`: preserve the named iteration as rejected; continue only if budget
  remains and the message gives a useful change.
- `status`: log and return a concise checkpoint without consuming an iteration.
- `report_next_tier`: outside the image-iteration budget, invoke the available
  OpenAI product-documentation skill once to refresh usage and compare the
  signed-in plan with its current next service tier. Log a separate
  `upgrade_report`. Never run this research during an ordinary usage poll.

Natural-language human controls are valid. “Stop and shut down” means `stop`;
“that's only half as large as requested” normally means the subject footprint,
not the PNG dimensions. If context cannot disambiguate canvas size from subject
scale, pause and ask one precise question rather than guessing.

Control precedence is: current owner message, owner control, controller control,
original request, worker preference. Process monotonically increasing sequence
numbers once. Preserve every processed control file.

## Event log contract

`jobs/<job_id>/events.jsonl` is the monitor's source of truth. Append one compact
UTF-8 JSON object per line, in one write, and flush it. Never rewrite or truncate
the log. Logging operations themselves are exempt from recursive logging.

Every live account-limit read also appends a `usage_read` followed by a
`usage_report` to `workers/<worker_id>/usage.jsonl`, including when no job is
claimed. If a job is active, mirror those two events into its `events.jsonl`.
The report contains consumed and remaining percentages, window durations and
reset times as the original Unix value, UTC, and Pacific local time, credit
availability, the scheduler decision, and only a boolean
`next_tier_report_recommended` marker. Pricing, plan comparisons, and production
advice are omitted unless an owner or controller explicitly sends
`report_next_tier`. An image-count maximum is `null` unless the provider
actually returns one; never estimate it from percentages. `event_seq` is
monotonic per worker in `usage.jsonl` and per job in `events.jsonl`.

Convert Pacific time with `America/Los_Angeles` rules. Any human-readable usage
status must include the reset's full date, time, and correct `PST` or `PDT`
suffix for every returned window. Never label a daylight-saving timestamp as
`PST` merely because “Pacific time” was requested.

Log immediately before and after every material action: claim, usage read,
request validation, reference inspection, prompt decision, generation dispatch,
tool return, artifact copy, visual evaluation, deterministic validation,
control handling, selection, delivery write, manifest write, state transition,
and shutdown. Long tool calls receive a `started` event before dispatch; their
completion is observed through app-server streaming even when the worker cannot
append during the call.

Event shape:

```json
{"protocol":"rimworld.codex-art/v1","event_seq":17,"ts":"2026-09-07T03:42:11.412Z","worker_id":"codex-art-01","job_id":"RUT_JAWA_WORKTABLE_NORTH_001","iteration":2,"event":"generation_dispatch","phase":"started","status":"running","message":"Targeted edit: increase subject footprint while preserving identity","paths":[],"metrics":{},"error":null}
```

`event_seq` is monotonic per job. `phase` is `started`, `completed`, `failed`,
or `observed`. Preserve exact external error text in `error.message`; add the
worker's interpretation separately in `error.interpretation`.

Update `workers/<worker_id>/state.json` at startup, before a long image call,
after it returns, and at shutdown. It contains `status`, `job_id`, `iteration`,
`thread_id` and `turn_id` when known, `last_event_seq`, and `updated_at`. This
file is a convenience heartbeat; `events.jsonl` remains authoritative.

## Artifact rules

Every returned image is evidence and is preserved. Never overwrite an earlier
iteration.

- Save raw output as
  `artifacts/iteration-NNN/source_intermediate.<ext>`.
- Make a checkerboard or otherwise inspectable preview as
  `preview_intermediate.png` when alpha is relevant.
- Save deterministic resized/padded output as
  `delivery_intermediate.png`.
- Write an `evaluation.json` containing criteria results, measured facts,
  visual diagnosis, and the single proposed change for another iteration.
- Mark every non-selected artifact with `artifact_role: "intermediate"` in the
  manifest. A rejected artifact remains intermediate and gains
  `decision: "rejected"` plus the reason.
- Copy only the selected, validated candidate to the declared delivery path.

Use native transparent generation when requested. Chroma key/removal is a
fallback only when `authority.may_use_chroma_fallback` is true. A source-size
mismatch is expected and is solved deterministically; do not spend another
generation merely to chase exact pixel dimensions.

## Work loop

For each authorized job:

1. Log worker readiness and read live usage limits when the transport exposes
   them. Obey the controller's usage policy. Never redeem a reset credit.
2. Atomically claim the request and log the result.
3. Validate the request contract, reference existence/hashes, delivery paths,
   and iteration ceiling. A malformed job becomes `needs_control`; it does not
   receive a guessed repair.
4. Inspect every reference with `view_image` before generation. Record ordered
   paths, roles, dimensions, and hashes. For an edit, make the edit target
   visible in the conversation before calling image generation.
5. Normalize the visual goal into a concise image prompt. Preserve canon and
   required details. State each reference's role. Restate edit invariants on
   every iteration. Prefer concrete desired visual states; concise negative
   constraints are allowed when they remove ambiguity.
6. Check controls, increment and log the iteration, then call the built-in
   image-generation tool once. One asset or variant per call.
7. Persist the returned image immediately as an intermediate artifact. A tool
   or stream timeout has an unknown outcome: inspect returned events, declared
   paths, and `$CODEX_HOME/generated_images` before declaring it absent.
8. Inspect the actual image. Run the applicable deterministic checks. Compare
   every acceptance criterion and invariant, not merely overall plausibility.
9. Write the evaluation and log one of:
   - `accept`: all `must` criteria pass and selection authority permits it;
   - `iterate`: budget remains and there is one concrete, high-confidence
     change likely to improve a failed criterion;
   - `needs_review`: art is plausible but subjective or selection authority is
     external;
   - `needs_control`: the request or new feedback is ambiguous/contradictory;
   - `failed`: a non-recoverable tool, policy, or validation failure;
   - `stopped`: a stop was received.
10. Before another generation, process controls, restate all invariants, and
    change only the diagnosed variable. Never retry merely because another
    attempt is available.
11. Stop early when the goal is met or further self-iteration has no specific
    expected gain. At `max_iterations`, select the best permissible candidate
    or report `needs_review`; never exceed the ceiling.
12. Write the final manifest, move the claim to its terminal request directory,
    update worker state, and either claim the next authorized job or shut down.

## Final manifest

Write `jobs/<job_id>/manifest.json` atomically. Minimum shape:

```json
{
  "protocol": "rimworld.codex-art/v1",
  "job_id": "RUT_JAWA_WORKTABLE_NORTH_001",
  "worker_id": "codex-art-01",
  "thread_id": null,
  "status": "accepted",
  "reason": "All must criteria passed on iteration 2.",
  "iterations_used": 2,
  "max_iterations": 4,
  "selected_iteration": 2,
  "request_sha256": "...",
  "references": [{"path": "...", "sha256": "...", "role": "identity", "order": 1}],
  "controls_applied": [{"sequence": 3, "command": "feedback", "message": "...", "interpretation": "..."}],
  "prompts": [{"iteration": 1, "prompt": "...", "change": "initial"}],
  "artifacts": [
    {"iteration": 1, "path": "...source_intermediate.png", "sha256": "...", "artifact_role": "intermediate", "decision": "rejected"},
    {"iteration": 2, "path": "...source_intermediate.png", "sha256": "...", "artifact_role": "selected", "decision": "accepted"}
  ],
  "delivery": [{"path": "...RUT_JawaWorktable_north.png", "sha256": "...", "width": 512, "height": 512, "has_alpha": true}],
  "criteria": [{"id": "silhouette", "severity": "must", "result": "pass", "evidence": "..."}],
  "usage_before": null,
  "usage_after": null,
  "started_at": "...",
  "finished_at": "...",
  "error": null
}
```

Terminal statuses are `accepted`, `needs_review`, `needs_control`, `failed`,
`refused`, and `stopped`. A missing artifact can never be `accepted`.

## Shutdown and recovery

“Stop and shut down” means stop this worker task, not the computer or Codex app.
Do not begin another image action. If interruption occurs during generation,
preserve and inspect any result that already arrived, log the interruption,
write a stopped checkpoint, and end. If the forced interrupt ended the turn
before that bookkeeping could run, perform only that bookkeeping in the
controller's checkpoint-recovery turn. Never turn a stopped claim back into
pending without controller instruction.

On restart, resume only a specifically named claimed job or a controller-requeued
parked job. Read its immutable request, complete event log, controls,
manifest/checkpoint, and existing artifacts before acting. The next iteration
number is one greater than the highest dispatched iteration in the event log;
never infer it from filenames alone.
