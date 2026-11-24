# Second reader brief: read a sample of the removed tickets

You are one second reader. You did not make any class that you read. Your item is one of the four second-read items in
`batches.json` (`second_reads`); it names the batches that are yours. The danger that you guard: a first reader gave a
wrong class, true work left the list, and nobody saw it.

Set `T=design/specs/2026-11-23-sort-old-list-tickets/sort_batch_accept.py`. Give each Bash call that runs `packet` or
`restore` a timeout of 600000 ms. Do not start helpers. Do not repair a ticket's work.

For each batch B of your item, one after the other:

1. `python3 $T sample B` prints the sampled rows (ID, class, evidence, target). The draw is fixed; do not choose others.
2. `python3 $T packet B --ids <each sampled ID>` prints each ticket. Read it BEFORE you weigh the first reader's
   evidence, and look at origin/main for what the class claims.
3. A row is RIGHT when the class is right by `reader_brief.md` §The classes. A row is WRONG when true work left the list:
   the work is still owed, a person would miss it, and no open item carries it. A wrong label on a ticket that had to go
   anyway (DEAD written as NOT_WORTH) is RIGHT; say so in the evidence.
4. Write `design/specs/2026-11-23-sort-old-list-tickets/second/B.tsv`: one line for each ticket read, `ID`, `RIGHT` or
   `WRONG`, and one line of evidence, a tab between. The evidence names what you looked at.
5. For each WRONG row: `python3 $T restore <ID> --why "<what is still owed>"`. The ledger reopens no closed ticket, so
   the tool files a successor with the same title and prose, and names it for Shape.
6. If more than one row in ten of the batch's sample is WRONG, read ALL removed tickets of that batch in the same way
   (the rows of `results/B.tsv` with another class than REAL_WORK). The item's check asks for this.
7. Land with `./publish` (explicit paths: the second/ files, the ledger shard, the new item prose), after each batch or
   two. Put the `./publish` in its own Bash call.

Then run `python3 design/specs/2026-11-23-sort-old-list-tickets/second_read_check.py <your item>`. When it prints HOLDS,
close the item, with the count of WRONG rows of each batch in the `--why`.

Stop level: one read of each sampled ticket, one verdict. No second pass, no report, no new findings. If you cannot
finish, land what you have and end with a `LEFT OPEN:` note that names the next batch.
