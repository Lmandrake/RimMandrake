# The art pipeline and Dispatch: what is there, where the seam is, and how to move the generic half

Item: `RIMMANDRAKE_STUDY_ART_PIPELINE_SPLIT_CODEX_GRAPHICS_FROM_RIMMANDRAKE_ART`. Study only: this run changed no code,
moved no file and restarted nothing. Written 2026-11-22, 3:30 to 4:30 PM PST, on Archmagi.
Sister item: `RIMMANDRAKE_ROUTE_EVERY_GPT_CONSULT_THROUGH_DISPATCH_ONE_DOOR_CAREFULLY` (the GPT consult door; its
draft is `D:\ClaudeWork\scratch\dispatch-gptdoor\design\specs\2026-11-22-gpt-door.md`, not landed when this was written).

Tags: **[measured]** = read or counted in this run, with the time; **[documented: source]** = a primary document
says so; **[guess ~N%]** = my estimate.

---

## Summary (one page; act on this)

**The dialog.** The "big dialog on black" is the Windows UAC prompt. Only the **Windows** `codex.exe` raises it,
when its `elevated` sandbox must run its setup for a Codex home. The setup creates two machine-wide users
(`CodexSandboxOffline`, `CodexSandboxOnline`) and firewall rules. It runs when a home has no sandbox state, when an
auto-update changes the command-runner build, or when another home's setup has reset those users' passwords
(every other home is then stale). Linux Codex inside WSL has no Windows setup and cannot raise it.
**Since 2026-11-10 every art job on Archmagi runs on Linux Codex** [measured: `codex_side()` = `wsl`, 36 jobs
passed from 2026-11-13 to 2026-11-21 in `/home/mandrake/.codex_workers/artpipe/w*`, and the 60 failures of
2026-11-20 ran there too]. The art path has not been able
to raise the dialog since then.

**The better way.** Keep it so, on purpose: Linux Codex is the one image route on Archmagi, and the Windows image
route and its ~600 lines of sandbox guards retire after one deprecation step. If a Windows route is ever needed
again, use Codex's newer `mxc` Windows sandbox (`[features] prefer_mxc = true`), which needs no administrator setup,
no extra accounts and no firewall rules [documented: developers.openai.com/codex/windows]. Confidence that the
Linux route stays free of the dialog: **~90%** [guess; the residual is an owner-run Codex desktop app or a
`--codex win` caller, both outside the art path].

**The real risk now is sign-in sharing, not the sandbox.** OpenAI's own guide says: "Use one auth.json per runner
or per serialized workflow stream. Do not share the same file across concurrent jobs or multiple machines"
[documented: developers.openai.com/codex/auth/ci-cd-auth]. The art daemon does the opposite in two places:
a new worker home is seeded with a copy of `~/.codex/auth.json` (the same file the GPT consults use), and
`resync_stale_worker_homes` copies one home's `auth.json` over the others.

**Why the queue was down, and its state now.** It is **up and idle** [measured 3:34 PM PST: `rm-artpiped` pid
1463194, phase IDLE, 0 pending, last job passed 2026-11-21 3:30 AM]. It was down from some time between
2026-11-15 5:31 PM and 2026-11-20 3:51 PM until 2026-11-21 3:24 AM, not "since 2026-11-10" [measured from
`throughput.jsonl`]. Cause: the five Linux worker homes were seeded on 2026-11-13 from `~/.codex`, so they held
copies of one refresh-token lineage that the GPT consults also refresh; on 2026-11-20 all 60 jobs failed with
"your refresh token was already used" [measured]. He fixed it with five device sign-ins on 2026-11-21. **Smallest
safe act to keep it up** (not done here): stop the daemon from copying sign-ins between homes (seed a new home by
`codex login --device-auth`, never by copy), and add the dead-sign-in alarm that item
`RIMMANDRAKE_TEST_ART_WORKERS_SHARING_ONE_CODEX_LOGIN_NOT_FIVE` already asks for.

**The seam, in three lines.**
1. Generic: "run one image request on a provider" (prompt, reference images, canvas, alpha, model, deadline),
   harvest the file, refuse a foreign file, report a typed outcome, hold one sign-in home per concurrent worker.
2. RimMandrake: what to draw and whether it is right (house register, canon briefs, facings, true scale,
   def canvases, validators, canon check, judges, review sheets, the art ledger, install).
3. Tangled today: the daemon `artpiped.py` (3,667 lines) does both, and about 26 one-off scripts call
   `codex_image.py` directly, each with its own sign-in home.

**Can Dispatch carry the generic half?** **Yes, with changes**: a `graphics` provider beside `providers/chatgpt/`,
one sign-in pool and one sign-in probe shared with the GPT door, typed outcomes, and no RimMandrake words in it
(Dispatch is a public repo). The queue, the gates and everything in line 2 stay in RimMandrake.

**First three steps** (each leaves the system working; details in §6):
1. Stop the sign-in copying and add the dead-sign-in alarm (RimMandrake and MandrakeWorkflows only; no Dispatch).
2. Fix `selftest_artpipe.py`, which writes a `.codex_sandbox_backup_*` folder into `C:\Users\Mandrake` on every run
   (169 of the 170 such folders are its fixtures) [measured].
3. Put the Codex image call behind a Dispatch `graphics` provider with the same command line as `codex_image.py`;
   prove it on recorded jobs; point the daemon at it.

**What I could not look at:** whether `mxc` is available on Archmagi (needs one attended `codex.exe` run);
whether five workers can share one sign-in safely (the open test item); the cost of the Images API for our
canvases (needs an API key; none is configured); the full 60,504 lines of `src/RimMandrake/Utils/art/` (I read the
entry points only).

