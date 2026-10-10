# BENCH_REBOOT_HANDOFF_202610102057 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610101044`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Art review is PAUSED (owner, 2026-10-10 ~14:00: "We have used up our ability to regen art"). Focus is now entirely validation, debugging and growing mods to maturity and completion.** Do not queue art jobs, rebuild sheets or enact sheets until he lifts it. Everything art-side below is parked, not abandoned: the redesigned schema-2 sheets are built, migrated (789 decided rows proven identical) and 15 are still served; the preview was Greentide Peko-peko and he saved decisions on it at 13:55 (committed 5e76f2e31) without commenting yet.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Story sitting is complete — all 22 cards ruled** with his typed words in `design/Jawa/story_sitting_cards_2026-10-10.md`, and propagated into the lore docs (43583cae, fee27cf06). One answer is ambiguous: card 14 "first launch" — he described the OPENING theft flight; whether a later relaunch has its own tone is unasked.
- **Art redesign self-reported 297/369 selftests** while naming only 4 known failures — ~70 are unaccounted for (crashed/skipped?). Not verified clean.
- **Two picks now show as conflicts on the redesigned sheets** (living-creature renders picked on catch rows): Rust Cathedral RM_CoolantEelCatch C, Twilight Sea RM_NuudalCatch C.
- **Old-ticks confirm sheet** (627 ticks, 309 on random pools) is served at http://localhost:38677/?t=zqVPucphxnO2UDkfwfBpyA — parked with art review; nothing ships from those ticks until he confirms.
- **Rot naming sheet** (14 names, 3 options each) still served at http://localhost:33533/?t=S0BNe6__FjYqr_YqERSFmw — unanswered, parked.
- **Mod list:** 14 vanilla-upscaler mods removed from `ModsConfig.FULL.LATEST.xml` (565→551) by his card; SimpleCameraSetting removed from the live list. Faces/races/facial-animation mods kept by his typed word.
- **Not yet deployed (game was running):** Ollopom outdoor-beauty DLL (da4180f3f) — run `deploy_custom_mods.py --compose biomes --apply` then `--mod SWBestiary --apply` once the game is closed; the game copy holds the OLD RSW_Ollopom.xml on purpose until the DLL lands.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `ART_REVIEW_PAUSE` — owner paused all art review/regeneration 2026-10-10; NEXT: do not touch art until he says it resumes, then start by asking him for comments on the Greentide Peko-peko preview row.
- `OLLOPOM_BEAUTY_DEPLOY` — built + tested, not deployed (DLL locked by running game); NEXT: when the game is closed, run `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply` then `--mod SWBestiary --apply`, then its `validation.py perceived_beauty` check on the next live session.
- `ART_SHEET_SELFTEST_GAP` — redesign reported 297/369 with only 4 named failures; NEXT: run `python3 src/RimMandrake/Utils/run_selftests.py` and account for every non-pass before calling the redesign clean.
- `WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE` / `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE` / `WARLAB_GARRISON_DESIGN_EARLY_BLAST` / `SEKKULAATH_RISING_DESIGN_CRATER_EVENT` — filed for BENCH from the story sitting; NEXT: draft each as a short option card for him when design time returns (validation/debug comes first now).
- `MATERIAL_MERGE_LOAD_CRASH_1` — from the previous handoff, FOUNDRY's; NEXT: check its ledger state before any full-list cold load.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `./publish` autostashes in a dirty shared clone and can strand other windows' work in stash@{0} (53 files, incl. served sheet HTML) (filed: LESSONS 20261010T164936Z).
- A PreToolUse hook refusing a compound Bash call drops the WHOLE call — a heredoc file write chained with a commit silently never happened (see: CLAUDE.md "Tools with surprising side effects").
- The push hook lints the LOCAL HEAD: pushing a temp-index commit from a clone whose HEAD is behind origin is refused as "NOT_APPEND"; push the literal sha from a clone at origin/main (scratchpad `land` clone) (filed: LESSONS 20261010T205804Z).
- zsh: `"$c:refs/heads/main"` applies the `:r` modifier and mangles the refspec — write `"${c}:refs/heads/main"` (see: CLAUDE.md zsh traps).
- `art.py enact` had five silent failure classes (vanilla-path picks counted live, ticked variants dropped, rename/description halves dropped, rejected art as reference, catch art before the creature) — fixed with selftest_enact_ws.py; independent verify-after-enact found every one (see: Transient/biome_ffar/weepingstones_verify_2026-10-10.md).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (9) — the next seat's queue

