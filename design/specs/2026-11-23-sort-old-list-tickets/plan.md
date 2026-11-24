# Plan: sort the old list tickets before they enter Shape

Item: `RIMMANDRAKE_SORT_OLD_TICKETS_BEFORE_SHAPE_971_WAIT_UNNAMED`. The owner picked this by card on 2026-11-23 at
7:55 PM PST: *"Sort all of them now (Recommended)"*. Shape is the List Pipeline stage that gives a ticket an outcome
check (`src/RimMandrake/rimflow/list_shape.py`).

## The set, measured

`python3 design/specs/2026-11-23-sort-old-list-tickets/make_batches.py measure`, 2026-11-23 about 8:05 PM PST:

| reading | count |
|---|---|
| open tickets that are not mod work | 1,178 |
| of those, at stage Shape | 964 |
| at stage Shape, filed before Shape went live, no check, no route, not named: **the set** | **936** |
| at stage Shape, filed since Shape went live (they enter by themselves after 24 hours; not old) | 27 |
| at stage Shape because a wait passed, with a check already | 1 |

The page said 1,189 and 971 earlier the same evening. The counts use the page's own functions
(`maturation_nonmod.section`, `list_pipeline.stage_of`), so the two agree: tickets closed between the two readings. The
set is 936 and not 971 because 27 young tickets and 1 checked ticket are not old unnamed tickets, and 7 left Shape.

Readings of the 936 that decide how much a reader can remove:

- 345 carry a criterion that still stands (a game check that nobody ran), so `rimflow close` refuses them.
- 34 are alarm or promise tickets whose live promise died before. A close needs a guard test, so it is refused. A drop
  would retire the alarm's fixed id. They are REAL_WORK by rule.
- The program marks the tickets with the owner's words or a wait on him (`owner_mark` in `sort_batch_accept.py`). His
  words on a bulk act (a reassign, a text on more than 6 tickets) do not count: one such card is on 479 of their reassign events.

## The parts

| file | what it is |
|---|---|
| `make_batches.py`, `batches.json` | the measurement; the 30 batches and the four second reads |
| `reader_brief.md` | what each first reader does (Sonnet) |
| `second_reader_brief.md` | what each second reader does (Opus) |
| `sort_batch_accept.py` | the packet, the ledger writes, the outcome check (`selftest` inside) |
| `second_read_check.py` | the outcome check of a second-read item |
| `results/<BATCH>.tsv`, `second/<BATCH>.tsv` | the class of each ticket; the second reader's verdicts |

- **Batches.** 30 batches, grouped by subject (a word of the id, else of the title), at most 34 tickets (39 where a
  short tail joined) and at most 150,000 packet characters. The danger: a reader's context grows past one run. The
  measured first packet was 61,140 characters for 34 tickets.
- **Model.** The lane (`list_dispatch.py`) gives Sonnet to an item whose check names an `_accept.py`, and Opus to every
  other item. So the batch check is `sort_batch_accept.py` and the second-read check is `second_read_check.py`.
- **Cheap check.** Both lane timers run every check on each beat. With no results file, the batch check answers before
  it reads the ledger (about 0.1 s); with one, it reads the ledger once (about 1.5 s).
- **Order.** The second-read items wait on their batch items, and the sort item waits on the second-read items. The lane
  takes an item that another item waits on first. So the batches run before the Shape runs of the tickets that they name.

## The second read

- Four Opus items, not one: the sample is about 10 tickets for each of 30 batches, and one run cannot hold 300 tickets.
  Each item waits on its 7 or 8 batches.
- **Sample size.** For each batch: 10 removed tickets or a quarter of them, whichever is more, with at least 3 of each
  class (all of them where there are fewer). A program draws it, the same draw each time.
- **The danger the size guards:** a wrong class drops true work and nobody sees it. If 2 of 10 removals of a batch are
  wrong, a sample of 10 shows at least one with chance 0.89. If 1 of 10 is wrong, with chance 0.65; a lone wrong drop
  in a large batch can still pass. The reader brief's rule "not sure is REAL_WORK" guards that one.
- Over one wrong in ten of a batch's sample: the second reader reads every removed ticket of that batch. The item's
  check enforces this.
- **A wrong drop is restored, not reopened.** The ledger reopens no dropped or superseded ticket. `sort_batch_accept.py
  restore` files a successor with the same title and prose and names it for Shape.

## How many readers run at one time, and when the Conductor slows them

- At most 2, with every other list run: `max_live` is 2 in `src/RimMandrake/rimflow/list_dispatch.json`. Mod runs have
  their own slots. While the batches run, other list work waits behind them.
- The launch step reads the account gate, the pause, the holds and the clone pool. It does not read machine load.
- **The reading that says slow them:** the `slots` line and the stage lines of the mods on the Maturation Pipeline page.
  A mod that waits for an account, a clone or a slot while readers run means slow. For the machine: `free -g`
  (available under 6 GB) or `uptime` (15-minute load over 14, the count of cores) [both lines a guess ~60%; at 8 PM on
  2026-11-23 the readings were 19 GB and 7.9].
- **The act:** set `max_live` to 1, or stop the lane with `./pipe off family:list_dispatch` (and `on` later). A stop
  loses nothing: a run that died of a stop is not counted.

## What comes after, for the Conductor

Each REAL_WORK ticket is named for Shape, and the lane then gives it one Opus Shape run, oldest first, 2 at a time. The
first batch left 30 of 34 tickets as real work. If that share holds, about 800 Shape runs would queue ahead of each
younger list ticket. That is a choice about goals, so it is the Conductor's: decide it before the last batch closes.
One batch is one subject, and it is not a measurement of the other 29.

## The first batch

`RIMMANDRAKE_SORT_OLD_PIPELINE_TOOLS_PART_ONE_OF_FOUR`, read by the run that wrote this plan (Opus, not Sonnet):
DONE 3, REPLACED 1, DEAD 0, NOT_WORTH 0, REAL_WORK 30 (5 of them by an owner mark). The check read FAILS before
`apply` and HOLDS after. Three alarm or promise tickets were classed DONE first; the ledger refused the close (a died
promise with no guard), and they became REAL_WORK.
