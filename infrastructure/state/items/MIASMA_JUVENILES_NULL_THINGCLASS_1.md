## Spec
All 7 juvenile ThingDefs in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_MiasmaNurseryJuveniles.xml`
(`RSW_MeeJuv`, `RSW_FaaJuv`, `RSW_LaaJuv`, `RSW_YobshrimpJuv`,
`RSW_SiltLampreyJuv`, `RSW_RustNipperJuv`, `RSW_OpeeSeaKillerJuv`) load with
a **null `thingClass`** — confirmed new on the 2026-09-10 restart (absent
from the prior load's log entirely) via
`python.exe src/RimMandrake/Utils/check_config_errors.py`:

```
Config error in RSW_FaaJuv: has null thingClass.
Config error in RSW_FaaJuv: animal has trainability = null.
Config error in RSW_FaaJuv: renderTree is null.
Config error in RSW_FaaJuv: RSW_FaaJuv has no combatPower.
```
(x7, one block per species — same four lines each)

This is the "whole ThingDef discarded" failure class (`MANYWATERS_COLOR_SUPPORT_1`
hit the same signature from a different cause). A reviewing subagent
(`ab04b4d40052f3631`, tonight) read this exact file in full and found it
"clean as-is" against the file's OWN documented design (the life-stage-
capping mechanism) — it did not catch this runtime symptom, because a
static XML read can't see def-inheritance resolution failing.

Each of the 7 ThingDefs uses `ParentName="RSW_<name>" MayRequire="mandrake.rsw.swbestiary"`,
where `RSW_<name>` is a real, active ThingDef (`Name="RSW_<name>"`, itself
`ParentName="AnimalThingBase"`) defined in
`src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Scalefish.xml`
(confirmed present, confirmed the mod is active in the live 579-mod
ModsConfig.xml). The matching PawnKindDefs use the identical pattern.

**Not yet root-caused.** MayRequire on a top-level Def node is a supported,
normal mechanism (unlike the `<Operation MayRequire>` trap documented on
`MODLIST_RESTORE_AND_BATCH_DEPLOY_1`) and the mod IS active, so a MayRequire
mismatch doesn't fit — if it failed, the def wouldn't exist at all, not
exist-with-null-thingClass. Cross-mod `ParentName` resolution is normally
load-order-independent (defs are pooled from all active mods before
inheritance resolves), so the fact this Juv file lives in a DIFFERENT mod
(`UtinniPatches`) than its parents (`SWBestiary`) shouldn't matter either —
but hasn't been proven not to matter here specifically.

A bridge live-query attempt (`jawa/get_defs`) to read the actual merged def
back was abandoned rather than guessed further at its parameter shape
(CLAUDE.md: never guess a field) — whoever picks this up should read that
tool's real schema first (`--list-tools`), not repeat the guess.

## Verify
```
PROVE   the actual merged ThingDef for RSW_FaaJuv (or any of the 7) via
        jawa/get_defs (real schema, not guessed) or a fresh RimSage def-dump
        index that includes tonight's mods
EXPECT  either thingClass resolves correctly once queried properly (meaning
        the ConfigError is itself a false/misleading signal), or a genuine
        inheritance-resolution failure is visible in the merged def
LIES    a clean validate_patch.py run says nothing about this -- it's a
        runtime inheritance-resolution symptom, not an XML-patch-matching one
```

## Criteria
- [ ] Real root cause identified (not guessed) via a live/fresh-dump def read
- [ ] Fix applied to all 7 species uniformly (same mechanism, same fix)
- [ ] `has no combatPower`/`trainability = null`/`renderTree is null`/
      `has null thingClass` all clear on the next load for all 7
