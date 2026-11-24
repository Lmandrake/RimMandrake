# BOUNDARY: the review stager's light, weather and chunk clear, Design Version 0.1.0

Code: `src/RimMandrake/Utils/stage_review.py` (`daylight`, `local_hour`, `clear`, `clear_chunks`, `settle_weather`, `main`). Item: `RIMMANDRAKE_FIX_STAGE_REVIEW_MIDDAY_IT_READS_NO_HOUR`.

## ACCEPTS
- A loaded map at any local hour, with or without free colonists, in any weather.
- `--clear` kinds `chunks`, `filth`, `buildings`, `plants`, `items`, over a rect or the whole map.

## DOES NOT SURVIVE
- A scene whose time-dated things (filth, loose ash) are what the shot is about: the clock jump ages them, always by under a day. Set the clock before the map exists.
- A map where the local hour does not set the light (a polar or tidally locked site). `daylight` reads the hour, not the glow.
- `--two-pass --settle-weather` over about 8,750 ticks: the second shot can end after 14 h. The run prints its hour.

## PROMISES (tests of the same name in `src/RimMandrake/Utils/selftest_stage_review.py`)
- **daylight-ends-between-10-and-14**: from any start hour, `--daylight` ends between 10 h and 14 h local, by a forward jump of under a day, and leaves an hour in that window alone. A `--settle` up to 4,000 ticks after it still ends in the window.
- **unread-hour-is-not-midday**: an hour that cannot be read, or a jump that did not move the clock, stops the run.
- **clear-chunks-takes-chunks-only**: `--clear chunks` destroys chunks and no other item. A chunk that shares its cell with another item stays, and the report counts it.
- **two-pass-shoots-clear-first**: `--two-pass` forces clear weather, runs its 4,000-tick transition, then takes the `_clear` shot, then the signature weather. With the default settle both shots fall in 10-14 h. A weather or a settle that did not take stops the run before a shot.
