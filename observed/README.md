# `observed/` — evidence captured from a running game

🔑 **There is ONE `observed/`, and it is this one: `/mnt/d/Luke/dev/Rimworld/observed/`.**
The former second root at `infrastructure/state/observed/` was merged into it on
2026-08-23; a bare `observed/…` path anywhere — a `rimflow` evidence string, a queue item,
a commit — resolves here and nowhere else.

## What lives here

| | |
|---|---|
| `<date>/<subject>/` | per-experiment captures — `README.md`, `validate.txt`, the artefacts a run produced |
| `<date>/`, `logs/` | harvested `Player.log` snapshots and `*_harvest_*.txt` |
| `LIVE.md` | facts you would otherwise need a running game to learn. Published by CHECK |
| `verify/`, `build/`, `bridge/` | standing capture areas, not dated |

## 🔴 Track the manifest, never the payload

**git never forgets: a save committed once is permanent, and untracking it later shrinks
nothing.** The rules in `.gitignore` are about refusing the NEXT payload — saves, raw
logs, def dumps, extracted sprite caches, screenshots and derived reports are all ignored,
while the manifest, the `README.md` and the summary `.md` beside them are the work product
and are committed.

⇒ **Before adding a new kind of capture, add its ignore rule in the same commit.**
