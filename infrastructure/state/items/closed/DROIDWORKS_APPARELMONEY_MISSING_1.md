## UPDATE 2026-09-08 (second pass, post-ISFLESH-GATE) — CLOSED
`DROIDWORKS_APPAREL_ISFLESH_GATE_1` closed (`8c274947`), unblocking this item.
Fresh live spot-check (5/kind, minimal 25-mod list) before this pass: `hk50`
5/5, `ADMkI` 4/5, `KX12UPD` 5/5, `KM1HMD` 1/5 (re-batched 3/15 = 20%), `GNK`
control 0/5 correctly bare.

**KM1HMD root cause, read from source not guessed** — `guy762_DroidRace_KM1HMD`
is `CHASSIS_PLAN`'d `"astromech-labour"` (bucket -> family "labour",
`APPAREL_MONEY["labour"] = (500, 1400)`), but its own `apparelTags`
(`KotORDroidArmorT3_stuffable`, `KotORDroidArmorT3_miningdroid`) resolve ONLY
to KotOR Class III/"heavy" armor (`Absorbed_KotorDroidModules_Armor.xml`:
`RSW_DW_Module_DroidArmorHvy` $1250, `_env` $1750, `_impact` $6750). It is the
ONE kind in the whole "labour" family with T3 tags — every other labour kind's
tags resolve to genuinely cheap gear (`GE3LD` T1 -> $300, `KM1MD` T2 ->
$500/$750, both comfortably inside 500-1400). A budget capped at 1400 can only
ever afford the $1250 item, and only on rolls in the top ~17% of the (500,
1400) range (`(1400-1250)/(1400-500)=17%`) — that IS the measured ~20% hit
rate, not vanilla noise. Confirmed by grepping every "labour"-budget kind's
`apparelTags` for an `ArmorT3` tag across all three `PawnKinds_*.xml`: KM1HMD
Good/Bad are the only two hits.

**Fix**: `APPAREL_MONEY_KIND_OVERRIDE` in `gen_droidworks_defs.py` pins
`KotORDroidGood_KM1HMD` and `KotORDroidBad_KM1HMD` to the `"heavy"` tier's own
`(900, 2200)` — the same range `ADMkI` (also T3-tagged, floor $1250) already
clears at ~80% — instead of raising "labour" for `GE3LD`/`KM1MD`, who don't
need it. Regenerated; diff is exactly 2 changed lines (`500~1400` ->
`900~2200`) on the two `KM1HMD` `PawnKindDef`s, zero unrelated churn.

**Live-verify after the fix** (minimal 25-mod list, fresh restart, bridge
taken/released, god mode, `jawa/pawn_get` per spawn — never `list_pawns`):
`KM1HMD` (Good) x20 -> **14/20 (70%) wearing real `RSW_DW_Module_DroidArmorHvy*`**,
4/20 (20%) bare, 2/20 (10%) wearing ONLY a vanilla item (`Apparel_Burka` /
`Apparel_Broadwrap`) with no droid armor — up from the pre-fix ~20%. Regression
check, same session: `hk50` 5/5, `ADMkI` 4/5, `KX12UPD` 5/5, `GNK` control 0/5
— all unchanged from the pre-fix baseline, confirming the one-kind override
touched nothing else.

**The residual 2/20 vanilla-only stray is NOT this item's bug.** Read
`PawnApparelGenerator.CanUsePair`/`GenerateStartingApparelFor`/
`AddFreeWarmthAsNeeded` in full (RimSage): every code path that can add an
apparel item to a pawn with a non-empty `kindDef.apparelTags` either requires
the ITEM to carry a matching tag (`CanUsePair`, the main candidate pass) or
requires `apparel.canBeGeneratedToSatisfyWarmth`/toxic/vacuum resistance
flags — and `Apparel_Burka`/`Apparel_Broadwrap` have neither a matching tag
nor `canBeGeneratedToSatisfyWarmth` (both explicitly `false`, confirmed via
`get_def_details`). The one stray pawn inspected in full (`jawa/pawn_get`)
came back `faction: null`, `xenotype: Highmate`, `ideo: Matro-Spiritism`, a
real human name/backstory/traits — Droidworks kinds are deliberately
Humanlike (colonist-capable "reprogrammed droid" identity, per
`ABF_SynstructExtension.playerReprogrammableDronePawnKindDef`), so a
faction-less spawn rolling a real ideoligion and picking up that ideoligion's
own apparel convention is a SEPARATE, pre-existing vanilla-ideology
interaction, not an `apparelMoney`/`apparelTags` miscalibration — filing a
"fix" for it here would be guessing at a mechanism not yet read. Noted for
whoever next touches Droidworks identity generation; not filed as a new item
since it doesn't fail this item's own criteria (14/20 real gear, 0/5 GNK
control still correctly bare).

