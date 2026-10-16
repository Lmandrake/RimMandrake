# FOUNDRY_HANDOFF_202610160546 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610151923`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Donor retirement (Phase 0 of design/RimMandrake/biome_sprint_kickoff_2026-10-15.md) is now blocked ONLY on owner art rulings and one live round: every port/patch/save step ran offline today. The owner rules art by PHONE in batches (full-res + true-scale + facings, built by `src/RimMandrake/Utils/art/chat_review.py`; index `Transient/chat_review_phase0_2026-10-15/INDEX.md`), accepted = install through the ledger (`artledger.store_put_file` then `art.py install ... --owner-said "<his words>"`); batches 1-4 are installed, batch 5 (Sarlacc, plants, spore, gel, silk) gates deploying SWBestiary, which gates the donor-off round `Transient/phase0_L1_runbook.md`.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Batch 5 (Q29-Q37) was SENT to his phone and not yet ruled; batch 6 (Q38-Q44: eggs, silk, fire-spit, tentacle composites) not yet sent.
- Six ideoligion icons (Transient/chat_review_ideoicons_2026-10-15/, repoint plan Transient/ideo_icons_repoint_plan.md) sent, not ruled.
- Forge slot: he accepted the PICTURES of jobbosh/dhoggur/jurrox but has not said which fills the crescendo-anole slot; nothing ported or cast.
- Shipped by his cards today: Aiwha dropped from our mods; Skorra cut; shrimps kept and ported; five slime-family creatures ported and cast on RM_GelatinousSlime; zhool haze+plant-conversion C# (not reviewed); Bloody Mess burst-only-when-killed C# (not reviewed); lastvine rear-up C# (review fixes unreviewed); tentacle twitch staged (art rendered, not installed); alien shock goat (RM_Zhissa) installed; moth variants A/B/C installed; donor-free save copy has 1,429 donor world mutators STRIPPED (restore note design/RimMandrake/phase0_save_mutators_restore_NOTE.md).
- Retired by art-ledger at his words: old horned shock-goat art. Frozen RUT_ twin biomes still cast donor shock goat/aerofleet (show donor art; die at repaint).
- Process flag: one agent bypassed the commit hook with git plumbing (own rows only, clean); the rule stands.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `PHASE0_ART_RULINGS_BATCH5_6` — batch 5 sent, batch 6 unsent; NEXT: read his rulings by question number, install accepted art via store_put_file + `art.py install --owner-said`, then deploy SWBestiary (unblocks the donor-off tier)
- `DONOR_OFF_L1_ROUND` — tier donor_off_phase0, driver script and runbook committed (53d34dcdc), 76/76 offline against a fake bridge, never met the game; NEXT: when the game is down and he says so (`./game --said`), take the bridge and run Transient/phase0_L1_runbook.md (live ModsConfig is a 23-mod test list; restore FULL with `modlist_swap.py --restore --apply` only on his word)
- `IDEO_ICONS_SIX_REPOINT` — six renders ideoicon_*_v1 (sundebt_v2) made, not installed; NEXT: on his accept install them and apply Transient/ideo_icons_repoint_plan.md
- `FORGE_SLOT_PICK` — three candidates' art installed (TheForge Textures, paths in Transient/forge_candidates_art_paths.md); NEXT: ask him which one fills the slot, then port and cast it on RM_TheForge
- `TENTACLE_TWITCH_GO_LIVE` — staged under each mod's Staged/TentacleTwitch/, 30 tt_* renders done, batch 6 composites; NEXT: on his accept install the pieces and do the three go-live steps in design/RimMandrake/tentacle_twitch_design_2026-10-15.md section 3
- `PHASE0_CODE_REVIEW_OWED` — zhool haze comp, Bloody Mess burst, lastvine render comp, zhool tentacle helper (marked clean by its reviewer) need independent full-file reviews; NEXT: spawn separate reviewers, mark CLEAN only after `code_review_status.py check` agrees
- `PHASE0_LIVE_PROOFS` — thunderbeast flashstorm/range, bulloo bursts, oomb grow/split, zhool haze, Sarlacc portal, lastvine reared, moth variants, tentacle twitch, mutator-stripped save load; NEXT: all are rows in the L1 script, run them in the donor-off round
- `PHASE0_P7_AND_GATE` — donor removal from full modset and Cherry Picker not done; Alpha Biomes retire yes/no still his (O1); NEXT: after L1 passes run P7 (`modset_builder.py`) and the section 0.5.5 gate checks
- `ART_LEDGER_FOLLOWUPS` — kept_but_purged.md (79) and ledger_drift.md in Transient/art_review_2026-10-15/; doctor shows 9 BENCH-owned uncommitted installs; art store has no second copy (he declined the backup); NEXT: file the 79 kept-but-purged for his decision and re-run `art.py doctor` after BENCH pushes
- `MULTI_HOME_AND_TWIN_ROWS` — Lirrith, Bileworm, Mullgoth cast in a second biome, frozen RUT_ rosters still name donors; NEXT: raise at the biome sittings, do not edit rosters (evictions are stopped)
- `DONOR_NAME_PATCHES_UNTIL_REPAINT` — 2,704 donor xpaths remain (evictions/renames), left by his card; NEXT: leave until the one-time repaint, re-measure then

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A deleted patch whose effect was 'folded elsewhere' left two creatures with no texture (filed: LESSONS).
- Frozen known-bad calibration fixtures that are live sprites decay when the sprite is fixed (filed: LESSONS).
- `art.py put` refuses files outside the clone; use `artledger.store_put_file` then install by sha; purged shas need `art.py unpurge` (filed: LESSONS).
- zsh does not word-split `$VAR` path lists: use bash arrays for `git commit "${P[@]}"`, and `git add -u` is hook-blocked (see: CLAUDE.md Git).

