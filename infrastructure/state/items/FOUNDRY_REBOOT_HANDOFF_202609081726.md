# FOUNDRY_REBOOT_HANDOFF_202609081726 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609081453`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**A subagent's `validate_patch.py`/`dotnet build` clean pass is not evidence anything
was deployed — check it hit the live Mods folder before trusting a "fixed" claim.**
This cost two live-verification passes this wave: `ARMOURY_PATCH_INNER_MISS_1`'s fix
was correctly committed and pushed, but `deploy_custom_mods.py --mod Armoury` had
never actually been run — the first full-list cold load still showed all 8 original
patch failures. `WORLD_LINT_WATER_HARDCODE_1`'s companion-DLL fix had the same shape
(built, not deployed, by the agent that wrote it — correctly deferred per its own
brief, but the NEXT session still has to remember to actually run the deploy before
re-testing). The pattern: an agent told "don't touch the bridge/game" during a build
pass sometimes over-generalizes that into "don't deploy either" — deploying static
XML/def output needs no running game and no bridge, only the C#-assembly half does.
Always run `deploy_custom_mods.py --mod <X>` (plan-only first) before trusting a
live re-test of anything a prior pass "fixed."

## What the owner should see

- **No Droidworks droid can wear ANY apparel today, and the reason is a vanilla
  engine gate, not a missing tag.** `PawnApparelGenerator.GenerateStartingApparelFor`
  returns immediately for `!IsFlesh` pawns, and every Droidworks race is
  `isOrganic:false` by an earlier deliberate ruling — so `apparelMoney` (this wave's
  own fix) is never even read. Fixing it needs a Harmony patch
  (`DROIDWORKS_APPAREL_ISFLESH_GATE_1`, filed, not built). Worth his eye because it's
  a real design tension: the "no organic body" ruling and "droids visibly wear armor
  modules" (the whole point of B2's absorption work) are in direct conflict until
  that patch lands — not a bug so much as two rulings nobody reconciled yet.
- **`DROIDWORKS_FORMAT_TIERS_1`'s need-gating by tier does not work live at all** —
  identical Mood/Power needs at every severity from blank through sapient, despite a
  vanilla-XML-only implementation that reads correct on paper. Not root-caused this
  wave (see item file for the repro and three candidate causes). This is B1, early
  in the droid critical path — worth flagging since several later packets assume it
  works.
- **`start_debug_game_ready` crashed the game outright on the owner's full 599-mod
  list** (mid-worldgen hang → process gone, no error dialog) — confirmed once this
  wave, recovered by swapping to the minimal list. Not yet added to any skill's
  traps file (skills are fresh-context-curation-only edits per `CLAUDE.md`). If this
  recurs it is not new — it's this same failure mode.
- **181 land-biome tiles sit at the three seas' own elevation (−350)** on the real
  V23 world, unmasked now that `WORLD_LINT_WATER_HARDCODE_1` stopped conflating them
  with the seas' own tiles (`WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1`, filed,
  unstarted). Possibly a real geography defect from whichever pass placed the seas;
  possibly harmless. Nobody has looked yet.

## What is half-done, and where it stops

Nothing is mid-flight unaccounted-for — every `doing` item is `BLOCKED` with a
reason naming the exact next action:

- `DROIDWORKS_FORMAT_TIERS_1` — need-gating fails live, not root-caused. Next
  action: read the shipped `HediffDefs_Droidworks.xml` stage-by-stage
  `<disablesNeeds>` against what `HediffSet.DisablesNeed` actually checks before
  assuming wiring vs. mechanism is at fault; also consider whether `Mood` on a
  `Humanlike`-intelligence race (Droidworks races keep this deliberately) has a
  code path that bypasses `disablesNeeds` entirely.
- `DROIDWORKS_MODULE_ABSORB_1` — apparel absorption itself is done and validated;
  blocked purely on `DROIDWORKS_APPAREL_ISFLESH_GATE_1` (below).
- `DROIDWORKS_APPARELMONEY_MISSING_1` — apparelMoney added and live-verified for
  the bare-skin half; blocked on the same isFlesh gate for the gear half.
- `DROIDWORKS_APPAREL_ISFLESH_GATE_1` — filed, not started. Needs a Harmony patch
  on `PawnApparelGenerator.GenerateStartingApparelFor` (or the specific method
  that gates on `IsFlesh`) analogous to the existing `Patch_ShouldHaveNeed_Power`
  pattern already in this codebase. Full writeup and the fix shape are in the
  item file.
