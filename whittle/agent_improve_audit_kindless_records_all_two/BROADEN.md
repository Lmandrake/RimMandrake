# Broaden — 2026-11-11 20:33 -0800

## The question (to GPT via `gpt_consult.py`, with the commit diff and STATEMENT.md)
Full text: `whittle/agent_improve_audit_kindless_records_all_two/evidence/broaden_question.md`. In short: here is what I
changed (kinds from a lesson's whole text, a new `item:` line, Relentless alarms' own item) and how I tested it (the
selftests, failing on the old code; 2 of 2 records measured; first line against whole text over 2391 lessons; gather old
against new at L1 for 8 days). What would a real user try that I haven't, and is there a correctness bug?

## The answer (full: `evidence/broaden_gpt_answer.out`)
1. Attribution accuracy: more coverage does not prove the kind belongs to the source item. Audit the lessons that
   gain a kind only from the whole text against independent provenance.
2. Environment lifetime: could a stale `RIMFLOW_ITEM`/`WC_ITEM` stamp the wrong item?
3. Two real bugs. (a) `item_of` took the FIRST `item:` line anywhere, so a quoted `item: X` in the lesson text beat the
   footer, and a malformed body line hid it. (b) `lessons.ITEM_ID` accepted two-word ids such as `GADGET_BUILD` that
   `agent_improve.ITEM_TOKEN` cannot read, so an explicit item silently lost to the prose. Also, `--item NONE` still let
   the prose assign a kind.

## What I tried and found
- **Bugs (a) and (b) and NONE: confirmed and fixed** (commit `991be3c29b`). `item_of` now reads only the footer
  (trailing `item:`/`home:` lines, nearest the end first). `ITEM_ID` uses ITEM_TOKEN's three-word grammar, so
  `--item GADGET_BUILD` is refused. `--item NONE` writes `item: NONE`. A footer item, including NONE or a legacy id
  with no intent word, is final: never second-guessed from the text. Covered in `selftest_lessons.py` (a quoted
  `item:` line in the text, at the end and mid-text; NONE; the two-word refusal) and `selftest_agent_improve.py`
  ("lesson kinds: footer item, NONE, kindless own item, a quoted item: line, none recorded").
- **Attribution (experiment 1), run over every lesson ever filed:** `evidence/attribution_audit.out`. For each lesson I
  asked whether its own seat wrote a ledger event on the first item it names, within 3 h of filing. First-line cases
  (the old rule): 42 of 158 corroborated (27%). Whole-text-only cases: 202 of 418 (48%). So the whole-text reading is
  no less sound than the rule it extends, but both are proxies. That is why the footer wins outright, and why the
  §4.3 paragraph now states these rates.
- **Environment lifetime (experiment 2), read from the launchers rather than run:** `WC_ITEM` is set per round on the
  runner command line (`infrastructure/whittle_claude/loop.sh:195`, `WC_ITEM="$ID" timeout ... run.py`), not exported
  into the loop shell, so it cannot outlive its round. Nothing in `src/` or `infrastructure/` sets `RIMFLOW_ITEM`; only
  `close_evidence.py` reads it. So no stale-value path exists today. A future launcher that exports one is the residual
  risk, and the precedence (RIMFLOW_ITEM first) follows close_evidence's.
- **Ordinary use:** I filed a real lesson in this round with plain `lessons.py add` (no `--item`). It got
  `item: AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO`, and the pass's own collector reads it as AUDIT
  (`evidence/ordinary_use_lesson.out`). The same output shows today's real inbox: 8 of 14 lessons come from Whittle
  loops, and all of those filed before this change read no kind.
