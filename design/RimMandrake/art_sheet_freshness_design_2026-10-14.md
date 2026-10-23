# Art sheet freshness — fresh or refuse (2026-10-14)

Item: `ART_SHEET_REDESIGN_FRESH_OR_REFUSE`. Owner, 2026-10-12: *"it needs some kind of hook or ensurance that it's not
serving stale information. By construction, by design, by hashes, by hooks, I'm not sure. But it must be improved in
freshness guarantee."* Approved for tonight: *"Yes to art sheet redesign."* (2026-10-13).

## The invariant

A served art sheet never shows a picture that is not what it claims to be. Per row:

1. **Installed claims are true.** Every picture in a column of kind `live` (labelled `IN GAME — …`, `shipped,
   shadowed — …`, `shipped, not loaded — …`) is, byte for byte (sha256), a file our mods hold on disk now.
2. **Installed art is never missing or mislabelled.** Every non-mask picture our mods hold on disk now, for any texPath
   the row shows, is on the row as an installed column. This catches a render that has since been installed but is still
   labelled `render …`, and a vanilla stand-in still labelled `IN GAME` after our art replaced it.
3. **The row shows what our defs draw now.** Every body-role texPath our defs draw, read from the src XML now, that
   has installed art of ours, has that art on the row. This catches the tap-clamp failure: a texPath taken from a cached
   def dump or census after a rename. A texPath with no file of ours has nothing the build could show, so it is exempt.
   So is one whose bytes are already on the row, because the build folds identical male and female files into one
   graphic.
4. **Thumbnails are the ones built.** Every thumbnail the row references exists, and on a sheet with a FRESHNESS block,
   has the sha256 recorded at build.
5. **Inputs are unchanged.** A sheet built from a texture manifest (`art_sheet.py --textures`) is stale once that
   manifest changes.

Candidates such as artpipe renders, git history and donor originals are content-addressed: a sha256 names the bytes for
good, so they cannot go stale. A `kept` column, which carries a set forward for a decision letter, may never say
`IN GAME`.

## Where each displayed image's bytes come from

| column kind | bytes | verified against |
|---|---|---|
| `live` | the art ledger's `live` events (what `art install` wrote) | **disk now**: `src/**/Textures/<texPath>[_facing].png` and the folder variants, hashed |
| `artpipe` / `git` / `donor` / `kept` | the art store, keyed by sha256 | immutable; a `kept` label claiming `IN GAME` is refused |
| stand-in (`--textures`) | the manifest's files, hashed into the store at build | the manifest's sha256 (an input) |
| thumbnail `img/<sha20>.webp` | made from the store bytes of that sha | it exists, and its sha256 matches the FRESHNESS block |

The ledger is a record. Disk is the instrument. If the two disagree, a build fails req 15 with the remedy
(`art.py backfill disk`), so a sheet can never be stale at birth.

## Where a texPath comes from (no cached location lists)

`generate_biome`, which every art sheet goes through, re-resolves each row's texPaths from the **src XML at build**
(`sheet_freshness.fresh_resources`, using `subject.World`, which parses XML and never matches text). This applies to
creatures (`PawnKindDef` lifeStages `bodyGraphicData`, shared with the race) and plants alike. When the census
(`Transient/biome_ffar/census.json`, last written 2026-10-07) disagrees, src wins and the build prints the stale row.
Only donor and vanilla rows, which have no src XML, keep the texPath the census resolved from the live dump. Those rows
are not covered by claim 3; see what remains.

The first trial rebuild (Leaning Scrub) re-resolved 17 rows, for example `RSW_Anooba` (`swanimals/…` →
`RimStarWars/SWBestiary/…`, after the donor-port W1 repoint), `RM_Chikka` and seven `*Venomvine` plants.

## Hashes: recorded at build, re-measured on use

- The sheet's `ITEMS` block (already embedded in every art sheet) is the claim. Verification needs nothing else, so
  **every sheet built before tonight is verified too**: this is the retrofit.
- New sheets also carry a `<script id="FRESHNESS">` block, inside the gate stamp's hash, holding the defs per row, where
  each texPath came from, the sha256 of each thumbnail and input, and the build time and git head.
- `sheet_freshness.verify_html` re-measures the disk, the src XML and the thumbnails on **every** call. It keeps no
  cache across calls; the only cache is a file-hash memo keyed on (path, size, mtime).

## Refuse at build, label at serve

- **`scaled_review_gate` req 15 `check_fresh`**: a sheet stale at build is never written. Because `refresh_sheets.py`
  re-runs the gate on every sheet it leaves alone, a sheet that has gone stale is rebuilt by the next refresh.
