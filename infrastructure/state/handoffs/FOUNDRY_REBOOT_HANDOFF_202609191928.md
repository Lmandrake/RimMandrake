# FOUNDRY_REBOOT_HANDOFF_202609191928 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609191332`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`FIREHAWK_FLIGHT_BEHAVIOR_1`'s `PawnRenderNodeProperties_Spastic` wing-render-tree
approach is the WRONG mechanism for flying-animal animation and the owner's own
live test confirmed it broken (no flap sideways, missing/misaligned wing north).
The real mechanism is `PawnKindDef.flyingAnimationFramePathPrefix` — a whole-body
directional flip-book (`<prefix><N>_<direction>`, N=1..frameCount x
{north,east,south}), MEASURED against Core's Chicken via `resources.assets`
extraction (UnityPy) and frame-diffed to confirm real pose change. Both
`CLAUDE.md` and `skills/generating-rimworld-sprites/SKILL.md` now carry the
correct mechanism and the warning against Spastic for this use — read those
before touching any flyer again. Separately, the owner also ruled ALL test mod
lists (including `modset_builder.py` tiers) carry all 5 expansions from now on;
that's fixed too (`1d6041fbc`), though it was not the cause of this specific
defect (Odyssey was confirmed active for the failed test).

## What the owner should see

- `VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1` (filed for BENCH) — his Impid/"fire imp"
  sighting surfaced that `PawnFlavorPhase2_Xenotype.xml` deliberately keeps 14
  non-Star-Wars vanilla xenotypes (Baseliner, Dirtmole, Genie, Highmate, Hussar,
  Impid, Neanderthal, Pigskin, Sanguophage, Starjack, VRESaurids_Saurid, Waster,
  Yttakin, guy762_debugxenotype_droid) reflavored rather than cut. He asked for a
  BENCH assessment (role coverage vs. an existing RSW_ species, removal cost) —
  not yet done.
- `DEEPS_FAUNA_MECHANICS_1`'s Grabber (RSW_BovineBeetle) — live-fire testing found
  the creature's own RaceProps (Wildness 0.05, no predator flag) make it flee from
  every combat setup tried, including a forced attack order (curJob snapped back
  to Flee every tick) and being attacked back (it fled, got caught, died before
  landing a single counter-hit). RM_CompGrappler has never been given a landed hit
  to respond to — this reads as a temperament/RaceProps mismatch with his own
  "great strength to Hold someone... slowly crush them" design intent, not a
  comp-code defect. Needs his call: make it predator/aggressive, or accept
  manhunter-only grapples.
- Flagged but not resolved: `RUT_TheForge`'s 3 heat-tolerant flora slots
  (BMT_FireLavender/Sagecrust/HeatsinkFungus, owner-ruled SIGNATURE content per
  `the_forge.json` §4, grow range 50–352°C) have no owned RUT_ port yet and block
  `biome_flora.py --write` for the whole game — CUT_FALLOUT_GENERATED_DATA_1's own
  note calls this "a design call, not a mechanical rename." Not attempted; these
  are real ruled content, not filler, so cutting them would be wrong.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `OFFBIOME_SHEET_RERENDERS_1` — 7 artpipe jobs filed (bolotaur/gualaar x3 facings, fulgurite x1) on the gemini channel after Codex quota exhausted, still pending; NEXT: once art lands in `infrastructure/artpipe/done/`, wire bolotaur+fulgurite textures into their existing mods and build the new GualaarArtOverride mod (gualaar ships as pure donor content today, no owned port).
