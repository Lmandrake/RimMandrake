# FOUNDRY_REBOOT_HANDOFF_202609251428 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609250325`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A cold restart onto the full 626-mod list this session found that three creature defs
built THIS SAME SESSION (`RUT_BrineBattery`, `RUT_EmperorVulture`, `RUT_MortuaryCrawler`)
shipped with invalid diet values, which crashed GeneticRim at startup and broke ALL
pawn/animal creation game-wide — the campaign save loaded with 0 pawns on the home map.
Fixed (`2db13d541`), second restart came up clean. **Building a def offline-clean
(`validate_patch.py` passing) is not proof it won't break pawn generation — only a real
load does that.** Multiple agents this session built content and closed items on
offline validation alone because the bridge was busy; that is the correct call under
contention, but it means a live load is now doubly owed before the next save-affecting
change, not a formality.

## What the owner should see

- **Twilight Sea is entirely deep water — nothing on it is fishable**, which contradicts
  the "make the surface fishable" ruling behind `FISH_BESTIARY_BUILD_1`. Needs either a
  terrain fix (some shallow/margin tiles) or a scope call that Twilight stays deep-only.
- **A colonist revived by Bacta after a heart-destroying wound comes back with no heart
  and just dies again** (`BACTA_REVIVAL_MECHANIC_1`) — needs a ruling: refuse such bodies,
  or have Bacta regrow the missing vital organ.
- `mandrake.rsw.bacta` had silently dropped out of the 626-mod `ModsConfig.xml` list
  before this session (restored this pass) — worth a glance at whatever process last
  edited that list, since a mod vanishing from it with no one noticing is exactly the
  failure mode the game-breaking bug above rode in on.
- The live restart-and-verify batch (23:04–01:25, ~2h20m) is the fullest single-session
  live-game proof this project has run in a while — full per-item results are in each
  item's own file (`FISH_BESTIARY_BUILD_1`, `SUMP_GASLIGHT_1`, `BACTA_REVIVAL_MECHANIC_1`,
  `BACTA_SIDE_ITEMS_1` closed, `LIQUID_BOTTLE_LOOP_1`), worth a look if you want the
  granular detail behind the summary above.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `BACTA_TANK_ART_1` — claimed+started at 2026-09-25T03:45Z, two minutes before another
  live FOUNDRY window's FireHawk bridge hold began; item file has no `##` sections and
  no commit exists under this item name from this window's work. NOT touched by this
  window despite showing `doing` under the shared FOUNDRY seat. NEXT: confirm with
  whichever window actually claimed it whether any art work happened, then either
  continue it for real or `rimflow drop`/reclaim if it was an accidental claim.
- `FORCE_DISTURBANCE_REFLAVOR_1` — `doing`, re-gated `needs: owner`. Flavor-text patch
  drafted and validated (0 errors, 34/34 xpaths), not deployed. NEXT: BENCH cards the
  exact wording for the owner's approval, then deploy and close.
- `SHIELD_MODS_LEVERAGE_1` — `doing`, `needs=bridge`. All 4 ruled shield fields now
  built (cryo envelope completed this session), two false statements in existing code
  fixed. NEXT: take the bridge, spawn the generator, cycle to Cryo, confirm temperature
  behavior + landing/escalation warnings, deploy, close.
- `THEY_MOD_REPLICATION_1` — `doing`. New standalone mod + C# built and validated
  (0 errors, 73/75 selftests). NEXT: BENCH cards the coined pseudo-Star-Wars label
  (owner naming decision), then once the 8 queued art jobs render and the bridge is
  free, live-verify and remove the donor from `ModsConfig.xml`, then close.
- `VANILLA_BEAST_EXCISION_1` — `doing`. Roster wiring confirmed already vanilla-free;
  the real gap is the vanilla ThingDefs themselves are not yet Cherry-Picker-cut (open
  manhunter/wander-in/self-tame/quest-reward/trader-stock/pack-animal routes). NEXT:
  execute the Cherry Picker cuts per the census in the item file, biome by biome, then
  the non-roster route audit, then a live full-mod-list verify.

## Traps learned

