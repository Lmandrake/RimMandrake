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

Why it is built this way: the 47-subject pilot (`design/RimMandrake/automated_art_evaluation_design_2026-10-23.md`
§6) found **Opus sees the owner's defect almost every time but files it as polish**, and **GPT rules hard but
perceives less**. So Opus looks first and severity comes from a written policy, not from either model's mood.

## The pipeline in one screen

```
card (cards.py) ── incomplete? ─────────────────────────────► HOLD_INPUT (machines need the in-game assembled capture)
   │  catch item and its living animal is REGEN? ───────────► REGEN_AFTER_SOURCE
   ▼
Opus first pass (claude -p, Read only) ─ band by severity_policy.md
   │ GOOD        = 0 blocking findings + every checklist item answered ok + model did not doubt  ─► ACCEPT
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

Each guard, as "owner's rule + guard", with its reason: `references/pipeline.md`.

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

- One `run` call per few subjects (each Opus call ~40–70 s, GPT ~25–45 s); a run id is **resumable** — re-running
  it skips subjects already decided, so split a batch across calls freely.
- `--test` never counts regen rounds, never writes delegated verdicts, never files jobs. Production runs drop it,
  add `--record` (writes `infrastructure/state/delegated/<date>/<subject>.json`, delegation_policy §3) and, when
  regens should actually be drawn, `--file-regens` (artpipe `fill_queue.py`; NONE/PLACEHOLDER/DONOR or candidate art,
  and owner-kept art only with its revert record — install with `art.py install --by-card` citing the card).
- **Fresh rounds and owner prompts** (owner card 2026-10-24, "After round 3 fate → 1 + user improved prompts"):
  never hand-edit `regen_rounds.json` or decision logs. `fauna_drive.py reset <DEF>... --source-run <run> --by-card
  "…"` appends `infrastructure/state/art_eval/round_resets.jsonl`; every counter (runner cap, fauna_drive rows /
  candidates / install) then counts the new series and job ids carry it (`arteval_<DEF>_s1r1_south`). Then
  `fauna_drive.py rows <source run> --only <DEF>... --out <rows.json> --file` files round 1. His prompt text for a
  creature (`fauna_drive.py owner-prompt <DEF> --text … --owner-said …`, or a note he typed on an
  `owner_escalations_*` sheet) is used VERBATIM inside the template's style sentences, never reworded; `fauna_drive.py
  prompts` lists what was found. If he keeps or picks the creature's art meanwhile, end the series with
  `fauna_drive.py stop <DEF>... --why|--by-card …` (rows/candidates/install then refuse it). Code: `src/RimMandrake/Utils/art_eval/round_series.py`.
- A spec is JSON: `subject, label, template (creature|plant|machine), module, description, invented,
  earth_body_named, body_plan, departures[], canon{must_show, engine_limits}, owner_notes[], owner_kept,
  depends_on, artpipe_job, previous_prompt, images{south,east,north,west,single,scale,living_reference,
  siblings,flight[],variants[],assembled[]}`. Schema detail: `references/schema.md`.

## Before you trust a decision

1. **The shadow sheet must show the picture that was judged.** `shadow.py build` FLAGs any row whose judged
   picture (source sha) is not on the sheet — art_sheet shows installed art and renders found by name or by
   `--jobs`. Give production specs their `artpipe_job` so the render is a column.
2. **Nothing reaches the owner unread** still holds: the pipeline's look IS the prereview (`looked_by judge:<models>`),
   but the sheet itself must render; build it with `art_sheet.py` only (`rimworld-review-sheets`).
3. **A prompt, template or policy change re-runs `runner.py regress`** before it decides anything; the run's
   `versions_key` names every prompt version, so two runs on different versions are never pooled.
4. **Machines without an in-game assembled capture are held, not judged.** Captures come from a keeper save via
   `rimworld-live-review`, batched.
5. **Never live-test a flyer to get frames** (owner): flight is judged from the flip-book stills.

## When the owner (or a live walk) disagrees

Every override or walk finding is a criteria-ledger entry the same day (`ledger.py add --owner-said "<his words>"`),
then a fix that names the check / prompt line / policy row changed and adds a regression example
(`ledger.py fix … --regression DEF:LETTER --expect ACCEPT|NOT_ACCEPT`). One verdict is not a pattern: an entry can
stay OPEN until a second case shows the rule — tuning to one key is how a judge learns a single sitting.
Format and examples: `references/criteria_ledger.md`.

## Files

| file | what |
|---|---|
| `references/pipeline.md` | the owner's rules and each guard, routing table, shadow mode, open questions |
| `references/schema.md` | card, reviewer replies, decision record, regen job |
| `references/severity_policy.md` | every reason code: blocking / polish / gross, and the card facts that demote one (machine-read) |
| `references/templates/{creature,plant,machine}.md` | the class module sent to reviewers + required panels + checklist (machine-read) |
| `references/prompts/*.md` | preamble, opus_first_pass, gpt_targeted_second_look, regen_prompt_edit, departures_brief (versioned) |
| `references/criteria_ledger.md` | the learning loop |
| `references/prompt_variants_<date>.md` | variant races against owner verdicts: tables, decisions (method in the 2026-10-23 file) |
| `src/RimMandrake/Utils/art_eval/` | policy.py (pure), cards.py, runner.py, shadow.py, ledger.py, selftest_art_eval.py |
| `infrastructure/state/art_eval/` | settings.json, runs/<id>/, criteria_ledger.jsonl, regression.jsonl, briefs/, shadow_log.jsonl |

Neighbours: `rimworld-review-sheets` (his page), `design/RimMandrake/art_judge_brief.md` (constraint IDs the codes
cite), `rimworld-sprite-facings` and `generating-rimworld-sprites` (the facts the preamble quotes),
`rimworld-live-review` (machine captures), `chatgpt-consult` (GPT is guidance, never a grading key).

## Subagent budget — read before spawning ANY helper for this pipeline (owner, 2026-10-23)

Helpers on this stream burned the account's Opus session limit in one morning. Hard rules, full text and the
measured incident in `references/subagent_budget.md`: **every brief carries `max_turns` and `max_judge_calls`
(default 30 turns; judge-call count stated, no default); fresh helper per batch, never one long-lived one; one Opus helper at a time, three total;
loops are one driver script, not a turn per picture; wait with Monitor, never polling turns; judge each picture once
per (image hash, prompt version); prompt comparison = incumbent + 2 variants, ≤12 known verdicts, one round per
order; probe quota before judge-heavy work and never record a 429 as a verdict; measure every helper afterwards with
`scripts/helper_cost.py`.**
