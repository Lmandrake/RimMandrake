# FOUNDRY_REBOOT_HANDOFF_202609090029 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609081726`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

The B1/B2 apparel chain resolved end-to-end this wave: `DROIDWORKS_APPAREL_ISFLESH_GATE_1`
(Harmony transpiler, one call site, `IsFlesh || fleshType==RSW_DW_FleshType_Droid`) plus
`DROIDWORKS_APPARELMONEY_MISSING_1`'s KM1HMD budget fix together took Droidworks kinds from
0/15 dressed to 70-100% across every tested family, which then let `DROIDWORKS_MODULE_ABSORB_1`
(B2) close on existing evidence with no fresh bridge session. **When a blocker's root cause is
"upstream" of the item in front of you, fix the upstream item first — closing three deep-chained
blockers in sequence this wave cost far less than three separate live-verify passes would have.**

## What the owner should see

- **`DROID_RETIRE_KOTORDROIDS_1` (D2) is genuinely NOT safe yet, and reverted.** A confirming
  cold load found `guy762.mm.kotorcore`'s `_DroidsBase` folder — itself `IfModActive`-gated to
  kotordroids — supplies 4 ammoDefs (`guy762_DroidWeapon_{microrocket,railgun,seekerrocket,trishot}`)
  that our OWN `src/RimStarWars/Armoury` weapon-part absorption consumes ungated. This is a
  two-hop donor dependency neither the original D1 census nor B2's module absorption walked.
  Full trace + two candidate fixes are in `DROID_RETIRE_KOTORDROIDS_1`'s item file — needs a
  human or a fresh FOUNDRY pass to pick a fix, not a re-run of the same cold load.
- **`DROIDWORKS_WIP_SWEPT_NOTICE_1`** (filed by BENCH, not me): my E3 subagent's uncommitted
  ModulePersonality work (hediffs+comp+csproj+DLL) got swept into BENCH's own commit `0f7da95c`
  by what looks like a broad directory `git add` on their end, not mine. Content was verified
  correct and is live on `main`, but the provenance is BENCH's commit message, not FOUNDRY's —
  flagging per this repo's own git-discipline rule, not alleging anything malicious.
- Bridge testing for `DROID_REPAIR_FOR_PROFIT_EVENTS_1`, `DROIDWORKS_WIPE_SEVERITY_1`,
  `DROID_HUTT_CAPTIVES_1` and `DROIDWORKS_MODULE_PERSONALITY_1` all still owe a live pass —
  none is a design question, all are routine "next window with the bridge free" work.

## What is half-done, and where it stops

- `DROIDWORKS_MODULE_PERSONALITY_1` — code-complete, built, offline-validated 0 errors. Left
  `doing`: bridge was held by D2's cold load and then the game was down for the rest of the
  window, so "wear spider-arm module -> trait; remove -> gone" was never live-tested. Next
  action: minimal 25-mod list, spawn a droid, debug-action `Wear apparel (selected)...` one of
  the 3 wired modules (`RSW_DW_Module_DroidHardware_agility`/`_DroidSensor_perception`/
  `_DroidSoftware_lockout`), `jawa/pawn_get` to confirm the hediff, unequip, confirm it's gone.
- `DROIDWORKS_WIPE_SEVERITY_1` — unchanged from before this window (owned by an earlier B10
  pass, not touched this wave). `Recipe_DWMemoryWipe.ApplyOnPawn` (record reset + quirk roll)
  has never been observed running live despite two dedicated attempts. Next action: force the
  wipe recipe onto a live pawn via `jawa/bill_add` + a doctor at proximity with work priority
  set (the two levers already tried), or accept the mechanism-level verification already on
  record (hediff/quirk-pool checked directly) as sufficient and close on that instead.
- `DROID_HUTT_CAPTIVES_1` — unchanged from before this window. Code-complete
  (`StockGenerator_DWHuttCaptives`, `Recipe_LiberateHuttCaptive`), never live-tested (bridge
  contention + mod not in the minimal test list last time it was tried). Next action: add the
  Hutt Cartel trader content to the minimal Droidworks-capable list, spawn a Hutt caravan, and
  check the captive-droid stock feature actually appears.
