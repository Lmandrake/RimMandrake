---
name: generating-images
description: Generates raster images from a text prompt by driving the Codex CLI's built-in $imagegen tool, then retrieves, inspects and validates the result locally. Use when asked to create, generate, draw, render or make an image, texture, sprite, icon, concept art or mockup, and when an image with a transparent background is needed. Covers asking the built-in tool for real alpha directly — the only route to transparency on a ChatGPT-auth Codex install. For modifying an image that already exists, use editing-images instead.
---

# Generating images through Codex

Claude cannot synthesise raster images. Codex can. This skill makes Codex the
image worker and keeps Claude as the controller — which matters, because the
controller is the half that can *look at the result and iterate*.

The Windows baseline dates to 2026-08-12; runtime selection and Linux image generation
were reverified on 2026-11-10 with codex-cli 0.167.0. Measured facts live in
`references/codex-contract.md`.

## Check the toolchain first

On Archmagi/WSL2 the default is Linux `~/.local/bin/codex`, with login and image cache in `~/.codex`.
`RM_CODEX_SIDE=win` selects the Windows installation; `generate`, `edit` and `probe` also accept
`--codex wsl|win`. Linux paths stay native, including ext4 `--codex-home` directories. Linux worker
homes skip Windows sandbox templates/UAC; the Windows precautions below apply only to `win`.
Other hosts retain their previous default. Both installations share account quota.

```bash
python skills/generating-images/scripts/codex_image.py probe
```

Reports the CLI path, `CODEX_HOME`, auth mode and version without generating
anything. Run it before concluding that a failure is your prompt's fault.
- **Codex sandbox setup raises a full-screen UAC dialog on the owner's screen; never cause it (owner: "PLEASE STOP making Codex pop up its dialog").** Each elevated setup re-provisions the machine-wide CodexSandbox users with new passwords, so a seed template or shared home whose `setup_marker.json` + `.sandbox-secrets/sandbox_users.json` predate the latest provisioning is stale even when the runner exe matches, and every new isolated worker home re-runs setup (one dialog per home; a stale `.codex_sandbox_seed` makes `--codex-home` workers fail in 2 s with a sandbox-build mismatch). Keep template and shared home synced to the newest provisioning (`codex_image.check_sandbox_fingerprint` refuses to seed on a difference; copy the shared home's `.sandbox`, `.sandbox-bin`, `.sandbox-secrets` into the seed and delete half-made worker homes), run one call at a time on the shared home (`facing_regen_batch.py` refuses `-j != 1`), and stop a batch if a home's `.sandbox/sandbox.*.log` gains 'sandbox setup required'. Never mass-queue artpipe jobs (the daemon wakes 5 workers via `workers5.conf`) or start the daemon without checking the worker count is 1 on the shared home; ask first. `telemetryd` is pythonw and NOT the artpipe daemon: identify a PID by its command line before `Stop-Process`.
- **After a Codex app update, kill stale pre-update `codex.exe` / `codex-code-mode-host.exe` processes.** 'Module could not be found' dialogs and UAC prompts from both an isolated worker home and the shared home cleared only that way. If `codex_image.py` misbehaves, run `tasklist.exe | grep codex` and look for old processes before anything else.

## Generate

```bash
python skills/generating-images/scripts/codex_image.py generate \
  --prompt "a rusty industrial smelter seen from directly above" \
  --out src/Jawa/art_bench/smelter.png
```

For anything needing transparency, ask for it directly in the prompt (see
below). Add `--dry-run` to see the resolved command and final prompt without
spending a generation.

## ⚠️ Transparency comes from the prompt now, not a chroma key

**Changed 2026-09-06 — there is no `--chroma-key` flag on `generate`/`edit` any
more.** The built-in `image_gen` tool on this `chatgpt`-auth install emits a
**real alpha channel directly** when the prompt asks for one — MEASURED:
1448x1086 RGBA, 55.7% alpha-0, all four corners `(0,0,0,0)`, 0.28% mid-alpha, no
rim or halo — cleaner than a keyed cut ever was. Ask for transparency in the
prompt itself; do not generate onto a flat key colour expecting to cut it out.

```bash
python skills/generating-images/scripts/codex_image.py generate \
  --prompt "a brass astrolabe, top-down, centred, on a fully transparent background" \
  --out src/Jawa/art_bench/astrolabe.png
```

`chroma_key.py` still exists as a **standalone post-process script** for the
rare case that genuinely needs to key out a flat background it already has
(e.g. `build_sea_facings.py` calls it directly) — it is no longer wired into
`codex_image.py generate`/`edit`, and reaching for its `--chroma-key` flag on
either subcommand will fail: the flag was removed with the generation path,
not merely deprecated.

`gpt-image-1.5 --background transparent` (the deterministic CLI fallback) still
requires an `OPENAI_API_KEY`, which this machine's `auth_mode: chatgpt` does not
provide — irrelevant now that the built-in tool gives real alpha for free.

## Always look at what you got

