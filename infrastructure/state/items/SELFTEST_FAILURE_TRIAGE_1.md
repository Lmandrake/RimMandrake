## spec

`run_selftests.py` reported **56/61** for an unknown period, with five standing
failures nobody was acting on. Surfaced as a side finding by an art-generation
agent, 2026-09-18. Reproduced independently before triage — same five.

Each was classified **stale instrument** vs **real defect** by measurement, not
by which side looked more likely. Doctrine being applied: CLAUDE.md's
"Instruments that lie with a number" (seven tools returning confident wrong
counts in one session) against its "Inaccurate material is DELETED" rule.

| selftest | verdict | what it was |
|---|---|---|
| `selftest_tool_metadata` | **stale instrument** | modelled the GM gate as 2 tools; it holds 43 |
| `selftest_sound_paths` | **stale instrument** | 2 Anomaly-packed clipPaths not yet allowlisted |
| `selftest_one_path_seam` | **real defect (code)** | new script hardcoded a LocalLow path |
| `selftest_retired_mods` | **real defect (content)** | 3 dead `FindMod` blocks for a mod retired the same day |
| `selftest_art_checks` | **BOTH** | 5 fixtures stale from a legitimate art wave; 2 real regressions inside it |

## verify

`python3 src/RimMandrake/Utils/run_selftests.py` → **61/61**, 2 skipped,
0 unmeasured.

## closed — what each one actually was

**1. `selftest_tool_metadata` — stale instrument, and the most dangerous kind.**
It compared the built DLL's `[Tool]` surface against source and reported 41
tools "declared in source, absent from DLL". All 41 are legitimately compiled
out by `#if JAWA_GM_TOOLS`. The bug: the test subtracted `build.GM_TOOLS`, which
build.py's own comment describes as a two-name **spot check** for "did the `#if`
fire at all", and treated it as the complete gated set. True when the gate held
2 tools, silently false once it held 43. MEASURED: source declares 327 = **284
ungated + 43 gated**; the DLL carried exactly 284 — a perfectly healthy build
reading as catastrophic loss. Fixed by deriving the gated set from source.

🔴 **A trap inside the fix, worth the ink.** The first scanner I wrote read the
`#if` regions **line by line** and returned **0 gated tools** — which would have
"proved" the gate was empty and sent the triage down the wrong road entirely.
The attribute is routinely written across two lines (`[Tool(` then the string on
the next), so the regions must be matched as TEXT. That is now written into
`gm_gated_names_from_source`'s docstring, since the wrong answer is a confident
round number.

**2. `selftest_sound_paths` — stale instrument.** 2 of 860 clipPaths unresolved,
both from `DEEPCALM_AMBIENT_SOUND_1` (`7c0f81401`, 2026-09-18): LanternDeeps'
`RUT_DeepHum`/`RUT_DeepChorus` cite clips that ship packed in Anomaly's
`AssetBundles/`, which no loose-file walk can see. The test already has a
`VANILLA_PACKED` allowlist for exactly this, requiring each entry to name the
donor SoundDef. Verified both verbatim against the donors via RimSage
2026-09-18 — `Ambient_Undercave` and `VoidNode_Ambient` carry those clipPaths
character for character — and added them with the donors named.

**3. `selftest_one_path_seam` — real defect in new code.** `artpipe/
build_flora_legibility_sheet.py:141` (added `64023068d`) hardcoded
`/mnt/c/Users/Mandrake/.../DefDump/defs.sqlite`. Fixed the code, not the test:
it now imports `game_paths.DUMP_ROOT`. ⚠️ `DUMP_ROOT`, **not** `DEF_DUMP` —
`DEF_DUMP` resolves to the newest capture DIRECTORY underneath it, while
`defs.sqlite` sits at the top of `DefDump/`. Confirmed both spellings resolve to
the same existing file before and after.

