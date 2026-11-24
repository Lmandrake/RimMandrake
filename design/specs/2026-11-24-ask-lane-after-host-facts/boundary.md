# Boundary for asking the SteveDesktop lane after the host's facts

`RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS` covers `host_facts.py`, `ask.py` and `testq.py ask` in
`src/RimMandrake/Utils/testq/`, tested in `selftest_ask_lane.py` beside them.

## ACCEPTS

An item id, a purpose chosen by the caller, the facts file (installed package ids, saves, Python packages, staged
companions, free disk, seconds left on each login) and the item's live-proof lines.

## DOES NOT SURVIVE

An unreachable host: the refresh writes nothing and reads `could not look`. The facts are never invented.

## PROMISES

- **Old facts are stale.** A missing, unreadable or over-2-hour-old file reads stale with no facts.
- **Absent is measured.** Fresh facts name a mod, save or package that is not there as `absent`, and a present one as nothing.
- **Stale never says absent.** With stale facts every need reads `could not look`.
- **No driver is CANNOT.** An item with no live-proof line, or a check marked live-check-owed, is never sent.
- **A missing tier mod is CANNOT.** The reason names the mod.
- **Stale facts are COULD NOT LOOK.** The exit code is 4; CANNOT is 3; asked is 0.
- **An ask is the whole line.** The argv carries the item, the sha and the proof ids; only `--purpose` and `--by` come from the caller.
- **A login low on time is named.** Under 3 days left names the account.

## LIMITS

- `MAX_AGE_S` is 2 hours. It guards against sending work on facts that may have changed (the hourly refresh gives one missed read of slack).
