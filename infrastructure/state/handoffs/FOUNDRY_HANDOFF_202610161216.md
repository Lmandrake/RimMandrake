# FOUNDRY_HANDOFF_202610161216 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610160546`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The donor-off load (21 mods, no donors) now runs at 254/267 L1 rows: what is left is owed ART (batch 6 items and creatures all ruled tonight, installs below), the pack-sprite decision, and two owner-sitting rosters (Bileworm, Zrrik). Tonight's biggest lesson: **a harness that has only met a fake bridge lies at once on the real one** (144/144 false `badTex` FAILs because Pawn.Graphic is unrendered; every modcheck suite UNMEASURED because the companion test profile EXPIRES at 09:00Z and the refusal reason was dropped). Both are fixed; check `ensure_test_profile` output before blaming a suite.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- His phase0 sheet is ruled (9 rows by notes, no accept button for several). Enacted: eggs, raptor plates, Braskeen E, Ismerrow A are INSTALLED (2f3085def, texPaths moved to our folders). Everything else is filed as items (below). He asked for the bridge back: it is FREE, game DOWN, live ModsConfig is the FULL list (backup `deployed/config/ModsConfig.full-found-live-20261016.xml`).
- Decisions only he can make: `PACK_SPRITES_DECIDE_HAULERS_LOADED` (48 races packAnimal, no Pack art) and `FORGE_SLOT_DECIDE_NEEDS_A_DESCRIPTION`.
- Biome suites (round 5-8): Leaning Scrub 81/0 fail, Contagion 77/0, Cauldron 69/0, all former FAILs were site/harness (roof collapse on mountain tiles, lapsed profile, bill_add bug). Last Cauldron fixes (wildlife clear, tox-smoke window) never re-run live.
- Hydenock/Jogan sizes set by him ("much much larger"): 5~10 and 5~8; scale images before tonight drew new defs at 1 CELL (fixed in chat_review.py).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `BEZZUL_DELETE_NOT_NEEDED_ANYMORE` — filed; NEXT: remove RM_Bezzul def, roster rows, patches, art refs (his words: drop it).
- `BRASKEEN_REDRAW_VARIATIONS_ON_E` — E installed; NEXT: commission variations referencing E, then `art.py purge --release-keep` the two kept symmetric ones using his sheet note.
- `ISMERROW_INSTALL_SEVEN_VARIANTS` — A installed single; NEXT: install A,B,C,D,F,G,H as Graphic_Random folder files and set the def back from Graphic_Single.
- `SIKKA_SIKKA_RENAME_AND_INSTALL` — filed; NEXT: install silkie variant D + silk A, rename label to Sikka Sikka (check defName tier rules).
- `JURROX_MIGRATE_INTO_WARSCAR_GAUNT` — filed; NEXT: write the creature def with a new name/description, add to RM_Warscar.
- `IDEOICONS_INSTALL_SIX_REPOINT` — accepted; NEXT: install six PNGs via ledger and apply Transient/ideo_icons_repoint_plan.md.
- `PLUURVA_DECIDE_OLD_DUPLICATE` — art rejected; NEXT: check whether a Rot creature already covers it, drop or redraw.
- `FIRESPIT_EXPLAIN_BEFORE_JUDGING` — he could not tell what it is; NEXT: re-show with user creature and description.
- `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` — NEXT: after the above installs, deploy compose, run the donor-off round once, then P7 (donors out of full modset and Cherry Picker) and the section 0.5.5 gate.
- `FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW` — filed; NEXT: get the stack from Player.log and fix.
- `PHASE0_L1_SAVE_LOAD` — save phase stayed on the main menu; NEXT: read get_ui_state during the load of CANONICAL_ASHKARR_START_2026-09-12_donorfree and find the blocking dialog.
- DIRTY files: fixer-agent validation.py/selftests and a few C# files for the biome suites; NEXT: independent full-file reviews then mark-clean.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Harness `thing_graphic` reads Pawn.Graphic = BadTexture for every undrawn pawn; a control Muffalo now proves it (filed: LESSONS).
- Companion test profile expires (09:00Z): runs end UNMEASURED with a dropped reason; `ensure_test_profile` now guards (see: src/RimMandrake/Utils/modcheck/runner.py).
- `modcheck run` resets live ModsConfig to the full list at the end; reapply the tier (Transient/night_rounds/run_suite.sh) (filed: LESSONS).
- Mountain tiles: `clear_area` removes support, roof collapses crush the test pawns on tick 1 (filed: LESSONS).
- chat_review scale images drew every def missing from the 2026-10-04 dump at 1 cell (filed: LESSONS).
- zsh does not word-split `$VAR` lists (use bash arrays) and `pkill -f` kills my own shell (see: CLAUDE.md memory).