- `validate_patch.py` clean does not mean a def survives a real load — three new
  creature defs with bad diet values crashed GeneticRim and broke all pawn creation
  game-wide, only caught by an actual cold restart (filed: LESSONS_INBOX).
- Bridge-lock "idle" time in the rimflow ledger only counts rimflow events, not real
  GABP calls — a subagent mid-live-verify can read "idle 58 min" while actively driving
  the game the whole time; don't infer a stall from it alone (filed: LESSONS_INBOX).
- `prove_fish_bestiary_live.py` itself had three instrument bugs voiding its own
  verdicts, fixed this session (see: commit `5488e4ddf`).
- A subagent that launches `run_in_background`/`Monitor` then waits for a notification
  deadlocks — it never arrives for a subagent, only the parent. Hit twice this session
  despite briefs already warning against it; the fix is a `SendMessage` nudge telling it
  to poll synchronously itself (see: `subagent-background-wait-deadlock-brief-line`
  memory, `efficient-subagents` skill).
- Screenshotting/photographing a creature to prove it is mid-flight does not work as a
  verification method — owner ruling, said three times this session (filed:
  LESSONS_INBOX; see also `CLAUDE.md`'s flight section and
  `FIREHAWK_FLIGHT_BEHAVIOR_1`).

## Closed since the last handoff (11)

- `CRACKED_LANDS_SEALED_WAKE_MECHANISM_1` — b36048f26
- `FEVER_WOOD_MECHANICS_1` — 2deb790184a27a3b5412d66c660caea075b1eccc
- `WASTELAND_BRINE_BATTERY_CREATURE_1` — 46fa03e5e5ca72f6fb3526b8532490931b78343d
- `WASTELAND_EXCRETOR_BEZOAR_1` — 46fa03e5e5ca72f6fb3526b8532490931b78343d
- `STOCKED_POOL_BUILD_1` — bf8820260a2fecae3146f01007bbe94678ab1f3c
- `PROPANE_LAKE_PIPE_MECHANICS_1` — 1f4d212710b14b2e05baad92f6d4cd667af00ca4
- `MIASMA_KARRATHIL_POLLINATION_GATE_1` — 1521b90acb545c5f33b3988b2ec8ca4889f56b0a
- `ROSTER_DEAD_BMT_NAMES_SWEEP_1` — 0e7e47af7b84cc1ca09983a31409ebbe5cbafda7
- `VQE_ANCIENTS_CURATION_1` — a3cfeee65
- `GOO_BOOM_COMMISSION_1` — b00ea42728e8edcae978858e54705abed4a519b9
- `BACTA_SIDE_ITEMS_1` — 5b9defb0fe696b036432a2fb073bbec2c8d20eed

## Filed and still open (10) — the next seat's queue

- `WASTELAND_RADIOTHERMAL_SOLITARY_1` — Radiothermal solitary: living-furnace creature, NEW C# heat-emission + same-species spacing law (no donor emits heat per _assignment_prep.md 4.4 -- ne
- `WASTELAND_STORM_WEATHER_DEFS_1` — Owner ruling owed: the three Wasteland storm WeatherDefs (ash / radiation-halo / plasma-terminator-only) need a scope ruling on the storm map-reshuffl
- `WASTELAND_SHIPPING_NAMES_1` — Owner card: name RUT_DosimeterLawn (radiotroph lawn) and RUT_VaultRoot (sequestration tree), the two wasteland working names minted this wave
- `GREENTIDE_YEARNING_FRUIT_1` — Digestive-accelerant fruit (the fruit that yearns): plant def + eat-fast/pass-seed hediff + filth C#
- `CONTAGION_UNFINISHED_SPAWNER_1` — The Unfinished: random-stat short-lived chimera spawner (random Hediff_AddedPart limbs, days-long life, dissolves to goo)
- `WASTELAND_BRINE_BATTERY_DISCHARGE_1` — Brine battery ion-gradient discharge: EMP/zap defense comp on RUT_BrineBattery
- `GREENTIDE_YEARNING_FRUIT_FILTH_1` — Yearning fruit's filth/seed-dispersal comp: pass-seed + filth on digestion, same shape as RM_HediffComp_ShadeStagger
- `GREENTIDE_SHIPPING_NAMES_1` — Owner card: name RUT_YearningFruit (the fruit that yearns) and RSW_CanopySwinger (the Swingers), two greentide working names
- `DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1` — grain-scale commensal fauna riding RM_MirrorGiant's shade
- `FLOWWORKS_DONOR_AFFORDANCE_GAP_1` — FlowWorks liquid terrains reference donor TerrainAffordanceDefs (BMT_DeepWaterBridgeable x38, TST_TerrainForMeditationStone x19) that break standalone