- `DROID_REPAIR_FOR_PROFIT_EVENTS_1` — code-complete, offline-clean, live-confirmed the quest
  offers with correct droid/payment data on two full-list cold loads, but "completes; pays" is
  unproven: `jawa/fire_quest` needs a map and quicktest map-gen crashed on the full list both
  times. Next action: run it on the MINIMAL Droidworks list per the run-sheet already written
  into the item file, not the full list.

## Traps learned

- **A subagent cannot receive an async background-task notification.** One of this wave's own
  FOUNDRY subagents (D2) started a cold load, said "I'll wait for the monitor's notification,"
  and then genuinely stopped forever — it has no channel to be woken by later. Only the PARENT
  session gets task-notifications. Any subagent doing a wait-for-external-state step must poll
  in a foreground loop (a bash `while` with sleeps) inside its own turn, never park itself
  waiting on a callback. Filed to LESSONS_INBOX.md.
- **A two-hop `IfModActive` donor dependency is invisible to a one-hop reference census.**
  `DROID_DONOR_REFGREP_1` (D1) checked every direct kotordroids reference in `src/` and active
  mods, correctly, but missed that a THIRD mod (`guy762.mm.kotorcore`) gates its own content on
  kotordroids and that our code depends on THAT mod's gated content. A retirement census needs
  to walk donor-of-donor chains, not just direct references to the mod being retired.
- **`jawa/list_pawns` has no apparel field** (again confirmed this wave, by two independent
  subagents) — only `jawa/pawn_get` carries it. A blind read via `list_pawns` reports a false
  `0/N` for every kind regardless of what's actually worn.
- **An `IncidentDef` cannot be both a random-pool entry (`rootSelectionWeight>0`) and a
  separately-fired quest root** — the engine's own `ConfigErrors()` forbids it outright. Two
  packets this wave (C5, E4) each had to pick exactly one firing route after hitting this live.

## Closed since the last handoff (16)

- `DROIDWORKS_HEADS_BRAINS_SPIKES_1` — c0e4e014eb25a4fc84c16be08f3abf4df28d30d6
- `DROIDWORKS_FINE_PARTS_1` — 2d9b14e39fa799fa530352b4cdc4e6e6981edcfd
- `DROIDWORKS_SHOP_BENCHES_1` — fbed41012fa07775b67dbd47d58efaa1727e98ce
- `DROIDWORKS_BOLT_PAYOFF_1` — 6556f22371134c50f92e9494a9cf1eb107d98c62
- `DROIDWORKS_ION_SHIELD_BODYSIZE_1` — b329e342c440ea11671b136ff473ff71fd1dc6d8
- `DROID_FDE_KINDS_REPOINT_1` — ac7c941ffbffb1239302d7fa7b5aa77178f50c6a
- `DROIDWORKS_FULL_LIST_COEXIST_1` — 3b970039e295b8627d2a6cb33e7b7f8586710ef6
- `BRIDGETOOLS_CSHARP_SWEEP_BUGS_1` — 27c90a5a65ec81aa7ab601dc6b4f650a9085b5ef
- `DROIDWORKS_RESEARCH_ROWS_1` — 42b3abd58cd526fff8f415b013b1b81369034238
- `DROID_FACTION_LOADOUTS_1` — 644080cb02c93290f8141d892914849fab2766ec
- `DROID_DISTRESS_CALL_REPOINT_1` — 44613332e16daba519df33d68cdf4175239b7947
- `DROID_PROTOCOL_TRADE_ADVANTAGE_1` — 005c0b8e8336fc8fa3b06bc50178726170fa2820
- `DROIDWORKS_APPAREL_ISFLESH_GATE_1` — 8c2749478b6aea3a44144011c9c9fed8db142f03
- `DROIDWORKS_WILD_DROIDS_1` — 92db2af5f1ed668a916af164cfa0b3c1b5a5efff
- `DROIDWORKS_APPARELMONEY_MISSING_1` — a7bbeaec4a279e14b59b28e75c7df1fb254572b5
- `DROIDWORKS_MODULE_ABSORB_1` — 29bc523540502ff55939ec75723d98657233421d

