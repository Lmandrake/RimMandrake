# FlowWorks line widths: the spec (owner, by question card, 2026-10-20 21:38 PDT)

Scale anchor: a cell holds 2,000 L per metre of depth, so it is about 1.41 m across. Cells are drawn at 64 px, which makes 1 m about 45 px.

| line | width | at 64 px per cell | note |
|---|---|---|---|
| rigid pipe | **30 cm** | about 14 px (about 1/5 of a cell) | water-main scale; readable at play zoom |
| flexible hose | **about half the pipe, about 15 cm** | about 7 px | The last walk measured the hose at about 2x the pipe, so the hose art gets thinner |
| flexible power cord (the new deck cord) | **the same thickness as Gimme Some Slack's overhead wires** | measure from GSS | one power look across the game |
| pipe-pole span sag | **about a third of GSS wire sag, about 2% of span** | — | GSS wires sag about 6%; the pipe looks stiffer but still hung |

The owner judges all of this in game before any new pipe-pole or cord art is made (pipes-across-pits ruling 8). Items: `LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED`, `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`, `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE`, `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS`.

## Measured, current art (BENCH, 2026-10-20 22:20 PDT)

- **Rigid pipe: on spec.** The straight cell of every `Pipe/<Look>/UniversalPipe_Atlas.png` (Scrapper, Industrial, Modern,
  Futuristic; 704 px atlas, 176 px per cell) has an opaque band (alpha > 16) of **14.5 px per 64 px cell = 0.227 cell**.
  Spec: about 14 px. No redraw queued.
- **Hose: about 3.5 to 4.3 times the spec, and the width is set in CODE, not by the art.** The strand textures
  (`Hose/Strand_Flat.png`, `Strand_Plump.png`, 256×64 strips) fill their strip and are stretched across a mesh whose width
  is `HoseMath.VisibleWidth` = `WidthScale × (FlatVisible 0.38 + PlumpExtra 0.085 × plump)` cell
  (`Source/Hose/HoseMath.cs`), i.e. **24.3 px flat, 29.8 px full plump** per 64 px cell at `WidthScale` 1 (the shipped
  value; Mod setting `RM_HoseSettings.thickness`). Spec: about 7 px (0.11 cell) ⇒ `WidthScale` ≈ 0.29 flat. Every
  fitting, wrap and clearance is sized from that width, so they follow it. **A redraw of the hose art cannot make the hose
  thinner**; none was queued. The change is the width constant or setting (FlowWorks code), then a look in game to see
  whether the strand art still reads at 7 px. Only if it does not is a redraw owed.
