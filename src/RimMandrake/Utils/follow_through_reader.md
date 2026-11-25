# Brief: {item}

You are the fresh reader of the weekly follow-through audit, week ending {date}. You did none of the work you read.
The audit asks one question: of the needs that started in the week, how many reached their result without the owner's
hand? Page: `design/specs/2026-11-23-follow-through-audit/boundary.md`. Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md` §The measurement.

## Steps

1. Draw the sample: `python3 src/RimMandrake/Utils/follow_through.py sample --week-ending {date} --write`. It writes
   the record `{record}` and the page `{page}`. If it refuses because the record already holds verdicts, judge on
   that record. Do not draw again.
2. In the record, each stream (`talk`, `pipe`) holds up to 20 drawn needs. A stream that is `null` could not be read:
   leave it `null`. The page then says UNMEASURED with the cause.
   - A `talk` need is a message that the owner typed into the Conductor window.
   - A `pipe` need is the first `LEFT OPEN:` note of a run on its item: the next act that the run named.
3. Read each need against the real files, commits, runs and ledger events: `rimflow show <item>`, `git log`, the
   files. Do not trust a note's account of itself. Then set its `verdict` to one of these words: {verdicts}.
   - `outcome`: the need reached its result. The asked thing exists, works or was answered.
   - `disposed`: the need was dropped or answered "no", for a stated reason that is on record.
   - `moved`: only a new note, a follow-on item or a new date. The need did not reach its result.
   - `nothing`: no act at all.
   - `not_a_need`: the message or note asked for nothing. Examples: "thanks", or a reply that a later message replaces.
     Use this word sparingly. A question that he asked is a need for an answer.
   Set `evidence` to one line that a second reader can check: a path, a sha, a run unit or an event (`SEAT:tsn`).
4. Read the section "Debts ripe over a day" on the page first. For each debt, write one line under
   `"debt_classes"` in the record: `{{"<ID>": "DONE: <evidence>" | "STALE: <evidence>" | "STILL OWED: <evidence>"}}`.
5. Compute the rates: `python3 src/RimMandrake/Utils/follow_through.py rates --week-ending {date} --write`. Then
   `python3 src/RimMandrake/Utils/follow_through.py judged --week-ending {date}` must print `HOLDS`.
6. Land the two files with `./publish -m "follow-through audit {date}: headline <rate>" {record} {page}`. Close
   `{item}` with that sha.

## Limits of this work

- The level that is enough: one verdict and one evidence line per drawn need, the debt classes, the rates, and the
  page landed. Then stop.
- Do not fix what you find. Write a need that was dropped as its verdict, not as a repair. If a drop is a pipeline
  defect that nobody has filed, file it (`python3 src/RimMandrake/rimflow/cli.py file "<NAME>" ... --not-now
  "independent: this audit measures follow-through and must not change it"`). Write its id under `"findings"` in
  the record. A page line alone holds no owed work.
- Do not change the draw, the seed or the program. If the program is wrong, write `LEFT OPEN:` with the defect and
  its evidence, and stop.
