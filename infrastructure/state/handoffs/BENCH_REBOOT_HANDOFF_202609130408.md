# BENCH_REBOOT_HANDOFF_202609130408 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609130215`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The Mantistanis two-fix question is RESOLVED — do not reopen it.** The prior
handoff's carry-forward ("fold the existence-guard into the generator or rule
it redundant") is discharged: the generator fix (90d58be79, `LOADFOLDERS_GATED`
in `design/Jawa/fauna/gen_cast_patch.py`) is the durable one and explains the
real mechanism (VGE ships the nine GR_ Megafauna hybrids under a LoadFolders
`IfModActive="Spino.Megafauna"` subfolder — the def never loads even though its
owning mod is active). FOUNDRY's hand guard (1f222320b) is REDUNDANT
belt-and-braces; the next `gen_cast_patch.py` regen deleting it is correct
behavior, not a regression. FOUNDRY's claim that "MayRequire evidently does not
gate" was measured against a pre-fix deployed copy (the stale-deploy trap) —
do not build on it; vanilla MayRequire comma-list AND-semantics stand. Deployed
game copy verified byte-identical to repo this window (the prior handoff's
"predates 1f222320b" line is stale). Proof rides GIDDYUP_NULLKEY_COLD_READING_1.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Three things wait on him, nothing executed without his card:

1. **The verdict sitting** (`ASSIGNMENT_SHEETS_VERDICT_SITTING_1`) — both
   sheets were served this window; if the URLs died with the session,
   re-serve: `python3 /home/mandrake/.claude/skills/review-sheets/assets/serve_sheet.py
   --sheet design/Jawa/worldbuilding/review/fauna_assignment_register.html
   --decisions design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json`
   (same for flora_).

2. **Giddy-Up ruling** (`GIDDYUP_KEEP_OR_CUT_1`) — TWO independent blind
   analyses now exist (yesterday's window did one the item never cited;
   this window ran a second before discovering it). **Both agree: KEEP —
   the active mod is the maintained Owlchemist-rewrite line (Giddy-Up 2
   Continued v2.2.5), and both 09-12 crashes were our own cast data.**
   Treat KEEP as double-confirmed; the card is only the three dials the
   arms split on: mechanoid mounts (today: off / yesterday: keep),
   RunAndGun (today: cut / yesterday: cheap-to-keep), giveCaravanSpeed
   (yesterday: turn ON — today's pass didn't weigh it).
   Reports: `D:\Luke\dev\Rimworld\Transient\giddyup_keep_or_cut_2026-09-12.md`
   and `D:\Luke\dev\Rimworld\Transient\GIDDYUP_KEEP_OR_CUT_analysis_2026-09-13.md`.

3. **Modlist shortlist** (`MODLIST_COMPLEXITY_AUDIT_1`) — same two-arm
   situation, and here the arms only partially overlap, which is signal:
   **named by BOTH (strongest cards): Jurassic dinos cut, Ancient Urban Ruins
   family deactivation** (the 09-09 ruling cut its CONTENT via Cherry Picker;
   deactivating the still-active mods+DLLs is a NEW card, not already
   authorized). Named by one arm each: yesterday — Caravan Adventures cut,
   Dubs Performance Analyzer out, Mo'Events, VGE, Yayo's-vs-CAI overlap;
   today — Big and Small Races (100% hollow), RimAI Framework+Core
   (contradicts the 09-05 `claude -p` transport ruling), CQF, plus keep-notes.
   ⚠️ Gate on every cut: the save pre-check found **7 of 8 of today's
   candidates leave references in `CANONICAL_ASHKARR_START_2026-09-12.rws`**
   (RimAI core has LIVE GameComponents; JRW has 5 placed DinoChitin) — every
   cut card needs a save-cleanup step or an accepted-load-errors line.
   Reports: `D:\Luke\dev\Rimworld\Transient\modlist_keep_or_cut_shortlist_2026-09-12.md`,
   `D:\Luke\dev\Rimworld\Transient\MODLIST_COMPLEXITY_AUDIT_shortlist_2026-09-13.md`,
   `D:\Luke\dev\Rimworld\Transient\modlist_cut_save_precheck_2026-09-13.md`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `ASSIGNMENT_SHEETS_VERDICT_SITTING_1` — prep complete (sheets served, sidecar
  prefill warning from the prior handoff still stands: touchedBySheet:true
  predates the sitting, do NOT consume as a finished review). Stops at: the
  owner's eyes. Next action: re-serve if needed, sit with him, then the item's
  own verify chain (apply_assignment_verdicts.py → _validate.py --cross → regens).