**4. `selftest_retired_mods` — real catch, and the test was right against a
same-day human decision.** 3 `PatchOperationFindMod` blocks in
`src/RimStarWars/Armoury/Patches/Turrets_{Renames,DamageDoctrine}.xml` named
`GravTech` / `GravTech - Big cannons`, retired hours earlier by
`RESEARCH_TRIO_RETIRE_1` (`59944939f`, owner ruling 2026-09-18). That item
recorded a deliberate decision to leave them, reasoning they "become harmless
no-ops, same pattern as every other retired-donor compat guard already in this
repo". **Both halves were false.** `selftest_retired_mods.py` exists precisely
to refuse this shape — a generator re-run silently re-emits such blocks, which is
`ARMOURY_LEATHER_GEN_DESYNC_1` — and it scanned 1422 XML files and found **these
3 and nothing else**, so there was no existing pattern to be consistent with.
Deleted (CLAUDE.md: inaccurate material is deleted, git is provenance), after
confirming nothing outside the blocks referenced anything they defined
(`RSW_Jawa_TD_Turret_BeamRepeater` was declared and consumed inside one block).
The false claim in `RESEARCH_TRIO_RETIRE_1.md` was corrected in the same change.

**5. `selftest_art_checks` — stale fixtures hiding two real regressions.** 10
assertion failures, all traced to two owner-approved 2026-09-17 commits
(`9e7e773a0` "Wire approved Pyrelands creature render wave", `bd9a1b8ee`
"Gizka: dino_v5 is the locked set") that replaced the art the fixtures were
pinned against on 2026-09-15/16. Every pin was re-measured against the pre-wave
blob and the current file:

- ✅ **Legitimately fixed, fixtures updated:** all 7 `duplicate_facings` pairs
  (3 Anooba, 2 Nuna, 2 Gizka/GizkaW) — making them distinct was the wave's
  DECLARED purpose, its own commit message says "now distinct on every facing".
  `Zeer` facing-height 1.480 → **1.024**, now the cleanest row in the corpus, so
  it moved from `HEIGHT_MUST_FLAG` to `HEIGHT_MUST_PASS`. `Nuna_f_east`'s top
  clip and `Gizka_south`'s right clip both gone.
- 🔴 **Two real regressions the stale fixtures were masking**, each filed and
  **pinned rather than excused**: `ORRAY_FACING_HEIGHT_REGRESSION_1` (known-good
  → 2.488, the corpus's 2nd-worst break, `needs: owner`) and
  `ZEER_EAST_TOP_CLIP_1` (the Zeer height fix scaled all facings to ~0.98 of
  canvas and clipped the top edge — a trade, offline-fixable).

🔑 **The structural lesson, and the reason `duplicate_facings` was rewritten
rather than re-pinned.** Its 7 fixtures were all *defects someone was actively
fixing*. When they succeeded, the corpus held zero identical pairs and the check
had nothing covering it — it would have passed this selftest while being
completely broken. It now builds its own positive case (two byte-identical
copies of one sprite) AND a negative control (the same pair with one pixel
changed, which must NOT be reported, proving it matches pixels and not names),
so art churn can never silence it again.

⚠️ **Deliberately NOT fixed here**, filed as `ART_SELFTEST_CORPUS_IN_TRANSIENT_1`:
`art_checks.py --selftest` reads its whole corpus from
`Transient/pyrelands_art_review/art`, which the ~14-day Transient sweep will
delete out from under the suite around 2026-09-30. Needs a design choice, not a
patch.

## open

Nothing. The two art regressions and the corpus coupling carry their own items.

⛔ **No selftest threshold was loosened anywhere in this triage.** The 1.35
facing-height threshold, `KEYLINE_MIN_FRAC`, `OUTLINE_MAX_FLAGGED_FILES` and the
boundary rules are all untouched; the two genuine art defects are pinned as
values that fail if they move in EITHER direction, rather than absorbed into the
known-bad sets.
