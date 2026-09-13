# FOUNDRY_REBOOT_HANDOFF_202609131746 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609130440`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A GL-emitted custom landform's `worldTileReq` keeps whatever the SHIPPED
source landform declares unless the caller explicitly overrides that field —
`gl_emit.py`'s `--from` path loosens `hilliness` unconditionally but only
loosens `topology` when `--topology` is passed. This is why Sinkhole sat at
1/8 success across two `MAPGEN_GL_SHEET_1` rounds (it inherited
`Topology=CliffAllSides`, essentially never rolled) while Canyon worked fine
(its native `CliffValley` apparently was hit). `--topology Any` fixed it,
2/2 first try. Generalizes to any future GL recipe built from a source
landform with a narrow native requirement on a field the emitter doesn't
loosen by default — read the shipped XML's `worldTileReq` before assuming a
recipe is "the same shape, just parameterized differently."

## What the owner should see

- `MAPGEN_GL_SHEET_1` is now fully ready for keep/cut:
  `Transient/mapgen_gl3/comparator_gl_vs_painter_v3.png`, all 8/8 landform
  categories live-proven. The generalized finding: GL's real terrain reads
  organic/branching/cave-riddled everywhere, the painter (even after two
  rounds) still reads comparatively geometric — bold rings for
  Sinkhole/Crater/LoneMountain, a fairly straight diagonal band for Canyon.
  This is the evidence `MAPGEN_PAINTER_V1_1`'s next round and
  `MAPGEN_CONVERGENCE_LOOP_1` were waiting on.
- `PLOT_MECHANISM_MODS_WAVE_1` rules 5/7/8 (Sh'kaar's escalation, The rooted
  receipt, The reckoning) are blocked on real design calls this session did
  not make up: which arrival modes count as "gentle" and how "most-wronged"
  is scored (rule 5); reading the third-party `mlie.rfrumorhasit` mod's
  actual API (rule 7); reading `tributedemand`'s dialog API (rule 8). Flagged
  twice before by prior passes; still nobody's decided them.
- `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1`'s Step 1 census is stale (checked-in
  `world/ASHKARR_WORLDMAP_mutators.csv`, committed 2026-08-23, disagrees with
  a later live V27 export cited in a 2026-09-08 review — 88/6710 tiles vs
  163/14290). Re-deriving it plus the owner's contact-sheet keep/cut (steps
  2-5) is worldmap-domain work this repo's own doctrine says is never a solo
  FOUNDRY sweep — needs a pass WITH him.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `MAPGEN_GL_SHEET_1` — mine, finished this window. All 8/8 landform
  categories live-proven, comparator sheet composed and pushed, `needs owner`
  set. Not closing it myself — closure is the owner's keep/cut per its own
  `PROVE` line, not FOUNDRY's to award.
- `MODLIST_RULED_CUTS_1` — not touched this window; carried from an earlier
  pass. Deploy done and verified in sync; owed a fresh-Player.log confirmation
  (three cut packageIds absent, zero new Config errors) on the next full-list
  restart — which just happened (this window's `MAPGEN_GL_SHEET_1` GL-testing
  restarts do NOT count, they ran on the minimal `ModsConfig.VANILLA_BRIDGE_GL`
  list, not the full list). Next action: grep the Player.log from the full
  reload this window triggered (in progress at handoff time, see Game/bridge
  state below) for the three deactivated packageIds and 0 new Config errors.
