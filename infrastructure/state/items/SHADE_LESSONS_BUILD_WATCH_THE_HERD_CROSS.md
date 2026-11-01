## spec
The design is `design/RimMandrake/shadecraft_lessons_design_2026-10-31.md`; it has the defNames, the
biome source table and the code facts. The answers it builds:

1. **Which lesson serves which piece.** Lessons teach ideas, and each piece needs two. Parasol:
   portable shade + deeper shade cloth. Tent: portable shade + keeping dew off.
2. **Cross-biome availability.** Plain research always unlocks the gear. Lessons only discount it.
   Each hot biome teaches its own lesson for the same gear.
3. **A herd crossing.** It progresses automatically for a colonist within sight of one.
4. **Mechanism.** Vanilla hidden research through `RM_FoundTechStudy`, the Forge spunstone pattern.

## criteria
- Selftest: both gear projects are reachable with no lessons at all.
- Selftest: one idea changes nothing; the second idea of a pair raises the project to 75%, and a
  second `Apply` does not raise it further.
- Selftest: a seen crossing adds one point, an unseen one adds none, and two watchers still add one.
- `RM_ShadeIdea_PortableShade` stays hidden until revealed, although no ThingDef carries it.
- Every source in the design's biome table carries its study comp after patching, with the mod
  composed into `mandrake.rm.biomes`.
- Mod Settings carries the toggle, and off degrades as the design's section 6 says.
- Quicktest on a Long Shade map: a colonist studies dewfringe, and a crossing is counted.
