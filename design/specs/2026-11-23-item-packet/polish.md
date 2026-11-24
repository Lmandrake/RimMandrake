# Polish: the item packet (nobody works these lines)

From the one fresh read, 2026-11-23:

- `spend_talk.strip` keeps the "needs X" phrase of a sentence that it takes out, so "It needs a bigger budget." keeps the word.
- `role_of` takes up to six words after "you are": "When you are done start one fresh reader" in a maker's brief reads as a
  fresh reader, and the maker gets no packet. Seen in 0 of 725 recorded briefs.
- Two hand-written briefs (READ_GAME_LOCK_FRESH, READ_VOID_COUNTERS_PAGE) gave a fresh read in words that `role_of` does not know.
- The steward's brief carries the fresh-reader rule, so a steward run gets no packet (about 23 recorded offline-build briefs).
- `stop_resume.note` still names `cli.py show` first.
- A missing `criteria` or `ledger` key in hand-made facts reads as not asked; `gather` always sets both.
- `_launch_locked` is tested by its source text only.
- The `git log` command that the packet prints also lists the `ledger:` commits, which the packet leaves out.
- `clean` counts a line as one that lost a sentence when the match spans two sentences and nothing was taken out.
