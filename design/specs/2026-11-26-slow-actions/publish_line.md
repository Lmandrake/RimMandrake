# The publish line: what the slot count guards, and what the door's re-runs touch (2026-11-27, 3:05 PM PST)

Item: `RIMMANDRAKE_MEASURE_PUBLISH_SLOT_DANGER_BEFORE_ANY_CHANGE` (row 7 of `one_page.md`: slot wait median 7 min, p90
39 min, 2 tree-check slots on 14 cores at load 22 and over; pipeline checks re-run 145 of 231 tests per publish).
Measurement script: `publish_line_measure.py` (same folder; read-only, runs no test).

## 1. The danger the slot count guards

`SLOTS = 2` (`design/specs/2026-11-24-treecheck-slots/boundary.md`, LIMITS). Its danger is a machine that a third door
run at once makes slower for every run: on 2026-11-24, at load 10 to 15, one door run alone took 50 s; 2, 4, 6 and 8
at once took 44, 82, 133 and 179 s each, so the throughput is flat from 2 up (about 22 s of wall per run) and each run
past 2 adds only wait and load (load 34 at 4, 68 at 8).

Not measured again today: a run past 2 makes a fresh full checkout while both kept trees are held (seen today: "a fresh
tree of its own (all 2 of the machine's kept trees are in use) (27.3 s, wrote 5229 MB)"), and the machine read load 26 to
52 the whole afternoon. A repeat of the curve would be the load that the limit guards, during the work it slows.

Today's readings (this bundle's publishes, Archmagi, load 26 to 52): slot waits 102, 520, 627, 1018 and 2493 s, and one
publish that waited 1980 s and was stopped; pipeline checks 192 to 217 tests in 991.5, 842.2 and 509.7 s; the line had
7 to 8 publishes ahead at 2:50 PM. So the line is long because each holder holds a slot for 9 to 17 min, not because 2
slots are too few for the machine.

A worse reading, by the Conductor (ps at 4:05, 4:08 and 4:13 PM PST 2026-11-27, load 30 to 48, 14 detached runs live):
11 `./publish` processes alive at 4:05 PM, ages 98 to 2,968 s; at 4:13 PM 10, ages up to 3,417 s, of which 2 held a
kept tree and 8 waited for a slot. In one kept tree, `selftest_maturation_autonomy.py` and
`selftest_maturation_dispatch.py` had each run for over 530 s. One publish ended in those 8 minutes. Before the pile-up
origin/main held a red time-budget lint (87693986ee to 4206877ef1) that refused publishers; that the refused publishers
came back together and made the pile-up is a guess, not measured. This reading says the same as the ones above: the
holders hold long, at a load that a third slot would raise.

## 2. What the door's re-runs touch (the door-reads record)

`publish_line_measure.py 25`, over the 25 newest commits on origin/main that select pipeline tests (2026-11-27, 2:55 PM):

| reason a selected test runs or not | test runs | share |
|---|---|---|
| touched: its last green run read a changed path | 350 | 10 % |
| unknown: its record ran another version of a `.py` | 1,631 | 46 % |
| unknown: its record holds a read the hook cannot see (61 tests, always) | 868 | 25 % |
| left out: its last green run read none of the change | 672 | 19 % |
| selected in all | 3,521 | |

For the newest commit (`4fdf8f066e`, a code_review_status change: 249 selected), 74 ran for "another version": 38 of
them named `maturation_now.py`. Of the 62 records that held a `maturation_now.py` other than origin's, every one held
`6733d33032`, the blob of this bundle's own maturation_now.py, which had not landed: its publish ran the tests at 2:52 PM
and was then stopped. The cause: the door-reads store is one per machine (`<RM_ROOT>/door-reads/`), keyed by test only,
and every publish's green run overwrites a test's record with the blobs of its own tree, landed or not. With 7 to 10
publishes in the line, the record of a test is often from a tree that is not the next publisher's base, and the test
runs again as "unknown". The older commits in the table overstate this share (today's records are newer than their
base); the newest commits read 74 to 77 of about 250 (30 %).

## The change this page recommends

1. Keep `SLOTS = 2`. Nothing measured today says the machine would finish more door runs with 3; the 2026-11-24 curve
   says it would not.
2. Keep a door-reads record per test and per tree, not per test only: keep the records of the last few distinct sets of
   read `.py` blobs, and let `relation` use the one whose blobs all match the base. A record of a tree that never landed
   then decides nothing and harms nothing. Expected: most of the 30 to 46 % "another version" re-runs leave.
   BUILT 2026-11-27 evening: `door_reads.py` keeps the newest `TREES = 16` records per test
   (promise `a-tree-that-never-landed-hides-no-record`, `design/specs/2026-11-26-door-reads/boundary.md`). The
   records of before decide as before until each test has been green once under the new store. At 7:30 PM PST, before it
   landed, the 3 newest selecting commits read 401 of 757 selected runs as "another version" (53 %).
3. Name the reads of the 61 tests whose records hold a read the hook cannot see (`door_reads.parse` keeps the first
   cause in `unknown`), so the door can leave them out when a change does not touch them: 25 % of the selected runs.
   Census of the store at 7:30 PM PST (68 records with an unseen read, first cause each): `git ls-files` 19, `git clone`
   11, a `systemctl` child 7, a `claude-account` child 6, `sh`/`bash` children 6, a Python child without the hook 4,
   `git cat-file` on its input 3, `git fetch` 2, and 10 kinds once each. `git ls-files`, `clone` and `fetch` do read
   the whole tree; a narrower record for them (the file list, not the contents) is a design per child. Filed as its
   own item.
4. Measure the line again after 2 and 3 with this script and the slot waits of a day.
