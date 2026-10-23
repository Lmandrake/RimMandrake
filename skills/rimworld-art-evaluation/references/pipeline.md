# The pipeline — the owner's rules, each with its guard

Owner, 2026-10-23 (by card; his words): *"Opus scores first. If it says good, auto-accept. If it says really bad,
regen. If it says weak/need a call, send to GPT. If GPT says strong accept, accept, otherwise regen. If Human live
walk notices a problem, look back and improve evaluation criteria or process that generated the issue. Please
evaluate this proposal for issues and improve."* — *"Use the system right now, but while we're evaluating it, build
human review sheets AFTER the process works for quick human feedback. Then we turn the human review off when it
looks good."* — scope *"Creatures + plants + machines (Recommended)"*.

He asked for the proposal to be evaluated and improved. The seat adopted nine improvements; each is written below
as **owner's rule + guard**, with the evidence that made the guard necessary and where the code enforces it.

## 1. "If it says good, auto-accept" + good is a HIGH bar, decided by policy

- **Rule:** Opus good → accept.
- **Guard:** "good" is not the model's word for it. Band GOOD requires zero policy-blocking findings, every
  applicable checklist item answered `ok` (or an allowed `n/a`), no gross code, and the model's own overall not
  `weak`/`really_bad`. Each reason code is blocking or polish by `severity_policy.md`; the model's severity guess is
  logged beside it (`severity_disagreements`).
- **Why:** the pilot — Opus named the owner's defect on 15 of 16 REDO rows but called 7 of them minor and kept the
  picture. Severity by model mood is the failure; severity by written policy fixes it without flipping its
  genuine polish notes (owner KEEPs it also commented on).
- **Code:** `policy.opus_band`, `policy.severity`.

## 2. "If it says weak, send to GPT" + a TARGETED second look

- **Rule:** weak/need a call → GPT.
- **Guard:** GPT is not asked to re-review blind. It gets the same card and images plus Opus's specific concerns
  (each blocking finding, each unreadable checklist item, or the bare doubt) and answers each confirmed / refuted /
  unclear with evidence, plus its own findings and a verdict.
- **Why:** a blind re-review throws away what Opus saw; the pilot showed GPT perceives less (missed "too camel",
  catch/species mismatch) so it should settle named questions, not search from scratch.
- **Code:** `policy.concerns_from`, `prompts/gpt_targeted_second_look.md`.

## 3. "If GPT says strong accept, accept" + strong means every concern refuted with evidence

- **Rule:** GPT strong accept → accept; otherwise regen.
- **Guard:** strong accept = verdict `strong_accept` AND every concern `refuted` with at least
  `min_refute_evidence_chars` of evidence pointing at the picture AND no policy-blocking finding of GPT's own.
  `unsure` is not strong.
- **Code:** `policy.gpt_outcome`.

## 4. "Otherwise regen" + regen is reason-driven and capped

- **Rule:** really bad / not strong-accepted → regen.
- **Guard:** the unrefuted blocking findings (Opus's, minus what GPT refuted, plus GPT's own) become explicit,
  positively phrased prompt edits through `prompts/regen_prompt_edit.md` (a sonnet-rung call; a deterministic
  composition is the fallback). An anatomy rejection drops the old render as reference (the ulvassk lesson in
  `generating-rimworld-sprites`). **At most `max_regen_rounds` (3) per subject**, then `ESCALATE` — one line to the
  owner, not a sheet (delegation_policy §4.5).
- **Code:** `policy.regen_findings`, `policy.cap_regen`, `runner.evaluate`, `runner.regen_jobs` (fill_queue rows).

## 5. Owner-KEPT art may be redrawn — and he sees every swap after, with a revert

- **Rule:** owner card 2026-10-23 06:42: *"Kept art judged really bad: may the pipeline redraw it on its own? → Yes, but show me after"* (delegation_policy §2.3 exception).
- **Guard:** kept art routes like any other subject; a regen verdict redraws it. Only when the spec carries a
  revert record — `kept_install: [{mod, rel, sha}]`, every kept file — otherwise `HOLD_KEPT` (+ a kept-but-flagged
  line if not GOOD). A redraw is recorded `replaces_kept`, with `revert` (the `art.py install` argv lists that put the
  kept sha back); its regen job carries `install_by_card` so the install is `art.py install --by-card "<that card>"`.
  The next shadow sheet flags the row *REPLACED YOUR KEPT ART* and offers **REVERT**; `shadow.py ingest` runs the
  revert through the art ledger (dry run unless `--apply-reverts`) and counts it as a blocking override.
- **Code:** `policy.after_opus`, `policy.revert_record_ok`, `policy.revert_commands`, `runner.evaluate`,
  `shadow.revert`.

## 6. The generator never judges itself

- **Guard:** renders come from GPT image (codex imagegen); the first and deciding look is always Opus. GPT is a
  second opinion only on WEAK subjects, never the sole judge of its own family's output.

## 7. Shadow mode — his quick sheet AFTER the run