- **`serve_gated.py`** re-verifies at start and on **every page load** (memo of 5 s or less). Since the owner's card
  of 2026-10-19 (*"How far do we go to make art review fast and reliable? → Python command, no agent before you see
  it"*, relaxing his 2026-10-14 card from "stale sheets are refused" to "stale rows are refused") each stale ROW is
  served with a red `STALE: <reason>` badge and its pick controls off; the other rows work. Nothing serves a stale row
  as fresh. Since 2026-10-22 "no agent" means no agent composes the page — one still reads every row first and
  serving needs `<stem>.prereview.json` (`standing_rulings.md` §Nothing reaches the owner unread). `selftest_sheet_freshness.py` (a) proves it.
- A page with no `ITEMS` is refused (exit 5); a check that crashes labels every row stale, never fresh.

## Install invalidates

Nothing has to invalidate for correctness, because every use re-measures. To make staleness visible at the moment it
happens:

- `art.py install` (not dry-run) runs `sheet_freshness.after_install([texPath, its folder])`. This prints each sheet
  showing that texPath that is now stale.
- `enact.py --apply` with any install or retire runs `after_install(None)`, a scan of every art sheet.

Both only print and never fail; the install has already happened, and the serve path labels the stale rows.

## Retrofit status at build time (2026-10-14)

A scan of the 39 sheets under `Transient/` found 20 FRESH and 16 STALE art sheets. The other 3 have no `ITEMS` block:
they are pre-template, non-art or icon pages, and are UNMEASURED and refused. The stale sheets include:

- 12 of the Oct 4–5 biome sheets (Weeping Stones 13 of 51 rows, The Scald 9 of 20, Leaning Scrub 6 of 83);
- the GSS owner-walk sheet (lamp mast since re-installed);
- GSS all-art (5 of 151) and FlowWorks owner-walk (1 of 47);
- tonight's Pyrelands sheet (9 of 9 rows: its renders are now installed). They are rebuilt by `refresh_sheets.py` or `art_sheet.py`; until then
their stale rows are labelled when served (since 2026-10-19).

## What remains (not built tonight)

- **The deployed copy.** "Installed" means the repo's `src/` here. The game reads `…\RimWorld\Mods`, and a sheet does
  not check that the deploy happened.
- **Donor and vanilla rows.** These are rows with no src XML. Their texPath still comes from the live def dump through
  the census (claim 3 does not cover them), and their donor `IN GAME` bytes are not re-hashed from the game folders.
- **Flip-book lanes** (`_flip:`) are not disk-verified frame by frame.
- **Winner by load order.** A `live` column's `winner` is not re-derived when the load order changes. Its bytes are
  still verified.
- `refresh_sheets.py` covers biome sheets only. A `--subjects`/`--textures` sheet is rebuilt by re-running its
  `art_sheet.py` command, and is refused until then.

## The owner's three other sheet rules (2026-10-12), built 2026-10-14

- **Retire and replace in ONE pass.** `✕ retire` on a live picture plus `use this` on another set in the same slot, in
  either order, both stand; the row says the retired picture "leaves the game in this same pass, replaced by X".
  `enact.retire_replaced` plans every live copy of the retired set that the pick's install does not overwrite, and the
  apply step retires it after the install, never while a def still names its texPath. With no pick in the slot a retire
  is still a redraw: the picture stays until its replacement exists.
- **No "accept unchanged".** The per-slot button and "accept all unchanged slots" are gone; an unanswered slot reads
  "unchanged — kept when you return the sheet", and only a required slot with nothing in game asks for him. When he says
  a sheet is done, `decisions_v2.py <file> --returned "<his words>" --apply` stamps `returned{at, said, by}`; ingest then
  records each slot he left alone as his keep of the in-game set (`raw_verdict: returned-unchanged`). Enact already did
  nothing to an unanswered slot.
- **"Decided" is only his.** The page seeds each row's `decision` with the agent's prefill. That seed now reads as
  "agent prefill X — not your answer", never as "using X", and `decisions_v2.owner_view` blanks it for enact and ingest
  unless his click stamped it (`decidedAt`), it was carried from his ruling, or it overrides the prefill. The page header
  already counted "decided by you" apart from the prefill. The sidecar's `decidedCount` field (the shared review-sheets
  skill) still counts seeded letters; nothing in this repo reads it.
- Selftests: `selftest_sheet_slots.py` (page), `selftest_sheet_owner_rules.py` (enact, ingest, decisions_v2).
