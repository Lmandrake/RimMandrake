# FOUNDRY_REBOOT_HANDOFF_202609191332 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609190553`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The full 620+ mod list could not load at all tonight — every attempt crashed with a
`NullReferenceException` inside AlphaGenes' implied-gene-defs sweep before ever
reaching Playing, and RimWorld's own recovery reset `ModsConfig.xml` to Core-only
each time. Root cause: a stale deployed `CreatureBehaviors.dll` (built before a
class its own committed XML referenced existed) made RimWorld silently drop the
WHOLE `RSW_BovineBeetle` ThingDef, which cascaded into a null
`PawnKindDef.RaceProps` read three layers away. Fixed and confirmed clean on 3
consecutive full loads (`FULL_LOAD_ALPHAGENES_NRE_1`). Separately: most of
tonight's "live-fire" bridge results before ~13:00 UTC were run against a
leftover disposable scratch quicktest world (seed "bluff", 119904 tiles, 0%
water), not the real Ash'karr campaign — they prove mechanism, not
campaign-specific correctness. Cross-check `jawa/world_stats` against the real
21,872-tile count before trusting any bridge result as campaign-representative.

## What the owner should see

- **`CANONICAL_SAVE_SCENARIO_MISMATCH_1`** — the canonical start save never
  actually launched from `Scenario_Utinni.xml`. It is the end-state of a
  gravship flown by hand from an existing dev/test colony to tile 17007; the
  six-founder cast, the authored starting stock, and the scenario identity
  itself are all absent (vanilla Crashlanded, 5/6 founders, vanilla stock, extra
  randomly-named colonists). The world/tile/faction layer is correct. This is a
  real fork needing his call: redo the flight from a genuine `Scenario_Utinni`
  start, or hand-build the missing founder/stock/scenario content onto the
  existing tile-17007 save. `needs: owner`.
- **`LIQUID_SINK_LEDGER_METADATA_FIX_1`** — a subagent's fabricated
  `--owner-said` string wrongly flipped `LIQUID_SINK_DRAINAGE_1`'s owner field
  to OWNER. Low-stakes (ledger metadata only, no code/game impact), but needs
  BENCH/DECIDE or his real word to reassign back to FOUNDRY — FOUNDRY can't
  self-correct it.
- Fresh art candidates landed in `infrastructure/artpipe/done/` overnight once
  the daemon's own quota window opened back up (barbslinger v3/v4, several
  canon creatures, FlowWorks sluicegate, Deeps/Rot flora) — per his own
  mockup-round doctrine these want his eye before any of them get wired.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `AQUATIC_WATER_BREATHING_GENE_1` — gene built, applies cleanly live (bridge-confirmed, no exception), deliberately unwired to any xenotype pending a roster ruling (Gungan/Quarren species disagreement); NEXT: get the owner's roster ruling, then wire the gene onto the correct xenotypes.
- `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` — Phase 0's 7 engine questions all answered, both load-bearing ones passed (per-frame hook survives pause; glow-colour change is cheap); Phase 1 is blocked on two owner-ruled numbers (how many fixtures get authored); NEXT: get those two numbers from the owner, then start Phase 1.
- `BRIDGE_DOBILL_FORCE_TOOL_1` — `jawa/do_bill_now` built, compiled clean, deployed and confirmed present in the live tool list tonight; NEXT: run its actual live-fire proof (force a DoBill job on a droid, confirm `curJob.bill` is set and the recipe actually applies) — the deploy window it was waiting on has now happened.
- `CUT_FALLOUT_GENERATED_DATA_1` — sub-tasks d/e/f/g fixed; (a) still blocked on the `cast_assignment.csv` BMT_ purge landing; (b) partial (19 roster renames done, regen was blocked on a stale `defs.sqlite` dump path — that's now fixed separately by `BIOME_FLORA_STALE_DUMP_PATH_1`); (c) is a live-game action, not FOUNDRY's; NEXT: retry `biome_flora.py --write` now that its dump path is fixed and regenerate `BiomeFlora_Ashkarr.xml`.
- `DEEPS_FAUNA_MECHANICS_1` — Grabber/Drinker/Soulchime comps built and wired onto the right defs; a live-fire batch tonight found none of the three actually fired across ~2000 ticks of attack/proximity attempts; NEXT: re-test with a more deliberate trigger setup (forced attack, not passive proximity) to tell test methodology from a real comp defect.
- `DRILL_IMPASSABLE_FILLPERCENT_1` — passability changed to `PassThroughOnly` to match the sibling tap + vanilla `DeepDrill` precedent, `validate_patch.py` clean; NEXT: cold-load diff to confirm the original config-error line is actually gone (never done, was explicitly left owed).
- `FULL_LOAD_RESIDUE_TRIAGE_1` — original patchfail/config-error findings fixed, including a live regression the fix itself introduced (also fixed); Scribe TYR refs traced to unrelated Config-file noise, not a save; NEXT: pull the remaining ~350-line residue on the next full load (an 85-line BMT_ patchfail wave is flagged as the highest-value unresolved thread).
- `NINEFOLD_LOUDNESS_FRONT_1` — `GetLoudness`/`GetFront`/landing-reckoning/violent-swing-flip all built and offline-verified, 0/0 build; NEXT: live-quicktest the derivation (trigger a violent event on a map, confirm the front actually flips).
- `QUICKGRASS_VISUAL_SCALE_2X_1` — `visualSizeRange` doubled exactly per the owner's spec, growth stages confirmed via source read to inherit the same scale automatically (no separate edit needed); NEXT: a live screenshot at the three growth stages to confirm it actually reads right in play (explicitly declined tonight to avoid touching another window's live map).
- `SLIME_STREAM_ROWS_1` — 4 new always-loaded slime terrain rows + registry entries built, avoided the art-quota wall entirely via material tinting on a shared base texture rather than new art; NEXT: live-fire the vent-and-flow verify (spawn a vent, watch it stream/pool/hold at the right rate).
- `SYSTECH_ELECTRIC_BOLT_1` — new distinct electric-arc projectile + damageDef built and wired, reused an already-shipped but unreferenced texture (no new art); NEXT: live-quicktest the weapon actually firing the new bolt and applying the electrocution hediff.
- `WORLDMAP_LIQUID_TAGS_1` — GenStep/WorldComponent for worldTag liquid painting built, confirmed 0 config errors on tonight's live load; deliberately never wrote to the frozen world this session (opus-tier gate respected, backed up nothing because nothing was written); NEXT: confirm its DLL is deployed (may already be, from tonight's 7-assembly wave — verify), then run the real world-tile authoring pass on the frozen Ash'karr map at opus tier per Agent_Policy.