## Commits

```
b598171bc Ledger sync: close BACTA_SIDE_ITEMS_1, block four live-verify items, bridge release
5b9defb0f Live-verify batch on the full 627-mod list: results for five items
5488e4ddf prove_fish_bestiary_live: fix three instrument bugs that voided its verdicts
5fb3dd079 FlowWorks bottles header: delete the false "no tank building exists" claim
8d3af1636 Ledger sync: SHIELD_MODS_LEVERAGE_1 claim/start/note/verify (cryo envelope)
8193255c7 SHIELD_MODS_LEVERAGE_1: build shd:cryo-envelope, the last unbuilt ruled shield
b0377e47b RIVER_STEAM_ANIMATION_1: offline re-verify pass (bridge held by a peer window)
37e1c92fa HELIX_TELLUROX_BUILD_1: re-verify offline, still correctly blocked
456c7d5e4 Ledger sync: GOO_BOOM_COMMISSION_1 unblock/close (RUT_Vhessk built)
b00ea4272 GOO_BOOM_COMMISSION_1: build RUT_Vhessk, the one boom creature that replaces the cut family
feddf8808 THEY_MOD_REPLICATION_1: replicate They! (Giant Ants) in our own tier
f70984178 DONOR_DEFS_PORT_TO_OURS_1: census the ten smaller donors (spec step 1)
2db13d541 Fix four defs the full load discards: Bacta field items, three RUT races
99e465258 Ledger sync: re-render queue projections after VQE_ANCIENTS_CURATION_1 close
8a10813c2 Ledger sync: VQE_ANCIENTS_CURATION_1 unblock + close
a3cfeee65 VQE_ANCIENTS_CURATION_1: close out steps 1/2/4 verification gaps
b9e9e6db5 RUT_SCAVENGEREVENTS_BUILD_1: license check, stale-scope fix, dead row cleanup
2475856ba Ledger sync: ROSTER_DEAD_BMT_NAMES_SWEEP_1 closed, prose moved to closed/
0e7e47af7 ROSTER_DEAD_BMT_NAMES_SWEEP_1: close — both owner-judgment calls landed elsewhere
4708b0400 COMMISSION_LEDGER_CLEANUP_1 wave 14: re-checked, all 6 remaining groups still contended
... 85 more: git log --oneline 40f767de7..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-25T08:24:17Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
D Transient/_focus_check.bmp   unclear origin — pre-existing scratch screenshot, not from this window's captures (this window's are named game_state_check*)
 D Transient/_focus_now.bmp   unclear origin — pre-existing scratch screenshot, not from this window's captures (this window's are named game_state_check*)
 M Transient/codebase_health.html   ambient — codebase-health dashboard auto-rebuild (triggered by rimflow activity this session), not hand-edited
 M Transient/codebase_health.json   ambient — codebase-health dashboard auto-rebuild (triggered by rimflow activity this session), not hand-edited
 M Transient/codebase_health_artifact.html   ambient — codebase-health dashboard auto-rebuild (triggered by rimflow activity this session), not hand-edited
 D infrastructure/artpipe/_artsrc/lockjaw_improve_a_r7/lockjaw_improve_a_r7.png   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/_artsrc/lockjaw_improve_b_r7/lockjaw_improve_b_r7.png   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_cundral_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_wildhealroot.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutbloomcrop_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutdarkcrust_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutdeltaloam_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutemperorvulture_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutemperorvulture_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutemperorvulture_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfleetflier_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfleetflier_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfleetflier_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfuzz_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutglower_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutglowercrust_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutkarrathil_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutkarrobel_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutstaggerseed_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutstaggerseeddish_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/pending/rutwelcomeblanket_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/dashboards/hub/data/health.json   ambient — codebase-health dashboard auto-rebuild (triggered by rimflow activity this session), not hand-edited
 M infrastructure/state/codebase_health_last.json   ambient — codebase-health dashboard auto-rebuild (triggered by rimflow activity this session), not hand-edited
MM infrastructure/state/queue/BENCH.md   FOUNDRY (this window) — queue-projection re-render churn from many concurrent closes this session; safe to regenerate via `rimflow render -- --overwrite-queues`
 M src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll   FOUNDRY (this window) — DLL rebuild artifact from the live-verify batch pass; verify still matches source and commit, or discard if stale
 M src/RimMandrake/Utils/modset_builder.py   prior FOUNDRY window (FIREHAWK_FLIGHT_BEHAVIOR_1's one-off 'firehawk' quicktest tier) — said to be discarded after use but still dirty; verify and revert or commit for real
 M src/RimUtinni/LanternDeeps/Assemblies/RimMandrake.Utinni.LanternDeeps.dll   unclear origin — not touched by any agent this window dispatched; likely another concurrent window's build
D  src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgaricusDomeCap.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agarilux/Agarilux_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/AgariluxPrime.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_east.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_north.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Agaripawn/Agaripawn_south.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/ArbuscularMycorrhiza/ArbuscularMycorrhiza_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Bryolux/Bryolux_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/DribblingCap/DribblingCap_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/GiantAgarilux/GiantAgarilux_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/GlowingAgarilux/GlowingAgarilux_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Glowstool/Glowstool_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/LilacBeacon/LilacBeacon_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_east.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_north.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/MycoidColossus/MycoidColossus_south.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/RecurvedStropharia.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/SlimyPholiota/SlimyPholiota_A.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_east.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_north.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Swarmling/Swarmling_south.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_east.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_north.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpawn/Wildpawn_south.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_east.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_north.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/Wildpod/Wildpod_south.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
D  src/RimUtinni/UtinniPatches/Textures/RotSpecies/WitchesOyster.png   another live FOUNDRY window's THEROT_RM_MOD_BUILD_1 biome-mod-split migration (confirmed via wave-14's git-log check) — mid-flight, do not touch
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY (this window) — tier-swap backup config from this session's quicktest-tier building; safe to leave or clean up
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY (this window) — tier-swap backup config from this session's quicktest-tier building; safe to leave or clean up
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_wildhealroot.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfuzz_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglower_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglowercrust_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvaultroot_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   ambient — artpipe daemon (background, continuous), failed-job bucket; not this window's
?? infrastructure/artpipe/pending/crags_brekkugar_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_brekkugar_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_brekkugar_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_dhukk_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_dhukk_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_dhukk_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_ghorrumak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_ghorrumak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_ghorrumak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_gruzz_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_gruzz_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_gruzz_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_hulggarok_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_hulggarok_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_hulggarok_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_kessik_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_kessik_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_kessik_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_shekkur_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_shekkur_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_shekkur_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_vrakk_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_vrakk_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_vrakk_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_zekkra_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_zekkra_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_zekkra_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_bladderboilcatch_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_noohm_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_noohm_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_noohm_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_saalcatch_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_shulla_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_shulla_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_shulla_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_shullacatch_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_steamcatchbuilding_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_ventbuilding_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_wreckframe_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_wreckhull_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/scald_wrecktank_v1.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_bezzul_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_bezzul_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_bezzul_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_hennul_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_hennul_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_hennul_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_oomb_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_oomb_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_oomb_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_thummorak_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_thummorak_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_thummorak_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_vohhm_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_vohhm_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_vohhm_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuppik_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuppik_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuppik_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuum_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuum_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuum_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_yollum_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_yollum_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_yollum_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   ambient — artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing (2026-09-11), not this window
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing modlist backup snapshot, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing modlist backup snapshot, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing modlist backup snapshot, not this window
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing modlist backup snapshot, not this window
?? src/RimMandrake/Utils/firehawk_flight_probe.py   another live FOUNDRY window — building the Pawn_FlightTracker state-read tool per this session's no-screenshot-flight-testing ruling on FIREHAWK_FLIGHT_BEHAVIOR_1; in progress, not this window's
```

