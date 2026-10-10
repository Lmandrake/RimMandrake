# BENCH_REBOOT_HANDOFF_202610100044 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610091300`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner wants every sheet instruction carried out AND independently audited before it is called done. Today the doers twice claimed complete and an independent auditor found 15, then 3, real FAILs (`Transient/cauldron_independent_audit_2026-10-09.md`). Run `art.py enact`, fix its TODO/CONFLICT residue, then send a FRESH agent to verify each row against primary evidence (sha on disk at the loaded texPath, parsed XML, job prompts, ModsConfig parsed) — that loop is the definition of finished.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **66-decision picture sheet** is open at `http://localhost:38017/?t=TCigyHWCjqNfYfSFQaT1Mw` (`D:\Luke\dev\RimMandrake\Transient\sheet_conflicts_review_2026-10-09.html`); he had made 6 of 66 picks at wrap (snapshot 90970e704). Each pick maps back via `Transient/sheet_conflicts_review_2026-10-09.map.json`.
- **Silooth**: no render passes canon after 4 tries. v3 (legs right) vs v4 (shell right) side by side at `D:\Luke\dev\_rmscratch\silooth_v3_v4.png`, sent to his phone; he has not picked.
- **Restart owed**: Cauldron/Contagion renames (ossrith, rhossak, galled rhossak, sarrowan, Garsulix), Silooth 8-wide + AI acid spit, and 8 new override mods (ModsConfig 614→622, backup `ModsConfig.xml.bak_cauldron_overrides_20261009_085401`) deployed after the 09:01 launch, so only the next launch shows them.
- **Calls made without him**: Sketto S/N floor set to 0.25, not his ~0.28 (back view measures 0.260); beskar smelt ratio (1/3 steel + slag) and prison-quest timing (day 30, every 60 days) are agent defaults in `beskar_armorer_quest_design_2026-10-09.md`; natural glasses stay separate from transparisteel (he confirmed by card).
- **Yob shrimp / pale yob shrimp** remain provisional: the Bestiary's text is not online anywhere; needs the physical book.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `FLYER_STABLE_BODY_GATE_1` — Sketto floor 0.25 shipped (94ef810d6), Sketto east still a failed set; Hawkbat south/north masters queued; NEXT: put the Hawkbat S/N masters in front of the owner when they render and ask whether the plate approach suits a torso-covering membrane.
- `BESKAR_ARMORER_QUEST_1` — design final (ea47cce63), filed for FOUNDRY; NEXT: confirm in engine whether a gravship can land on a custom orbital world object before building.
- `SHIP_ALLOY_FORGE_1` — zersium is a rare local ore in ONE home biome (card); NEXT: propose the home biome to the owner as a one-line card.
- `CANON_MATERIALS_BUILD_1` — hard rules ruled (plasteel: droid shells + prosthetics; duranium: large frames; doonium: cores; durasteel none); NEXT: confirm the design doc §4 table reflects the 15:01 card note, then leave to FOUNDRY.
- `SCALD_UNDERWATER_FLORA_1` — built, may now be deployed (game relaunched 09:01); NEXT: open a Scald map and confirm the 7 flora and the wreck thurlsponge spawn.
- `TWILIGHTSEA_FLORA_PASS_1` — built; NEXT: on a Twilight map, check floor flora, well placement and both comps live.
- `UNSUBSTANTIATED_SPECIES_ABILITIES_1` — 31 genes removed (87888849a); NEXT: spawn one Anzati and one Cerean and confirm the genes are gone.
- `ART_SHEET_DONOR_JOIN_GAPS_1` — all 27 biome sheets rebuilt today (01b5cdb29); NEXT: confirm RSW_Plant_Nysyllin_Wild joins its renders on the rebuilt sheet, then close.
- `SHEET_DONOR_COLUMN_FALSE_PASS_1` — fixed at 98b0bac5f, sheets rebuilt; NEXT: close it with sha 98b0bac5f.
- `WEATHER_STONES_OWN_ART_1` — renders done (wsart_RM_*); NEXT: put the 3 renders to the owner for a pick, then `art install` them.
- `LEANINGSCRUB_VENOMVINE_SITTING_1` — run-sheet ready (620b54f6f); NEXT: stage the sitting per `Transient/venomvine_sitting_runsheet_2026-10-09.md` when the owner is present with the bridge.
- `SELFTEST_DRIFT_CLEANUP_1` — 2 selftests red (RUT_DeadCreep/DyingCreep missing from the def dump; Greentide MOD_OPTIONS_RETROFIT_1 A3 has no criterion); NEXT: refresh the def dump and give A3 a criterion.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- enact dry run vs apply disagreed (ingest marked ✕'d pictures kept before purge); fixed 7c623ab47 (filed: lessons)
- A subagent's "Deployed, VERIFIED" was overwritten by another clone's older deploy within minutes (filed: lessons)
- Legacy pre-10-04 sheet replace rulings never became redraws — 229 rows (filed: lessons)
- Shared-clone sync: path-scoped stash + rebase + pop, push in a separate call (filed: lessons)
- Owner-quote guard rejects a typed question and joined quotes as authorization (filed: lessons)

## Closed since the last handoff (2)

- `CANON_ENTRY_BRIEFS_OWED_1` — af124406f
- `CANON_MATERIALS_DESIGN_1` — 71c9b7fd6

## Filed and still open (8) — the next seat's queue

- `MAP_LANDFORM_MUTATORS_DESIGN_1` — MAP_LANDFORM_MUTATORS_DESIGN_1
- `BIOME_MAP_GENERATORS_DESIGN_1` — BIOME_MAP_GENERATORS_DESIGN_1
- `CANON_MATERIALS_BUILD_1` — Build the decided canon materials design: RSW_Durasteel with donor conversion, plasteel salvage/trade only, trade-only RSW_Phrik/Transparisteel/Stygiu
- `MATERIAL_MERGES_CLEANUP_1` — Material merges and bronzium removal: one chitin ladder, drop 7 RUT_ duplicates, one common salt (+4 Grey Sea premium), merge plasteel slags and tiban
- `GLASS_TO_TRANSPARISTEEL_1` — Transparisteel replaces glass: sifted Stillsand fine sand -> RSW_Transparisteel; sun/lens glass fold in; bottles and lenses made of it
- `SHIP_ALLOY_FORGE_1` — Alloy forge aboard with progressive unlocks: durasteel early (steel + zersium, route TO CONFIRM), plasteel late
- `ASTEROID_DESERT_ORES_1` — Doonium asteroid ore smelted aboard with glower crust; rare desert phrikite smelted aboard into phrik
- `BESKAR_ARMORER_QUEST_1` — Blackstar quest to a rare Mandalorian armorer, the only way to reforge beskar (quest design needs the owner)

## Commits

```
90970e704 Snapshot: owner's first 6 picks on the 66-conflict sheet; owner ledger events; sheet state
ea47cce63 Beskar armorer quest: decided design (orbital covert, two routes), L1..L10
e2622ff17 FOUNDRY handoff 202610100040
739d078b5 Belt fix log e (seabed gate)
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
... 153 more: git log --oneline 0e2ecffbe..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-09T23:07:23Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/modcheck/fixtures.json   FOUNDRY modcheck run output (not this window)
 M Transient/sheet_conflicts_review_2026-10-09.decisions.json   owner's live clicks on the 66-conflict sheet, written by its server (snapshot committed 90970e704)
?? conversations/   earlier BENCH windows' conversation exports (not this window)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   earlier BENCH windows (attributed in the 10-08 morning handoff)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   earlier BENCH windows (attributed in the 10-08 morning handoff)
```

