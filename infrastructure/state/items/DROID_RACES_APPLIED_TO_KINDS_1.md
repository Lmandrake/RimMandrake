## spec
**Executes the ruling in `DROID_KINDS_NEED_A_RACE_1` (closed, DECIDE, 2026-08-21). Read that
item for the reasoning; this one is the edit.**

The four `Jawa_Droid_*` kinds declare `<race>Human</race>` against
`Jawa_FreeDroidEnclaves`' empty `xenotypeSet`, so the faction fields `Baseliner` 4-of-4.

**In `src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`, set `<race>`:**

| kind | its label | `<race>` | `<race>` line | `<useFactionXenotypes>` line |
|---|---|---|---|---|
| `Jawa_Droid_Grunt` | labour droid | `OuterRim_ImperialLaborDroid` | 391 | 395 |
| `Jawa_Droid_Heavy` | security droid | `OuterRim_KXSecurityDroid` | 408 | 412 |
| `Jawa_Droid_Specialist` | medical droid | `OuterRim_ProtocolDroid` | 425 | 429 |
| `Jawa_Droid_Leader` | First Speaker R-41 Rell | `OuterRim_SuperTacticalDroid` | 442 | 446 |

⚠️ Line numbers drift — **match on the `<defName>` above each**.

**And set `<useFactionXenotypes>false</useFactionXenotypes>` on all four.** A xenotype is a
Human-race concept; with a droid race the field asks the faction for something the race
cannot wear.

**All four are from `Neronix17.OuterRim.DroidDepot` and that is deliberate** — the faction
already `MayRequire`s exactly that package on its Trader group, so this adds **no new mod
dependency**. ⛔ Do not substitute a `guy762_DroidRace_*` equivalent for any of them.

⛔ **NO BATTLE DROIDS.** `B1`, `B2`, `BX Commando` and `MagnaGuard` read as *Separatist
army*; this faction is an enclave of **freed** droids and its roster reads as what its
members were built for and escaped from. Two of the four (`KXSecurityDroid`,
`ProtocolDroid`) are **already fielded by this faction** in its Trader group makers.

⛔ **DO NOT TOUCH `<xenotypeSet Inherit="False" />` in `JawaFreeDroidEnclaves.xml`.** It is
frozen on purpose (owner, 2026-08-19; marker written 2026-08-21) to stop
`apply_race_factions.py` refilling it at 1.000 and walking an Ugnaught out of a droid
enclave. The empty set is the fix working, not the bug. Leave the freeze marker intact.

⚠️ **One thing genuinely left to your judgement: the load-order guard.** These four
`PawnKindDef`s are named **without `MayRequire`** by `JawaFreeDroidEnclaves.xml`'s `Combat`
and `Settlement` group makers. If Droid Depot is absent, an unresolved `<race>` kills the
kind and those group makers then dangle. Choose the guard that is correct for this mod's
structure and **say which, and why, in the commit body**.

**Measured against `OFFICIAL-2026-08-21`** (`DefDump/defs.sqlite`, 578 mods /
`e0f11692cf69e516`, 24904 ThingDefs MEASURED): all four exist, spelled exactly as above, all
`intelligence: Humanlike`, all `race.body = OuterRim_HumanoidDroid`,
`thinkTreeMain = Humanlike`. Each carries **one** `lifeStageAges` entry against Human's six —
a single adult stage, so **no droid children**. That is correct and is not a defect to fix.
🔴 That measurement came from read-only SQL over the frozen capture, **not** from `rimsage`
— which answers "not found" for every modded def and reports it as a clean zero. See
`infrastructure/state/BUILDABLE.md` entry 8 before you verify any of this a different way.

## verify
```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml --defs
```
All four `<race>` values resolve to a `ThingDef`; **no `<race>Human</race>` remains on any
`Jawa_Droid_*` kind**; all four read `<useFactionXenotypes>false</useFactionXenotypes>`.

## criteria
Spawn each of the four into `Jawa_FreeDroidEnclaves` and read the pawn's race: **0 of 4 come
out `Baseliner`**, and each wears the race in the table. A `Combat` group generated for the
faction contains no Human.

## notes
⚠️ **One contestable call, flagged rather than buried.** `Jawa_Droid_Specialist` is labelled
*"medical droid"* and gets a **protocol** chassis, because **there is no medical droid in the
Humanlike set** — 2-1B and FX have no Humanlike `ThingDef` in this stack (33 Humanlike droids
measured across 636 `OuterRim_*` + `guy762_DroidRace_*` ThingDefs). Protocol is the nearest
attendant silhouette. If the owner would rather the label moved than the chassis,
*"attendant droid"* costs nothing. ⛔ **Do not wait on that** — build the table as ruled.

🔑 Smaller: *"R-41"* is an astromech-style designation on a leader given a Super Tactical
chassis. The only R-series humanlike droid in the stack is `guy762_DroidRace_R8009UD`, in the
other mod, which would break the one-mod rule. The name is the cheaper thing to change if it
ever grates.
