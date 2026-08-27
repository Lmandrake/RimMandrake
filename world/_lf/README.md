# `world/_lf/` — the 2026-08-26 CHECK session's working scripts

⚠️ **Mostly throwaway.** 110 one-off probe scripts written against a live game, kept only as
provenance for the evidence files in `infrastructure/state/evidence/` — each of those cites the
numbers, and these are how they were taken. Nothing here is a maintained tool and nothing else
depends on them.

🔑 **The four worth keeping, and why:**

| script | what it does |
|---|---|
| `shakedown.py` | **First-drive harness for newly deployed bridge tools.** Calls each one minimally and buckets the reply as WORKS / REFUSES / LIES? / ERROR. Read-only pass by default, `--writes` for the rest. Re-run it after any companion deploy |
| `score.py` | Scores all 44 Geological Landforms graphs against a live tile export, reading the requirement ranges straight out of the mod's own NodeCanvas XML rather than a hand-copied table |
| `gaps.py` | How far each landform gate is from firing on this planet — the "relax which field and how much" numbers |
| `census.py` | Live `jawa/` tool census, independent of any prove script |

Everything else — `c40_*`, `j4*`, `tpl2*`, `cold*`, `heat*`, `stray*`, `diag*` — is a single
question asked once. Read the matching evidence file instead.

⛔ **`live_tiles.csv` and the `*.json` here are derived** (exports and read-backs). The planet's real
bundles live in `world/` proper.