**Disk that could go** (listed, not deleted; §3.6): about 90 GB of Windows-era Codex homes in
`C:\Users\Mandrake\.codex_workers\` (last art use 2026-11-08), 24 of which hold an `auth.json` copy, and 169
selftest leftovers in `C:\Users\Mandrake\.codex_sandbox_backup_*`.

---

## 1. What is there today

### 1.1 The parts, with sizes [measured 2026-11-22]

| part | where | lines | what it does |
|---|---|---|---|
| art daemon | `src/RimMandrake/Utils/artpipe/artpiped.py` | 3,667 | claims queue jobs, builds the prompt, runs a worker per job, gates, finalizes |
| daemon helpers | `artpipe/common.py` | 759 | queue paths, job schema (`load_job`), house register, size clause, Codex home lease, sandbox wrappers |
| queue location | `artpipe/state_dir.py` | 63 | `D:\ClaudeWork\rimmandrake\artpipe` (`pending/ active/ done/ failed/ _artsrc/`) |
| queue writers | `artpipe/fill_queue.py`, `idle_fill.py` (timer `rm-artpipe-idle-fill`) | 904 + 228 | turn art lists into job files; refill when the queue is low |
| registry | `artpipe/artreg.py` | 855 | sole writer of `registry.jsonl` (which render belongs to which subject) |
| queue ops | `artpipe/artpipe_state.py` | 832 | `where`, `find`, `collect` (done job to a Textures path) |
| canon check | `artpipe/canon_check.py` | 656 | grades a finished render against its canon entry with a vision call (Codex) |
| console | `artpipe/console.py` | 764 | the status line, per-run log, `status/heartbeat.json` |
| image tool | `~/dev/MandrakeWorkflows/skills/generating-images/scripts/codex_image.py` | 1,854 | finds Codex, seeds a home, sandbox guards (Windows), runs `$imagegen`, harvests the file, foreign-file guard |
| finder copy | `src/RimMandrake/Utils/codex_cli.py` (deleted 2026-11-22, `c96e6cb2`) | 172 | was a copy of the finder half of `codex_image.py`, for `gpt_consult.py`; the consult finder now lives in Dispatch `providers/chatgpt/bin/gpt_door.py` |
| second queue | `generating-images/scripts/codex_queue_runner.py` | 302 | N one-shot workers draining a file queue (the first parallel design; superseded by the daemon in practice) |
| Gemini channel | `generating-images/scripts/gemini_image.py` | 171 | Nano Banana Pro, API key in `~/.config/rwgfx/gemini.key`, no alpha (rembg after) |
| meters | `generating-images/scripts/codex_grumpiness.py` | 147 | reads the account rate-limit meter from a Codex rollout file |
| alpha tools | `chroma_key.py`, `rembg_cut.py`, `pnglib.py`, `preview_alpha.py` | 698 | cut-outs and PNG facts |
| sprite rules | `skills/generating-rimworld-sprites/scripts/` (`validate_sprite.py`, `conform_sprite.py`, `make_sprite.py`) | — | RimWorld canvas, alpha and footprint rules |
| art ledger | `src/RimMandrake/Utils/art/artledger.py` + CLI `art.py` | 2,212 + 578 | events `infrastructure/state/art/events/<SEAT>.jsonl`; `install`, `put`, `bans`, `purge`, `ingest` |
| enact | `art/enact.py` | 2,690 | carries out a ruled review sheet in one pass |
| sheets | `art/art_sheet.py` (+ `serve_gated.py`) | 4,081 | all-versions comparison sheets, true scale beside a vanilla human |
| writes into Textures | `art/artwrite.py` | 155 | the only sanctioned way a script writes a texture |
| facings | `art/facing_regen.py`, `facing_scale_lint.py` | — | redraws S/N facings from the approved east view; calls `codex_image.py edit` directly |
| judges | `art_eval/runner.py`, `auto_judge.py` (timer `rm-arteval-autojudge`) | 1,137 + 806 | Opus scores, GPT second look, regen or accept |
| the rest of `art/` | 254 Python files | 60,504 total | censuses, one-off moves, flyer tools, donor regen, placeholders |

Direct callers of `codex_image.py` or `gemini_image.py` that bypass the daemon: **26** files [measured by grep;
listed in §2.3]. Callers that file queue jobs: 25 files.

### 1.2 Who calls whom, what state lives where, which sign-in home

```
 art lists, review-sheet rulings, judges' regen calls
   │  art/enact.py, art/donor_regen_jobs.py, art_eval/runner.py, art/facing_regen.py, idle_fill.py (timer)
   ▼
 fill_queue.py ──writes job JSON──▶ D:\ClaudeWork\rimmandrake\artpipe\pending\        (queue, 9p drive)
                                         │ atomic rename
                                         ▼
 rm-artpiped.service = artpiped.py ──claim──▶ active\  ──▶ done\ | failed\  (+ throughput.jsonl, logs\, status\)
   │  build_job_prompt()  ◀── common.py: HOUSE_ART_REGISTER, canon_brief(), size_clause() ◀── live def dump
   │  lease a home      ◀── common.acquire_codex_home_lease(): flock on <root>/w<i>/.artpipe_lease.lock
   │  run_worker()  ──subprocess──▶ codex_image.py generate|edit --codex-home <root>/w<i>
   │                                   │  side "wsl": ~/.local/bin/codex 0.167.0 (Linux, bubblewrap sandbox)
   │                                   │  side "win": codex.exe 0.167.0-alpha.3.2 + [windows] sandbox="elevated"
   │                                   ▼
   │                          ChatGPT sign-in in <home>/auth.json  ──▶  $imagegen (gpt-image-2)
   │                                   │  harvest from <home>/generated_images, foreign-file guard
   │  run_gemini_worker() ──▶ gemini_image.py (API key file, spend cap GeminiBudget)
   │  _check_size_and_validate() ──▶ validate_sprite.py (canvas, alpha, footprint), reskin-validate
   │  run_facts_gate(), run_legibility_gate(), canon_gate() ──▶ canon_check.py ──▶ Codex vision (~/.codex)
   │  ban_failure() ◀── art ledger bans
   ▼
 finalize_job() ──▶ manifest in done\ ; artreg.py ──▶ registry.jsonl
   ▼
 artpipe_state.py collect / art.py install ──▶ artwrite.TextureWriter ──▶ src/<Mod>/Textures/... + art ledger event
   ▼
 art_sheet.py + serve_gated.py ──▶ sheet for him (true scale) ──▶ decisions.json ──▶ art.py enact
 art_eval/auto_judge.py (timer, every 2 h) ──▶ Opus judge, GPT second look ──▶ accept | regen (back to the top)