## Filed and still open (11) — the next seat's queue

- `DROID_SUICIDE_CHARGE_STATE_1` — Junker suicide droid: proactive charge-and-detonate MentalState, beyond the existing death-detonation
- `RIMPROPERTY_ANIMAL_THEFT_1` — RimProperty: trainable stealing for agile pets, wild-animal theft, droid loaders carry the hauler property (owner, 2026-09-08)
- `EGG_PROXIMITY_HATCH_TRIGGER_1` — Egg proximity-hatch trigger: eggs hatch AT you on approach (owner, 2026-09-08); BirthHatchDemo retirement gated on this
- `CHRONICLE_EVENT_SPINE_1` — RimChronicle event spine spec: one-page event taxonomy + soft-hook API before the sprint; Property/Pursuit/Ninefold/Aftermath-rules become producers-c
- `MOD_CONSOLIDATION_SPRINT_1` — Execute the consolidation map: 77 to 53 mods, one mechanical game-down window per MOD_CONSOLIDATION_PLAN.md section 4 (signed off 2026-09-08)
- `GRAFFITI_GENERIC_MARKS_1` — Author generic vanilla-style default marks for RM Graffiti (R7): the nine campaign styles move to Salvation, RM ships with examples
- `PYRELANDS_GENERIC_TEXT_1` — De-campaign Pyrelands text for the self-contained RM biome (R9); resolve the donor BiomeDef VERIFY (zylle.morevanillabiomes) with the absorption track
- `CHRONICLE_NINEFOLD_DECOUPLE_1` — Decouple Aftermath from Ninefold per CHRONICLE_EVENT_SPINE.md: subscription API, drop hard modDependency+csproj ref, godTie God enum to string (C#, mo
- `MANYWATERS_GENERIC_SPLIT_1` — ManyWaters is not generic yet: RiverSteamHook.cs hardcodes ZBiome_Grasslands — split the Ashkarr wiring out as a RUT patch/data hook (C#)
- `NAMESPACE_RETIER_PASS_1` — C# namespace re-tier pass: RiverSteamHook → RimMandrake.ManyWaters, RimMandrake.DesertVehicleReskin → RimMandrake.StarWars.* — namespace+XML Class att
- `DROIDWORKS_WIP_SWEPT_NOTICE_1` — NOTICE: your uncommitted ModulePersonality WIP (hediffs+comp+csproj+DLL) was swept into BENCH commit 0f7da95c by a directory add — verify its state be

## Commits

```
93d5bfdd Sync rimflow ledger
f25b6ce4 DROID_RETIRE_KOTORDROIDS_1: blocked — cold load found an unabsorbed donor chain
106e6459 Ledger: freeze item closed on the owner's sprint authorization
2050af8c Sprint repo-side COMPLETE: tombstone removed, freeze closed, selftests 45/45, state recorded on the item
b0e18f89 Sprint wave B: R4 re-prefix — 120 defs (21 RSW_, 99 RUT_) renamed with repo-wide references; property selftest repointed at RimProperty (20/20)
11edf682 DROIDWORKS_MODULE_PERSONALITY_1: spec, mechanism and offline verify recorded
0f7da95c Sprint wave B: Armoury extractions — SovSith genes/headtypes+13 textures → StarWarsRaces, droid namer rulepacks → Droidworks (VERIFY passed: pure RulePackDefs, no consumers)
f25e58b8 Sprint: JawaVoice + StrandedQuest VERIFY rows resolved clean (definitive reads)
8e779fb2 Sprint: game-down runbook with 15 live id swaps; ManyWaters split + namespace re-tier items filed
7ff9ef21 Sync rimflow ledger: close DROIDWORKS_MODULE_ABSORB_1
29bc5235 Re-verify DROIDWORKS_MODULE_ABSORB_1: KotOR kinds confirmed wearing real absorbed modules
32013962 Sprint global pass: 23 dying/re-tiered packageIds rewritten across 32 files; RSW_WS_/RSW_FE_ re-prefixed (R4); 4 assemblies rebuilt 0W/0E; lint baseline moved to the new roster (73→45, all sprint-attributable cleared); PlantNames_CanonSW rename (map row 103)
485380d4 Sprint wave A: WeatherSuite+Pyrelands promoted to RM whole; RiverSteam → ManyWaters; FactionSlate → UtinniPatches
b704076b Sync rimflow ledger: close DROIDWORKS_APPARELMONEY_MISSING_1
7e6eda0b Sprint wave A: 7 fix mods fold into per-tier Patches (deps carried into loadAfter); DesertVehicleReskin moves WHOLE to RSW — fold reversed, it ships C#
a7bbeaec KM1HMD apparelMoney: labour-family budget too low for its T3-tagged gear
247cd6d4 Sprint wave A: fauna → SWBestiary (5 mods, 93 files + art/C# followed); structures → StructureInjections SW/RUT; UtinniShell → MenuShell (RimThemes pattern kept top-level)
f32eef5f Sprint wave A: crime merge — Property+SalvageClaim+TheftHauler → RimProperty, builds clean (0W/0E), both verbs string-verified in DLL
dea06f60 Chronicle event spine spec delivered; 3 hard couplings found — decouple item filed, Chronicle rows stay gated
9dd2fdce Sprint claimed by BENCH on owner's word; src/ write-freeze notice filed for FOUNDRY
43ce8279 Ledger: audit item closed for real (prior close errored on a bad flag)
90334957 Close MOD_NAMING_CONSOLIDATION_AUDIT_1
647c1f51 Consolidation plan SIGNED OFF (plant/recipe sweep clean): sprint + 2 gate items filed with specs
5e1efcde Sync rimflow ledger: close DROIDWORKS_WILD_DROIDS_1
92db2af5 Wild crashed droids: factionless incident, capture, spike-to-recruit (E4)
7b07a7d8 MOD_CONSOLIDATION_PLAN v3: expansions adopted, judgment calls ratified — pending owner sign-off
ba1f167f Four expansions adopted (owner cards): Chronicle spine item filed; reskin tie-break + display-name amendments in naming plan
b5ac6b8d Sync rimflow ledger: close DROIDWORKS_APPAREL_ISFLESH_GATE_1
8c274947 Droids can wear apparel: transpile the IsFlesh half of PawnApparelGenerator's guard
92c130cb C5 item file: live findings, and the run-sheet for the half still owed
e310909b Consolidation map review: 15 owner rulings recorded; RIMPROPERTY_ANIMAL_THEFT_1 + EGG_PROXIMITY_HATCH_TRIGGER_1 filed with specs
3df346c6 C5: drop the paired IncidentDef — the engine forbids both firing routes
c15a58f0 Repair-for-profit droid quest, RUT tier (C5)
49e73af2 Rebuild Droidworks.dll against current HEAD (C4+C6 both included)
e7dcfbec Sync rimflow ledger
005c0b8e Protocol droids shift trade prices both ways (C4)
c84f16b2 Sync rimflow ledger: close DROID_DISTRESS_CALL_REPOINT_1
44613332 Repoint BTD Droid Distress Call quest's KotOR kinds to Droidworks kinds
63433d82 Sync rimflow ledger: DROID_HUTT_CAPTIVES_1 note
4f338439 Droidworks: Hutt captive droids -- purchase (Trade Cartel caravan) and rescue (liberate recipe), site composition scoped out
dd4b9ba2 Sync rimflow ledger (game-state stamps)
1d77ecef Sync rimflow ledger
539ebf35 C1 live-verified on a full 600-mod load: 0 discards, 0 dangling refs
644080cb Droids into six faction loadouts, no droid faction (C1)
4fdee742 MOD_CONSOLIDATION_PLAN draft + executable map (99 rows) — pending owner review
30167ee8 DROIDWORKS_RESEARCH_ROWS_1: seven Unbolting research rows, 37 recipe gates
7c6739aa JAWA_PATCHES_SPLIT_1: correct stale-premise note (split already ran, 2385af29); ledger sync for the sitting
42b3abd5 Sync rimflow ledger: BRIDGETOOLS_CSHARP_SWEEP_BUGS_1 close
27c90a5a BRIDGETOOLS_CSHARP_SWEEP_BUGS_1: deployed, restarted, spot-checked
260f01a1 JAWA_PATCHES_SPLIT_1: split executes inside the consolidation sprint
c1a307d5 Sync rimflow ledger
da4f1e52 Consolidation sitting: 9 owner rulings landed; RimMaster→RimMandrake executed; mod domain census committed
81135e10 B9/B10: live spot-check notes - capMods confirmed, bill completion still owed
7ccec154 Droidworks: fix RSW_DW_Race_Primitive_G2 defName (ThingDefs can't end in a digit)
b317ef4c Sync rimflow ledger: DROIDWORKS_FULL_LIST_COEXIST_1 close
3b970039 A2: confirming full-list restart clean; refresh config-error baseline
e7d83fc3 Sync rimflow ledger: DROIDWORKS_PRIMITIVE_TIER_1 claim/start/block
5c80b179 Droidworks Primitive tier (B9): DW_Family_Primitive, G2 + Junker droids, ~40%-stat craftable parts/modules
4b2fcb39 Sync rimflow ledger — DROIDWORKS_WIPE_SEVERITY_1 claim/start/needs/note
07db7373 Droidworks B10: memory wipe now has teeth — 7-day relearning debuff, service-record reset, accreting hardware quirks
edeb0c9e Sync rimflow ledger
ac7c941f Repoint FDE droid kinds onto Droidworks races; fix the generator
2d25018e Sync rimflow ledger: DROIDWORKS_ION_SHIELD_BODYSIZE_1 claim/start/close
b329e342 JawaIonWeapons: ion breaks shields (B6, merged with body-size scaling)
d46d5bdd Sync rimflow ledger: DROIDWORKS_BOLT_PAYOFF_1 claim/start/close
6556f223 Droidworks: restraining bolt consequences - aura, shear, rebellion (B5)
6eea8d07 Sync rimflow ledger: DROIDWORKS_SHOP_BENCHES_1 claim/start/close
fbed4101 Droidworks: repair bench, reassembly harness, shop rebuild, overclock (B4b)
5c5f8ded Sync rimflow ledger: DROIDWORKS_FINE_PARTS_1 claim/start/close
2d9b14e3 Droidworks: fine parts per family, quality-scaled effects (B4a)
0e816ff4 Sync rimflow ledger: DROIDWORKS_HEADS_BRAINS_SPIKES_1 claim/start/close
c0e4e014 Droidworks: heads, brain trio, per-faction data spikes (B3)
40387d95 Sweep remaining uncommitted work outside Transient/ — owner directive, avoid losing anything
147e370c Sweep uncommitted Transient/ work (560 files, 217MB) — owner directive, avoid losing anything
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-09T00:26:34Z

Uncommitted (say for each whether it is yours or another seat's):

```
 M Transient/codebase_health.html                        -- NOT mine: BENCH's health-hook auto-snapshot
 M Transient/codebase_health.json                         -- NOT mine: same
 M Transient/codebase_health_artifact.html                -- NOT mine: same
 M Transient/codebase_health_hook.log                     -- NOT mine: same
 M infrastructure/state/codebase_health_last.json         -- NOT mine: same
 M infrastructure/state/items/IKEE_MYNOCK_ART_REGEN_1.md  -- NOT mine: unrelated art item, another seat's
 M infrastructure/state/items/MOD_CONSOLIDATION_SPRINT_1.md -- NOT mine: BENCH's sprint item, mid-flight
```
(41 further untracked Transient/ files, all from this wave's own bridge-test screenshots/logs —
disposable per the Transient/ rule, none is the only copy of anything, none referenced by a
committed doc.)

My own tree is clean: `git status --short` shows nothing of mine uncommitted, `git log
origin/main..HEAD` is empty (fully pushed), the rimflow ledger was synced in `93d5bfdd`.

