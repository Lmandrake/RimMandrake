# GENEPACK_MODS_PLUNDER_1 — done; findings

Report: `design/Jawa/worldbuilding/genepack_mods_plunder.md` (2026-09-06).

## outcome
- Mods identified: **Genepacks Injection** (TommasoBelluzzo.GenepacksInjection, ws 3784789591)
  and **More Consumables and Mutagens (Continued)** (Mlie.MoreConsumablesAndMutagens, ws 2042709249).
- 🔴 **Neither mod contains a single GeneDef** — Genepacks Injection is consumption-side
  (any genepack becomes directly injectable, no Biotech lab). The Rot's heat-generating
  gene must be AUTHORED; closest ready-made numbers: hediffs `IgniFurnace`/`IgniWarm`.
- **CMSlime + CatalystSerum chain = the living-gene-reactor pattern in vanilla comps**
  (milkable/egg/butcherable organism + temperature-spoiling hatcher item) — reusable for
  AB_GelatinousSuperorganism, with Genepacks Injection closing the consumption loop.
- **Oracalium / Ichorio** are ready-made Rot bargain templates; AmbrosiaTea/HearthBrew
  give the rot-destroys-live-tea template.
- UNMEASURED: DLL internals (About-text only); no Ichorio recipe found.
