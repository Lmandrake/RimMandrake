# BENCH_REBOOT_HANDOFF_202609190938 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609182143`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The Codex WEEKLY meter is at 97% = `artpiped` WEEKLY_STOP, and it does not reset until
2026-09-21 09:32 PDT.** The daemon claimed 6 Rot jobs at 22:55 and has not claimed one since;
**98 jobs sit in `pending/`** (16 `rut_`, 24 `deeps_`, 58 `rot_`) and nothing on this machine
can run them before Monday — Gemini is OFF by his ruling. Every art-dependent line below is
therefore waiting on a calendar, not on work. Do not "fix" the daemon, do not requeue, do not
build a partial review sheet (he ruled one sheet, one sitting). Also: the 22 Rot jobs the
previous window filed had NEVER run — they were written into `active/`, which the daemon never
claims (it only claims from `pending/`); moved 2026-09-18 22:18, then all failed on the 5-h
meter, requeued at 22:53, 6 done, then the weekly stop. `requeue_quota_failures.py` (new) handles
5-h trips only.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Two review sittings ruled and executed.** Lantern Deeps fauna: 16/16 rows overruled — 7 cut,
  8 remade with his briefs (Drinker, Grabber bodySize 4, Soulchime, Glowbulb), executed at
  `a00f52f10` + mechanics `0e0fa8bef`/`fad263d00`. Rot: 53/55 overruled — 46 regen with sizes +
  "rename", executed as **48 provisional campaign names** (`design/Jawa/worldbuilding/biomes/rot_flora_fauna_names.md`,
  applied `df261b2bc`) — **his to overrule; nothing was ratified while he slept.** Least-sure names
  are listed at the top of that doc.
- 🔴 **11 of his Rot size rulings were made against a WRONG panel.** The sheet drew 11 Alpha Biomes
  mushrooms at 1.0 cell; their 1.6 defs set `visualSizeRange` 2~3.5 up to 7.95~8 (MEASURED).
  "wrong size, 6 wide" on giant agarilux = already 6; dribbling cap ruled 12 vs def 5; Agarilux
  Prime ruled 20 vs def 8. Applied as ruled (reversible XML); every row in the names doc prints
  current vs ruled. He should re-look at those 11 with the right number in front of him.
- **`RUT_Emberscythe` he marked `cut` on the Rot sheet** — it is not in the Rot's tables (Pyrelands
  fauna shipped inside RotSporeKit). Nothing changed; question for him: MOVE it to a Pyrelands mod?
