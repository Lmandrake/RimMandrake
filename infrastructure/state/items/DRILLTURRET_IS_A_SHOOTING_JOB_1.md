## spec
🔴 **OWNER, 2026-08-21 22:39:** *"And I still like shooting for the laser, please make it so."*
Confirms his 21:53 instinct after being shown the measured cost.

`JAWA_SCENARIO_PARTS_1` §2 puts `disabledWorkTags: Mining` on a `MandrakeJawa` gene. The
drill turret exists so a Jawa can still mine **by machine** — but
`OperateDrillTurret`'s `WorkGiverDef` carries `workType = "Mining"`, so that same gene would
bar them from operating it. Re-point the work type.

⛔ **AUTHOR NOTHING AND COMMISSION NO ART.** `DrillTurret` is a whole shipped mod —
*MiningCo. DrillTurret (Continued)* — with `ResearchDrillTurret`, `Blueprint_DrillTurret`,
`Frame_DrillTurret`, `Techprint_*`, a `JobDef` and `DrillTurret.JobDriver_OperateDrillTurret`,
and its own art. `JAWA_SCENARIO_PARTS_1` used to claim no such def existed; it was wrong.

**Do:** a `PatchOperationReplace` on
`Defs/WorkGiverDef[defName="OperateDrillTurret"]/workType`, `Mining` → **`Hunting`**.

**Why `Hunting` is what "shooting" means here, measured.** Across every Core/DLC
`WorkTypeDef`, exactly one carries the Shooting skill:

    Hunting    relevantSkills ['Shooting','Animals']   workTags: Violent, Hunting, Shooting, ManualSkilled...
    Crafting   relevantSkills ['Crafting']             workTags: ManualSkilled, Commoner, Crafting

⚠️ **The cost, accepted with the ruling rather than discovered later:** `Hunting` carries
`Violent`, so a pawn incapable of violence cannot operate the turret, and the job sits in the
Hunting work column alongside hunting animals. The owner was shown this and chose shooting.

⛔ **Do NOT patch vanilla's `Drill` WorkGiver, and change nothing else of DrillTurret's.**
One field of someone else's mod, and nothing more.
⚠️ Guard it with `MayRequire` / `PatchOperationFindMod` on the DrillTurret mod — a
`PatchOperationReplace` whose xpath matches nothing **logs nothing**.

## verify
- `validate_patch.py --defs --live` clean, and the op reported as **MATCHING**, not merely
  well-formed
- in the LIVE def set, `OperateDrillTurret`'s `workType` reads `Hunting` and not `Mining`
- ⛔ vanilla's `Drill` WorkGiver is unmodified
- ⛔ `git status` shows zero added files under any `Textures/`

## criteria
CHECK, next load: a Jawa colonist carrying the mining-disabled gene can be assigned to, and
will operate, a built drill turret. A pawn incapable of Violence cannot — that is the ruling
working, not a defect.