- `CATHEDRAL_REGARD_BLACKBOARD_1`, `GM_BLACKBOARD_SHADOW_M4_1`,
  `FEVER_WOOD_MECHANICS_1`, `MIASMA_MECHANICS_1`, `SCALD_MECHANICS_1`,
  `SUMP_MECHANICS_1`, `LIQUID_TYPES_MOD_1` — none touched this window;
  carried from earlier passes, each with a clear self-written "left in doing"
  note already in its own item file (read the tail of each before touching):
  CATHEDRAL_REGARD_BLACKBOARD_1 and GM_BLACKBOARD_SHADOW_M4_1 both need a real
  live triggering event (kyber sale / real §2 inputs) this campaign hasn't
  produced yet, not more code; the four EnvironmentalHazards kit spikes
  (FEVER_WOOD/MIASMA/SCALD/SUMP) are explicitly partial builds awaiting their
  full-kit FOUNDRY pass, not blocked on anything; LIQUID_TYPES_MOD_1's defs
  are authored and validated but owed live/bridge verification, explicitly
  deferred by its own spike verdict.

## Traps learned

- `python.exe` misreads a WSL absolute path handed as a script argument
  (`can't open file 'D:\\mnt\\d\\...'`) — always `cd` into the repo first and
  pass a relative path. Bit me twice this session on the same mistake.
