---
name: rimworld-art-evaluation
description: Automated evaluation of RimMandrake game art — creatures (walkers, swimmers, flyers, catch items), plants, and machines with ports — by the owner's pipeline. Opus scores first; good is auto-accepted, really bad is regenerated, weak goes to a targeted GPT second look; GPT strong-accept accepts, anything else regenerates with reason-driven prompt edits (3 rounds, then escalate), and every decision lands on a shadow review sheet afterwards until a template earns trust. Use whenever a render or regen lands and must be judged, before ANY art reaches the owner, when a review sheet needs its prereview record, when asked "does this art look right / is this facing / perspective / pipe bore correct", when a catch item, flyer or machine assembly needs judging, when the owner overrides an agent art verdict or a live walk finds bad art the pipeline passed (that is a criteria-ledger entry), and when prompts, templates or severity rules for art judging change (re-run the regression set).
---

# RimWorld art evaluation — the owner's pipeline, with guards

Owner, 2026-10-23, verbatim (by card):

> *"Opus scores first. If it says good, auto-accept. If it says really bad, regen. If it says weak/need a call, send
> to GPT. If GPT says strong accept, accept, otherwise regen. If Human live walk notices a problem, look back and
> improve evaluation criteria or process that generated the issue."*
>
> *"Use the system right now, but while we're evaluating it, build human review sheets AFTER the process works for
> quick human feedback. Then we turn the human review off when it looks good."*
>
> Scope: *"Creatures + plants + machines"*.

Why it is built this way: a pilot of 47 subjects tested both reviewers
(`design/RimMandrake/automated_art_evaluation_design_2026-10-23.md` §6). The pilot found two things:

- **Opus sees the owner's defect almost every time but files it as polish.** Polish is a fault that does not stop an
  accept.
- **GPT rules hard but perceives less.**

So Opus looks first. A written policy sets the severity of each finding. The mood of a model never sets it.

## The pipeline in one screen

```
card (cards.py) ── incomplete? ─────────────────────────────► HOLD_INPUT (machines need the in-game assembled capture)
   │  catch item and its living animal is REGEN? ───────────► REGEN_AFTER_SOURCE
   ▼
Opus first pass (claude -p, Read only) ─ band by severity_policy.md
   │ GOOD        = 0 blocking findings + every checklist item ok (or allowed n/a) + model did not doubt      ─► ACCEPT
   │ REALLY_BAD  = a gross code, or a blocking finding at confidence ≥ 0.8                      ─► REGEN
   │ WEAK        = anything else                                                                ─► GPT
   │ owner-KEPT art: routed the same, needs a revert record (else HOLD_KEPT); a redraw is flagged
   │   "replaced your kept art" on the shadow sheet with REVERT (owner card 2026-10-23)
   ▼
GPT targeted second look (gpt_consult.py + images): answers EACH Opus concern confirmed/refuted/unclear
   │ strong_accept AND every concern refuted WITH evidence AND no blocking finding of its own   ─► ACCEPT
   │ anything else                                                                              ─► REGEN
   ▼
REGEN: the unrefuted blocking findings become explicit prompt edits (regen_prompt_edit.md); round ≤ 3, then ESCALATE
   ▼
every decision → decisions.jsonl (prompt versions, model ids read back, image shas) → SHADOW SHEET after the run
```

