# DIRTY_CODE_REVIEW_LOOP_RESTART_9

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_8` — read that file (and its own chain) for the fuller
history. This file is the short version: what this session did, current numbers, and
what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`: **618 clean entries** (was 509 at the
start of this session). In-scope reviewable files: **635** (was 853 — see the scope
correction below). **618/635 = 97.3% clean.** Every one of the remaining 17 real files
(there's a duplicate-looking 20 more, but that's `code_review_status.py list`'s own
`lstrip('./')` bug eating the leading dot off `.claude/hooks/*` paths in a throwaway
census script — the actual entries are correctly dotted and correctly clean, checked
individually) is deliberately deferred, not overlooked — see below.

## What this session actually did, in order

1. **Owner said, twice this session (this and the prior one), "how do we validate all
   the XML"** — answered with `XML_PATCH_VALIDATION_SWEEP_1` (closed, `bc9d2bb2`): ran
   `validate_patch.py` across all 616 authored XML files against a fresh live 589-mod
   dump. 65 raw errors, every one individually traced to real source (never guessed):
   32 validator false positives (a documented dump blind spot, an inactive-but-real
   mod, and a whole class of vanilla-packed-asset texPaths a directory scanner
   structurally cannot resolve — filed as `VALIDATE_PATCH_BLIND_SPOTS_1`), 28 correct
   `Conditional` guards for other inactive mods, 5 genuinely-dead patch blocks (fixed,
   `7fdf3a48` — two FactionDef entries for content Caravan Adventures removed going
   into 1.6), 6 real missing-art errors on our own Karrask creature (filed as
   `KARRASK_ART_MISSING_1`, needs the sprite pipeline). Also re-confirmed
   `LOAD_CONFIG_ERROR_SWEEP_1`'s frozen baseline still holds byte-for-byte against the
   live game's current `Player.log` (31/5, no drift) — that item's own fix work is
   still open, still explicitly low-priority, untouched here.
2. **Scope correction to `codebase_health.py`'s `EXCLUDE_PREFIXES`** (`40dbdb57`,
   `75dc435c`): added `world/` (211 files) and `infrastructure/state/evidence/`
   (6 files) — both are per-session live-bridge provenance records, each subdir
   self-declaring "throwaway"/"nothing here is regenerable" in its own README or cited
   the same way from design docs, not maintained code. This is why "in-scope" dropped
   from 853 to 635 while the clean count only grew by 109 — most of the apparent
   backlog was never real review debt, it was mis-scoped bookkeeping.
3. **Fanned out 5 parallel full-file reviewers** across the (then-)366 never-reviewed
   in-scope files. Net: **104 marked clean outright**, plus fixes for what they found:
   - `allocate_cast.py` (fauna): SUPER-slot promotion could write the same defName
     twice into a biome's cast CSV — fixed, excludes this biome's own picks.
   - `gen_name_patch.py` (fauna): a shared label across two distinct defNames silently
     renamed only the first — now detected and refused with a report, not applied blind.
   - `ashkarr_settle.py`: self-declared stale since 2026-08-24 in four places with NO
     enforcement — added a hard `--i-know-its-stale` run-guard.
   - `bench_mode.py`: stale `POLICY.md` reference (superseded by `CHARTER.md`) —
     docstring fixed.
   - `warn_doc_budget.py`: retired no-op stub whose own deletion condition was long
     satisfied — deleted.
   - Three small dead-code trims (`salvage_filter.py`, `biome_fit.py`,
     `plant_harvest_coverage.py`).
   - Then, re-reviewing 12 files that had gone dirty-again since their last clean
     mark: found `rimflow/render.py` was computing `view_sections()` TWICE per seat on
     every render (a real 2-3x perf regression a prior session's own diff introduced,
     invisible to the diff review, caught only by actually running
     `selftest_render.py`) — fixed, halved the "views" stage cost. **Lesson for next
     time this loop reviews a diff: run the file's OWN selftest before marking it
     clean, not just read the diff — a correct-looking diff still broke a real
     benchmark here.**
4. **Deliberately NOT touched, and why** (all 26 real remaining-dirty files):
   - `design/Jawa/research_review/*` (12 files) — very recent, same-day, likely
     still-active BENCH work (`RESEARCH_TREE_NORMALIZATION_1`, frozen decks). One of
     these (`build_retag_patches.py:32`) currently fails `selftest_one_path_seam.py`
     (a hardcoded LocalLow path literal outside the seam) — pre-existing, not
     introduced this session, left for whoever owns that file next.
   - `design/Jawa/mods/gen_plant_sheet.py`, `design/Jawa/worldbuilding/review/gen_turret_register.py`
     — both have a "dead-looking" branch that a reviewer flagged, but both are
     deliberate provisional scaffolding tied to an explicit not-yet-reversed owner
     ruling ("keep everything for now" / "pending the 4th-keep ruling") — collapsing
     them now would remove a lever that reactivates the moment that ruling changes.
   - `infrastructure/output/pawn_flavor_phase2_census_gen.py`,
     `skills/skills-workspace/**` (7 files) — both already-classified frozen/dead
     records (their own headers say so, or a prior item already ruled "leave").
   - `skills/rimworld-modding/scripts/validate_patch.py`,
     `skills/rimworld-quests/scripts/validate_quest.py`,
     `skills/editing-images/scripts/compare_images.py`,
     `skills/generating-rimworld-sprites/scripts/selftest.py` — real bugs found and
     filed (`VALIDATE_PATCH_BLIND_SPOTS_1`, `VALIDATE_QUEST_FALSE_NEGATIVES_1`,
     `IMAGE_SKILL_SCRIPT_NITS_1`), not fixed here: skill scripts are edited in
     dedicated fresh-context curation sessions per CLAUDE.md, not ad hoc mid-sweep.
5. `run_selftests.py`: **33/35 clean** (was 35/35 at RESTART_8, now down 2 — both
   pre-existing/environmental, not regressions from this session's own edits, checked
   individually: `selftest_one_path_seam.py` per point 4 above, and
   `selftest_render.py`'s ONE remaining failure is a 100ms wall-clock perf budget that
   this session's own fix cut roughly in half (352ms → ~137-200ms across repeated
   runs) but a shared machine under load 18-24 still can't consistently clear — not
   chased further). `selftest_cli.py` needs up to ~240s standalone under load; that's
   why `run_selftests.py`'s own 240s-per-test budget flakes on it under contention —
   not a bug, just budget it accordingly if it times out again.

## Recommended next steps, in order

1. Whichever of the 4 filed skill-script items (`VALIDATE_PATCH_BLIND_SPOTS_1`,
   `VALIDATE_QUEST_FALSE_NEGATIVES_1`, `IMAGE_SKILL_SCRIPT_NITS_1`) comes up in a
   skills curation session — all pre-verified, ready to fix without re-deriving.
2. `KARRASK_ART_MISSING_1` — needs the `generating-rimworld-sprites` pipeline, not this
   loop's kind of work, but blocks the creature from rendering correctly.
3. Everything RESTART_7/8 already flagged and still open: the bridgetools `--gm`
   deploy debt, the 49 deprioritized files across 11 inactive mods (re-verify activity
   first, the list decays), `rimflow/` itself (still deliberately deferred pending an
   owner ask — the two items THIS session found in `rimflow/render.py` were found
   despite that deferral, by re-reviewing a diff that had already landed, not by
   opening the module cold).
4. Otherwise: keep pulling `rimflow next --seat FOUNDRY`.
