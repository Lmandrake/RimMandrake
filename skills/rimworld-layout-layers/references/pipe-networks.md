# Resource pipe networks — what is installed and how membership works

Audited 2026-08-26 against `ModsConfig.xml` and mod source. Every claim marked
CONFIRMED was read from `.cs` or `.xml`, never from `strings` on a DLL.

⚠️ **Mod list state at audit:** the FULL list was active — **582 mods** in
`<activeMods>`. If a minimal list is live instead, every modded net below is
absent from the running game and a def check will read INVALID. Verify which
list is live before concluding anything.

## One framework covers four of the five nets

**`PipeSystem`**, shipped inside **Vanilla Expanded Framework**, packageId
`OskarPotocki.VanillaFactionsExpanded.Core` (ModsConfig `vanillaexpanded.vfecore`).
Source: `vendor/mod_sources/VanillaExpandedFramework-main/Source/PipeSystem/PipeSystem/`.

🔑 **One connectivity checker, parameterised by `PipeNetDef`, covers all four.**

### Core classes (CONFIRMED)
| class | role |
|---|---|
| `PipeSystem.PipeNet` | the live net: `connectors`, `producers`, `receivers`, `storages`, `PipeNetDef def` |
| `PipeSystem.PipeNetManager` | MapComponent; registers/unregisters connectors |
| `PipeSystem.PipeNetDef` | the Def for one resource: `resource`, `pipeDefs`, `linkToRefuelables` |
| `PipeSystem.CompResource` / `CompProperties_Resource` | **membership**; `CompProperties_Resource.pipeNet` is a `PipeNetDef` reference |
| `PipeSystem.CompResourceTrader` | produces/consumes |
| `PipeSystem.CompResourceStorage` | stores |
| `PipeSystem.CompConvertToResource` / `CompConvertToThing` | the item↔resource boundary |
| `PipeSystem.CompDeepExtractor`, `CompResourceProcessor`, `CompRefillWithPipes`, `CompPipeValve`, `CompSpillWhenDamaged` | the rest |
| `PipeSystem.Building_Pipe` | `thingClass` of the pipe piece |
| `PipeSystem.PlaceWorker_Pipe` | blocks two same-resource pipes stacking; adds no wall logic |

### How a def declares net membership
```xml
<comps>
  <li Class="PipeSystem.CompProperties_Resource">
    <pipeNet>VHGE_HelixienNet</pipeNet>
  </li>
</comps>
```

### Wall coexistence (CONFIRMED across every pipe def checked)
Every pipe ThingDef ships `<building><isEdifice>false</isEdifice></building>`,
`<altitudeLayer>Conduits</altitudeLayer>`, `<passability>Standable</passability>`
— the identical pattern vanilla uses for `PowerConduit`. RimWorld rejects only a
second **edifice** per cell, so a pipe stacks under a wall exactly like a power
conduit.

🔑 `isEdifice == false` is the single testable property that should permit a
same-cell stack in any layout linter.

## The active nets

| net | `PipeNetDef` | pipe defNames | mod / packageId |
|---|---|---|---|
| Helixien gas | `VHGE_HelixienNet` | `VHGE_HelixienPipe`, `VHGE_SubterraneanHelixienPipe` | Vanilla Helixien Gas Expanded — `VanillaExpanded.HelixienGas` |
| Chemfuel | `VCHE_ChemfuelNet` | `VCHE_ChemfuelPipe`, `VCHE_UndergroundChemfuelPipe` | Vanilla Chemfuel Expanded — `VanillaExpanded.VChemfuelE` |
| Deepchem | `VCHE_DeepchemNet` | `VCHE_DeepchemPipe` | same mod as chemfuel |
| Turret ammunition | `Reel_AmmoNet` | `Reel_AmmoPipe`, `Reel_SubAmmoPipe` | Reel's Turret Pipeline — `Reel.TurretPipeline` |

Turret ammo producer/consumer buildings: `REEL_AmmoTank`
(`CompProperties_ResourceStorage`, capacity 1000), `Reel_AmmoOutput`
(`Building_Storage` + `CompProperties_ConvertResourceToThing`), `Reel_AmmoDrain`
(`Building_Storage` + `CompProperties_ConvertThingToResource`). The net's
`linkToRefuelables` names `ReelTurretAmmo`.

⚠️ `VCHE_DeepchemPipe`'s own `isEdifice` field was not individually dumped; it
parents the same `BuildingBase` pattern as `VCHE_ChemfuelPipe` in the same file.
Treat that one field as UNCERTAIN.

## Rimefeller — a separate, parallel implementation

**Not `PipeSystem`.** Mod: Rimefeller, packageId `Dubwise.Rimefeller`.

- `thingClass = Rimefeller.Building_Pipe`
- `placeWorkers: Rimefeller.PlaceWorker_Pipe`
- membership comp `Class="Rimefeller.CompProperties_Pipe"`
- pipe defNames `OilPipeline`, `OilPipelineHidden`, plus `pipelineValve`
- same `isEdifice=false` wall-coexistence trick, independently implemented

⚠️ The repo's vendor copy has Defs and Languages but **no `Source/` folder**, so
the C# bodies — including whether it maintains a net object analogous to
`PipeNet` — are **UNMEASURED**. Only the XML-declared class names are confirmed.
Do not assume the PipeSystem model transfers.

## Ruled out (checked, negative)

- **Vanilla 1.6** — no resource pipe net of any kind. `PowerConduit` is the only
  vanilla "pipe". Odyssey's substructure and Anomaly add none.
- **Nutrient paste** — no `PipeNetDef`; `NutrientPasteDispenser` searches adjacent
  hoppers for items, it is not a network.
- **VFE Power** (`VanillaExpanded.VFEPower`) — generators and batteries, no
  `PipeSystem` reference in its 1.6 defs.
- **Belt Extractors** (`GroovyTaco.BeltExtractors`) — ships no Defs folder at
  all; a patch-only compat mod, unrelated.

## Bridge support

🔴 **None.** A grep of the whole companion source for `PipeNet`,
`CompResourceStorage`, `CompGasTrader` and net-grid patterns returns **zero hits**,
live or in source. There is no pipe tool in either direction. This is a blank
layer, not a deployment gap — unlike `jawa/power_net`, which is written but
undeployed.

⇒ Until a tool exists, the only live reading of a pipe net is
`jawa/inspect_string`, which surfaces the inspect pane as free text.
