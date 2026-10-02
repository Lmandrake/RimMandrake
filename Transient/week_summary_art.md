# Art census — 2026-09-18 to 2026-09-25

## Scope
Read-only census of art produced and ruled on in the window 2026-09-18..2026-09-25 inclusive.

## Manifests touched in window (infrastructure/artpipe/done/)
Method: mtime alone is unreliable (git checkout/rewrite can touch files without regenerating
art), so dates were derived from the `rollout-<date>T...` timestamp embedded in each
manifest's `meter_before/meter_after.rollout` path (the codex worker session log path),
which is a real per-job generation timestamp.

- 1161 total `.manifest.json` files in `infrastructure/artpipe/done/`, all `status: ok`.
- **763 individual image-generation jobs** (facing-level, e.g. `_east`/`_north`/`_south`)
  fall inside 2026-09-18..2026-09-25: 93(18th) / 128(19th) / 160(20th) / 1(21st) / 83(23rd)
  / 131(24th) / 167(25th). No jobs dated the 22nd found (quiet day).
- Collapsing facings gives **394 distinct subjects** generated in the window.
- 1153 of 1161 total manifests are `mode: generate` (new art), 2 `edit`, 6 with no
  parseable rollout date (still `status: ok`).
- Top subject-prefix clusters in the window (by manifest/facing count):
  desertportb 100, desert 99, rot 62, canon 57, rut 57, scald 55, contagion 39, RSW 36,
  crags 34, deeps 24, RM 23, bluedesert 21, graffiti 14, offbiome 14, xeno 11, feverwood 10.
  These map to biome/theme work: a desert-port biome build, "TheRot"/rot flora-fauna,
  a wave of canon Star Wars creature regens (`canon_<name>_v1`, 19 distinct canon
  creatures x3 facings = 57), RUT-tier biome content, a Scald (fish/sea biome) art
  upgrade wave, Contagion biome, RSW canon-adjacent regens, Crags/Deeps biomes,
  Blue Desert biome, Graffiti Punk ideoligion art, and an off-biome sheet re-render pass.

## registry.jsonl / art_status.json
`art_status.json` itself has not been touched since 2026-09-13 (stale relative to this
window; not a source for this census). `registry.jsonl` (6558 lines total, event log
with `by`/`event`/`source`/`target`/`ts`) gives, filtered to ts in [2026-09-18, 2026-09-26):

- **4748 events** in the window: 1270 `generated`, 1270 `validated`, 1104 `registered`,
  1104 `queued` (fill_queue side).
- Of the 1270 `validated` events, verdicts split almost exactly evenly:
  **636 pass / 634 fail** — roughly half of automated validator passes failed and
  presumably triggered a retry/regen (consistent with the artpipe's iterate-until-pass
  design, not evidence of a broken pipeline by itself).
- Top named `source` items driving registry activity in the window: `DESERT_FAMILY_PORT_EXECUTION_1`
  (260), `DONOR_DEFS_PORT_TO_OURS_1` (114), `ROT_FLORA_FAUNA_VERDICTS_1` (62),
  `SUMP_FAUNA_ROSTER_1` (54), `FEVERWOOD_RM_MOD_BUILD_1` (53), `CAVERNS_PARITY_BUILD_1` (49),
  `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` (49), `BLUEDESERT_DESIGN_SITTING_1` (48),
  `TERMINALBIOMES_RM_MOD_BUILD_1` (42), `SCALD_ART_UPGRADE_WAVE_1` (42),
  `WEEPINGSTONES_RM_MOD_BUILD_1` (40), `WEBWORK_FAUNA_ROSTER_1` (30),
  `DEEPS_FAUNA_VERDICTS_1` (24), `STOCKED_POOL_BUILD_1` (24), `MIASMA_FLORA_ROSTER_1` (24),
  `GREENTIDE_JUNGLE_TREE_ROSTER_1` (18), `THEROT_RM_MOD_BUILD_1` (18),
  `FIREHAWK_FLIGHT_BEHAVIOR_1` (15), `OFFBIOME_SHEET_RERENDERS_1` (14).
  (3644 events carry no `source` — anonymous/ad-hoc registrations.)

## Decisions files / review sheets modified in window
Caveat: 12 of these 20 files share the identical mtime `2026-09-21T02:30:17.7xx` to the
millisecond — a single bulk script pass (adding a `reviewStatus`/provenance-audit field),
NOT the real ruling time. Real ruling dates were read from each file's `savedAt` /
`reviewStatus.at` / `owner_said` fields instead. `art_review_2026-09-06.decisions.json`
was touched in that same bulk pass but its real content is from 2026-09-06 — **outside**
the window, excluded below. Three files below (`desert_art_verdict_2026-09-20`,
`landmark_density_2026-09-19`, `lantern_deeps_strange_life_2026-09-20`) are agent
pre-fills the owner never actually ruled on — flagged, not counted as rulings.

Real owner rulings landing in the window, oldest first:

- **`deeps_art_review_2026-09-18`** (48 rows) — *"We approve all of the art review of
  Lantern Deeps!"* — blanket **keep 48**.
- **`deeps_flora_fauna_review_2026-09-18`** (16 rows) — *"Accept Lantern Deeps ruling and
  follow its regeneration request."* — **cut 8 / regen 8**.
- **`rot_flora_fauna_review_2026-09-18`→ruled 2026-09-19** (55 rows) — *"rot art ruled. Now,
  deploy these art decisions..."* — **regen 46, keep 7, cut 2** (frozen breakdown: 45 regen /
  2 cut / 3 keep / 5 new-art-approve).
- **`rot_size_rejudge_2026-09-19`** (33 rows, 28 decided) — *"Finished the re-judge sizes of
  the Rot. Also the Colossus art didnt wire up, see comments."* — **17 confirmed-ok, 11
  resize, 5 left deliberately open**. Named pipeline bug: the Colossus's art failed to wire
  into the def (see Pipeline problems below).
- **`bulk_art_misroute_2026-09-19`** (82 rows, prefill "right" as null hypothesis) — 3 rows
  hand-corrected to **misrouted**: `AA_MycoidColossus` (confirmed a droid render mixed into
  animal art, already pulled to `Droidworks/ArtIncoming`), and Star Wars animals `Grank` and
  `GreaterKraytDragon` (art didn't match canon reference — a "saw-toothed, huge teeth, red
  skin" grank was cited). Both reappear as freshly regenerated `desertportb_grank_*` and
  `desertportb_greaterkraytdragon_*` manifests dated 2026-09-24/25 — a misroute caught and
  then actually fixed inside the window.
- **`desert_family_review_2026-09-20`** (109 rows) — *"Yes. All of the desert sheet should be
  keep but replace with our own version of creature and art. Port. All of them. Now."* —
  blanket **replace 109** (a verbal ruling, sheet never clicked; approvalRoute confirms no UI
  writes).
- **`port_tail_2026-09-20`** (95 rows) — *"Yes replace everything."* — **replace 95**. Sheet
  triaged 95 donor-tail/no-`MayRequire` rows against the LIVE def dump (617 active mods): 60
  real active donor content with a missing guard (mostly Alpha Biomes, 52 rows), 14 dead-mod
  rows (inactive `biomesteam.biomescaverns`), 4 vanilla/DLC excluded, 2 already-ours excluded.
- **`port_alphaanimals_2026-09-20`** (55 rows) — same blanket *"Yes replace everything."* —
  **replace 55**.
- **`port_swac_2026-09-20`** (36 rows, Star Wars Animal Collection) — same ruling, same
  sitting — **replace 36**.
- **`stoneback_identity_2026-09-22`** (2 rows) — owner, in-sheet notes: bokka *"Arid biome
  approved, make sure our art is up to modern standards"* (regen implied); korrum *"This is
  good for Scarlands. Regenerate art."* — **1 keeps_name, 1 renamed**, both flagged for art
  regen to current quality bar.
- **`deepfire_pigment_review` (2026-09-25, latest in window)** (8 rows) — *"Review sheet
  done"* — **cut 6 / keep 2** — a pigment/colour-variant review, majority cut.

Net: the desert/tail/alphaanimals/swac blanket rulings (109+95+55+36 = **295 rows**) are the
single biggest driver of the window's generation volume — they map directly onto the
`desertportb`/`desert`/`canon` prefix clusters (259 of the 763 window manifests) and the
`DESERT_FAMILY_PORT_EXECUTION_1` (260) / `DONOR_DEFS_PORT_TO_OURS_1` (114) registry sources.

## New PNGs added to git since 2026-09-18
`git log --since="2026-09-18 00:00:00" --diff-filter=A --name-only -- '*.png'`:

- **4073 PNG "add" lines** across the commit range (a line per file per add-commit; this can
  double-count a file added, removed and re-added, but no such pattern was found — treat as
  ~4073 distinct new PNGs).
- **2347 under `src/`** (shipped mod content) vs **1726 under `Transient/`** (review-sheet
  thumbnails, extraction scratch, reference matrices — NOT shipped art).
- Biggest `src/` cluster by far: **`src/RimStarWars/Armoury` — 1619 PNGs**, landed in ~4
  commits concentrated on 2026-09-18 (plus one 2026-09-20 commit) — apparel body-type/facing
  variants (Fat/Female/Hulk/Male x facings x many wearables, e.g. `bandolier_chewbacca`).
  This reads as a **bulk donor-texture import**, not artpipe-generated art — worth flagging
  separately from the generation counts above since it dwarfs everything else by file count.
- Next `src/` clusters: `SWBestiary` 323, `LanternDeeps` 76, `TerminalBiomes` 74,
  `UtinniPatches` 65, `FeverWood` 34, `Webwork` 33, `TheRot` 29, `RotSporeKit` 18,
  `LeaningScrub`/`AshkarrFlora` 14 each.
- Biggest `Transient/` clusters are exactly the review-sheet thumbnail folders already
  identified above (`desert_family_review_thumbs_2026-09-20` 105, `art_review_desert_wraps/
  matrix_work` 102, `sea_raw` 92, `bulk_art_misroute_thumbs_2026-09-19` 82, `port_tail_thumbs_
  2026-09-20` 80, `rot_art_landed_20260920/thumbs` 64, etc.) plus donor-extraction scratch
  (`mlie_waveb_extract/swanimals/acklay` 52, `.../gorg` 44, `.../porg` 35) and a
  `triposr_prototype/output/0` 34 (a 3D-reconstruction experiment, separate track).

## Owner rulings found
(pending)

## Art-quality standards established
- **Painterly style is the standing law** (already recorded project-wide as `ART_PAINTERLY_RESTORATION_1`):
  live manifests in the window explicitly cite it — every `legibility` check in every
  manifest sampled reads `"skipped"` with finding `"gate disabled by default
  (ART_PAINTERLY_RESTORATION_1) — set ARTPIPE_LEGIBILITY_THRESHOLDS=<path> to re-enable;
  skipped, not a pass"`. So the automated flat-legibility gate is deliberately OFF this whole
  window in favour of painterly rendering, and validator passes rest on the `facts` check
  (silhouette/transparency/size) plus human review, not a legibility score.
  - `worker_self_report` notes converge on a hard technical bar regardless of style: exact
    canvas size (256x256 or 512x512 per subject), RGBA with a **fully transparent
    background and all four corners transparent**, silhouette inside frame.
- **Canon accuracy is enforced by direct reference, not vibes**: the misroute review corrected
  `Grank` art against a cited Wookieepedia image ("saw-toothed... huge teeth, red skin"), and
  the stoneback ruling explicitly asked for regen "to modern standards" — i.e. the bar keeps
  rising and older art gets re-judged against it, not grandfathered in.
- **Owner's blanket "replace with our own art" ruling (2026-09-20)** established that
  donor-sourced/no-`MayRequire` creature and item art across the desert family, tail rows,
  Alpha Animals and Star Wars Animal Collection is not acceptable long-term even where it
  "works" — it must be ported to our own generated art. This is the single biggest scope
  decision of the week and is driving most of the 763-job volume.

## Pipeline problems hit and fixed
- **Misrouted/mismatched art caught by review, then actually regenerated**: `AA_MycoidColossus`
  render was a droid mixed into animal-art output (pulled, moved to `Droidworks/ArtIncoming`);
  `Grank` and `GreaterKraytDragon` art didn't match canon and were flagged — both reappear as
  fresh `desertportb_grank_*` / `desertportb_greaterkraytdragon_*` manifests dated 2026-09-24/25,
  i.e. the fix actually landed within the window, not just noted.
- **"Colossus art didn't wire up"** — owner note on `rot_size_rejudge_2026-09-19`: generated art
  existed but failed to connect to its def/texPath, a distinct failure mode from bad art (see
  `texture-binds-by-texpath-not-defname` lesson already in memory) — flagged for a follow-up fix,
  not confirmed closed in the sources read here (UNMEASURED whether it was wired up before
  2026-09-25).
- **Missing south-facing sprites repaired**: an 8-creature `facingrepair_*` batch (dewback,
  grmolebear, kreetle, megatardi, orray, rutcathedralroach, rutscarroach, wyyyschokk)
  specifically generated the missing frontal south-facing sprite for each — all 8 succeeded
  (`status: ok`), with minor per-job worker hiccups self-corrected (ImageMagick unavailable on
  one job, a PowerShell constructor error on another, both resolved with a retry inside the
  same job rather than failing it).
- **Automated validator/legibility failing ~half the time**: 1270 `validated` registry events
  split 636 pass / 634 fail almost exactly evenly — consistent with an iterate-until-pass
  design (the manifests actually landed in `done/` are 100% `status: ok`, meaning failures were
  retried to success, not shipped broken), but the near-50% first-pass failure rate is itself
  worth watching if it is new behaviour — no baseline from an earlier week was available here
  to say whether it moved.

## Open questions / UNMEASURED
- Whether the "Colossus art didn't wire up" defect was actually fixed before 2026-09-25 —
  not established from `done/` manifests, registry, or decisions files read here.
  UNMEASURED.
- Whether the near-50/50 validated pass/fail split in `registry.jsonl` is typical of the
  artpipe or a regression — no prior-week baseline was pulled for comparison. UNMEASURED.
- `infrastructure/artpipe/art_status.json` was not updated since 2026-09-13, so it could not
  be used as a source for this window; whatever tracking it's meant to provide is stale here.
- The 763-job count and 394-subject count are **generation attempts/subjects**, not a count of
  distinct shipped textures currently deployed to the Mods folder — that would require a
  separate deploy-state check (`rimworld-deploy` skill), not attempted here (out of scope: this
  was an artpipe/decisions/git census only).
