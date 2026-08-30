## Spec
The next batched window scores everything below, then this closes and a fresh sheet is
filed. Predecessor COLD_LOAD_RUN_SHEET_1 was scored 2026-08-29 (see its notes); detail
for any named item lives in items/<ID>.md.

## 0 — game DOWN, before anything else ✅ DONE 2026-08-29 (BENCH, second sitting)
```
taskkill.exe /F /IM RimWorldWin64.exe
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply
```
- ✅ Deployed at 81610f55: carries the scenario tools AND everything since
  (gravship skipCutscene, GM pair). Surface MEASURED 254 upper bound via
  tool_surface (was "expected 246" when only the scenario pair was pending —
  drift is later commits, not a leak; the launch ready-line derives its own
  gate from EXPECTED_TOOLS).
- ✅ sync_mod_state --apply: 7 files, every record now 1.6.4871 rev591 / 585
  mods, verified; backups alongside as *.bak-sync_mod_state.
- ✅ defDump RE-ARMED (dump_request.txt = all): the PAWN_FLAVOR and ISEKAI
  checks below need a fresh 585 capture from this load.
- ✅ RE-RUN 2026-08-29 (third sitting, game DOWN after the owner's session): game
  DLL copy was stale (55cd2e4971dd); rebuilt and redeployed at 8186a298939e — now
  carries the kcsg_place/vge_spawn bridge commits. deploy_custom_mods in sync
  (0 files, 14 held); sync_mod_state agrees (1.6.4871 rev591 / 585); dump still
  armed `all`. ⚠️ FOUNDRY's JAWA_TOOLS_ALL_DARK_DUPLICATE_ALIAS_1 may still be in
  this build — the launch ready-line gate decides.

## 1 — decision strings at launch
| # | expect | means if wrong |
|---|---|---|
| 1 | `[JawaBench] ready: 245 tools` (246 surface - 1 phantom... MEASURE, do not trust this literal) | old DLL loaded |
| 2 | `[JawaBench] context: modSet 582/…` | wrong mod list |
| 3 | NO `defDump ARMED` on the context line | a stray dump_request.txt re-appeared |

## 2 — with the bridge, campaign/scratch map
| item | reading |
|---|---|
| EMPIRE_PURSUIT_SCENPART_INSTALL_1 | the one-call install + scratch proof; exact call in the item note (2026-08-29). initCalls REQUIRED. |
| SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1 | mechanism still unread; substitution measured again 2026-08-29 (5/39 battery, 6/245 harvest, always vanilla Colonist, always bare) |
| SIX_FACTIONS_NEVER_RAID_1 | re-run ONLY on an aged colony with >600-tick census windows; identify the raid-deferring Harmony patch first (see 2026-08-29 note) |
| JAWA_SCENARIO_PARTS_1 | Jawa_UtinniStart spawns exactly one Ikee, Obedience-trained, Bonded — needs a NEW game start, could not run 2026-08-29 without tearing down the owner's loaded session |

## 3 — needs the GRAVSHIP SAVE loaded (BENCH_console_fixed.rws or successor)
| item | reading |
|---|---|
| EXPORTER round trip (owner sequencing: FIRST) | export_structure.py --rect 83,59,86,133 on the real megabone ship; the 2026-08-29 attempt exported desert rock — the ship is NOT on the fresh-start Ash'karr map |
| hull repaint | ONLY after the round trip: repaint_hull.py --census, --plan world/_ship/v2/plan_corrosion_halo.json --apply, RE-EXPORT, confirm paint carries; then apply_wall_colors.py/apply_wall_stuff.py are superseded and deletable |

## 4 — owner decisions surfaced 2026-08-29, still open
- ~~Frozen OFFICIAL capture gone~~ RESOLVED before this line was read: registry
  carries OFFICIAL-2026-08-29 (capture 2026-08-29T13-30-02Z, 584 mods, by owner),
  superseding the lost 2026-08-21 entry. Owner confirmed 2026-08-29: newer one is
  right.
- ~~'Galactic Empire' names TWO factions~~ NOT OPEN — ruled 2026-08-28 (canon.yml
  `empire.outerrim_faction_excluded`, does not reopen): OuterRim FactionDef cut in
  Cherry Picker (verified `present` in live settings 2026-08-29), mod stays active.
  The double reading was BENCH_console_fixed.rws, initiated pre-cut — residual only.
  WORLDMAP_V1_original.rws verified clean 2026-08-29 (0 hits both copies, literal
  scan w/ control; vanilla Empire present).
- WILD_ANIMALS_PADDED_LISTS_1: cast biomes are not exclusive (145 non-cast animals at >0 in
  Desert); 10 Anomaly-entity cast entries can never wild-spawn.

## 5 — look-at (owner's eyes, unchanged from sheet 1)
Adult bantha/eopie carry the new art; world labels clear of the limb (W5 exactly four
substitutions); 23 creatures visibly smaller, Zakkeg/Thrumbungus bigger; the Ikee reads as
a creepy eye with slime trail + nuzzle + mood pair. Plus NEW: the test dwelling stands at
rect 25,25,18,10 on the current map (disposable).

## PAWN_FLAVOR_STARWARS_1 — Jawa_PawnFlavor first load (added 2026-08-29, BENCH)
Deployed and active at position 581 (after mandrake.jawa.patches). Decision
strings for the next full-list load, written BEFORE the launch:
- FAIL if Player.log contains `Config error in Jawa_` or
  `Could not resolve cross-reference` naming any `Jawa_` or `JawaBSC_` id, or
  `Could not find parent node` after our mod loads.
- PASS positive observation (not mere silence): the post-load def dump contains
  BackstoryDef `Jawa_FarmFostered` and TraitDef `Jawa_WaterDiscipline`
  (`measure count BackstoryDef` should read 1225+50+5=1280 against a 585
  capture — round 5 added 5 Deepwater backstories 2026-08-29:
  `Jawa_CisternHatched` present, and Jawa_DeepwaterCompact's merged
  backstoryFilters carry `JawaBSC_Deepwater`),
  AND one spawned pawn of Homestead Defense League or Deep Desert Tribes shows a
  Jawa_* backstory title in its Bio tab (bridge: spawn via faction pawnkind,
  screenshot the card). Filter merge means roughly 1-in-3 pawns draw our
  category — check several pawns before calling absence.
- Also due at next game-DOWN: sync_mod_state (saves record 584, list is 585).

## PAWN_FLAVOR cut pass — Cherry Picker verification (added 2026-08-29, BENCH)
143 new keys written to Mod_CherryPicker.xml (1342 -> 1485; backup
`.bak-20260829-pawnflavor`): 141 BackstoryDefs (Minotaur/Medieval/VQE-Ancients/
Archon) + TraitDef/RBM_Herculean_Trait + TraitDef/VQE_IdealPatient. Decision
strings, written BEFORE the launch:
- PASS: `[Cherry Picker]` removal list in Player.log contains
  `- BackstoryDef/RBM_Akabeko,` (sentinel for the whole class) and the two
  TraitDef lines. ⚠️ BackstoryDef is UNPRECEDENTED in this config — if the log
  shows the ThingDef cuts but NO BackstoryDef lines, Cherry Picker does not
  process that def type: revert nothing, file the spawnCategories-neutering
  patch fallback instead.
- EXPECTED noise, not failure: up to one `No shuffled ... Choosing random`
  error per VQE-quest patient or stray consumer pawn (10 mod-private categories
  emptied on purpose; engine falls back benignly — verified in source).
- The two save-carried exclusions (`RBM_Roamer`, `SH_MED_MedievalAlchemist`)
  must NOT appear in the removal list.

## RAKATA sleeper backstories first load (added 2026-08-29, BENCH — supersedes the
## "expected VQE noise" line above: the pools are now FILLED, so that noise is a FAIL)
`Jawa_PawnFlavor/Defs/Backstories_Rakata_Sleepers.xml` (10 defs into the two VQE
categories) + `Jawa_Patches/Patches/VQEPatients_AreRakata.xml` (repoints
VQE_Experiment's fixed backstories off three CUT defs; validate_patch 3 ops / 1
match each). Both deployed. Decision strings, written BEFORE the launch:
- PASS positive: post-load def dump contains BackstoryDef `Jawa_RakataLineBreaker`
  and `Jawa_RakataFleshShaped`; dump's VQE_Experiment kind reads
  fixedChildBackstories=Jawa_RakataTakenChild, fixedAdultBackstories=
  Jawa_RakataFleshShaped, and NO forcedTraits node.
- FAIL: `Could not resolve cross-reference` naming `VQE_KidnappedChild`,
  `VQE_IdealPatient` or any `Jawa_Rakata*`; or `No shuffled backstory ...
  VQE_AncientPatient` (that pool must no longer be empty — this REVERSES the
  "EXPECTED noise" line in the cut-pass section for the VQE categories; the other
  9 mod-private categories' noise stays expected).
- forcedTraits ride: ShootingAccuracy(1), TooSmart, Nerves(±), Tough, GreatMemory,
  NaturalMood(-1), BodyPurist — all verified in capture 13-30-02Z + RimSage degrees.
- ALSO (owner yes, 2026-08-29): both VQE kinds forced `RimMandrakeRakata` 1.0 +
  useFactionXenotypes false (same R-A4 shape as AncientsAreRakata). PASS: dump
  reads exactly ONE xenotypeChances entry on VQE_Patient and VQE_Experiment;
  bridge-spawn one VQE_Patient — Rakatan head/gaunt body, not baseline (the VQE
  C# then adds archite genes on top: expected, it IS the flesh-shaped fiction).

## ISEKAI reflavor first load (added 2026-08-29, BENCH)
IsekaiTraits_StarWarsReflavor.xml deployed (validate_patch: 30 ops, 1 match
each). Decision strings:
- PASS: next def dump (post-patch) reads TraitDef `Isekai_Protagonist` degree
  label as `chosen one` and `Isekai_Rank_F` as `guild rating F`
  (`measure record`); no `Patch operation ... failed` naming
  IsekaiTraits_StarWarsReflavor in Player.log.
- Remember: a patch that matches nothing logs nothing — the dump read is the
  positive check, the log only catches structural failure.

## EMPIRE_PURSUIT_SURVEY_SHADOW_1 — fork swap first load (added 2026-08-29, BENCH)
Owner asked for it at the bench. `mandrake.empirepursuit` (survey-shadow fork)
deployed and swapped into upstream's exact ModsConfig slot (295;
matathias.ruthlessmechanoids OUT; snapshot
`infrastructure/state/modlists/ModsConfig_2026-08-29_pre_empirepursuit_swap.xml`;
saves re-synced to the new 585). Decision strings:
- FAIL: `ReflectionTypeLoadException` or `Could not resolve type` naming
  RuthlessPursuingMechanoids; or the campaign load raising a scenario/ScenPart
  error (`Could not load reference` on the scribed pursuit part) — the fork
  keeps upstream's defName+class precisely so the save resolves.
- PASS positive: campaign loads clean AND (bridge, game-up) the item's own
  verify — scratch game, tiny delays: normal-biome map on the fast clock, an
  `AB_RockyCrags` (Forsaken Crags) map on the ~4x clock, read from the part's
  scribed mapRaidTimers in a save.
- ⚠ RimSort is possibly open: its view is now stale — hit Refresh, don't Save
  over this.

## TURRET DOCTRINE first load (added 2026-08-29 third sitting, BENCH — AFK batch)
Deployed: `Turrets_DamageDoctrine.xml` (71 generated ops) + `Turrets_Renames.xml`
(10 label ops) in Jawa_Armoury; 28 new Cherry Picker keys (1485→1513, backup
`.bak-20260829-turretroster`): 27 non-roster turrets + Grenade_TurretPack (its
Turret_TacticalTurret is cut; Apparel_PackTurret was already cut). Decision
strings, written BEFORE the launch:
- FAIL: `Patch operation ... failed` naming Turrets_DamageDoctrine or
  Turrets_Renames; or a red duplicate-def error naming any `Jawa_TD_*` clone
  (the anchored-add matched more than one file).
- PASS positive (dump): `Bullet_TurretSniper` damageAmountBase 960;
  `EWebShot` damageDef `OuterRim_Blaster` 368; `Bullet_TeslaBlaster` damageDef
  `EMP` 80; `GTbc_Rocket_TheSingularityCannon` 72085 r14.9; label of
  `VFES_Turret_ChargeRailgun` reads `helical charge railgun`. Clones present:
  `Jawa_TD_Turret_AutoChargeBlaster` (107), `Jawa_TD_GraserBeam` (395).
- PASS (Cherry Picker log): removal list contains `- ThingDef/Turret_MiniTurret,`
  and `- ThingDef/Turret_Autocannon,`.
- EXPECTED noise, not failure: KCSG/structure-gen or settlement gen misses
  naming cut turrets (VOID bases, DP maps, Settlement_Generic, VQE symbols) —
  bases just lose a turret. UNEXPECTED: an NRE at map gen naming one.
- ✅ LIVE-VERIFIED 2026-08-29 (BENCH, bridge, owner's test save, cleaned up
  after): patches applied with zero failures; renames live on spawned objects
  ("Steel ancient beam cannon", "scrap beam zapper"); Jawa_TD_* clones +
  Jawa_TD_GraserBeam resolvable live; Cherry Picker removal sentinels present;
  uranium slug turret ACQUIRED AND FIRED under the doctrine patch (30→28
  shots). Numeric writes stand on validator-1-match × 72 + clean log.
- Still owed at a quicktest (NOT the campaign map): an observed HIT carrying a
  doctrine number (spawn a slow/large hostile at proper range — fast scarabs
  rush inside turret minimum ranges and eat misses); ancient beam cannon
  auto-fire question (custom C# — never engaged while powered+factioned; may
  be manual-fire, which matters for its Rakatan-ruin placement); tesla EMP
  arc; VEF flame stream; one r14.9 blast look. Watch mech-cluster gen still
  places AutoMini-less mixes.
- ⚠ New this load, upstream of us: `Jawa Patches (local)` logs one failed
  PatchOperationFindMod(Vanilla Factions Expanded - Insectoids 2) — predates
  today's work, needs one look.
- ~~Mortars research orphan~~ CORRECTED 2026-08-30: measured 21 unlocks, only 2
  cut — NOT an orphan; the research pass handles it with the whole tree.

## SALVAGERS_FOLD_JUNKERS — campaign load check (added 2026-08-29, BENCH)
WORLDMAP_V1_original.rws edited: Salvagers ("The Comet Party") scribed
`defeated=True` (backup `.pre_salvager_fold_2026-08-29.rws`). On the next
CAMPAIGN load: no Scribe error naming `Faction_24` or `Salvagers`; The Comet
Party absent from the faction/comms UI (or listed defeated); Junkers unchanged.

## Load scored 2026-08-30 (the doctrine load, BENCH — game up at 02:0x, build 585b31e0)
- ✅ TURRET DOCTRINE: 72-op patch (anticraft included) + renames applied, 0
  failures, 0 duplicate Jawa_TD_* errors; Cherry Picker removal list carries
  the turret cuts (autocannon sentinel read). Grenade_TurretPack key is INERT
  (projectile-shaped def, CP does not process it) — harmless: its delivering
  apparel IS removed, so the projectile is unreachable. Key left in place.
- ✅ PAWN_FLAVOR/RAKATA/ISEKAI/EMPIRE_PURSUIT/SALVAGERS: all FAIL strings zero
  on the PREVIOUS load's log (harvested before the cycle); BackstoryDef
  Cherry-Picker sentinel fired there. This load: Jawa_ config errors 0,
  cross-refs 0.
- ✅ JawaBench ready: 301 tools, build 585b31e0 (HEAD) — companion current.
- ⚠ Droidworks (inactive) logged a dependency-URL warning ×2 — About.xml
  fixed + redeployed same sitting; gone at next launch.
- Bio-tab positive check + live-fire observations ride the bridge session
  (bridge held by FOUNDRY at scoring time; BENCH queued on release).

## Bridge session 2026-08-30 (BENCH, quicktest map — game up, doctrine load)
- ✅ **TURRET DOCTRINE OBSERVED LANDING: Gunshot severity 960 EXACT** — one
  uranium slug killed a penned manhunter thrumbo outright, severing three body
  parts (save qt_fire_probe7, screenshot doctrine_kill_20260830.png). The
  in-place write mechanism is proven end-to-end; remaining rows stand on
  validator+log. Learned en route: turrets ignore placid animals (threat
  gating), mannable pieces (VFES ballista) never auto-fire, VFES flamer needs
  chemfuel network, "Cannot fire: Roofed" is in the inspect string, zapper
  beams slice damage in C# so severities can't read the patch.
- ✅ **PAWN_FLAVOR POSITIVE PASS**: pawns spawned UNDER the reskinned factions
  (OutlanderCivil=Homestead, TribeCivil=DeepDesert) drew 4/16 Jawa_ backstory
  slots incl. the sentinel `Jawa_FarmFostered` + Jawa_MoistureBaron,
  Jawa_KraytWatcher x2 (save qt_flavor_probe2). Faction context is REQUIRED -
  kind-only spawns draw generic bios (that is by design, filters ride factions).
- ✅ SPAWN_PAWN_SUBSTITUTES: defect not reproducing (see item note).
- ⏳ Singularity Cannon blast look: STILL OWED — it needs a linked GravTech
  targeting terminal + a loaded Black Hole Shell + 55 minimum range: a siege
  CHAIN, not a spawn. (Also good vault-design intel: it cannot be casually
  fired.) Tesla EMP arc + flame stream: mechanism-proven by the 960; specific
  behaviors ride the next sitting or the vault dressing pass.

## The Salvation + VME_Nomad (added 2026-08-30, BENCH — owner ruling)
Player .rid now carries VME_Nomad as a 4th normal meme (repo + Ideos copies,
validated 267/267). At next load with the ideo in play: PASS = The Salvation
loads with all 4 memes visible and the settled-too-long mechanic armed; WATCH =
any meme-cap complaint or a silently dropped meme (fixed-ideo loads usually
bypass editor caps — verify, don't assume).
