# FOUNDRY_REBOOT_HANDOFF_202609250325 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609242045`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Multiple fresh subagents this window independently and falsely claimed "this WSL machine cannot compile
C# .csproj files, Windows-native dotnet only" and shipped C# build-unverified — checked every single time,
every claim was wrong. `/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build 'D:\Luke\dev\Rimworld\src\...\Foo.csproj'
-c Release` (Windows-style path, run from a WSL bash shell) builds clean with zero extra setup. This is now
the single most common false claim this project's subagents produce — brief any C#-touching subagent with
this explicitly rather than letting it "try, fail to find a toolchain, and give up." Filed to memory
(`rimworld-csharp-toolchain`), not yet to `LESSONS_INBOX.md` — do that on wake.

## What the owner should see

- Five naming cards await his word (working names he can keep or replace): `POISONFOREST_SHIPPING_NAMES_1`,
  `SCARLANDS_SHIPPING_NAMES_1`, `PROPANELAKES_SHIPPING_NAMES_1`, `MIASMA_SHIPPING_NAMES_1`,
  `CRACKEDLANDS_SHIPPING_NAMES_1` — all from `COMMISSION_LEDGER_CLEANUP_1` waves, none blocking anything.
- `PYRELANDS_BURROWER_GRAZER_1` needs a ruling: is a dedicated burrower-grazer wanted distinct from the
  already-imported `Orray` (a burrow-on-fire hybrid predator already wired at 0.25 commonality), or does
  Orray already cover that roster slot?
- `FLORA_LEGIBILITY_BAR_1`'s grading sheet (`Transient/flora_legibility_sheet_2026-09-17/sheet.html`, 127
  flora + 5 vanilla probes) is built, current, and ready for his grading pass whenever he's free — nothing
  else in that item can proceed until he grades it.
- Three question-card rulings he gave earlier this window are already acted on and recorded on their items:
  beast renames took BOTH defName and label (`NONCANON_BEAST_RENAME_1`, closed); the Graffiti punk register
  blends NYC wildstyle + UK stencil + his own typed addition "mystic traditions in the abstract"
  (`GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`); Shokkweave's invented balance numbers ship as first-pass, tune later
  (`SHOKKWEAVE_SOLE_SOURCE_1`). Nothing further needed from him on these three.
- Four items flagged earlier this session as too big for a quick card still need a real sitting whenever he
  has time: `DONOR_DEFS_PORT_TO_OURS_1` (76-donor porting order), `TECHPRINT_FACTION_GATING_1` (faction-tech
  alignment mapping), `FASCINATING_WORLD_JUNK_1` Phase 3 (the item's own text says roster-carding needs him,
  not an agent), `CANON_CREATURE_REGEN_1` (a second ungraded fidelity sheet, `Transient/canon_regen_wave3_2026-09-23/sheet.html`).

## What is half-done, and where it stops

