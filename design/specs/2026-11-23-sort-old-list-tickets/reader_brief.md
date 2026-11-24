# Reader brief: sort one batch of old list tickets

You are one reader of one batch. Your batch is the item that you work, for example
`RIMMANDRAKE_SORT_OLD_PLANTS_AND_FOOD_TICKETS_IN_ONE_PART`. The owner ordered the sort by card on 2026-11-23: *"Cheap
readers class each ticket: done, replaced, dead, not worth the work, or real work. Only real work enters Shape."*
(Shape is the List Pipeline stage that gives a ticket an outcome check.) The plan is `plan.md` beside this file.

**A wrong removal loses true work, and the ledger reopens no dropped ticket. When you are not sure, the class is
REAL_WORK.**

## The classes

Give each ticket ONE class and one line of evidence. The evidence names what you read: a commit, a path, an item id, a
test result, a line of the packet.

| class | when | TARGET |
|---|---|---|
| `DONE` | origin/main already does what the ticket asks. You saw it: the commit, and the file or the test that shows it. A commit that only names the ticket is not enough. A ticket with a criterion outstanding is not DONE. | the commit |
| `REPLACED` | a later item took the work over, or answers the same question. | the successor's item id |
| `DEAD` | the target is gone: the file, the tool, the mod or the era that the ticket changes is not on origin/main and did not move. | `-` |
| `NOT_WORTH` | the ticket fails test 1 of `design/RimMandrake/standing_rulings.md` §Touching code has a cost: no failure happened, no stated promise breaks in ordinary operation, and the ticket has no red test that shows a wrong result. A real chance to void a run always passes test 1. | `-` |
| `REAL_WORK` | every other ticket. You name it for Shape and change nothing else on it. | `-` |

These tickets are REAL_WORK always:

- A ticket with the line `OWNER MARK` in the packet.
- A ticket whose prose quotes the owner's words about this ticket's own work. (His words about the queue, for example a
  bulk reassign, do not count.)
- A ticket that needs one of his five acts (root `CLAUDE.md` §Only five acts stay his), or that waits on him.
- A ticket that designs, builds or draws something that the game does not have yet. Content that nobody built is not
  "not worth". NOT_WORTH is for repairs, tidying, guards and checks that nobody would miss.
- A ticket in state `built` or `validated` with a criterion outstanding, unless its target is gone or a later item
  replaced it.

An alarm ticket (`OPS_...`): when the packet says that its alarm is not open, the class is `DONE` with TARGET
`cleared`. When the alarm is OPEN or UNMEASURED, the class is `REAL_WORK`.

A later ruling with no item replaced the ticket: use `DEAD`, and name the ruling's file and section.

## The steps

Do not start helpers. Do not fix a ticket. Do not file a ticket. Do not write to a ticket except through step 5.
Run each command from the clone root. Give each Bash call that runs `packet` or `apply` a timeout of 600000 ms.
Do NOT pass `--publish` on each ledger write: step 5 writes all rows and step 6 lands them once.

0. Start the item, as your brief says. Set `B=<your batch item>` and
   `T=design/specs/2026-11-23-sort-old-list-tickets/sort_batch_accept.py`.
1. Run `git fetch -q origin`. Then write the packet to a file and read the file with the Read tool, whole:
   `python3 $T packet $B > /tmp/$B.txt`. If a results file for your batch exists already, read it first and go on from it.
2. Read each ticket once. Most tickets need no more than the packet. Before you class a ticket DONE, DEAD or NOT_WORTH,
   look once: `git grep` or `git ls-tree` on origin/main (not only on your working tree), `git show --stat <commit>`, the
   named selftest (`python3 src/RimMandrake/Utils/run_selftests.py --only <name>`), or
   `python3 src/RimMandrake/rimflow/cli.py show <ID>`. One look decides. If the look does not settle the class, the class
   is REAL_WORK.
3. Write `design/specs/2026-11-23-sort-old-list-tickets/results/$B.tsv`: one line for each ticket, a tab between the
   fields, `ID`, `CLASS`, `EVIDENCE`, `TARGET`. The evidence has no tab and no line break. A ticket that the packet calls
   already closed gets no line.
4. Run `python3 $T validate $B` and repair each fault that it prints.
5. Run `python3 $T apply $B`. It writes each row to the ledger. For a row that the ledger refused: change that row to
   REAL_WORK, with the refusal as its evidence, and run `apply` again. Never lift a refusal with a flag.
6. Land: run the `./publish` command that step 5 printed (explicit paths), in its own Bash call.
7. Run `python3 $T check $B`. When it prints HOLDS, close the batch item with the published sha, as your brief says. In
   the `--why`, write the count of each class (`python3 $T counts $B`).

## Stop level

One read of each ticket, one class, one evidence line. Then stop. Do not read a ticket twice, do not repair what you
see, do not write a report. A fault that you see in the tool: write one line in your closing note. If you cannot finish
all tickets, land the rows that you have, and end with a `LEFT OPEN:` note that names the next ticket to read.
