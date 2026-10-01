# BENCH_REBOOT_HANDOFF_202610010838 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610010527`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The north-star pipeline has never produced a GREEN, and Graffiti is the pilot that will. All three trial checklists are VALIDATED (Graffiti 10 bars; FlowWorks 38+5, hash 34e2ec9f…; Pyrelands 19+1, hash eca2fe9b…), Graffiti is WIRED (10/10 bars carry `shows=`; mock run is 10/10 *state* PASS, not GREEN), and the fast driver lives in `src/RimMandrake/Utils/northstar_driver/`. It has never run live. Every bridge call shape in it is assumed, so the first live run is a calibration run: expect wrong shapes and fix them before reading any bar as FAIL. Plans: `design/RimMandrake/northstar_trials/<Mod>_trial_plan.md`.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **I switched off the retired Pits mod** in the live `ModsConfig.xml` on his card (612 → 611 active; backup in `infrastructure/state/modlists/ModsConfig_before_pits_off_*.xml`). The deployed `Mods\Pits\` folder and `ModsConfig.FULL.LATEST.xml` still carry it (`PITS_STALE_DEPLOY_COLLISION_1`).
2. **GPT stood in for his read on two validations**, on his typed word (Pyrelands and FlowWorks; his sentences are on the validate events). Rejected GPT points are in each plan's GPT section if he wants to overrule.
3. **The Abyss rename is done** (`a534284e4`). The canonical save's 1,135 `RUT_ForsakenCrags` tiles are now dead references until the repaint, which he accepted when he asked for the full rename now.
4. **Graffiti's walk has one stale hashed subsection** ("what this checklist refuses today"). Replacing it needs his word to re-validate; the text is in plan §5.7. He also has an open question: should his one-time sheet review lapse when the art, DLL or judge changes (on `GRAFFITI_NORTHSTAR_TRIAL_1`)?
5. **The repo-rename scan:** 764 old-path BREAKS in 443 files, so the `Rimworld` symlink must stay for now (`Transient/repo_rename_scan_2026-09-30.md`). `D:\Luke\dev\Rimworld-wt-sightblock` is an orphan folder he could delete.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1` — WIRED and textures deployed, but the DLL is NOT deployed (the game held the lock) and FOUNDRY holds the bridge for its own full-list session; NEXT: once `rimflow bridge who` says free, stop the game, `deploy_custom_mods.py --mod Graffiti --apply`, swap to the `graffiti_solo` tier, cold load, run `python.exe src/RimMandrake/Utils/northstar_driver/cli.py preflight` then `run --mod Graffiti`, and fix wrong call shapes first.
- `GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1` — 5 JawaBench tools are needed for exact variant coverage and site checks (thing_graphic, spawn_variant, running_mods, glow_at, site_state); NEXT: build them per skills/rimbridge-companion in the same game-down window as the DLL deploy.
- `BLACKCRAGS_BEDAZZLE_SITTING_1` — volley turn 1 is ruled and ticketed (the Abyss); turn 2 has not been asked; NEXT: put a card to the owner on etchfall, cutting/keeping the two echoes (gust turbines, lamps-as-crops), housekeeping (cindermare/skarnix to the free mod, switch on ghorrumak/zhurrakor, Lightfall's bottom) and whether the cryptid "Forsakens" keep that name.
- `FLOWWORKS_NORTHSTAR_TRIAL_1` — VALIDATED; wiring not started; NEXT: dispatch a Sonnet agent on `FLOWWORKS_NORTHSTAR_WIRE_1` and `_SITE_PREP_1` per the plan (new liquid bridge tools are listed there).
- `PYRELANDS_NORTHSTAR_WIRING_1` — VALIDATED; not wired; `selftest_walklint` now fails on the walk's `mandrake.rm.biomes` ids; NEXT: teach walklint the composed biomes id (`MODCHECK_COMPOSED_BIOMES_LIST_1`), then wire the bars.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Subagents cannot pass the rimflow owner-said flag: the provenance guard cannot see the owner's chat from a subagent, so the seat window must run owner-quoted verbs itself, or the quote lands in a note. (filed: LESSONS_INBOX)
- A `git worktree add` on /mnt/d takes over 2 minutes; run it in the background, never inline under a 120 s timeout. (filed: LESSONS_INBOX)

## Closed since the last handoff (8)

- `CONTAGION_BEDAZZLE_SITTING_1` — c16e11a6f
- `WASTELAND_BEDAZZLE_SITTING_1` — c16e11a6f
- `BLUEDESERT_BEDAZZLE_SITTING_1` — c16e11a6f
- `FLOODEDCANYON_BEDAZZLE_SITTING_1` — c16e11a6f
- `PYRELANDS_NORTHSTAR_VALIDATE_1` — 2691d0c47
- `FLOWWORKS_NORTHSTAR_REVALIDATE_1` — e890abfc4
- `ABYSS_FULL_RENAME_1` — a534284e4
- `GRAFFITI_NORTHSTAR_WIRED_1` — 541852456

## Filed and still open (20) — the next seat's queue

- `REPO_RENAME_SYMLINK_RETIRE_1` — Retire the Rimworld -> RimMandrake symlink: repoint every old-path reference, then remove the link
- `BLACKCRAGS_BEDAZZLE_SITTING_1` — Black Crags (was Forsaken Crags) bedazzle sitting - program row 11: review, roster fill, four-turn volley, ticket-out; rename executes here behind the
- `NORTHSTAR_FAST_DRIVER_1` — Ultra-fast Python bridge driver for north-star validation (core built, live proof owed)
- `NORTHSTAR_PHASE_LADDER_1` — North-star phase ladder standard: DRAFT, VALIDATED, WIRED, GREEN min, GREEN full, SHIPPED
- `PYRELANDS_NORTHSTAR_WIRING_1` — Wire every Pyrelands bar with shows= and fix suite bugs (composed mandrake.rm.biomes packaging)
- `MODCHECK_COMPOSED_BIOMES_LIST_1` — modcheck builds a test list from the retired dev packageId for composed biomes (no closure, biome silently absent)
- `PYRELANDS_GREEN_MINIMAL_1` — Pyrelands north star GREEN on the pyrelands tier (pre-flight gates, 2-ring scratch sites, K-pooled census)
- `PYRELANDS_GREEN_FULL_1` — Pyrelands north star GREEN on the full list (fresh full-list mapgen on a scratch save, never quicktest)
- `PYRELANDS_SHIP_READINESS_1` — Pyrelands SHIPPED rung: Ashwallow/Emberscythe art, code review CLEAN, settings gate mechanics, composed deploy
- `GRAFFITI_NORTHSTAR_TRIAL_1` — Graffiti north-star trial: pipeline pilot to first GREEN (parent of WIRED/GREEN_MINIMAL/GREEN_FULL/SHIP)
- `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1` — Graffiti: GREEN on MINIMAL+graffiti via fast driver, owner sheet review
- `GRAFFITI_NORTHSTAR_GREEN_FULL_1` — Graffiti: GREEN on the owner's FULL list (fresh launch, full-list driver mode)
- `GRAFFITI_NORTHSTAR_SHIP_1` — Graffiti: SHIPPED - art complete, settings superb, CLEAN, stamped, deployed
- `ABYSS_DARK_BUILD_1` — The Abyss: the Dark (real air, heat clears it), the Unveiling, ghorrumak storm call, strength slider
- `ABYSS_HIDDEN_SHIP_PROBES_1` — The Abyss: hidden-ship cover; probe droids still come and must be avoided
- `ABYSS_GHARREK_BUILD_1` — New creature gharrek, the gust-feeder (RM_Gharrek)
- `ABYSS_DURRGAK_BUILD_1` — New creature durrgak, the placer (RM_Durrgak)
- `ABYSS_KRIZZAK_BUILD_1` — New flying creature krizzak, the light-thief (RM_Krizzak)
- `ABYSS_ETCHCAP_BUILD_1` — New plant etchcap, the gourmet fungus (RM_Etchcap)
- `GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1` — JawaBench tools the Graffiti trial cannot fake: thing_graphic, spawn_variant, running_mods, glow_at, site_state

## Commits

```
693bc1927 Ledger: close GRAFFITI_NORTHSTAR_WIRED_1, file GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1
13fb839a0 Ledger: claim/start STILLSAND_SKELETONS_TRACKS_1
3843ba1f4 STILLSAND_SKELETONS_TRACKS_1: giant skeletons, bone harps, corpse-to-skeleton, horizon dust
0fc53d244 Codebase health artifacts refresh
0637a9e78 Codebase health artifacts refresh
f5f328ab5 Ledger: close STILLSAND_GLASS_LENS_CHAIN_1 at 86e2b0fc9
86e2b0fc9 STILLSAND_GLASS_LENS_CHAIN_1: drift yields glass sand; sun furnace, lens bench, solar ovens
1f7cc6f8e Ledger: close STILLSAND_RETURN_RITUAL_1 at c1aa656de, file STILLSAND_RETURN_REMAINDER_1
541852456 northstar: Graffiti plan + site primitives + graffiti_solo tier; chains record prep failures
787bdf840 Graffiti: rebuild DLL with .srchash stamp
41f534dfc Ledger: claim and start STILLSAND_RETURN_RITUAL_1
c1aa656de STILLSAND_RETURN_RITUAL_1: the Sun-Debt water ledger and the Return
7d9efe9de Ledger: close STILLSAND_STILL_COOLING_DRAUGHT_1 at 568fa9d2c
654b1e2f9 Graffiti suite: count the whole mark pool, all 6 settings, shows= on all 10 bars
e3fcd0d48 Ledger: close STILLSAND_WIND_SUN_BEARING_1 at 4398421d4, file STILLSAND_SUN_GOGGLES_ART_1
568fa9d2c STILLSAND_STILL_COOLING_DRAUGHT_1: cooling draught hediff
fe24f7a64 Graffiti: wire 45 generated textures (37 defs); only Glyph_Bloodfeeding still has no art
808225f8e Ledger: close STILLSAND_MIRAGE_CONDITION_1 at 6106d6a2d, start wind lock
4398421d4 STILLSAND_WIND_SUN_BEARING_1: dune wind locked to the sun bearing
8a5973d92 Ledger: close PYRELANDS_NORTHSTAR_VALIDATE_1 at 2691d0c47
... 45 more: git log --oneline ae5d24058..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: FREE    since 2026-10-01T01:26:33Z

Working tree clean apart from untracked `Transient/`.

