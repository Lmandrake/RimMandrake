## spec
Thin when filed — no spec/verify/criteria. Decided here (FOUNDRY, 2026-09-08):
enable `mandrake.rsw.droidworks` on the full 600-mod list alongside the donors
it will eventually retire (guy762.kotordroids, killathon.artificialbeings.syncore,
neronix17.outerrim.droiddepot, neronix17.asimov, mandrake.rsw.msedroidfix),
load it once, and read what a real full-list load says that a design pass
never would — texPath census, Harmony collision census, and Def.ConfigErrors().
This is the mod's FIRST EVER load on any mod list; it was authored but never
actually run.

## FOUNDRY, 2026-09-08 — enabled, loaded, three real bugs found and fixed

Inserted `mandrake.rsw.droidworks` into the live ModsConfig.xml after
`btd.gbp.shippack.kotor.vge` (last of the donor loadAfter targets; Droidworks'
own loadAfter is only Harmony + HumanoidAlienRaces). Restarted via Steam
(`steam.exe -applaunch 294100`, per rimworld-load-round's own launch rule).
Load landed clean — no "Recovered from incompatible or corrupted mods" dialog,
`Bridge token:` present, 600 mods held.

`harvest_log.py` + `check_config_errors.py` against the fresh log found:

1. **texPath census: CLEAN.** `texture path failures 0 = baseline 0`.
2. **Harmony idempotency: CLEAN.** `Harmony patch failures (C#) 1 = baseline 1`
   — the one pre-existing HAR/Universal-Pregnancy collision, unrelated to
   Droidworks. No new Harmony collision from coexisting with the donors.
3. **Def ConfigErrors: 181 lines, 164 distinct, ALL NEW** (baseline had 17).
   Every one attributed to Droidworks (`RSW_DW_*`). Three real, fixed bugs
   (a35e4f62):
   - `RSW_DW_DataSpike` (Items_Droidworks.xml): recipeMaker.skillRequirements
     used the List<SkillRequirement> `<li>` shape instead of
     RecipeDef.skillRequirements' real Dictionary<SkillDef,int> shorthand —
     threw ArgumentNullException, discarded the WHOLE ThingDef (`defdiscard`
     RED), and separately produced a "No SkillDef named li" cross-reference
     failure (`crossref` RED). Every OTHER recipe in this mod already used
     the correct `<Crafting>N</Crafting>` shape — this was the one exception.
   - `RSW_DW_PoweredDown` / `RSW_DW_RestrainingBolt` / `RSW_DW_BoltResentment`:
     declared `everVisible`, which does not exist on HediffDef in 1.6 (3
     Config errors, silently dropped every load since these defs were
     authored). Removed. `BoltResentment`'s C# comp header documents an
     intent ("player never sees a number") this field never actually
     fulfilled — flagged as a TODO next to its existing stub-mechanic TODOs;
     no real def-level hide-from-health-tab field exists to replace it with.
   - 80 `RSW_DW_` PawnKindDefs across PawnKinds_JDS/KotOR/OuterRim.xml never
     set `initialResistanceRange`/`initialWillRange` — required by vanilla
     for any humanlike-race PawnKindDef (160 of the 164 distinct lines, one
     resistance + one will line per kind). Fixed with a new self-scoped
     patch (`Patches/PawnKind_HumanoidDroidResistanceWill.xml`) adding the
     donor-convention placeholder (10~20 / 5~10, matching Droid Depot's own
     humanlike droid kinds — see Source/extraction.json) to every `RSW_DW_`
     kind missing them. **Flat placeholder, not a balance pass** — every
     kind gets the same range regardless of toughness; revisit if
     resistance/will ever becomes load-bearing for droids specifically.
   - `RSW_DW_ChargeDock`: the same "impassable, player-buildable... can be
     shot/seen over" warning already fixed for Dark.Signs elsewhere in this
     repo (`ThirdPartySignConfigErrors_Fix.xml`) — same
     `disableImpassableShotOverConfigError` field, applied directly since we
     own this def.

All four fixes validated offline against the live 600-mod def dump
(`DefDump/captures/2026-09-08T13-46-04Z`) via `validate_patch.py`: 0
errors/0 warnings on the three edited Defs files; the new patch matches
exactly 80/80 on both operations (full coverage, no double-hits, no
FindMod guard needed since its xpath only ever matches this mod's own
defs by `RSW_DW_` prefix). Deployed (`deploy_custom_mods.py --apply`).

**Not yet done:** a confirming restart. BENCH held the bridge for the whole
of this session's work (the one that was interrupted when this session first
restarted the game without checking — see ledger `note` around 2026-09-08
~13:26Z). Whoever next restarts on the full list should re-run
`check_config_errors.py` and expect these 164 lines gone, leaving only the
pre-existing 17-line baseline.

## verify
```
PROVE   the three fixed bug classes no longer log on a fresh full-list load,
        and no NEW RSW_DW_ Config error appeared that this pass missed
EXPECT  check_config_errors.py reports 0 NEW distinct lines against
        config_error_baseline_2026-09-06.json restricted to RSW_DW_*
        patterns; defdiscard/crossref finding no longer names
        Items_Droidworks.xml or "No SkillDef named li"
LIES    validate_patch.py's 0-errors verdict proves the XML is well-formed
        and the patch's xpath matches what it should — it does NOT prove the
        game accepts the values at runtime (a live ConfigErrors() pass is
        the only thing that closes this)
```
Leaving `doing` — the confirming restart is the one thing left, and it isn't
mine to force while BENCH is driving.
