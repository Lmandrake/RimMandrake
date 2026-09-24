# FOUNDRY_REBOOT_HANDOFF_202609241247 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609240404`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**RimSage works from this Desktop session** (confirmed live, not assumed — it answered
real queries this window) even though standing doctrine says it's Mac-laptop-dead;
that doctrine was never wrong about the Mac, it just never said the Desktop is fine.
Use it freely here for engine-source questions instead of reasoning from docs — it
closed a genuine multi-week-open question (impassable-biome wildAnimals spawning) in
one call this session.

## What the owner should see

- **Codex is down for the whole artpipe daemon** — `wss://chatgpt.com/backend-api/codex/responses`
  answers 403 Forbidden, every job attempted for hours has failed the same way. This
  needs a Codex CLI re-login on the Windows side (interactive OAuth, his account) —
  not something this seat can fix. Everything art-generation-dependent is stalled
  until then; non-art queue work continued in the meantime.
- **`CANON_CREATURE_REGEN_1` wave 4 fidelity sheet is served and waiting on his
  grade** — 7 creatures (Boma/Dewback/Insectomorph/Shiro/Vornskyr/Whisperbird/Zakkeg),
  `Transient/canon_regen_wave4_2026-09-23/sheet.html`. Two facings (dewback/south,
  insectomorph/east) are still backfilling behind the Codex outage.
- **`SHOKKWEAVE_SOLE_SOURCE_1`'s full live behavioral proof (wake-on-approach,
  butchery) was deliberately NOT attempted** on the canonical save — it was
  mid-encounter (mechanoids + HuttCartel present) and advancing ticks near that
  risked resolving real combat. Needs a throwaway quicktest session instead.
- **`DONOR_DEFS_PORT_TO_OURS_1` found a real gap**: `sarg.alphaanimals` (102 roster
  entries, the second-largest donor) has no retirement plan at all, unlike the other
  two large donors (`MLIE_FAUNA_ABSORPTION_1`, `BMT_FAUNA_ABSORPTION_1`).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `CANON_CREATURE_REGEN_1` — wave 4 sheet served, `needs=owner`; NEXT: collect the owner's fidelity grades, then deploy the graded-keep textures into their ArtOverride mods.
- `SETTLEMENT_VISIT_LOOP_1` — mod+debug-actions confirmed live, blocked on tile-selection/picker-dialog bridge tooling; NEXT: either OS-screenshot+click the manifest picker after `jawa/world_tile_map_generate` on an empty tile, or add a non-interactive debug-action overload taking a manifest defName directly.
- `SHOKKWEAVE_SOLE_SOURCE_1` — wake-up fix confirmed re-parsed live, `needs=owner` on two build decisions (trader-stock tool vs. accepting source proof; new colonist harvest-job for emergent-Shokk); NEXT: get those two decisions, then run the deferred behavioral proof on a throwaway quicktest map.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `jawa/get_defs` falsely reports "No def TYPE named" for genuinely-loaded custom Def subclasses — verify via a debug-action census instead (filed: LESSONS_INBOX, rimbridge traps.md).
- 15 artpipe jobs were `bad_job_file` (a real prompt-wording bug: "top-down" trips the facing-camera validator), not the Codex outage — check `worker_status` before assuming every stuck job shares the day's outage (filed: LESSONS_INBOX).
- `requeue_quota_failures.py` only matches the literal "hit your usage limit" sentence — running it during a genuine auth/connectivity outage (403s) just cycles jobs through a second guaranteed-fail attempt for no benefit (see: `CANON_CREATURE_REGEN_1` 2026-09-24 note).

## Closed since the last handoff (2)

- `KOTOR_CRYSTAL_GENSTEP_DRIFT_1` — c8511162068538eafe378364ddf0bada54af8e3a
- `DESERT_PORT_PLACEHOLDER_ART_1` — 502b24794ce8f04c3571891b2c704e391c0de7d6

## Filed and still open (6) — the next seat's queue

