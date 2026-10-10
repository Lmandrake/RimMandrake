# FOUNDRY_HANDOFF_202610100040 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610091641`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

Helpers' landings (`land.sh`) publish from elsewhere, so this clone's HEAD lags origin and its tracked tree shows hundreds of phantom 'modified' lines that are already on origin. Before trusting `git status` here, `git fetch` and diff the dirty paths against `origin/main`; I synced with `git reset origin/main` plus `git checkout --` of the 15 stale paths (nothing unpushed was lost).

## What the owner should see

- **Ruled in chat:** Scald gallery reward = the long-reach circulation pump; he wants the hose settings thought through, 'likely two pumps with two mod settings' (note on `SCALD_GALLERY_SCHEMATIC_UNLOCK_1`). Three questions to put to him: pump with hoses off, the 1500-cell hose cap, inert keepsake if the pump setting is off.
- **He decides tonight:** venomvine / Cistrel / Nubrith own renders replacing his kept pictures.
- **9 big-question card drafts:** `D:\Luke\dev\RimMandrake\Transient\backlog_big_questions_20261009.md`; plus morning card sets 2-9 in `Transient\morning_cards_20261009.md`.
- **Auto-decided and built PROVISIONAL (62 items, toggle default on):** log `Transient\belt_autodecide_log_20261009g.md`; only offline selftests ran.
- **Art picks waiting on him:** Halquin/Maulith (B vs kept A); Weeping Stones 20 rows have renders but no review sheet; Webwork TookeTrap redo and Chellow v2 north failed validation.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `SCALD_GALLERY_SCHEMATIC_UNLOCK_1` — circulation pump chosen, nothing built; NEXT: put the three hose/setting questions on a card, then build the pump with its own setting, marked PROVISIONAL.
- `HAZARD_CLOCK_INSPECT_LINES_1` A2 and `GREY_TWILIGHT_SEABED_BIOME_GATE_1` A2 — partial; NEXT: load a Twilight sea-floor map and read the twilight-well line.
- `CHILL_SUIT_SHELTER_RULE_1` — warm-room arm passes, charger arms unproven (suit never depleted); NEXT: force a depleted suit, then test same-room and behind-wall chargers.
- `SURFACE_HOME_MAP_HELPER_1` — weak L1 evidence; NEXT: exercise the five return call sites with a sea-floor home map open.
- `LONGSHADE_STAMPEDE_LIVECHECK_1` — canFireNow false in every arm; NEXT: fire the incident against the right map (`fire_incident` takes no map).
- `LONGSHADE_JAWATOW_LIVECHECK_1` — dropped for its RECHECK item; NEXT: deploy LongShade and run that recheck with `S.run(5)` before each dry run.
- `FLOODEDCANYON flood caller` — new outcome method exists, caller not switched; NEXT: switch it and run the HazardMultiplier selftests.
- `CORPSE_SITE_SAFETY`, `FLOW_ORDER_EXTERNAL_INPUT`, `ANT_HIVE_REAL_GEOMETRY`, `WARSCAR_VALIDATION_FIDELITY` — partly built; NEXT: finish each after his answers to the big-question cards.
- Game: UP on the 15-mod `acc_biomes` list; NEXT: `modset_builder.py --restore` after killing the game by PID when he wants his full list back.
- Remaining acceptance criteria and ~105 never-candidate backlog items (45 need the bridge); NEXT: `rimflow next --acceptance --seat FOUNDRY`.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `static_call` rejects `args=""`; omit it or pass a dummy (see: Transient/belt_bridge_log_20261009c.md)
- `room_heat` pins don't hold on sea-floor maps and worn apparel can't be read by `comp_read`; read charge via `ComfyTemperatureMin` on `pawn_stats` (see: Transient/belt_bridge_log_20261009e.md)
- Grey/Twilight sea features gated on `RM_GreySea` never ran on the real `RM_SeabedFloor_*` biome (see: GREY_TWILIGHT_SEABED_BIOME_GATE_1)
- TerminalBiomes is folded into the composed biomes mod; deploy with `deploy_custom_mods.py --compose biomes --apply`, which also pushes other pending DLLs (see: Transient/belt_bridge_log_20261009e.md)
- Closed-item art on `_artpipe\done` can be an owed install, not missing art (see: Transient/belt_art_log_20261009f.md)

## Commits

