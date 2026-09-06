# A receiving agent inside Codex — accelerating graphics generation

Exploration, 2026-09-06. **Nothing here is built.** No skill or script was edited;
no image was generated. CLI facts read off *this* machine against **codex-cli
0.153.1** — `skills/generating-images/references/codex-contract.md` was verified
against 0.147.0-alpha.6.6 and has decayed (§2.3).

## 1. How the pipeline runs today

`skills/generating-images/scripts/codex_image.py` builds one process per image:

```
codex.exe exec --sandbox workspace-write --skip-git-repo-check \
    [-m MODEL] [-i <win-path>]... [--] "<prompt>"        cwd = the output PNG's parent
```

`build_prompt()` emits `Use $imagegen to <prompt>` + optional flat-chroma-key
clause + *"copy the generated image into the cwd as `<name>`"*. The built-in
`image_gen` tool takes **no destination argument**, so output lands in
`$CODEX_HOME/generated_images/<session-uuid>/exec-<uuid>.png` and is recovered by
the agent obeying that instruction or by `harvest_new()` diffing the directory.
Downstream is ours: `chroma_key.py` (or `rembg_cut.py` via `make_sprite.py`) →
`conform_sprite.py` → `validate_sprite.py` → `preview_alpha.py`/`contact_sheet.py`.

### The drivers already contradict the doctrine

Thirteen scripts call `codex_image.py`; three are batch drivers.
`src/RimStarWars/SeaBeasts/art/tools/gen_sea_facings.py` runs
**`ThreadPoolExecutor(max_workers=3)`** — 3-way parallel, `--timeout 210`, 3
attempts, per-call wall time logged. `gen_sea_mockups.py` and
`gen_livestock_mockups.py` are deliberately serial (`max_workers=1`,
`--timeout 420`).

🔑 **`generating-images/SKILL.md` forbids batching; the newest driver batches
3-way and justifies it inline.** `gen_sea_facings.py` also records the
measurement the skill lacks: **an `edit` carrying a ~1.5 Mpx reference lands at
120–170 s, not the ~80 s measured for `generate`** — reference-conditioned work,
which is exactly what a receiving agent would mostly do, costs roughly double.

### Measured cost — 427 images across 327 sessions, 2026-08-12 → 2026-09-06

From `$CODEX_HOME/generated_images/`: session start from the UUIDv7 ms prefix,
arrival from file mtime.

| | median | p25 | p75 | p90 | min | n |
|---|---|---|---|---|---|---|
| session create → **first** image on disk | **62 s** | 47 | 76 | 89 | 27 | 327 |
| **second** image in the same warm session | **54 s** | 43 | 95 | — | 27 | 100 |

- **243 of 327 sessions produced exactly one image** — the cold start is paid on
  ~74% of images, and warmth is worth only ~8 s of 62 s.
- **Max concurrent image sessions observed: 4**; ≥3 at 42 distinct moments.
  Parallel `codex exec` has already produced images here.
- **Peak measured throughput: 17 images in 10 min** from 2026-08-24 00:35 →
  **102 img/h**, against ~58/h implied by the serial median.

### Where the serialization actually is

Not the model. **The orchestrator.** `SKILL.md` mandates *"one generation per
invocation, in the foreground"* after backgrounded batching "failed" on
2026-08-24 — **yet 2026-08-24 00:35 is the highest-throughput window in the whole
history.** The skill itself notes the batch "reported failed … *sometimes while
the shell was still alive and still writing files*." The generator was at its
best measured rate while the orchestrator called it dead. ⚠️ How much of the 62 s
is CLI/agent startup versus render is **UNMEASURED** — mtimes cannot separate
them. A third, softer cost: every image spends a Claude turn re-explaining the
same constraints and returning unstructured chat.

### 🔴 The channel is wedged as this is written

`TREE_GRAPHICS_OWNERSHIP_1` (ledger, 2026-09-05/06) records **~14 consecutive
timeouts at 105–180 s producing no file**, across three passes, while `codex.exe`
PID 5028 and `codex-code-mode-host.exe` PID 11236 sat unchanged for hours — both
still alive now. Its second finding decides a design question: *"Lock file in
`.codex/thread-writer-locks/` renews every time ANY codex exec call runs
(including mine), so its freshness does not distinguish self from external
contention."*