## Commits

```
2f3085def Enact his phase0 art sheet: eggs, raptor plates, Braskeen E, Ismerrow A installed; texPaths moved to our folders
5a3244465 Phase 0: one combined review sheet for all remaining art (20 rows)
a37d27d3c Cauldron+Contagion modcheck: round-5 FAILs were harness (vexxiss walk window, tox puff read once, Bill_Production surgery); burn native/sunbeam/clock-stall reads made honest; Cauldron clears mapgen wildlife
6aac4fe8e jawa/bill_add: a surgery on a pawn makes a Bill_Medical (Bill_Production never ran ApplyOnPawn); list_pawns hediffs carry lastInjury
bc25e0e4e Contagion selftest: pin patient_wont_lie UNMEASURED and slow_walkers PASS (review)
4cbe9f44f Contagion selftest: a site break must never crash the script (review)
7a148af11 Contagion modcheck: sunbeam arrest gets its toggle-off arm, grown-limbs arm needs the inject's gestation, armored control must stay on the open pad (+ selftest breaks) (review)
712968886 Contagion modcheck: fresh visitor read on the open pad, absent native UNMEASURED, roof patch read back (+ selftest break) (review)
bd63a6de2 Contagion modcheck: roofed control read under the patch, armored control never under it, empty roster guarded; fake armored natives do not dive (as the mod) (review)
5ad078a8f Contagion modcheck: touched off arm needs its colonist alive (review)
18740c67d Contagion modcheck: armored control respawned on the open pad, coalescence off arm waits 1500, roster names matched exactly (review)
0cdd9ec4d Contagion modcheck: contact dose judged against a far control under the same sky; off-arm Unfinished removed before the absorb arm (review)
27fca0b77 Contagion modcheck: jump read back off the clock, full xref page is UNMEASURED, native needs Burn evidence, kid alive before the push, every spilled sample graded (review)
a43703ef9 Contagion modcheck: close vacuous passes (bool read-back, open visitor, whole-map dissolve, pre-hit touched, xref drain, repulsor read after lapse, grass baseline) (review)
ba1a3ac5a modcheck4 review fixes: roof strip says when it did not take and runs in its own guard; stamp unlocks weather; pyre hint must be flammable
b17dd968f Contagion modcheck: negative arms need their subject alive (roofed/fresh visitor, armored native, zhool off arm) (review)
ef557e442 Cauldron+LeaningScrub modcheck4: strip roof over cleared pads (collapse crushed actors, buried the vent); pyre/stamp proofs get real pads
244dfc1fd Contagion modcheck: unroof before the clear, host must be inside its rect, fake crushes the support margin (review)
b78788d1a Contagion modcheck: unroof cleared pads (mountain roof collapse crushed fixtures), clear mapgen wildlife, exact in-bed read, spawner host guard
6317c3759 modcheck: refuse a run when the companion test profile is lapsed or lapsing; GovernorStop names a profile refusal
... 69 more: git log --oneline 135d2d7b7..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/scale_ground_measured.json   generated/other (sweep or not mine)
 M conversations/2026-10-14-0337-b833ee96.md   generated/other (sweep or not mine)
 M conversations/2026-10-16-0044-cccc4587.md   generated/other (sweep or not mine)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   generated/other (sweep or not mine)
 M infrastructure/state/ledger/events/OWNER.jsonl   generated/other (sweep or not mine)
 M infrastructure/state/modcheck_status.json   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/01fbc3e8db36f63ab5e8.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/0246ec2415ecfd9034c5.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/0365aef56ed78f6d87d8.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/037c682927ae2ff0ddef.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/03e20205e836860cb067.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/03e388a41435a8895e9b.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/046b4216ce4eef45833d.webp   generated/other (sweep or not mine)
?? Transient/biome_ffar/img/05c5e9c0a46d55d12961.webp   generated/other (sweep or not mine)
... 871 more uncommitted paths (by top-level dir: Transient 866, conversations 2, deployed 2, infrastructure 1): git status --short
```