`references/pipeline.md` gives each guard as "owner's rule + guard", with its reason. Its routing table lists each decision,
also those that the diagram does not show. `references/history.md` holds the records behind measured claims (the first pilot's score).

## Run it

```bash
cd src/RimMandrake/Utils/art_eval
python3 runner.py brief <DEF:LETTER>...                 # departures brief for invented creatures/plants (once per subject)
python3 runner.py run --spec <spec.json>... --run-id <id> [--record] [--file-regens]
python3 runner.py run --pilot RM_Ssurr:B RM_HulduCatch:C:D --run-id <id> --test   # pilot-bundle subjects, no side effects
python3 shadow.py build <run id>                        # the owner's quick sheet AFTER the run (+ prereview.json)
python3 shadow.py ingest <sheet>.decisions.json --run <run id>   # his KEEP/OVERRIDE → shadow log + criteria ledger
python3 shadow.py status                                # per-template streak vs the turn-off threshold
python3 ledger.py add|fix|list                          # the criteria ledger (how the pipeline learns)
python3 runner.py regress [--run-id <id> --max-new 4]  # re-run the regression set after ANY prompt/template/policy change (11 rows ~13 min: run in parts, resume with --run-id)
python3 race.py run --race <tag> --rows <rows.jsonl>... --variant incumbent --variant <name>=<overlay dir>   # race prompt variants in parallel; race.py score --race <tag> --rows ...  (references/prompt_variants_2026-10-23.md)
python3 selftest_art_eval.py                            # pure parts + a mocked end-to-end run
```

- `DEF:LETTER` names one candidate picture of the pilot. A catch item is the caught animal as an object,
  a dead specimen. For a catch item, a third part names the picture of the living animal.
- **Batch size.** Give each `run` call a few subjects. One Opus call takes ~40–70 s. One GPT call takes ~25–45 s.
- **A run id is resumable.** A second call with the same run id skips each subject that the run already decided. So you can
  split a batch across calls freely. A `HOLD_ERROR` record also counts as decided
  ([references/traps.md](references/traps.md) § Run it).
- **`--test`** never counts regen rounds, never writes delegated verdicts and never files jobs.
- **A production run** does not use `--test`.
  - Add `--record`. The runner then writes `infrastructure/state/delegated/<date>/<subject>.json` (delegation_policy §3).
  - Add `--file-regens` only when the regens should actually be drawn. The runner then files the jobs with artpipe
    `fill_queue.py`. You may file for NONE/PLACEHOLDER/DONOR art (no art, a stand-in, or borrowed art) and for candidate
    art. You may file for owner-kept art only with its revert record. Install the redraw of owner-kept art with
    `art.py install --by-card`, and cite the card.
  - The spec must hold `owner_kept`. Without that field, the runner turns a REGEN into `HOLD_INPUT`.
    `fauna_spec.py` writes the field from the art ledger.
- **Timer.** `rm-arteval-autojudge.timer` runs `auto_judge.py run` every 2 hours. That pass judges finished art-eval renders.
- **Fresh rounds and owner prompts** (owner card 2026-10-24, "After round 3 fate → 1 + user improved prompts"):
  - Never hand-edit `regen_rounds.json` or decision logs.
  - To start a fresh series of rounds, run `fauna_drive.py reset <DEF>... --source-run <run> --by-card "…"`.
    - A reset is the owner's decision. The tool also takes `--owner-said` or `--per-ruling`.
    - The command appends a line to `infrastructure/state/art_eval/round_resets.jsonl`.
    - Every counter then counts the new series: the runner cap, and fauna_drive rows / candidates / install.
    - The job ids carry the series (`arteval_<DEF>_s1r1_south`).
  - Then run `fauna_drive.py rows <source run> --only <DEF>... --out <rows.json> --file`. That command files round 1.
  - His prompt text for a creature is used VERBATIM inside the template's style sentences, never reworded. Only
    `fauna_drive.py rows` uses the text; `--file-regens` and the timer do not. The text has two sources:
    `fauna_drive.py owner-prompt <DEF> --text … --owner-said …`, or a `prompt` field on an `owner_escalations_*` sheet row.
  - A free sheet `note` is never a prompt, because his notes are complaints and instructions. Record a note with
    `owner-prompt` only when the note really is prompt text.
  - `fauna_drive.py prompts` lists the owner prompts that it found.
  - If he keeps or picks the creature's art meanwhile, end the series with `fauna_drive.py stop <DEF>... --why|--by-card …`.
    Then rows/candidates/install refuse the creature.
  - Code: `src/RimMandrake/Utils/art_eval/round_series.py`.
- A spec is JSON: `subject, label, template (creature|plant|machine), module, description, invented,
  earth_body_named, body_plan, departures[], canon{must_show, engine_limits}, owner_notes[], owner_kept,
  depends_on, artpipe_job, previous_prompt, images{south,east,north,west,single,scale,living_reference,
  siblings,flight[],variants[],assembled[]}`. Schema detail: `references/schema.md`.

More traps for this section: [references/traps.md](references/traps.md) § Run it.

## Before you trust a decision

1. **The shadow sheet must show the picture that was judged.** `shadow.py build` compares
   source shas. The tool FLAGs a row when one of its judged records has no picture on that row.
   The sheet from art_sheet shows installed art and renders that it finds by name or by `--jobs`.
   `shadow.py` also passes the judged pictures to art_sheet with `--references`. Give production specs their
   `artpipe_job`, so that the render is a column.
2. **Nothing reaches the owner unread** still holds. The pipeline's look IS the prereview (`looked_by judge:<models>`).
   But the sheet itself must render. Build the sheet with `art_sheet.py` only (`rimworld-review-sheets`).
3. **A prompt, template or policy change re-runs `runner.py regress`** before the change decides anything. Never pool two
   runs on different versions. The run's `versions_key` names every prompt version, the severity policy and the creature
   template. For a plant or a machine, the template version is in `prompt_versions` of each decision, not in `versions_key`.
4. **Machines without an in-game assembled capture are held, not judged.** Captures come from a keeper save via
   `rimworld-live-review`, batched.
5. **Never live-test a flyer to get frames** (owner). Judge flight from the flip-book stills.
   - A pass from stills is not evidence about motion. Judges passed three faults: a wing baked into the plate, squash noise,
     and flesh that rips away with the wing. He saw all three at speed. The plate is the body layer without the wings.
   - Give a flyer judge the `flyer_eye_checks.py parts` sheet and every frame at full size.
   - Count only the faults that the flyer judge finds. Its pass counts for nothing.
   - Score any flyer check against `../rimworld-sprite-facings/references/flyer_truth_set.md`.

More traps for this section: [references/traps.md](references/traps.md) § Before you trust a decision.

## When the owner (or a live walk) disagrees

- Every override or walk finding is a criteria-ledger entry the same day (`ledger.py add --owner-said "<his words>"`).
- Then comes a fix. The fix names the check / prompt line / policy row that changed. The fix also adds a regression example
  (`ledger.py fix … --regression DEF:LETTER --expect ACCEPT|NOT_ACCEPT`).
- One verdict is not a pattern. An entry can stay OPEN until a second case shows the rule. A judge that you tune to one key
  (the answers of one sitting) learns only that sitting.

Format and examples: `references/criteria_ledger.md`.

## Files

| file | what |
|---|---|
| `references/pipeline.md` | the owner's rules and each guard, routing table, shadow mode, his answers to the open questions |
| `references/schema.md` | card, reviewer replies, decision record, regen job |
| `references/severity_policy.md` | every reason code: blocking / polish / gross, and the card facts that demote one (machine-read) |
| `references/templates/{creature,plant,machine,head}.md` | the class module sent to reviewers + required panels + checklist (machine-read); `head` also holds the greyscale limits of its code gate (`head_truth.py`) |
| `references/prompts/*.md` | preamble, opus_first_pass, gpt_targeted_second_look, regen_prompt_edit, departures_brief (versioned) |
| `references/criteria_ledger.md` | the learning loop |
| `references/prompt_variants_<date>.md` | variant races against owner verdicts: tables, decisions (method in the 2026-10-23 file) |
| `src/RimMandrake/Utils/art_eval/` | policy.py (pure), cards.py, runner.py, shadow.py, ledger.py, selftest_art_eval.py, and the tools named above |
| `infrastructure/state/art_eval/` | settings.json, runs/<id>/, criteria_ledger.jsonl, regression.jsonl, briefs/, shadow_log.jsonl, and the records named above |

Neighbours:

- `rimworld-review-sheets`: his page.
- `design/RimMandrake/art_judge_brief.md`: the constraint IDs that the codes cite.
- `rimworld-sprite-facings` and `generating-rimworld-sprites`: the facts that the preamble quotes.
- `rimworld-live-review`: machine captures.
- `chatgpt-consult`: GPT is guidance, never a grading key.

**Style memory**, learned from his overrides: `design/RimMandrake/art_style_memory.md`. That file is a reference for the art
judge, not a constraint. The pipeline, its timers and its judge run exactly as this skill says.

## Subagent budget — read before spawning ANY helper for this pipeline (owner, 2026-10-23)

Helpers on this stream burned the account's Opus session limit in one morning. The limits below are that day's answer. The
full text and the measured incident are in `references/subagent_budget.md`. The hard rules:

- **Every brief carries `max_turns` and `max_judge_calls`.** The default is 30 turns. The brief states the judge-call count;
  that count has no default. Both numbers count work. Never put a token or spend figure in a brief (root `CLAUDE.md`
  §No launched agent is told its spend).
- **Use a fresh helper for each batch, never one long-lived helper.**
- **Run one Opus helper at a time, and three helpers in total.**
- **A loop is one driver script, not a turn per picture.**
- **Wait with Monitor, never with polling turns.**
- **Judge each picture once per (image hash, prompt version).**
- **A prompt comparison is the incumbent + 2 variants, with ≤12 known verdicts and one round per order.** An order is one
  instruction to compare prompts. `references/subagent_budget.md` rule 11 says when a second round can start.
- **Probe the quota before judge-heavy work. Never record a 429 as a verdict.**
- **Measure every helper afterwards with `scripts/helper_cost.py`.**
