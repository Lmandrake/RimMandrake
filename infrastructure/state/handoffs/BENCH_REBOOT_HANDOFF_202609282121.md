# BENCH_REBOOT_HANDOFF_202609282121 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609270451`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The bedazzle ritual now runs two biomes to full ticket-out in one session, and the
proven shape is reusable verbatim:** backgrounded Fable review agent (movement 1–2,
brief template in this session's transcript / the Blue Desert brief), in-window
volley with the owner, **ledger-note every ruling the moment it lands** (the one
fragility), Fable commission agent for movement 4, then the in-window sheet
amendment + the two-item ticket pattern (`<BIOME>_RULED_CONTENT_1` +
`<BIOME>_MECHANICS_BUILD_1`). Blue Desert and the Cracked Lands both closed their
volleys this way today. The one near-miss: a biome can live under TWO names
(program table vs campaign label) and a single-name search reports its design
record missing (filed: LESSONS_INBOX).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **The Contagion art review sheet awaits his eye**:
   `D:\Luke\dev\Rimworld\Transient\contagion_cast_art_review\sheet.html` — 47
   subjects (all 38 Contagion rows validated-pass, plus the 9-subject desert redo
   wave annotated with his original improve/regen flags).
2. **Cracked Lands batch-4h renames ship as DRAFT-unapplied** (qattora / qetta /
   saqqat / luttaq / uttaqar-as-label) — he passed on the question twice, so
   current names ship; a future card if he wants them applied.
3. **33 new art jobs queued this session** (11 Blue Desert, 19 Cracked Lands, 3
   Grimewing) — the artpipe daemon runs on the Desktop only; nothing generates
   until it picks them up.
4. Wax tank dropped on a MEASURED basis (FlowWorks has no water-loss model), his
   ruling; the wax went to sealed underwater suits, terrain survival only.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `CONTAGION_BEDAZZLE_SITTING_1` — ticketed out; review sheet BUILT and pushed
  (`Transient/contagion_cast_art_review/`); NEXT: put the sheet in front of the
  owner, then harvest its decisions.json and file the keep/replace outcomes.
- `WASTELAND_BEDAZZLE_SITTING_1` — close-out DONE this session (sheet amendment,
  two FOUNDRY builds, storm card closed, Grimewing ruled in + 3 jobs queued);
  open for art only; NEXT: when the 24 Wasteland renders pass (4/22 at last
  read), build its review sheet on the Contagion pattern.
- `BLUEDESERT_BEDAZZLE_SITTING_1` — volley + ticket-out + commission DONE (11
  jobs queued); open for art only; NEXT: review sheet when renders land.
- `FLOODEDCANYON_BEDAZZLE_SITTING_1` — volley + ticket-out + commission DONE (19
  jobs queued; rename ticketed `CRACKEDLANDS_FULL_RENAME_1`); open for art only;
  NEXT: review sheet when renders land.
- `ARTPIPE_FACING_COHERENCE_1` — inherited in doing from a prior BENCH window,
  untouched today; NEXT: read `daemon_run_20260927_derivefacings.log` against the
  item and either close on evidence or re-scope.
- `BIOME_MOD_UNIFICATION_1` — untouched today (compose manifest already carries
  wave 0); NEXT: write the spec-pass card agenda the item's own next step names.
- `DARKSEA_LIGHT_ATTRACTION_1` — untouched today, parked by design on the Grey
  and Scald danger passes; NEXT: design it inside whichever of those runs first.
- `GREYSEA_FLORA_PASS_1` — untouched today; NEXT: run the four sea-flora passes
  as one Fable design wave (one agent per sea, four distinct registers).
- `GREYSEA_SHIP_CRYSTALLISATION_1` — untouched today; NEXT: fold into the Grey
  Sea danger/floor design pass alongside the flora pass.
- `PROPANELAKE_FLORA_PASS_1` — untouched today; NEXT: rides the same four-sea
  design wave as the Grey.
- `SCALD_UNDERWATER_FLORA_1` — untouched today; NEXT: rides the same four-sea
  design wave (and sets plantDensity — the item's own first bar).
- `TWILIGHTSEA_FLORA_PASS_1` — untouched today; NEXT: rides the same four-sea
  design wave.
- `TWILIGHT_BOTTOM_CAST_1` — untouched today, needs owner; NEXT: draft the 6–8
  bottom-house resident sheet from the content doc §9.3 and card it to him.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A biome living under two names (program-table name vs campaign label) makes a
  single-name search report its sheet/roster missing (filed: LESSONS_INBOX).
- One agent's registry.jsonl query returned 0 for a subject with finished art
  while filename search over done/_artsrc found it — filename search is the
  working instrument for art existence (see:
  `bluedesert_bedazzle_cast_2026-09-28.md`, side finding).

## Closed since the last handoff (7)

- `PROPANELAKES_SHIPPING_NAMES_1` — a5a49c0d7
- `CHILL_WARLAB_ROUTES_1` — ba165f519
- `BLUEDESERT_MOD_DEPENDENCY_DECISION_1` — c28fa9719
- `GREYSEA_ANCHOR_CREATURES_1` — 17007f2ad
- `LONGSHADE_DESIGN_SITTING_1` — 59b95b8a4
- `STILLSAND_DESIGN_SITTING_1` — 59b95b8a4
- `WASTELAND_STORM_WEATHER_DEFS_1` — fcde34f5c

## Filed and still open (33) — the next seat's queue

- `SCALD_UNDERWATER_FLORA_1` — Scald underwater flora pass: set plantDensity and design strange small sea-plants - bacterial filament strings, sponges, soft corals, alien twists (ow
- `TERMINALBIOMES_REVIEW_FIXES_1` — TerminalBiomes 29-file review fix wave: 2 dead tickerType mechanisms (vaulisk lure never springs, mobile glower never runs), 6 more BUGs, 6 RISKs, 4 N
- `WAVEGLASS_PANEL_REPLACES_FLOOR_PLANT_1` — Retire RM_MoldMatRoof: the waveglass is a sky, not a floor plant - replace it with a shed panel that drifts down and is harvested
- `GREYSEA_FLORA_PASS_1` — Grey Sea underwater flora pass: cold pale register, own strange-flora roster (decision taken by question card 2026-09-26 - all sea floors get one, not
- `TWILIGHTSEA_FLORA_PASS_1` — Twilight Sea underwater flora pass: own strange-flora roster in the light-economy register (decision taken by question card 2026-09-26)
- `PROPANELAKE_FLORA_PASS_1` — Propane Lake underwater flora pass: not water-chemistry at all, own strange-flora roster (decision taken by question card 2026-09-26)
- `TWILIGHT_TENANCY_PAPER_REMOVAL_1` — Remove the Twilight tenancy paper layer from shipped code: delete RM_SkylightRight, RM_WellChart, RM_ClaimBuoy, the poaching-standing tracker and char
- `SPECULATIVE_ART_COMMISSION_1` — Speculative art commission 2026-09-27 (owner directive, free pipeline)
- `SELFTEST_FAILURES_TRIAGE_1` — Four pre-existing selftest failures found by a full run 2026-09-27 (none caused by that day's artpipe diff): (1) block_dll_source_mismatch 5/6 - 'DLL 
- `CHILL_SURFACE_SITTING_1` — The Chill surface: its own full biome pass sitting (Burner guardian place, shore ecology)
- `EMPIRE_ESCALATION_LADDER_1` — Empire escalation ladder: evadable probes first, new raid kinds per rung, until you move
- `TWILIGHT_REVIEW_FIXES_1` — Fix the 14 Twilight-wave code-review findings: 4 ship-blockers (plant CompTick lure, Never-ticker cargo float, undersurge on every biome, unstandable 
- `BIOME_MOD_UNIFICATION_1` — Merge the biome mods into ONE player-facing RimMandrake.Biomes mod with per-biome toggles (ruled by card 2026-09-27, Q17): spec pass + card agenda, th
- `GREYSEA_RULED_CONTENT_1` — Build the Grey Sea content ruled 2026-09-27: ten understorey flora at 0.22, catch rebalanced rare, crust clock + weather/berth multipliers, determinis
- `GREYSEA_USELESS_ARTIFACT_PLOT_1` — The Elders' sixth treasure - 'a beautifully useless artifact whose significance only becomes apparent much later' - is a PLOT HOOK: build the item onl
- `WORLDMAP_BIOME_APPEARANCE_1` — Regenerate our biomes' worldmap tile appearance AFTER the terminal repaint - measured 2026-09-27: only 2 of 29 BiomeDefs carry their own worldmap text
- `PLANETARY_LOADSCREEN_RENDERS_2` — Photo-realistic loadscreen planet renders seeded from OUR post-repaint worldmap beauty shots (ring, real terrain, color-to-reality mapping) - successo
- `BAROQUE_BEDAZZLE_PROGRAM_1` — The bedazzle program: eleven biomes raised to the Baroque bar in ruled order (Contagion first, Black Crags last), four-movement ritual, nine-mark bar 
- `STILLSAND_CAVERN_AUTHORING_1` — Author the Stillsand caverns as a place (ruled STILLSAND_DESIGN_SITTING_1 Q10, 2026-09-27: re-file both halves - beast+eggs went to DESERT_CAVERN_BEAS
- `CONTAGION_BEDAZZLE_SITTING_1` — Contagion bedazzle sitting - program row 1: review, roster fill, the four-turn volley to the nine-mark Baroque bar, then ticket + commission
- `CONTAGION_RULED_CONTENT_1` — Build the Contagion grotesque cast: 35 RM_ defs replacing the donor roster outright (no patches), 8 new species, 4 real flyers, Wombpod wired to the b
- `CONTAGION_MECHANICS_BUILD_1` — Build the Contagion mechanics: Burn/Bloom weather + tells, the Coalescence (one growing organism), Cloud Repulsor + gravship hardpoint, Sunbeam + arre
- `WASTELAND_BEDAZZLE_SITTING_1` — Wasteland bedazzle sitting - program row 2: review, roster fill, the four-turn volley to the nine-mark Baroque bar, then ticket + commission
- `WARCASKET_SUIT_CLASS_1` — Warcaskets as a cross-cutting suit class (ruled 2026-09-28): extreme-temp + vacuum + toxin rated, the alternative to space suits; very slow, bulky, co
- `BLUEDESERT_BEDAZZLE_SITTING_1` — Blue Desert bedazzle sitting - program row 3: score against the nine-mark bar, fill gaps, four-turn volley, ticket + commission
- `WASTELAND_RULED_CONTENT_1` — Build the Wasteland survivor cast: full RM_ donor replacement - 8 fauna ports, 3 new processors, 6 flora, bezoar/soot items, brine label renames, texP
- `WASTELAND_MECHANICS_BUILD_1` — Build the Wasteland mechanics: 20-cell Middenshell on TitanicCreatures, processor gatherable comps, ambient-dose comp, three storm WeatherDefs + Movin
- `BLUEDESERT_RULED_CONTENT_1` — Build the Blue Desert ruled cast: depth cast (zhaaz/vrisk/dovvik/utikka) + bedazzle four (Vhaulk/Murrek/Ossivel/Virr) + RM_BlueIce + water-plant cut +
- `BLUEDESERT_MECHANICS_BUILD_1` — Build the Blue Desert mechanics: vhaulk trigger-gated detonation (EMP-on-hit trap), Warnings study ladder + cold-cutting, blue-ice thaw rolls, three w
- `FLOODEDCANYON_BEDAZZLE_SITTING_1` — Flooded Canyon bedazzle sitting - program row 4: score against the nine-mark bar, fill flora/fauna, four-turn volley, ticket + commission (hard-deps F
- `CRACKEDLANDS_FULL_RENAME_1` — Full rename FloodedCanyon -> CrackedLands everywhere: defs, code, file names, docs (owner-typed 2026-09-28); live-tile/savegame check gates any defNam
- `CRACKEDLANDS_RULED_CONTENT_1` — Build the Cracked Lands ruled content: roster surgery (vanilla zoo out, RM_ migration, eopie to merchants), five new natives (Muttavaq/Uttaqar/Irqit/T
- `CRACKEDLANDS_MECHANICS_BUILD_1` — Build the Cracked Lands mechanics: the Swale (FlowWorks-normal, Utinni-locked biome discovery), survey+cistern loop, wall fossils + flood re-cut, gian

## Commits

```
e4140e46a FLOODEDCANYON_BEDAZZLE_SITTING_1: cast bible + art CSV (19 jobs queued)
1e28cd03a Ledger sync: bridge release after THEY_MOD_REPLICATION_1
0cccc3676 Close THEY_MOD_REPLICATION_1: ledger sync + item prose move to closed/
63427c882 THEY_MOD_REPLICATION_1: live-verify done, donor retired from the campaign list
9d45fedcb Fix 4 ParentName defects that never resolve: XmlInheritance keys on Name=, not defName
9ae2ba099 Cracked Lands sitting ticketed out: sheet amendment + two FOUNDRY builds
096a1d165 THEY_MOD_REPLICATION_1: offline re-verify pass, add greentideant load tier
e5dc2e84e Cracked Lands volley turn 2: rulings noted + full-rename ticket filed
1cbb4caf8 FOUNDRY handoff: Baroque Biomes unification complete
33408ba72 Record BIOME_MOD_UNIFICATION_1's execution in its own spec
440b20316 GREENTIDE_HUMMING_GROVE_1: deploy step done via the biome fold, needs -> owner
a4d0635b0 rimflow: close LONGSHADE_RM_MOD_BUILD_1 - step 5 proven by unification
8d1104bdf rimflow: close LANTERNDEEPS_TIER_COLLISION_1 - swap verified complete
37bb40e74 FLOODEDCANYON_BEDAZZLE_SITTING_1 movement 1: Cracked Lands nine-mark review
59408ed01 Note Q17 execution complete in the architecture doc
afbfa81e1 Retire test tiers that wanted now-folded biomes standalone
dff88d3e0 Fix 6 small RimUtinni mods' hard modDependencies on folded packageIds
25fa5c2db rimflow: note BIOME_MOD_UNIFICATION_1 with wave completion status
46564d867 rimflow: close BAROQUE_BIOMES_WAVE3_RETARGET_1, release bridge
d202a4f6b BAROQUE_BIOMES_WAVE3_RETARGET_1: consolidate loadAfter into mandrake.rm.biomes
... 248 more: git log --oneline d6e05eb2d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     BMT_FAUNA_ABSORPTION_1: full-list live verify, close if clean

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-generated by the health/maturity publishers
 M Transient/codebase_health.json   auto-generated by the health/maturity publishers
 M Transient/codebase_health_artifact.html   auto-generated by the health/maturity publishers
 M design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M design/Jawa/worldbuilding/biomes/rosters/the_propane_lakes.json   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M design/Jawa/worldbuilding/biomes/terminal_seas_cast_proposal_2026-09-25.md   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M design/RimMandrake/flowworks_liquid_matrix.md   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M design/RimMandrake/sea_dive_maps_spec.md   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M design/RimMandrake/sea_shore_mutator_spec.md   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M design/RimUtinni/vanilla_beast_excision_census.md   FOUNDRY's Chill seabed wave (its handoff 96c018a0e) - not mine, left in place
 M infrastructure/artpipe/daemon_run_20260927_derivefacings.log   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/failed/rut_greentideant_carapacewall_atlas.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/failed/rut_greentideant_carapacewall_menuicon.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Oorrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Oorrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Oorrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Ruukka_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Ruukka_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Ruukka_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_SandBusterMound_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/registry.jsonl   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/dashboards/hub/data/health.json   auto-generated by the health/maturity publishers
 M infrastructure/state/LESSONS_INBOX.md   mine (BENCH) - committed with this handoff
 M infrastructure/state/codebase_health_last.json   auto-generated by the health/maturity publishers
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   ledger/state churn - committed with this handoff
 M infrastructure/state/ledger/events/OWNER.jsonl   ledger/state churn - committed with this handoff
 M infrastructure/state/queue/BENCH.md   ledger/state churn - committed with this handoff
 M infrastructure/state/queue/FOUNDRY.md   ledger/state churn - committed with this handoff
?? deployed/config/ModsConfig.before-THEY_MOD_REPLICATION_1-retirement-write.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-baroque_wave0.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-baroque_wave0_control.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-firehawk.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-greentideant.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   load-round / modset archives - prior sessions, several seats
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/active/RM_CrackWaxSuit.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bleedleaf.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bleedleaf.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Blisterfloat_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Blisterfloat_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Blisterfloat_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Blisterfloat_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Blisterfloat_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Blisterfloat_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bloodlurk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bloodlurk_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bloodlurk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bloodlurk_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bloodlurk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Bloodlurk_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyFist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyFist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyMess_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyMess_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyMess_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyMess_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyMess_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BloodyMess_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BlueIce.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BlueIce.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilbulb.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilbulb.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilhide_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilhide_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilhide_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilhide_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilhide_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Boilhide_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BrinePlate.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_BrinePlate.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cinderfelt.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cinderfelt.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_CloudRepulsor.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_CloudRepulsor.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Crispling_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Crispling_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Crispling_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Crispling_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Crispling_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Crispling_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dakkra_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dakkra_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dakkra_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dakkra_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dakkra_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dakkra_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Danglemaw_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Danglemaw_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Danglemaw_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Danglemaw_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Danglemaw_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Danglemaw_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dewfringe.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dewfringe.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Doublemaw_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Doublemaw_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Doublemaw_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Doublemaw_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Doublemaw_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Doublemaw_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Drazz.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Drazz.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Duumma_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Duumma_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Duumma_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Duumma_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Duumma_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Duumma_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyebark.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyebark.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyestinger_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyestinger_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyestinger_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyestinger_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyestinger_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Eyestinger_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Fleshsop_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Fleshsop_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Fleshsop_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Fleshsop_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Fleshsop_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Fleshsop_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gaanok_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gawpsack_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gawpsack_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gawpsack_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gawpsack_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gawpsack_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gawpsack_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gennok_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Glasscrust.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Glasscrust.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gnashling_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gnashling_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gnashling_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gnashling_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gnashling_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gnashling_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorekite_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorekite_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorekite_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorekite_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorekite_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorekite_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorestalk.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gorestalk.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gravelgut_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gravelgut_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gravelgut_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gravelgut_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gravelgut_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gravelgut_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Grimewing_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Grimewing_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Grimewing_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Grimewing_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Grimewing_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Grimewing_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gristleswarm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gristleswarm_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gristleswarm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gristleswarm_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gristleswarm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Gristleswarm_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_HalfmadeTree.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_HalfmadeTree.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_HalfmadeTreeBlighted.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Hourbloom.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Hourbloom.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ikee_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ikee_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ikee_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ikee_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ikee_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ikee_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_KneelOllim.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_KneelOllim.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_KneelOllim_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_KneelOllim_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Lashgrass.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Lashgrass.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Liikka_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Liikka_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Liikka_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Liikka_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Liikka_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Liikka_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Loomma_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meatvine.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meatvine.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meltgut_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meltgut_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meltgut_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meltgut_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meltgut_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Meltgut_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenbeetle_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenbeetle_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenbeetle_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenbeetle_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenbeetle_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenbeetle_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenshell_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenshell_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenshell_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenshell_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenshell_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Middenshell_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Murrek_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Murrek_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Murrek_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Murrek_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Murrek_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Murrek_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Oorrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Oorrik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Oorrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Oorrik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Oorrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Oorrik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Orruhmu_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ossivel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ossivel_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ossivel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ossivel_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ossivel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ossivel_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Peeper_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Peeper_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Peeper_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Peeper_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Peeper_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Peeper_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pirrik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pusberry.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pusberry.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Qorrax_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Qorrax_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Qorrax_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Qorrax_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Qorrax_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Qorrax_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Rattlegrope.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Rattlegrope.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ruukka_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ruukka_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ruukka_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ruukka_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ruukka_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Ruukka_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SandBusterMound_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SandBusterMound_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sapblister.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sapblister.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scabspinner_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scabspinner_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scabspinner_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scabspinner_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scabspinner_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scabspinner_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scaldhide_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scaldhide_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scaldhide_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scaldhide_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scaldhide_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scaldhide_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scorchpod_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scorchpod_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scorchpod_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scorchpod_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scorchpod_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scorchpod_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumgrass.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumgrass.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumrat_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumrat_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumrat_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumrat_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumrat_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Scumrat_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Shambles_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Shambles_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Shambles_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Shambles_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Shambles_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Shambles_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skinflap_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skinflap_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skinflap_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skinflap_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skinflap_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skinflap_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Slagmole_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Slagmole_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Slagmole_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Slagmole_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Slagmole_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Slagmole_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloghog_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloghog_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloghog_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloghog_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloghog_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloghog_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloshbelly_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloshbelly_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloshbelly_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloshbelly_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloshbelly_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sloshbelly_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Smolderback_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Smolderback_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Smolderback_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Smolderback_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Smolderback_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Smolderback_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sollak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soorrak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SootGristleswarm_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SootGristleswarm_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SootGristleswarm_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sootgrazer_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sootgrazer_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sootgrazer_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sootgrazer_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sootgrazer_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sootgrazer_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SparkleechGrub_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SparkleechGrub_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_SparkleechGrub_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sparkleech_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sparkleech_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sparkleech_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sparkleech_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sparkleech_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sparkleech_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sunbeam.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sunbeam.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_TallScumgrass.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_TallScumgrass.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_b_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_b_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_b_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_b_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_b_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_b_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tebbra_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tekk.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tekk.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Toothmoss.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Toothmoss.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_UltracactusPad.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_UltracactusPad.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Veessa_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Veessa_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Veessa_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Veessa_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Veessa_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Veessa_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vhaulk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vhaulk_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vhaulk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vhaulk_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vhaulk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vhaulk_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Virr.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Virr.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Wartshrub.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Wartshrub.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Wombpod.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Wombpod.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_eldspar.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_eldspar.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_fuselight.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_fuselight.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_ghostpane.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_ghostpane.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_keelgrass.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_keelgrass.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_pitchpearl.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_pitchpearl.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_skyharp.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_skyharp.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_slackwax.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_slackwax.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_stillbloom.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_stillbloom.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_stonewater.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_stonewater.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_tarspool.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/chill_plant_tarspool.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/coalescence_stage1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/coalescence_stage1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/coalescence_stage2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/coalescence_stage2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/coalescence_stage3.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/coalescence_stage3.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_chillauroracollector_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmshademite_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmshademite_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmshademite_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmshademite_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmshademite_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmshademite_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_atlas.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_atlas.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_menuicon.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_greentideant_carapacewall_menuicon.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmshademite_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmshademite_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmshademite_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmshademite_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmshademite_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmshademite_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_FossilDeepStratum.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_FossilImpression.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_FossilSkeleton.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Irqit_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Irqit_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Irqit_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Muttavaq_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Muttavaq_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Muttavaq_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Swale.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Tarruq_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Tarruq_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Tarruq_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Uttaqar_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Uttaqar_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Uttaqar_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RM_Veqma.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/RUT_CrackWax.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/dashboards/hub/tabs/maturity.html   auto-generated by the health/maturity publishers
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   auto-generated by the health/maturity publishers
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   unattributed churn - not mine, left in place
?? infrastructure/state/logs/harvested/   unattributed churn - not mine, left in place
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/modlists/ModsConfig_before_miasma_predation_proof_2026-09-27.xml   load-round / modset archives - prior sessions, several seats
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   unattributed churn - not mine, left in place
?? src/RimMandrake/Utils/firehawk_flight_probe.py   unattributed churn - not mine, left in place
```

