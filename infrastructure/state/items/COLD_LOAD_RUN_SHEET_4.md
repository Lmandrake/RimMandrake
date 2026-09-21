## spec
Six entries, each a reading that could not be taken offline. See history for
the full original text (entries 1-3 filed 2026-09-06T22:10:31Z, 4-6 added
2026-09-06T23:03:44Z).

## FOUNDRY, 2026-09-07 -- worked on a fresh full 598-mod load

**ENTRY 1 (FLUID_CANAL_DEBUG_SURFACE_1) -- INCONCLUSIVE, different reason than
expected.** `jawa/type_visibility typeName=RimMandrake.FlowWorks.FlowWorksDebugActions`
returned `assemblyFound: false` (not the theorized `typeInAllTypes=false AND
getTypesThrew=true AND typeInitializerNull=true`). Checked why: `mandrake.rm.flowworks`
is not in `ModsConfig.FULL.LATEST.xml` at all -- confirmed via `deploy_custom_mods.py
--mod FlowWorks`, which reports "in sync (9 files)" but "not enabled in ModsConfig".
The mod is correctly deployed, just off. This is consistent with `FLUID_CANAL_MECHANIC_1`
(the underlying feature) still being unclosed/proposed -- FlowWorks is not
campaign-ready yet, so its absence from the real list looks intentional, not a
regression. The GenTypes.AllTypes recovery-path theory remains untested; needs
FlowWorks actually enabled on some load to test at all.

**ENTRY 2a (DEV_LOG_AUTOOPEN_SUPPRESS_1) -- PASS, confirmed live + by screenshot.**
`jawa/log_autoopen_suppress action=get` -> `installed: true, suppressed: true`
(default). `action=testerror` -> `verdict: "PASS - the engine attempted an
auto-open and it was suppressed."`, `delta: 1`. `jawa/clear_ui` +
`rimworld/take_screenshot` immediately after: the screen-targets payload lists
exactly one window (`Verse.ImmediateWindow`, a small coordinate-readout overlay,
192x25px) -- no Debug Log window present. Manual-open-still-works path NOT
independently verified this pass (no bridge tool reaches the debug menu's log
icon directly; not chased further -- low risk given the code path is
documented as separate).

**ENTRY 2b -- NOT properly testable this session; blown ordering.** The test
needs the FIRST bridge call of a session to be non-`jawa/` (to catch whether
JawaBench's lazy init has fired before any `jawa/` tool runs in a "plain play"
session). Entry 1's `jawa/type_visibility` call came first by necessity of this
run's own ordering, so that window was already gone before 2b could be tried.
**This doesn't need a full load** -- it's a JawaBench-init question, testable
on a cheap minimal-list quicktest restart, done FIRST thing next time before
any other jawa/ call.

**ENTRY 3 (BEHEMOTH_TEXTURE_MISSING_LIVE_1) -- NOT REACHED.** `rimworld/
start_debug_game_ready` crashed the process during quicktest generation before
a colony/pawn existed to test on (see NINEFOLD_DEBUG_GAME_READY_CRASH_1, noted
separately -- a known, already-diagnosed OOM ceiling on this mod count, not a
new bug). Still owed: spawn/select a pack Behemoth carrying cargo (not in
portrait) and confirm the `JawaBehemoth_fPack` texture-missing log line is gone.

**ENTRY 4 (ARMOURY_SWMODS_MODNAME_GAP_1) -- confirmed indirectly, not by the
literal live readback envisioned.** `jawa/get_def` and `jawa/get_defs` do not
surface `ThingDef.tools[]` (melee) or a projectile's `damageAmountBase`
(ranged) -- both are non-scalar/nested and outside what either tool reads
(`get_defs`' `tools` field came back as bare type-name stubs `["Tool","Tool","Tool"]`,
not values; confirms the gap `rimbridge-companion`'s own skill already names).
Fell back to: (a) the deployed `Armoury_MeleePower.xml` genuinely sets
`tools/li[label="edge"]/power` to `36` for `guy762_vsword_echani` (read directly
off the file actually shipped to `Mods/Armoury/Patches/`); (b) this load's
Player.log has ZERO failure lines naming either `guy762_vsword_echani` or
`RSW_Low_Red_Blaster_Bolt` (the only Armoury patch failures present are the
three already-known-accepted `PatchOperationFindMod` misses for absent optional
mods -- Dungeon Pack, Outer Rim Core, Lightsaber). Absence of a failure for
these two ops, on THIS load, combined with the shipped value being 36/24, is
good evidence but not the literal in-game stat readback the item's verify
block asked for -- a companion tool reading `tools[]`/`projectile.damageAmountBase`
would close this properly; not built this pass (would cost another restart
cycle for a single-purpose read).

**ENTRY 5 (ARMOURY_ABSORBED_KOTORCORE_DUPES_1) -- CLEAN.** Zero `Could not
resolve cross-reference` lines anywhere in this load's log (not just zero
naming a KOTOR_ def -- zero total).