- `BACTA_REVIVAL_MECHANIC_1` — 5/5 files deployed and offline-verified this window; full live-proof checklist (corpse-freshness window, real tank job, missing-parts/brain preserved, post-revival healing, both settings toggles) is entirely unrun — the item's own brief explicitly forbids closing without it; NEXT: game up + bridge, run the live-proof checklist in the item's own `## acceptance criteria`, then close.
- `BACTA_SIDE_ITEMS_1` — DLL deployed this window, 10/10 files in sync, offline-clean; NEXT: game up + bridge, run the droid-healing/patch-spray-consumption/settings-render quicktest in the item's own `## verify`, then close.
- `COMMISSION_LEDGER_CLEANUP_1` — 10 waves landed this window, ~36 of 85 slugs resolved (arid_shrubland, poison_forest, the_forge, the_scarlands, the_propane_lakes, the_miasma, the_blue_desert, fall_line, the_scald, the_cracked_lands all closed out); NEXT: `rimflow show COMMISSION_LEDGER_CLEANUP_1`, pick an unclaimed sheet group from the remaining ~49 slugs/15 groups (`dune_sea+deep_desert`, `nightside_ice`, `terminator_sea+the_grey_deep`, `terminator_sea+the_twilight_deep`, `the_contagion`, `the_greentide`, `the_rot`, `the_slime`, `wasteland`), check-before-build per the item's own now-well-established discipline.
- `FEVER_WOOD_MECHANICS_1` — F1-F7 build passes all landed this window plus a fresh ground-refusal terrain mechanic; wild bore-cave occupant roster (a content decision, deliberately not invented solo) and all live/bridge verification remain untouched; NEXT: read the item's F-labeled history for what's left, or take the bridge and live-verify what's built.
- `FIREHAWK_FLIGHT_BEHAVIOR_1` — flip-book art (already-rendered, previously unused) installed and wired this window, grounded sprite confirmed live; no actual mid-air takeoff frame was observed in ~35 min of stepped ticks (trigger chance is only 15%, so this is inconclusive, not negative); NEXT: game up + bridge, a longer/more patient observation window, or judge the structural proof sufficient and close.
- `FISH_BESTIARY_BUILD_1` — this window corrected a stale blocker reference (`QUICKTEST_RIVER_WATER_MISSING_1` actually closed 2026-09-24) and ran a clean `--live` validate pass across all 84 fish-related files; NEXT: game up + bridge, live fishing pass on Weeping Stones and Greentide, confirm a documented Greentide creature-instead-of-item bug is gone, then close.
- `FLORA_LEGIBILITY_BAR_1` — this window found the grading sheet already existed, re-confirmed it's still current (no new flora art landed since), and fixed a missing `reviewStatus` stamp; steps 2-4 (fit a flora model, canvas law, processing) are gated entirely on the owner's actual grading; NEXT: owner grades the sheet, then build from his grades.
- `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` — engine, all 27 meme glyphs, the Artistic-6 skill gate, and the crown-stencil hostility gate all shipped and build-verified this window (a false "can't compile" claim was checked and disproven); 49 art jobs queued across two waves; NEXT: once the artpipe daemon finishes rendering, review on a contact sheet and wire in; the item's own RUT seam-test stub is also still unbuilt.
- `LIQUID_BOTTLE_LOOP_1` — the one DLL that was OS-lock-blocked for multiple prior sessions finally deployed this window during a game-down window, all 66 files confirmed in sync, 75/75 selftests; NEXT: game up + bridge, live quicktest of the tank loop (pour a filled container in, drain an empty one out, watch the inspect string move), then close.
- `STOCKED_POOL_BUILD_1` — bestiary + mood economy + cuisine (wave 1) and the pen-zone/PoolStock bookkeeping + STOCK/FEED jobs (waves 2-3) all shipped this window; feature stays OFF by default since the loop isn't playable end-to-end yet; NEXT: build HARVEST/CULL/RECAPTURE jobs, the vhorrin emergence trigger, and the vizhik escape event before flipping the setting on.
- `SUMP_GASLIGHT_1` — its OS-lock-blocked DLL also deployed this window; offline pieces 1-4 re-validated clean; NEXT: game up + bridge for the remaining live checks (glow-grid repaint on radius change, flame craftability/quality-scaling, the two research-gate unlocks, gas spawning on scrub completion).

## Traps learned

- WSL genuinely CAN compile this repo's C# (`/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build <Windows-path>.csproj`) — four separate subagents this window falsely claimed otherwise and shipped unverified; always brief this explicitly (see: memory `rimworld-csharp-toolchain`, not yet in `LESSONS_INBOX.md`).
- A `MayRequire="<packageId>"` on a `Class=`/xpath reference with that packageId missing from the SAME mod's own `About.xml` `loadAfter` silently discards the whole def if that assembly is ever inactive — hit 3 times this window, once at 89-file scale across all of UtinniPatches, all fixed (see: `DIRTY_CODE_REVIEW_STANDING_LOOP_1` waves 79-81).
- `linkedBodyPartsGroup`/`linkedBodyPartsGroups` naming a `BodyPartDef` instead of a real `BodyPartGroupDef` is a guaranteed load-time crash and is easy to author by mistake on new creature content (see: `DIRTY_CODE_REVIEW_STANDING_LOOP_1` wave 85).
- A new player-facing `Designator` class needs explicit registration (a `DesignationCategoryDef.specialDesignatorClasses` patch) — an unregistered one compiles and loads clean but is silently invisible in the Architect menu forever, orphaning the whole feature (see: `DIRTY_CODE_REVIEW_STANDING_LOOP_1` wave 75, `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`).
- A "pre-existing/unrelated" selftest-failure claim from a subagent is not proof — `selftest_deployed_biome_refs.py`'s `RSW_VentStalker` dangling reference was waved off as noise by two separate agents; it was a real deploy gap (the def existed in-repo but was never pushed to the live Mods folder), fixed by one `deploy_custom_mods.py --apply` call (see: `7d8cb25f3`).
- `validate_patch.py`'s `check_value_shape()` compared at the wrong xpath tree level for `PatchOperationInsert` (correct for Add, wrong for Insert, whose xpath targets a sibling not the field) — would have false-flagged the first real Insert patch anyone authored as a dict-keyed collision; fixed (see: `4afec3797`).
- `StatModifier` has no `factor`/`offset` XML field, only `value` — the verbose `<li><stat>X</stat><factor>Y</factor></li>` shape silently registers the outer `<li>` tag itself as a bogus StatDef cross-reference, so the real value is never applied; use the shorthand `<StatDefName>value</StatDefName>` form (see: `9c035dc7c`, `RUT_Tarred_Hediffs.xml`).

