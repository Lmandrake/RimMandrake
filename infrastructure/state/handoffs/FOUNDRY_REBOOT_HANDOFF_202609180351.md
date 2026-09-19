# FOUNDRY_REBOOT_HANDOFF_202609180351 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609180218`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**`rimflow close`'s ownership refusal is no longer absolute.** The CLI still refuses
`FOUNDRY may not close X — it belongs to OWNER` (or another seat) by default, but the
owner ruled this session (verbatim: *"Please stop being an absurd stickler for rules.
When you find something done ANYONE can close the item."*) and it's now written into
`infrastructure/agents/CHARTER.md`'s Queue section as a standing default: when a seat
finds an item **genuinely DONE** (proven, not assumed — same bar `close` always
required), it may close it under any owner, citing the ruling verbatim via
`--owner-said` — no fresh ask needed each time, no code change needed (the tool's
existing escape hatch already does it). Used it this session to close
`NINEFOLD_GRAVSHIP_HOOK_SCOPE_1` (an owner-kind item whose work had shipped weeks
earlier and just never got closed). Don't rediscover this by getting refused and
giving up, or by pinging him again for something already ruled.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Water-breathing gene roster contradicts canon** — the design brief
  (`design/RimStarWars/aquatic_water_breathing_design.md` §6, item
  `AQUATIC_WATER_BREATHING_GENE_1`) found the item's own species list (Mon Calamari,
  Nautolan, Gungan, Selkath) doesn't match the canon library: Gungan's own canon text
  calls it a *breath-holder*, not a water-breather, and Quarren (not on the list) is
  canon's actual "most comfortable underwater" species. Design + mechanism (one
  GeneDef, no new C#) is ready to build the moment he picks a roster. Already told him
  this once mid-session; repeating here so it doesn't get lost at reboot.
