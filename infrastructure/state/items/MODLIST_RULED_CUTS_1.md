
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
