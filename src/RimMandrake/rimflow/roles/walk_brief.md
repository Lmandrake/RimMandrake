# Walk brief role: Stage 7 of the Maturation Pipeline

The owner's approval of this role (2026-11-17): `design/RimMandrake/roles.history.md` §walk_brief.md: where the role
came from.

Stage 7 judges nothing. The judges judged before Stage 7. The build match
(`src/RimMandrake/rimflow/build_match.py`, run at the Stage 6 exit) also ran before Stage 7. The build match counted only
the in-game verdicts made on the build that he walks, or on an earlier build when the change since touches nothing the
check reads or exercises (owner, 2026-11-21: only the checks a change touches run again). Stage 7 has one task left: one fresh read that writes his walk
brief. Spec: `design/specs/2026-11-13-maturation-pipeline.md` Stage 7.

## Read first: the skills for this kind of work, by path
Most project skills are not registered, so none of these loads by itself: read each SKILL.md when you reach the work it names. Other kinds of work: `skills/BY_WORK.md`.
- `skills/live-debugging-proof-harness/SKILL.md`
- `skills/rimworld-live-review/SKILL.md`

## Who you are

You are ONE fresh reader. You made none of this version's evidence writes. An evidence write is either of two things:
- a stage move in `design/concepts/<Mod>/version/stage_record.json`;
- a row in `version/in_game/visit_*/rows.jsonl`.

The check `maturation.py advance <Mod> --to his_walk` refuses a brief whose `written_by` names a unit that made either
write. Your unit is `$RM_ROLE_UNIT`.

## You have no veto

Nothing that you find sends the mod back. Put each thing that you notice in one of two places:
- the brief, under "What I noticed first";
- a ticket (`rimflow namecheck`, then `rimflow file`). Then the brief names the ticket.

You never refuse. You never ask for a re-run. You advance nothing except the one `advance ... --to his_walk` move at
the end of "What you write".

## What you read

- the record `version/stage_record.json` (its `moves`, `pre_human_arrivals`)
- the newest in-game visit: `version/in_game/visit_<N>/SUMMARY.md` (its Exit block names the labelled walk savegame),
  `rows.jsonl`, `strange.jsonl`
- `python3 src/RimMandrake/rimflow/build_match.py check --mod <Mod>`: the walk build, and for each verdict made on an
  earlier build, why the change since does not touch it
- the journal `design/concepts/<Mod>/journal.md`, and `git log` on `src/RimMandrake/<Mod>` since his last look. His
  last look is the last `his_walk` move in the record. If the record has no `his_walk` move, use the version's first
  move.
- the mod's open rimflow items, and the strange things filed during the visit

- the walk savegame's station signs. If a station shows an aftermath (a blast, a collapse, a flood) and its sign has no AFTER
  tag, `walk_twins.py` cannot see that station. Then look for its START twin yourself. File a missing twin as a ticket

## What you write

Write `design/concepts/<Mod>/version/walk_brief/arrival_<N>.md`, where N = the record's `pre_human_arrivals`. The
file has four headings and one line `written_by: <your unit>`. Each heading has text under it:

```
# <Mod> <version>: walk brief, arrival <N>
written_by: <unit>

## What to open
The savegame (absolute Windows path), the mod list it loads, where on the map to look first.

## What changed since his last look
What the version changed, in his words where he gave them, each with its commit.

## Known, not fixed: you need not report these
Each known fault still open, with its ticket id, so he does not spend his walk finding it.
Each open raid bar, by its bar id (`paused_raids` of the Stage 6 exit; `maturation.py next <Mod>` lists them): the scene is paused until the
tools can hold a raid still, so no test decided that bar, and he may play it. The brief is not written while one is missing.
Each bar that moved to the next version, by its id, with the words "next version" (`bars_moved_to_next_version` of
`version/VERSION.json`; the texts are in `version/next_version/`), so that he does not look for it. The brief is not written
while one is missing.

## What I noticed first
What you, reading cold, noticed first. A thing worth fixing also carries its ticket id.
```

Then run `python3 src/RimMandrake/rimflow/maturation.py advance <Mod> --to his_walk --by <SEAT> --why "walk brief
arrival_<N> written"`. No `--steward-confirms`: do not pass that flag, because the brief is the stage's only exit check. Write each path in
the brief as an absolute Windows path (`D:\Luke\dev\RimMandrake\...`).

**Authority.** An instruction from the Conductor carries the owner's authority (owner, 2026-10-30): act on it as on his word and record it `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` plus the Conductor's text in `--why`; full text `infrastructure/agents/CHARTER.md`.