- `WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1` — filed, not started. Verify plan is
  in the item file (check whether the 181 tiles cluster at sea edges before
  assuming a fix is needed at all).

The Droidworks C# assembly currently deployed to the live Mods folder matches
`e55a9854` (apparelMoney). `Armoury`'s deployed copy matches its own latest
commit as of this wave (verified via the cold-load re-test). Neither the
`DROIDWORKS_APPAREL_ISFLESH_GATE_1` Harmony patch nor the `FORMAT_TIERS`
need-gating fix exist yet, so there is nothing further to deploy for those.

## Traps learned

- **A subagent's own `commit + push` claim is not proof of `deploy`.** See "the one
  thing to carry forward" above — this is the single costliest lesson of the wave,
  repeated twice.
- **`rimworld/start_debug_game_ready` on the owner's full ~599-mod list is not
  calibrated and can crash the game outright**, not just hang — measured this wave
  (mid-worldgen, `Player.log` stopped growing for 5+ minutes, then
  `Get-Process RimWorldWin64` found nothing). Always swap to the minimal list
  (`modlist_swap.py --minimal --apply`) before any `start_debug_game_ready` call;
  the full list is fine for an ordinary boot-to-main-menu or a real save load, just
  not for quicktest worldgen.
- **This session's own background-task infrastructure killed two long-running
  bridge/game-wait `Bash run_in_background` calls for "low memory"**, even though
  WSL-side `free -h` showed 32GB+ available the whole time — the pressure being
  measured is evidently host-wide, not WSL-local. The `Monitor` tool (an
  until-loop polling a log file / process check) did NOT get killed the same way
  and is the safer pattern for "wait for RimWorld's bridge to come up" — use it,
  not a bare `run_in_background` bash wait, for anything that outlasts a couple of
  minutes.
- **Repeated, contradictory cross-session "Game is down/loading/up" messages
  arrived all wave**, sometimes in bursts that didn't match measured reality at
  all. Best working theory, not confirmed: a spawned subagent's own `./game --said`
  calls (run inside its own process context, per its briefing) get relayed back to
  this window via `broadcast.py` as if from a peer, because the subagent doesn't
  count as "this window" the way a same-process call would. Never replied to any
  of them (cross-agent messaging is off, hard rule) — always re-measured with
  `./game` / `Get-Process` instead of trusting the announcement. Worth a real
  investigation sometime, not urgent.
- **`jawa/pawn_get`'s single-pawn detail view has no `downed`/`dead` field** — only
  the bulk `jawa/list_pawns` listing rows carry it. A `Downed` precondition check
  against the detail view silently reads as `None`, not `false`.
- **`jawa/pawn_get`'s `needs` list keys each entry `"need"`, not `"def"`** — the
  same field-name mismatch that has bitten this project before elsewhere. Cost one
  wasted verification pass on `DROIDWORKS_FORMAT_TIERS_1` before the mistake was
  caught and redone.
- Filed to `LESSONS_INBOX.md` as one line each (the deploy-gap one and the
  full-list-crash one — the other three are more session-mechanics than
  reusable modding lessons).

## Closed since the last handoff (6)

- `KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1` — cbd371cc83309b73533d4508887a236db3600de8
- `DROIDWORKS_LIVE_LOOP_PROOF_1` — cbc0a8718f1bb7131548580bbd9c0df15751cea2
- `ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1` — 7c5f48b27fc693b788f7cbdc29e5e7e381234236
- `DROIDWORKS_DETONATION_REVIEW_1` — 72c58ea2af55495c905149dabb9c98dba40599b3
- `WORLD_LINT_WATER_HARDCODE_1` — 7df58354394685e0190163d6e813fff10237accc
- `ARMOURY_PATCH_INNER_MISS_1` — 7df58354394685e0190163d6e813fff10237accc

## Filed and still open (10) — the next seat's queue

