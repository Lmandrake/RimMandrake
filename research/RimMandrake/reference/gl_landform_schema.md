# Geological Landforms - landform recipe XML schema (machine-derived)

Derived by `src/RimMandrake/Utils/rimbench/gl_schema_census.py` from 44 files in `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2773943594/1.6/Landforms-v1`.

Root element: `<NodeCanvas type="GeologicalLandforms.GraphEditor.Landform">` with children `<EditorStates/>`, `<Groups/>`, `<Nodes>`, `<Connections>`, `<Objects>`.

## 1. Node-type census

Distinct node `type=` values across the corpus: **79**.

| type | node instances | files using it |
|---|---|---|
| `gridPreview` | 367 | 44 |
| `valueRandom` | 196 | 44 |
| `gridOperator` | 177 | 42 |
| `gridPerlin` | 103 | 44 |
| `gridLinear` | 94 | 39 |
| `gridSelectValue` | 70 | 32 |
| `valueOperator` | 65 | 11 |
| `outputNamed` | 54 | 28 |
| `gridCache` | 52 | 25 |
| `terrainGridPreview` | 46 | 33 |
| `landformManifest` | 44 | 44 |
| `worldTileReq` | 43 | 43 |
| `valueWorldTile` | 43 | 28 |
| `gridRotateToMapSides` | 38 | 23 |
| `gridRotate` | 38 | 23 |
| `valueSelectValue` | 35 | 9 |
| `outputElevation` | 34 | 34 |
| `outputTerrain` | 33 | 33 |
| `gridSelectTerrain` | 31 | 28 |
| `valueRiverLinks` | 29 | 7 |
| `curveLinear` | 27 | 5 |
| `curveSelectValue` | 27 | 5 |
| `terrainNaturalWater` | 26 | 24 |
| `gridFromValue` | 26 | 22 |
| `curvePreview` | 25 | 5 |
| `inputNamed` | 23 | 5 |
| `outputScatterers` | 18 | 18 |
| `valuePolarRectPosition` | 17 | 5 |
| `gridSelectTerrainGrid` | 16 | 10 |
| `pathCost` | 16 | 5 |
| `mapSize` | 13 | 5 |
| `pathExtendTowards` | 13 | 4 |
| `pathExtend` | 12 | 5 |
| `valueSelectGridValue` | 10 | 9 |
| `gridSlice` | 10 | 5 |
| `curveOperator` | 10 | 5 |
| `terrainGridNaturalRock` | 9 | 6 |
| `gridSelectBiomeGrid` | 8 | 4 |
| `terrainFromBiome` | 7 | 5 |
| `pathLoss` | 7 | 4 |
| `pathSplit` | 7 | 4 |
| `pathCombine` | 7 | 4 |
| `pathCollision` | 7 | 4 |
| `layerConfig` | 6 | 6 |
| `valueSelectPath` | 6 | 4 |
| `terrainGridFromValue` | 6 | 3 |
| `outputCaves` | 5 | 5 |
| `pathTrace` | 5 | 5 |
| `pathOrigin` | 5 | 5 |
| `inputElevation` | 5 | 5 |
| `pathWidth` | 5 | 5 |
| `pathDensity` | 5 | 5 |
| `applyLayer` | 5 | 5 |
| `pathSwerve` | 5 | 5 |
| `pathTenacity` | 5 | 5 |
| `gridTunnels` | 4 | 4 |
| `worldTileGraphic` | 4 | 4 |
| `valueConst` | 4 | 4 |
| `mapIncidents` | 4 | 4 |
| `outputBiomeGrid` | 4 | 4 |
| `biomeGridPreview` | 4 | 4 |
| `pathEndCondition` | 4 | 4 |
| `pathSpeed` | 4 | 4 |
| `valueAngleDelta` | 4 | 2 |
| `outputFertility` | 3 | 3 |
| `valueSelectBiome` | 3 | 1 |
| `outputTerrainPatches` | 3 | 3 |
| `inputBiomeGrid` | 2 | 2 |
| `inputTerrain` | 2 | 2 |
| `terrainNaturalPriority` | 2 | 2 |
| `valueValidatePosition` | 1 | 1 |
| `outputWaterFlow` | 1 | 1 |
| `gridTurbulence` | 1 | 1 |
| `gridKernel` | 1 | 1 |
| `biomeSelectValue` | 1 | 1 |
| `gridMorphGroupFilter` | 1 | 1 |
| `inputCaves` | 1 | 1 |
| `biomeGridFromValue` | 1 | 1 |
| `valueRiversAndRoads` | 1 | 1 |

## 2. Per node type: scalar fields and ports

### `gridPreview` (367 instances, 44 files)

Scalar children (`tag`+`name` -> values):

- `<string name="PreviewModelId">`: ['Default', 'Elevation', 'Default x100', 'Default x10'] (367 occurrences)
- `<string name="PreviewTransformId">`: ['Default'] (307 occurrences)
- `<int name="RandSeed">`: range [18871959.0 .. 2144618561.0] (367 occurrences, 176 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x367): dynamic=['False'], direction=['In']
- `OutputKnob` (x367): dynamic=['False'], direction=['Out']

