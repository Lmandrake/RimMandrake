# Review-sheet lifecycle — commands, files, hand-offs

All tools are under `src/RimMandrake/Utils/art/` unless a path says otherwise. Sheets, decisions and
serve logs live in `Transient/biome_ffar/`; snapshots in `infrastructure/state/art/sheets/`.

## Files of one sheet `<name>_sheet_<date>`

| file | written by | tracked? | read by |
|---|---|---|---|
| `<name>_sheet_<date>.html` | `art_sheet.py` / `refresh_sheets.py` (gated, stamped) | yes | the owner's browser, the gate |
| `<name>_sheet_<date>.decisions.json` | the sidecar (his clicks); prefill by `art_sheet.py` only while untouched | yes | `art.py enact`, `remap_decisions.py`, the gate (req 8) |
| `infrastructure/state/art/sheets/<sheet>.snapshot.json` | `art_sheet.py` | yes | letters → pictures; `L.snapshot_by_id` recovers ruled ones from git |
| `<name>_sheet_<date>.serve.log` | the server's stdout | no (gitignored) | `refresh_sheets.served_url` |
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
- **`--subjects` and `--textures` together merge the manifest rows into the subjects census** (`subjects_with_textures`), so a def-art look-over plus C#-drawn manifest art (drawbridge renders) is one sheet; `--jobs JOB=DB_key` bindings otherwise give empty rows because manifest rows carry their texPath/render_match only in the manifest. `gpt_consult.py` takes `-i/--image` and needs the `--` terminator before the stdin `-`.
- **`art_sheet --textures`: a row's `render_match` is `re.search`ed against the column label "render <family>".** A `^`-anchored pattern hides every candidate and the gate still PASSes; compare the build's sets count against candidates.
- **Reference panels:** show a row's read-only references before `_scale_for`'s early return for a row with no candidate of its own, and drop any reference whose sha already equals a column (gate req 15 forbids hiding the column, which is installed bytes). `art_eval/shadow.py` passes the judged files both as `--jobs` columns and as `--references`. `--sheet-only` leaves decisions untouched; on a drifted sheet the `snapshotId` changes and ingest resolves the old letters from the snapshot's git history.
- **To keep a render set off an `art_sheet`, removing its artpipe job from `--jobs` is not enough:** `art_sheet` also finds renders by name (`arteval_<subject>_<cand>`). Pass `--hide-sets <label substring>` and check by sha that the dropped files are absent from the built HTML. A row with more than 52 picture sets exits 1 ("letters run out"; RM_HoseReel base row; the Venomvine row folded in 79 sets from every LeaningScrub variant): `--hide-sets` each variant's spellings (dripping_venomvine, DrippingVenomvine, drippingvenomvine ...), sheet the per-look ThingStyleDef instead (RM_HoseReel_Modern, 7 sets), or purge first. The real fix for the folding is matching renders by `target_def` before the name word.
- **`art_sheet.py` drops a row whose every picture is already ruled (`droppedAllRuled`),** so a NEW per-row question (e.g. the non-canon option) never reaches the owner on rows he already finished: a new question must keep its rows live until answered (`_nc_open`).
- **Rebuilding a `--subjects` art sheet rewrites its COMMITTED snapshot `infrastructure/state/art/sheets/<X>_sheet_<D>.snapshot.json` and can re-letter columns** under an existing decisions file whose picks are letters (sluice_panning_warden: A/B singles gone, new E set). Do not commit a rebuilt snapshot for a sheet with owner picks unless `art.py remap` has run; restore with `git show HEAD:<path> > <path>`.
- **`art_sheet.py --jobs` only shows renders already in the art ledger index (`kind=artpipe` events);** finished artpipe renders are NOT indexed until `art.py backfill artpipe --budget 480` runs (1957 unindexed once; 12 Dragonsnake r1-r3 norths vanished with no warning and gate PASS). Run it before building a `--jobs` sheet and check the snapshot's labels list the jobs you named. The 26-letter column cap is filled by stale renders first: `--hide-sets` them.
- **Shadow-sheet census files (`art_eval_shadow_*.subjects.json`, `drawbridge_art.subjects.json`) store `reference_textures`/`textures_manifest` as ABSOLUTE `/home/mandrake/rm/bench/...` paths,** so a sheet rebuilt in any other clone renders bench's files, not its own. To rebuild a sheet that lives only untracked in bench: rebuild in your clone, pin html + subjects, and copy the byte-identical html + new `img/` files into bench before publishing, or bench's `seat_sync` refuses (a DIFFERENT untracked file where upstream adds one).