- `BRIDGETOOLS_DLL_GM_DRIFT_1` — JawaBench DLL is 41 tools behind source (built without GM pair); selftest_tool_metadata FAILs until companion rebuild+redeploy on a game-down window
- `UTINNI_SHELL_DEFNAME_BUG_1` — UtinniShell emits Config error every full-list load: defName 'Utinni Shellmandrake.rut.shell' — name and packageId concatenated somewhere in its def a
- `STARWARSRACES_TOOLBOX_SOFT_DEP_1` — StarWarsRaces DefModExt_HeadTypeStuff depends on neronix17.toolbox with no MayRequire — every HeadTypeDef silently vanishes if Tabula Rasa goes inacti
- `RAIDREDESIGNER_HARD_PROPERTY_REF_1` — RaidRedesigner DLL hard-references RimMandrakeProperty (PropertyEngine.Fire) but About.xml declares only soft loadAfter — declare the hard dep or guar
- `ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1` — AshkarrFlora RUT_SweetlineTree texture folder is empty; 11 candidate PNGs sit unmoved in _artsrc — wire or cut (walk-authoring find)
- `LANTERNDEEPS_GENSTEP_ALLOWLIST_DEAD_1` — LanternDeeps GenStep biome allowlist names biomes from mods its About.xml never declares — on most lists the scatter step silently never fires (walk-a
- `DROIDWORKS_APPARELMONEY_MISSING_1` — gen_droidworks_defs.py never emits apparelMoney on any of the 80 PawnKindDefs -- no Droidworks kind can ever generate apparel regardless of apparelTag
- `KOTOR_CRYSTAL_GENSTEP_DRIFT_1` — Deployed KOTOR_CrystalFormation genstep scatters only Stygium; repo's absorbed copy lists 12 crystal variants — diff repo vs deployed, redeploy or pul
- `WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1` — 181 land-biome tiles (AridShrubland/Desert/Wasteland/AB_RockyCrags/AB_MycoticJungle/ZBiome_Badlands) sit at the three seas' own elevation (-350), unma
- `DROIDWORKS_APPAREL_ISFLESH_GATE_1` — Harmony patch: PawnApparelGenerator skips apparel generation entirely for isFlesh=false Droidworks pawns

## Commits

```
e55a9854 Droidworks: add apparelMoney to every generated PawnKindDef
7df58354 Full-list cold load verification: close WORLD_LINT_WATER_HARDCODE_1 and ARMOURY_PATCH_INNER_MISS_1 for real
017d2c52 BENCH reboot handoff 202609081635: AFK wave complete — 8 closed, 9 parked on owner review
8d64f329 Crystal mods inventory: orange crystal = KOTOR_SmallCrystal_orange (ours via Armoury); 6 systems catalogued
c13d35c0 biome_flora.py: supersede HorrorWastes + BMT_CrystalCaverns entries (BIOME_FLORA_ROSTER_GAP_1)
4de53d06 from-water metric calibrated + deep_desert far-ring table refreshed; ancient-ruins audit landed
2a76e9e0 Staged lore descriptions: FEASIBLE verdict, def-field mutation route, one cache trap named
a5cae96c Alpha family source review: no license = no code reuse; 6 mechanics to reimplement
46cafe02 Memory-audit synthesis digest + mutation modifiers survey
2175f938 Ledger sync: gizka + brainworm specs claimed/parked on owner; sub-measure notes
acfdbd05 Brain worm design spec: Space Worms donor read + canon cited, def plan for owner review
804a817c Gizka ship-pest design spec: Tribble module examined, donor art absence MEASURED
a9d5d251 Live-verify B1/B2 on the redeployed build: B1's need-gating fails live, B2 root-caused to a platform-wide apparelMoney gap
4ae1ac59 Sub-measure refresh: hilliness/rain-zero/per-region stats in the instrument; 5 sheets' flagged fractions fixed
fbd74868 rimflow: claim/start/block DROIDWORKS_MODULE_ABSORB_1
c6b9b7d9 DROIDWORKS_MODULE_ABSORB_1: absorb KotOR droid module apparel (hardware/software/sensor + armor)
2f60c5dc Close DROIDWORKS_DETONATION_REVIEW_1 (ledger sync)
72c58ea2 Ledger sync: sitting closes (ring, water, walks) + 4 walk-finding items filed
cb7c9057 Validation walks for all 77 systems + four owner rulings (2026-09-08 sitting)
7c5f48b2 ARMOURY_CROSSFILE_ADD_REPLACE_ORDER_1: close as resolved by 1974a7c6
e3333bed Sync ledger: DROIDWORKS_FORMAT_TIERS_1 claimed, started, blocked on live quicktest
b81a023b Droidworks B1: format tiers (blank/mindless/programmable/sapient)
b380f413 Water taxonomy as data: 19 kinds, 3 not-water, transmutations pending owner ruling (WATER_KINDS_TAXONOMY_1)
b8b65eb4 Golden stat-refresh: 18 biome sheets re-measured against the V23 world
1974a7c6 Fix ARMOURY_PATCH_INNER_MISS_1: 3 FindMod inner-match failures, 2 root causes
6180f961 Rakatan engineered-legacy index: 5 ruled + 1 open (the Webwork question)
71753752 Lanes doctrine paragraph in the biome grammar README (LANES_DOCTRINE_PARAGRAPH_1)
80e38de9 Dashboard pass 3 (review-agent findings): stale loses the reserved yellow, DATA.weighting rendered, needs-owner tile, GOAL_SHEET per-box tooltips, updated-by in hover card, unknown-review tile when nonzero
a7c1dc2c biome_sheet_stats.py: V23 per-biome stats via CSV + 8 overlay plans
e4e32de0 Dashboard pass 2: ladders read most-mature-first, matching the matrix
cbc0a871 DROIDWORKS_LIVE_LOOP_PROOF_1: live-prove the five-state loop on GNK + KotOR kind
03c9db14 LESSON: drvfs stale reads mimic a hard revert; peer reset --hard in reflog
c8c206a9 Maturity dashboard v2: dense rework + 28 evidence-based rung promotions
cbd371cc Resolve KOTORCORE_ADAPTIVESTORAGE_PARENTNAME_1: false alarm, no fix needed
807ce1c9 Fold Spikes into their mods; add rimflow 'capability retire' (owner ruling)
f56dc9d4 world_lint: fix landBiomeSubmerged hard-coded water biome check
77dccf02 Maturity grid: real mod names, tier colors, hover cards, progress chips
c672bfda Maturity dashboard: restore the 70s brown palette from the seed-proposal page
6b8739da Ledger sync: close PROJECT_MATURITY_DASHBOARD_1 at 78fe3b38
78fe3b38 Seed maturity capability registry: 78 systems from the folder survey
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-08T17:14:28Z

Uncommitted (say for each whether it is yours or another seat's):

**NOT mine** — `codebase_health_last.json`, `IKEE_MYNOCK_ART_REGEN_1.md`,
`BeastLairs/About.xml`, `BeastLairs/Defs/.../RSW_BeastLairs_Buildings.xml` were
already uncommitted at the very start of this window's session (present in the
first `git status` this seat ever ran, before touching anything) — someone else's
in-progress art-regen work (`IKEE_MYNOCK_ART_REGEN_1`, last touched by commit
`0d199cbd`, not this wave). Left untouched on purpose; not evaluated for content.
`ledger/events.jsonl`/`queue/BENCH.md`/`queue/FOUNDRY.md` showing modified here is
routine — `handoff.py` itself just wrote to them.

```
M infrastructure/state/codebase_health_last.json
 M infrastructure/state/items/IKEE_MYNOCK_ART_REGEN_1.md
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? claude_sha.txt
?? design/Jawa/art/gods/busts/.gitignore
?? "design/Jawa/worldbuilding/lua suggestions/"
?? design/Jawa/worldbuilding/review/creature_art/
?? design/Jawa/worldbuilding/review/creature_register.fiftyone_export.json
?? design/Jawa/worldbuilding/review/deck/creature_deck.pptx
?? design/Jawa/worldbuilding/review/deck/creature_deck_manifest.json
?? design/Jawa/worldbuilding/review/furniture_art/
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260902_181509.xml
?? infrastructure/state/codebase_health_last.json.lock
?? infrastructure/state/facts/mlie_creature_defname_map_wave_a.json
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260907_215737.xml
?? research/RimMandrake/inspiration/map_injection_2026-09-06/p2_createprefab_export.xml
?? src/RimMandrake/LoadTracer/Assemblies/
?? world/_lightfall_read.py
?? world/_load16.py
?? world/_poll16.py
?? world/_ready_ring.py
?? world/_roads/meander_v12/_tools_world.json
?? world/_roads/meander_v12/ancient_edges.json
?? world/_roads/meander_v12/harvest.py
?? world/_roads/meander_v12/landmarks_before.json
?? world/_roads/meander_v12/objects_before.json
?? world/_roads/meander_v12/probe.py
?? world/_roads/meander_v12/probe2.py
?? world/_roads/meander_v12/rerouted_v12.json
?? world/_roads/meander_v12/roads_import.csv
?? world/_roads/meander_v12/world_info.json
?? world/_settle_shot.py
?? world/_shot_globe.py
?? world/_shot_lightfall.py
?? world/graycrags_to_crags_plan.json
```

