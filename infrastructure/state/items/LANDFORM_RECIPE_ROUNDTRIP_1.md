# LANDFORM_RECIPE_ROUNDTRIP_1 — can Geological Landforms load a landform file WE wrote?

Spec source: `design/RimMandrake/map_content_injection_research.md` §9.3 step 1
(owner ruled "yes, go" 2026-09-06). This is the probe that decides the terrain
route for the map generator: if the engine accepts a recipe we wrote, the generator
writes recipes and the engine draws real rivers/caves/cliffs; if not, terrain goes
through a painted-mask worker of our own (P10) with a lower ceiling.

## spec

- Source recipe: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2773943594\1.6\Landforms-v1\LandformDesertPlateau.xml`
  (31 KB, `NodeCanvas type="GeologicalLandforms.GraphEditor.Landform"`, nodes
  `landformManifest`, `worldTileReq`, `gridPerlin`, `gridLinear`, `gridOperator`,
  `gridRotate`, `valueRandom`, previews).
- Drop location (EXISTS on this machine, empty or not — check first):
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\CustomLandforms-v1\`.
- Copy the file there; change `<string name="Id">` to `RUT_ProbePlateau`, set
  `IsCustom` true, change ONE visible parameter (a Perlin scale or the linear
  function's slope) so the result is distinguishable from stock DesertPlateau.
  Set `worldTileReq` requirements loose enough that a quicktest tile qualifies, or
  force it if GL offers a forced-landform debug path.
- Restart may be needed (GL loads landforms at startup via `LunarLoader`) — minimal
  list, ~22 s. Check GL's Keyed strings / README for hot-reload first.
- Prove it: (a) GL's in-game landform list / editor shows `RUT_ProbePlateau`;
  (b) Map Preview (installed, `m00nl1ght.MapPreview`) on a qualifying tile renders
  the modified shape; (c) one quicktest map on that tile, screenshot with a unique
  filename, LOOK at it.

## verify

```
PROVE   RUT_ProbePlateau appears in GL's landform list, and a preview/map shows the changed parameter
EXPECT  a plateau silhouette visibly different from stock DesertPlateau (state the parameter and the expected visual change BEFORE looking)
LIES    GL silently ignores a malformed custom file (no log line) and the stock DesertPlateau renders — that is why the parameter change must be VISIBLE, and why "a plateau appeared" is not a pass
```

Outcome goes into `map_content_injection_research.md` §5.7 as P17, CONFIRMED or
FAILED with the log line / screenshot path. Either answer closes this item and
decides which of §9.3 step 6's two routes gets filed.

## not chasing

Composing a NEW landform from scratch, GL node semantics, the emitter. One
parameter, one preview, one screenshot.