- `PLANET_ATMOSPHERE_CLOUD_COST_1` — Measure Planet Atmosphere 8K cloud cost: load-time and VRAM A/B with and without the mod (owner Q2 = measure first; spec Transient/texture_mod_review_
- `WEEPINGSTONES_SETTLED_FOLLOWUPS_1` — Weeping Stones: Vellak description after art, 5 catches waiting on their creature, huldu fur question
- `RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT` — Reclamation trigger: rewire the built 45-day chain delay to a woken-ancients count (owner card 13, 2026-10-10)
- `WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE` — War lab specimens: design the player's containment choice, the breakout, the recover-or-fail beat (owner card 3, 2026-10-10)
- `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE` — Cradle strike on the war lab vs the player's own lab dive: reconcile (owner card 11, 2026-10-10)
- `WARLAB_GARRISON_DESIGN_EARLY_BLAST` — Early lake blast: Empire heat rise + Imperial garrison outside the revealed war lab (owner card 8, 2026-10-10)
- `SEKKULAATH_RISING_DESIGN_CRATER_EVENT` — Sekkulaath rises in the crater event: Wildsteam site damage, closed world sites (owner card 19, 2026-10-10)
- `ASSAILANT_WARLAB_BUILD_MERGE` — Assailant complex IS the war lab: fold ASSAILANT_DUNGEON_BUILD_1 and ANCIENT_WAR_LAB_1 into one build, reconcile core-socket thaw vs two-key gate (own
- `SPIRE_DUNGEONS_MERGE_DARK_TOWER` — Spire IS the Scald dark tower: reconcile the two built dungeons (SCALD_DARK_TOWER_1, ASHFALL_RESEARCH_BASE_1) as one building (owner card 6)

## Commits

```
5e76f2e31 Greentide sheet: owner's decisions saved on the redesigned sheet preview (13:55), art review paused
504a3c795 launch_and_wait.sh: restore the executable bit (it was 100644, so the documented call failed with 126)
f34b77501 preflight_bridge O02: read the holder after the HELD token
2d5b08e0f FOUNDRY ledger + bridge-improve B progress log (preflight/lint/manifest items implemented)
3815260a2 preflight_bridge O13: byte-exact deploy match in seconds (Windows walk via python.exe)
b80e7accf Rename preflight.py -> preflight_bridge.py: it shadowed live_queue's preflight module
9d315a76f Art sheets: renders named as flight/young/catch frames leave body lanes for UNASSIGNED; ruled by-name renders never fall back into the body lane
54a71044d Progress log: FOUNDRY bridge control-plane pass A
eb55f0a47 FULL gap proposal: 14 mods with insert points, gated on a clean 551 cold load (owner ruling)
0e4bb3b6e preflight: parse About.xml packageIds, tasklist presence, modmanifest lists, flushed rows
27edb8a0e Durasteel convert covers ore + work-site refs; phrikite Stillsand gate uses AnyOf
447dd1324 Ledger: companion safety tickets implemented (fd2375d54)
fd2375d54 Companion profiles: campaign keeps authoring, refuses only debug/test/heavy-diagnostic/quiet-world
fee27cf06 Delete stale Spire plot-prep doc (G80): it still said the Spire function was unruled; the Key ruling and the 2026-10-10 sitting stand
50fc88e51 ledger: file 7 items from the 2026-10-10 story rulings
43583caed Story rulings 2026-10-10 propagated into lore docs; 7 items filed
e45bd904f Bridge pre-flight: preflight.py, effective_def_lint.py, experiment_manifest.py
70d7d862f FOUNDRY ledger: file/claim/implemented six bridge control-plane items
87d8821c2 Per-call bridge evidence + INDETERMINATE mutation block (BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN)
bd7e0ec3e Companion: guarded TPS hooks, safe-by-default profile gate, stale-target refusals, handshake, lazy GeneratePawn
... 207 more: git log --oneline b022e2a5c..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : DOWN  → corrected to LOADING, measured now
- Bridge: for     551 cold load + live proofs

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/abyss_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/blue_desert_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/cauldron_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/contagion_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/deep_desert_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/desert_sheet_2026-10-04.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/feverwood_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/feverwood_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/floodedcanyon_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/floodedcanyon_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/gelatinousslime_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/greentide_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/greysea_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/greysea_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/lanterndeeps_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/leaningscrub_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/miasma_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/nightsideice_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/pyrelands_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/rustcathedral_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/sheets_state.json   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/thechill_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/theforge_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/theforge_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/therot_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/thescald_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/thesump_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/twilightsea_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/warscar_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/wasteland_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/wasteland_sheet_2026-10-05.serve.log   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/webwork_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/biome_ffar/weepingstones_sheet_2026-10-05.html   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   — BENCH: served review-sheet HTML/logs/state (rebuilt for the redesign; HTML commits are hook-blocked by design)
?? conversations/   — pre-existing untracked leftovers from earlier sessions, not this window
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   — pre-existing untracked leftovers from earlier sessions, not this window
?? deployed/config/ModsConfig.before-tier-flowworks.xml   — pre-existing untracked leftovers from earlier sessions, not this window
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   — pre-existing untracked leftovers from earlier sessions, not this window
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   — pre-existing untracked leftovers from earlier sessions, not this window
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   — pre-existing untracked leftovers from earlier sessions, not this window
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   — pre-existing untracked leftovers from earlier sessions, not this window
```