- `GRAFFITI_VARIANT_COUNTS_1` — 8 more artpipe jobs filed (gemini channel) to close Scratches/TallyMarks/WarningGlyph to parity (3/3/4 -> 6/6/6) with Vandal; NEXT: once art lands in done/, drop the new PNGs into `RM_Graffiti_{Scratches,TallyMarks,WarningGlyph}` and deploy.
- `FIREHAWK_FLIGHT_BEHAVIOR_1` — root-caused live (see "one thing to carry forward"); NEXT: retire the BodyDef/PawnRenderTreeDef/Spastic wiring and wing-split art, author frameCount x 3 real flip-book frames per the corrected skill section, re-verify live (step ticks to actual takeoff, not a standing screenshot).
- `DEEPS_FAUNA_MECHANICS_1` — Grabber root-caused live (temperament/RaceProps mismatch, see "what the owner should see"); NEXT: get the owner's ruling on predator/aggression, then retest; Drinker/Soulchime not re-retested this pass.
- `PYRELANDS_DONOR_PORT_4` — the owed live mod-list cleanup (4 dead ArtOverride mods) is DONE; NEXT: BENCH's calls on mechanics re-attachment (flamefang/sytheclaw/barbslinger/fire wasp dropped abilities) and barbslinger/fire-wasp naming, plus a code-review pass (no file in this port is CLEAN yet).

## Traps learned

- `deploy_custom_mods.py`'s held-file reporting was blind to a file already
  deployed byte-identical BEFORE a hold was written for it — it never showed up
  in new/changed/gone so the plan read "in sync" forever with no sign it was
  held, and `--prune` couldn't catch it either (still present in `src/`). Fixed:
  `compare()`'s same-bucket is now checked like the other three (see:
  `DEPLOY_HOLD_SAME_BUCKET_BLIND_1`, commit `2dc1483a0`).
- A hostile-faction wild animal spawned via `jawa/spawn_pawn` with no Lord just
  stands idle — faction hostility alone does not give it an attack directive
  (see: `DEEPS_FAUNA_MECHANICS_1` note this wave).
- `jump_camera_to_cell` + `rootSize: 11` (closest zoom) renders forbidden-item
  icons the size of the whole screen, not the animal you meant to look at —
  back off to `rootSize` ~14-18 before screenshotting a specific pawn (filed:
  LESSONS_INBOX).
- A `.gitignore`d/stale `.git/index.lock` recurred repeatedly this session on a
  shared worktree with BENCH active concurrently — checked for a live process
  each time before removing (`ps aux | grep git`), never removed blind (see:
  `shared-worktree-remeasure-before-acting`, memory).

## Closed since the last handoff (4)

- `BIOME_FLORA_ROSTERS_DIR_POLLUTION_1` — a553ef6946bd336e641bdd5b8d6d6e8436e748bb
- `VENTFORGE_KILN_RECIPEWIRING_HELD_1` — 2dc1483a05ce19ad5e843eb11175eb95ba06f545
- `DEPLOY_HOLD_SAME_BUCKET_BLIND_1` — 2dc1483a05ce19ad5e843eb11175eb95ba06f545
- `BRIDGE_DOBILL_FORCE_TOOL_1` — 0e55faf5023cef88c2f2fac5211d6f6943656d1e

## Filed and still open (2) — the next seat's queue