## Closed since the last handoff (8)

- `WATER_TRUCE_RETRIBUTION_1` — 7a61fc356
- `OASIS_MAKER_BUILD_1` — bb984a61b
- `NONCANON_BEAST_RENAME_1` — f7cf979ab
- `WEEPINGSTONES_RM_MOD_BUILD_1` — 55d52a2fe
- `TWILEK_TROPE_GENES_MOVE_1` — b479016a8
- `SYSTECH_ELECTRIC_BOLT_1` — 8da782aee
- `EXTREME_DESERT_SIGNATURE_FLORA_1` — 93a29cd74
- `LIQUID_REGISTRY_CORE_1` — 4d3ed7fc3

## Filed and still open (13) — the next seat's queue

- `FORCE_DISTURBANCE_REFLAVOR_1` — Reflavor vanilla psychic assault/drone storm events as disturbances in the Force at the RimStarWars tier
- `VANILLA_BEAST_EXCISION_1` — No vanilla beasts in the Utinni scenario: cut every vanilla/DLC animal at the scenario layer, biome by biome as each biome's own cast is ready — never
- `THEY_MOD_REPLICATION_1` — Replicate They! (Giant Ants) in our own tier and retire the dependency — 1 race/2 kinds/hidden raid faction/carapace stuff+wall trivial XML, one small
- `POISONFOREST_SHIPPING_NAMES_1` — Owner card: poison_forest working names (vent stalker, dark crust)
- `SCARLANDS_SHIPPING_NAMES_1` — Owner naming: Scarlands mortuary crawler (COMMISSION_LEDGER_CLEANUP_1)
- `PROPANE_LAKE_PIPE_MECHANICS_1` — Propane lake pipe network mechanics: gas vent, saturation tracker, pipe rupture, V-wake pump agitation
- `PROPANELAKES_SHIPPING_NAMES_1` — Owner card: propane lakes working names (Burner Ascendant, V-Wake)
- `MIASMA_KARRATHIL_POLLINATION_GATE_1` — Gate the mangals' flowering reproduction on karrathil presence, once the plant-reproduction engine question is answered
- `MIASMA_SHIPPING_NAMES_1` — Owner card: the_miasma working names (karrobel, karrathil, stranded deformation)
- `PYRELANDS_BURROWER_GRAZER_1` — Author a dedicated burrower-grazer creature for the Pyrelands' 'three families' fire-web (owner-ruled, all-ruled §4) -- new C# burrow-on-fire behavior
- `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1` — Feral-race crash-survivor pawnkind + permanent mental-scar hediff + capture-to-slave wiring
- `CRACKEDLANDS_SHIPPING_NAMES_1` — Owner card: name the Cracked Lands' two new commission species
- `CRACKED_LANDS_SEALED_WAKE_MECHANISM_1` — Sealed sleeper: water-trigger wake comp + gather-crack-wax-after-wake job

## Commits