Player.log: 12 `Config error in` / 21 crossref lines after the restart, all
pre-existing (smeltable-armor warnings, missing content-mod defs on the
25-mod minimal list) — grepped by name, none mention `KM1HMD`, `apparelMoney`,
or any file this pass touched. Zero new errors.

**Criteria met**: every family-tier kind now carries a calibrated
`apparelMoney`; live spawns across five kinds (Battle/Heavy/Labour-outlier/
Probe/Power-control) show gear where intended (70-100% per real-tagged kind)
and bare skin where intended (0/5 GNK). Closing.

## UPDATE 2026-09-08 (live-verify pass) — blocked on DROIDWORKS_APPAREL_ISFLESH_GATE_1
`gen_droidworks_defs.py` now emits a per-kind `<apparelMoney>` (0,0 for any
kind with no `apparelTags` at all — RimWorld's `PawnApparelGenerator.CanUsePair`
only tag-filters `if (!apparelTags.NullOrEmpty())`, so a nonzero budget on an
untagged kind draws from the WHOLE apparel pool and dresses a droid in random
human clothes, measured live on `RSW_DW_OuterRim_GNKDroid`; a nonzero
family-tier value otherwise, sized against the real `RSW_DW_Module_*` armor
`MarketValue` floor each family's own tags resolve to). Diffed clean against
the pre-change committed XML (80 added `<apparelMoney>` lines, zero removed,
zero other changes) and this part of the fix IS live-verified: `bare skin
where not intended` now holds (GNK stayed `apparel: []` across a batch after
the fix, was previously dressed in a vanilla `Apparel_Broadwrap`).

`gear where the design intends it` is NOT yet live — 15/15 spawns across
Battle/Heavy/Labour/Probe kinds with real `apparelTags` and a budget
comfortably above their own cheapest matching item still came back
`apparel: []`. Root cause (read from engine source, not guessed):
`PawnApparelGenerator.GenerateStartingApparelFor`'s first line returns
immediately when `!pawn.RaceProps.IsFlesh`, and every Droidworks race is
`isOrganic:false` by an earlier, deliberate ruling — confirmed live,
`isFlesh: False` on every spawned DW kind via `jawa/pawn_get`. `apparelMoney`
is never even read. Full writeup, the fix shape, and the reopened verify
plan: `DROIDWORKS_APPAREL_ISFLESH_GATE_1`.

This item stays open/blocked rather than closing: its own criteria requires
a live spawn showing GEAR where intended, which does not hold yet.

## spec
Found 2026-09-08 while live-verifying `DROIDWORKS_MODULE_ABSORB_1` (B2). Three
Droidworks KotOR kinds spawned via `rimworld/execute_debug_action` `Spawn Pawn...`
came in with `apparel: []`, `equipment: []` — not missing modules specifically,
missing apparel entirely. `grep -n "apparelMoney"
src/RimStarWars/Droidworks/Source/gen_droidworks_defs.py` returns zero hits: the
generator that writes all 80 `PawnKindDef`s (`Defs/PawnKinds_*.xml`) has never
emitted an `<apparelMoney>` field on any of them. `apparelTags` are present and
correct (spot-checked against real absorbed apparel from B2), but vanilla
`PawnGenerator` will not spend anything on apparel for a kind with no/zero
`apparelMoney`, regardless of how many tagged items exist to match against.

This is upstream of, and blocks, every packet that expects a Droidworks kind to
visually carry gear: B2 (module apparel), B3 (heads — different slot, may be
unaffected, check), B9 (Primitive tier fabricated modules), and any faction
loadout work (C1) that expects a spawned droid to look armed/armored.

## verify
```
PROVE   spawn one kind per family (or a representative sample) via the bridge,
        read jawa/pawn_get's apparel list
EXPECT  a Battle/Heavy-family kind spawns wearing at least one tagged item once
        apparelMoney is set; a Labour/Protocol kind may deliberately stay bare
        if that is the intended design choice (check droid_verbs_decisions.json
        for any existing ruling on how "dressed" different families should be
        before inventing numbers)
LIES    checking only that apparelMoney now has a nonzero value in the XML —
        PawnGenerator's actual apparel-selection roll is probabilistic and
        budget-gated in ways a static read cannot confirm; a live spawn (ideally
        several, per this project's own "spawn many" discipline) is the only
        real proof
```

## criteria
Every concrete Droidworks `PawnKindDef` (or at minimum every Battle/Heavy/Power
family kind — the ones with combat-relevant apparelTags) carries an
`apparelMoney` FloatRange sized to its family/tier, verified by a live spawn
showing gear where the design intends it and bare skin where it doesn't.