```
b9a9b0652 FOUNDRY ledger: owner picks circulation pump for Scald gallery
6e64c63f9 Belt bridge 20261009e: seabed gate deployed; CRUST A2 pass, hazard inspect engine+lamp lines, chill suit warm arm
b8ae46ee2 belt autodecide: ledger sync, big-question cards, log; HUGETHINGS_TEST_HONESTY_1 prose to closed/
bf265debf HugeThings: titans never route under thick roof (B3.5 D3.1 D1.4 route exclusion via providerCost; B2.6 comment; labels and walk corrected)
57262ad08 FeverWood: ant hive rooms keep real water clearance, never overlap, and are dug out of rock (open-ground walls left as a design call)
6b9e51e16 FeverWood: a lost kurreth raid-back finalizes every unrecovered animal; recovered means unbound, on a map and out of the kidnap tracker (PROVISIONAL)
ca6ddbf3e HugeThings validation: register largePawnsClearingOff, follow ForwardToPlant's area flag (static_checks were red after 0758922a0/cfbaa88e0)
4dd520149 FeverWood: thefts finalize per kurreth column; lure waves run at the bait from true opposite fronts; pools are connected clusters and escaped young skip enclosed water (PROVISIONAL)
effdbd926 HugeThings: plant footprint hardening (A2.3 A3.3 A3.8 A3.11 A3.12 C3.2 A2.6/C2.8/D2.5 C4.9/D2.1)
c37f05633 FlowWorks: pump/drill-fed cells seed the flow order so a sourceless flat channel spreads; kernel fixture (FLOW_ORDER_EXTERNAL_INPUT_1, part 1)
74a910b99 LuminousPigment: mat sighting needs colonist LOS or fresh mat in hand; Buildable lifts the press prerequisite instead of finishing research; deepfire jobs reserve by count and pay only when carried covers cost; settings apply refreshes every light (PROVISIONAL)
73bb522ef HugeThings: test apparatus honesty (C3.7 C3.8 C3.9 C2.5a C2.5c C2.5d C2.6)
047977287 TerminalBiomes: vaulisk springs on touch or harvest order; cage keeps its real crops through minify and rotation; settings wired or relabelled honestly; settings save+load round-trip proof
8c59a2cac GimmeSomeSlack: section signature carries strand sway/ripple eligibility, sway-pref transitions reprint (CORD_STATIC_DYNAMIC_HANDOFF_1); one visible-first spark set shared by glow/sparks/downed wires, intensity scales downed sparks (SPARK_EFFECT_BUDGET_REWORK_1)
574391621 Warscar: ordnance set off by a real shot; chotrix drops prey that gains company; panel chance relabelled; validation derives settings from C# and restores pre-test values (PROVISIONAL)
2c729bace belt art log 20261009h: fish already enacted, flat flora/Weeping Stones already rendered, nothing to queue
cfbaa88e0 HugeThings: plant interaction guards (A3.4 A3.6 A3.7 C3.3 C3.10)
21600855c GimmeSomeSlack: cut halves lay toward the exact cut point (AERIAL_CUT_POINT_PRECISION_1); power tap picks its own-faction transmitter, guard stops futile re-queues (POWER_TAP_MIXED_NET_CONNECT_1)
d78622086 DivingInteraction: re-assert seabed floor densities in-generation after Map Designer's reset (Grey floor grew 0 plants)
2bad6c96a EnvironmentalHazards: venom non-lethal clamp inside TakeDamage; alias chains/conflicts/fromHash; warden walks back to water; tar beast one limit + live pace + hunt retry; weather gate covers whole condition; thornbug fear local-only (PROVISIONAL)
... 46 more: git log --oneline 219ab6ec1..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/acc_d_checks.py   helpers' scratch from tonight's belt; Transient shelf life ~14 days
?? Transient/acc_d_checks2.py   helpers' scratch from tonight's belt; Transient shelf life ~14 days
?? Transient/acc_d_gloom.py   helpers' scratch from tonight's belt; Transient shelf life ~14 days
?? Transient/belt_acc3_q_20261009.py   helpers' scratch from tonight's belt; Transient shelf life ~14 days
?? Transient/belt_acc4_diff_out.txt   helpers' scratch from tonight's belt; Transient shelf life ~14 days
?? Transient/belt_fix_log_20261009e.md   helpers' scratch from tonight's belt; Transient shelf life ~14 days
?? conversations/   generated: Lodestar conversation records
?? deployed/config/ModsConfig.before-tier-acc_20261009.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_20261009b.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_20261009d.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-ishko.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-live_20261008.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-live_20261008b.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.before-tier-watchers_live.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ns_flowworks_backup.20261002T070221.json   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ns_flowworks_backup.20261005T142015.json   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? deployed/config/ns_flowworks_backup.20261005T161529.json   generated: tier-swap ModsConfig/northstar backups from prior sessions
?? infrastructure/state/items/PLASTEEL_DURASTEEL_MERGE_1.md   another window's item file, untouched here
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json   generated: tier-swap ModsConfig/northstar backups from prior sessions
```