```
248390e93 Ledger sync: COMMISSION_LEDGER_CLEANUP_1 wave 10 note + queue re-render
b431cb4a3 COMMISSION_LEDGER_CLEANUP_1 wave 10: the_cracked_lands, 4 commissions
9cb8cc265 Rot sitting ruled: migration ratified, names applied, 18 art jobs
fb6e71959 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 88 note + queue re-render
9e6a3ae3f DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 88: mark 10 UtinniPatches/StarWarsRaces files CLEAN
af13f4632 Ledger sync: COMMISSION_LEDGER_CLEANUP_1 wave 9 note + queue re-render
9c035dc7c DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 88: fix broken StatModifier XML in RUT_Tarred_Hediffs.xml
4b94a2da6 COMMISSION_LEDGER_CLEANUP_1 wave 9: the_scald welcome-blanket flora + fall_line feral-survivor re-file
9f30170a2 Slime seed pass ruled in: 3-5 pre-slimified visitors at map gen
fa63801ef Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 87 note + queue re-render
e6ef78f49 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 87: mark 10 DesertPort/StructureInjectionsSW/StarWarsRaces files CLEAN
2096b7306 Biome build sweep: all 20 items now FOUNDRY-claimable
32a8f920c Ledger sync: GREENTIDE_MECHANICS_2 M3 Roil-spawn wave note + queue re-render
1d50f06c9 GREENTIDE_MECHANICS_2: M3's Roil-condition steam devil spawn route
26b17b0d6 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 86 note + queue re-render
16003687a DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 86: mark 12 ResearchRetag/RustCathedralHum/ShokkweaveEconomy/UtinniPatches files CLEAN
33550ddc7 Ledger sync: COMMISSION_LEDGER_CLEANUP_1 wave 8 (the_blue_desert/the_webwork/the_pyrelands) + PYRELANDS_BURROWER_GRAZER_1 filing + queue re-render
5bf731e03 FeverWood cast art: 53 jobs filed (16 fauna x3 + 5 flora)
55dae716a Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 85 note + queue re-render
d70591c5a LESSONS_INBOX: \b rename sweeps miss RM_ defName forms
... 156 more: git log --oneline 0c1db0075..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-25T01:33:23Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   ambient, DIRTY_CODE_REVIEW_STANDING_LOOP_1's health-rebuild side effect (queue_lint prune/list trigger), not this window's direct edit
 M Transient/codebase_health.json   ambient, DIRTY_CODE_REVIEW_STANDING_LOOP_1's health-rebuild side effect, not this window's direct edit
 M Transient/codebase_health_artifact.html   ambient, DIRTY_CODE_REVIEW_STANDING_LOOP_1's health-rebuild side effect, not this window's direct edit
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralgrazer_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_feralnerf_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_grank_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_grank_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_grank_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_horax_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_horax_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_horax_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_porg_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_porg_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_porg_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_strill_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_strill_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_strill_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_cundral_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
 M infrastructure/artpipe/registry.jsonl   ambient, artpipe daemon (background, continuous) -- not a seat's write
 M infrastructure/artpipe/throughput.jsonl   ambient, artpipe daemon (background, continuous) -- not a seat's write
 M infrastructure/dashboards/hub/data/health.json   ambient, health-rebuild side effect, not this window's direct edit
 M infrastructure/state/codebase_health_last.json   ambient, health-rebuild side effect, not this window's direct edit
 M src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll   FOUNDRY this window -- LIQUID_BOTTLE_LOOP_1 deploy-window rebuild, b4a1f8f14
 M src/RimUtinni/LanternDeeps/Assemblies/RimMandrake.Utinni.LanternDeeps.dll   FOUNDRY this window -- DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 72 SeedPart fix rebuild, cf0f72239
 M src/RimUtinni/UtinniPatches/Assemblies/RimMandrake.Utinni.UtinniPatches.dll   FOUNDRY this window -- COMMISSION_LEDGER_CLEANUP_1 waves rebuilding UtinniPatches repeatedly (most recently RSW_VentStalker deploy, 7d8cb25f3)
?? deployed/config/ModsConfig.before-tier-firehawk.xml   FOUNDRY this window -- FIREHAWK_FLIGHT_BEHAVIOR_1 live-verify agent's modlist_swap backup
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   FOUNDRY this window -- WEEPINGSTONES_RM_MOD_BUILD_1 live-verify agent's modlist_swap backup
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_brekkugar_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_brekkugar_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_brekkugar_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_dhukk_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_dhukk_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_dhukk_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_ghorrumak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_ghorrumak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_ghorrumak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_gruzz_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_gruzz_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_gruzz_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_hulggarok_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_hulggarok_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_hulggarok_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_kessik_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_kessik_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_kessik_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_shekkur_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_shekkur_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_shekkur_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_thrizzik_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_thrizzik_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_thrizzik_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_ulkhorr_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_ulkhorr_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_ulkhorr_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_vrakk_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_vrakk_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_vrakk_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_zekkra_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_zekkra_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_zekkra_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_zhurrakor_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_zhurrakor_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/crags_zhurrakor_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_bezzul_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_bezzul_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_bezzul_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_hennul_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_hennul_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_hennul_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_oomb_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_oomb_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_oomb_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_thummorak_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_thummorak_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_thummorak_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_vohhm_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_vohhm_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_vohhm_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_wuppik_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_wuppik_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_wuppik_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_wuum_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_wuum_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_wuum_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_yollum_east.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_yollum_north.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/artpipe/pending/slime_yollum_south.json   ambient, artpipe daemon (background, continuous) -- draining an ongoing desertportb/rm_*/bluedesert/contagion/crags/nightside/slime batch, not this window's
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing (2026-09-11), not this window
?? infrastructure/state/ledger/events/OWNER.jsonl   not mine to touch -- another seat's ledger shard
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing, not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing (before this window started), not this window
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing, not this window
```