### `valueRandom` (196 instances, 44 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Average">`: range [-64.0 .. 60.0] (196 occurrences, 54 distinct)
- `<double name="Deviation">`: range [0.0 .. 180.0] (196 occurrences, 29 distinct)
- `<boolean name="DynamicSeed">`: ['false', 'true'] (196 occurrences)
- `<int name="RandSeed">`: range [8762686.0 .. 2115010304.0] (196 occurrences, 124 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `AverageKnob` (x196): dynamic=['False'], direction=['In']
- `DeviationKnob` (x196): dynamic=['False'], direction=['In']
- `OutputKnob` (x196): dynamic=['False'], direction=['Out']

### `gridOperator` (177 instances, 42 files)

Scalar children (`tag`+`name` -> values):

- `<double name="ApplyChance">`: ['1', '0.85000002384185791', '0.5', '0.34999999403953552', '0'] (177 occurrences)
- `<Operation name="OperationType">`: 10 distinct values, first 8: ['Add', 'Smooth_Max', 'Min', 'Multiply', 'Max', 'Invert_Above', 'Invert', 'Smooth_Min'] ...
- `<int name="RandSeed">`: range [10560305.0 .. 2142067531.0] (177 occurrences, 98 distinct)
- `<double name="Smoothness">`: ['0', '1.4500000476837158', '3', '0.550000011920929', '2', '1'] (177 occurrences)
- `<double name="StackCount">`: ['1', '0', '4.2891762708987056', '0.8947562572766925'] (163 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Values`: 177 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Apply chance` (x7): dynamic=['True'], direction=['In']
- `Input 0` (x177): dynamic=['True'], direction=['In']
- `Input 1` (x177): dynamic=['True'], direction=['In']
- `Input 2` (x19): dynamic=['True'], direction=['In']
- `OutputKnob` (x177): dynamic=['False'], direction=['Out']
- `Smoothness` (x12): dynamic=['True'], direction=['In']
- `Stack count` (x2): dynamic=['True'], direction=['In']

### `gridPerlin` (103 instances, 44 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Bias">`: range [-1.0 .. 1.5] (103 occurrences, 12 distinct)
- `<boolean name="DynamicSeed">`: ['false', 'true'] (103 occurrences)
- `<double name="Frequency">`: range [0.0 .. 0.10000000149011612] (103 occurrences, 14 distinct)
- `<double name="Lacunarity">`: ['2', '1.5'] (103 occurrences)
- `<boolean name="MapSizeAdj">`: ['true', 'false'] (24 occurrences)
- `<int name="Octaves">`: ['3', '6', '8', '4'] (103 occurrences)
- `<double name="Persistence">`: ['0.5', '0.40000000596046448'] (103 occurrences)
- `<int name="RandSeed">`: range [10875669.0 .. 2097089793.0] (103 occurrences, 41 distinct)
- `<double name="Scale">`: range [0.0 .. 5.0] (103 occurrences, 10 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `BiasKnob` (x103): dynamic=['False'], direction=['In']
- `FrequencyKnob` (x103): dynamic=['False'], direction=['In']
- `LacunarityKnob` (x103): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputKnob` (x103): dynamic=['False'], direction=['Out']
- `PersistenceKnob` (x103): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `ScaleKnob` (x103): dynamic=['False'], direction=['In']

### `gridLinear` (94 instances, 39 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Bias">`: range [-2.5 .. 2.5] (94 occurrences, 23 distinct)
- `<boolean name="Circular">`: ['true', 'false'] (94 occurrences)
- `<double name="ClampMax">`: range [-0.20000000298023224 .. 1.7976931348623157e+308] (94 occurrences, 13 distinct)
- `<double name="ClampMin">`: range [-1.7976931348623157e+308 .. 0.10000000149011612] (94 occurrences, 12 distinct)
- `<double name="OriginX">`: range [-0.05000000074505806 .. 0.6000000238418579] (94 occurrences, 22 distinct)
- `<double name="OriginZ">`: range [0.0 .. 0.6226320696461676] (94 occurrences, 9 distinct)
- `<int name="RandSeed">`: range [3943569.0 .. 2113846217.0] (94 occurrences, 40 distinct)
- `<double name="SpanNx">`: range [-71.01617333292961 .. 64.55387878417969] (94 occurrences, 17 distinct)
- `<double name="SpanNz">`: range [-100.0 .. 300.0] (94 occurrences, 14 distinct)
- `<double name="SpanPx">`: range [-130.0 .. 200.0] (94 occurrences, 31 distinct)
- `<double name="SpanPz">`: range [-130.0 .. 300.0] (94 occurrences, 25 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Bias` (x94): dynamic=['True'], direction=['In']
- `Clamp max` (x47): dynamic=['True'], direction=['In']
- `Clamp min` (x47): dynamic=['True'], direction=['In']
- `Origin x` (x94): dynamic=['True'], direction=['In']
- `Origin z` (x61): dynamic=['True'], direction=['In']
- `OutputKnob` (x94): dynamic=['False'], direction=['Out']
- `Span nx` (x65): dynamic=['True'], direction=['In']
- `Span nz` (x35): dynamic=['True'], direction=['In']
- `Span px` (x94): dynamic=['True'], direction=['In']
- `Span pz` (x61): dynamic=['True'], direction=['In']

### `gridSelectValue` (70 instances, 32 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['true', 'false'] (61 occurrences)
- `<int name="RandSeed">`: range [5282694.0 .. 2049839794.0] (70 occurrences, 62 distinct)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 70 occurrences (refIDs vary per-file, local to that file)
- `Values`: 70 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x70): dynamic=['False'], direction=['In']
- `Option 0` (x120): dynamic=['True'], direction=['In']
- `Option 1` (x20): dynamic=['True'], direction=['In']
- `Option 2` (x34): dynamic=['True'], direction=['In']
- `Option 3` (x30): dynamic=['True'], direction=['In']
- `Option 4` (x28): dynamic=['True'], direction=['In']
- `OutputKnob` (x70): dynamic=['False'], direction=['Out']

### `valueOperator` (65 instances, 11 files)

Scalar children (`tag`+`name` -> values):

- `<double name="ApplyChance">`: ['1'] (65 occurrences)
- `<Operation name="OperationType">`: ['Add', 'Multiply', 'Subtract', 'Divide', 'Invert'] (65 occurrences)
- `<int name="RandSeed">`: range [70206466.0 .. 2138053199.0] (65 occurrences, 47 distinct)
- `<double name="Smoothness">`: ['0'] (65 occurrences)
- `<double name="StackCount">`: ['1'] (64 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Values`: 65 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Input 0` (x65): dynamic=['True'], direction=['In']
- `Input 1` (x65): dynamic=['True'], direction=['In']
- `Input 2` (x13): dynamic=['True'], direction=['In']
- `OutputKnob` (x65): dynamic=['False'], direction=['Out']

### `outputNamed` (54 instances, 28 files)

Scalar children (`tag`+`name` -> values):

- `<string name="Name">`: 10 distinct values, first 8: ['coastNoise', 'lakeNoise', 'riverCoastalBuildup', 'riverHideMask', 'river', 'riverFlowValue', 'riverFlowOffset', 'riverDistance'] ...
- `<int name="RandSeed">`: range [18978246.0 .. 2138337347.0] (54 occurrences, 35 distinct)
- `<string name="TypeId">`: ['GridFunc', 'ValueFunc'] (54 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Value` (x54): dynamic=['True'], direction=['In']

### `gridCache` (52 instances, 25 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [113171475.0 .. 2122237803.0] (52 occurrences, 31 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x52): dynamic=['False'], direction=['In']
- `OutputKnob` (x52): dynamic=['False'], direction=['Out']

### `terrainGridPreview` (46 instances, 33 files)

Scalar children (`tag`+`name` -> values):

- `<string name="PreviewTransformId">`: ['Default'] (40 occurrences)
- `<int name="RandSeed">`: range [186414889.0 .. 2001587270.0] (46 occurrences, 15 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `ElevationInputKnob` (x46): dynamic=['False'], direction=['In']
- `ElevationOutputKnob` (x46): dynamic=['False'], direction=['Out']
- `InputKnob` (x46): dynamic=['False'], direction=['In']
- `OutputKnob` (x46): dynamic=['False'], direction=['Out']

### `landformManifest` (44 instances, 44 files)

Scalar children (`tag`+`name` -> values):

- `<string name="DisplayName">`: [''] (44 occurrences)
- `<boolean name="DisplayNameHasDirection">`: ['false', 'true'] (44 occurrences)
- `<string name="Id">`: 44 distinct values, first 8: ['Archipelago', 'Atoll', 'Badlands', 'Caldera', 'Canyon', 'CaveEntrance', 'Cirque', 'Cliff'] ...
- `<boolean name="IsCustom">`: ['false'] (44 occurrences)
- `<boolean name="IsEdited">`: ['false'] (44 occurrences)
- `<boolean name="IsExperimental">`: ['false'] (44 occurrences)
- `<boolean name="IsInternal">`: ['false', 'true'] (35 occurrences)
- `<int name="RandSeed">`: ['1333644392'] (44 occurrences)
- `<int name="RevisionVersion">`: ['3', '1', '2', '6', '4', '5'] (44 occurrences)
- `<long name="TimeCreated">`: range [1653353880001.0 .. 1726163992280.0] (44 occurrences, 44 distinct)

### `worldTileReq` (43 instances, 43 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="AllowSettlements">`: ['false', 'true'] (43 occurrences)
- `<boolean name="AllowSites">`: ['false', 'true'] (43 occurrences)
- `<float name="CaveChance">`: range [0.0 .. 1.0] (43 occurrences, 12 distinct)
- `<float name="Commonness">`: range [0.008379889 .. 1.0] (43 occurrences, 23 distinct)
- `<int name="RandSeed">`: ['351232153', '2118777191'] (43 occurrences)
- `<Topology name="Topology">`: 15 distinct values, first 8: ['CoastAllSides', 'Inland', 'CliffValley', 'CaveEntrance', 'CliffThreeSides', 'CliffOneSide', 'CliffAndCoast', 'CliffTwoSides'] ...

`FloatRange` children (`name` -> min/max seen):

- `AvgTemperatureRequirement`: min in [-100.0 .. 2.259887], max in [-20.3389835 .. 100.0] (43 occurrences)
- `BiomeTransitionsRequirement`: min in [0.0 .. 0.0], max in [6.0 .. 6.0] (43 occurrences)
- `DepthInCaveSystemRequirement`: min in [0.0 .. 0.0], max in [0.0 .. 10.0] (36 occurrences)
- `ElevationRequirement`: min in [-1000.0 .. 745.7627], max in [388.571442 .. 5000.0] (43 occurrences)
- `HillinessRequirement`: min in [1.0 .. 6.0], max in [1.45197737 .. 6.0] (43 occurrences)
- `MapSizeRequirement`: min in [0.0 .. 250.0], max in [0.0 .. 1000.0] (43 occurrences)
- `RainfallRequirement`: min in [0.0 .. 706.214661], max in [437.853119 .. 5000.0] (43 occurrences)
- `RiverRequirement`: min in [0.0 .. 0.502285659], max in [0.0 .. 1.0] (43 occurrences)
- `RoadRequirement`: min in [0.0 .. 0.05142857], max in [0.0 .. 1.0] (43 occurrences)
- `SwampinessRequirement`: min in [0.0 .. 0.5480226], max in [1.0 .. 1.0] (43 occurrences)
- `TopologyValueRequirement`: min in [-1.0 .. -1.0], max in [1.0 .. 1.0] (36 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `AllowedRiverTypes`: 14 occurrences (refIDs vary per-file, local to that file)

### `valueWorldTile` (43 instances, 28 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [18716120.0 .. 2109167218.0] (43 occurrences, 31 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `BiomeOutputKnob` (x43): dynamic=['False'], direction=['Out']
- `CaveSystemDepthValueOutputKnob` (x39): dynamic=['False'], direction=['Out']
- `ElevationOutputKnob` (x43): dynamic=['False'], direction=['Out']
- `HillinessOutputKnob` (x43): dynamic=['False'], direction=['Out']
- `RainfallOutputKnob` (x43): dynamic=['False'], direction=['Out']
- `TemperatureOutputKnob` (x43): dynamic=['False'], direction=['Out']
- `TopologyAngleOutputKnob` (x33): dynamic=['False'], direction=['Out']
- `TopologyValueOutputKnob` (x39): dynamic=['False'], direction=['Out']

### `gridRotateToMapSides` (38 instances, 23 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [35781376.0 .. 2084577709.0] (38 occurrences, 14 distinct)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `MapSides`: 38 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Input 0` (x38): dynamic=['True'], direction=['In']
- `Input 1` (x12): dynamic=['True'], direction=['In']
- `Input 2` (x5): dynamic=['True'], direction=['In']
- `Input 3` (x1): dynamic=['True'], direction=['In']
- `Output 0` (x38): dynamic=['True'], direction=['Out']
- `Output 1` (x12): dynamic=['True'], direction=['Out']
- `Output 2` (x5): dynamic=['True'], direction=['Out']
- `Output 3` (x1): dynamic=['True'], direction=['Out']

### `gridRotate` (38 instances, 23 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Angle">`: range [-137.28743059560657 .. 180.0] (38 occurrences, 10 distinct)
- `<int name="RandSeed">`: range [12842592.0 .. 2138247723.0] (38 occurrences, 26 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `AngleKnob` (x38): dynamic=['False'], direction=['In']
- `InputKnob` (x38): dynamic=['False'], direction=['In']
- `OutputKnob` (x38): dynamic=['False'], direction=['Out']

### `valueSelectValue` (35 instances, 9 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['true', 'false'] (35 occurrences)
- `<int name="RandSeed">`: range [66305738.0 .. 2060948890.0] (35 occurrences, 34 distinct)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 35 occurrences (refIDs vary per-file, local to that file)
- `Values`: 35 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x35): dynamic=['False'], direction=['In']
- `Option 0` (x67): dynamic=['True'], direction=['In']
- `Option 1` (x3): dynamic=['True'], direction=['In']
- `Option 2` (x15): dynamic=['True'], direction=['In']
- `Option 3` (x9): dynamic=['True'], direction=['In']
- `Option 4` (x3): dynamic=['True'], direction=['In']
- `OutputKnob` (x35): dynamic=['False'], direction=['Out']

### `outputElevation` (34 instances, 34 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [297073253.0 .. 1918357657.0] (34 occurrences, 11 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x34): dynamic=['False'], direction=['In']
- `OutputKnob` (x34): dynamic=['False'], direction=['Out']

### `outputTerrain` (33 instances, 33 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['842846725', '1207926160', '276299414', '1441011932', '1375216286', '1652175673', '1149281262', '862575613'] (33 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `BaseKnob` (x33): dynamic=['False'], direction=['In']
- `CaveKnob` (x30): dynamic=['False'], direction=['In']
- `StoneKnob` (x33): dynamic=['False'], direction=['In']

### `gridSelectTerrain` (31 instances, 28 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (27 occurrences)
- `<int name="RandSeed">`: ['1317255026', '588585345', '1555528661', '427768406', '557108696', '1648275490', '1963563707'] (31 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 31 occurrences (refIDs vary per-file, local to that file)
- `Values`: 31 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x31): dynamic=['False'], direction=['In']
- `Option 0` (x32): dynamic=['True'], direction=['In']
- `Option 1` (x30): dynamic=['True'], direction=['In']
- `Option 2` (x30): dynamic=['True'], direction=['In']
- `Option 3` (x28): dynamic=['True'], direction=['In']
- `OutputKnob` (x31): dynamic=['False'], direction=['Out']

### `valueRiverLinks` (29 instances, 7 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [17648071.0 .. 2132210997.0] (29 occurrences, 23 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InflowAngleOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `InflowOffsetOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `InflowWidthOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `OutflowAngleOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `OutflowWidthOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `TertiaryAngleOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `TertiaryOffsetOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `TertiaryWidthOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `TributaryAngleOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `TributaryOffsetOutputKnob` (x29): dynamic=['False'], direction=['Out']
- `TributaryWidthOutputKnob` (x29): dynamic=['False'], direction=['Out']

### `curveLinear` (27 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Bias">`: ['0'] (27 occurrences)
- `<double name="ClampMax">`: ['1.7976931348623157E+308'] (27 occurrences)
- `<double name="ClampMin">`: ['-1.7976931348623157E+308'] (27 occurrences)
- `<int name="RandSeed">`: range [317621462.0 .. 2132753657.0] (27 occurrences, 9 distinct)
- `<double name="Slope">`: ['1'] (27 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Bias` (x27): dynamic=['True'], direction=['In']
- `OutputKnob` (x27): dynamic=['False'], direction=['Out']
- `Slope` (x27): dynamic=['True'], direction=['In']

### `curveSelectValue` (27 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['true', 'false'] (27 occurrences)
- `<int name="RandSeed">`: range [127519580.0 .. 1918659522.0] (27 occurrences, 9 distinct)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 27 occurrences (refIDs vary per-file, local to that file)
- `Values`: 27 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x27): dynamic=['False'], direction=['In']
- `Option 0` (x54): dynamic=['True'], direction=['In']
- `Option 2` (x20): dynamic=['True'], direction=['In']
- `Option 3` (x20): dynamic=['True'], direction=['In']
- `Option 4` (x20): dynamic=['True'], direction=['In']
- `Option 5` (x1): dynamic=['True'], direction=['In']
- `OutputKnob` (x27): dynamic=['False'], direction=['Out']

### `terrainNaturalWater` (26 instances, 24 files)

Scalar children (`tag`+`name` -> values):

- `<MapSide name="MapSide">`: ['Front', 'Right', 'Left'] (26 occurrences)
- `<int name="RandSeed">`: ['2019941122', '1495595294', '2006778718', '43963903', '785085385', '745333795', '146842798', '416773477'] (26 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `BeachOutputKnob` (x26): dynamic=['False'], direction=['Out']
- `DeepOutputKnob` (x26): dynamic=['False'], direction=['Out']
- `RiverDeepOutputKnob` (x3): dynamic=['False'], direction=['Out']
- `RiverShallowOutputKnob` (x3): dynamic=['False'], direction=['Out']
- `RiverbankOutputKnob` (x3): dynamic=['False'], direction=['Out']
- `ShallowOutputKnob` (x26): dynamic=['False'], direction=['Out']

### `gridFromValue` (26 instances, 22 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [238478001.0 .. 2122854953.0] (26 occurrences, 18 distinct)
- `<double name="Value">`: ['0'] (21 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x26): dynamic=['False'], direction=['In']
- `OutputKnob` (x26): dynamic=['False'], direction=['Out']

### `curvePreview` (25 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<string name="PreviewModelId">`: ['Default'] (25 occurrences)
- `<int name="RandSeed">`: ['1573329959', '31004698', '28452364', '1034519809', '382173833', '2038163865'] (25 occurrences)
- `<double name="ViewportMaxX">`: ['150', '5', '40', '200'] (25 occurrences)
- `<double name="ViewportMaxY">`: ['5', '1', '4.3000001907348633', '3'] (25 occurrences)
- `<double name="ViewportMinX">`: ['0'] (25 occurrences)
- `<double name="ViewportMinY">`: ['-5', '0'] (25 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x25): dynamic=['False'], direction=['In']
- `OutputKnob` (x25): dynamic=['False'], direction=['Out']

### `inputNamed` (23 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<string name="Name">`: 10 distinct values, first 8: ['coastNoise', 'riverDepthPatternOffset', 'riverCoastalBuildup', 'lakeNoise', 'river', 'riverDistance', 'riverSide', 'riverFlowValue'] ...
- `<int name="RandSeed">`: range [111456465.0 .. 2028481512.0] (23 occurrences, 20 distinct)
- `<string name="TypeId">`: ['GridFunc', 'ValueFunc'] (23 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Value` (x23): dynamic=['True'], direction=['Out']

### `outputScatterers` (18 instances, 18 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [54184704.0 .. 1936058131.0] (18 occurrences, 13 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `CaveHivesKnob` (x13): dynamic=['False'], direction=['In']
- `MineablesKnob` (x18): dynamic=['False'], direction=['In']

### `valuePolarRectPosition` (17 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Angle">`: ['0'] (17 occurrences)
- `<double name="Margin">`: ['0.10000000149011612', '0.20000000298023224', '0'] (17 occurrences)
- `<double name="Offset">`: ['0'] (17 occurrences)
- `<int name="RandSeed">`: ['104887173', '1306208913', '1562410431', '201340367', '730079713', '1779432890', '1987406815', '1642528745'] (17 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `AngleKnob` (x17): dynamic=['False'], direction=['In']
- `MarginKnob` (x17): dynamic=['False'], direction=['In']
- `OffsetKnob` (x17): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputXKnob` (x17): dynamic=['False'], direction=['Out']
- `OutputZKnob` (x17): dynamic=['False'], direction=['Out']

### `gridSelectTerrainGrid` (16 instances, 10 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (14 occurrences)
- `<int name="RandSeed">`: range [552940034.0 .. 1997893409.0] (16 occurrences, 10 distinct)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 16 occurrences (refIDs vary per-file, local to that file)
- `Values`: 16 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x16): dynamic=['False'], direction=['In']
- `Option 0` (x21): dynamic=['True'], direction=['In']
- `Option 1` (x11): dynamic=['True'], direction=['In']
- `Option 2` (x3): dynamic=['True'], direction=['In']
- `Option 3` (x2): dynamic=['True'], direction=['In']
- `Option 4` (x1): dynamic=['True'], direction=['In']
- `OutputKnob` (x16): dynamic=['False'], direction=['Out']

### `pathCost` (16 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: range [237848775.0 .. 2107579451.0] (16 occurrences, 13 distinct)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Cost ~ Overlap` (x16): dynamic=['True'], direction=['In']
- `Cost ~ Overlap Parent` (x16): dynamic=['True'], direction=['In']
- `Cost ~ Position` (x16): dynamic=['True'], direction=['In']
- `InputKnob` (x16): dynamic=['False'], direction=['In']
- `OutputKnob` (x16): dynamic=['False'], direction=['Out']

### `mapSize` (13 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['2036869946', '1005275115', '552856519', '2068154722', '311304843', '475824551', '380212942'] (13 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `OutputKnob` (x13): dynamic=['False'], direction=['Out']

### `pathExtendTowards` (13 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Length">`: ['9999', '0'] (13 occurrences)
- `<int name="RandSeed">`: ['1437411794', '336134874', '2143865119', '741341770', '163597862', '1084023838', '1202563196', '1899230038'] (13 occurrences)
- `<double name="StepSize">`: ['5'] (13 occurrences)
- `<double name="TargetX">`: ['0'] (13 occurrences)
- `<double name="TargetZ">`: ['0'] (13 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x13): dynamic=['False'], direction=['In']
- `LengthKnob` (x13): dynamic=['False'], direction=['In']
- `OutputKnob` (x13): dynamic=['False'], direction=['Out']
- `StepSizeKnob` (x13): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `TargetXKnob` (x13): dynamic=['False'], direction=['In']
- `TargetZKnob` (x13): dynamic=['False'], direction=['In']

### `pathExtend` (12 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Length">`: ['0', '9999'] (12 occurrences)
- `<int name="RandSeed">`: ['1521046576', '1657264963', '326930754', '1296011111', '5260013', '560918656', '499628651', '1548158891'] (12 occurrences)
- `<double name="StepSize">`: ['5'] (12 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x12): dynamic=['False'], direction=['In']
- `LengthKnob` (x12): dynamic=['False'], direction=['In']
- `OutputKnob` (x12): dynamic=['False'], direction=['Out']
- `StepSizeKnob` (x12): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `valueSelectGridValue` (10 instances, 9 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (9 occurrences)
- `<int name="RandSeed">`: ['1734950954', '545112172', '1095087770', '133420186', '952764042', '1137229954', '780468564', '497474604'] (10 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 10 occurrences (refIDs vary per-file, local to that file)
- `Values`: 10 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x10): dynamic=['False'], direction=['In']
- `Option 0` (x16): dynamic=['True'], direction=['In']
- `Option 1` (x4): dynamic=['True'], direction=['In']
- `OutputKnob` (x10): dynamic=['False'], direction=['Out']

### `gridSlice` (10 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Position">`: ['0'] (10 occurrences)
- `<int name="RandSeed">`: ['102292614', '174246154', '5575352'] (10 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x10): dynamic=['False'], direction=['In']
- `OutputKnob` (x10): dynamic=['False'], direction=['Out']
- `PositionKnob` (x10): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `curveOperator` (10 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="ApplyChance">`: ['1'] (10 occurrences)
- `<Operation name="OperationType">`: ['Divide', 'Scale_Around_1'] (10 occurrences)
- `<int name="RandSeed">`: ['1272542585', '1084378444'] (10 occurrences)
- `<double name="Smoothness">`: ['0'] (10 occurrences)
- `<double name="StackCount">`: ['1'] (10 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Values`: 10 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Input 0` (x10): dynamic=['True'], direction=['In']
- `Input 1` (x10): dynamic=['True'], direction=['In']
- `OutputKnob` (x10): dynamic=['False'], direction=['Out']

### `terrainGridNaturalRock` (9 instances, 6 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['2097876217', '1421341744', '1545662926'] (9 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `OutputKnob` (x9): dynamic=['False'], direction=['Out']

### `gridSelectBiomeGrid` (8 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (6 occurrences)
- `<int name="RandSeed">`: ['135031405', '109076526', '976568151', '1148652274', '600472745', '1954612819', '271722858', '1241408089'] (8 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 8 occurrences (refIDs vary per-file, local to that file)
- `Values`: 8 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x8): dynamic=['False'], direction=['In']
- `Option 0` (x12): dynamic=['True'], direction=['In']
- `Option 1` (x4): dynamic=['True'], direction=['In']
- `Option 2` (x2): dynamic=['True'], direction=['In']
- `Option 3` (x1): dynamic=['True'], direction=['In']
- `OutputKnob` (x8): dynamic=['False'], direction=['Out']

### `terrainFromBiome` (7 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<string name="Biome">`: ['TemperateForest'] (2 occurrences)
- `<double name="Fertility">`: ['0', '1'] (7 occurrences)
- `<int name="RandSeed">`: ['1254668707', '1418560660', '210181670', '1079838190', '1064018736'] (7 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `BiomeKnob` (x7): dynamic=['False'], direction=['In']
- `FertilityKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputKnob` (x7): dynamic=['False'], direction=['Out']

### `pathLoss` (7 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<double name="DensityLoss">`: ['0'] (7 occurrences)
- `<int name="RandSeed">`: ['1568671278', '1795989233', '2073306503', '1287516055', '365845332', '91519502'] (7 occurrences)
- `<double name="SpeedLoss">`: ['0'] (7 occurrences)
- `<double name="WidthLoss">`: ['0'] (7 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `DensityLossKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `InputKnob` (x7): dynamic=['False'], direction=['In']
- `OutputKnob` (x7): dynamic=['False'], direction=['Out']
- `SpeedLossKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `WidthLossKnob` (x7): dynamic=['False'], direction=['In']

### `pathSplit` (7 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['9600620', '803268992', '1700373011', '1894072072', '146007291', '1647763575'] (7 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Angles`: 7 occurrences (refIDs vary per-file, local to that file)
- `Speeds`: 7 occurrences (refIDs vary per-file, local to that file)
- `Widths`: 7 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Angle 0` (x7): dynamic=['True'], direction=['In']
- `Angle 1` (x7): dynamic=['True'], direction=['In']
- `InputKnob` (x7): dynamic=['False'], direction=['In']
- `Output 0` (x7): dynamic=['True'], direction=['Out']
- `Output 1` (x7): dynamic=['True'], direction=['Out']
- `Speed 0` (x7): dynamic=['True'], direction=['In']
- `Speed 1` (x7): dynamic=['True'], direction=['In']
- `Width 0` (x7): dynamic=['True'], direction=['In']
- `Width 1` (x7): dynamic=['True'], direction=['In']

### `pathCombine` (7 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1952068049', '1485853170', '1997515040', '143870044', '305259301', '238332184'] (7 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Input 0` (x7): dynamic=['True'], direction=['In']
- `Input 1` (x7): dynamic=['True'], direction=['In']
- `OutputKnob` (x7): dynamic=['False'], direction=['Out']

### `pathCollision` (7 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<double name="ArcIntensity">`: ['0', '0.5'] (7 occurrences)
- `<double name="ArcRange">`: ['0', '15'] (7 occurrences)
- `<double name="MergeResultTrim">`: ['0', '-999', '-1'] (7 occurrences)
- `<int name="RandSeed">`: ['856103528', '7876285', '952422063', '1652261564', '2084566050', '1678041391'] (7 occurrences)
- `<double name="SplitTurnLock">`: ['2', '0.5'] (7 occurrences)
- `<double name="StableRange">`: ['0', '30', '20', '15'] (7 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `ArcIntensityKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `ArcRangeKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `InputKnob` (x7): dynamic=['False'], direction=['In']
- `MergeResultTrimKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputKnob` (x7): dynamic=['False'], direction=['Out']
- `SplitTurnLockKnob` (x7): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `StableRangeKnob` (x7): dynamic=['False'], direction=['In']

### `layerConfig` (6 instances, 6 files)

Scalar children (`tag`+`name` -> values):

- `<string name="LayerId">`: ['river', ''] (6 occurrences)
- `<int name="Priority">`: ['10', '12'] (6 occurrences)
- `<int name="RandSeed">`: ['1336421998'] (6 occurrences)

### `valueSelectPath` (6 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (6 occurrences)
- `<int name="RandSeed">`: ['1801810367', '2133379688', '342739164', '87242715', '620702620', '1148465585'] (6 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 6 occurrences (refIDs vary per-file, local to that file)
- `Values`: 6 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x6): dynamic=['False'], direction=['In']
- `Option 0` (x12): dynamic=['True'], direction=['In']
- `Option 2` (x1): dynamic=['True'], direction=['In']
- `OutputKnob` (x6): dynamic=['False'], direction=['Out']

### `terrainGridFromValue` (6 instances, 3 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['2088635601', '1753343862', '557574107', '345369221', '462425424', '263624329'] (6 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x6): dynamic=['False'], direction=['In']
- `OutputKnob` (x6): dynamic=['False'], direction=['Out']

### `outputCaves` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1750516046', '652404239', '1309280291'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x5): dynamic=['False'], direction=['In']
- `OutputKnob` (x5): dynamic=['False'], direction=['Out']

### `pathTrace` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="GridMargin">`: ['3', '0'] (5 occurrences)
- `<int name="RandSeed">`: ['1297630991'] (5 occurrences)
- `<double name="TraceMarginInner">`: ['5'] (5 occurrences)
- `<double name="TraceMarginOuter">`: ['50'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `DistanceOutputKnob` (x5): dynamic=['False'], direction=['Out']
- `GridMarginKnob` (x5): dynamic=['False'], direction=['In']
- `InputKnob` (x5): dynamic=['False'], direction=['In']
- `MainOutputKnob` (x5): dynamic=['False'], direction=['Out']
- `OffsetOutputKnob` (x5): dynamic=['False'], direction=['Out']
- `SideOutputKnob` (x5): dynamic=['False'], direction=['Out']
- `TraceMarginInnerKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `TraceMarginOuterKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `ValueOutputKnob` (x5): dynamic=['False'], direction=['Out']

### `pathOrigin` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="Count">`: ['1'] (5 occurrences)
- `<double name="Density">`: ['1'] (5 occurrences)
- `<double name="Direction">`: ['0'] (5 occurrences)
- `<double name="PosX">`: ['0'] (5 occurrences)
- `<double name="PosZ">`: ['0'] (5 occurrences)
- `<int name="RandSeed">`: ['1463430737'] (5 occurrences)
- `<double name="Speed">`: ['0.75', '-0.75'] (5 occurrences)
- `<double name="Width">`: ['0'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `CountKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `DensityKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `DirectionKnob` (x5): dynamic=['False'], direction=['In']
- `OutputKnob` (x5): dynamic=['False'], direction=['Out']
- `PosXKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `PosZKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `SpeedKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `WidthKnob` (x5): dynamic=['False'], direction=['In']

### `inputElevation` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['752039297', '1553234700', '1571208059'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Knob` (x5): dynamic=['False'], direction=['Out']

### `pathWidth` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['249281086'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Buildup ~ Position` (x5): dynamic=['True'], direction=['In']
- `Extent ~ Pattern` (x5): dynamic=['True'], direction=['In']
- `Extent ~ Position` (x5): dynamic=['True'], direction=['In']
- `Extent ~ Width` (x5): dynamic=['True'], direction=['In']
- `InputKnob` (x5): dynamic=['False'], direction=['In']
- `OutputKnob` (x5): dynamic=['False'], direction=['Out']
- `Pattern ~ Stable width` (x5): dynamic=['True'], direction=['In']
- `Side balance ~ Pattern` (x5): dynamic=['True'], direction=['In']

### `pathDensity` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['28208669'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Density ~ Extent` (x5): dynamic=['True'], direction=['In']
- `Density ~ Position` (x5): dynamic=['True'], direction=['In']
- `InputKnob` (x5): dynamic=['False'], direction=['In']
- `OutputKnob` (x5): dynamic=['False'], direction=['Out']

### `applyLayer` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<string name="LayerId">`: ['RiverTerrain'] (5 occurrences)
- `<int name="RandSeed">`: ['335365894', '1568030984'] (5 occurrences)

### `pathSwerve` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['525064301', '1446844182'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x5): dynamic=['False'], direction=['In']
- `OutputKnob` (x5): dynamic=['False'], direction=['Out']
- `Pattern ~ Stable width` (x5): dynamic=['True'], direction=['In']
- `Swerve ~ Cost` (x5): dynamic=['True'], direction=['In']
- `Swerve ~ Pattern` (x5): dynamic=['True'], direction=['In']
- `Swerve ~ Position` (x5): dynamic=['True'], direction=['In']
- `Swerve ~ Width` (x5): dynamic=['True'], direction=['In']

### `pathTenacity` (5 instances, 5 files)

Scalar children (`tag`+`name` -> values):

- `<double name="AngleLimitAbs">`: ['6'] (5 occurrences)
- `<double name="AngleTenacity">`: ['0.30000001192092896'] (5 occurrences)
- `<int name="RandSeed">`: ['2143510717', '1527638155'] (5 occurrences)
- `<double name="SplitTenacity">`: ['0.5'] (5 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `AngleLimitAbsKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `AngleTenacityKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `InputKnob` (x5): dynamic=['False'], direction=['In']
- `OutputKnob` (x5): dynamic=['False'], direction=['Out']
- `SplitTenacityKnob` (x5): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `gridTunnels` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<double name="BranchChance">`: ['0.014999999664723873', '0.019999999552965164'] (4 occurrences)
- `<int name="BranchMinDistanceFromStart">`: ['25'] (4 occurrences)
- `<double name="BranchWidthOffsetMultiplier">`: ['0.5'] (4 occurrences)
- `<double name="ClosedTunnelsPer10K">`: ['0'] (4 occurrences)
- `<double name="DirectionChangeSpeed">`: ['8'] (4 occurrences)
- `<double name="InputThreshold">`: ['0.699999988079071', '5.9000000953674316'] (4 occurrences)
- `<int name="MaxClosedTunnelsPerRockGroup">`: ['0'] (4 occurrences)
- `<int name="MaxOpenTunnelsPerRockGroup">`: ['10', '8', '12', '15'] (4 occurrences)
- `<int name="MinEdgeCells">`: ['25'] (3 occurrences)
- `<double name="OpenTunnelsPer10K">`: ['10', '15'] (4 occurrences)
- `<int name="RandSeed">`: ['230599817', '2067078130'] (4 occurrences)
- `<double name="TunnelWidthMultiplierMax">`: ['2.2999999523162842'] (4 occurrences)
- `<double name="TunnelWidthMultiplierMin">`: ['0.800000011920929', '1.2000000476837158'] (4 occurrences)
- `<double name="WidthReductionPerCell">`: ['0.039999999105930328'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `DepthsKnob` (x3): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `InputKnob` (x4): dynamic=['False'], direction=['In']
- `OffsetsKnob` (x3): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputKnob` (x4): dynamic=['False'], direction=['Out']

### `worldTileGraphic` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="AtlasSizeX">`: ['4', '1'] (4 occurrences)
- `<int name="AtlasSizeY">`: ['4', '1'] (4 occurrences)
- `<DrawMode name="DrawMode">`: ['HexAdjacencyCaves', 'HexRandom'] (4 occurrences)
- `<int name="RandSeed">`: ['324907296', '993959854', '1890569045'] (4 occurrences)
- `<string name="TexPath">`: [''] (3 occurrences)

### `valueConst` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1230393023', '174230859', '323041973', '1619348942'] (4 occurrences)
- `<double name="Value">`: ['0.5', '-1'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `OutputKnob` (x4): dynamic=['False'], direction=['Out']

### `mapIncidents` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1963115152', '1894316866', '1333075478'] (4 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `ArrivalModeEntries`: 4 occurrences (refIDs vary per-file, local to that file)
- `GameConditionEntries`: 4 occurrences (refIDs vary per-file, local to that file)
- `IncidentEntries`: 4 occurrences (refIDs vary per-file, local to that file)
- `RaidStrategyEntries`: 4 occurrences (refIDs vary per-file, local to that file)

### `outputBiomeGrid` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1237655550', '807867685', '1789817781', '2129679617'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `BiomeGridKnob` (x4): dynamic=['False'], direction=['In']
- `BiomeTransitionKnob` (x4): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `biomeGridPreview` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<string name="PreviewTransformId">`: ['Default'] (3 occurrences)
- `<int name="RandSeed">`: ['1832911739', '203014413', '1843329198', '2028897846'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x4): dynamic=['False'], direction=['In']
- `OutputKnob` (x4): dynamic=['False'], direction=['Out']

### `pathEndCondition` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['702985599', '667461794', '1360849424'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x4): dynamic=['False'], direction=['In']
- `OutputKnob` (x4): dynamic=['False'], direction=['Out']
- `WidthMaskKnob` (x4): dynamic=['False'], direction=['In']

### `pathSpeed` (4 instances, 4 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1345131829', '16064138', '2037404425', '1990647281'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x4): dynamic=['False'], direction=['In']
- `OutputKnob` (x4): dynamic=['False'], direction=['Out']
- `Speed ~ Position` (x4): dynamic=['True'], direction=['In']

### `valueAngleDelta` (4 instances, 2 files)

Scalar children (`tag`+`name` -> values):

- `<double name="First">`: ['0'] (4 occurrences)
- `<int name="RandSeed">`: ['741208328', '837394741', '179953894', '570005463'] (4 occurrences)
- `<double name="Second">`: ['0'] (4 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `FirstKnob` (x4): dynamic=['False'], direction=['In']
- `OutputKnob` (x4): dynamic=['False'], direction=['Out']
- `SecondKnob` (x4): dynamic=['False'], direction=['In']

### `outputFertility` (3 instances, 3 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1042686644'] (3 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x3): dynamic=['False'], direction=['In']
- `OutputKnob` (x3): dynamic=['False'], direction=['Out']

### `valueSelectBiome` (3 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (3 occurrences)
- `<int name="RandSeed">`: ['325115113', '973802279', '180595103'] (3 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 3 occurrences (refIDs vary per-file, local to that file)
- `Values`: 3 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x3): dynamic=['False'], direction=['In']
- `Option 0` (x6): dynamic=['True'], direction=['In']
- `Option 2` (x2): dynamic=['True'], direction=['In']
- `Option 3` (x2): dynamic=['True'], direction=['In']
- `OutputKnob` (x3): dynamic=['False'], direction=['Out']

### `outputTerrainPatches` (3 instances, 3 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['298118684', '1331185592', '705053841'] (3 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `FrequencyKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `LacunarityKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OffsetKnob` (x3): dynamic=['False'], direction=['In']
- `PersistenceKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `inputBiomeGrid` (2 instances, 2 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1987241307', '1986460014'] (2 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Knob` (x2): dynamic=['False'], direction=['Out']

### `inputTerrain` (2 instances, 2 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['374895672', '1211629763'] (2 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Knob` (x2): dynamic=['False'], direction=['Out']

### `terrainNaturalPriority` (2 instances, 2 files)

Scalar children (`tag`+`name` -> values):

- `<PriorityOptions name="Options">`: [''] (2 occurrences)
- `<int name="RandSeed">`: ['562566542', '1266267943'] (2 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputAKnob` (x2): dynamic=['False'], direction=['In']
- `InputBKnob` (x2): dynamic=['False'], direction=['In']
- `OutputKnob` (x2): dynamic=['False'], direction=['Out']

### `valueValidatePosition` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<int name="Attempts">`: ['150'] (1 occurrences)
- `<double name="ExclusionRadius">`: ['0'] (1 occurrences)
- `<int name="RandSeed">`: ['25289267'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `ExclusionRadiusKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `InputXKnob` (x1): dynamic=['False'], direction=['In']
- `InputZKnob` (x1): dynamic=['False'], direction=['In']
- `OutputXKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputZKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `ValidatorKnob` (x1): dynamic=['False'], direction=['In']

### `outputWaterFlow` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1209735150'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `FlowAlphaKnob` (x1): dynamic=['False'], direction=['In']
- `FlowBetaKnob` (x1): dynamic=['False'], direction=['In']
- `RiverTerrainKnob` (x1): dynamic=['False'], direction=['In']

### `gridTurbulence` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<double name="IntensityX">`: ['0.20000000298023224'] (1 occurrences)
- `<double name="IntensityZ">`: ['0.30000001192092896'] (1 occurrences)
- `<int name="RandSeed">`: ['1289019036'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `IntensityXKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `IntensityZKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `OutputXKnob` (x1): dynamic=['False'], direction=['Out']
- `OutputZKnob` (x1): dynamic=['False'], direction=['Out']

### `gridKernel` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<Operation name="OperationType">`: ['Add'] (1 occurrences)
- `<int name="RandSeed">`: ['1019313232'] (1 occurrences)
- `<double name="Size">`: ['1'] (1 occurrences)
- `<double name="Step">`: ['1'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x1): dynamic=['False'], direction=['In']
- `OutputKnob` (x1): dynamic=['False'], direction=['Out']
- `SizeKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `StepKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `biomeSelectValue` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<boolean name="Interpolated">`: ['false'] (1 occurrences)
- `<int name="RandSeed">`: ['705902593'] (1 occurrences)

`Variable` children (indirection: `<Variable name="X" refID="N"/>` points at `<Objects><Object refID="N">` holding a typed `List<T>`, e.g. thresholds/values/mapSides arrays):

- `Thresholds`: 1 occurrences (refIDs vary per-file, local to that file)
- `Values`: 1 occurrences (refIDs vary per-file, local to that file)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x1): dynamic=['False'], direction=['In']
- `Option 0` (x2): dynamic=['True'], direction=['In']
- `Option 2` (x1): dynamic=['True'], direction=['In']
- `Option 3` (x1): dynamic=['True'], direction=['In']
- `Option 4` (x1): dynamic=['True'], direction=['In']
- `Option 5` (x1): dynamic=['True'], direction=['In']
- `OutputKnob` (x1): dynamic=['False'], direction=['Out']

### `gridMorphGroupFilter` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<double name="MaxGroupSize">`: ['350'] (1 occurrences)
- `<double name="MinGroupSize">`: ['0'] (1 occurrences)
- `<int name="RandSeed">`: ['59715515'] (1 occurrences)
- `<double name="ThinLimit">`: ['0.75'] (1 occurrences)
- `<double name="Threshold">`: ['1'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x1): dynamic=['False'], direction=['In']
- `MaxGroupSizeKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `MinGroupSizeKnob` (x1): dynamic=['False'], direction=['In']
- `OutputKnob` (x1): dynamic=['False'], direction=['Out']
- `ThinLimitKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)
- `ThresholdKnob` (x1): dynamic=['False'], direction=UNKNOWN (never resolved via a connection in this corpus)

### `inputCaves` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1636584131'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `Knob` (x1): dynamic=['False'], direction=['Out']

### `biomeGridFromValue` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1819528853'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `InputKnob` (x1): dynamic=['False'], direction=['In']
- `OutputKnob` (x1): dynamic=['False'], direction=['Out']

### `valueRiversAndRoads` (1 instances, 1 files)

Scalar children (`tag`+`name` -> values):

- `<int name="RandSeed">`: ['1996212253'] (1 occurrences)

Ports seen (`name`: dynamic flag(s), resolved direction(s)):

- `AngleOutputKnob` (x1): dynamic=['False'], direction=['Out']
- `OffsetOutputKnob` (x1): dynamic=['False'], direction=['Out']
- `RiverWidthOutputKnob` (x1): dynamic=['False'], direction=['Out']
- `RoadWidthOutputKnob` (x1): dynamic=['False'], direction=['Out']

## 3. How connections are encoded

Each file has one flat `<Connections>` list of `<Connection port1ID="X" port2ID="Y" />` elements. `X`/`Y` are **Port IDs**, unique only within that file's `<Nodes>` section (never a Node ID directly) - a port's owning node is found by scanning `<Node>` elements for a child `<Port ID="X">`.

`port1ID`/`port2ID` are **not source/target** - the order carries no meaning. Direction comes from the port's own record: a dynamic port (`dynamic="True"`) carries an explicit `<Direction name="direction">In</Direction>` or `Out`; a fixed port (`dynamic="False"`) is inferred by name convention (`...OutputKnob` => Out, `...InputKnob` => In) or, for ambiguous fixed "parameter" knobs (e.g. `FrequencyKnob`, `AverageKnob`, `AngleKnob`, `BaseKnob`, `MineablesKnob`), by fixpoint propagation across every connection that touches a port whose direction is already known (a connection always pairs exactly one Out port with one In port). Data flow is producer(Out) -> consumer(In).

Literal example, `LandformDesertPlateau.xml`:

```xml
<Connection port1ID="17" port2ID="0" />
```

port 17 = "OutputKnob" (Out) on Node ID=7 ("Linear Function", type=gridLinear); port 0 = "InputKnob" (In) on Node ID=2 ("Preview", type=gridPreview). Data flows producer -> consumer.

**30 connections across the corpus could not be resolved to an Out/In pair** (both ends stayed ambiguous - i.e. neither end's port name nor any chain of connections reached a `...OutputKnob`/`...InputKnob`/explicit-Direction port). First few: [('LandformRiver.xml', '40', '75'), ('LandformRiver.xml', '41', '76'), ('LandformRiver.xml', '56', '67'), ('LandformRiver.xml', '57', '68'), ('LandformRiver.xml', '84', '120')]

## 4. Output/terminal nodes and manifest/requirement nodes

### `landformManifest`

- `<string name="DisplayName">`: [''] (44 occurrences)
- `<boolean name="DisplayNameHasDirection">`: ['false', 'true'] (44 occurrences)
- `<string name="Id">`: 44 distinct values, first 8: ['Archipelago', 'Atoll', 'Badlands', 'Caldera', 'Canyon', 'CaveEntrance', 'Cirque', 'Cliff'] ...
- `<boolean name="IsCustom">`: ['false'] (44 occurrences)
- `<boolean name="IsEdited">`: ['false'] (44 occurrences)
- `<boolean name="IsExperimental">`: ['false'] (44 occurrences)
- `<boolean name="IsInternal">`: ['false', 'true'] (35 occurrences)
- `<int name="RandSeed">`: ['1333644392'] (44 occurrences)
- `<int name="RevisionVersion">`: ['3', '1', '2', '6', '4', '5'] (44 occurrences)
- `<long name="TimeCreated">`: range [1653353880001.0 .. 1726163992280.0] (44 occurrences, 44 distinct)

### `worldTileReq`

- `<boolean name="AllowSettlements">`: ['false', 'true'] (43 occurrences)
- `<boolean name="AllowSites">`: ['false', 'true'] (43 occurrences)
- `<float name="CaveChance">`: range [0.0 .. 1.0] (43 occurrences, 12 distinct)
- `<float name="Commonness">`: range [0.008379889 .. 1.0] (43 occurrences, 23 distinct)
- `<int name="RandSeed">`: ['351232153', '2118777191'] (43 occurrences)
- `<Topology name="Topology">`: 15 distinct values, first 8: ['CoastAllSides', 'Inland', 'CliffValley', 'CaveEntrance', 'CliffThreeSides', 'CliffOneSide', 'CliffAndCoast', 'CliffTwoSides'] ...
- `FloatRange name="AvgTemperatureRequirement"`: min in [-100.0 .. 2.259887], max in [-20.3389835 .. 100.0]
- `FloatRange name="BiomeTransitionsRequirement"`: min in [0.0 .. 0.0], max in [6.0 .. 6.0]
- `FloatRange name="DepthInCaveSystemRequirement"`: min in [0.0 .. 0.0], max in [0.0 .. 10.0]
- `FloatRange name="ElevationRequirement"`: min in [-1000.0 .. 745.7627], max in [388.571442 .. 5000.0]
- `FloatRange name="HillinessRequirement"`: min in [1.0 .. 6.0], max in [1.45197737 .. 6.0]
- `FloatRange name="MapSizeRequirement"`: min in [0.0 .. 250.0], max in [0.0 .. 1000.0]
- `FloatRange name="RainfallRequirement"`: min in [0.0 .. 706.214661], max in [437.853119 .. 5000.0]
- `FloatRange name="RiverRequirement"`: min in [0.0 .. 0.502285659], max in [0.0 .. 1.0]
- `FloatRange name="RoadRequirement"`: min in [0.0 .. 0.05142857], max in [0.0 .. 1.0]
- `FloatRange name="SwampinessRequirement"`: min in [0.0 .. 0.5480226], max in [1.0 .. 1.0]
- `FloatRange name="TopologyValueRequirement"`: min in [-1.0 .. -1.0], max in [1.0 .. 1.0]

### `outputBiomeGrid`

- `<int name="RandSeed">`: ['1237655550', '807867685', '1789817781', '2129679617'] (4 occurrences)
- Port `BiomeGridKnob`: dynamic=['False'], direction=['In']
- Port `BiomeTransitionKnob`: dynamic=['False'], direction=UNKNOWN

### `outputCaves`

- `<int name="RandSeed">`: ['1750516046', '652404239', '1309280291'] (5 occurrences)
- Port `InputKnob`: dynamic=['False'], direction=['In']
- Port `OutputKnob`: dynamic=['False'], direction=['Out']

### `outputElevation`

- `<int name="RandSeed">`: range [297073253.0 .. 1918357657.0] (34 occurrences, 11 distinct)
- Port `InputKnob`: dynamic=['False'], direction=['In']
- Port `OutputKnob`: dynamic=['False'], direction=['Out']

### `outputFertility`

- `<int name="RandSeed">`: ['1042686644'] (3 occurrences)
- Port `InputKnob`: dynamic=['False'], direction=['In']
- Port `OutputKnob`: dynamic=['False'], direction=['Out']

### `outputNamed`

- `<string name="Name">`: 10 distinct values, first 8: ['coastNoise', 'lakeNoise', 'riverCoastalBuildup', 'riverHideMask', 'river', 'riverFlowValue', 'riverFlowOffset', 'riverDistance'] ...
- `<int name="RandSeed">`: range [18978246.0 .. 2138337347.0] (54 occurrences, 35 distinct)
- `<string name="TypeId">`: ['GridFunc', 'ValueFunc'] (54 occurrences)
- Port `Value`: dynamic=['True'], direction=['In']

### `outputScatterers`

- `<int name="RandSeed">`: range [54184704.0 .. 1936058131.0] (18 occurrences, 13 distinct)
- Port `CaveHivesKnob`: dynamic=['False'], direction=['In']
- Port `MineablesKnob`: dynamic=['False'], direction=['In']

### `outputTerrain`

- `<int name="RandSeed">`: ['842846725', '1207926160', '276299414', '1441011932', '1375216286', '1652175673', '1149281262', '862575613'] (33 occurrences)
- Port `BaseKnob`: dynamic=['False'], direction=['In']
- Port `CaveKnob`: dynamic=['False'], direction=['In']
- Port `StoneKnob`: dynamic=['False'], direction=['In']

### `outputTerrainPatches`

- `<int name="RandSeed">`: ['298118684', '1331185592', '705053841'] (3 occurrences)
- Port `FrequencyKnob`: dynamic=['False'], direction=UNKNOWN
- Port `LacunarityKnob`: dynamic=['False'], direction=UNKNOWN
- Port `OffsetKnob`: dynamic=['False'], direction=['In']
- Port `PersistenceKnob`: dynamic=['False'], direction=UNKNOWN

### `outputWaterFlow`

- `<int name="RandSeed">`: ['1209735150'] (1 occurrences)
- Port `FlowAlphaKnob`: dynamic=['False'], direction=['In']
- Port `FlowBetaKnob`: dynamic=['False'], direction=['In']
- Port `RiverTerrainKnob`: dynamic=['False'], direction=['In']

## 5. The `pos=` attribute

`pos="x,y"` on `<Node>` is the GraphEditor canvas layout coordinate only. Confirmed structurally: `<Connection>` elements reference only Port IDs, `<Variable>`/`<Object>` elements reference only refIDs and typed list contents - nowhere in the schema is a node's `pos` value read back by ID, index or coordinate match. As corroborating evidence, the two always-first nodes (`landformManifest` ID=0 and `worldTileReq` ID=1) carry the **same literal placeholder pos across every file** (`landformManifest` pos values seen: ['-950,-517']; `worldTileReq` pos values seen: ['-950,-357', '-950,-517']), i.e. the editor never bothers to lay these two out and nothing downstream cares. A generator can therefore emit any pos (or a fixed grid layout) safely.

## 6. Minimal-graph sketch (DesertPlateau: Perlin sources -> outputs)


Backward trace to Node ID=19 "Terrain Output" (type=outputTerrain):
  Node 3 (terrainGridPreview, port "OutputKnob") -> Node 19 (outputTerrain, port "BaseKnob")
  Node 20 (terrainGridPreview, port "OutputKnob") -> Node 19 (outputTerrain, port "StoneKnob")
  Node 28 (gridSelectTerrainGrid, port "OutputKnob") -> Node 3 (terrainGridPreview, port "InputKnob")
  Node 27 (gridSelectTerrainGrid, port "OutputKnob") -> Node 20 (terrainGridPreview, port "InputKnob")
  Node 8 (gridPreview, port "OutputKnob") -> Node 28 (gridSelectTerrainGrid, port "InputKnob")
  Node 29 (terrainGridNaturalRock, port "OutputKnob") -> Node 28 (gridSelectTerrainGrid, port "Option 2")
  Node 25 (outputElevation, port "OutputKnob") -> Node 27 (gridSelectTerrainGrid, port "InputKnob")
  Node 26 (terrainGridNaturalRock, port "OutputKnob") -> Node 27 (gridSelectTerrainGrid, port "Option 1")
  Node 10 (gridRotate, port "OutputKnob") -> Node 8 (gridPreview, port "InputKnob")
  Node 33 (gridPreview, port "OutputKnob") -> Node 25 (outputElevation, port "InputKnob")
  Node 4 (gridOperator, port "OutputKnob") -> Node 10 (gridRotate, port "InputKnob")
  Node 11 (valueRandom, port "OutputKnob") -> Node 10 (gridRotate, port "AngleKnob")
  Node 32 (gridPreview, port "OutputKnob") -> Node 33 (gridPreview, port "InputKnob")
  Node 2 (gridPreview, port "OutputKnob") -> Node 4 (gridOperator, port "Input 1")
  Node 6 (gridPreview, port "OutputKnob") -> Node 4 (gridOperator, port "Input 0")
  Node 31 (gridOperator, port "OutputKnob") -> Node 32 (gridPreview, port "InputKnob")
  Node 7 (gridLinear, port "OutputKnob") -> Node 2 (gridPreview, port "InputKnob")
  Node 5 (gridPerlin, port "OutputKnob") -> Node 6 (gridPreview, port "InputKnob")
  Node 30 (gridPreview, port "OutputKnob") -> Node 31 (gridOperator, port "Input 0")
  Node 35 (gridPreview, port "OutputKnob") -> Node 31 (gridOperator, port "Input 1")
  Node 9 (valueRandom, port "OutputKnob") -> Node 7 (gridLinear, port "Span px")
  Node 9 (valueRandom, port "OutputKnob") -> Node 7 (gridLinear, port "Span nx")
  Node 9 (valueRandom, port "OutputKnob") -> Node 7 (gridLinear, port "Span pz")
  Node 9 (valueRandom, port "OutputKnob") -> Node 7 (gridLinear, port "Span nz")
  Node 22 (gridOperator, port "OutputKnob") -> Node 30 (gridPreview, port "InputKnob")
  Node 34 (gridLinear, port "OutputKnob") -> Node 35 (gridPreview, port "InputKnob")
  Node 21 (gridPerlin, port "OutputKnob") -> Node 22 (gridOperator, port "Input 0")
  Node 23 (gridFromValue, port "OutputKnob") -> Node 22 (gridOperator, port "Input 1")
  Node 24 (valueWorldTile, port "HillinessOutputKnob") -> Node 23 (gridFromValue, port "InputKnob")
  Perlin source node IDs feeding this chain: ['21', '5']

Backward trace to Node ID=25 "Elevation Output" (type=outputElevation):
  Node 33 (gridPreview, port "OutputKnob") -> Node 25 (outputElevation, port "InputKnob")
  Node 32 (gridPreview, port "OutputKnob") -> Node 33 (gridPreview, port "InputKnob")
  Node 31 (gridOperator, port "OutputKnob") -> Node 32 (gridPreview, port "InputKnob")
  Node 30 (gridPreview, port "OutputKnob") -> Node 31 (gridOperator, port "Input 0")
  Node 35 (gridPreview, port "OutputKnob") -> Node 31 (gridOperator, port "Input 1")
  Node 22 (gridOperator, port "OutputKnob") -> Node 30 (gridPreview, port "InputKnob")
  Node 34 (gridLinear, port "OutputKnob") -> Node 35 (gridPreview, port "InputKnob")
  Node 21 (gridPerlin, port "OutputKnob") -> Node 22 (gridOperator, port "Input 0")
  Node 23 (gridFromValue, port "OutputKnob") -> Node 22 (gridOperator, port "Input 1")
  Node 24 (valueWorldTile, port "HillinessOutputKnob") -> Node 23 (gridFromValue, port "InputKnob")
  Perlin source node IDs feeding this chain: ['21']

