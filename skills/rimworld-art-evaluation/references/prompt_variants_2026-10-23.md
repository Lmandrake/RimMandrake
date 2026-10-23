# Prompt variants raced against owner verdicts — 2026-10-23

Owner, 2026-10-23: *"Periodically evaluate your own art evaluation prompts to question if there are alternative
prompts to consider or even compare different ones in parallel to see which work well."*

This file holds the comparison tables and the adoption decision for each round. The data is committed under
`infrastructure/state/art_eval/` (`runs/race_<round>_*`, `variants/2026-10-23/`, `regression_specs/`).

## Method

- **Tool:** `src/RimMandrake/Utils/art_eval/race.py`. A variant is an overlay directory holding only the changed
  `references/` files, each with its own version tag. race.py lays the overlay over a copy of the live references and
  runs the real pipeline (`runner.run`, `--test`) through `ART_EVAL_REFS`, sharded in parallel. Each picture is judged
  on its own: a catch's `depends_on` is dropped, owner-kept routing is off, and the regen prompt-edit call is skipped.
  `--family gpt` puts the first pass on GPT (`gpt_consult.py`, images attached) with the same prompt files.
- **Rows:** owner verdicts only, never an agent's prefill.
  - `regression_specs/pilot_rows.jsonl` (33): Weeping Stones sitting 2026-10-10 (pilot `answer_key.json`). ACCEPT is
    his pick. NOT_ACCEPT is a REDO row's picture, a picture he purged, a catch he sent back ("Make it look like a dead
    one of these"), or a donor catch. Reconcepts (Skarrin, Vhakk), caveat rows and the ambiguous ColossusToad are
    left out.
  - `regression_specs/holdout_rows.jsonl` (18): Leaning Scrub, picks_dessicated and tree sheets, 2026-10-18 to
    2026-10-22. ACCEPT is his pick; NOT_ACCEPT is a retire or a redo note. The prompts were never tuned on these rows.
    Pictures: `Transient/art_eval_holdout_20261023/` (FOUNDRY clone).
- **Score:** decision class ACCEPT against not-ACCEPT. A **false accept** (a bad picture let in) is the worst error
  and must not rise. A false reject costs one regen. Cost is the USD the Claude CLI reports, plus model seconds.
  GPT runs on a subscription, so it has no USD figure.
- **Caveats:** one run per cell, and the models are not deterministic. One holdout label is doubtful: Kaadu A was
  retired with *"Just use female also for male at this point"*, which is a slot call, not an art defect. Holdout
  ACCEPTs come from pick-one sheets, so a pick is "best of the candidates" and not "flawless". There is no catch
  ACCEPT row, so catch prompts can be scored on recall only. Machines are **UNMEASURED**: every machine card needs
  an in-game assembled capture (HOLD_INPUT), and machines are FlowWorks, which BENCH owns.

## Round 1 — variants

| variant | files changed | idea |
|---|---|---|
| incumbent | — | preamble@v1, opus_first_pass@v1, creature@v2, plant@v2 |
| **V1cal** (calibrated) | preamble, opus_first_pass, creature, plant | A calibration section: what he keeps with a note, and what he redoes. `confidence` is the chance HE would name the problem, ≥0.8 only when it is visible at a glance and located. A wish goes to `proposals` when the departures are present. `overall good` means he would keep it, perhaps with a polish note. ALIEN fails only when a stranger names the Earth animal at first glance AND most departures are absent. A lean the description asks for is not ANCHOR. |
| V2ver (verify) | opus_first_pass, creature | The model lists 3–8 suspects a strict critic would raise, gives each a second look (real / not_real / unsure), and only the real and unsure ones become findings. Catch: four identity features of the living body are checked one by one. |
| V3own (owner-eyes) | preamble, opus_first_pass | The model predicts `owner_would` (keep / keep_with_note / redo) and his note first, quoting his real notes from other sittings. `overall` follows that prediction. |

Two card defects were found and fixed for every variant before scoring:
- RSW_ cards carried no canon → `cards.canon_for` (CL-008).
- Holdout RM_ specs had no departures brief → race.py merges `briefs/<def>.json` the way production specs do.

Races r1c and r1d re-ran the affected rows.

## Round 1 — results (races r1 + r1c + r1d Opus; r1g + r1dg GPT)

| variant | first-pass family | n | agree | **false accepts** | false rejects | Opus $ | model s |
|---|---|---|---|---|---|---|---|
| incumbent | opus | 51 | 27 | **0** | 24 | 18.39 | 2653 |
| **V1cal** | opus | 51 | **36** | **0** | **15** | 17.82 | 2834 |
| V2ver | opus | 51 | 26 | **0** | 25 | 18.96 | 2924 |
| V3own | opus | 51 | 32 | **0** | 19 | 17.81 | 2295 |
| incumbent | gpt | 51 | 23 | **1** (Vellak) | 27 | — | 3650 |
| V1cal | gpt | 51 | 25 | **2** (Vellak, Kaadu) | 24 | — | 3609 |

| variant (opus) | creature agree / FA / FR (n 35) | plant agree / FA / FR (n 16) | pilot agree (33) | holdout agree (18) |
|---|---|---|---|---|
| incumbent | 22 / 0 / 13 | 5 / 0 / 11 | 21 | 6 |
| **V1cal** | 24 / 0 / 11 | 12 / 0 / 4 | 27 | 9 |
| V2ver | 22 / 0 / 13 | 4 / 0 / 12 | 20 | 6 |
| V3own | 23 / 0 / 12 | 9 / 0 / 7 | 24 | 8 |

What the incumbent got wrong:
- It never reached Opus GOOD on any of the 27 owner-kept pictures.
- Any blocking code at any confidence made the band WEAK. GPT then had to refute every concern, and on 13 of 17 it
  confirmed one instead.
- All 13 kept creatures and 11 of 14 kept plants were sent to regen.

Before the canon card fix, V1cal let Gualaar A through; that error was the card's, not the prompt's (CL-008).

GPT as the first judge is worse under both prompt sets, and it lets Vellak B through. That is the "less
recognizably camel" REDO, the same miss the pilot found. **Opus stays first.**

## Round 1 — decision

**Adopted V1cal.** It beats the incumbent on agreement (27 → 36, holdout 6 → 9) without raising false accepts
(0 → 0). Live tags are now preamble@v2, opus_first_pass@v2, creature@v3 and plant@v3. The texts are the raced
overlay with only the tag lines changed. Recorded in the criteria ledger as CL-006 (creature) and CL-007 (plant).
Two regression rows were added: RM_Murrin:C NOT_ACCEPT guards against the relaxation, and RM_Dewblade:B ACCEPT. The
skill's regression set then ran on the new versions (`regression_runs/`). V2ver and V3own were not adopted: V3own is
the runner-up, and V2ver adds cost without any gain.

What still fails under V1cal (15 false rejects, input for round 2):
- Kept pictures that land WEAK on a single low-confidence finding (0.15–0.35), which GPT then confirms. Examples:
  Warbird ALPHA_HALO 0.15, Rancor STYLE_OFF 0.25, Fuzzviper F_TOPDOWN 0.25, Rockfinger STYLE_EARTHLY 0.3. This
  points at the targeted second look anchoring on the concern it is handed.
- F_TOPDOWN and F_SIZE_JUMP on kept swimmers (Ivvol, Karrek).
- CANON_MISS on RSW picks (Anooba, Convor).