- `EMBERSCYTHE_PYRELANDS_REHOME_1` — Move RUT_Emberscythe out of RotSporeKit into a Pyrelands mod — owner ruled MOVE, not cut (2026-09-19 question card)
- `VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1` — Assess the 14 non-Star-Wars xenotypes (Baseliner/Dirtmole/Genie/Highmate/Hussar/Impid/Neanderthal/Pigskin/Sanguophage/Starjack/VRESaurids_Saurid/Waste

## Commits

```
8cf24f95a rimflow: sync derived health dashboard
b5bbf7641 rimflow: sync ledger (FIREHAWK_FLIGHT_BEHAVIOR_1 -- live-fire failure root-caused)
1f33f4acc generating-rimworld-sprites: flier animation is a flip-book, not a wing layer
307b7105b CLAUDE.md: correct the flight-animation mechanism, record all-DLC test rule
1d6041fbc modset_builder.py: every tier includes all 5 expansions now
de5435a4d Any seat ends a dead queue item — owner's ruling, 2026-09-19
51e0cebc1 BENCH_REBOOT_HANDOFF_202609191902: Pyrelands donor port, flyers, and a live art-misroute sweep
ff445e0ec rimflow: sync ledger — 4 items closed, ROT_SIZE_REJUDGE_APPLY_1 filed
14c8e0d5f ROT_SIZE_REJUDGE_APPLY_1: file the owner's 11 re-judged Rot sizes as owed work
558808979 Live load 2026-09-19: Pyrelands port + flight verified in the running game
0204e4be3 rimflow: sync ledger (GRAFFITI_VARIANT_COUNTS_1 -- 8 parity jobs filed)
66a0cca4e DEPLOY_HOLD: hold the rescued mis-route renders, as FILE paths not a directory
afb08ef4f modlist: recapture FULL.LATEST at 617 (PYRELANDS_DONOR_PORT_4 cleanup)
3785aac81 Flyers fly: standing rule recorded, fire wasp and fire-hawk given real flight
c1b342131 WildAnimals_Pyrelands.xml: fix stale comment (still said "plus vanilla Boomalope")
84c7c6a90 PYRELANDS_DONOR_PORT_4: remove 4 dead ArtOverride mods (621->617 active)
f537c3462 PYRELANDS_DONOR_PORT_4: delete a false hazard claim I wrote into this item
ca636ebfd rimflow: sync ledger (BRIDGE_DOBILL_FORCE_TOOL_1 closed, DEEPS_FAUNA_MECHANICS_1 root-caused live)
0e55faf50 PYRELANDS_DONOR_PORT_4: file the item the port commits already cited
f38b50542 rimflow: sync ledger (crossref fix confirmed 185->38, game UP)
... 25 more: git log --oneline 9929af465..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-19T19:04:34Z

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
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_drinker_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_gembug_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_gembug_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_gembug_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_glowbulb_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_glowbulb_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_glowbulb_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_grabber_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_grabber_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_grabber_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_megapleura_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_megapleura_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_megapleura_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_mossbeetlelarvae_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_mossbeetlelarvae_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_mossbeetlelarvae_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_shatterjaw_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_shatterjaw_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_shatterjaw_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_soulchime_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_soulchime_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/deeps_soulchime_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
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
 D infrastructure/artpipe/pending/rot_agaricusdomecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agariluxprime_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agaripawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_agelesscap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_arbuscularmycorrhiza_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_arpeau_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_blastpodshroom_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_bleedingtooth_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_brightbell_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_bryolux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_crimsoncap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dewshrooms_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dribblingcap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_dulcisplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_euphoriccrown_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_falsefruit_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_flakespirefungus_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fruitingbodies_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_furnacecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_giantagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_glowingagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_glowstool_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_greylady_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_lilacbeacon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mortalmorelplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_nogtyl_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_nuitae_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_palemoss_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_paletree_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_pusmelon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_recurvedstropharia_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_regenerantveil_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_rustpuff_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_sagecrust_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_shinecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_skulltop_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_slimypholiota_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_swarmling_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_swarmling_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_swarmling_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_violetwimple_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wildpawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wildpawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wildpawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wildpod_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wildpod_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wildpod_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_witchesoyster_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
 D infrastructure/artpipe/pending/rot_wrinklecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_falsefruit_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_grownfurnace_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_palemoss_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_paletree_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
AD infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/registry.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
MM infrastructure/artpipe/throughput.jsonl   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   stray debug artifact from an earlier bridge tool call, not mine, safe to delete
?? deployed/config/ModsConfig.before-tier-oracle.xml   pre-existing modset_builder.py auto-backup, not mine (never ran those tiers with --apply this session)
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   pre-existing modset_builder.py auto-backup, not mine (never ran those tiers with --apply this session)
?? deployed/config/ModsConfig.before-tier-warlab.xml   pre-existing modset_builder.py auto-backup, not mine (never ran those tiers with --apply this session)
?? infrastructure/artpipe/failed/deeps_drinker_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_drinker_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_drinker_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_drinker_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_drinker_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_drinker_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_gembug_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_gembug_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_gembug_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_gembug_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_gembug_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_gembug_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_grabber_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_grabber_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_grabber_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_grabber_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_grabber_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_grabber_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_megapleura_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_megapleura_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_megapleura_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_megapleura_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_megapleura_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_megapleura_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_soulchime_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_soulchime_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_soulchime_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_soulchime_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_soulchime_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/deeps_soulchime_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_east.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_east.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_north.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_north.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_south.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_south.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_fulgurite_v2.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_fulgurite_v2.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_east.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_east.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_north.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_north.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_south.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_south.manifest.json   mine -- codex-channel attempt failed on Codex quota exhaustion (resets 2026-09-21 09:32), retried as the _v3 gemini-channel jobs above
?? infrastructure/artpipe/failed/rot_agaricusdomecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaricusdomecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agariluxprime_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agariluxprime_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaripawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaripawn_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaripawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaripawn_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaripawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agaripawn_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agelesscap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_agelesscap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_arbuscularmycorrhiza_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_arbuscularmycorrhiza_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_arpeau_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_arpeau_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_blastpodshroom_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_blastpodshroom_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_bleedingtooth_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_bleedingtooth_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_brightbell_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_brightbell_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_bryolux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_bryolux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_crimsoncap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_crimsoncap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_dewshrooms_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_dewshrooms_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_dribblingcap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_dribblingcap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_dulcisplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_dulcisplant_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_euphoriccrown_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_euphoriccrown_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_falsefruit_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_falsefruit_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_flakespirefungus_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_flakespirefungus_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fruitingbodies_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fruitingbodies_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_furnacecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_furnacecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_giantagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_giantagarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_glowingagarilux_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_glowingagarilux_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_glowstool_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_glowstool_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_greylady_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_greylady_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_lilacbeacon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_lilacbeacon_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mortalmorelplant_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mortalmorelplant_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_nogtyl_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_nogtyl_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_nuitae_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_nuitae_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_palemoss_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_palemoss_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_paletree_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_paletree_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_pusmelon_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_pusmelon_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_regenerantveil_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_regenerantveil_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_rustpuff_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_rustpuff_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_sagecrust_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_sagecrust_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_shinecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_shinecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_skulltop_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_skulltop_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_slimypholiota_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_slimypholiota_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_swarmling_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_swarmling_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_swarmling_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_swarmling_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_swarmling_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_swarmling_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_violetwimple_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_violetwimple_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpawn_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpawn_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpawn_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpawn_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpawn_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpawn_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpod_v2_east.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpod_v2_east.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpod_v2_north.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpod_v2_north.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpod_v2_south.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wildpod_v2_south.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_witchesoyster_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_witchesoyster_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wrinklecap_v2.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rot_wrinklecap_v2.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_falsefruit_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_falsefruit_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_furnacecap_plant_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_furnacecap_plant_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_gene_furnaceblood_icon_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_gene_furnaceblood_icon_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_grownfurnace_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_grownfurnace_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveingredient_agelesscap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveingredient_agelesscap_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveingredient_euphoriccrown_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveingredient_euphoriccrown_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveingredient_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveingredient_regenerantveil_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveprep_toxicinjection_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_liveprep_toxicinjection_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_livingfurnacecap_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_livingfurnacecap_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_palemoss_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_palemoss_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_paletree_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_paletree_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_regenerantveil_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_regenerantveil_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_mycoid_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_mycoid_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_nightwake_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_nightwake_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_quickflesh_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_quickflesh_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_sheenblood_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_symbiont_sheenblood_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_tea_agereversal_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_tea_agereversal_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_tea_bioregeneration_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_tea_bioregeneration_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_tea_pleasure_v1.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/failed/rut_tea_pleasure_v1.manifest.json   artpipe daemon queue/output, not mine (pre-existing daemon churn pattern)
?? infrastructure/artpipe/pending/graffiti_scratches_p1.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_scratches_p2.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_scratches_p3.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_tally_p1.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_tally_p2.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_tally_p3.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_warn_p1.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/graffiti_warn_p2.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   mine -- filed this session, still pending the daemon (Codex quota was exhausted, retried on gemini channel)
?? infrastructure/state/.rimflow_conc_97j8px_9/   rimflow concurrency scratch dir, not mine
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing since 2026-09-11, not mine
```

