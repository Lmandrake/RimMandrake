# Boundary for asking the SteveDesktop lane after the host's facts

Code: `src/RimMandrake/Utils/testq/host_facts.py` and `src/RimMandrake/Utils/testq/ask.py`. Tests:
`src/RimMandrake/Utils/testq/selftest_ask_lane.py` and `src/RimMandrake/Utils/selftest_steve_visit_feed.py`.

`RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS` covers `host_facts.py`, `ask.py` and `testq.py ask` in
`src/RimMandrake/Utils/testq/`, tested in `selftest_ask_lane.py` beside them.

The gate in `visit_feed.py` (`facts_gate`) is tested in `src/RimMandrake/Utils/selftest_steve_visit_feed.py`. The timer is
`rm-host-facts.timer` (`src/RimMandrake/Utils/systemd/`), every 30 minutes; it writes `host_facts.json` in the test queue's folder.

## The danger

- A job for a mod, save, package or companion that the host lacks dies on the load. 16 of 61 asked jobs died so in 7 days.
- Until 2026-11-24 the reader read `C:\\Program Files (x86)\\Steam` through cmd.exe. No lane game uses that install: 18 mods, none of the
  tiers'. Read by the feed, it would have refused every check. The lane's games are on `D:`.

## ACCEPTS

- An item id, a purpose chosen by the caller, the facts file and the item's live-proof file (`proof_lines.py` reads it).
- The facts, per game and together: package ids, saves, Windows Python packages, staged companions, free disk, seconds left on each login.
  The logins are `login_watch.host_login_deadlines`, which also raises their alarm. This page raises no second alarm.

## DOES NOT SURVIVE

- An unreachable host: the refresh writes nothing and reads `could not look`. The facts are never invented.
- A mod that one game has and the other lacks: it counts as there. The lane refuses that job on the other game and sends it again.
- A dependency that a tier's mod pulls in by itself. Only the mods that the tier names are read.

## PROMISES

- **Old facts are stale.** A missing, unreadable or over-2-hour-old file reads stale with no facts.
- **Facts written during a pass are never read as stale.** `rm-host-facts.timer` writes the file while a `testq-tick` pass runs, so a later step of
  that pass reads facts stamped after the time that the pass took at its start. Facts stamped up to `MAX_FUTURE_S` after the caller's time read
  fresh; facts stamped further ahead (a broken clock) read `could not look`.
- **Absent is measured.** Fresh facts name a mod, save or package that is not there as `absent`, and a present one as nothing.
- **Stale never says absent.** With stale facts every need reads `could not look`.
- **An unread part is never absent.** A game, an About.xml or a package list that was not read makes its names `could not look`.
- **A refresh that fails writes nothing.** An unread companion or login part is null and named; the others stand.
- **No driver is CANNOT.** An item with no live-proof line, or a check marked live-check-owed, is never sent.
- **A missing tier mod is CANNOT.** The reason names the mod.
- **Stale facts are COULD NOT LOOK.** The exit code is 4; CANNOT is 3; a refused submit is 2; asked is 0.
- **An ask is the whole line.** The argv carries the item, the sha and the proof ids; only `--purpose` and `--by` come from the caller.
- **Each clause goes to its own list.** `live-tier` names a clause's tier; without one its list is made from `live-mods`. One submit per tier.
- **A held companion is queued, not dropped.** HOLD queues the job. The lane's admission holds it until the companion is staged.
- **A login low on time is named.** Under 3 days left names the account.
- **A check the host cannot run is not sent.** The visit feed and the filler hold a check on stale, unread or absent facts, and the step's
  record says which. A check with whole facts is sent.

## LIMITS

- `MAX_FUTURE_S` is 13860 s, 10 times the longest `testq-tick` pass measured (1386 s). It guards against facts of a broken clock read as current.
- `MAX_AGE_S` is 2 hours. It guards against sending work on facts that may have changed. The half-hour refresh leaves three missed reads.
- `_ssh` ends after 180 s: a hang guard. A read takes about 10 s.