## Gate and classify

```bash
python3 src/RimMandrake/Utils/art/scaled_review_gate.py check <html> [--urls] [--stamp]   # all 14 requirements
python3 src/RimMandrake/Utils/art/scaled_review_gate.py all                              # every biome_ffar sheet
python3 src/RimMandrake/Utils/art/game_art.py classify <html>...                          # GAME-ART / NOT-ART + evidence
python3 src/RimMandrake/Utils/art/game_art.py deliver <html>...                           # what serve/commit/phone apply
```
- **`scaled_review_gate.py check` needs a sheet's `img/` scale panels (~150 MB for a 119-row flora sheet) and its census, and pins never commit `img/`,** so a blind checker on a fresh clone cannot rerun the gate: prove a pinned sheet with `scaled_review_gate.verify_stamp` (a body hash written only on a pass), not with `check`.

## Serve, and the hand-off

```bash
cd Transient/biome_ffar
setsid python3 ../../src/RimMandrake/Utils/art/serve_gated.py --no-open --sheet X_sheet_D.html \
    --decisions X_sheet_D.decisions.json > X_sheet_D.serve.log 2>&1 < /dev/null &
```

- Keep the `<sheet>.serve.log` beside the sheet in `Transient/` or one subfolder down: `refresh_sheets.served_url` reads the last URL
  there that answers 200 (RimPulse, which also listed it, is retired 2026-11-03; give the owner the URL yourself). Art sheets live in `Transient/biome_ffar/`; a
  non-art sheet is REFUSED there (`nonart_sheet.py`), so serve it from `Transient/` itself.
- Start servers one at a time: eight at once raced the WSL loopback relay and four tabs showed "Network error".
- `refresh_sheets.py` restarts a dead server itself (same log), so an already-served sheet needs nothing.
- Non-art sheets take the same launcher; it routes them through `nonart_sheet.py check`, which refuses one whose
  pictures are game art.
