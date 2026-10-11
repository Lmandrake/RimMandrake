# Review-sheet lifecycle — commands, files, hand-offs

All tools are under `src/RimMandrake/Utils/art/` unless a path says otherwise. Sheets, decisions and
serve logs live in `Transient/biome_ffar/`; snapshots in `infrastructure/state/art/sheets/`.

## Files of one sheet `<name>_sheet_<date>`

| file | written by | tracked? | read by |
|---|---|---|---|
| `<name>_sheet_<date>.html` | `art_sheet.py` / `refresh_sheets.py` (gated, stamped) | yes | the owner's browser, the gate |
| `<name>_sheet_<date>.decisions.json` | the sidecar (his clicks); prefill by `art_sheet.py` only while untouched | yes | `art.py enact`, `remap_decisions.py`, the gate (req 8) |
| `infrastructure/state/art/sheets/<sheet>.snapshot.json` | `art_sheet.py` | yes | letters → pictures; `L.snapshot_by_id` recovers ruled ones from git |
| `<name>_sheet_<date>.serve.log` | the server's stdout | no (gitignored) | RimPulse, `refresh_sheets.served_url` |
| `sheets_state.json` | `refresh_sheets.py` (fingerprint per sheet) | no | `refresh_sheets.py` — missing means rebuild all once |
| `<name>.subjects.json` | `art_sheet.py --subjects` (the subject sheet's one-entry census) | yes | rebuilds, the gate (via the snapshot's `census`) |
| `img/scale_*.png` | `scale_panel.render_panel` | untracked | the sheet |

## Build

```bash
python3 src/RimMandrake/Utils/art/art_sheet.py --biome RM_Greentide [--sheet-only] [--refresh]
python3 src/RimMandrake/Utils/art/art_sheet.py --subjects RSW_WreckedSkiff RSW_BeastNest_Large --name crawler_wrecks --label "Crawler road wrecks"
python3 src/RimMandrake/Utils/art/art_sheet.py --jobs <artpipe job id>... --name <name>      # renders join their target_def's row
```

- `--sheet-only`: rewrite the HTML, never the decisions file (a sheet under live review).
- `--refresh` (biome): backfill finished renders, ingest game textures, re-run the census first.
- `--allow-failing "<reason>"`: only when the sheet being replaced renders blank; writes it UNSTAMPED with a red banner.
- A `--subjects` sheet's census is exactly the subjects named in the last command; a row he ruled that is left out
  keeps its snapshot entry, so his letters still resolve. Its panels sit on vanilla Soil (measured).
- Sizes, per kind: `python3 src/RimMandrake/Utils/art/scale_panel.py --def <defName>...` prints status, cells and source.

## Gate and classify

```bash
python3 src/RimMandrake/Utils/art/scaled_review_gate.py check <html> [--urls] [--stamp]   # all 14 requirements
python3 src/RimMandrake/Utils/art/scaled_review_gate.py all                              # every biome_ffar sheet
python3 src/RimMandrake/Utils/art/game_art.py classify <html>...                          # GAME-ART / NOT-ART + evidence
python3 src/RimMandrake/Utils/art/game_art.py deliver <html>...                           # what serve/commit/phone apply
```

## Serve, and the RimPulse hand-off

```bash
cd Transient/biome_ffar
setsid python3 ../../src/RimMandrake/Utils/art/serve_gated.py --no-open --sheet X_sheet_D.html \
    --decisions X_sheet_D.decisions.json > X_sheet_D.serve.log 2>&1 < /dev/null &
```

- RimPulse lists sheets ONLY from `Transient/biome_ffar/*.serve.log` (the last URL that answers 200). Output sent
  anywhere else makes the sheet invisible to it; a dead server's log keeps the sheet listed until stopped.
- Start servers one at a time: eight at once raced the WSL loopback relay and four tabs showed "Network error".
- `refresh_sheets.py` restarts a dead server itself (same log), so an already-served sheet needs nothing.
- Non-art sheets take the same launcher; it routes them through `nonart_sheet.py check`, which refuses one whose
  pictures are game art.
- Phone: `python3 src/RimMandrake/Utils/sheet_to_artifact.py --sheet <html> --title "Name" --out <page.html>`, then
  publish; fold the sitting back with the review-sheets skill's `merge_artifact_db.py --apply`. Refuses unstamped game art.

## Refresh

```bash
python3 src/RimMandrake/Utils/art/refresh_sheets.py [--dry-run] [--force] [--only <substr>]
```

Backfills renders, rebuilds sheets whose candidate fingerprint changed (HTML-only once he has saved decisions),
re-verifies the rest, restarts dead servers, and ends with `UNPUBLISHED: … land.sh -m "…" <paths>` — run that, or
the rebuilt sheets sit dirty in the clone. A failing rebuild keeps the previous sheet and is retried every cycle.

## Remap, enact, audit, notes

```bash
python3 src/RimMandrake/Utils/art/remap_decisions.py            # dry run: unchanged / remapped / orphaned per sheet
python3 src/RimMandrake/Utils/art/remap_decisions.py --apply    # backs each file up, rewrites only remapped letters
python3 src/RimMandrake/Utils/art/art.py enact Transient/biome_ffar/X_sheet_D.decisions.json            # the plan
python3 src/RimMandrake/Utils/art/art.py enact Transient/biome_ffar/X_sheet_D.decisions.json --apply \
    [--hold <subject>]... [--mark-done <row>]... [--no-deploy]
```

- Enact = ingest rulings → install picks → queue redraws (his note verbatim as `owner_note`) → purge ✕ (never a
  protected picture; those are CONFLICTS) → cut rows → deploy touched mods. A job that already carries his note is
  reported, never re-filed.
- Audit afterwards from the sources, not the summary: `art.py status <subject>` per row, artpipe `pending/` for the
  redraws, `git log` for the installs.
- A followed note moves to `notes_followed`; `serve_gated.py` drops a stale browser tab's re-post of it. Before acting
  on any note by hand, look for an artpipe job whose `owner_note` carries it and compare `decidedAt` / the job's
  `created`, never the row's `at` (every save bumps it).
