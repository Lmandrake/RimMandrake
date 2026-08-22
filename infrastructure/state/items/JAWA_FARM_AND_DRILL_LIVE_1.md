## spec
Two rulings landed offline and deployed on 2026-08-21. **Defs are parsed only at startup**,
so neither is visible without a load.

| change | file | commit |
|---|---|---|
| `MandrakeJawa` gains `AptitudeTerrible_Plants` (Plants −8), genes 35 → 36 | `RimMandrake_StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml` | `56d2b4d` |
| `OperateDrillTurret` `workType` `Mining` → `Hunting` | `Jawa_Patches/Patches/DrillTurret_ShootingJob.xml` | `fe0064c` |

⚠️ **`MandrakeJawa.xtp` deliberately does NOT carry the new gene.** The def and the owner's
saved editor artifact differ by exactly one gene, on purpose. Do not report that as drift,
and do not "fix" it by editing the `.xtp`.

⚠️ **`Hunting` carries the `Violent` work tag.** A pawn incapable of violence being unable
to operate the turret is the ruling working, not a defect. The owner was shown that cost and
chose shooting.

## verify
On the next load, spawn a `MandrakeJawa` colonist and read the Work tab and skills.

## criteria
- The Jawa's **Plants** skill shows the *terrible at* aptitude and is **NOT greyed out as
  incapable** — they can still be assigned to harvesting and to plant cutting, and can
  **chop wood**. 🔑 That last one is the whole reason an aptitude was chosen over
  `disabledWorkTags: PlantWork`; if wood-chopping is barred, the wrong mechanism shipped.
- A Jawa carrying the mining-disabled gene **can** be assigned to a built drill turret and
  will operate it.
- A pawn incapable of Violence **cannot** be assigned to it. Expected.
- ⛔ Vanilla's own `Drill` WorkGiver still reads `workType Mining` — only the turret moved.