The reason this pipeline is worth building is that you can inspect the result.
Read the PNG back — Claude renders images — and check it against what you
asked for. To judge alpha specifically, composite over a checkerboard first;
transparent and black look identical otherwise.

```bash
python skills/generating-images/scripts/preview_alpha.py \
  --input src/Jawa/art_bench/astrolabe.png --out src/Jawa/art_bench/_check.png
```

Then read `_check.png`. A green rim, a soft halo or a chewed edge is visible
there and invisible in the raw file.
- **Check `im.mode` and the raw size after every render.** `codex_image.py edit` can return an OPAQUE RGB picture on pure black even when the prompt asks for real alpha (3 of 3 fire-reel masters; `rembg_cut.py` was OOM-killed rc 137 in the seat cgroup, while a border flood fill over max-channel <= 10 cut the flat black cleanly because the subject never touched pure black), and it can return 256x256 when the attached reference is 256x256: attach a larger reference or accept the native size for small-canvas art, and check the raw size before conforming.
- **Never trust an agent-placed output file as the generated image.** When codex `image_gen` returns no output path the agent may copy the newest PNG from ANY codex cache (even the global `~/.codex`) into the output path, and a worker's `self_report` is no check (7 of 8 foreign-copy installs self-reported ok). The guard (`codex_image.py` CODEX_FOREIGN_IMAGE_COPY) must compare by PICTURE, not bytes, because workers resize to canvas (0 of 10,697 cache files matched by sha) and one resize beats a byte-identity guard: alpha-bbox crop, 16x16 box thumbnail, mean abs diff <= 4.0 (copies measured 1.1-1.6, nearest legitimate pair 7.05), against the cache AND other jobs' outputs, excluding candidates near the call's own `--image` inputs. Confirm any coarse match with a fine-detail measure (high-pass correlation at 32x32: copies 0.96-1.00, independent terrain -0.03..0.05), since independent flat subjects (soil vs soil, ice vs snow) score 1.8-3.6 on the thumbnail; calibrate against a census of real sibling pairs, not synthetic tests (`/mnt/d/ClaudeWork/rimmandrake/guard_resize/calib.json`, `guard_vet/`). To trace a copy, read the worker's rollout jsonl (manifest `meter_after.rollout`) for its Copy-Item/cp command, which names the cache file; legit vs suspect done jobs differ in manifest `worker_stderr_tail` 'harvested exec-'. A match names TWO jobs and neither is necessarily the source (a prop sheet of four bollards was placed by both): look at the pair, and check the art-eval decisions before requeueing, since the pipeline may already have judged and redrawn the copy.

## Prompting

Full guidance in `references/prompting.md`. The three rules that matter most,
because they are the ones that get violated:

1. **Never phrase a constraint as a prohibition.** Image models condition on
   the tokens present, so "no glowing lights" reliably produces glowing lights.
   Write the state you want instead: "every lamp is dark grey, cracked, unlit".
2. **Constraints first, and keep the whole prompt short.** Early tokens carry
   more weight. A 900-word specification gets sampled, not followed.
3. **Nothing human-facing in the prompt.** Shell commands and rationale dilute
   what is left and cannot be acted on.

## Cost and timing

A generation takes roughly one to several minutes and consumes the owner's
Codex quota. Treat each call as costing something real: use `--dry-run` while
iterating on prompt wording, and generate at low ambition first — one small
image proves the plumbing before a large one proves the art.

### 🔴 RUN GENERATIONS IN THE FOREGROUND, ONE PER CALL. DO NOT BATCH THEM.

**Measured 2026-08-24 over ~20 `edit` calls in one sitting** against an
`auth_mode: chatgpt` install:

| how it was run | result |
|---|---|
| **Foreground, one call per turn, `--timeout` ~105 s** | **8 of 9 succeeded**, 79–93 s each. The one failure succeeded on an immediate retry. |
| **Backgrounded batch script looping over facings** | Repeatedly reported **failed** (exit 1, exit 144) partway through — *sometimes while the shell was still alive and still writing files*. |

⇒ **The generator is reliable; batching it is what was not.** A long-running
background job here can be reported dead, and killed, while its work is incomplete —
so a retry loop inside one never gets to retry, and its partial output turns up later
looking like a ghost.

**The rules that follow from that:**

- ✅ **One generation per invocation, in the foreground.** ~80 s fits inside a normal
  command budget. Retry at the CALLER's level, not inside a script.
- ⏱️ **Cap `--timeout` near 105 s.** A good call returns in 79–93 s; past ~110 s it is
  not coming, and the default 780 s burns thirteen minutes to learn nothing.
- 🔁 **A failure is not a diagnosis — just run it again.** The identical prompt
  succeeded on the next attempt every time it was tried.
- ⚠️ **Check for orphans before re-running a batch.** Two copies of a killed script
  were still alive and racing on the same output paths; `codex_image.py` refuses to
  overwrite, which is the only reason it was harmless. Kill by **PID**.

⛔ **AND NEVER "CLEAN UP STRAYS" BY PATTERN:**

    pgrep -f codex_image.py | xargs -r kill -9      # matches the PARENT too