**ENTRY 6 (config errors) -- CLEAN.** `check_config_errors.py` against this
load's fresh log: 17 lines / 11 distinct, all matched against
`config_error_baseline_2026-09-06.json` (6 ours-accepted, 2 ours-open-bug,
1 third-party-cosmetic, 2 third-party-unattributed). No lines outside the
baseline. The 598 vs 594-596 baseline delta is measured clean, not just assumed.

## Side benefit: fresh full-mod-set def dump captured
Armed before this load (`echo all > DefDump/dump_request.txt`); captured at
`2026-09-07T08-59-33Z` (709MB, 598 mods) BEFORE the crash, since the dump
writes at main-menu/startup, not at quicktest time.
`src/RimMandrake/Utils/refresh.py` picked it up (`defs.sqlite` now current,
79663 defs). This is a verification-tier dump (not the frozen `official`
baseline, which stays owner-only at 584 mods, 2026-08-29).

## verify
```
PROVE   the six per-entry outcomes above, each with its own evidence
EXPECT  entries 5, 6, 2a fully close; 1 needs FlowWorks enabled somewhere to
        even test; 2b and 3 need one more session (2b: first-call-ordering on
        a cheap quicktest; 3: past NINEFOLD_DEBUG_GAME_READY_CRASH_1's known
        OOM risk, or a campaign-save load instead of the debug quicktest
        generator); 4 needs a new companion tool for tools[]/projectile
        damage to close properly
LIES    treating "no failure line in the log" as equivalent to "the patch
        definitely applied" -- it is evidence, not the same class of proof
        as reading the resolved value back
```

Leaving `doing` -- three of six entries (2b, 3, 4's full form) still owed.

---

## 🔴 NEXT LOAD — assembled by BENCH, 2026-09-21, on the owner's sequencing ruling

He ruled: **"Fix mapgen first, then one load for everything."**

⚠️ **The premise of that ruling has since dissolved, and he has not been told.** It was put
to him as *"map generation is currently BROKEN on the full list"*. It is not: the crash log
`Transient/crash_mapgen_20260920T1900.log` records **19 mods** in its own
`Initializing new game with mods:` line — the `desertplants` tier — and FOUNDRY had already
diagnosed and closed `MAPGEN_NRE_FULL_LIST_20260920_1` at `fa21d88857a`. ⇒ **There is no
mapgen fix to wait for.** The operative half of his ruling is the half that still stands:
**ONE batched load, not several.** Do not spend a load on any single entry below.

⚠️ **Deploy before loading.** Several entries are built but undeployed because the game was
running (`deploy_custom_mods.py --mod <name>`, plan first, then `--apply`).

| # | entry | what it proves | state going in |
|---|---|---|---|
| 1 | `PYRELANDS_DEFNAME_RENAME_1` | `RM_Pyrelands` resolves; no red errors from the 3 renamed C# string literals | built + 3 assemblies rebuilt clean at `84d42c63b`, **NOT deployed** |
| 2 | `OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` | GelatinousSlime loads | ⛔ **not yet in `ModsConfig`** — activate it BEFORE the load, not after. AshkarrFlora is already active (re-measured: 619 active mods) |
| 3 | `TITANOSLIME_SLIME_BIOME_1` | the spec's seven §8 gates, with growth now **PERMANENT** (his one overturned default) | deployed, 0 validation errors; the permanent-growth change is still owed in the build |
| 4 | `FOUNDERS_IMPORTER_OWED_1` | all 6 founders carry `Wimp` | `FOUNDER_IMPORTER_LIVETEST_2026-09-21.rws` built and verified offline. **One load and it closes** |
| 5 | `BRIDGE_SELECT_NONCOLONIST_PAWN_1` | "does not refuse on faction" | DLL deployed, all 3 tools in the live tool list. 🔑 **Does NOT need this load** — a ~90 s beastmechanics quicktest closes it, and `PORTED_BEAST_MECHANICS_REBUILD_1` 4–6 with it |
| 6 | `WORLD_LABEL_SIZE_HIERARCHY_1` | the 71 resized labels read as a hierarchy | offline pass in flight; needs the bridge (`world_features_set` + `world_commit`) and a NEW save slot, ⛔ never the canonical save |

### Order, and the trap in it

1. 🔴 **Entry 5 FIRST and separately, on the cheap list** — it needs no cold load and a
   22 s minimal-list run buys it. Spending a 15–21 minute load on it is pure waste.
2. Activate GelatinousSlime, deploy everything owed, THEN launch once.
3. ⚠️ **`launch_and_wait.sh` exits 0 on TIMEOUT at 280 s** and a full-list cold load has
   measured **21 minutes**. Its exit code is not the signal — grep the log for the bridge
   line.
4. Harvest the whole Player.log before touching anything, and write the strings each entry
   will be decided by BEFORE launching.

⛔ **Do not add a seventh entry without deleting one.** This sheet's own history is four
previous loads where entries 3+ were "NOT REACHED".