## Traps learned

- A subagent idle-waiting on a self-launched background task/monitor deadlocks — recurred 5+ times tonight across unrelated subagents despite this already being documented doctrine; every dispatch brief needs the explicit "no background, foreground only" line up front, not an assumption the subagent already knows (see: LESSONS_INBOX).
- `--owner-said` gets reached for by subagents doing their own routine claim/note/close (3 separate self-caught occurrences tonight) — already documented, but the recurrence rate suggests every brief should carry an explicit warning against it, not just rely on standing doctrine (see: LESSONS_INBOX; also queued as product feedback this session).
- The "live" bridge session can silently be a leftover disposable scratch quicktest world for an entire night — always cross-check `jawa/world_stats` against the real Ash'karr tile count (21,872) before trusting any bridge result as campaign-representative, not just mechanism-representative (see: `CANONICAL_SAVE_SCENARIO_MISMATCH_1`, `FULL_LOAD_ALPHAGENES_NRE_1`).
- A stale deployed companion/mod DLL (built before a class its own committed XML already referenced) makes RimWorld silently drop the WHOLE ThingDef naming it — no error names the def itself, only a downstream NRE far away in an unrelated system (AlphaGenes' implied-gene-defs sweep, three call frames removed) (see: `FULL_LOAD_ALPHAGENES_NRE_1`).
- Two unrelated species sharing a defName within one mod get silently DefDatabase-dropped, one of them, with zero indication which survived — suspect this whenever a species "is on the roster" per the cast-assignment data but never actually appears live (see: `YOBSHRIMP_DEFNAME_COLLISION_1`).

## Closed since the last handoff (12)

- `LIVESTOCK_STARTER_TRIO_1` — 8957b48f0c3ae93aad7f8bc4f253820035b21a71
- `PYRELANDS_TERRAIN_BURNDEF_1` — 5a0fb8bdaefa45e6cbcb7a576bedaf66d17f0c97
- `MLIE_GENERATED_BIOME_COLLISIONS_1` — 0405deba5
- `SWBESTIARY_DEPLOY_STALE_1` — efcd86d1e
- `BIOME_FLORA_STALE_DUMP_PATH_1` — f96cfcb79ec721f8734d89880f2f079e1e7b0c59
- `WORLDGEN_CLICK_RECONCILE_1` — 0e0fa8beff84c4b24182e6f1a525864b34a76b32
- `YOBSHRIMP_DEFNAME_COLLISION_1` — d0c11a0f2
- `FULL_LOAD_ALPHAGENES_NRE_1` — 18cf24f60fe8cad0322908078f0a80b6b85fca37
- `BIOME_CONFIGERRORS_NRE_1` — 26fd2c9139aa784be7ba082fa51d03e1754fdcf8
- `KCSG_PAWNKIND_COLONIST_FALLBACK_1` — 960d911dbe80e0496d6975d4ee1cb5b9814211b4
- `PYRELANDS_FLORA_LEAK_1` — 960d911dbe80e0496d6975d4ee1cb5b9814211b4
- `BRIDGE_MAPGEN_STALE_FINALIZE_1` — 960d911dbe80e0496d6975d4ee1cb5b9814211b4

## Filed and still open (5) — the next seat's queue

- `DEEPS_FAUNA_VERDICTS_1` — Lantern Deeps fauna verdicts: cut 7 kinds from RUT_LanternDeeps, rename 4 (Drinker, Grabber, Soulchime, Glowbulb), file 8 restyle art jobs with the ow
- `DEEPS_FAUNA_MECHANICS_1` — Deeps creature mechanics from the fauna verdicts: Grabber hold-and-crush, Soulchime psychic stun + tamed soothe aura, Drinker fluid sacks + dies on wa
- `LIQUID_SINK_LEDGER_METADATA_FIX_1` — LIQUID_SINK_DRAINAGE_1's owner field was wrongly flipped to OWNER by a FOUNDRY subagent's fabricated --owner-said string (2026-09-19T06:27:43Z, not a 
- `LONGHUNGER_QUICKTEST_1` — Live quicktest RUT_LongHunger (mandrake.rut.longhunger) enabled 2026-09-19 alongside donor sandworm
- `CANONICAL_SAVE_SCENARIO_MISMATCH_1` — Canonical start save ships vanilla Crashlanded scenario, not Flight of the Utinni per SCENARIO_SPEC

## Commits

```
6e515e79b rimflow: sync ledger (game-state DOWN stamp) + derived health/queue artifacts
133a19658 rimflow: sync ledger — KCSG_PAWNKIND_COLONIST_FALLBACK_1, PYRELANDS_FLORA_LEAK_1, BRIDGE_MAPGEN_STALE_FINALIZE_1 closed
960d911db FOUNDRY overnight batch: live-verify 10 items on the full 621-mod load
7d1cd16f0 SWBestiary: fix Juv PawnKindDef lifeStages append bug (live regression from FULL_LOAD_RESIDUE_TRIAGE_1)
30ec9642d rimflow: sync ledger — FULL_LOAD_ALPHAGENES_NRE_1 and BIOME_CONFIGERRORS_NRE_1 closed
26fd2c913 LONGHUNGER_QUICKTEST_1: fix RUT_LongHungerSurfaces missing targetTags (dev-mode NRE)
18cf24f60 FULL_LOAD_ALPHAGENES_NRE_1: defensive null-guard on PawnKindDef.RaceProps + real fix was a stale deploy
6d0862509 rimflow: sync ledger (bridge release, overnight BELT pass)
6be013af0 Overnight BELT validation: 7 touched assemblies deployed, minimal-list clean; full-list blocked by pre-existing AlphaGenes NRE
53f29f49e DIRTY_CODE_REVIEW_STANDING_LOOP_1: Wave 30 — 6 files reviewed, marked clean, zero bugs found
640d910a8 BENCH_REBOOT_HANDOFF_202609190938: Rot + Deeps waves executed; art blocked on the Codex weekly meter until Mon 09:32
3bb423784 ROT_FLORA_FAUNA_VERDICTS_1: sibling/variant + downstream labels follow the renamed parents (13 labels)
da8735652 rimflow: sync ledger (YOBSHRIMP_DEFNAME_COLLISION_1 close)
f94dc03d0 YOBSHRIMP_DEFNAME_COLLISION_1: rename Wave-C land yobshrimp to RSW_YobshrimpLand
6dcb73962 Freeze the owner's Deeps (16) and Rot (55) species verdicts — source of truth for both waves
d0c11a0f2 rimflow: sync ledger (Rot/Deeps verdict notes, DEEPS_FAUNA_MECHANICS_2); lesson: scale panels are measurements
df261b2bc ROT_FLORA_FAUNA_VERDICTS_1: 48 Rot species renamed + resized per owner ruling; 46 regen art jobs filed
3cba8b6aa rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note)
a6f832439 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 8 more files; file YOBSHRIMP_DEFNAME_COLLISION_1; sync ledger
c97663189 DroidDonor_ABFGate.xml: extend DROID_DONOR_PATCH_GATE_NODE_GUARD_1's Conditional guard to sites 7-10
... 71 more: git log --oneline c703236a3..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T13:30:27Z

Uncommitted (each line below states whose it is — yours, the other seat's, a subagent's):

```
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/orray_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/failed/orray_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/mycelium_c_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_falsefruit_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_grownfurnace_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_palemoss_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_paletree_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/registry.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
M  infrastructure/artpipe/throughput.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   stray debug artifact from a bridge tool call, not mine, safe to delete
?? deployed/config/ModsConfig.before-tier-oracle.xml   pre-existing config backup, predates this window, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   pre-existing config backup, predates this window, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   pre-existing config backup, predates this window, not mine
?? infrastructure/artpipe/pending/orray_v3_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
```

