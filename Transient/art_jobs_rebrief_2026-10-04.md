# Stale-template art jobs: pulled and re-briefed (2026-10-04)

Item: `ART_VERSION_WRANGLING_1`. Owner ruling 2026-10-04 (question card): pull the stale-template art
jobs (the "Heavy, clean black outline" prompts) and re-brief them with no outlines, the canon brief,
the biome register, and facings derived from one approved view.

## Counts (MEASURED from `D:\Luke\dev\_artpipe`, 2026-10-04 ~07:40 PDT)

| | jobs |
|---|---|
| Jobs created since 2026-10-03 | 363 (307 on 10-03, 56 on 10-04) |
| ...carrying the black-outline clause | **245**: 203 of the 307 from 10-03, plus 42 filed 10-04 |
| Pending or active when the pull ran | **0**. `pending/` and `active/` were empty, so the daemon had already taken every one |
| Moved to `held/` | **0**. There was nothing left to hold, and no job file was moved or deleted |
| Already rendered from the stale template | **227 done + 18 failed** |
| Re-briefed and requeued | **245** (223 artlist rows) |
| Desertport jobs requeued | **0**. None of the 245 is desert-family, and the desert family stays parked until the art ledger exists |

The diagnosis counted 187 of 285. The figures above are a later re-count that includes jobs filed since then.

Stale renders by item (they stay in `done\` and `_artsrc\` as provenance):
STARWARS_JUNK_RESKIN_1 171 done + 13 failed · SEA_FISHABLES_ALIVE_IN_DEPTHS_1 30 · STATUE_ART_EXPANSION_1 16 ·
ART_REGEN_FLORA_WAVE1/2 6 + 1 · MIASMA_ROTTING_BED_CORPSES_1 1 · SUMP_CAPSTAN_DRAWJOINT_RESEARCH_1 1 ·
FLAME_STATUES_MOD_BUILD_1 3 failed · SCALD_WALKING_PASTURE_1 3 failed.

Not pulled: 47 more jobs from 10-03/04 mention a "keyline" but not a black outline, for example "soft dark keyline"
in Messy Conduit, and the Slime, Miasma, Stillsand and Cryptoforge jobs. Those jobs carry biome registers and
`derive_from`, so they were left alone. **From now on, `fill_queue` refuses any row that mentions a keyline.**

## Requeued jobs

The re-briefed artlist is `D:\Luke\dev\RimMandrake\design\RimMandrake\art_rebrief_2026-10-04_artlist.json`.
- New ids are version-bumped: `_v1`→`_v2`, `_v2`→`_v3`, and anything else gets `_v2`, for example `RSW_Junk_AncientRustedCar_01_v2`. The art registry
  strips the suffix, so each new job lands on the same asset target. Each job's style_notes name the old job it replaces.
- The 11 three-facing creatures (10 Twilight Sea fishables and the scald walker) file east as the master. North and south
  `derive_from` it, per the 2026-09-27 flow at `07676bd1d`.
- Biome registers:
  - **Cauldron** for the poison-forest flora.
  - **Sump** for the drawjoint.
  - **Twilight Sea floor** for the fishables, from `the_twilight_deep.md` §light/palette.
  - **Scald** for the walker, from `the_scald.md`.
  - **Biome-neutral** for the junk, statues and bone icon. These are stuff-tinted, or meant for every map.
- Canon briefs: 3 junk rows (droideka arm → `droid_droideka`, DSD1 cluster → `droid_dsd1`, MagnaGuard arm →
  `droid_magnaguard`). The droideka wheel-form row was left without one, because that entry's Must-show says
  "deployed form only". No other subject has a canon-library entry. The junk is vehicles, and the creatures are invented.
- The junk review sheet `Transient\junk_reskin_review_2026-10-04\` was built on the stale renders. It is now superseded
  by the `_v2` renders.

## Template diff, in words

- **`common.py`** adds:
  - `HOUSE_ART_REGISTER`: "realistic painted natural-history illustration, matte, soft painted edges, silhouette
    carried by value contrast, never cartoonish, never cute, no outlines". This is the Long Shade register kept 2026-10-02.
  - `scrub_stale_outline` and `has_stale_outline`.
  - `canon_brief(name)`: returns the canon entry's `## Visual brief` and `## Must show`.
- **`fill_queue.py`**:
  - Strips the black-outline clause and warns when it does.
  - **Refuses** any row still mentioning "black outline" or "keyline".
  - New row field `canon`: folds the brief into the job, and refuses a row naming an entry that is missing.
  - New row field `biome_register`: prepended to style_notes. A row with neither `biome_register` nor `biome_neutral` gets a warning.
  - Bakes the house register into every transparent-background job's style_notes.
  - The derive prefix now says "same edge treatment", replacing "same keyline weight".
- **`artpiped.py`** `build_job_prompt`:
  - Scrubs the clause again at render time, which covers hand-filed jobs and re-runs.
  - The readability block no longer asks for a "bold darker keyline". It is now always appended, where before it was skipped
    whenever the prompt said "painterly".
  - Adds the house register when the job lacks it.
- **Docs:**
  - `statue_mods_spec.md` common prompt head and `RM_titanoslime_spec.md` §Outline now state the register.
  - The junk artlist `starwars_junk_reskin_artlist_2026-10-03.json` is scrubbed and marked `biome_neutral`.

## What the pipeline cannot do, and caveats

- **Reference images:** the pipeline has no inspiration-image input. `reference=` triggers reskin-validate, and
  `derive_from` only attaches the job's own east master. Canon reference JPGs therefore reach the jobs only as the
  written visual brief. Adding a reference-image input that skips validation needs a daemon change.
- **The daemon runs from the FOUNDRY clone** (`/home/mandrake/rm/foundry`, unit `rm-artpiped`), so the
  `artpiped.py` change takes effect only after FOUNDRY pulls and the unit restarts. The requeued jobs do not depend
  on that restart: the prompts are already scrubbed, and the register is baked into style_notes.
- `common.py`, `fill_queue.py` and `artpiped.py` now have code-review status DIRTY. They were not marked clean.
