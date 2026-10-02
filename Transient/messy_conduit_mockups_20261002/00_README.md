# Messy Conduit — phase-0 mock-ups (2026-10-02)

Offline PNGs for the owner to pick from (MESSY_CONDUIT_MOD_1, design §8). No game or bridge
was used. Renderer, scene and selftest: `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\mockups\messy_conduit\`
(`render.py --seed N` re-renders this exact set; the output is deterministic).

## Files

| file | shows |
|---|---|
| `00_overview.png` | all four styles side by side, DEFAULT messiness, same network |
| `0Na/b/c_<style>_<level>.png` | the base scene at 80 px/cell, messiness 1 tidy-ropey / 2 ropey-jury-rigged (DEFAULT) / 3 rat's nest |
| `0Ns_<style>_swatches.png` | close-ups at 110 px/cell: every strand type, the default bundle, T and X junctions, splice/joiner, slack loop, capped stub + spare coil, over-a-wall, into-rock grommet, trunk wrap, lamp-post climb, machine hookups, break live vs dead |
| `0Nt_<style>_break.png` | break readout: 4 frames of the live end (whip + sparks) beside the still dead end, plus a power-off panel where both ends read dead |

Styles: **01 Cybertek** (sleek silver/graphite metallic, chrome ferrules, hex pods with a cyan light) ·
**02 Extension cord** (glossy orange/green/brown/yellow/blue, power-strip junctions, plug-into-socket joiners, unplugged plug heads as caps) ·
**03 Star Wars friendly** (thick black rubber, corrugated steel hose, coiled black cord, greebled boxes) ·
**04 Jawa** (faded orange cord, ribbed armoured grey, red/black twin-lead, bare copper, braided green, greasy black; tape lumps, hose clamps, rag caps, ration-tin box, grease).

## Grid key (columns A.., rows 0.. — printed on every scene)

| cells | what |
|---|---|
| E3:F4 | generator, the only power source |
| G4..L4, L4:L7 | main line; L4..L7 runs ON TOP of the west wall (stapled), then drops into the room along row 7 |
| H6..J8 | a closed conduit loop around the lamp post at I7; J5 links it to the main line |
| I7 | lamp post; its hookup sags in from I8 and is taped up the post |
| H9..E9 | branch west; wraps the tree trunk at G9 |
| **D9** | **the break** (one-cell gap): E9 live end sparks and whips, C9 dead end lies limp |
| B9..B11 | dead side of the break, feeding the console at C11 (screen off: unpowered) |
| P7 | X junction: north to the workbench N3:P3, south under the door at P10 |
| S7 | T junction: north to the battery bank S3:T3 |
| U7 | end of the main line, hooked into the heater at U8 |
| P12 | lone dead end: a deliberate capped stub (never sparks) |
| E12, R8, N8, K11, M9 | floor items, always drawn over wires |

## Knobs (`styles.py`)

Per level: strands per run (1-2 / 2-3 / 3-4), bundle spread, wander, sag, floor-loop chance,
splice chance, spare-coil chance, extra tape, grease, hookup strand count and hookup sag.
Per style: strand kinds with weights, widths and colours, surface pattern (gloss, metal, rubber,
corrugated, coil, twin-lead, braid, bare copper), junction/splice/cap decals, wander scale and grease.
`--seed` changes every random pick (strand mix, loops, splices) without changing the network.

## What would differ in game (honest limits)

- **Procedural placeholders, not shipping art.** Every texture is drawn from code; the in-game set
  would be ~23-26 painted strips and decals (§8.8). Treat these as layout, colour and density studies.
- **Static frames.** Sway, whip and sparks are drawn as poses. In game sparks are vanilla
  MicroSparks/LightningGlow flecks; whip is per frame; sway depends on the CutoutPlant shader (unverified, §8.9).
- **Simplified occlusion.** Painter's order here is per layer, not the matched-Y depth trick (§8.3);
  a tree or lamp directly south of a wrap is not tested in this scene.
- **Scene art is a stand-in.** Walls, machines, tree and lamp are not vanilla sprites, and the zoom is
  fixed at 80 px/cell (110 for swatches). Far-zoom shimmer and the LOD swap are not shown.
- **Rat's nest is capped**: sprawl is clamped to 0.38 cell per the clipping rule, so even level 3 stays
  close to its own cells. It can go wilder if that rule is relaxed.
- **Known weak spots:** the trunk wrap reads small at scene zoom (clearer in the swatch). The Star Wars
  coiled cord reads as ribbed black cable at 80 px/cell. Hookups into a machine straight north of the
  conduit hang nearly vertical, so their sag is subtle.

## What the owner is asked to judge

1. Which style(s) ship, and whether 04 Jawa is the default or the campaign-only set.
2. Which messiness level is the default (proposed: level 2).
3. Whether the break readout (live sparks vs limp dead end) reads at a glance.
4. Wire on the wall top and the trunk wrap: keep, change or drop.
