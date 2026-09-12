# HUB_TAB_PUBLISHER_MIGRATION_1 — standalone dashboard publishers repoint to the hub

The hub is live and pinned: https://claude.ai/code/artifact/d066e619-b84d-479c-842f-a81b0182511c
(`DASHBOARD_HUB_ARTIFACT_1`; source `infrastructure/dashboards/hub/`). Each tab
reads ONE data file; a seat republishes ONLY its own file against that URL
(pass it as `url`; unpassed files are kept).

## spec
- artpipe: after `artreg.py render`, republish `data/art.json` (from
  `infrastructure/artpipe/art_status.json`) against the hub URL — fold into the
  render step or the daemon's post-wave hook.
- codebase-health hook: after writing `Transient/codebase_health.json`, run
  `python3 infrastructure/dashboards/hub/make_tab_data.py health` and republish
  `data/health.json`.
- maturity dashboard generator: same pattern, `maturity`.
- Retire the standalone dashboard artifacts (Repo Health Treemap etc.) only on
  the owner's word — the hub links replace them.
- 🔴 Doing ANY one of these from FOUNDRY's session completes the hub's two-seat
  no-clobber verify: after your republish, this seat's tabs must still render
  (fingerprints prove nothing else changed). Record the proof on
  DASHBOARD_HUB_ARTIFACT_1.

## verify
Each publisher republishes only its own tab file; `hub_check.py` shows all
lamps tracking their sources; two different seats have republished without
clobbering (fingerprint evidence on the hub item).

## Status 2026-09-11 (FOUNDRY) — codebase-health done, 1/3

Folded the hub republish into `src/RimMandrake/Utils/codebase_health_publish.py`:
its `build()` now calls `infrastructure/dashboards/hub/make_tab_data.py health`
right after writing `Transient/codebase_health.json`, so
`infrastructure/dashboards/hub/data/health.json` regenerates automatically on
every rebuild (best-effort — a failure there WARNs and doesn't fail the
standalone page). Actually pushing that file to the hub Artifact URL still
needs a session with the `Artifact` tool (no CLI exists for it), so the hook
prints a reminder rather than pretending to publish.

Ran the hook (`--force`), then republished ONLY `data/health.json` (files:
`{"data/health.json": ...}`) against
`https://claude.ai/code/artifact/d066e619-b84d-479c-842f-a81b0182511c` →
Version 6. `hub_check.py` confirms `health GREEN 7.0 h source ok`
(fingerprint `db8a05d6a520` matches `Transient/codebase_health.json` on
disk). Confirmed no clobber of `art`/`maturity`/`worldmap`/`sheets` by
re-reading the live artifact before and after. Full proof filed for BENCH at
`RECORD_HUB_HEALTH_PROOF_1` (the item-file write hook blocks a non-owner
editing `DASHBOARD_HUB_ARTIFACT_1.md` directly).

**Still open — artpipe and maturity are untouched by this pass:**
- artpipe: after `artreg.py render`, fold in a republish of `data/art.json`
  (from `infrastructure/artpipe/art_status.json`) — same pattern, different
  hook (the render step or the daemon's post-wave hook).
- maturity dashboard generator: same pattern as codebase-health, target
  `data/maturity.json` via `make_tab_data.py maturity`.

## Status 2026-09-12 (FOUNDRY, reclaimed) — 3/3 done, closing

**artpipe** (`src/RimMandrake/Utils/artpipe/artreg.py`, `render()`): art has no
transform step — `make_tab_data.py`'s own docstring already says
`art_status.json` "meets the contract ... published directly, not copied
here", and `hub_check.py`'s `TABS["art"]` reads that file directly. So
`render()` now just prints the same "a session still owes a republish"
reminder the other two generators print, naming the hub URL and this item —
nothing to regenerate, only to remember.

**maturity** (`src/RimMandrake/Utils/project_maturity_dashboard.py`, `main()`):
added `refresh_hub_tab()`, the same shape as
`codebase_health_publish.py`'s — calls
`infrastructure/dashboards/hub/make_tab_data.py maturity` right after writing
`Transient/project_maturity_dashboard.json`, best-effort (WARNs, doesn't fail
the standalone build), gated on `--out-dir` being the default `Transient/`
(make_tab_data.py's source path is hardcoded, so a custom `--out-dir` run must
not regenerate the hub tab from a path it didn't write to).

**Republish + no-clobber proof, this session:** ran both generators
(`project_maturity_dashboard.py --json-only`, `artreg.py render`), confirmed
`hub_check.py` GREEN/source-ok on all four lamps, then republished ONLY
`data/art.json` (from `infrastructure/artpipe/art_status.json`) and
`data/maturity.json` (from `infrastructure/dashboards/hub/data/maturity.json`)
against the hub URL → Version 11. Re-read `data/health.json` and
`data/worldmap.json` from the live artifact before and after: both
byte-identical (sha256 `49d59b38c9a2…997a` / `7dc27b3b6fda…e922`,
1219 B / 716 B, unchanged) — no clobber. `data/art.json` on the live artifact
now matches the local file exactly (sha256 `17b85884a4ab…d374`). This is the
second seat/session to republish its own tab(s) against this URL without
touching the others' — proof recorded on `DASHBOARD_HUB_ARTIFACT_1` via
`rimflow note`.

All three publishers now repoint to the hub on every regen; only the actual
push to the Artifact URL still needs a session holding the `Artifact` tool
(no CLI exists for that half) — same limitation the codebase-health pass
already noted, unchanged by this item.
