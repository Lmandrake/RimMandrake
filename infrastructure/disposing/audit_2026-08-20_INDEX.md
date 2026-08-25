# Cleanup audit — 2026-08-20

Four parallel audits, all read-only. Nothing was deleted or moved to produce them.
**~1.85 GB reclaimable of a 2.4 GB tree — and almost none of it is in `.git`.**

| area | report | reclaimable |
|---|---|---|
| `observed/` + `world/` | `audit_2026-08-20_observed.md` | ~1.03 GiB |
| `research/` + `vendor/` | `audit_2026-08-20_research_vendor.md` | 789 MB |
| `infrastructure/` + `design/` docs | `audit_2026-08-20_docs.md` | ~30 MB |
| scripts + strays | `audit_2026-08-20_code.md` | ~17 MB |

🔑 **The repo is not bloated. The disk is.** Every byte in the delete columns is
already gitignored and was never committed; no tracked file anywhere exceeds 50 MB.
The derived-artifact rule has been followed. This is disk hygiene.

## Blockers that must be cleared BEFORE deleting

1. 🔴 **`.gitignore` negations do not work.** It claims `scan_manifest.json` and
   `GENERATED_FROM.json` are tracked exceptions under `observed/genome/`; a later
   ignore line swallows both and `git ls-files observed/genome/` returns zero.
   **Deleting `art_cache/` today destroys the only record of which mod set produced
   it.** Fix the negations, commit the two manifests, then delete.
2. 🔴 **`vendor/mod_sources/` has no committed provenance** — 62 flattened branch
   zips, no `.git` dirs, no manifest. Branch and commit are unrecoverable once
   deleted. That missing provenance is why the stale-branch trap fired twice. Write
   `SOURCES.md` first; then 197 MB is safe to drop.
3. ⚠️ **Four bridge findings (M4 zones/gas, E1 raids) exist only in commit
   messages.** Harvest into `observed/LIVE.md` before quarantining the 35
   `bridgetools/prove_*` one-shots that produced them.
4. ⚠️ **`generating-a-world.md` contradicts the code** — it names six `world_*.py`
   as the live painter; `ashkarr_paint.py` imports none of them. Settle the doc
   before judging 8 files and 872 KB of `.npz`.

## Not what it looks like

- `review\biome_register.html` (8.6 MB) reads as derived and is **not** — no
  generator rebuilds it, and it carries per-biome owner cut annotations.
- `world\WORLDMAP_gen.rws.bak` (14.2 MB) is untracked **and unignored**. A blanket
  `git add` would put it in history permanently.
- `Utils/README.md` names only 17 of 105 scripts, so "absent from the README" is not
  evidence of anything.
