# FOUNDRY_REBOOT_HANDOFF_202609132338 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609131929`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

`start_debug_game_ready` is unreliable against the owner's full 590-mod stack —
today it hit repeated `WorldGenStep`/pawn-generation exceptions
(`ModularWeapons2` x `ShowMeYourHands` MonoMod IL collision) and never produced
a game, just sat at Entry indefinitely with no long-event flag to poll on.
Matches `quicktest-crashes-full-modlist-use-cheap-mechanism-list` memory
exactly. **Never quicktest on the full list — always build a `modset_builder.py`
tier first** (new `warlab` and `oracle` tiers added this session as
examples/precedent for future mechanism-only content mods).

## What the owner should see

- Asked him directly mid-session (question cards): he ruled **leave
  `ANCIENT_WAR_LAB_1`'s remaining scope (world-tile siting, submerged-route
  gating) queued for now**; **the crater-ignition test IS allowed to actually
  mutate the real frozen Ash'karr world** when someone picks it up (not
  read-only) — recorded on `WAR_LAB_CRATER_HOOK_1`; and **he'll review the
  three pending sheets himself** (MAPGEN_GL_SHEET_1 v3, MAPGEN_PAINTER_V1_1
  v4, MACRO_GENERATOR_V0_1's round-4 chooser OPTIONS) rather than a rundown.
- I edited his **global** `C:\Users\Mandrake\.claude\settings.json` (outside
  this repo) to drop a stale `Write(~/.claude/**)` permission rule the CLI
  itself flagged as invalid — flagging it since it's outside the repo, not
  asking him to revert it.
- He also re-logged in the Windows `claude.exe` mid-session at my request
  (OAuth had expired) — confirmed working with a real live model response
  delivered in-game. If any OTHER in-game LLM consumer was silently failing
  for the same reason, it should now work too.

Nothing else this wave needs his eye beyond the three sheets above.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ANCIENT_WAR_LAB_1` — three-band KCSG dungeon quicktest+screenshot-proven
  live this session (real defNames, guardians+fauna confirmed via
  `jawa/list_pawns`; `Transient/ancient_war_lab/warlab_quicktest_proof_2026-09-13.png`).
  Two criteria still open: reachable-only-via-submerged-route (no world-tile
  siting attempted) and the crater ending (separate item). **Owner ruled:
  leave both queued, do not push into them next wave** unless he says
  otherwise. Next action if/when resumed: site `RUT_WarLabSite` over the
  Impact Site tile under Umbra (footprint now frozen, `LIQUID_BIOMES_MAP_1`
  closed) — this is new scope, not a continuation of tonight's proof.
- `MODCHECK_RUNNER_SWAP_LIVE_PROOF_1` — **CLOSED this session** (83196c8bb).
  Its own `verify` run had already recorded a PASS (2026-09-13T20:42:15Z,
  Pits config) from earlier in this window; nobody had closed it. No new
  work done, just the paperwork.
- `MODCHECK_SUITE_CORRECTIONS_1` — **not touched by me**, carried from
  earlier in this window (last note 2026-09-13T20:06:33Z, sha 81c6c00f9):
  4 of ~14 RED suites fixed (Inhabited's `_debug()` path, RimProperty's
  success-check), none live-reverified yet (no save/quicktest was loaded
  that tick). Exact next action per its own note: **live quicktest re-run of
  Inhabited + RimProperty + Graffiti + StructureInjections** to confirm the
  four fixes in one pass, then continue on the ~10 still-unaddressed REDs
  (Ninefold/Pyrelands/Droidworks/PawnFlavor/JawaIonWeapons/StarWarsRaces/
  Antiquities/ShipMemory/ResearchRetag partials, Aftermath 0/3 — separate
  cause, no `execute_debug_action` call at all in its suite).

## Traps learned

- `start_debug_game_ready` on the full 590-mod stack: real, reproducible
  `WorldGenStep`/pawn-gen exceptions (`ModularWeapons2` x `ShowMeYourHands`
  MonoMod IL collision), not a hang — stays at `Entry`, `hasCurrentGame:
  false`, `longEventPending: false` forever, no exception surfaced to the
  bridge caller. Only `Player.log`'s "Error while generating pawn.
  Rethrowing." lines reveal it. Filed to LESSONS_INBOX.
- `OracleClient.cs` (and likely any subprocess-wrapping C#) only read
  `stderr` on a nonzero exit — a real `claude -p` auth failure ("Failed to
  authenticate: OAuth session expired") printed to **stdout**, so the
  fallback log showed an empty, useless diagnostic. Fixed (fall back to
  stdout when stderr is empty); worth checking any OTHER subprocess wrapper
  in this repo for the same one-stream-only assumption.
- Debug-action categories from `[DebugAction(Cat, ...)]` attributes do NOT
  nest under their category name in the bridge's tree — they sit as flat
  entries directly under `Actions\<Label>` with a `category` field on the
  node. `list_debug_action_children({"path":"Actions"})` then grep the
  `category` field, not a guessed nested path.
- `GameComponentTick` (and therefore any `ConcurrentQueue`-based async
  delivery pattern like Oracle's) never drains while the game is **paused**
  — which `start_debug_game_ready` leaves it by default. `step_game_ticks`
  a handful of ticks (still paused, no risk) to force delivery before
  checking a result.

## Closed since the last handoff (3)

- `MODCHECK_SHELVED_TOGGLE_COMPONENTS_1` — 075eed21d695ca51e395bde07e789f85c67864d5
- `ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1` — 5d3a18555975dabda9ecae060a36cdf040ab5fb1 (live model
  response confirmed after owner's CLI re-login, see above)
- `MODCHECK_RUNNER_SWAP_LIVE_PROOF_1` — 83196c8bb (verify had already passed, just needed closing)

## Blocked, pending the owner (2)

- `MACRO_GENERATOR_V0_1` — round-4 chooser OPTIONS (three 8-premise sets,
  Fable design pass) sitting for his ruling
- `MAPGEN_CONVERGENCE_LOOP_1` — its own file explicitly says don't resume
  corpus-stats convergence work without a fresh ruling; two fresh sheets
  (`MAPGEN_GL_SHEET_1` v3, `MAPGEN_PAINTER_V1_1` v4) are both `needs:owner`
  ahead of it anyway

## Filed and still open (9) — the next seat's queue

- `DEBUG_ACTION_ENUM_CRASH_1` — search_debug_actions/list_debug_action_children(Actions) crash on any broad query (RitualSiegeWithSpecifics NREs in PrepareNode)
- `BAZAAR_WINDOW_GRID_1` — The Bazaar slice 1: Dialog_Trade replacement via WindowStack.Add intercept + virtualized grid, presets, wishlist, plugin defs — silver math identical 
- `BAZAAR_PRICE_ENGINE_1` — The Bazaar slice 2: read-side RM_BazaarEconomy (worldTag-seeded buckets, history ring, drift+clamp) + intel layers L0-L4 + the three found artifacts —
- `BAZAAR_HAGGLE_DUEL_1` — The Bazaar slice 3: WHOLE-DEAL patience-meter haggle duel (owner: per-item rejected as monotonous) — crits give junk freebies or true rumors; determin
- `BAZAAR_BROKER_TAB_1` — The Bazaar slice 4: bulk-liquid Broker tab — renders Liquid Logistics' tank API both directions at worldTag-weighted prices
- `BAZAAR_BANTER_LINES_1` — The Bazaar slice 5: authored banter pools (day one) + dormant claude -p Oracle consumer gated on ORACLE_EXPERIMENT_SPIKE_1 live proof — model: opus
- `BAZAAR_DISPLACEMENT_PASS_1` — Retire Trade UI Revised + Utility Columns + VTE from the campaign list after Bazaar slices 1-2 prove live; VTE unwind rehearsed on a save copy first
- `PIT_TRAP_VISUAL_REDESIGN_1` — Design the pit trap's real visual interface (covered/sprung/occupied, size) - owner wants a big dark pit, not the vanilla trap icon
- `FLORA_LEGIBILITY_BAR_1` — Flora legibility bar: own grading pass + model (no keyline law), sizeBin-scaled canvases, no stroke — carries the owner's alientree + ambrosia flags

## Commits

```
3e73efd34 rimflow: re-render FOUNDRY queue after Oracle confirmation note
c5b3e3ad3 Pilot sheet: four canon-brief rows (pekopeko cobalt, dactillion, wyyyschokk + dragonsnake borderline)
28d483f55 Pilot sheet: terramorph (wild, matches donor fantasy), tentacular, anooba B2 rows added
6213bf023 rimflow: confirm live Oracle model response after owner's CLI re-login
1d33f6320 Toyfig pilot v2: leg-sparing renders (owner's MegaFauna/AA dialect) — three-way A/B sheet
2408ae738 rimflow: close ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1 ledger entry
5d3a18555 ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1: live-verify the claude -p transport, fix a diagnostic bug
8c28b318f Toy-figurine pilot A/B sheet: 4 law re-renders vs current, all passed the locked gate
d8aeb00c3 TOYFIG_LAW_PILOT_1: 4 law-compliant re-renders queued at priority 1 for owner A/B
71fd324fb rimflow: close ART_QUEUE_DRAWSIZE_BACKFILL_1 at 247f7d481
247f7d481 drawSize backfill v5 + class-aware regate: creatures at true size, flora exempt from gate and stroke
f206a4e08 ANCIENT_WAR_LAB_1: quicktest+screenshot proof of the three-band KCSG dungeon
646c34650 Item file for ART_QUEUE_DRAWSIZE_BACKFILL_1
1e053ccf7 drawSize-aware legibility: gate tiers and canvas ceiling scale by cells; jobs carry drawsize
cdb0120db Final works-band review sheet: 153/353 under locked rules (9 as-is, 144 stroke-promoted)
52674def9 Lock the legibility rules: outside-stroke defaults, 256 canvas refusal, margin exit 4, model floors, auto-reinforce flow
e8565965a Keyline reinforcement v3: OUTSIDE stroke (owner: outline around the art, never etched in)
47c1b617e A/B stroke turned up to 1.0 / 5% (owner: more strengthening, none would suffer) — 18/19 reach works band
0b4968359 A/B sheet: correct the invented-rule line to v2 stroke settings
e51459064 Keyline reinforcement v2: true outline stroke (fringe solidified) — visible at play zoom; A/B rebuilt at 0.9/3%
ee6d72895 Fitted 3-band legibility gate (LOO rho 0.81) + keyline reinforcement tool + owner A/B sheet
212e5871c Owner grading batches 1-4 + correlation: keyline_v1@32 rho=0.83, all 19 overrides works->borderline
05375bebe Metric zoo: complete the 8 space-path rows (70/70)
af8587176 Metric zoo values for the 70 grading-sheet rows
2644a6d62 Legibility metric zoo + owner grading sheet (70 rows, 22 shipping-art probes interleaved)
ac5215581 Legibility gate v2: keyline is now outline SURVIVAL (owner feedback) + diagnostic overlay sheets
1dfaacb14 Legibility gate review sheets: 353 pipeline sprites, 164 pass / 189 fail, borderline sheet
5b2903ecf rimflow: close ART_LEGIBILITY_GATE_1 at b2d7ea116
b2d7ea116 ART_LEGIBILITY_GATE_1: automated downscale-legibility gate, calibrated + wired into artpiped
83196c8bb Bazaar: Utility Columns off the retire list (it's a building mod); retire = absorb-then-improve first
86c530c06 ledger sync: FOUNDRY MODCHECK_SUITE_CORRECTIONS_1 reclaim/notes this tick
81c6c00f9 MODCHECK_SUITE_CORRECTIONS_1: RimProperty checks set_thing_props' own success
ca6e58dd3 The Bazaar ruled: scavenger trade window design + 6 build items
a2a1f6717 ledger sync: FOUNDRY queue activity for MODCHECK_SHELVED_TOGGLE_COMPONENTS_1 close, MODCHECK_SUITE_CORRECTIONS_1 claim/notes, DEBUG_ACTION_ENUM_CRASH_1 filing
08ddb4ccc MODCHECK_SUITE_CORRECTIONS_1: fix Inhabited's _debug() debug-action path
075eed21d MODCHECK_SHELVED_TOGGLE_COMPONENTS_1: set_setting() uses jawa/mod_settings_field
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found
  yet, so this is a genuinely in-progress load, not a stuck one)
- recorded  : UP
- Bridge: FREE (I released it before this handoff)
- **The game is mid-restart on the owner's restored full 590-mod list** (I
  tore it down twice this session for the `warlab` and `oracle` test tiers,
  restoring the full list and relaunching each time). This is a normal
  ~15-25 min full-stack cold load, already fingerprint-clean (590/590
  resolved, 0 missing per `refresh.py --fingerprint`) — just let it finish;
  do not touch ModsConfig.xml until it's confirmed up.
- `harvest_log.py` on the PRIOR full-stack log (before I tore it down for the
  oracle test) showed several RED findings above baseline (1 dead mod by
  static ctor, 4 cross-reference failures, 10 stale Scribe entries, 74 def
  ConfigErrors vs baseline 17, 16 failed patch ops vs baseline 5, 8 Outer Rim
  new-mod errors, JawaBench readiness MISSING) — **not triaged this session**,
  no time. Whoever wakes next should re-run `harvest_log.py` fresh once THIS
  load finishes (mod set hasn't changed, so the same REDs likely recur) and
  decide whether any are new regressions worth filing.

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M Transient/legibility_final_review_2026-09-13/decisions.json
 M infrastructure/artpipe/art_status.html
 M infrastructure/artpipe/art_status.json
 D infrastructure/artpipe/pending/alientreepolluted_v1.json
 D infrastructure/artpipe/pending/ambrosia_v1.json
 D infrastructure/artpipe/pending/aridgrass_v1.json
 D infrastructure/artpipe/pending/arpeau_v1.json
 D infrastructure/artpipe/pending/bindweed_v1.json
 D infrastructure/artpipe/pending/bloddle_v1.json
 D infrastructure/artpipe/pending/bloodbouquet_v1.json
 D infrastructure/artpipe/pending/brambles_v1.json
 D infrastructure/artpipe/pending/bubblespore_v1.json
 D infrastructure/artpipe/pending/bush_v1.json
 D infrastructure/artpipe/pending/chakroot_v1.json
 D infrastructure/artpipe/pending/creepstern_v1.json
 D infrastructure/artpipe/pending/crimsoncushion_v1.json
 D infrastructure/artpipe/pending/crystalflower_v1.json
 D infrastructure/artpipe/pending/dervish_v1.json
 D infrastructure/artpipe/pending/doomsprout_v1.json
 D infrastructure/artpipe/pending/eclipsusflower_v1.json
 D infrastructure/artpipe/pending/eclipsusleaves_v1.json
 D infrastructure/artpipe/pending/felucianglowspore_v1.json
 D infrastructure/artpipe/pending/firelavender_v1.json
 D infrastructure/artpipe/pending/flakespirefungus_v1.json
 D infrastructure/artpipe/pending/frostleaf_v1.json
 D infrastructure/artpipe/pending/gargantuanlithops_v1.json
 D infrastructure/artpipe/pending/giantseptimum_v1.json
 D infrastructure/artpipe/pending/giantstikehr_v1.json
 D infrastructure/artpipe/pending/gianttoxicflower_v1.json
 D infrastructure/artpipe/pending/glowinggrass_v1.json
 D infrastructure/artpipe/pending/graygrass_v1.json
 D infrastructure/artpipe/pending/grimmoss_v1.json
 D infrastructure/artpipe/pending/gutterplantain_v1.json
 D infrastructure/artpipe/pending/halfalientree_v1.json
 D infrastructure/artpipe/pending/hardygrass_v1.json
 D infrastructure/artpipe/pending/healroot_v1.json
 D infrastructure/artpipe/pending/heatsinkfungus_v1.json
 D infrastructure/artpipe/pending/hubbagourd_v1.json
 D infrastructure/artpipe/pending/magmacactus_v1.json
 D infrastructure/artpipe/pending/mangrovepalm_v1.json
 D infrastructure/artpipe/pending/martyr_v1.json
 D infrastructure/artpipe/pending/mortalmorel_v1.json
 D infrastructure/artpipe/pending/mujafruit_v1.json
 D infrastructure/artpipe/pending/nogtyl_v1.json
 D infrastructure/artpipe/pending/nuitae_v1.json
 D infrastructure/artpipe/pending/nysyllin_v1.json
 D infrastructure/artpipe/pending/parasiticmangrove_v1.json
 D infrastructure/artpipe/pending/poisonplanttallgrass_v1.json
 D infrastructure/artpipe/pending/poisonshrub_v1.json
 D infrastructure/artpipe/pending/polux_v1.json
 D infrastructure/artpipe/pending/poluxbush_v1.json
 D infrastructure/artpipe/pending/poxsorghum_v1.json
 D infrastructure/artpipe/pending/primordialgrass_v1.json
 D infrastructure/artpipe/pending/primordialtallgrass_v1.json
 D infrastructure/artpipe/pending/pusmelon_v1.json
 D infrastructure/artpipe/pending/rainbowtongue_v1.json
 D infrastructure/artpipe/pending/ravennettle_v1.json
 D infrastructure/artpipe/pending/recurvedstropharia_v1.json
 D infrastructure/artpipe/pending/redbugloss_v1.json
 D infrastructure/artpipe/pending/redleaves_v1.json
 D infrastructure/artpipe/pending/redplantstall_v1.json
 D infrastructure/artpipe/pending/reeds_v1.json
 D infrastructure/artpipe/pending/rgtoxigrass_v1.json
 D infrastructure/artpipe/pending/rimenodules_v1.json
 D infrastructure/artpipe/pending/ripthorn_v1.json
 D infrastructure/artpipe/pending/sagecrust_v1.json
 D infrastructure/artpipe/pending/scorchedstars_v1.json
 D infrastructure/artpipe/pending/septimum_v1.json
 D infrastructure/artpipe/pending/sewerreed_v1.json
 D infrastructure/artpipe/pending/shinecap_v1.json
 D infrastructure/artpipe/pending/shrublow_v1.json
 D infrastructure/artpipe/pending/skulltop_v1.json
 D infrastructure/artpipe/pending/slimecasia_v1.json
 D infrastructure/artpipe/pending/slimyfern_v1.json
 D infrastructure/artpipe/pending/slimytree_v1.json
 D infrastructure/artpipe/pending/snaketails_v1.json
 D infrastructure/artpipe/pending/tallslimygrass_v1.json
 D infrastructure/artpipe/pending/talltoxigrass_v1.json
 D infrastructure/artpipe/pending/tangletea_v1.json
 D infrastructure/artpipe/pending/tentacular_v1.json
 D infrastructure/artpipe/pending/tinklegrass_v1.json
 D infrastructure/artpipe/pending/tooketrap_v1.json
 D infrastructure/artpipe/pending/toxibulb_v1.json
 D infrastructure/artpipe/pending/toxicivy_v1.json
 D infrastructure/artpipe/pending/toxipotato_v1.json
 D infrastructure/artpipe/pending/tropicalchokevine_v1.json
 D infrastructure/artpipe/pending/tumorbulbhyacinth_v1.json
 D infrastructure/artpipe/pending/twisteddandelion_v1.json
 D infrastructure/artpipe/pending/twistingthorngrass_v1.json
 D infrastructure/artpipe/pending/twistingthornweed_v1.json
 D infrastructure/artpipe/pending/violetwimple_v1.json
 D infrastructure/artpipe/pending/weepingtoxberry_v1.json
 D infrastructure/artpipe/pending/wildrashroot_v1.json
 D infrastructure/artpipe/pending/witchesoyster_v1.json
 D infrastructure/artpipe/pending/wrinklecap_v1.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/artsheets.json
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/dashboards/hub/data/publish_ready.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/modcheck_status.json
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll
 M src/RimMandrake/Utils/atomic_copy.py
 M src/RimMandrake/Utils/modcheck/runner.py
 M src/RimMandrake/Utils/modcheck/selftest.py
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/daemon_run_20260913_134734.log
?? infrastructure/artpipe/daemon_run_20260913_152021.log
?? infrastructure/artpipe/daemon_run_20260913_153234.log
?? infrastructure/artpipe/daemon_run_20260913_155045.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/aaklac_v1.json
?? infrastructure/artpipe/done/aaklac_v1.manifest.json
?? infrastructure/artpipe/done/abtoxigrass_v1.json
?? infrastructure/artpipe/done/abtoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/agariluxprime_v1.json
?? infrastructure/artpipe/done/agariluxprime_v1.manifest.json
?? infrastructure/artpipe/done/aliengrass_v1.json
?? infrastructure/artpipe/done/aliengrass_v1.manifest.json
?? infrastructure/artpipe/done/alientree_v1.json
?? infrastructure/artpipe/done/alientree_v1.manifest.json
?? infrastructure/artpipe/done/alientreepolluted_v1.json
?? infrastructure/artpipe/done/alientreepolluted_v1.manifest.json
?? infrastructure/artpipe/done/ambrosia_v1.json
?? infrastructure/artpipe/done/ambrosia_v1.manifest.json
?? infrastructure/artpipe/done/anooba_toyfig_a_east.json
?? infrastructure/artpipe/done/anooba_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/anooba_toyfig_b2_east.json
?? infrastructure/artpipe/done/anooba_toyfig_b2_east.manifest.json
?? infrastructure/artpipe/done/aridgrass_v1.json
?? infrastructure/artpipe/done/aridgrass_v1.manifest.json
?? infrastructure/artpipe/done/arpeau_v1.json
?? infrastructure/artpipe/done/arpeau_v1.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_east_r2.json
?? infrastructure/artpipe/done/ashrunner_v1_east_r2.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_north.json
?? infrastructure/artpipe/done/ashrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/ashrunner_v1_south_r2.json
?? infrastructure/artpipe/done/ashrunner_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_east.json
?? infrastructure/artpipe/done/bilespawn_v1_east.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_north_r2.json
?? infrastructure/artpipe/done/bilespawn_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/bilespawn_v1_south.json
?? infrastructure/artpipe/done/bilespawn_v1_south.manifest.json
?? infrastructure/artpipe/done/bindweed_v1.json
?? infrastructure/artpipe/done/bindweed_v1.manifest.json
?? infrastructure/artpipe/done/bleedingtooth_v1.json
?? infrastructure/artpipe/done/bleedingtooth_v1.manifest.json
?? infrastructure/artpipe/done/bloddle_v1.json
?? infrastructure/artpipe/done/bloddle_v1.manifest.json
?? infrastructure/artpipe/done/bloodbouquet_v1.json
?? infrastructure/artpipe/done/bloodbouquet_v1.manifest.json
?? infrastructure/artpipe/done/boma_toyfig_a_east.json
?? infrastructure/artpipe/done/boma_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/boma_toyfig_b_east.json
?? infrastructure/artpipe/done/boma_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/brambles_v1.json
?? infrastructure/artpipe/done/brambles_v1.manifest.json
?? infrastructure/artpipe/done/brightbells_v1.json
?? infrastructure/artpipe/done/brightbells_v1.manifest.json
?? infrastructure/artpipe/done/bryolux_v1.json
?? infrastructure/artpipe/done/bryolux_v1.manifest.json
?? infrastructure/artpipe/done/bubblespore_v1.json
?? infrastructure/artpipe/done/bubblespore_v1.manifest.json
?? infrastructure/artpipe/done/bush_v1.json
?? infrastructure/artpipe/done/bush_v1.manifest.json
?? infrastructure/artpipe/done/chakroot_v1.json
?? infrastructure/artpipe/done/chakroot_v1.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/corronip_v1_east.json
?? infrastructure/artpipe/done/corronip_v1_east.manifest.json
?? infrastructure/artpipe/done/corronip_v1_north.json
?? infrastructure/artpipe/done/corronip_v1_north.manifest.json
?? infrastructure/artpipe/done/corronip_v1_south.json
?? infrastructure/artpipe/done/corronip_v1_south.manifest.json
?? infrastructure/artpipe/done/creepstern_v1.json
?? infrastructure/artpipe/done/creepstern_v1.manifest.json
?? infrastructure/artpipe/done/crimsoncap_v1.json
?? infrastructure/artpipe/done/crimsoncap_v1.manifest.json
?? infrastructure/artpipe/done/crimsoncushion_v1.json
?? infrastructure/artpipe/done/crimsoncushion_v1.manifest.json
?? infrastructure/artpipe/done/crystalflower_v1.json
?? infrastructure/artpipe/done/crystalflower_v1.manifest.json
?? infrastructure/artpipe/done/crystalhorn_v1.json
?? infrastructure/artpipe/done/crystalhorn_v1.manifest.json
?? infrastructure/artpipe/done/dactillion_toyfig_b_east.json
?? infrastructure/artpipe/done/dactillion_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/dervish_v1.json
?? infrastructure/artpipe/done/dervish_v1.manifest.json
?? infrastructure/artpipe/done/dewback_toyfig_a_east.json
?? infrastructure/artpipe/done/dewback_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/dewback_toyfig_b_east.json
?? infrastructure/artpipe/done/dewback_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/dewshrooms_v1.json
?? infrastructure/artpipe/done/dewshrooms_v1.manifest.json
?? infrastructure/artpipe/done/direwail_v1_east.json
?? infrastructure/artpipe/done/direwail_v1_east.manifest.json
?? infrastructure/artpipe/done/direwail_v1_north.json
?? infrastructure/artpipe/done/direwail_v1_north.manifest.json
?? infrastructure/artpipe/done/direwail_v1_south.json
?? infrastructure/artpipe/done/direwail_v1_south.manifest.json
?? infrastructure/artpipe/done/doomsprout_v1.json
?? infrastructure/artpipe/done/doomsprout_v1.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/eclipsusflower_v1.json
?? infrastructure/artpipe/done/eclipsusflower_v1.manifest.json
?? infrastructure/artpipe/done/eclipsusleaves_v1.json
?? infrastructure/artpipe/done/eclipsusleaves_v1.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_toyfig_a_east.json
?? infrastructure/artpipe/done/fanback_toyfig_a_east.manifest.json
?? infrastructure/artpipe/done/fanback_toyfig_b_east.json
?? infrastructure/artpipe/done/fanback_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/felucianglowspore_v1.json
?? infrastructure/artpipe/done/felucianglowspore_v1.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/firelavender_v1.json
?? infrastructure/artpipe/done/firelavender_v1.manifest.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.manifest.json
?? infrastructure/artpipe/done/firevinetree_v1.json
?? infrastructure/artpipe/done/firevinetree_v1.manifest.json
?? infrastructure/artpipe/done/flakespirefungus_v1.json
?? infrastructure/artpipe/done/flakespirefungus_v1.manifest.json
?? infrastructure/artpipe/done/frostleaf_v1.json
?? infrastructure/artpipe/done/frostleaf_v1.manifest.json
?? infrastructure/artpipe/done/fruitingbodies_v1.json
?? infrastructure/artpipe/done/fruitingbodies_v1.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
?? infrastructure/artpipe/done/gargantuanlithops_v1.json
?? infrastructure/artpipe/done/gargantuanlithops_v1.manifest.json
?? infrastructure/artpipe/done/giantagarilux_v1.json
?? infrastructure/artpipe/done/giantagarilux_v1.manifest.json
?? infrastructure/artpipe/done/giantagaritox_v1.json
?? infrastructure/artpipe/done/giantagaritox_v1.manifest.json
?? infrastructure/artpipe/done/giantgamma_v1.json
?? infrastructure/artpipe/done/giantgamma_v1.manifest.json
?? infrastructure/artpipe/done/giantseptimum_v1.json
?? infrastructure/artpipe/done/giantseptimum_v1.manifest.json
?? infrastructure/artpipe/done/giantstikehr_v1.json
?? infrastructure/artpipe/done/giantstikehr_v1.manifest.json
?? infrastructure/artpipe/done/gianttoxicflower_v1.json
?? infrastructure/artpipe/done/gianttoxicflower_v1.manifest.json
?? infrastructure/artpipe/done/globularplant_v1.json
?? infrastructure/artpipe/done/globularplant_v1.manifest.json
?? infrastructure/artpipe/done/glowingagarilux_v1.json
?? infrastructure/artpipe/done/glowingagarilux_v1.manifest.json
?? infrastructure/artpipe/done/glowinggrass_v1.json
?? infrastructure/artpipe/done/glowinggrass_v1.manifest.json
?? infrastructure/artpipe/done/glowstool_v1.json
?? infrastructure/artpipe/done/glowstool_v1.manifest.json
?? infrastructure/artpipe/done/gomphoeria_v1.json
?? infrastructure/artpipe/done/gomphoeria_v1.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_east.json
?? infrastructure/artpipe/done/gorewalker_v1_east.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_north.json
?? infrastructure/artpipe/done/gorewalker_v1_north.manifest.json
?? infrastructure/artpipe/done/gorewalker_v1_south.json
?? infrastructure/artpipe/done/gorewalker_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/graygrass_v1.json
?? infrastructure/artpipe/done/graygrass_v1.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/greenrockfern_v1.json
?? infrastructure/artpipe/done/greenrockfern_v1.manifest.json
?? infrastructure/artpipe/done/greylady_v1.json
?? infrastructure/artpipe/done/greylady_v1.manifest.json
?? infrastructure/artpipe/done/grimmoss_v1.json
?? infrastructure/artpipe/done/grimmoss_v1.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/gutterplantain_v1.json
?? infrastructure/artpipe/done/gutterplantain_v1.manifest.json
?? infrastructure/artpipe/done/halfalientree_v1.json
?? infrastructure/artpipe/done/halfalientree_v1.manifest.json
?? infrastructure/artpipe/done/hardygrass_v1.json
?? infrastructure/artpipe/done/hardygrass_v1.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/healroot_v1.json
?? infrastructure/artpipe/done/healroot_v1.manifest.json
?? infrastructure/artpipe/done/heatsinkfungus_v1.json
?? infrastructure/artpipe/done/heatsinkfungus_v1.manifest.json
?? infrastructure/artpipe/done/hubbagourd_v1.json
?? infrastructure/artpipe/done/hubbagourd_v1.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_east.json
?? infrastructure/artpipe/done/huskrunner_v1_east.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_north.json
?? infrastructure/artpipe/done/huskrunner_v1_north.manifest.json
?? infrastructure/artpipe/done/huskrunner_v1_south.json
?? infrastructure/artpipe/done/huskrunner_v1_south.manifest.json
?? infrastructure/artpipe/done/hydenocktree_v1.json
?? infrastructure/artpipe/done/hydenocktree_v1.manifest.json
?? infrastructure/artpipe/done/iashiphus_v1.json
?? infrastructure/artpipe/done/iashiphus_v1.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/jogantree_v1.json
?? infrastructure/artpipe/done/jogantree_v1.manifest.json
?? infrastructure/artpipe/done/jungletree_v1.json
?? infrastructure/artpipe/done/jungletree_v1.manifest.json
?? infrastructure/artpipe/done/keeningcordax_v1.json
?? infrastructure/artpipe/done/keeningcordax_v1.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/largeslimytree_v1.json
?? infrastructure/artpipe/done/largeslimytree_v1.manifest.json
?? infrastructure/artpipe/done/lilacbeacon_v1.json
?? infrastructure/artpipe/done/lilacbeacon_v1.manifest.json
?? infrastructure/artpipe/done/magmacactus_v1.json
?? infrastructure/artpipe/done/magmacactus_v1.manifest.json
?? infrastructure/artpipe/done/mangrovepalm_v1.json
?? infrastructure/artpipe/done/mangrovepalm_v1.manifest.json
?? infrastructure/artpipe/done/mangrovetree_v1.json
?? infrastructure/artpipe/done/mangrovetree_v1.manifest.json
?? infrastructure/artpipe/done/martyr_v1.json
?? infrastructure/artpipe/done/martyr_v1.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_east.json
?? infrastructure/artpipe/done/mireflit_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_north.json
?? infrastructure/artpipe/done/mireflit_v1_north.manifest.json
?? infrastructure/artpipe/done/mireflit_v1_south.json
?? infrastructure/artpipe/done/mireflit_v1_south.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.json
?? infrastructure/artpipe/done/mireflitwarden_v1_east.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_north_r2.json
?? infrastructure/artpipe/done/mireflitwarden_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.json
?? infrastructure/artpipe/done/mireflitwarden_v1_south.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_east.json
?? infrastructure/artpipe/done/miremoth_v1_east.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_north.json
?? infrastructure/artpipe/done/miremoth_v1_north.manifest.json
?? infrastructure/artpipe/done/miremoth_v1_south.json
?? infrastructure/artpipe/done/miremoth_v1_south.manifest.json
?? infrastructure/artpipe/done/mortalmorel_v1.json
?? infrastructure/artpipe/done/mortalmorel_v1.manifest.json
?? infrastructure/artpipe/done/mujafruit_v1.json
?? infrastructure/artpipe/done/mujafruit_v1.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/nogtyl_v1.json
?? infrastructure/artpipe/done/nogtyl_v1.manifest.json
?? infrastructure/artpipe/done/nuitae_v1.json
?? infrastructure/artpipe/done/nuitae_v1.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_east.json
?? infrastructure/artpipe/done/oozemaw_v1_east.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_north.json
?? infrastructure/artpipe/done/oozemaw_v1_north.manifest.json
?? infrastructure/artpipe/done/oozemaw_v1_south.json
?? infrastructure/artpipe/done/oozemaw_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/parasiticmangrove_v1.json
?? infrastructure/artpipe/done/parasiticmangrove_v1.manifest.json
?? infrastructure/artpipe/done/pekopeko_toyfig_b_east.json
?? infrastructure/artpipe/done/pekopeko_toyfig_b_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/poisonplanttallgrass_v1.json
?? infrastructure/artpipe/done/poisonplanttallgrass_v1.manifest.json
?? infrastructure/artpipe/done/poisonshrub_v1.json
?? infrastructure/artpipe/done/poisonshrub_v1.manifest.json
?? infrastructure/artpipe/done/polux_v1.json
?? infrastructure/artpipe/done/polux_v1.manifest.json
?? infrastructure/artpipe/done/poluxbush_v1.json
?? infrastructure/artpipe/done/poluxbush_v1.manifest.json
?? infrastructure/artpipe/done/poxsorghum_v1.json
?? infrastructure/artpipe/done/poxsorghum_v1.manifest.json
?? infrastructure/artpipe/done/primordialgrass_v1.json
?? infrastructure/artpipe/done/primordialgrass_v1.manifest.json
?? infrastructure/artpipe/done/primordialtallgrass_v1.json
?? infrastructure/artpipe/done/primordialtallgrass_v1.manifest.json
?? infrastructure/artpipe/done/pusmelon_v1.json
?? infrastructure/artpipe/done/pusmelon_v1.manifest.json
?? infrastructure/artpipe/done/rainbowtongue_v1.json
?? infrastructure/artpipe/done/rainbowtongue_v1.manifest.json
?? infrastructure/artpipe/done/ravennettle_v1.json
?? infrastructure/artpipe/done/ravennettle_v1.manifest.json
?? infrastructure/artpipe/done/recurvedstropharia_v1.json
?? infrastructure/artpipe/done/recurvedstropharia_v1.manifest.json
?? infrastructure/artpipe/done/redbugloss_v1.json
?? infrastructure/artpipe/done/redbugloss_v1.manifest.json
?? infrastructure/artpipe/done/redleaves_v1.json
?? infrastructure/artpipe/done/redleaves_v1.manifest.json
?? infrastructure/artpipe/done/redplantstall_v1.json
?? infrastructure/artpipe/done/redplantstall_v1.manifest.json
?? infrastructure/artpipe/done/reeds_v1.json
?? infrastructure/artpipe/done/reeds_v1.manifest.json
?? infrastructure/artpipe/done/rgtoxigrass_v1.json
?? infrastructure/artpipe/done/rgtoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/rimenodules_v1.json
?? infrastructure/artpipe/done/rimenodules_v1.manifest.json
?? infrastructure/artpipe/done/ripthorn_v1.json
?? infrastructure/artpipe/done/ripthorn_v1.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_east.json
?? infrastructure/artpipe/done/rotscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_north.json
?? infrastructure/artpipe/done/rotscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/sagecrust_v1.json
?? infrastructure/artpipe/done/sagecrust_v1.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/scorchedstars_v1.json
?? infrastructure/artpipe/done/scorchedstars_v1.manifest.json
?? infrastructure/artpipe/done/septimum_v1.json
?? infrastructure/artpipe/done/septimum_v1.manifest.json
?? infrastructure/artpipe/done/sewerreed_v1.json
?? infrastructure/artpipe/done/sewerreed_v1.manifest.json
?? infrastructure/artpipe/done/shinecap_v1.json
?? infrastructure/artpipe/done/shinecap_v1.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/shrublow_v1.json
?? infrastructure/artpipe/done/shrublow_v1.manifest.json
?? infrastructure/artpipe/done/skulltop_v1.json
?? infrastructure/artpipe/done/skulltop_v1.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/slimecasia_v1.json
?? infrastructure/artpipe/done/slimecasia_v1.manifest.json
?? infrastructure/artpipe/done/slimyfern_v1.json
?? infrastructure/artpipe/done/slimyfern_v1.manifest.json
?? infrastructure/artpipe/done/slimytree_v1.json
?? infrastructure/artpipe/done/slimytree_v1.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/snaketails_v1.json
?? infrastructure/artpipe/done/snaketails_v1.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_east.json
?? infrastructure/artpipe/done/sporehulk_v1_east.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_north.json
?? infrastructure/artpipe/done/sporehulk_v1_north.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_south.json
?? infrastructure/artpipe/done/sporehulk_v1_south.manifest.json
?? infrastructure/artpipe/done/sugarfamewort_v1.json
?? infrastructure/artpipe/done/sugarfamewort_v1.manifest.json
?? infrastructure/artpipe/done/tallslimygrass_v1.json
?? infrastructure/artpipe/done/tallslimygrass_v1.manifest.json
?? infrastructure/artpipe/done/talltoxigrass_v1.json
?? infrastructure/artpipe/done/talltoxigrass_v1.manifest.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.manifest.json
?? infrastructure/artpipe/done/tangletea_v1.json
?? infrastructure/artpipe/done/tangletea_v1.manifest.json
?? infrastructure/artpipe/done/tentacular_v1.json
?? infrastructure/artpipe/done/tentacular_v1.manifest.json
?? infrastructure/artpipe/done/tinklegrass_v1.json
?? infrastructure/artpipe/done/tinklegrass_v1.manifest.json
?? infrastructure/artpipe/done/tooketrap_v1.json
?? infrastructure/artpipe/done/tooketrap_v1.manifest.json
?? infrastructure/artpipe/done/toxibulb_v1.json
?? infrastructure/artpipe/done/toxibulb_v1.manifest.json
?? infrastructure/artpipe/done/toxicgamma_v1.json
?? infrastructure/artpipe/done/toxicgamma_v1.manifest.json
?? infrastructure/artpipe/done/toxicivy_v1.json
?? infrastructure/artpipe/done/toxicivy_v1.manifest.json
?? infrastructure/artpipe/done/toxipotato_v1.json
?? infrastructure/artpipe/done/toxipotato_v1.manifest.json
?? infrastructure/artpipe/done/tropicalchokevine_v1.json
?? infrastructure/artpipe/done/tropicalchokevine_v1.manifest.json
?? infrastructure/artpipe/done/tumorbulbhyacinth_v1.json
?? infrastructure/artpipe/done/tumorbulbhyacinth_v1.manifest.json
?? infrastructure/artpipe/done/twisteddandelion_v1.json
?? infrastructure/artpipe/done/twisteddandelion_v1.manifest.json
?? infrastructure/artpipe/done/twistingthorngrass_v1.json
?? infrastructure/artpipe/done/twistingthorngrass_v1.manifest.json
?? infrastructure/artpipe/done/twistingthornwood_v1.json
?? infrastructure/artpipe/done/twistingthornwood_v1.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/violetwimple_v1.json
?? infrastructure/artpipe/done/violetwimple_v1.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_east.json
?? infrastructure/artpipe/done/wastewing_v1_east.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_north_r2.json
?? infrastructure/artpipe/done/wastewing_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/wastewing_v1_south_r2.json
?? infrastructure/artpipe/done/wastewing_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/weepingtoxberry_v1.json
?? infrastructure/artpipe/done/weepingtoxberry_v1.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wildradagast_v1.json
?? infrastructure/artpipe/done/wildradagast_v1.manifest.json
?? infrastructure/artpipe/done/wildrashroot_v1.json
?? infrastructure/artpipe/done/wildrashroot_v1.manifest.json
?? infrastructure/artpipe/done/witchesoyster_v1.json
?? infrastructure/artpipe/done/witchesoyster_v1.manifest.json
?? infrastructure/artpipe/done/wrinklecap_v1.json
?? infrastructure/artpipe/done/wrinklecap_v1.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.manifest.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.manifest.json
?? infrastructure/artpipe/failed/nysyllin_v1.json
?? infrastructure/artpipe/failed/nysyllin_v1.manifest.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? infrastructure/state/items/PIT_TRAP_VISUAL_REDESIGN_1.md
```