- `GIDDYUP_KEEP_OR_CUT_1` — analysis double-done, merged card in "What the
  owner should see" above. Stops at: his ruling. Next action: serve the card;
  on a ruling, propagate (Mod Settings change and/or ModsConfig edit + item close).
- `MODLIST_COMPLEXITY_AUDIT_1` — two shortlists + save pre-check done. Stops
  at: his cards. Next action: serve the both-arms candidates first (JRW, AUR
  deactivation); each cut ruling needs its save-cleanup step executed and its
  own propagation (ModsConfig/Cherry Picker + per-cut item).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- **Repo-root `defs.sqlite` is a 0-byte decoy** (Sep 10) — an instrument
  pointed there reads an empty DB and calls everything absent. The real
  current dump: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs.sqlite`
  (594 mods, 2026-09-12, matches the save). Filed to LESSONS_INBOX; delete or
  repoint whatever left it.
- **An item filed alongside a finished analysis must cite the report path.**
  GIDDYUP_KEEP_OR_CUT_1 / MODLIST_COMPLEXITY_AUDIT_1 were filed with specs but
  no pointer to the prior window's completed reports in Transient/ — this
  window re-ran both as fresh Fable analyses before finding them via the old
  handoff. Salvaged as two-blind-arms evidence, but the spend was unplanned.
  Filed to LESSONS_INBOX.
- zsh: `echo ===` between commands is not a separator, `===` executes as a
  command and kills the chain — use `echo ---`.

## Closed since the last handoff (2)

- `GIDDYUP_NULLKEY_CRASH_1` — 1f222320b2e78f19b6c4bef2e95e845e90df6e47
- `CORRECT_GIDDYUP_NULLKEY_1` — 1f222320b2e78f19b6c4bef2e95e845e90df6e47

## Filed and still open (1) — the next seat's queue

- `GIDDYUP_NULLKEY_COLD_READING_1` — Cold-load log reading for the GR_Mantistanis null-key fix (1f222320b): add to the next run sheet

## Commits

```
b8fafc737 ledger: pre-check note on MODLIST_COMPLEXITY_AUDIT_1
7b80d69fa MODLIST_COMPLEXITY_AUDIT_1: save placed-things pre-check — 7/8 cut candidates DIRTY in canonical start save
f3476da1c artpipe/ledger housekeeping: daemon claimed retried jobs, render sync
838cd5cdb rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1 (2026-09-12 wave)
7dbb80b82 ART_REGEN_FLORA_WAVE1_QUEUE_1: wave 2, queue 15 more flora art:improve jobs + requeue 9 failed fauna jobs
b982f6b02 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark ashkarr_settle.py and JawaBenchSocietyTools.cs clean
e82a4ea05 MODLIST_COMPLEXITY_AUDIT_1: ranked 12-mod shortlist report (Fable)
77b83b31c COLD_LOAD_RUN_SHEET_4: fold in ENTRY 7 (Giddy-Up null-key + duplicate-key restart verify)
dc90b5b6d FOUNDRY BELT wave wrap: sync ledger/artpipe/review-status housekeeping
160e1e685 rimflow: close WORLD_NAME_FIXES_1
1df76373c WORLD_NAME_FIXES_1: apply and verify all 7 world renames live
efb2f02ad selftest_block_canon_contradiction: cover the write-time refusal path
bff684833 rimflow: close ART_REGEN_FLORA_WAVE1_QUEUE_1 at 4e3af6dc6
4e3af6dc6 ART_REGEN_FLORA_WAVE1_QUEUE_1: queue 14 flora art:improve jobs (daemon drained)
36521df01 TILEGEN_SILENT_REUSE_1: add live-repro diagnostic logging to world_tile_map_generate
655d3369f GIDDYUP_KEEP_OR_CUT_1: background analysis report (Fable) — recommends keep GU2 trimmed, cut RunAndGun
41608694e BENCH: start ASSIGNMENT_SHEETS_VERDICT_SITTING_1 — sheets served, awaiting owner
67f908c08 BENCH AFK wave: close GIDDYUP_NULLKEY_CRASH_1 + carrier, file cold reading, start keep-or-cut analyses
b83e7ff49 FOUNDRY wake: mode -> belt, sync ledger/artpipe/dashboard housekeeping
4fe0f502a FOUNDRY reboot handoff 202609130316: full-BELT wave wrap
6a9499a1b code-review: mark-clean 12 re-dirtied files (diff-scoped review)
bfa7c2f92 code-review: mark-clean 24 files (rimdrive/modcheck L1-L4a, RimUtinni FOUNDRY untracked wave)
d1c393c02 fix: modcheck runner truncation operator-precedence bug on finding names
bdf1b9a39 code-review: mark-clean remaining 20 RimStarWars files (Mlie Wave C defs, 16 SWBestiary animal ThingDefs_Races)
032461ff4 code-review: mark-clean 30 RimStarWars files (Settings/.cs, Sarlacc Defs+About, StructureInjectionsSW GenStep/TileMutator pairs)
c4858101e code-review: mark-clean 5 dev-tool Python files (Pits validation, art_zoom_sim, artpipe verdict sheet/apply)
aa2e63220 code-review: mark-clean GravshipLanding/LiquidTypes About.xml + LiquidTypes defs, biome dupe generator
bda42ac64 code-review: mark-clean 18 RimMandrake Mod Settings/GenStep/bridgetools files
f69955e42 fix: jawa/transporter_launch ignored dryRun for an existing transporterId
d85b7103f code-review: mark-clean 39 RimUtinni files (last-third batch)
18e1ab1b6 code-review: mark-clean 10 DivingInteraction/FloodedCanyon/FluidCanals files
d8a0b9b7d code-review: mark-clean 14 DivingInteraction/FloodedCanyon files
47ae589d5 fix: LiquidCorrosionMapComponent apparel-corrosion loop skipped items on removal
58720b3c2 code-review: mark-clean 5 Mod Settings files (WeatherSuite/RimProperty/Greentide/ProximityHatch)
311d90fc5 code-review: mark-clean 6 RustCathedralHum/Sarlacc gameplay files
e0f4ffdc7 fix: CompSarlaccSwimmer reserve refill was gated on prey survival, not kill
2f1e3946b code-review: mark-clean artpiped.py and selftest_artpipe.py
c8e2d629a BIOME_WORLD_SWITCH_WAVE_1: rename 19 stale roster defNames to RUT_; eviction still noisy
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-13T03:48:43Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 D infrastructure/artpipe/active/bilespawn_v1_north_r2.json
 D infrastructure/artpipe/pending/glowingagarilux_v1.json
 D infrastructure/artpipe/pending/gomphoeria_v1.json
 D infrastructure/artpipe/pending/hydenocktree_v1.json
 D infrastructure/artpipe/pending/iashiphus_v1.json
 D infrastructure/artpipe/pending/jogantree_v1.json
 D infrastructure/artpipe/pending/jungletree_v1.json
 D infrastructure/artpipe/pending/keeningcordax_v1.json
 D infrastructure/artpipe/pending/lilacbeacon_v1.json
 D infrastructure/artpipe/pending/mangrovetree_v1.json
 D infrastructure/artpipe/pending/mireflitwarden_v1_north_r2.json
 D infrastructure/artpipe/pending/rotscythe_v1_south_r2.json
 D infrastructure/artpipe/pending/sugarfamewort_v1.json
 D infrastructure/artpipe/pending/wastewing_v1_north_r2.json
 D infrastructure/artpipe/pending/wastewing_v1_south_r2.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
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
?? infrastructure/artpipe/done/agariluxprime_v1.json
?? infrastructure/artpipe/done/agariluxprime_v1.manifest.json
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
?? infrastructure/artpipe/done/crystalhorn_v1.json
?? infrastructure/artpipe/done/crystalhorn_v1.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/direwail_v1_east.json
?? infrastructure/artpipe/done/direwail_v1_east.manifest.json
?? infrastructure/artpipe/done/direwail_v1_north.json
?? infrastructure/artpipe/done/direwail_v1_north.manifest.json
?? infrastructure/artpipe/done/direwail_v1_south.json
?? infrastructure/artpipe/done/direwail_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
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
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.json
?? infrastructure/artpipe/done/fenshear_v1_north_r2.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.json
?? infrastructure/artpipe/done/firevine_fireweed_v1.manifest.json
?? infrastructure/artpipe/done/firevinetree_v1.json
?? infrastructure/artpipe/done/firevinetree_v1.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_east.json
?? infrastructure/artpipe/done/fumeback_v1_east.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_north.json
?? infrastructure/artpipe/done/fumeback_v1_north.manifest.json
?? infrastructure/artpipe/done/fumeback_v1_south.json
?? infrastructure/artpipe/done/fumeback_v1_south.manifest.json
?? infrastructure/artpipe/done/giantagarilux_v1.json
?? infrastructure/artpipe/done/giantagarilux_v1.manifest.json
?? infrastructure/artpipe/done/giantagaritox_v1.json
?? infrastructure/artpipe/done/giantagaritox_v1.manifest.json
?? infrastructure/artpipe/done/giantgamma_v1.json
?? infrastructure/artpipe/done/giantgamma_v1.manifest.json
?? infrastructure/artpipe/done/globularplant_v1.json
?? infrastructure/artpipe/done/globularplant_v1.manifest.json
?? infrastructure/artpipe/done/glowingagarilux_v1.json
?? infrastructure/artpipe/done/glowingagarilux_v1.manifest.json
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
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/greenrockfern_v1.json
?? infrastructure/artpipe/done/greenrockfern_v1.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
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
?? infrastructure/artpipe/done/mangrovetree_v1.json
?? infrastructure/artpipe/done/mangrovetree_v1.manifest.json
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
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
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
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_east.json
?? infrastructure/artpipe/done/rotscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_north.json
?? infrastructure/artpipe/done/rotscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.json
?? infrastructure/artpipe/done/rotscythe_v1_south_r2.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_east.json
?? infrastructure/artpipe/done/sporehulk_v1_east.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_north.json
?? infrastructure/artpipe/done/sporehulk_v1_north.manifest.json
?? infrastructure/artpipe/done/sporehulk_v1_south.json
?? infrastructure/artpipe/done/sporehulk_v1_south.manifest.json
?? infrastructure/artpipe/done/sugarfamewort_v1.json
?? infrastructure/artpipe/done/sugarfamewort_v1.manifest.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.json
?? infrastructure/artpipe/done/tanglerootmangrove_v1.manifest.json
?? infrastructure/artpipe/done/toxicgamma_v1.json
?? infrastructure/artpipe/done/toxicgamma_v1.manifest.json
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
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wildradagast_v1.json
?? infrastructure/artpipe/done/wildradagast_v1.manifest.json
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
?? infrastructure/artpipe/failed/rotscythe_v1_south.json
?? infrastructure/artpipe/failed/rotscythe_v1_south.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_north.json
?? infrastructure/artpipe/failed/wastewing_v1_north.manifest.json
?? infrastructure/artpipe/failed/wastewing_v1_south.json
?? infrastructure/artpipe/failed/wastewing_v1_south.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

