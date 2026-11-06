# PUSH_REFUSALS_MEASURE_BEFORE_BUYING_GITLAB

Not before 2026-11-05T00:00Z (4pm PST 11-04, the token reset), per the owner.

**Question.** Is the race to push to origin/main costly enough to justify a single lander in front of a local bare repo (GitHub as a mirror)? The owner asked about a local GitLab; the Conductor's view (2026-11-04) is that conflicts are not a hosting problem and that one serialized lander is the real fix. This item measures; it does not decide.

**Measure, over the last 7 days, per day and per writer (seat, Relentless worker, timer):**
- pushes attempted vs refused (non-fast-forward / "fetch first") and retries before success, from `./publish`, `land.sh`, `seat_sync.py`, the belt and Relentless publish acts (`publish_unknown` included);
- time spent in those retry loops;
- real content conflicts (rebase stopped on a file) vs pure ordering races, and which files.
State each source's coverage; anything with no log is UNMEASURED, never 0. Separate the GitHub outage window (2026-11-04 from ~09:37Z) from normal days.

**Done = the owner has the numbers.** One plain-language report in `D:\ClaudeWork\rimmandrake\conductor\log.md` headed `RAISE FIRST: push-refusal numbers for Mandrake`, and a line in his daily digest. ⛔ Owner: *"don't take action on the result, just make sure I find out."* No design, no filed follow-ups, no change to landing tools.
