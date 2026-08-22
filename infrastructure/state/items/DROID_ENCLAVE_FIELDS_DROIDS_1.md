## spec
`DROID_RACES_APPLIED_TO_KINDS_1` (`9b01b10`) gave the four `Jawa_Droid_*` kinds droid
races and turned `useFactionXenotypes` off. Deployed to the game copy, VERIFIED in sync.
**Defs are parsed only at startup, so nothing here is visible without a load.**

| kind | label | race |
|---|---|---|
| `Jawa_Droid_Grunt` | labour droid | `OuterRim_ImperialLaborDroid` |
| `Jawa_Droid_Heavy` | security droid | `OuterRim_KXSecurityDroid` |
| `Jawa_Droid_Specialist` | medical droid | `OuterRim_ProtocolDroid` |
| `Jawa_Droid_Leader` | First Speaker R-41 Rell | `OuterRim_SuperTacticalDroid` |

⛔ **`<xenotypeSet Inherit="False" />` in `JawaFreeDroidEnclaves.xml` is frozen on purpose**
(owner, 2026-08-19). The empty set is the fix working. Do not report it as a defect.

⚠️ All four now carry `MayRequire="Neronix17.OuterRim.DroidDepot"`, as do the seven group
maker entries naming them. **On a reduced mod list without Droid Depot the faction's Combat
and Settlement groups are EMPTY and it fields nobody** — that is the chosen guard, not a
fault. Check this on the full 578 list, not the minimal one.

## verify
Spawn each of the four into `Jawa_FreeDroidEnclaves` and read the pawn's race.

## criteria
- **0 of 4 come out `Baseliner`**, and each wears the race in the table above.
- A `Combat` group generated for `Jawa_FreeDroidEnclaves` contains **no Human**.
- ⚠️ Contestable call, flagged not buried: `Jawa_Droid_Specialist` is labelled *"medical
  droid"* and wears a **protocol** chassis, because there is no medical droid in the
  Humanlike set — 2-1B and FX have no Humanlike `ThingDef` in this stack. If the owner
  would rather the label moved than the chassis, *"attendant droid"* costs nothing.