- `WEBWORK_FLORA_ROSTER_1` — Build the 16 invented Webwork flora defs (webwork_flora_roster doc) + Utinni tooke-trap patch (ruled kept-low); the 6 donor cuts stay PROPOSED pending
- `WEBWORK_FAUNA_ROSTER_1` — Build the 5 invented Webwork fauna defs (Quarrok/Vennick/Skennet/Cravvet/Sivvern, Sivvern flies for real) + execute the 3 ruled donor cuts; JewelBeetl
- `OLLATHRIX_OWNER_SPECIES_1` — Build RM_Ollathrix (one race one kind, owner-and-nest doc S1) with mechanisms in mandrake.rm.webwork and the Wyyyschokk skin patch in mandrake.rsw.sho
- `WEBWORK_NEST_EGG_ECONOMY_1` — Build the Webwork nest + egg economy: nest on EVERY map, re-lay 20-30d while mother lives, RM_OllathrixEgg, Wildsteam egg bounty (S6 rulings 2,3,4)
- `SHOKK_SKIN_SHRINK_1` — Shrink mandrake.rsw.shokk to the Wyyyschokk skin patch; move bound/spit/sun-scald/emergent-spawn mechanisms into mandrake.rm.webwork (S6 ruling 1, inv
- `WEBWORK_EGG_BLACKMARKET_BUILD_1` — Build the ruled egg black market: Cartel caravan kind + Bazaar broker channel, tradeability-All patch with leak check, The Reckoning quest family with

## Commits

```
166e4f6f2 ROSTER_DEAD_BMT_NAMES_SWEEP_1: live-resolution check done (Desktop session); KORRUM_ART_REGEN_1 flagged
79381caa5 artpipe: fix 15 jobs stuck on a real prompt-authoring bug, unrelated to the Codex outage
8d14e1abe KORRUM_ART_REGEN_1: correct stale quota-block framing, same Codex outage as everything else
0dfb6955f ROSTER_DEAD_BMT_NAMES_SWEEP_1: impassable-biome engine question resolved via RimSage
861af9273 Ledger sync: DESERT_PORT_PLACEHOLDER_ART_1 closed, prose moved to closed/
502b24794 DESERT_PORT_PLACEHOLDER_ART_1: wire the remaining 13 species' already-generated art, fix surra grass
7bd1b7376 Ledger sync: KOTOR_CRYSTAL_GENSTEP_DRIFT_1 closed, prose moved to closed/
c85111620 KOTOR_CRYSTAL_GENSTEP_DRIFT_1: stale block cleared, fix confirmed already shipped 2026-09-19
4ee90b4bc DONOR_DEFS_PORT_TO_OURS_1: fold in a stray 2026-09-20 census that never reached the item file
1d0675375 Ledger sync: egg black-market design closed ruled; two successors filed
f50288aad Webwork egg black-market: seven S5 rulings recorded in the design doc
174b2d01d SETTLEMENT_VISIT_LOOP_1: mod+debug-actions confirmed live; real live-proof blocker is tile-selection/picker tooling, not the mod
600f3b1cf Webwork egg black-market and assassination quests: design draft (WEBWORK_EGG_BLACKMARKET_1)
4b3119d76 CANON_CREATURE_REGEN_1 wave 4: sheet served (7 creatures); Codex 403 outage recorded across 151 requeued jobs
65be1619c Webwork follow-up rulings 9-10: all flora dispositions and the JewelBeetle cut ruled
42640ab2f SHOKKWEAVE_SOLE_SOURCE_1 sixth pass: wake-up fix re-parse confirmed live, full behavioral proof deferred
e587f3a00 WEBWORK_DESIGN_SITTING_1 prose to items/closed on close
513ec8d7b Ledger sync: Webwork sitting closed, six successor items filed
1868e1928 Webwork sitting ruled: eight S6 rulings recorded, dispositions marked, grammar row updated
17ae09f82 Webwork sitting: flora and fauna rosters written (WEBWORK_DESIGN_SITTING_1)
... 5 more: git log --oneline 3516080ce..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-24T05:42:47Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   -- ambient, health-publisher regen output, nobody's edit
 M Transient/codebase_health.json   -- ambient, health-publisher regen output, nobody's edit
 M Transient/codebase_health_artifact.html   -- ambient, health-publisher regen output, nobody's edit
 M infrastructure/artpipe/registry.jsonl   -- ambient, artpipe daemon (background, continuous)
 M infrastructure/artpipe/throughput.jsonl   -- ambient, artpipe daemon (background, continuous)
 M infrastructure/dashboards/hub/data/health.json   -- ambient, health-publisher regen output, nobody's edit
 M infrastructure/state/codebase_health_last.json   -- ambient, health-publisher regen output, nobody's edit
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   -- pre-existing (2026-09-11), not this window
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   -- pre-existing (2026-09-21), not this window
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   -- other in-session work (COLD_LOAD_RUN_SHEET_4), not this queue-work stretch
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   -- other in-session work (rustcathedral enable), not this queue-work stretch
```