⇒ **One wedged `codex.exe` takes the whole channel down and there is no reliable
liveness signal.** Any design must assume this, or N-way parallelism just buys N
simultaneous timeouts. It is also the decisive argument against a single
long-lived receiver (§2.2 B).

## 2. Feasibility — Codex 0.153.1 as a receiver

### 2.1 Verified (from `--help` and strings in the binary, this machine)

| capability | flag / command | note |
|---|---|---|
| non-interactive | `codex exec [PROMPT]`, `-` for stdin | used today |
| reference images | `-i, --image <FILE>...` **variadic**, needs `--` | used today |
| **deterministic reply** | `-o, --output-last-message <FILE>` | **unused** — removes all output scraping |
| **structured reply** | `--output-schema <FILE>` (JSON Schema) | **unused** — makes a machine-readable manifest first-class |
| event stream | `--json` (JSONL) | per-request progress, failure attribution |
| **session persistence** | `codex exec resume [ID\|--last]`, `codex exec fork` | warm pools |
| **mailbox into a live session** | `codex queue --thread <uuid\|name> --message TEXT [-i ...]` | needs the app-server daemon |
| workspace isolation | `-C, --cd <DIR>`, `--add-dir <DIR>` | per-worker scratch; lets a worker run our validators |
| no session litter | `--ephemeral` | |
| **project prose IS read** | `AGENTS.md` | binary: *"AGENTS.md file at the root of the repo and any directory…"*, *"the scope … is the entire directory tree rooted at…"*; config keys `project_doc_max_bytes`, `project_doc_fallback_filenames`. **No AGENTS.md exists anywhere in this repo or in `$CODEX_HOME`** |
| per-session lock | `$CODEX_HOME/thread-writer-locks/<uuid>.lock` | not a global mutex — ⚠️ but renewed by *any* exec, so useless as a busy signal |

**Cannot:** there is no watcher daemon — `codex exec` is one-shot and `codex
queue` needs a session already live, so the receiving agent is *prose plus a file
contract*, never a service Codex hosts for us; the image tool still has no output
path; there is no rate-limit introspection (`auth.json` carries only
`auth_mode: chatgpt`, and 4 concurrent is merely the highest we have accidentally
reached, **UNMEASURED** as a ceiling); and a Codex agent can measure its art but
cannot grade it — style stays a Fable-tier review.

### 2.2 The three architectures