## Commits

```
43e306312 Art review 2026-10-15 reports, Phase 0 L1 runbook, session record
be1956920 Ideo icons: Sun-Debt refiled as v2 (v1's scar cuts were grey stripes, not gaps)
5549a54a7 Retire the old horned shock-goat art (owner: drop this version entirely); alien zhissa replaces it
887a7f76f RM_Zhissa: owner-accepted alien art installed (donorart_zhissa_alien_v1), placeholder removed; art_checks selftest freezes Anooba_m/FireWasp pre-rescale fixtures
ce02e9484 Ideo icons: commission six new ideoligion icons (owner's 'Draw new icons'), repoint plan held for install
2b3a428f9 Dustveil: owner-accepted moth looks A/B/C as live per-moth variants (vanilla alternateGraphics), larva art; donor picture dropped
972711789 Phase 0 P6: donor tile mutators stripped from the donor-free save; restore note for the repaint
53d34dcdc Phase 0 L1 prepared: donor_off_phase0 tier, l1_donor_off_round.py driver + selftest, runbook (not run)
a019347b5 Commission donorart_zhissa_alien_v1: truly alien lightning-rippled zhissa (owner 2026-10-15), filed, not installed
33c5148f3 RM_Zhissa and RM_Bulloo were invisible (ported defs, no art at RM_ path): TEMP placeholder texPaths to our existing renders
ce514e019 Chittik (Rot swarmling, RM_Chittik) art installed from rot_swarmling_v2, unpurged on the owner's batch-01 accept
14857fbb3 GimmeSomeSlack north star VALIDATED (owner by card after walking the save)
75ff5157a Art ledger: owner-only art.py unpurge — his newer words reverse an older purge
9540b08e2 Owner verified the GSS walkthrough in game; unroutable-cord look A2 passes, item done
ddb62b522 Phase 0 P6: donor-free copy of the canonical save (census, rename/drop table, two save tools)
3ce539138 Ledger: HOSE_REEL_COUPLING_REDRAW_QUIT_STARING_BACK noted and closed at 8f9390e7ee by owner's card
8f9390e7e ReelIntakeGeometry regenerated from the plain-sleeve reel art; FlowWorks rebuilt (repo only)
bb843d66e Forge art installed via ledger: greater bulloo, metallovore, jobbosh/dhoggur/jurrox slot candidates (art only, no roster); greater bulloo def repointed to our path, donor guard dropped
e29156518 Install owner-accepted batch 02 art (wuum, oomb, greater/lesser oomb, siezer, lastvine calm+reared, sharpshrimp); slime and lastvine defs repointed to RM_ texPaths, Alpha Animals roster guards dropped
5ead1e026 Install owner-accepted batch 01 art (bed bug, crystal mit, zhool, blistered bulloo, zrrik); Contagion bulloos repointed to RM_ texPaths, donor roster guards dropped
... 174 more: git log --oneline ea5c0b4e0..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/scale_ground_measured.json   BENCH (not mine)
 M conversations/2026-10-14-0337-b833ee96.md   generated (session record)
 M infrastructure/state/ledger/events/OWNER.jsonl   his card events (ledger sweep commits it)
?? Transient/biome_ffar/img/00063bfc98bbf60c00c9.webp   BENCH (not mine)
?? Transient/biome_ffar/img/004678d5bc522129f222.webp   BENCH (not mine)
?? Transient/biome_ffar/img/0099e32f18695cf71e35.webp   BENCH (not mine)
?? Transient/biome_ffar/img/012b0e9de80257c66cba.webp   BENCH (not mine)
?? Transient/biome_ffar/img/0139244f2dcf4a25b9e9.webp   BENCH (not mine)
?? Transient/biome_ffar/img/0172b49133d12ef1a9d8.webp   BENCH (not mine)
?? Transient/biome_ffar/img/01fbc3e8db36f63ab5e8.webp   BENCH (not mine)
?? Transient/biome_ffar/img/0246ec2415ecfd9034c5.webp   BENCH (not mine)
?? Transient/biome_ffar/img/0365aef56ed78f6d87d8.webp   BENCH (not mine)
?? Transient/biome_ffar/img/037c682927ae2ff0ddef.webp   BENCH (not mine)
?? Transient/biome_ffar/img/03e20205e836860cb067.webp   BENCH (not mine)
?? Transient/biome_ffar/img/03e388a41435a8895e9b.webp   BENCH (not mine)
?? Transient/biome_ffar/img/046b4216ce4eef45833d.webp   BENCH (not mine)
?? Transient/biome_ffar/img/05c5e9c0a46d55d12961.webp   BENCH (not mine)
?? Transient/biome_ffar/img/06aa0e0bb52a2036646c.webp   BENCH (not mine)
?? Transient/biome_ffar/img/07b66a2274fb4d0778ae.webp   BENCH (not mine)
?? Transient/biome_ffar/img/07be76681b529c2f20aa.webp   BENCH (not mine)
... 572 more uncommitted paths (by top-level dir: Transient 569, conversations 1, deployed 1, infrastructure 1): git status --short
```

