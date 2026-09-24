# FOUNDRY_REBOOT_HANDOFF_202609242045 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609241836`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`apply_blanket_ruling.py`'s core safety guard has been silently non-functional since it was
written: it checked `savedBy in ("review-sheet-page", "sidecar")`, but `serve_sheet.py`'s real
stamp is `"review-sheet-sidecar"` — the guard never actually fired for a genuine sidecar review,
so a blanket ruling run against sidecar-reviewed data could have silently flattened real per-row
decisions with no warning, ever. Found and fixed in code-review wave 62 (`3afd996db`) by a second,
independent full-file pass over 7 tools a stale "never-entered" pointer had wrongly claimed were
untouched for 47 waves (they were actually marked CLEAN back in waves 39/40 — the pointer was
copy-forwarded without re-checking `CODE_REVIEW_STATUS.json` for 22 waves and had rotted). Worth
a scan for whether any blanket ruling was ever actually run against sidecar-sourced data while
this guard was dark.

## What the owner should see

- **Barbslinger redesign**: sent him the south/east/north contact sheet, he ruled the tails are
  right but the south-facing candidate has stray claws near the mouth that the east profile
  doesn't — a real cross-facing inconsistency. NOT yet re-filed for a fix (see half-done below).
- **Three question-card rulings acted on and live**: `RSW_SandLion` keeps the label "vekka"
  despite the canon-character-name collision (his call, recorded); the three duplicate-name
  pairs found by the beast-rename census (mullgoth/grommo, durrok/pukko, ikee/oxxa) now all
  resolve to the earlier-ruled name, relabeled and deployed; the water-breathing-gene species
  question turned out to be moot — `RSW_WaterBreathing` was already correctly wired onto exactly
  the four species he re-confirmed today (Mon Calamari/Nautolan/Gungan/Selkath), from a
  2026-09-20 commit neither open item had recorded. Both items' stale status corrected and one
  (`XENOTYPE_NONCOSMETIC_FIXES_1`) closed outright.
- `NONCANON_BEAST_RENAME_1` Phase 1 (every land biome) is DONE: 124 drafted pseudo-Star-Wars
  names across 3 docs, collision-swept and canon-checked, sitting at `needs: owner` for whenever
  he wants that review. Only the sea batch remains, still blocked on `TERMINALBIOMES_RM_MOD_BUILD_1`.
- `DONOR_DEFS_PORT_TO_OURS_1` now has a real porting-cost census for both large donors (step 1 of
  its own spec): Alpha Animals is 15 HIGH / 51 MEDIUM / 0 LOW (every single entry needs at least
  the VEF framework, no free ports); Star Wars Animal Collection (Mlie) is 76 / 76 LOW (the
  cheapest donor by far — no assemblies at all, resolves to vanilla classes). Ready for the
  keep/cut-then-order sitting the item's own spec calls for before any actual porting starts.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NONCANON_BEAST_RENAME_1` — Phase 1 (land) complete, `needs: owner`; NEXT: run the sitting over the 124 drafted names plus the flagged conflicts (skezzar withdrawal since sytheclaw is already his ruled pick, fumerider placeholder, emberscythe mantis unruled coinage, dryad/VFEI2 scope questions).