- Phone (his device is off the tailnet): `python3 src/RimMandrake/Utils/art/sheet_to_artifact.py <html> --out <dir>`
  writes `<dir>/index.html`, `<dir>/img/*` (every lane, every facing, the true-scale panels, each sprite at full
  resolution, under 16 MB) and `<dir>/files.json` (the Artifact tool's `files`). Publish it privately with the
  capabilities it prints (`db`, read admin / write owner). Read his `picks` collection back with ArtifactData into a
  file, then `python3 src/RimMandrake/Utils/art/sheet_artifact_merge.py <picks.json> <x>.decisions.json` (dry run) and
  `--apply`: written as his input via `claude-artifact-db`, savedBy `artifact-db-merge`. Both refuse unstamped or
  unread sheets; the merge refuses picks made on an older row rev (remap first).
- **A sheet that gates an item on the owner's look is pinned (`transient_pin.py add`) the moment it is filed as the gate.** Unpinned Transient decays in ~14 days; a format sheet died unseen and blocked its item for 7 weeks.

## Refresh

```bash
python3 src/RimMandrake/Utils/art/refresh_sheets.py [--dry-run] [--force] [--only <substr>]
```

Backfills renders, rebuilds sheets whose candidate fingerprint changed (HTML-only once he has saved decisions),
re-verifies the rest, restarts dead servers, and ends with `UNPUBLISHED: … land.sh -m "…" <paths>` for pinned (tracked) sheets only — run that, or
the rebuilt sheets sit dirty in the clone. A failing rebuild keeps the previous sheet and is retried every cycle.

## Remap, enact, audit, notes

```bash
python3 src/RimMandrake/Utils/art/remap_decisions.py            # dry run: unchanged / remapped / orphaned per sheet
python3 src/RimMandrake/Utils/art/remap_decisions.py --apply    # backs each file up, rewrites remapped letters, moves snapshotId to now; skips a file with orphans
python3 src/RimMandrake/Utils/art/art.py enact Transient/biome_ffar/X_sheet_D.decisions.json            # the plan
python3 src/RimMandrake/Utils/art/art.py enact Transient/biome_ffar/X_sheet_D.decisions.json --apply \
    [--hold <subject>]... [--mark-done <row>]... [--no-deploy]
```

- Enact = ingest rulings → install picks → queue redraws (his note verbatim as `owner_note`) → purge ✕ (a kept or
  live picture is archived instead, and his newest mark beats an older keep — never re-asked; `delegation_policy.md` §2.3) → cut rows → deploy touched mods. A job that already carries his note is
  reported, never re-filed.
- Audit afterwards from the sources, not the summary: `art.py status <subject>` per row, artpipe `pending/` for the
  redraws, `git log` for the installs.
- A followed note moves to `notes_followed`; `serve_gated.py` drops a stale browser tab's re-post of it. Before acting
  on any note by hand, look for an artpipe job whose `owner_note` carries it and compare `decidedAt` / the job's
  `created`, never the row's `at` (every save bumps it).
- **`art.py enact` installs a ticked variant at `<base>V_<letter>`, so a sheet column letter that matches an existing variant slot overwrites the owner's earlier pick there on every run** (GorgV_G clobbered pick M). Check existing `V_` slots before `enact --apply`.
- **`art.py enact` installs 0 files when the row's live texPath is a vanilla/Core slot** (Cauldron soils used `Terrain/Surfaces/Soil`): `art install` the pick to a new mod-owned rel path and repoint the def's texturePath.
- **`art.py enact` and `art.py status` do not understand a `Graphic_Random` folder pool:** enact refuses to retire the old single PNG ("a def still draws <texPath>") and status on a pool file says UNMEASURED. Install pool files with `art.py install <mod> <texPath>/<name>_a.png <sha> --owner-said`, retire the old single via `artledger.retire(<full src path>, owner_said=...)`. A sheet's column A is usually "IN GAME", so an owner pick of A keeps the current art; check snapshot labels before installing "set A".
- **`art.py enact` cannot install a per-tier pick for a styled part whose tiers share one texPath** (RM_SuspensionStyles: one picture per look): it reports the shared file's owner-kept keep as a CONFLICT for every tier. Give each picked tier its own `<part>_<Tier>` path, install there with `--ruling <his ingested ruling id>`, repoint the ThingStyleDef, and hold those rows in enact.
- **`art.py enact` skips a picked picture that already ships at ANOTHER slot (`live_anywhere`):** a male-lane pick of a female render installed only its south and left the male a mixed A/B set. After enact, audit every pick per facing against the slot it was picked for (snapshot `graphic_of`), not enact's summary.
- **The review-sheets template's number hotkeys (1-9 -> A-I) and shift+digit group bulk call `setDecision` directly and skip `itemOptions`/`bulk:false`,** so an art sheet's `setDecision` wrapper must check that the letter is a set of the row's slot itself. Snapshot `graphic_of` is NOT slot membership (former/alternate texPaths sit in a slot lane), so do not use it as an enact guard.
- **Before trusting an enact safety rule (refuse a pick at a stale lane), diff HEAD's dry-run install/conflict sets against the change over EVERY real decisions file.** Two drafts that passed their own fixtures regressed real routing: one raised 162 conflicts on rows already shipping, the next refused donor-lane picks that HEAD correctly rebinds to the row's own path via `own_slot`. Cache `load_jobs` or it takes 11 s per file.
- **A decisions record's `rev` is NOT the snapshot he clicked on.** Find the sheet he saw by click time: the newest snapshot revision with `built` <= `decidedAt` (max `built` over the whole window, never git commit order); any unreadable revision in the window must refuse, since it could be the right one. Preferring a rev match refused 35 real picks. Enact selftest fixtures must carry a snapshot `built` stamp like every real snapshot, or the click-time proof is impossible and a strict enact refuses every pick.
- **An enact guard must be tested on BOTH routes of a schema-1 pick:** KEYED `picks{lane:L}` and DERIVED from a decision letter. A moved-between-lanes refusal and the same-pictures check added to one route left keyed picks routing by a stale lane (Hawkbat G). A lane where nothing of ours ships (a "donor" lane) on the clicked snapshot is not proof the pick belongs at today's lane: route it only when that snapshot row's `res` WAS the old lane, our defs no longer name the old lane but do name today's, and the letter's pictures are identical; else refuse by name.
- **A per-row enact review misses cross-row defects.** Several rows can share one lane (bridge anchors Heavy, Steel, Timber of a look) and three different picks were planned onto ONE file, the last silently winning. Scan every real decisions file for `(mod, rel)` targets that two installs hit with different shas; `build_plan` now refuses the collision by name.
- **An enact refusal or skip is per PICK (row + letter), never per file or per facing.** Any refused or skipped facing (already live, purged, no slot, owner-kept, shared-file collision) holds the whole pick and its `replaced_by` retires (`enact.py held_back`), else the creature is drawn from two sets (Fuzzrunner C, BedBug V_E, RM_TunnelSnake B, RM_Vurra B). Apply retires only on that pick's own install (`ok_picks`). Check a dry-run plan by grouping installs per (row, letter) against the letter's facing count. An owner card that authorises overwriting kept art covers only keeps made before the judgement it cites: compare the keep's `at` against that judgement.
- **Committing `infrastructure/state/art/events/<SEAT>.jsonl` while sibling helpers are mid-enact sweeps their install events into your commit without their PNGs,** and the pre-push art guard (`ART_VERSION_WRANGLING_1`) refuses the whole push. Run `art_guard.py worktree` first and commit only when every ledger-live path it names is yours or already committed. `./publish` rebases, so `rimflow close --sha` given before the push names a vanished sha: close after publish.
- **`art.py purge` deletes the picture's bytes from the art store (`artstore/xx/<sha>.png`) by design,** so "originals recoverable from the art store" is wrong after a purge: copy the shas out (sha-verified) first if they must stay recoverable. `purge` alone never bans: removing rejected art with no sheet mark takes `purge --ban --subject <def>`, and a live picture needs `retire` first. `validate_sprite` accepts a hi-res redraw only with `--drawsize` (artpiped passes the job drawsize); a CLI run without it refuses any canvas != reference.
- **Fixing the art pre-push guard for a commit that ADDED a texture (old=None) installed with `--why`:** delete the target and re-run `art.py install` with the same bytes plus `--owner-said`/`--reason script:...` (no history rewrite), because install records `prev` = the on-disk sha (None when absent) and `check_change` takes the latest event whose `prev` matches the commit's old. `--file` must be inside the clone. Commit the ledger shard before `./publish` (the guard reads the ledger at HEAD).
- **A tool's `--json`/`--out` report path can land on a ruling file** (`remap_decisions.py --json` overwrote an owner's 20-pick `*.decisions.json` and a bulk commit carried it). Before calling a `*.decisions.json` "not a decisions doc", read its `git log`: it may be a clobbered ruling to restore, not junk to move. Guarded in `remap_decisions.py`; checked by `selftest_decisions_glob_hygiene.py`.
- **Old-sheet pending X marks that his reject+purge already deleted are planned BAN-ONLY by enact** (45 on the Weeping Stones sheet). 2 carry variant kind `canon` (RSW_Boma 99557fa15ec5, RSW_Dactillion cb80f22cfd51): a near-duplicate ban of a canon-library picture could re-roll faithful redraws. Simulated against all 10837 live shas: 0 hits. Look before `--apply` if canon targets matter.
