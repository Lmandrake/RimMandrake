# GL_GRAPH_EMITTER_1 — write Geological Landforms recipe files from Python

Spec source: `design/RimMandrake/map_content_injection_research.md` §9.3 step 6, route
decided by §5.8 (P17 CONFIRMED 2026-09-06: GL loads and renders a landform file we
wrote). This is the map generator's terrain APPLY path: the generator produces a
landform graph; GL evaluates it in-engine at mapgen with real elevation, terrain,
fertility, caves and water flow. Data only — no C#.

## spec

- Input schema: `research/RimMandrake/reference/gl_landform_schema.md` (79 node
  types; `<Connection port1ID port2ID/>` pairs Port IDs, order meaningless, direction
  from the port record or name; fixed-knob directions for gridPerlin's parameter
  knobs are UNKNOWN there — never wire them until proven). Regenerate with
  `src/RimMandrake/Utils/rimbench/gl_schema_census.py`.
- Build `src/RimMandrake/Utils/rimbench/gl_emit.py`: a small typed builder —
  `Graph()`, `g.node(type, name, **fields)`, `g.connect(src_node, out_port_name,
  dst_node, in_port_name)`, `g.manifest(id, display_name)`, `g.tile_req(...)`,
  `g.write(path)` — that emits a `NodeCanvas` XML byte-compatible with the 44
  shipped files: same element/attribute order, same `pos=` layout attrs (any
  values), unique Port IDs, `RandSeed` per node, `IsCustom=true`.
- Proof of shape, OFFLINE: rebuild `LandformDesertPlateau.xml` from the builder
  (read the source, express it as builder calls, emit) and show the census script
  parses the emitted file to the SAME node-type multiset, field values and
  connection set as the original (a normalised diff, ignoring IDs/pos/seeds). Add
  that as the selftest (`--selftest`, prints `SELFTEST PASS N/N`).
- Then ONE variant the builder makes on purpose: DesertPlateau with the primary
  Perlin `Frequency` as a parameter and `Id=RUT_EmitterPlateau`, written to
  `Transient/RUT_EmitterPlateau.xml`. The LIVE proof (parent does it, not a
  subagent — one bridge driver): drop in `Config\CustomLandforms-v1\`, restart on
  minimal+GL, quicktest, `Map generator context: … Landforms: RUT_EmitterPlateau`
  in Player.log, screenshot. Then REMOVE it from the live config (commonness
  hijack, §5.8 d).
- Do not target the 14 Odyssey-disabled Ids (§5.8 c). Do not touch the workshop
  folder.

## verify

```
PROVE   census(emitted DesertPlateau) == census(original) modulo IDs/pos/seeds; and GL log names RUT_EmitterPlateau on a quicktest
EXPECT  0 field diffs, 35 connections both sides; log line present within one quicktest
LIES    GL silently skips a malformed custom file (no log line) and the stock landform draws — the log's 'Landforms:' field is the only proof, a plateau on screen is not
```

## not chasing

Composing NEW shapes, node semantics beyond what the rebuild needs, the generator's
chooser (`MACRO_GENERATOR_V0_1`).