- `BARBSLINGER_SCORPION_REDESIGN_1` — `needs: owner` answered (tails good, south-facing mouth-claws flagged as wrong); NEXT: file a corrected south-facing (and check north for the same defect) art job matching the east profile's mouth treatment, then get another look before wiring any facing.
- `AQUATIC_WATER_BREATHING_GENE_1` — Card 1 resolved and confirmed live; `needs: bridge`; NEXT: the live-quicktest proof this item has owed for days — `RM_PitDrowning` immunity in a flooded FlowWorks pit plus wading-path/mood check on a drafted water-breather (avoid `jawa/pawn_health`+`WoundInfection`, see this repo's existing bridge traps doc). Bridge was FREE all session and I didn't get to this.
- `DONOR_DEFS_PORT_TO_OURS_1` — both large-donor cost censuses complete; `needs: owner`; NEXT: a BENCH/owner sitting on the keep/cut pass (spec step 2) and porting order (step 3) — do not start porting defs before that sitting happens.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — standing loop, wave 62 just landed clean (`CLEAN 3218 DIRTY 7 NEVER ENTERED 238`); NEXT: wave 63 — `code_review_status.py list --show-untracked` fresh (no named cluster queued this time; remaining NEVER-ENTERED is almost entirely XML defs now, the `.cs` backlog is exhausted).

## Traps learned

- A `needs: owner` item's own last note can go stale within days, not just weeks — `AQUATIC_WATER_BREATHING_GENE_1` and `XENOTYPE_NONCOSMETIC_FIXES_1` both still said the water-breathing species assignment was unresolved, but it had actually been wired live 4 days earlier (`e7c8042db1`) and neither item's notes were ever updated. Always re-check the live def before asking the owner a question that might already be answered — nearly asked him something already settled (filed: LESSONS_INBOX).
- `apply_blanket_ruling.py`'s `savedBy` guard never matched `serve_sheet.py`'s real `"review-sheet-sidecar"` stamp — see the carry-forward line above (see: `DIRTY_CODE_REVIEW_STANDING_LOOP_1` wave 62 entry).
- A question-card option LABEL the owner clicks is not `--owner-said` material even when it reads exactly like a quote — tripped this myself mid-session, `block_forged_owner_said.py` refused it correctly; record a click as "decision taken by question card" instead (see: CLAUDE.md's own doctrine on this, already documented — a live trip-and-recover, not a new lesson).

## Closed since the last handoff (3)

- `BOOMALOPE_CUT_EVERYWHERE_1` — d9287058ed237fbae925113adbadda89ef030f6e
- `GRAFFITI_VANDAL_ART_REGEN_1` — 728586288
- `XENOTYPE_NONCOSMETIC_FIXES_1` — b90029e23805fa4e262c30fc53e95436fea9d173

## Filed and still open (3) — the next seat's queue

- `WATER_TRUCE_RETRIBUTION_1` — Water-truce retribution (owner typed 2026-09-24): first GUILTY hit in truce radius turns wildlife on the aggressor faction; engine attribution MEASURE
- `STOCKED_POOL_BUILD_1` — Build the Stocked Pool kit: 8-row pool bestiary, husbandry loop (pen zones, PoolStock bookkeeping), doubt-meat mood economy, cuisine hooks - all rulin
- `OASIS_MAKER_BUILD_1` — Build the oasis-maker machine: ring-growth to real water at center, shade+rock placement floor with projected-footprint overlay, sold-very-expensive +

## Commits

```
7bce6f5d1 rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 62 ledger note
45b3a50d9 BENCH handoff 202609242041: Weeping Stones full sitting + shine wave wrapped
33aacd8dd DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 62: mark-clean 8, close RUT_Sump.xml thread, kill stale "13 never-entered" pointer
3afd996db DIRTY_CODE_REVIEW wave 62: fix 4 real bugs in never-entered Utils tools
50c52e632 Ledger sync: NONCANON_BEAST_RENAME_1 Phase 1 (land) complete, gated to owner
06b5b2abf NONCANON_BEAST_RENAME_1: batch 3 drafts close Phase 1 for every land biome
00ecc5b7d Ledger sync: XENOTYPE_NONCOSMETIC_FIXES_1 closed, AQUATIC_WATER_BREATHING_GENE_1 re-gated to bridge
b90029e23 NONCANON_BEAST_RENAME_1: resolve 3 duplicate-name pairs, keep the earlier name
f53b7fa38 Ledger sync: design items superseded by their FOUNDRY build successors
1ebd0b644 Second card round ruled: wild-gentle/stocked-nasty, doubt-meat mood economy, real water at oasis center, sold-very-expensive acquisition
aab6045c5 Stocked Pool design draft: 8-row pool bestiary, husbandry loop, cuisine hooks
7b9ac3956 Oasis-maker spec drafted; Terramorph misidentification corrected to Fertile Fields
bd39b17cc rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61 ledger note
8b3cc5a83 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61 note
9c6a17531 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61: mark 5 more files CLEAN
9d2e88945 Fix: RM_Patch_LeachmossWildSpawnGate.cs was missing from RM_EnvironmentalHazards.csproj
bef32f63e Shine portfolio ruled: fish husbandry greenlit, oasis-makers + retribution redirected, 2 options dead
80fe48b93 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 61: mark 3 EnvironmentalHazards files CLEAN
fd960504b rimflow: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 60 ledger note
ceb853672 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 60: mark 8 EnvironmentalHazards files CLEAN
... 38 more: git log --oneline 009c91bd9..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T15:03:39Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   ambient, health-publisher regen output, nobody's edit
 M Transient/codebase_health.json   ambient, health-publisher regen output, nobody's edit
 M Transient/codebase_health_artifact.html   ambient, health-publisher regen output, nobody's edit
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_grank_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_grank_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_grank_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_horax_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_horax_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_horax_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_porg_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_porg_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_porg_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_strill_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_strill_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_strill_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_cundral_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
 M infrastructure/artpipe/registry.jsonl   ambient, artpipe daemon (background, continuous) -- its own bookkeeping, not this window's
 M infrastructure/artpipe/throughput.jsonl   ambient, artpipe daemon (background, continuous) -- its own bookkeeping, not this window's
 M infrastructure/dashboards/hub/data/health.json   ambient, health-publisher regen output, nobody's edit
 M infrastructure/state/codebase_health_last.json   ambient, health-publisher regen output, nobody's edit
 M infrastructure/state/queue/BENCH.md   mine -- regenerated by rimflow render after every ledger write this session; re-dirtied again by code-review subagents' own `code_review_status.py list` calls triggering the health-rebuild hook (CLAUDE.md's known 'self-inflicted rebase dirt' pattern) after my last ledger-sync commit
 M infrastructure/state/queue/FOUNDRY.md   mine -- regenerated by rimflow render after every ledger write this session; re-dirtied again by code-review subagents' own `code_review_status.py list` calls triggering the health-rebuild hook (CLAUDE.md's known 'self-inflicted rebase dirt' pattern) after my last ledger-sync commit
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_* batch, not this window's
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing (2026-09-11), not this window
?? infrastructure/state/ledger/events/OWNER.jsonl   not mine to touch -- another seat's ledger shard
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing, not this window
```

