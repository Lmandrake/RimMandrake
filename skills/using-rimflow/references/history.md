# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only records and lines that are no longer true. Git holds the rest.
Each line below is a record, not a rule.

## Item hygiene

- `NORTHSTAR_PROCESS_RETRO_1` named a `Transient/` notes file as a first input. The file was gone from every clone when the
  item came up. The same item's helper list was stale: two of six helpers were built under other names.
- Two items carried specs but no pointer to the prior window's `Transient/` report. The next window re-ran both analyses
  blind.
- An agent acted on a "NEXT:" note without a check and made a whole redundant review sheet. A later item of the same day
  recorded that the noted work had already been served and ruled.

## Seat identity

- Until 2026-11-01, `rimflow next --seat <OTHER SEAT>` took a lease as that seat in your clone in every case. A diagnostic
  `next --seat FOUNDRY`, before that seat was retired, wrote a lease into the local `FOUNDRY.jsonl` and then blocked
  `./publish`. Now a window that has a seat of its own gets a read (`_other_seats_read` in
  `src/RimMandrake/rimflow/cli.py`).

## Committing ledger writes

- A botched `git stash pop` landed unresolved conflict markers straight into a ledger file. That is one torn-line incident.
- Until 2026-11-23 the skill said that rimflow has "no git integration at all". `--publish` exists now.
- Until 2026-11-23 the skill said that `./publish` refuses when origin also changed OWNER.jsonl. `./publish` merges live
  shard appends now, and only warns (`src/RimMandrake/Utils/publish.py`).

## Verbs, and done means running

- Until 2026-11-23 the skill said that `bridge who` "reads/repairs the mirror". `who` reads the driver lock. An agent's
  `who` writes nothing to the ledger.
- Until 2026-11-23 the skill said that the `live` verb is "the one way out of `done`". A `verify` fail on closed work also
  reopens an item.
