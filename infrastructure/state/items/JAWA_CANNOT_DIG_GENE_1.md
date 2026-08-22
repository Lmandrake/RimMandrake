## spec
🔴 **OWNER'S RULING, already on file — lever (b)** in
`items/the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07.md`:
*"Gene stays as specced — `disabledWorkTags: Mining` on `MandrakeJawa`, so no Jawa digs by
hand and no Jawa operates a deep drill. The laser is taken out of the `Mining` work type so
a Jawa can run it."* Original ruling: *"they should not be able to mine ore, though some
other races still can. And the mining laser should be able to do this very well."*

**The laser half shipped 2026-08-21** (`DRILLTURRET_IS_A_SHOOTING_JOB_1`, `fe0064c`):
`OperateDrillTurret` is now `workType Hunting`. **This item is the other half.**

⭐ **A gene and not a `ScenPart`, and the reason is the ruling itself.** A designator ban is
colony-wide and would stop a recruited non-Jawa mining too — but the owner said *"some other
races still can."* A gene is per-pawn, so it delivers that exactly, **and it reaches enemy
Jawa factions**, which nothing else buys.

⚠️ **`disabledWorkTags: Mining` here, NOT an aptitude** — and that is not inconsistent with
`JAWA_CANNOT_FARM_GENE_1` taking the aptitude. The two differ because the WorkTags enum
does: `PlantWork` is the only plant tag and it drags `PlantCutting` (so no wood), while
`Mining` covers the `Mining` work type and nothing else. Farming needed a soft lever because
a hard one had collateral. Mining does not.

**Do:** author a `GeneDef` in
`src/Jawa/RimMandrake_StarWarsRaces/Defs/GeneDefs/`, modelled on Biotech's
`ViolenceDisabled` — the only shipped gene of this exact shape (`disabledWorkTags Violent`,
`biostatMet 3`, `biostatCpx 1`). Add it to `MandrakeJawa`; genes 36 → 37.

⛔ **NO NEW ART.** Owner, 2026-08-21: *"NOT produce any art please!!!"* Reuse an `iconPath`
a **shipped** gene already uses — that is proof it resolves. 🔑 Do **not** check for a loose
PNG and conclude one is missing: Biotech's gene icons are not loose files, and *missing
views are not missing art*.

⚠️ **The design depends on Jawa being capable of VIOLENT work**, because the drill turret is
now `Hunting`, whose workTags include `Violent`. Measured 2026-08-21: none of `MandrakeJawa`'s
genes disables any work tag. If that ever changes, the turret silently becomes unusable.

## verify
- `validate_patch.py --defs --live` clean on both files
- `MandrakeJawa` carries the new gene exactly once; gene count 37; no duplicates
- the gene's `iconPath` is one a shipped GeneDef already uses
- ⛔ zero files added under any `Textures/`
- ⛔ `MandrakeJawa.xtp` unchanged, and repo and live copies still byte-identical
- **assert no OTHER MandrakeJawa gene disables a work tag**, or the Hunting turret breaks

## criteria
CHECK, next load: a Jawa colonist's **Mining** work is greyed out as incapable and they
cannot be assigned to a deep drill — but they **can** be assigned to a drill turret. A
recruited non-Jawa on the same colony mines normally.