- **`MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` is 1/3 done, not 3/3.** He ruled "enable at
  next restart" for all three inactive mods; `mandrake.rm.environmentalhazards` is now
  ACTIVE (another window's commit `9bf9ccf4e` beat me to it), but
  `mandrake.rut.injections` and `mandrake.rut.utinnipatches` are STILL inactive as of
  this handoff (re-checked directly against the live `ModsConfig.xml`, not assumed) —
  the next restart still owes flipping those two on with correct load-order placement.
- **Universal cargo tank**: real building now exists (`RM_LiquidTank`,
  `LIQUID_BOTTLE_LOOP_1`, commit `52b9c584e`) with fill/drain jobs and his art on it.
  Its assembly (`RimMandrakeFlowWorks.dll`) failed to deploy — locked by the running
  game — so it isn't live yet even after a restart unless that deploy is re-run first.
  No live quicktest has ever run on it or the fill/wash bottle chain underneath it.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
Touched this window (real progress, verified/committed/pushed, left `doing` on purpose):
- `LIQUID_BOTTLE_LOOP_1` — bottle/bucket/barrel real art shipped and wired
  (`cbe48fdf7`), tank building + fill/drain jobs built (`52b9c584e`). Not touched by
  the 2026-09-18 window that followed this one. NEXT: deploy `FlowWorks`'s assembly at
  a game-down window, then a live quicktest of both the tank and the fill/wash bottle
  chain — neither has ever run live. (Note: FlowWorks' liquid framework was found this
  same 2026-09-18 window to have never had working water terrain at all due to a
  case-mismatched enum value — fixed in `cd8ab494e`, see `QUICKTEST_RIVER_WATER_MISSING_1`
  — re-verify this item's own liquid mechanics still work once that fix is deployed.)
- `AQUATIC_WATER_BREATHING_GENE_1` — design brief complete (`d47ab4874`), mechanism
  chosen (one GeneDef, no new C#, one added clause in FlowWorks' `CanSwim`). Not
  touched by the 2026-09-18 window that followed this one. NEXT: owner picks the
  species roster (see "What the owner should see" above), then FOUNDRY builds it.
- `MLIE_FAUNA_ABSORPTION_1` — STALE, superseded by the 2026-09-18 window's own handoff:
  now at Pass 19 (29/90 remaining, not 51), see `FOUNDRY_REBOOT_HANDOFF_202609181353`'s
  own half-done entry for the current, precise state (Pass 20 was interrupted mid-flight,
  real uncommitted art exists). NEXT: read that later handoff instead of this stale one.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — several waves this window: Armoury (58 files, 2
  bugs), RotSporeKit/AftermathRites/RaidRedesigner/RimProperty/Droidworks(both tiers)
  (13 files, 4 bugs including a real `<li>`-discards-the-def MayRequire gap), FlowWorks
  (71 files, 5 bugs including a broken tar-superdeep passability and a pit double-
  occupant UI gate that could never actually place a second prisoner). Continued heavily
  in the 2026-09-18 window under the `DIRTY_CODE_REVIEW_LOOP_RESTART_N` chain (now past
  RESTART_15, ~98.7% clean). NEXT: run `code_review_status.py list` fresh, then continue
  from whatever `DIRTY_CODE_REVIEW_LOOP_RESTART_N` (highest N) names as its own next pick.
- `TILE_STRUCTURE_DESIGNS_1` — STALE, superseded by the 2026-09-18 window's own handoff:
  now 19/22 promises, 8/22 whispers (whisper side effectively done — remaining 14 rows
  all explicitly rejected/duplicated with evidence). NEXT: see
  `FOUNDRY_REBOOT_HANDOFF_202609181353`'s own half-done entry — rebuild The Kiln's
  promise row now that its identity is ruled (crater, not furnace), then the item's
  last real criterion (`GenStep_RimplacePlan` proven via a live quicktest) needs bridge.
- `MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` — filed this window, 1 of 3 already resolved
  by another window. NEXT: enable `mandrake.rut.injections` and
  `mandrake.rut.utinnipatches` at the next restart, correct load-order per
  `rimworld-start-prep`, per the owner's explicit ruling recorded on the item.

Pre-existing `doing` items re-verified this window, NOT advanced (offline-only re-check
found no drift or gap — flagging per the handoff gate, not claiming new progress):
- `VAULT_DUNGEON_BUILD_1` — no drift since 2026-09-12. Neither
  `mandrake.rut.injections` nor `mandrake.rut.utinnipatches` (holding the vault
  templates/quests and the V5 landmark) is active live — same gap as above, same fix.
  Still owed: Type-2's live quicktest, V5 landmark placement on tile 37, six
  real-site hand-finish passes (with the owner, per the item's own note).
- `NINEFOLD_MISSING_EVENT_HOOKS_1` — all four god hooks (Sh'kaar, Ohm, Mob'Unloo,
  Ta'Baa) confirmed source-complete and building clean; Sh'kaar/Ohm already
  live-confirmed earlier, Mob'Unloo/Ta'Baa still need a real trade and a real launch
  triggered live to prove satiation actually updates. Two companion bridge tools
  (`jawa/trade_execute`, `jawa/transporter_launch`) exist but aren't deployed (game
  running, locked) — deploy at the next restart alongside everything else above.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- **Deploy ≠ enabled, and this bit three items independently in one session.**
  `deploy_custom_mods.py --apply` reporting "in sync" only means the FILES match — it
  says nothing about whether the mod is active in `ModsConfig.xml`. Three custom mods
  (EnvironmentalHazards, StructureInjectionsRUT, UtinniPatches) were all byte-identical
  deployed on disk but simply never enabled, silently making real shipped code do
  nothing in the actual game. Worth checking both, always — `deploy_custom_mods.py`'s
  own plan output DOES print "not enabled in ModsConfig" when it's true, it's just easy
  to skim past.
- **A companion/mod DLL cannot be written while the game is running** — hit again this
  session (CreatureBehaviors, then FlowWorks). Not new, but worth restating: any pass
  that touches C# and reports "0 warnings/0 errors" on `dotnet build` has NOT actually
  redeployed if the game was up at the time — check the deploy step's own output, don't
  infer success from the build alone.
- **A rebuilt DLL with unchanged source still shows as a git diff.** .NET embeds a
  fresh MVID/timestamp on every build, so `dotnet build` with zero source changes still
  produces a byte-different (same-size) assembly. Caught one on `RimMandrakeNinefold.dll`
  at handoff time — a pure re-verify build with no code touched, `git checkout --`'d
  rather than committed as a churny no-op. Don't mistake this for a real change, and
  don't leave it dirty in a handoff either.
- **`rimflow file --needs game-up` prints a refusal-shaped warning but still files the
  item anyway** — the printed text ("A live check is owed only to a mechanism never
  once observed running... Answer in one line...") reads like a hard refusal but is
  actually just a prompt; check `rimflow show <ID>` after a `file` call that looks like
  it bounced, don't assume it didn't file. (Separately: `needs=game-up` was the wrong
  tag for `MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` — the roster DIFF is pure offline file
  comparison; only flipping mods on and proving they work needs the restart. Left the
  tag as-is with a clarifying note rather than fighting the CLI further.)
- **Heavy concurrent multi-window activity is normal now, not an anomaly.** This
  session ran 8 subagents across 3 waves while BENCH and at least one other FOUNDRY
  window pushed 15+ of their own commits interleaved (Pyrelands density, five ROT_*
  builds, EMBERSCYTHE_MANTIS_REAUTHOR_1) with zero collisions — the pathspec-on-every-
  commit discipline (never `git add -A`, never a bare `git commit -m`) held up under
  real concurrent load exactly as designed. Worth confidence, not just caution.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (3) — the next seat's queue

- `MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1` — Live 632-mod ModsConfig.xml has several deployed custom mods INACTIVE -- reconcile before the next restart/play session
- `AQUATIC_WATER_BREATHING_GENE_1` — Design and build a real water-breathing mechanism (gene or hediff) for the 4 aquatic xenotypes currently missing one entirely
- `EMBERSCYTHE_MANTIS_REAUTHOR_1` — Re-author the dead GR_Mantistanis as our own Emberscythe (Pyrelands flame-edge hunter) and wire it into the cast

## Commits

```
3cedfdca9 rimflow: ledger sync (LIQUID_BOTTLE_LOOP_1 tank pass note)
52b9c584e LIQUID_BOTTLE_LOOP_1: build the universal-tank v1 slice — fill/drain at RM_LiquidTank
82cf04e80 EMBERSCYTHE_MANTIS_REAUTHOR_1: RUT_Emberscythe race+kind (the dead GR_Mantistanis, ours now)
0c86c019b rimflow: ledger sync (MLIE_FAUNA_ABSORPTION_1 Pass 12 note)
2cd0ebcb1 MLIE_FAUNA_ABSORPTION_1 Pass 12: port Gizka, Grank, GreaterKraytDragon, Hawkbat (56 -> 51 remaining); remove stale Nuna worklist entry
3f33928de rimflow: ledger sync (water-breathing design note, PYRELANDS_DENSITY_TRIPLE_1 filing)
d47ab4874 AQUATIC_WATER_BREATHING_GENE_1: design brief — one GeneDef + one CanSwim clause
1d55fa45d Pyrelands: plantDensity 3.0 + enforcer that beats the startup rewriter (owner: "three times that. No more small nudges")
e4c3d18dd rimflow: ledger sync (DIRTY_CODE_REVIEW_STANDING_LOOP_1 FlowWorks wave note)
6bc642cb9 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 71 FlowWorks files this wave
d0b0d6b7b DIRTY_CODE_REVIEW_STANDING_LOOP_1: FlowWorks wave, 5 real bugs fixed across 71 files reviewed
c94704c67 CHARTER: any seat may close a genuinely-done item (owner ruling 2026-09-18); close NINEFOLD_GRAVSHIP_HOOK_SCOPE_1; record mod-enable ruling; file AQUATIC_WATER_BREATHING_GENE_1
9bf9ccf4e Activate mandrake.rm.environmentalhazards in both mod lists (owner: "Yes, both lists")
b8d87d692 ROT_LIVE_PREPARATIONS_1: brewing vessel, 3 teas, 4 symbionts, sale conscience (cards 1+6)
296d1dd83 rimflow: ledger sync (NINEFOLD_MISSING_EVENT_HOOKS_1 / NINEFOLD_GRAVSHIP_HOOK_SCOPE_1 notes)
e0ba9648e NINEFOLD_MISSING_EVENT_HOOKS_1: offline re-verify pass, no wiring gap found
1f1b0ec8c rimflow: ledger sync (MLIE_FAUNA_ABSORPTION_1 Pass 11 note)
bab45edca MLIE_FAUNA_ABSORPTION_1 Pass 11: port IridonianReek, Jakobeast, Jamel, Jimvu (60 -> 56 remaining)
b59ff976f rimflow: file MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 (three inactive custom mods found this wave)
00da90518 VAULT_DUNGEON_BUILD_1: offline re-verify pass, no drift, one new finding
6bc5c684a DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean the 4 fixed RotSporeKit/AftermathRites files
562ae2718 DIRTY_CODE_REVIEW_STANDING_LOOP_1: RotSporeKit + AftermathRites/RaidRedesigner validation wave
785100e16 rimflow: pyrelands checkout closes 2 items; ENVHAZARDS_NEVER_ACTIVATED_1 filed; rot wave notes; bridge released
211b2f0c8 ROT_GUARDIAN_GROVES_1: three defended tea-source mushrooms + false-fruit lure (card 6: confession toggle)
1659c1793 rimflow: ledger sync (BELT wave notes: Mlie pass 10, Armoury review, liquid bottle art, xenotype fixes, structure batch)
e8aec8b25 TILE_STRUCTURE_DESIGNS_1: whisper batch 2 - Listening Dark + Sarlacc Sign (3/22 -> 5/22)
06dd34811 MLIE_FAUNA_ABSORPTION_1 Pass 10: port Gutkurr, Hrumph, Hssiss, Igitz (64 -> 60 remaining)
a63dc4d2a Rot wave shared wiring + FIX: b5b947fe9 shipped no code (csproj compile list)
94f1139bc ROT_WARM_MAT_1: warm-ground map component + grown furnace + Furnaceblood gene (card 3: free forever)
35680b323 ROT_SHEEN_WEATHER_1: Sheen weather reskin + exposure ladder (card 5: gear slows 4x, symbiont only full immunity)
4eab208d6 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark 58 Armoury files clean
0fc737f9d DIRTY_CODE_REVIEW_STANDING_LOOP_1: Armoury wave, two real bugs
512d1fb57 ROT_PALE_TREE_1: RUT_PaleTree anima reskin, psylink cap 2 (owner card 4) + RUT_PaleMoss
cbe48fdf7 LIQUID_BOTTLE_LOOP_1: real art for the bottle/bucket/barrel line + tank concept
5d5a16577 Xenotypes: give Sith Massassi the caste's own nameMaker (XENOTYPE_NONCOSMETIC_FIXES_1)
eaef4cf04 rimflow: drop FLUID_CANAL_MECHANIC_1 (absorbed into FLOWWORKS_BUILD_PROGRAM_1)
ae93947dd rimflow: bridge take/release (ROT-kit quicktests deferred, no restart this pass)
bc894b2ab Rot kit: all six owner cards RULED at the bench (spec + ledger)
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     measure live plantDensity, then deploy x3 (owner order)

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? infrastructure/artpipe/active/rotscythe_v1_south.json
?? infrastructure/artpipe/active/twistingthornweed_v1.json
?? infrastructure/artpipe/active/wastewing_v1_north.json
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/state/.rimflow_conc_97j8px_9/
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? src/RimStarWars/GizkaStowaway/
```