- A GL custom landform swapped into `Config\CustomLandforms-v1\` while the
  game keeps running is NOT picked up by `go_to_main_menu` +
  `start_debug_game_ready` alone — confirmed live, twice. A full process
  kill + Steam relaunch is required to see a swapped recipe file; a same-
  recipe tile re-roll (via go_to_main_menu) needs no restart. Filed as a new
  finding, not previously in `skills/rimbridge`.
- `rimworld/screenshot_cell_rect` needs `set_camera_zoom_extension(true)`
  called first even when a prior session in the SAME Player.log already used
  it — the setting does not persist across a process restart (obviously, but
  easy to forget when copy-pasting a working call from a prior round's log).
  A 200x200 crop at rootSize 100 also needed edge padding (`requiredRootSize`
  104 > 100 cap) that round 2's own identical-looking call didn't hit —
  narrowed to a slightly-off-map-center landform position, not a regression;
  shrinking the crop to 192x192 cleared it.
- Also, mid-session the owner flagged my glob `rm -f <dir>/*` cleanup calls
  as a dangerous formulation — switched to explicit-filename `rm` for the
  rest of the session. Worth keeping as a standing habit, not just a one-off
  correction.

## Closed since the last handoff (4)

- `GRAVSHIP_MAP_SIZE_1` — f81afa5f3c0032f715504d90b642c01305f3cabe
- `HUB_URL_POINTER_FIX_1` — 9f4c06b9acccae35e707139cf1c2ee93815bc469
- `INHABITED_STOCK_ONTO_MAP_AND_FATE_1` — 28c223fea211b4bfbfd470a06d49aea7be7a5cdb
- `RM_GENSTEP_PLACED_SETPIECES_1` — b47fe61a0

## Filed and still open (15) — the next seat's queue

- `MODLIST_RULED_CUTS_1` — Execute the 2026-09-12 bench modlist rulings: cut profiler + blood animations + slower pawn tickrate; Jurassic retirement lands after texPath check; M
- `CATHEDRAL_REGARD_BLACKBOARD_1` — Cathedral Regard counter + stage machine + exposure pressure on the GM blackboard, shadow-mode first
- `CATHEDRAL_STAGE_HUM_BRIDGE_1` — Stage-to-hum-baseline bridge lane into RM_BiomeAttitudeDef (C#, row-3)
- `CATHEDRAL_STAGE_COMMENTARY_POOLS_1` — Stage-keyed RUT_HumCommentary pools + the bans-2/6 linter gate every arc item runs
- `CATHEDRAL_MISSION_BOON_OFFERS_1` — Deniably-sourced Assailant missions + Heat-gated gravtech boons
- `CATHEDRAL_SURVEY_MISDIRECTION_QUEST_1` — The A4 Imperial-survey misdirection quest, three branches, K2 anti-laundering
- `CATHEDRAL_MECHANOID_PASS_VERBS_1` — GRANT/REVOKE mechanoid-pass instrument, scoped Harmony hostility exception (C#, row-3)
- `CATHEDRAL_DESCENT_REVEAL_SITE_1` — The A7 real under-plate descent site + reveal beat + A1 Utinni-receiver lore propagation
- `CATHEDRAL_EXPOSURE_COMPLETION_1` — The A6 pyrrhic discovery ending: witnessed fall, warzone flip, priced Hutt extraction, ship mourns
- `GM_BLACKBOARD_SHADOW_M4_1` — Build M4: Imperial Heat + orbital-detection timer + dark-tile pause as a Python shadow-mode state machine
- `ARTPIPE_FAILED_REQUEUE_1` — ARTPIPE_FAILED_REQUEUE_1 clear the 46-job failed/ pile: drop 27 gemini-banned, requeue 16 codex transients, fix 3-job canvas-size bug
- `DOING_SEDIMENT_RECLAIM_1` — DOING_SEDIMENT_RECLAIM_1 reclaim 21 zombie doing items to ready (dead-session starts, last touch 2026-09-06..10)
- `BRIDGE_STATIC_SETTINGS_FIELDS_1` — BRIDGE_STATIC_SETTINGS_FIELDS_1 update_mod_settings cannot flip public-static settings fields — measured on Pits, blocks toggle-flip components in 6+ 
- `MODCHECK_SUITE_CORRECTIONS_1` — MODCHECK_SUITE_CORRECTIONS_1 first-live-run corrections for the 12 RED + 2 aborted mature-mod suites (evidence: Transient/modcheck sheets + summaries 
- `MODCHECK_DONOR_ENVIRONMENTS_1` — MODCHECK_DONOR_ENVIRONMENTS_1 Armoury and WreckedMachines modcheck environments: compose their donor mods (ModularWeapons2+KotOR sounds; VFEFactory ch

## Commits

```
cf728d1d7 MAPGEN_GL_SHEET_1: compose the full 8/8 GL-vs-painter comparator sheet
2d5fc37a1 MAPGEN_GL_SHEET_1: root-cause and fix Sinkhole's 1/8 GL application rate
ab9f86eb2 PLOT_MECHANISM_MODS_WAVE_1: catch up item file on rule-4 wiring (commits 39da0b74f, 92b9cb7b3)
28c223fea INHABITED_STOCK_ONTO_MAP_AND_FATE_1: live-prove the fate cause/consequence
6fbec5895 BENCH handoff 202609131130: modcheck wave done, queue exhausted
0b68412b6 rimflow sync: game up (full list restored), bridge released after modcheck wave
b47fe61a0 File RM_GENSTEP_PLACED_SETPIECES_1: the shared def-list set-piece scatterer
65cb8448b rimflow: claim+start RM_GENSTEP_PLACED_SETPIECES_1
0ebd2b65a File RM_GENSTEP_PLACED_SETPIECES_1: the missing shared scatterer
f19caaaa6 lesson: python.exe's python3 is a Windows python3 — split modcheck halves by platform
b8fc3e00e SUMP_MECHANICS_1: spike pass — resolve 3 ❓ claims, build S2/S6b lottery + S1 igniter
c553d4c49 rimflow sync: close MODCHECK_MATURE_WAVE_1
db3ccced0 MODCHECK_MATURE_WAVE_1: first live wave, 16 suites run — 2 GREEN, 12 RED, 2 aborted
2ea364221 rimflow sync: 21 zombie doing items reclaimed to ready (owner-said), MACRO needs-owner
d775cd5b4 rimflow: claim+start SUMP_MECHANICS_1
15093c3e1 MODLIST_RULED_CUTS_1: note the mid-session modlist drift and restore
6cb3d9fe8 Restore live modlist to FULL + reapply MODLIST_RULED_CUTS_1's 4 cuts
d3240830a SCALD_MECHANICS_1: spike pass — resolve 5 ❓ claims, fix a live Ban 1 violation
5f0df1d7b modcheck retrofit: validation.py for Droidworks (17 toggles, 12 chains), PawnFlavor
53ca571c0 modcheck retrofit: validation.py for Armoury (24 toggles, 3 tiers), JawaIonWeapons, StarWarsRaces
a471fa94e modcheck retrofit: validation.py for FluidCanals, Graffiti, StructureInjections; BRIDGE_STATIC_SETTINGS_FIELDS_1 filed
346253a90 rimflow: claim+start SCALD_MECHANICS_1
76c1085d6 Fix stale 'unruled' owner-card headers across 4 mechanics kit specs
a51efa0c0 modcheck retrofit: validation.py for Pyrelands (FireEcology system), ResearchRetag, ShipMemory
e9f405be0 modcheck retrofit: validation.py for Aftermath, Antiquities, WreckedMachines
f341215ac modcheck retrofit: validation.py for Inhabited, Ninefold (M0), RimProperty
1b55bb6c2 rimflow: claim+start FEVER_WOOD_MECHANICS_1
769eaf180 FEVER_WOOD_MECHANICS_1: wire F2/F3 (from prior pass) plus F1/F5 into real Defs
64824b061 modcheck: compose MINIMAL + mods-under-test into the live list; deploy before composing
6a617e183 BENCH handoff 202609131000 + ledger-projection lesson
a4d7ef93f rimflow sync: close DOING_ITEMS_RECONCILE_1
d07d585cd Doing-items audit: 61 real (not 102), 21 zombies filed for FOUNDRY reclaim
861c2b284 rimflow: block TECHPRINT_FACTION_GATING_1
adba3ee9c CATHEDRAL_REGARD_BLACKBOARD_1: Regard/stage/exposure, shadow mode
82a728250 rimflow sync: doing-audit pass 1 — sittings set needs-owner, dependency holds noted, TECHPRINT_FACTION_GATING_1 reassigned to FOUNDRY ready
2cd449c40 rimflow: file+start DOING_ITEMS_RECONCILE_1 (102-item doing sediment audit)
6dcbc3981 ARTPIPE_FAILED_REQUEUE_1 filed: 46 failed jobs triaged (27 gemini-banned, 16 codex transients, 3 size-bug)
9d100d37c Transient: commit ~9 days of untracked evidence files (logs, probes, backups)
79d452398 code review: mark regen_hub.py + selftest CLEAN (full-file review, no findings)
32637c842 rimflow: claim+start CATHEDRAL_REGARD_BLACKBOARD_1
47fa9dac2 GM_BLACKBOARD_SHADOW_M4_1: fix seat mislabel in section header
bdc930b32 GM_BLACKBOARD_SHADOW_M4_1: the external blackboard, shadow mode only
6de920900 rimflow: claim+start GM_BLACKBOARD_SHADOW_M4_1
521ee823a File GM_BLACKBOARD_SHADOW_M4_1: the missing M4 prerequisite
6e5cb6355 Add regen_hub.py: single-script, no-LLM hub regeneration + publish validation
1fbdcb75e rimflow: close HUB_URL_POINTER_FIX_1
9f4c06b9a HUB_URL_POINTER_FIX_1: repoint HUB_TAB_PUBLISHER_MIGRATION_1 to the rebuilt hub
730145633 FEVER_WOOD_MECHANICS_1: spike pass — engine ground-truth + 6 compiling proofs
cfd5929fe rimflow sync: CATHEDRAL_ARC_OPEN_CARDS_1 ruled+closed; HUB_URL_POINTER_FIX_1 filed for FOUNDRY
3f6f98cd2 Cathedral cards ruled + hub rebuilt at new artifact URL
f081c3f13 MIASMA_MECHANICS_1: spike pass — engine ground-truth + 4 compiling proofs
eaf0e96e4 LIQUID_TYPES_MOD_1: author the full liquid roster (14 rows)
7f6a86c2a VQE_ANCIENTS_CURATION_1: step 4 string relabel pass (Forsaken exonym)
a6ebcb7a2 code review: mark MoEventsChancesZeroed_RuledCut.xml CLEAN
4319dca4c rimflow: close GRAVSHIP_MAP_SIZE_1
f81afa5f3 GRAVSHIP_MAP_SIZE_1: apply and live-verify the 325x325 landing size ruling
649f53406 MODLIST_RULED_CUTS_1: execute the owner's ruled mod cuts
b4a65f3f5 DROIDWORKS_PRIMITIVE_TIER_1: live-verify G2 body, flag missing head art
86b2b4694 DROIDWORKS_PRIMITIVE_TIER_1: deliver the live G2 savegame
eeb343c2f COLONY_VISIBILITY_BUILD_1: live-prove the threat-point Prefix
f2f99c7b2 BENCH reboot handoff 202609130700: sitting wrap, queue exhausted for BENCH
7995fcc13 rimflow sync: cathedral arc closed, build items filed, dungeon drafts noted
fdca83980 Dungeon set-piece prose: candidate drafts for the owner's strike pass (Fable)
060301d43 Cathedral arc: 8-item build decomposition filed (Fable), open-cards item, arc item card text updated to ruled state
62969c71f RIVER_STEAM_ANIMATION_1: confirm real live Pyrelands+river, hit new bridge render-void trap
3ae01c39a rimflow sync: bench sitting 2026-09-12 events (rulings, closes, new items)
eafb95ab0 Bench sitting 2026-09-12 rulings as data: protected_mods.json + cut-execution, deferred-cards and map-size item specs
18daf67a6 Giddy-Up + modlist complexity analyses (Fable agents); owner ruled at the bench 2026-09-12
b52b31054 Cathedral arc: A6 (pyrrhic discovery ending) + A7 (real descent site) ruled at the bench, spec amended in place
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-13T17:42:36Z
- **Confirmed healthy at handoff time (re-checked after the auto-probe above):**
  full-list cold reload (this window's own restore after `MAPGEN_GL_SHEET_1`'s
  minimal+GL testing) came up clean — `rimbridge/ping` answers, 320 companion
  tools registered, 0 companion warnings/errors, `ModsConfig.xml` on disk
  matches the full-list backup byte-for-byte. No `MAPGEN_GL_SHEET_1`-caused
  regression. Not yet checked: `MODLIST_RULED_CUTS_1`'s own verify (grep this
  fresh Player.log for its 3 deactivated packageIds + 0 new Config errors) —
  see that item's line above.

Uncommitted (say for each whether it is yours or another seat's):
**None of the following is mine.** My own work this window is fully committed
and pushed (see Commits below); the only things I left untracked on purpose
are `Transient/mapgen_gl3/shots/` (a reconstructible working directory, see
that dir's README) and nothing else. Everything below — `codebase_health.*`,
`infrastructure/artpipe/*` (hundreds of art-daemon job files — the artpipe
daemon is a live background process, not a stale mess), `defs.sqlite`,
`design/Jawa/worldbuilding/review/*.log` — belongs to other windows/daemons
mid-edit. Do not touch it; do not `git add -A` over it.

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
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
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
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
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/dervish_v1.json
?? infrastructure/artpipe/done/dervish_v1.manifest.json
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
?? infrastructure/artpipe/failed/ashrunner_v1_east.json
?? infrastructure/artpipe/failed/ashrunner_v1_east.manifest.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.json
?? infrastructure/artpipe/failed/ashrunner_v1_south.manifest.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.json
?? infrastructure/artpipe/failed/bilespawn_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.json
?? infrastructure/artpipe/failed/mireflitwarden_v1_north.manifest.json
?? infrastructure/artpipe/failed/nysyllin_v1.json
?? infrastructure/artpipe/failed/nysyllin_v1.manifest.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.json
?? infrastructure/artpipe/failed/twistingthornweed_v1.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

