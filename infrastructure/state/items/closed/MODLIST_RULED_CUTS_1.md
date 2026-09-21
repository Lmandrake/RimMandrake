
## spec
Owner rulings, bench sitting 2026-09-12 (cards + verbatim in the ledger notes):
1. Deactivate in ModsConfig.xml (takes effect NEXT load; back up ModsConfig to
   Transient/ first, per standing practice):
   - dubwise.dubsperformanceanalyzer.steam  (profiler out of the play stack)
   - fuu.bloodanimations                    (only combat-pile cut he picked)
   - arkymn.slowerpawntickrate              (keep taranchuk.performanceoptimizer)
2. Jurassic retirement (mlie.jurassicrimworlddinosaursonly, ruled 2026-09-05,
   still live): FIRST run the donor-art texPath reachability check flagged in
   Transient/MODLIST_COMPLEXITY_AUDIT_shortlist_2026-09-12.md (retextures bind
   by texPath — reading-rimworld-graphics skill); only then deactivate.
3. Mo'Events (mlie.moevents): zero all MO_ event baseChances via its settings
   NOW; the mod itself stays until RUT_SCAVENGEREVENTS_BUILD_1's port lands.
⚠️ Do NOT touch: facial-animation pile, giddyup, runandgun, yayoscombat3,
meleeanimation — infrastructure/state/facts/protected_mods.json (owner ruling).
ModsConfig is written by three uncoordinated writers — rimworld-start-prep
skill before editing.

## verify
Diff ModsConfig before/after: exactly the ruled packageIds deactivated, nothing
else moved; protected list untouched; next cold load's Player.log shows none of
the three cut mods loading and no new Config errors.

## criteria
The three cuts are out of the live list, Jurassic's retirement is executed or
its texPath check documented as blocking, MoEvents chances are zero, and no
protected mod was disturbed.

## 2026-09-13 (FOUNDRY) — all four actions done, one live check owed on next load

**Jurassic reachability check, done first**: the 8 absorbed creatures live in
`mandrake.rsw.swbestiary` (`RSW_Absorbed_*.xml`), each declaring its own
`texPath` under `swanimals/absorbed/<Name>/` — 27 loose PNGs confirmed
physically present in the repo AND `deploy_custom_mods.py --mod SWBestiary`
confirmed already in sync (1571 files) — none reference Jurassic's own
donor-mod texture path. Safe to deactivate; nothing depends on it staying up.

**ModsConfig.xml, 4 packageIds deactivated** (backed up first to
`Transient/ModsConfig_before_MODLIST_RULED_CUTS_1_20260913_001920.xml`,
diffed after — only the `activeMods` line changed, 594 → 590 entries, exactly
these four gone and nothing else moved):
`dubwise.dubsperformanceanalyzer.steam`, `fuu.bloodanimations`,
`arkymn.slowerpawntickrate`, `mlie.jurassicrimworlddinosaursonly` (executes
the already-ruled retirement, closing the gap between the 2026-09-05 ruling
and disk this item's own audit source flagged). Cross-checked against
`infrastructure/state/facts/protected_mods.json` — no overlap. Game was up
throughout; per `rimworld-start-prep`'s own §3 ("RimWorld does NOT rewrite
ModsConfig.xml on exit"), this is safe and simply takes effect next load.

**MoEvents, chances zeroed via a patch, not settings**: `rimworld/
get_mod_settings` on its live settings surface
(`mod-settings:mlie.moevents:93488948b97c9e6d`) returned an empty object
(`topLevelSettingCount: 0`) — nothing there for a runtime settings write to
reach, and no `Config/Mod_2035143365_*.xml` has ever been written for it
either. Read the donor's own `Defs/IncidentDef/IncidentDefs.xml` directly
instead (own copy in the Workshop folder, not guessed): 🔴 a naive grep found
13 `MO_` defNames, but `xml.etree.ElementTree` parsing (which correctly
skips XML comments, unlike grep) found only **10 real, live ones** — three
(`MO_Recovery`, `MO_Calm`, `MO_GoodRest`) sit entirely inside the donor
author's own `<!--` comment blocks ("Bugged", "Not working correctly right
now") and never load. Wrote
`src/RimUtinni/UtinniPatches/Patches/MoEventsChancesZeroed_RuledCut.xml`,
`PatchOperationReplace` on all 10 real `baseChance` fields to `0`, gated by
`PatchOperationFindMod`. `validate_patch.py --defs <Data+Workshop+Mods>
--mods-config <live>`: 0 errors, 0 warnings, all 10 operations report exactly
1 live match each. Deployed (`deploy_custom_mods.py --mod UtinniPatches
--apply`), verified in sync.

**Still owed**: this item's own `## verify` asks for confirmation in a fresh
Player.log that none of the three cut mods load and no new Config errors
appear — that needs an actual restart, not done this pass (batching with
other game-up work rather than a solo restart for this alone, per standing
doctrine). Fold into the next full-list load's run-sheet: grep the fresh log
for the three deactivated packageIds (expect zero) and confirm 0 Config
errors from the new MoEvents patch. Left `doing`.

## 2026-09-13 (FOUNDRY) — game went DOWN mid-session, live list had drifted; restored and re-baselined

Owner announced the game down. Found the LIVE `ModsConfig.xml` at only
6-36 active mods — another window's `modcheck` tool had composed a
MINIMAL+mods-under-test list for its own validation and never restored it
before the game closed. Restored to the stored `FULL.LATEST` (594), then
re-applied this item's own 4 deactivations on top (diffed clean — exactly
those four gone, nothing else moved), then `modlist_swap.py --capture-full`
so the ruled cuts are now baked into `FULL.LATEST` itself (590 active) as
the permanent baseline — a plain `--restore` will no longer silently
resurrect the three cut mods. **The next load will be the one this item's
own verify check can finally read** (a Player.log captured during tonight's
session predates both this deploy and the earlier deploy-blocked window, so
it does not count — checked, correctly not used to close this item).