A script written by a heredoc carries its own text — that string included — in the
parent shell's argv, so this SIGKILLs the batch it is retrying. ✅ `timeout` already
reaps the child.

⚠️ **TWO WRONG DIAGNOSES WERE PUBLISHED HERE BEFORE THE RIGHT ONE, AND THAT IS THE
LESSON WORTH MORE THAN THE FIX.** First "the second `--image` causes it" — three
two-image calls hung in a row, then a single-image call hung identically. Then "the
`pgrep` line causes it" — removing the line changed nothing. Both were confident,
both fitted the evidence to hand, and both were wrong because the sample was small
and confounded. ⇒ **Before blaming a component, run the simplest possible version of
the call by hand.** That took 77 seconds and settled it.

⚠️ **Concurrent workers collide on the shared harvest dir.** Two codex `image_gen`
workers running at once can both land in the same `CODEX_HOME`'s generated-output
folder, and one worker's harvest picks up the OTHER worker's render as its own —
an unrelated subject silently reported as a success (BENCH 2026-09-14). Serialize
generation, or give each worker its own `--codex-home` (and therefore its own
harvest dir) rather than sharing the default.

## Validation plan — what you owe whoever checks this

Whoever asked for the image is the one who decides it is right, and their look
costs more than yours — so hand the image over with the plan for checking it,
not just the file. Whoever asked for the image is the one who decides it is
right, and their look costs more than yours — so hand the image over with the
plan for checking it, including the prediction you made before you looked.

**1. The observable — what a player SEES when it works.**
🔴 **A positive observation, never "no error".** Name the thing on screen.

**2. The route — the exact call, click path or spawn that produces it.**
The defName, the tool call with its arguments, the menu path. ⚠️ **If the route
needs a tool that does not exist yet, say so and file it as blocked on the
tool.**

**3. The prediction — written BEFORE the look.**
A number or a specific string. Without it you will rationalise whatever you see.

**4. The threshold — what CLOSES it, and what is explicitly out of scope.**
⭐ **A good threshold is usually one observation, not a battery.**

**5. Batch or solo.**
Most checks ride together. Solo is for anything that would destroy attribution.

**6. What a FALSE PASS looks like.**
The way this particular check lies. Every check has one, and it is the field
people skip.

```
PROVE    <exact call / defName / click path>
EXPECT   <number or string, written before the look>
LIES     <how this check produces a false pass>
```

Three lines. If it does not fit, the item is really two items.

### How generated-image checks lie

- **Transparent and black are the same picture.** Judging alpha from the raw PNG
  passes a fully opaque black background and fails a correct cutout for the same
  reason: neither is visible. Route the check through `preview_alpha.py` and say
  in the plan that the reviewer is looking at the checkerboard composite.
- **The key came out and so did part of the subject.** A green fitting on a
  `#00ff00` key gets holes punched through it, and the result still reads as a
  clean cutout wherever the hole sits over dark detail. Predict the coverage
  figure, and re-key on `#ff00ff` if it drops.
- **An invisible fringe passes every visual check.** Pixels at alpha 1–31 are
  invisible on screen and still corrupt every bounding box, coverage and
  centroid measured downstream. The eyes cannot see this one; only the numbers
  can, so put a number in the plan.
- **The consumer is stale.** The generation succeeded and the reviewer opened
  the previous file at the same path. Give the full path and its mtime with the
  hand-off.
- **The auto-detected key matches banked alpha, not the flat background.** On two
  mockups banked WITH alpha, the border pixels sampled as transparent BLACK, so
  `chroma_key.py`'s auto-detect took that as the key and keyed out every dark pixel
  of the subject. The validator reported **0 REJECT** — it only measures the
  output's shape, not whether the subject survived. Only a contact sheet, looked
  at, showed the wreckage (AbyssalColo and ElderSando washed out beside solid
  siblings). Detection for this case was added in `build_sea_facings.py`
  (`f66246a7`) — check whether the border sample is already transparent before
  trusting an auto-detected key on art that may already carry alpha.

### Worked example

```
PROVE    python skills/generating-images/scripts/preview_alpha.py --input astrolabe.png --out _check.png
EXPECT   full brass ring and crossbars over the checkerboard, no green rim, no chewed edge · coverage 25–40% of canvas; all four corners fully transparent; no pixels at alpha 1–31
LIES     the raw PNG hides everything — an opaque black background looks identical to real alpha
```

## Reference

- `references/codex-contract.md` — verified CLI facts: how the binary is
  located, auth modes and what each unlocks, size limits, output locations.
- `references/prompting.md` — what works, what backfires, worked examples.
- `scripts/codex_image.py` — the engine: `generate`, `edit`, `probe`.
- `scripts/chroma_key.py` — key-to-alpha with self-validation.
- `scripts/preview_alpha.py` — composite over a checkerboard for inspection.
- `scripts/pnglib.py` — dependency-free PNG read/write/resize.

## Dependencies

**None beyond the standard library.** This is deliberate: Pillow is not
installed here, so the Codex-supplied `remove_chroma_key.py` cannot run, and
everything in `scripts/` works without it.
