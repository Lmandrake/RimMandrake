## spec
Found 2026-09-08 live-verifying `DROIDWORKS_APPARELMONEY_MISSING_1`'s fix.
Adding `<apparelMoney>` to every generated `PawnKindDef` (sized per family
against real `RSW_DW_Module_*` armor `MarketValue` floors, see that
generator's own comment) was necessary but **not sufficient** — every
Droidworks pawn still spawns with `apparel: []`, confirmed live even for
kinds carrying real `apparelTags` and a budget well above their cheapest
matching item's price.

Root cause, read from the engine source
(`RimWorld/PawnApparelGenerator.cs:686`, `GenerateStartingApparelFor`), not
guessed:
```csharp
if (!pawn.RaceProps.ToolUser || !pawn.RaceProps.IsFlesh || pawn.RaceProps.IsAnomalyEntity)
{
    return;
}
```
This is the method's FIRST line and its ONLY call site
(`Verse/PawnGenerator.cs:1169`). `RaceProperties.IsFlesh => FleshType.isOrganic`
(`Verse/RaceProperties.cs:340`). Every Droidworks race carries
`RSW_DW_Race_Base`'s `<fleshType>RSW_DW_FleshType_Droid</fleshType>` with
`<isOrganic>false</isOrganic>` (`Defs/Races_Base.xml`, a deliberate ruling
from `droid_system_build_spec.md §1`, NOT something to reverse here) — so
`IsFlesh` is `false` for every DW pawn, confirmed by reading the LIVE field
straight off the bridge (`jawa/list_pawns`/`jawa/pawn_get` both expose
`isFlesh` directly): every spawned kind across Battle/Heavy/Labour/Probe
families read `isFlesh: False`. The apparel-generation method therefore
returns on its first line for every Droidworks pawn, before it ever reads
`apparelMoney` or `apparelTags` — the field being absent was a real, correctly
diagnosed defect, but fixing it alone changes nothing a player would see.

This is the SAME class of bug this codebase has already hit and fixed once:
`Races_Base.xml`'s own comment on `isOrganic:false` documents that
`PawnComponentsUtility.CreateInitialComponents` also gates on
`RaceProps.IsFlesh` (leaves `pawn.relations` null) and Droidworks already
ships a Harmony postfix for that — `Source/Droidworks/Patch_ShouldHaveNeed_Power.cs`
(actually gates `ShouldHaveNeed`, a different vanilla method with the same
"isOrganic:false breaks a Humanlike-intelligence assumption" shape). No
existing patch touches `PawnApparelGenerator` — grepped
`src/RimStarWars/Droidworks/`, `src/RimUtinni/` and `vendor/mod_sources/`
(including `AlienRace-HAR-main` and `VanillaExpandedFramework-main`, the two
mods in the minimal test list most likely to touch pawn apparel generation)
for `GenerateStartingApparelFor`/`IsFlesh`/`PawnApparelGenerator` — VFE Core
has ONE postfix on this method (`PawnApparelGenerator_GenerateStartingApparelFor.cs`)
but it only recolors apparel already generated; it does not bypass the
early-return. Nothing bypasses the gate today.

One live anomaly NOT explained by this diagnosis, recorded rather than
suppressed: on the FIRST test round (before this root cause was found), a
spawned `RSW_DW_OuterRim_GNKDroid` (isFlesh false, no `apparelTags` at all,
`apparelMoney` 0~20 at the time) came back wearing a vanilla
`Apparel_Broadwrap`. Every subsequent test (15 spawns across 4 kinds/families
with real tags and budgets well above their own cheapest matching item)
came back with `apparel: []`, 15/15 — a result that is astronomically
unlikely under a "budget roll was just unlucky" theory (each kind's own
cheapest match was affordable on a comfortable majority of rolls) and fully
consistent with the `IsFlesh` gate applying uniformly. Whoever picks this up:
the gate theory explains 15/15 empty results and the source code exactly; it
does not explain the one Broadwrap. Re-check it if it reproduces after the
fix below ships — it would mean something else is ALSO going on.

## fix shape (not yet built)
A Harmony patch (new `.cs` under `Source/Droidworks/`, wired into
Droidworks' existing bootstrap alongside `Patch_ShouldHaveNeed_Power.cs`)
that lets `PawnApparelGenerator.GenerateStartingApparelFor` run for
`RSW_DW_FleshType_Droid` pawns despite `IsFlesh` being false — a transpiler
or prefix that skips/adjusts the `IsFlesh` half of the guard specifically for
that fleshType (never disable the `ToolUser`/`IsAnomalyEntity` halves, and
never touch `isOrganic` itself — that is `DROIDWORKS_FAMILY_LAYER_1`/
`droid_system_build_spec.md`'s ruling, not this item's to reverse). Requires
a C# build + `deploy_custom_mods.py --apply` (assembly — game must be DOWN to
write it) + a restart to verify, same cycle as this item's own live check.

## verify
```
PROVE   spawn a representative sample per family (Battle/Heavy/Labour/Probe
        at minimum — the kinds this item's parent already identified:
        RSW_DW_KotORDroidBad_hk50, RSW_DW_KotORDroidBad_ADMkI,
        RSW_DW_KotORDroidGood_KM1HMD, RSW_DW_KotORDroidGood_KX12UPD are
        already confirmed to have real matching apparelTags + adequate
        apparelMoney), read jawa/pawn_get's apparel list
EXPECT  the same combat-tier kinds that came back apparel: [] in this item's
        parent now show at least one RSW_DW_Module_* item worn on a majority
        of a 4-5-pawn batch per kind; RSW_DW_OuterRim_GNKDroid (apparelMoney
        pinned to 0~0, no apparelTags) stays apparel: [] — the patch must not
        accidentally widen the untagged-kind bare guarantee the parent item
        just established
LIES    a single spawn passing is not proof (RNG); checking only that the
        patch loaded (Harmony patch report, no exception in Player.log) is
        not proof either — GenerateStartingApparelFor can run cleanly and
        still produce apparel: [] for unrelated reasons (this item's own
        parent hit exactly that with a too-low apparelMoney on the first
        pass) — only a live spawn batch showing worn RSW_DW_Module_* items
        closes this
```

## criteria
The IsFlesh gate no longer silently discards Droidworks apparel generation:
a live spawn of the four kinds named above shows real module gear worn on a
majority of a small batch, and `DROIDWORKS_APPARELMONEY_MISSING_1` can then
be re-verified and closed against this fix.