```

Sign-in homes in use or on disk [measured 2026-11-22]:

| home | used by | sign-in |
|---|---|---|
| `/home/mandrake/.codex` | GPT consults (`gpt_consult.py`), `canon_check.py` vision, seed source for new worker homes | own lineage; refreshed 2026-11-22 23:01 UTC |
| `/home/mandrake/.codex_workers/artpipe/w0`..`w4` | the art daemon (5 workers) | five device sign-ins of 2026-11-21 03:20 to 03:24 PST (his act) |
| `~/.codex_workers/facing_regen` (absent today) | `facing_regen.py` | would be seeded from `~/.codex` on first use (a copy) |
| `C:\Users\Mandrake\.codex` | `--codex win` callers, the Codex desktop app | Windows sign-in |
| `C:\Users\Mandrake\.codex_workers\*` (28 folders, 32 `artpipe\w*`) | the Windows era of the daemon and one-off scripts; last art job there 2026-11-08 | 24 hold an `auth.json` copy |

---

## 2. The seam

### 2.1 Generic: "ask a provider to make or edit an image"

These functions know nothing about RimWorld. Each could live in a provider with no RimMandrake word in it.

| function | file | note |
|---|---|---|
| `find_codex_cli`, `base_codex_home`, `child_env`, `wsl_to_win`, `win_to_wsl`, `codex_side` | `codex_image.py` (and the copy in `codex_cli.py`) | two copies today |
| `run_codex`, `build_prompt`, `snapshot_generated`, `harvest_new`, `harvest_with_grace`, `_cache_entries`, `_preexisting_twin` | `codex_image.py` | the run and the harvest |
| `foreign_source`, `_near_copy`, `_ThumbIndex`, `_peer_outputs` | `codex_image.py` | refuses a file that another job made |
| `seed_codex_home`, `read_auth_freshness`, `resync_stale_worker_homes`, `auth_mode` | `codex_image.py` | sign-in handling (see §4: two of these copy sign-ins) |
| every `sandbox_*`, `ensure_home_sandbox`, `adopt_current_sandbox_state`, `check_sandbox_fingerprint`, `seed_sandbox_from_template`, `machine_sandbox_password_set`, `kill_orphaned_sandbox_helpers` | `codex_image.py` | Windows sandbox guards; dead weight on the Linux route |
| `acquire_codex_home_lease` | `common.py` | one live worker per home |
| `codex_sandbox_preflight`, `ensure_worker_sandbox`, `sandbox_check_report`, `sync_shared_sandbox` | `common.py` | thin wrappers over the above |
| `Detector`, `quota_state`, `_select_meter_windows`, `_looks_rate_limited`, `_is_no_image_failure` | `artpiped.py` | admission by account meter |
| `codex_grumpiness.py` | MandrakeWorkflows | reads the meter |
| `GeminiBudget`, `read_gemini_spend*`, `_looks_gemini_quota_error`, `run_gemini_worker` | `artpiped.py` | Gemini spend cap |
| `gemini_image.py`, `chroma_key.py`, `rembg_cut.py`, `pnglib.py`, `png_info` | MandrakeWorkflows | provider call and alpha tools |
| `claim_next`, `reconcile`, `repair`, `atomic_write_json`, `append_jsonl` | `artpiped.py`, `common.py` | a file queue; generic, but it need not move (§5) |

### 2.2 RimMandrake: "what to draw, and is it right"

| function or file | what is ours about it |
|---|---|
| `HOUSE_ART_REGISTER`, `scrub_stale_outline`, `has_stale_outline` | his art register rulings |
| `canon_brief`, `canon_attachment`, `canon_check.py`, `canon_gate`, `_canon_grade` | the canon library `design/RimStarWars/canon_references/` |
| `canvas_for_cells`, `measure_in_game_size`, `size_clause`, `size_warnings`, `cells_from_register_note`, `_downscale_oversized_png` | def canvases and true scale from the live def dump |
| `facing_contradictions`, `_refuse_contradicted_facing`, `_body_plan_clause`, `derive_from` handling, `facing_regen.py`, `facing_scale_lint.py` | facings |
| `load_job` (fields `rimflow_item_id`, `target_def`, `target_texpath`, `canon_na`, `install_to`) | the job schema names our ledger and defs |
| `build_job_prompt` | joins all of the above into one prompt |
| `run_validator` (→ `validate_sprite.py`), reskin-validate, `run_facts_gate`, `run_legibility_gate`, `placeholder_failure` | RimWorld sprite rules |
| `ban_failure`, `ban_reroll` | the art ledger's bans |
| `finalize_job`, `artreg.py`, `artpipe_state.py collect` | the registry and collect |
| `fill_queue.py`, `idle_fill.py`, `art/donor_regen_jobs.py`, `art/enact.py` | what is owed |
| `artledger.py`, `art.py`, `artwrite.py`, `art_sheet.py`, `serve_gated.py`, `art_eval/*` | the art ledger, install, sheets, judges |

### 2.3 What is tangled

1. **One process does both halves.** `process_codex_job` (`artpiped.py:2350`) leases a home, runs the worker,
   reads the meter, harvests, and then runs our gates and bans in the same function.
2. **The generic job schema carries our fields.** `load_job` requires `rimflow_item_id`. A generic image request
   has no such thing.
3. **Two copies of the finder.** `codex_cli.py` and `codex_image.py` (the docstring says a fix goes in both).
4. **Three repos for one call.** The daemon is in RimMandrake, the image tool in MandrakeWorkflows, the consult
   transport (with the best typed outcomes) in Dispatch.
5. **26 direct callers bypass the daemon**, each with its own sign-in home or a hard-coded one [measured]:
   `design/specs/2026-11-20-vanilla-electrical-art-home/art/gen_direct.py`,
   `skills/generating-rimworld-sprites/scripts/make_sprite.py`, `src/RimMandrake/Graffiti/art_source/manifest.py`,
   `src/RimMandrake/Utils/mockups/messy_conduit/round5_art_jobs.py` and `round6_art_jobs.py`, 11 scripts under
   `src/RimMandrake/FlowWorks/art_source/` (BridgeRedraw, Ladder ×3, LiquidContainers, PitRamp ×2, ReelTapRedraw,
   RiverWorks ×2, TankTall, Weir ×2), 7 under `src/RimStarWars/` (Armoury ×3, DesertVehicleReskin, SWBestiary ×3),
   `src/RimUtinni/MenuShell/_artsrc/gen_bg.py`, plus the two mock workers and the two path modules.
   `bridge_redraw.py` hard-codes `/mnt/c/Users/Mandrake/.codex_workers` and its `bench_lad*` homes.
6. **Two queue designs.** `codex_queue_runner.py` (MandrakeWorkflows) and `artpiped.py` both drain a file queue
   with N one-shot workers.

---

## 3. The sandbox and the modal dialog

### 3.1 What triggers the dialog (written before any act near it)

The dialog is a **Windows UAC consent prompt**. The record, in order:

- **2026-09-07** [measured then, `codex_image.py` comment]: a brand-new Codex home needs its own sandbox setup. On
  Windows the `elevated` setup creates two local accounts (`CodexSandboxOffline`, `CodexSandboxOnline`), which
  needs administrator consent, which is the UAC prompt. Two new worker homes gave two prompts. The fix then: copy
  the `.sandbox`, `.sandbox-bin`, `.sandbox-secrets` folders from one elevated home (the seed template
  `C:\Users\Mandrake\.codex_sandbox_seed`) into each new home, so `codex.exe` sees "setup already done".
- **2026-09-09, `CODEX_UAC_STORM_1`** [closed item]: Codex auto-updated 0.153.1 → 0.153.4. The seed template still
  held the old runner build, so each of 13+ new calibration homes re-ran setup: about 30 prompts. The fix: a
  version-aware seed (fingerprint of the newest `codex-command-runner-*.exe`) and a daemon preflight that turns
  the Codex channel off on a mismatch.
- **2026-10-16, `SANDBOX_UAC_ONE_STATE`** [measured then, `codex_image.py` comment]: every elevated setup
  re-provisions the two machine-wide users and **resets their passwords**. So the one valid sandbox state is
  whichever home ran setup last; every other home (the shared `~/.codex`, the seed, all workers) goes stale at that
  second and would itself re-run setup, which never converges with N homes. The fix: compare each home's
  `setup_marker.json` `created_at` with Windows' "Password last set" for those users (`net.exe user`), copy the
  current state into a home before launch (`ensure_home_sandbox`), refuse to launch if it cannot prove it, and
  `artpiped.py --sync-sandbox` to adopt the current state.
- **2026-11-10** [lesson `20261110T153542Z-BENCH-linux-codex-cli-npm-openai-codex.md`]: Linux codex-cli 0.167.0
  became the default on Archmagi. "Linux uses native paths, ~/.codex, ext4 scratch … and no Windows runtime
  adapter, sandbox templates or UAC setup." `$imagegen` worked on Linux in 30 s.

**Triggers, in one list.** `codex.exe` with `[windows] sandbox = "elevated"` raises the prompt when it launches
against a Codex home whose sandbox state is (a) missing (a new home), (b) built for another runner version (an
auto-update), or (c) older than the machine's last provisioning (another home ran setup). Running setup in one home
makes (c) true for every other home. Nothing on the Linux route can trigger it [documented: "Linux Codex inside
WSL2 uses the Linux sandbox, avoiding native Windows sandbox setup", developers.openai.com/codex/windows/wsl, via
GPT; measured: 36 Linux art jobs passed, and no setup step exists in that code path].

**A second, different dialog.** Chrome's "Allow remote debugging?" sheet belongs to Dispatch's `--transport chrome`
for GPT consults on the Mac. It is not on the art path. The chatgpt-consult skill records it.

**Live reading of the Windows side** [measured by the sister run, 3:38 PM PST]: the Windows base home
`C:\Users\Mandrake\.codex` marker matches the machine provisioning (2026-10-16T17:20:37Z vs :36Z), and its runner
build 0.166.0-alpha.5.1 is the newest in its `.sandbox-bin`. The installed `codex.exe` is 0.167.0-alpha.3.2
(desktop-app folder `5449c1f0f26f1f98`, dated 2026-11-10) [measured]. I did not launch `codex.exe`.

### 3.2 What the folders are

| folder | what writes it | what it holds | count, size [measured] |
|---|---|---|---|
| `C:\Users\Mandrake\.codex_sandbox_seed` | a hand `cp -r` on 2026-09-09, refreshed by `--sync-sandbox` | the clean seed template | 1, 403 MB |
| `.codex_sandbox_seed.bak-0.153.4`, `.bak_20261014`, `.stale-0.153.1-20260909` | hand recaptures | older seeds | 3, 304 + 313 + 8 MB |
| `.codex_sandbox_backup_20261016` | the SANDBOX_UAC_ONE_STATE repair | real backups (`seed`, `shared`) | 1, 679 MB |
| `.codex_sandbox_backup_<UTC stamp>` (169) | **`selftest_artpipe.py`** | fixture copies named `_codex_sandbox_base` and `_codex_sandbox_template` | 169, 0 to 8 KB each |

The 169: `selftest_artpipe.py` sets `RM_CODEX_SIDE=win` (line 43) and runs `--sync-sandbox` against its fixture
homes. `adopt_current_sandbox_state` writes its backup to `windows_home()` — the real `C:\Users\Mandrake` — not to
the test's temporary folder (`codex_image.py:468`). Every run leaves a pair five seconds apart (the newest pair:
2026-11-22T22:18:38Z and :43Z) [measured]. They are not "daily backups"; they are a test that reaches outside its
sandbox. Its docstring says "NEVER touch real Codex".

### 3.3 Today's workaround and what it costs

On Archmagi the workaround is now **not to use Windows Codex for art**. What remains is cost, not risk:

- About 600 lines of Windows sandbox code [measured roughly: `codex_image.py` lines 146 to 615 and 1468 to 1525, plus the `common.py` wrappers] in `codex_image.py`, its wrappers in `common.py`, and its selftests,
  all kept alive for a route the daemon no longer takes.
- 90 GB of Windows-era homes (§3.6).
- A selftest that writes into his profile on every run.
- Off Archmagi, `codex_side()` still defaults to `win` (any host not named `archmagi`), so the guards still matter
  there if art ever runs on the Desktop or SteveDesktop.

### 3.4 Is there a better way? The options

GPT consult with live web search, 2026-11-22 (question and answer: `gpt_research_answer.md` beside this file); the two
claims the plan rests on I read myself on developers.openai.com.

| option | removes the UAC prompt | removes the sign-in race | cost | what it cannot do |
|---|---|---|---|---|
| **A. Linux Codex in WSL (today)** | yes [documented: /codex/windows/wsl, via GPT; measured] | no, by itself | subscription allowance; images use it "3–5x faster" [documented: /codex/image-generation] | nothing we need; image generation under Linux `codex exec` is not in the docs but is measured here (36 jobs) |
| B. Windows `mxc` sandbox (`[features] prefer_mxc = true`) | yes where supported [documented: /codex/windows: "without administrator-approved setup, additional Windows accounts, or local firewall rules"] | no | allowance | run where the device does not support it (then it falls back to the legacy selection, which here is `elevated`) |
| C. Windows `unelevated` sandbox | yes [documented] | no | allowance | weaker network isolation; no denied-read paths |
| D. Windows `--sandbox danger-full-access` for the image worker | expected [guess ~95%; an issue reports it, no guarantee found] | no | allowance | any isolation of the worker |
| E. `codex sandbox setup --elevated` once by IT | no (it is the prompt, once per home) | no | allowance | cover many homes at once (not documented) |
| F. **One sign-in per worker** (device sign-in per home) | — | **yes** [documented: /codex/auth/ci-cd-auth "one auth.json per runner or per serialized workflow stream"] | one device sign-in per home, renewed when revoked | nothing |
| G. OpenAI Images API (`gpt-image-2` family) with an API key | yes (no Codex) | yes (no refresh tokens) | API tokens: $5/M text in, $8/M image in, $30/M image out for GPT-Image-2.6 [documented: platform pricing, via GPT; not read by me] | the agent loop (crop, resize, self-check); the daemon would do those itself; needs a key and a money decision (one of his five acts) |

**Recommendation.** A + F now. Retire the Windows image route on Archmagi after step 4 of §6. Keep B as the
documented fallback if a Windows route is needed (one attended test first). Hold G as the route for a large batch:
the Codex docs themselves say "For larger batches, set OPENAI_API_KEY … so API pricing applies" [documented:
/codex/image-generation]. G spends money, so it is his call.

### 3.5 The sign-in story (the risk that actually took the queue down)

- ChatGPT refresh tokens rotate. Two homes holding copies of one lineage cannot both refresh; the second gets
  "refresh token was already used" (`ARTPIPE_WORKER_AUTH_STALENESS_1`, 2026-09-26). An OpenAI maintainer describes
  a reuse grace of about an hour [documented: github.com/openai/codex/issues/10332, via GPT; not read by me].
- The daemon's fix for that (2026-09-26) was to **copy the freshest `auth.json` over every home**
  (`resync_stale_worker_homes`) and serialize refresh-due jobs. That is the pattern the OpenAI guide warns
  against: "Do not overwrite a persistent runner's refreshed file from the original seed on every run" and "Do not
  share the same file across concurrent jobs" [documented: /codex/auth/ci-cd-auth, read by me].
- The Linux worker homes were created 2026-11-13 12:57 PST [measured: folder birth time] and seeded by
  `seed_codex_home`, which copies `auth.json` from `~/.codex`. `~/.codex` is the GPT consults' home and refreshes
  often (last 2026-11-22 23:01 UTC) [measured]. So the workers held a copy of a lineage that another, busier client
  rotates. They worked 2026-11-13 to 2026-11-15 and were dead on 2026-11-20 [measured]. That the consult refresh
  is what killed them is the best explanation of the record [guess ~75%]; the old tokens are gone, so it cannot be
  proved now.
- Since 2026-11-21 each worker home has its own device sign-in [measured: five different `last_refresh` times,
  03:20 to 03:24 PST]. **The next daemon start will undo that**: `main()` calls `resync_stale_worker_homes`, which
  copies the freshest home over any home with a different refresh token (`codex_image.py:816`), so five
  independent sign-ins become one lineage again [measured from code; the failure itself is predicted, not seen].

### 3.6 What I would delete (nothing was deleted)

| path | size [measured] | what reads it | why it could go |
|---|---|---|---|
| `C:\Users\Mandrake\.codex_workers\artpipe\w0`..`w31` | 76 GiB | nothing on the Linux route; `sync_shared_sandbox` searches it for sandbox state on the Windows route only | Windows-era daemon homes; last job 2026-11-08 |
| `C:\Users\Mandrake\.codex_workers\` 24 one-off homes (`bench_lad1-5`, `bench_spk1-4`, `dw1-4`, `pyr0-3`, `bench_pyrelands`, `w_barrel`, `w_tank`, `sample61`, `greatbole_art`, `painterly_regen`, `artpass_mantistanis`) | 11.2 GiB | `bridge_redraw.py` (hard-coded `bench_lad*`); `gen_sea_facings.py` and `gen_matrix_parallel.py` on the `win` side | each holds a stale `auth.json` copy: a credential on disk for no use |
| `C:\Users\Mandrake\.codex_workers\artpipe_x`, `pyre_repaint` | 1.8 GiB | none found | no `auth.json`; old scratch homes |
| `C:\Users\Mandrake\.codex_workers\artpipe_authbackup_1790454277` | 32 KB | none | the 2026-09-26 auth backup; eight stale `auth.json` copies |
| `C:\Users\Mandrake\.codex_sandbox_backup_<stamp>` ×169 (not `_20261016`) | < 1 MB | none | selftest fixtures |
| `.codex_sandbox_seed.stale-0.153.1-20260909`, `.bak-0.153.4`, `.bak_20261014` | 625 MB | none | superseded seeds |

**Keep**: `C:\Users\Mandrake\.codex` (the desktop app and the Windows meter read its `sessions`),
`.codex_sandbox_seed` and `.codex_sandbox_backup_20261016` until the Windows image route is formally retired.
Deleting these is "a deletion of work that is not ours" only in the sense that they sit in his profile; they are
all agent-made. Do it as a Conductor act with `lost:` and `undo:` (undo: none for the credentials; re-sign-in).

---

## 4. Why the art queue went down, and the smallest safe fix

**State now** [measured 3:34 PM PST]: `rm-artpiped.service` is enabled; pid 1463194 started 2026-11-19 1:32 PM;
`heartbeat.json` phase IDLE, 0 pending, 5 workers, weekly Codex meter 49% used; `idle_fill.json` at 3:22 PM:
NOTHING_OWED (every remaining row refused as already rendered). The queue is up. It has little to do.

**The outage** [measured from `throughput.jsonl` and `logs/artpiped_20261119_133234_1463194.log`]:

| date (PST) | jobs | result |
|---|---|---|
| 2026-11-08 | last job on the Windows homes | ok |
| 2026-11-13 to 11-15 | 21 | ok, on the new Linux homes |
| 2026-11-20 3:51 PM | 60 | all `worker_error`: "refresh token was already used. Please log out and sign in again." |
| 2026-11-21 3:20 to 3:24 AM | — | five device sign-ins, his order ("Let's fix CODEX. Keep going, finish all five.") |
| 2026-11-21 3:27 AM | 15 | ok |

The handoff `BENCH_REBOOT_HANDOFF_202611210050` and item `RIMMANDRAKE_TEST_ART_WORKERS_SHARING_ONE_CODEX_LOGIN_NOT_FIVE`
both say "dead from 2026-11-10". The record bounds the death between 2026-11-15 5:31 PM and 2026-11-20 3:51 PM;
2026-11-10 is the day the route moved to Linux, not the day the sign-ins died.

**Why nothing rang**: no alarm reads worker sign-in health. The daemon only learns at a job, and the jobs were few.

**Smallest safe act** (not done; it touches code):
1. In `codex_image.py`, make `resync_stale_worker_homes` refuse to copy over a home that has its **own** live
   lineage (a home whose refresh token differs and whose access token is not expired), and make `seed_codex_home`
   refuse to copy `auth.json` from a home that another client uses; a new worker home gets a device sign-in
   instead (`codex login --device-auth`, which the agent may finish in his Chrome, per his 2026-11-21 ruling).
2. Add the dead-sign-in alarm the open item already specifies (red on a planted dead sign-in).
Neither touches a sandbox, a Windows home or the launch path. Risk to the dialog: none (Linux only).

---

## 5. Can Dispatch carry the generic half?

**Yes, with changes.** Reasons for yes:

- Dispatch already owns "send work to another provider and classify what came back". Its chatgpt provider has the
  typed outcomes this needs (`codex_worker.py`: `completed`, `refused`, `auth_required`, `allowance_exhausted`,
  `transport_error`, `deadline`; exits 0/2/20/21/22/23), a refusal-under-a-length-floor check, a per-credential-home
  `WorkerLock`, and a login command per profile.
- The sister item builds the one door for GPT consults there (`providers/chatgpt/bin/gpt_door.py`, draft). The
  sign-in status and renewal must be one thing for both doors: the same account, the same homes, the same refresh
  race. Two sign-in managers would recreate today's fault.
- The image call is already outside RimMandrake (MandrakeWorkflows). Moving it to Dispatch puts it beside the
  consult transport and ends the `codex_cli.py` copy.

The changes Dispatch needs:

1. **A `graphics` provider** (`providers/graphics/` or `providers/chatgpt/graphics/`), with the `codex_image.py`
   run, harvest and foreign-file guard. No RimWorld words, no owner names, no private paths (Dispatch is public and
   built by `~/dev/Lodestar/bin/publish.py`).
2. **A sign-in pool**, shared with the GPT door: N homes, each with its **own** sign-in; a lease (flock) per home;
   a three-valued probe per home (signed in / signed out / could not read); one renewal command that runs the
   device sign-in and prints the URL and code (never a token). No code path copies an `auth.json`.
3. **Native Linux transport.** Dispatch's Codex transport runs only in a Colima container on the Mac. Archmagi runs
   native Linux Codex. The provider needs a `native` transport beside `container` (the sister run meets the same
   need).
4. **Windows side as a named, off-by-default transport**, with `prefer_mxc` as its first choice and the old guards
   kept only until that is measured.

What stays in RimMandrake: the queue (`pending/active/done/failed`), `fill_queue`, `idle_fill`, the prompt builder
and every rule in §2.2, the gates, the registry, the art ledger, sheets, judges and install. The daemon becomes "our
queue and our gates around one Dispatch call".

### 5.1 Sketch of the provider interface

```text
graphics.request(spec) -> Result            # one call, one image; the caller owns queues and retries
spec:
  op            "generate" | "edit"
  prompt        str                          # already built by the caller (our rules live there)
  references    [path]                       # input images, in order
  canvas        {width, height} | None       # requested output size
  alpha         "native" | "chroma" | "none" # how transparency is made
  model, effort str | None                   # None = the provider's pinned default
  out           path                         # where the file must land
  deadline_s    float                        # a hang guard, set far above a real run
  pool          str                          # which sign-in pool ("art"), never a home path
Result:
  outcome       one of the values below
  image         path | None                  # present only for COMPLETED
  png           {width, height, color_type, has_alpha} | None
  home          pool slot name (w0..)        # for the log; never a token
  meter_before, meter_after                  # account meter readings, or UNMEASURED with its cause
  seconds, events_file, message
outcomes (each with its own exit code):
  COMPLETED            an image of ours landed at `out`
  NO_IMAGE             the provider answered and made no image (looked: empty)
  FOREIGN_IMAGE        a file landed but the guard proved it is another job's (refused)
  REFUSED              the request was refused before sending (bad spec, secret scan)
  AUTH_REQUIRED        this slot is signed out; names the renewal command
  AUTH_UNREADABLE      could not read the slot's sign-in (could not look; not "signed out")
  ALLOWANCE_EXHAUSTED  the account meter refused; carries the reset time
  SANDBOX_NOT_READY    a launch would raise the Windows setup; nothing was launched
  TRANSPORT_ERROR      the CLI failed for another named reason
  DEADLINE             the hang guard fired; a late file is still harvested first
pool.status() -> [{slot, state: signed_in|signed_out|unknown, last_refresh, cause}]
pool.renew(slot) -> prints the device URL and code; returns when the slot reads signed_in
pool.lease(n) -> context manager over n slots (flock per slot), queues when all are held
```

The four kinds of "nothing" stay apart: `NO_IMAGE` (looked, none), `AUTH_UNREADABLE` and `SANDBOX_NOT_READY`
(could not look or could not safely try), `TRANSPORT_ERROR`/`DEADLINE` (failed, cause named), and a meter that
could not be read is `UNMEASURED`, never 0.

---

## 6. Migration plan

Each step leaves the queue working. "Proof" is how the step shows the old and new paths give the same result.
Effort is a rough estimate in weighted tokens (`weighted_v2`, Opus 5.5 input = 1) [guess ±50% each].

| # | step | proof of coverage | retires | risk to the dialog | effort | needs him |
|---|---|---|---|---|---|---|
| 1 | **Stop copying sign-ins.** `resync_stale_worker_homes` never overwrites a home with its own live lineage; `seed_codex_home` never copies from `~/.codex`; a new slot gets a device sign-in. Add the dead-sign-in alarm (item `RIMMANDRAKE_TEST_ART_WORKERS_SHARING_ONE_CODEX_LOGIN_NOT_FIVE`). | a selftest red on today's code (five fixture homes with different refresh tokens are overwritten) and green after; the alarm red on a planted dead sign-in; one daemon restart afterwards leaves the five `last_refresh` values unchanged | the copy-based sign-in handling | none (Linux only) | ~300k | no (a device sign-in is the agent's act when his Chrome is signed in; the first of a sitting needs his passkey) |
| 2 | **Fix the selftest leak.** `adopt_current_sandbox_state` takes its backup root from its caller; `selftest_artpipe.py` passes a temp folder. | count of `C:\Users\Mandrake\.codex_sandbox_backup_*` is the same before and after one selftest run (today it rises by 2) | 2 junk folders per run | none: the test uses fixture homes and launches no `codex.exe`; the fix removes a write into the real profile | ~80k | no |
| 3 | **Dispatch `graphics` provider, native Linux transport**, same command line as `codex_image.py generate|edit`. `codex_image.py` becomes a thin shim that calls it. | replay 20 recorded jobs from `done\` (10 generate, 10 edit, both channels' manifests) through old and new paths on the same prompts; compare outcome class, PNG facts (size, alpha) and harvest path, not pixels (the model is not deterministic); plus every existing `selftest_codex_image.py` case run against the shim | the second copy of the finder (`codex_cli.py`), once the sister door uses the same finder | none on Linux; the Windows transport stays the old code, untouched | ~600k | no |
| 4 | **Shared sign-in pool** with the GPT door: `pool.status`, `pool.renew`, `pool.lease`. The daemon's `acquire_codex_home_lease` calls `pool.lease`. | the daemon runs 5 workers for one night on the pool; throughput.jsonl shows the same pass rate band as 2026-11-21 (15/15) and no `AUTH_*` outcome; `pool.status` read by the ops alarm | `acquire_codex_home_lease`, `read_auth_freshness` and `resync_stale_worker_homes` in RimMandrake and MandrakeWorkflows | none | ~400k | no |
| 5 | **Daemon split.** `process_codex_job` and `process_gemini_job` call `graphics.request`; the meter `Detector` and `GeminiBudget` move behind the provider; the job schema keeps our fields only in our layer. | the same 20-job replay as step 3, now through the daemon; `selftest_artpipe.py` green; one live night | ~800 lines of `artpiped.py` | none | ~900k | no |
| 6 | **Move the 26 direct callers** to `graphics.request` (or to the queue where a sheet follows). One-off scripts that will not run again are marked HISTORY instead of edited. | each moved caller runs once on its recorded input and lands a file of the same size and alpha; the grep census reads 0 direct callers | 26 private sign-in homes and the hard-coded `/mnt/c` homes | none | ~500k (Sonnet-class) | no |
| 7 | **Retire the Windows image route on Archmagi.** `--codex win` for images refuses by name and points to `prefer_mxc` as the documented way back; the sandbox guard code moves to a dormant module. Then the Conductor deletes the §3.6 list as a recorded act. | `grep` finds no image caller that selects `win` on Archmagi; disk freed is measured | ~600 lines of sandbox guards on the live path; ~90 GB | low: nothing launches `codex.exe`; deletion touches only agent-made homes, never `C:\Users\Mandrake\.codex` | ~250k | no (the deletion is a Conductor act with `lost:`/`undo:`) |
| 8 | (optional) **`mxc` test**, if a Windows route is ever wanted (another host, or Archmagi again): one attended `codex.exe exec` with `-c features.prefer_mxc=true` against a throwaway home. | the Windows sandbox log reads `mxc`, no UAC prompt is seen, one image lands | the elevated setup on that host | **real**: if `mxc` is unavailable it falls back to `elevated`, which on a fresh home is the prompt; so: attended, base home current first, one home only | ~100k | **yes**: he must be at the screen (a dialog he must see) |
| 9 | (optional) **Images API channel** for big batches. | 10 recorded jobs through both channels; the judge pass rate compared | — | none | ~400k | **yes**: an API key is a money spend |

Owner looks at art: none of steps 1 to 7 change what is drawn; they change how a request reaches the model. A
replay compares outcome classes and PNG facts, not taste. If a step changes a prompt (it must not), its art goes
to the delegated art judge (`design/RimMandrake/art_judge_brief.md`), not to him.

Total for steps 1 to 7: about 3.0M weighted tokens [guess].

---

## 7. Open questions, in order

1. Is `mxc` available on Archmagi's Windows build? Unmeasured; step 8 measures it, attended.
2. Can five workers share one sign-in safely? The open item tests it. The OpenAI guide says no for concurrent jobs;
   the measured 2026-09-26 race says no. I expect the test to fail [guess ~80%] and the answer to be "one sign-in
   per worker", which step 1 makes permanent.
3. Does anything else still seed a home by copy? `facing_regen.py` would (its home is absent today). The sister
   census counts 76 `auth.json` files and 14 token families on this machine [measured by the sister run].
4. What should SteveDesktop and the Desktop use for images? Off Archmagi, `codex_side()` defaults to `win`. Not
   studied here.

## 8. Evidence

- Queue state: `D:\ClaudeWork\rimmandrake\artpipe\status\heartbeat.json`, `idle_fill.json`, `throughput.jsonl`
  (14,562 rows), `logs\artpiped_20261119_133234_1463194.log`, `_requeued_manifests\vea_battery_v1_industrial_east.manifest.1795218705.json`.
- Sign-in reads: `read_auth_freshness` on `~/.codex` and `~/.codex_workers/artpipe/w0..w4` (no token printed).
- Ledger: OWNER events of 2026-11-21 11:41Z on `RIMMANDRAKE_TEST_ART_WORKERS_SHARING_ONE_CODEX_LOGIN_NOT_FIVE`;
  lessons `20261110T153542Z`, `20261121T114132Z`, `20261122T230832Z`; closed items `CODEX_UAC_STORM_1`,
  `CODEX_WORKER_SANDBOX_WRITE_1`, `ARTPIPE_WORKER_AUTH_STALENESS_1`.
- Primary docs read by me, 2026-11-22: developers.openai.com/codex/windows, /codex/auth/ci-cd-auth,
  /codex/image-generation. GPT consult (Linux Codex, web search) for the rest: question and answer in
  `design/specs/2026-11-22-art-pipeline-and-dispatch/gpt_research_answer.md`.
- Dispatch read at `c527c2d`: `README.md`, `CLAUDE.md`, `providers/chatgpt/codex/README.md`,
  `providers/chatgpt/bin/codex_worker.py`, `skills/chatgpt-consult/SKILL.md`.