| | **A · N parallel `exec` workers over a request directory** | **B · One persistent session fed by `codex queue`** | **C · Hybrid: warm pool** |
|---|---|---|---|
| shape | supervisor scans `pending/*.json`, launches ≤N `codex exec`, each `-C` into its own scratch with `-o` + `--output-schema` | one long-lived session; `queue --thread` posts each request; serial backlog | K warm sessions; `exec resume <id>` with the next request |
| speedup | **~N×, bounded by an unknown account ceiling.** 4-way already demonstrated; 102 vs 58 img/h ≈ **1.8× at unknown concurrency**. N=4 → target ~3–4× | **~1.1×** — warmth saves ~8 s of 62 s, and it is serial by construction | ~N× × 1.15 |
| failure modes | orphans racing one output path (already bitten us; `codex_image.py`'s overwrite refusal is the only reason it was harmless); 429s that read as refusals; the `--` trap's silent exit-0; **N workers all timing out on one wedge** | **the wedge is this architecture's normal state** — a long-lived process is exactly what is stuck now; one poisoned context degrades every later request; a crash loses the backlog; `queue` is fire-and-forget | context drift across a long batch; session bookkeeping; a resumed session inherits its own mistakes |
| build cost | **~1 day**: supervisor ~200 lines, JSON contract, `AGENTS.md`, reuse every existing validator | ~half a day for a small prize | ~1.5 days |
| verdict | ✅ **build this** | ❌ | ⏭️ after A is measured |

### 2.3 ⚠️ A live contradiction worth settling first

`C:\Users\Mandrake\.codex\skills\.system\imagegen\SKILL.md` now says three times
that the **built-in tool does transparency with no API key**: *"built-in
`image_gen` tool for image generation, editing, and transparent-image requests.
Does not require `OPENAI_API_KEY`"*; *"ask built-in `image_gen` for a transparent
background and preserve the generated alpha."* Our contract doc says the
opposite, and every sprite pays a chroma-key round trip and despill for it. **If
native alpha works now, that whole stage disappears** — a quality win too, since
chroma-keying has twice destroyed subjects here. **UNVERIFIED**; one generation
settles it, and it rewrites §3.

## 3. The prose — `AGENTS.md` for the receiving agent

At the root of the worker workspace (e.g. `Transient/artqueue/AGENTS.md`) so its
scope covers the queue tree; keep it under `project_doc_max_bytes`.

> ### You are an image worker. One request in, one manifest out.
>
> Read the request file named in your prompt, produce exactly the image it
> specifies, prove it meets the stated constraints, write a manifest. You are not
> a conversationalist and you do not ask questions. If a request is impossible,
> say so **in the manifest** and stop.
>
> **The request** is one JSON file at the absolute path in your prompt:
> `id` (echo verbatim) · `prompt` (use as written — normalise, never expand) ·
> `references[]` (absolute paths, already attached to this turn as images **in
> this order**, each with `role`: `style`, `edit_target`, `silhouette`) ·
> `canvas` `{width,height}` — the size you must **generate at**, already legal
> (multiples of 16, max edge ≤3840, ratio ≤3:1, 655,360–8,294,400 px) ·
> `background` (`"transparent"` or a hex key such as `"#10e010"`) · `footprint`
> (optional box the silhouette must fit inside **and span ≥94% of**) · `out`
> (absolute path the finished PNG must exist at) · `manifest` (where your report
> goes).
>
> **In this order:**
>
> 1. If a reference has role `edit_target` and is a file on disk, open it with
>    `view_image` first — the built-in editor only sees images already in this
>    conversation.
> 2. Call built-in `image_gen` **once**, at `canvas`'s exact size. If
>    `background` is `transparent`, ask for a genuinely transparent background
>    and preserve the alpha it returns. If it is a hex colour, render the subject
>    on a perfectly flat solid field of that colour — one uniform colour, no
>    shadow, gradient, floor plane or lighting variation — and use that colour
>    nowhere in the subject.
> 3. **Never phrase a constraint as a prohibition.** Image models condition on
>    the tokens present, so "no glowing lights" reliably produces glowing lights.
>    Write the state you want: "every lamp is dark grey, cracked, unlit".
> 4. Copy the file to `out`. The tool takes no destination argument, so this is a
>    real copy and it is yours to do. Never leave the only copy in
>    `$CODEX_HOME/generated_images/`.
> 5. Check it **by measuring, not by looking**: read the PNG header for
>    width/height and colour type; if transparency was asked for, confirm the
>    colour type carries alpha and all four corners are fully transparent.
> 6. Write `manifest` and stop. Your final chat message is one line: the `id`,
>    and `ok` or `fail`.
>
> **The manifest** — exactly this JSON, no prose around it:
>
> ```json
> {"id":"<echoed>", "status":"ok|fail|refused", "out":"<abs path or null>",
>  "width":0, "height":0, "has_alpha":true, "corners_transparent":true,
>  "background_used":"transparent|#rrggbb", "attempts":1,
>  "note":"<=200 chars: what you changed from the prompt, or why it failed"}
> ```
>
> **Failure is reported, never disguised.**
> If the tool refuses, `status` is `refused` and `note` carries the refusal's own
> words — do not paraphrase it into something friendlier, and retry a refusal at
> most once. If you produced an image that misses a constraint — wrong size, no
> alpha when transparency was asked for, an opaque corner — write `fail` with the
> measured numbers. ⛔ **Do not fix it by cropping, upscaling or padding**; a
> wrong-sized image reported honestly beats a right-sized one silently mangled. A
> missing `out` with `status: "ok"` is the worst outcome available to you —
> verify the file exists before writing `ok`. You get **one** retry, only for a
> tool error or refusal, never to improve the art; set `attempts: 2` if you use it.
>
> **Never:** edit outside your working directory · touch another request's files ·
> generate more than the one image asked for · leave the manifest unwritten (a
> crashed run with no manifest is indistinguishable from a hung one, and the
> supervisor will kill you for it) · put in the chat what the manifest should carry.

### The file contract and the supervisor

```
artqueue/  AGENTS.md
  pending/<id>.json     supervisor writes; worker never touches
  running/<id>.json     atomic rename on claim = the lock
  out/<id>.png          manifest/<id>.json      done/ | failed/
```

```
codex.exe exec --sandbox workspace-write --skip-git-repo-check \
  -C artqueue/scratch/<id> --add-dir artqueue \
  -i <win path to ref>... \
  -o artqueue/manifest/<id>.last --output-schema artqueue/manifest.schema.json \
  -- "Process the request at <win path to running/<id>.json>."
```

**Preflight, before any worker launches** — the part that earns its keep: run
`codex --version` with a 20 s cap as a liveness canary; snapshot the Windows
`codex.exe` PID set; refuse to start when a PID has persisted since the previous
run *and* the last few requests all timed out — that is the §1 wedge signature,
and the honest response is to stop and say so, not to burn N workers on it.
⛔ **Never kill a `codex.exe` the supervisor did not start** — a persistent one
may be the owner's own session.

Then per request: wait with a timeout near **150 s** for a `generate`, **220 s**
for a reference-carrying `edit` (cold p90 is 89 s; a 1.5 Mpx edit measured
120–170 s) → read the manifest → if absent, harvest `generated_images/` by
directory diff exactly as `codex_image.py` does today → run
`chroma_key.py`/`rembg_cut.py`, `conform_sprite.py` and `validate_sprite.py`
**outside** Codex, because those are ours and their thresholds are calibrated →
move to `done/` or `failed/`. Retries live at the supervisor, never inside a
worker, and it kills **by PID** — `pgrep -f` matches its own argv and has
SIGKILLed the parent here before.

## 4. Recommendation and open questions

**Build architecture A: a request-queue directory with N parallel one-shot
`codex exec` workers, each carrying the `AGENTS.md` prose above and returning a
schema-validated manifest via `--output-schema` and `-o`.** The case is that the
only ceiling we have ever measured is the orchestrator's — on 2026-08-24 the
pipeline hit 102 images/hour, 1.8× the serial median, during the very sitting
whose batch script was recorded as a failure, and four concurrent Codex image
sessions have run here without incident. The prose matters as much as the
parallelism: today each request re-explains its constraints through a Claude turn
and returns chat that a script greps, whereas a receiving agent that already
knows the contract turns each image into a file write and a manifest read — which
is what makes N-way fan-out safe to supervise at all. Expected speedup at N=4 is
**~3–4×, UNMEASURED**, with ~1.8× already demonstrated at unknown concurrency; so
the honest first deliverable is not the queue but a calibration run sweeping
N ∈ {1,2,4,6} over the same eight prompts, reporting images/hour and failure rate
per N. That number does not exist yet, and the wedge must clear before it can.

**Open questions for the owner:**

1. 🔴 **Is `codex.exe` PID 5028 yours?** ~14 generations have timed out against
   it; the channel is blocked as this is written, nothing below can be tested
   until it clears, and it is not ours to kill.
2. 🔴 **Does the built-in tool now do native transparency** (§2.3)? One
   generation settles it and it deletes a whole pipeline stage if true.
3. **What is the account's concurrency ceiling, and what does exceeding it look
   like?** A rate-limit refusal that reads as a content refusal would poison the
   manifest's `status` semantics. ~8 images to find out.
4. **Doctrine call:** `SKILL.md` forbids batching while `gen_sea_facings.py`
   batches 3-way. Whichever way calibration lands, one of those files must be
   rewritten — and skills are curated only in fresh-context passes, so it needs
   scheduling, not an in-flight edit.
5. Supervisor in `src/RimMandrake/Utils/` as a first-class tool, or in
   `skills/generating-images/scripts/` beside the engine it drives?

**Prior art:** `design/Jawa/worldbuilding/graphics_pipeline_recommendation.md`
(2026-09-05) already proposed "batch/parallelize overnight" and a parallel Gemini
CLI channel as CONSIDER-ONLY; this is the concrete design for the first half and
does not touch the second.
`skills/generating-images/references/codex-contract.md` stays the verified-facts
file, but §2.1 and §2.3 supersede it on this install's version, on
`--output-schema`/`-o`/`resume`/`queue`, and possibly on transparency.