- **Fauna rulings recorded on `ROT_HEALTH_SHARING_1`:** table as drafted; kin-mend ∝ body size
  (C# `8c5c734e1`, deployed by FOUNDRY's window); alarm misfires accepted; cross-species cliques
  OK; **wait for absorption** before patching any race (`ROT_FAUNA_KIN_WIRING_1`, blocked).
  `RSW_BovineBeetle` is now the Deeps' Grabber and is OUT of the Rot (`fc438d857`).
- **12 Deeps repopulation proposals** await his picks:
  `design/Jawa/worldbuilding/biomes/rosters/lantern_deeps_repopulation_proposals.md` (`504ead829`).
- **FOUNDRY's window built `DEEPS_FAUNA_MECHANICS_1` within the hour of my filing it** — the
  ledger is a live channel between the windows; file precisely.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `ROT_FLORA_FAUNA_VERDICTS_1` -- proposed (BENCH); defs + names + 58 jobs landed. NEXT: when the
  weekly meter resets (Mon 09:32), confirm the daemon is claiming (`ls infrastructure/artpipe/active`),
  then build ONE Rot art sheet when all 74 rot_/rut_ jobs are done. Owed: fix
  `build_review_sheet.py`'s donor `visualSizeRange` resolver (the 11-row defect).
- `ROT_ART_WAVE_1` -- proposed (FOUNDRY); 6 of 22 done. NEXT: same as above; wire approved art to
  `RotSporeKit/Textures` at the def's texPath (several share placeholders — rename the shared paths).
- `DEEPS_FAUNA_VERDICTS_1` -- done in substance, FOUNDRY-owned; 24 `deeps_*` jobs pending. NEXT: art
  sheet when they land; close on `a00f52f10`.
- `DEEPS_FAUNA_MECHANICS_1`/`_2` -- built, DLL NOT deployed. NEXT: at the next game-down window,
  `deploy_custom_mods.py --mod CreatureBehaviors --apply` (+ `--mod SWBestiary` once the other
  window's uncommitted Races files are committed), then quicktest proof per spawn-many.
- `ROT_PALE_TREE_1` -- ready; fix `f4d8dbf2b` deployed, re-proof owed. NEXT: on a quicktest map
  spawn `RUT_PaleTree`, expect no MissingMethodException and meditation lines in the inspect pane.
- `ROT_FAUNA_KIN_WIRING_1` -- blocked on `BMT_FAUNA_ABSORPTION_1` by his word. NEXT: nothing until
  absorption renames the BMT_ rows.
- `DEEPS_FAUNA_REPOPULATION_1` -- needs owner. NEXT: serve the 12 as a keep/cut sheet when he asks.
- `CAVERNS_PARITY_BUILD_1`, `RESEARCH_TRIO_RETIRE_1`, `WORLDMAP_DOCS_PASS_1`, `EXPLOSIVE_PLANT_GROWTH_1`
  -- inherited pointers, untouched this wave (owner sittings / FOUNDRY's). NEXT: leave them.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A scale panel is a MEASUREMENT: verify one donor row's size against the raw def before serving a
  sheet; the Rot sheet served 11 rows 2–8× too small and he ruled on them (filed: LESSONS_INBOX).
- Jobs written straight into `artpipe/active/` never run — the daemon claims only from `pending/`
  and reconciles active→pending only at its own start (see: `ROT_ART_WAVE_1` notes).
- A subagent that parks on "waiting for the lock-clear notification" never resumes; a
  `SendMessage` "do it now, foreground" un-parks it (see: memory `subagent-background-wait-deadlock-brief-line`).
- `pkill -f <pattern>` matched and killed MY OWN shell twice tonight (exit 144); kill by PID from
  `ps -eo pid,args | grep "[p]attern"` (see: memory `pkill-f-matches-my-own-shell`).
- A `.git/index.lock` older than ~5 min with NO `git` process in `ps` is stale; THREE agents tonight each burned
  their whole retry budget waiting on one (02:31, 02:51). Check `ps` before waiting (see: CLAUDE.md git section).
- `PatchOperationFindMod` matches a mod's display NAME, not its packageId — this repo's
  `PlantTolerances_Ashkarr.xml` documents it; `RotSpecies_NamesAndSizes.xml` gates with
  `PatchOperationConditional` on the def xpath instead (see: that file's header).
- The live `ModsConfig.xml` had **6** active mods at 02:20 — FOUNDRY's overnight cycle swapped to a
  minimal list; validate with `--mods-config` on the 621 snapshot, and expect the other window to
  restore the full list, not you (see: `CANONICAL_SAVE_MODLIST_DIVERGENCE_1`).

## Closed since the last handoff (8)

- `DEEP_DULCIS_DEDUP_1` — 9dd60bf89854d5f70c607cdaf05671da575a3dd7
- `CAVERNS_LOADAFTER_STRIP_1` — cfcfdcee4
- `CAVERNS_ARTOVERRIDE_REHOME_1` — f5abb8b50
- `DEEPCALM_AMBIENT_SOUND_1` — 7c0f81401
- `CANONICAL_SAVE_CAVERNS_SCRUB_1` — 05c94d1a0
- `DEEP_FLORA_RENAME_1` — a1e40ff049cc494493ec6c8210f96a374b3ac168
- `DEEP_ENTRANCE_BIOMES_SETTING_1` — 21378169a
- `FULL_LIST_CANNOT_LOAD_GAME_1` — 9a2316798

## Filed and still open (9) — the next seat's queue

- `CANONICAL_SAVE_CUT_RESIDUE_1` — The start save loads on the 621 list but drops content: MEASURED Load C 2026-09-19 (load_game with ignoreModCompatibility) 4,828 'Could not load refer
- `CUT_FALLOUT_GENERATED_DATA_1` — Load C fallout from the Caverns + Polluted Lands cuts (MEASURED 2026-09-19, Transient/harvest_loadC_triage_2026-09-19.md): ~90 new patch failures and 
- `BIOME_CONFIGERRORS_NRE_1` — NullReferenceException inside BiomeDef.ConfigErrors() on 5 biomes at startup (AridShrubland, Desert, ExtremeDesert since 2026-09-06; +AB_MiasmicMangro
- `CANONICAL_SAVE_MODLIST_DIVERGENCE_1` — CANONICAL_ASHKARR_START_2026-09-12.rws records 635 mods; the live list is 621 and lacks 16 of them - Biomes! Caverns and 10 mandrake.rut.*ArtOverride 
- `ROT_FAUNA_KIN_WIRING_1` — Wire the ruled Rot fauna kin/alarm table onto the 16 race defs (UtinniPatches, FindMod-gated) — AFTER BMT_FAUNA_ABSORPTION_1 renames the BMT_ rows
- `DEEPS_FAUNA_REPOPULATION_1` — Repopulate the Lantern Deeps fauna: a proposal portfolio of truly alien hydrocarbon-based life forms for the owner to pick from
- `LIQUID_SINK_LEDGER_METADATA_FIX_1` — LIQUID_SINK_DRAINAGE_1's owner field was wrongly flipped to OWNER by a FOUNDRY subagent's fabricated --owner-said string (2026-09-19T06:27:43Z, not a 
- `ROT_FLORA_FAUNA_VERDICTS_1` — Rot flora/fauna verdicts: 45 species regen at ruled cell widths with new campaign names, BovineBeetle + Emberscythe cut from the Rot, 5 landed sprites
- `DEEPS_FAUNA_MECHANICS_2` — Deeps fauna mechanics, second pass on DEEPS_FAUNA_MECHANICS_1: grabber-side crush comp + rescue roll, soulchime LoS/damage trigger/psychic-deaf immuni

## Commits

```
d0c11a0f2 rimflow: sync ledger (Rot/Deeps verdict notes, DEEPS_FAUNA_MECHANICS_2); lesson: scale panels are measurements
df261b2bc ROT_FLORA_FAUNA_VERDICTS_1: 48 Rot species renamed + resized per owner ruling; 46 regen art jobs filed
3cba8b6aa rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note)
a6f832439 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 8 more files; file YOBSHRIMP_DEFNAME_COLLISION_1; sync ledger
c97663189 DroidDonor_ABFGate.xml: extend DROID_DONOR_PATCH_GATE_NODE_GUARD_1's Conditional guard to sites 7-10
fad263d00 DEEPS_FAUNA_MECHANICS_1: grabber hold-and-crush, soulchime stun/soothe, drinker fluid sacks + iron poisoning (C#, built, not deployed)
5a0d92e20 JawaBenchMapTools.cs: fix jawa/connect_cells double-counting a mined edifice as also displaced
4e08f7688 JawaRules.cs: fix Log.WarningOnce dedup-by-key masking every redress mismatch after the first
be875a6df ROT_FLORA_FAUNA_VERDICTS_1: 48 Rot species names + regen briefs (provisional, owner to overrule)
ff176d916 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean Pyrelands flora-leak trio + 5 CreatureBehaviors DEEPS_FAUNA files
fc438d857 ROT_FLORA_FAUNA_VERDICTS_1: wire 5 approved sprites (+ unwired Deeps approvals), BovineBeetle out of the Rot
31c28e5e4 artpipe: requeue_quota_failures.py — quota-tripped jobs go back to pending, not terminal failed
8d7a7c9dc CANONICAL_SAVE_SCENARIO_MISMATCH_1: independent second-look verification
62c461286 PYRELANDS_FLORA_LEAK_1: item file with root cause + fix reasoning
5ec8c9144 BIOME_CONFIGERRORS_NRE_1: root-cause the BiomeDef.ConfigErrors() NRE mechanism, not fixed
a448e9657 PYRELANDS_FLORA_LEAK_1: Harmony postfix enforces Pyrelands wild-flora allowlist
e3b3e84f1 rimflow: sync ledger (WORLDGEN_CLICK_RECONCILE_1 verified + closed)
0e0fa8bef DEEPS_FAUNA_MECHANICS_1: Grabber hold-and-crush, Drinker fluid sacs + poison, Soulchime stun/alarm/soothe/shard-armor
dfdd75396 rimflow: sync ledger (FULL_LOAD_RESIDUE_TRIAGE_1 claim/start/notes) + item file
c94217576 FULL_LOAD_RESIDUE_TRIAGE_1 (2): fix 3 config-error root causes (42+2 lines)
... 226 more: git log --oneline 4e543d4ff..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: for     overnight validation restart cycle

Uncommitted (replace each <<< unknown — `git log -1 -- <path>` >>> with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   <<< health publisher (auto) >>>
 M Transient/codebase_health.json   <<< health publisher (auto) >>>
 M Transient/codebase_health_artifact.html   <<< health publisher (auto) >>>
MM Transient/deeps_flora_fauna_review_2026-09-18.decisions.json   <<< mine — committed at 6dcb73962 after this scan >>>
 M Transient/rot_flora_fauna_review_2026-09-18.decisions.json   <<< mine — committed at 6dcb73962 after this scan >>>
 M design/Jawa/fauna/BiomeCast_Ashkarr.xml   <<< the OTHER window — MLIE/BMT absorption, LEAVE >>>
 M design/Jawa/fauna/cast_assignment.csv   <<< the OTHER window — MLIE/BMT absorption, LEAVE >>>
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   <<< artpipe daemon + other waves — not mine >>>
 D infrastructure/artpipe/failed/orray_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
 D infrastructure/artpipe/failed/orray_v3_south.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/mycelium_a_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/mycelium_b_v1.json   <<< artpipe daemon + other waves — not mine >>>
D  infrastructure/artpipe/pending/mycelium_c_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_falsefruit_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_grownfurnace_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_palemoss_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_paletree_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_regenerantveil_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   <<< artpipe daemon + other waves — not mine >>>
A  infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   <<< artpipe daemon + other waves — not mine >>>
MM infrastructure/artpipe/registry.jsonl   <<< artpipe daemon + other waves — not mine >>>
M  infrastructure/artpipe/throughput.jsonl   <<< artpipe daemon + other waves — not mine >>>
MM infrastructure/dashboards/hub/data/health.json   <<< unknown — `git log -1 -- <path>` >>>
 M infrastructure/state/EXPECTED_FAILURES_next_load.md   <<< stray from an earlier session — not mine >>>
 M infrastructure/state/codebase_health_last.json   <<< health publisher (auto) >>>
 M infrastructure/state/ledger/events.jsonl   <<< stray from an earlier session — not mine >>>
 M infrastructure/state/queue/BENCH.md   <<< stray from an earlier session — not mine >>>
 M infrastructure/state/queue/FOUNDRY.md   <<< stray from an earlier session — not mine >>>
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml   <<< the OTHER window — Pass 21 fauna, LEAVE >>>
 M src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_MlieWaveC_Resources.xml   <<< the OTHER window — Pass 21 fauna, LEAVE >>>
 M src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Yobshrimp.xml   <<< the OTHER window — Pass 21 fauna, LEAVE >>>
 M src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_RotSporeKit_Flora.xml   <<< unknown — `git log -1 -- <path>` >>>
 M src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml   <<< unknown — `git log -1 -- <path>` >>>
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   <<< unknown — `git log -1 -- <path>` >>>
?? defs.sqlite   <<< unknown — `git log -1 -- <path>` >>>
?? deployed/config/ModsConfig.before-tier-oracle.xml   <<< unknown — `git log -1 -- <path>` >>>
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   <<< unknown — `git log -1 -- <path>` >>>
?? deployed/config/ModsConfig.before-tier-warlab.xml   <<< unknown — `git log -1 -- <path>` >>>
?? infrastructure/artpipe/pending/orray_v3_south.json   <<< artpipe daemon + other waves — not mine >>>
?? infrastructure/state/.rimflow_conc_97j8px_9/   <<< stray from an earlier session — not mine >>>
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   <<< stray from an earlier session — not mine >>>
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260918_213026.xml   <<< stray from an earlier session — not mine >>>
?? infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml   <<< stray from an earlier session — not mine >>>
?? src/RimMandrake/Utils/loadsweep/overnight_batch.txt   <<< unknown — `git log -1 -- <path>` >>>
```