- **Rule:** *"build human review sheets AFTER the process works … then we turn the human review off when it looks
  good."*
- **Guard:** `shadow.py build <run>` makes a gated `art_sheet.py --subjects` sheet with one row per subject, the
  pipeline's decision and both reviewers' verdicts as the row's question (prefill = agent guess, KEEP / OVERRIDE
  buttons) and a `prereview.json` written from the pipeline's own look. A row whose judged picture is not on the
  sheet is FLAGged (the sheet must show what was judged). `shadow.py ingest` turns his answers into
  `shadow_log.jsonl` rows and every OVERRIDE into a criteria-ledger entry.
- **Turn-off threshold (owner card 2026-10-23: *"30 in a row"*; a setting):** per template, `off_after_consecutive_clean` (30) consecutive
  owner-reviewed subjects with no **blocking** override (he says accept→regen or regen→accept, or "other"). A polish
  override does not reset the streak. Eligibility is printed by `shadow.py status`; turning it off is his word.
  Statistical note for him: with zero misses in n independent subjects, the one-sided 95 % upper bound on the miss
  rate is about 3/n — **30 → ≤10 %, 59 → ≤5 %, 149 → ≤2 %** (GPT plan review, standard rule of three).
- **Code:** `shadow.py`, `policy.shadow_status`, `infrastructure/state/art_eval/settings.json`.

## 8. The learning loop — every miss changes a check

- **Rule:** *"If Human live walk notices a problem, look back and improve evaluation criteria or process that
  generated the issue."*
- **Guard:** every override / walk finding / disagreement with a past owner verdict → `ledger.py add`; the fix names
  the check, prompt line or policy row changed, records prompt versions after, and adds a regression example;
  `runner.py regress` re-runs every example on the current versions. Prompts carry `<!-- version: … -->` lines and
  sha256s; every decision records them. An entry may stay OPEN until a second case shows the rule.
- **Code:** `ledger.py`, `runner.regress`, `references/criteria_ledger.md`.

## 9. Catch items follow their living creature; invented creatures get required departures

- **Guard (catch):** living subjects run first; a catch whose living animal is REGEN/ESCALATE becomes
  `REGEN_AFTER_SOURCE` (the catch is redrawn from the settled living art). Otherwise the catch is judged against
  `living_reference.png` with `CATCH_WRONG` and `CATCH_POSE` blocking.
- **Why:** the owner's 8 catch REDOs were exactly the catches of species he redid the same sitting (pilot SCORE §5).
- **Guard (alien):** instead of the blunt "nameable Earth animal → REDO", each invented creature/plant gets a
  description-derived brief (`runner.py brief`, `prompts/departures_brief.md`): its nearest Earth body, whether the
  description itself names that body (`earth_body_named` demotes `STYLE_EARTHLY` to polish), and 3–5 visible
  departures the reviewer checks one by one (`DEPARTURE_MISSING`).
- **Why:** the blunt rule would have rejected Burrak/Vobbal-style subjects whose text names the Earth body (pilot
  §6.2) — and, measured in the e2e run, a plant described as "a fern" (criteria ledger CL-001).

## 10. Every decision is reproducible

Each `decisions.jsonl` record carries: prompt versions (tag + sha of preamble, first pass, GPT, regen, departures,
the template, the severity policy), the model ids **read back** from `claude -p` `modelUsage` and from
`gpt_consult.py`'s own log line (nothing names an account or a model id in code: Opus/Sonnet resolve through
`ART_EVAL_<RUNG>_MODEL` / `ANTHROPIC_DEFAULT_<RUNG>_MODEL` or the CLI alias), card and source-image sha256s, the
gates, both raw replies, and the reasons. Raw replies are also kept in the card directory under the agent storage
root.

## Routing table

| situation | decision |
|---|---|
| required panel missing (machine without assembled capture, catch without living reference) | HOLD_INPUT |
| catch, living animal REGEN / ESCALATE / waiting | REGEN_AFTER_SOURCE |
| owner-kept, no revert record | HOLD_KEPT (+ kept-but-flagged line if not GOOD) |
| owner-kept with a revert record | routed like any subject; a REGEN is flagged *replaced your kept art* + revert |
| Opus GOOD | ACCEPT |
| Opus REALLY_BAD | REGEN (round n) or ESCALATE after 3 |
| Opus WEAK → GPT strong accept (all refuted with evidence, no own blocking) | ACCEPT |
| Opus WEAK → GPT anything else | REGEN (round n) or ESCALATE after 3 |
| a reviewer reply invalid twice, or a transport failure | HOLD_ERROR (one line) |

## His answers (owner cards 2026-10-23 06:42)

1. Kept art: *"Yes, but show me after"* — §5.
2. Shadow off: *"30 in a row (Recommended)"* — §7's setting stands.
3. Override definition: *"Keep that definition (Recommended)"* — accept↔regen flips, "other" and REVERT reset the
   streak; a polish note does not.
