# FOUNDRY_HANDOFF_202610190435 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610181652`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The game is UP on the donor-free 542-mod list with CANONICAL_ASHKARR_START_2026-10-18_DONORFREE.rws (ikee swapped to RSW_Ikee, bond to Yeku verified by state read; reload reports compatible, 542 recorded, 0 missing, zero new dead references). Live ModsConfig.xml and infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml are both the 542-mod list; Alpha Memes and the tail mods STAY (owner decides DONOR_TAIL_MODS_DECIDE_STAY_OR_GO). The running game still has the OLD texture fixes: deploy+restart picks up acb9d7245. Bench now owns FlowWorks; this seat does not edit it.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Bulk-accepted art (578 renders incl. 197 past his keeps/rejections, 20 donor-copy stand-ins, ~70 Alpha-Biomes ports with stand-in art, the 16 kept FloodedCanyon PNGs retired): his words were relayed through the coordinator; he said he will re-review later (NEXT filed).
- DONOR_TAIL_MODS_DECIDE_STAY_OR_GO: Alpha Memes, Alpha Genes, VFE Insectoids 2, Isopoda, Horrors, Cockroach, ReGrowth, Vanilla Genetics Expanded still on the list.
- Possible conflict: his 2026-10-16 "Sump... NOT snowing! No precipitation" vs the ruled tar rain in RM_TheSump (SUMP_TAR_LIVING_SYSTEMS_1 follows the specific ruling).
- AA_Behemoth promotion dropped from CreatureResize_Ashkarr.xml (RSW_Behemoth is a different animal); AngelMoth "C only" ruling no longer enforced in TheRot; Taozin wool now needs a patch against stat RSW_WoolTaozin.
- Guardrail A2 (setting persists) and A3 (walked-step refusal has no live control) are PARTIAL; rimflow shows the item validated anyway.
- Fall death at 7 m: 2-3 of 20-40; curve 0 up to 6 m is provisional.
- Beasts of the Rim was retired 2026-09-05 but still listed until today; removed.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `DONOR_FOUR_RETIRE_JUST_GET_IT_DONE` — A1, A4 pass, A2, A3 partial (mapgen on 16 biomes all generate; one MineralsFramework settlementDistProbFactor NRE per map, other mod; TheForge 0 animals; ROSTER Cauldron/Miasma fail on RM_Bileworm absent); NEXT: redeploy (deploy_custom_mods.py --apply + --compose biomes --apply), restart on the 542 list, then `python3 src/RimMandrake/Utils/harvest_donor_free.py` and expect texOurs 0 and xref 0.
- `ZRRIK_VAMPIRIC_STAB_REBUILD_OWN_BLOODLUST` — Zrrik lost its self-heal; NEXT: write our own bloodlust comp and wire RM_Zrrik.
- `FLOWWORKS_AB_FINDMOD_DELETE_LAST_HOLDOUT` — FlowWorks RM_PipeNetAdapters.xml still names Alpha Biomes; NEXT: Bench removes that FindMod (FlowWorks is Bench's).
- `RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY` — guardrail A3 unproven live; NEXT: add a force-one-step-over-the-edge hook or correct the criterion, then verify.
- `FALL_GUARDRAILS_BUILD_REAL_OBJECT` — validated with A2/A3 partial; NEXT: settle A2 (save/reload of pitGuardrailEnabled) once a settings-class bridge save exists.
- `DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO` — 765 job files, 38 filed, feeder timer rm-donor-regen-feeder.timer (lost on WSL restart); NEXT: re-arm with `donor_regen_jobs.py submit --jobs design/RimMandrake/donor_regen_jobs_2026-10-18.json` if the timer is gone, then `art_accept_finished.py --prefix dregen_` (dry run) and --apply as renders land.
- `TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING` — ~92 roster rows with renders that could not be matched to one destination; NEXT: match them by hand from the audit design/RimMandrake/biome_texture_regeneration_audit_2026-10-18.md and install.
- `NONSW_XENOTYPES_SCOPE_1` / `SUMP_TAR_LIVING_SYSTEMS_1` / `SCALD_WALKING_PASTURE_1` / `SANGUOPHAGE_KEPT_UNREACHABLE_1` / `TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER` — built, live checks owed (sithline mod not yet confirmed in the list; Cherry Picker --is-cut; tar rain on a non-campaign Sump map); NEXT: add mandrake.rsw.sithline to the list and run each item's owed L1/L2 on the next load.
- `BIG_CREATURES_DESIGN_WALLS_AND_SLOTS` / `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` / `CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD` — Bench has taken these with FlowWorks; NEXT: leave to Bench.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — 5 waves, ~84 files, 1 real bug (Ninefold); NEXT: only continue when the queue is empty; CauldronFuzz.cs/ContagionFuzz.cs remain DIRTY.
- `BUILDUP_BUILD_CLONES_STOP_BREEDING` — done; NEXT: add --apply to rm-scratch-reap.timer's service once the owner trusts the dry-run report (pushclone 11.9G, pubclone 7.6G, rebase_clone 6.8G need a human look).
- `DONOR_TAIL_MODS_DECIDE_STAY_OR_GO` — NEXT: put to the owner as a card.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A bridge/launch hold by a subagent is not permission: an agent was launched with game powers while Bench held the game (stopped before acting, as far as the transcript shows); confirm `rimflow bridge who` and the driver lock before delegating game work (filed: LESSONS).
- Session scratchpad clones can hold the only copy of unpushed commits; a disk cleanup lost CRACKEDLANDS_FULL_RENAME_1's three local commits (redone) (filed: LESSONS).
- `running_mods` is the truth about what loaded: a 26-mod minimal game ran while ModsConfig said 544; always compare jawa/running_mods to the file (see: harvest_donor_free.py --running-mods).
- Windows cannot hold case-twin files (PaleTree_B.png vs _b.png): the biomes compose never converged until one was retired through artledger.retire (filed: LESSONS).
- A stale unresolved bridge-journal entry (step_game_ticks) blocks every non-read-only call until `rimbridge_client.py --reconcile --resolve` with evidence (see: rimbridge skill).

## Commits

```
d3945fddd ledger: acceptance verifications for donor retirement; game state events
2705e5680 Transient: pin donor-free mapgen L1 result
7d7652b06 review: 7 FlowWorks/HugeThings files clean; file TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG
25f465291 HugeThings: titan squeeze backs out on job expiry (Succeeded with done=false left it in the gap)
28e5987ad review: RM_WallClimb.cs and RM_PocketGridMath.cs clean at 9b14d46036
9b14d4603 FlowWorks: drop dead ReachVetoedAcross (ReachVetoedWhole decides); RelativeVeto doc names the ladder graph
d0e00ddd3 Fix 3 donor-free texture failures: Noothelm/LungerFry stand-in art, Salvessa immature folder path
ba169dedc ledger: thirst regressions reassigned to BENCH for offline diagnosis
1dd2b3be1 ledger: TITAN_TRENCHES_WIRE_MIND_THE_GAP implemented at 5a98a31d4e; live rows A1-A5 owed
5a98a31d4 FlowWorks+HugeThings: titans step over trenches narrower than B/4 (TITAN_TRENCHES_WIRE_MIND_THE_GAP)
7f6f9754f ledger: RAIDER_TRENCH_FIX_REACH_BOUNCE and WALL_CLIMB_FIX_BUDGET_CAP_LEAKY_MEMOS closed at dea256e4e04b; live rows owed; note to titan trenches
dea256e4e FlowWorks: reach agrees with A* across trenches; wall-climb caps 3 pathfinds/tick, memos cleared on load
05df9733a FlowWorks: walk under suspension bridges, sunken bridges, crush below (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD)
75f7afe95 HugeThings: mock-runnable live script for BIG_CREATURES A2-A8 (walls_slots_live.py); flowworks_hugethings tier; plan section 8
f32cb1cee ledger: HUGE_WALLS_FIX_DECIDER_RETRIES_FOREVER closed at ca7e9515e2; review marks
ca7e9515e HugeThings: walls/slots decider cools down unreachable destinations; held crossings pruned (HUGE_WALLS_FIX_DECIDER_RETRIES_FOREVER) Per-creature 600-tick UnreachableMemo (rebuilt, cleared on a backwards tick); HeldBook pruned of dead/despawned creatures, gone maps, expired entries. Fuzz families memo, heldprune.
af5dd3059 FlowWorks: register wall climb, raider trench, swim, water mend settings; review 12 files clean, file 3 fix items
0a79327f2 ledger: wall-climb routing and raider gear follow-up done at 52e55c61d1; 5 live rows owed; hook note to big creatures
5508fc144 ledger: TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP implemented (c2c7302a52, DLL b466a50bed); live rows A2-A3 owed; notes to wall-climb and big-creatures
6ca807824 FlowWorks: rebuild DLL from clean HEAD (stamp matched the sources of three interleaved commits)
... 252 more: git log --oneline dd68458cd..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   generated (untracked Transient scratch, not pinned; other seats/agents)
 M Transient/modcheck/fixtures.json   generated (untracked Transient scratch, not pinned; other seats/agents)
 M conversations/2026-10-16-0549-c453ca3a.md   generated (conversation records; catch-up landing is the handoff conversations_land step)
 M conversations/2026-10-16-1218-9a5985c9.md   generated (conversation records; catch-up landing is the handoff conversations_land step)
 M conversations/2026-10-16-1839-6972cfb2.md   generated (conversation records; catch-up landing is the handoff conversations_land step)
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   generated (modset_builder tier-swap backup)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_p00.png   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_p03.png   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_p10.png   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S1_p14.png   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S2_p00.png   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S2_p10.png   generated (untracked Transient scratch, not pinned; other seats/agents)
?? Transient/fw_scenes/live/S2_p30.png   generated (untracked Transient scratch, not pinned; other seats/agents)
... 140 more uncommitted paths (by top-level dir: Transient 128, deployed 5, conversations 3, src 2, (root) 1, infrastructure 1): git status --short
```

