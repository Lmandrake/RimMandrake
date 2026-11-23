# Jetty and bridge art: the generated options

Item: `RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD`. Written 2026-11-22 by a detached art run.
Status: options for the owner's pick. No art is installed in the mod. The procedural options and the design are in
`design.md` beside this page.

## Where to look

Folder: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_REDESIGN_JETTY_AND_BRIDGE_ART_STEEL_ONE_READS_AS_WOOD\generated\`

| sheet | what it shows |
|---|---|
| `overview_generated.png` | the review sheet: every generated option at default zoom, east/west and north/south |
| `steel_jetty_generated.png`, `heavy_jetty_generated.png` | the jetties: 2 options each |
| `bridge_scrapper_generated.png`, `bridge_industrial_generated.png`, `bridge_modern_generated.png`, `bridge_futuristic_generated.png` | stations 61-64: 2 options per look |
| `heavy_bridge_generated.png` | the heavy bridge: 2 options |
| `four_looks_one_pick_each.png` | the recommended pick per look, side by side at default zoom |
| `seams\<option>.png` | each deck's pieces joined at 1, 2 and 4 cells east/west, and 4 cells north/south |

Each option sheet shows the generated option at close zoom (128 px per cell, a vanilla colonist at the same scale) east,
west, north and south, the procedural geometry it was built on beside it, and the option again at default zoom (40 px per
cell). Every scene is over the real pit from his 2026-11-22 walk capture. The sheets are uncompressed PNGs on the warm
dark-brown page.

## What was generated (Codex image generation, 22 pictures, 4 of them redone)

- **Decks:** one long painted strip per option. `gen_tiles.py` straightens it, scales it to the option's deck width and
  cuts it into ROOT, MID, TIP and SOLO pieces (`design.md` §2). MID repeats seamlessly, and every joint between pieces is
  a joint between two places of the same painted strip.
- **Posts and towers:** 12 sprites (3 pictures of 4), drawn the way RimWorld draws tall things (rising north).
- **Cables:** 6 textures (1 picture): black steel wire rope, galvanised wire, rusty lashed wire, chain, graphite with cyan
  clamps, graphite with magenta clamps. Each is laid along the run of each cable, hanger, A-frame leg or beam.
- The geometry (where posts stand, where cables run, the shadows) is `render.py`'s, so each generated option sits on the
  geometry it was built on.

| kind | generated options (built on geometry) | why these two |
|---|---|---|
| steel jetty | B open grating, C gangway truss | GPT was asked with the procedural sheets attached; agreed |
| heavy jetty | A cast slab, B box girders | the same |
| bridge, Scrapper | A patchwork plate, C hull plate and chain | the widest spread between the four looks |
| bridge, Industrial | A diamond plate, C sand-grey standard issue | the same |
| bridge, Modern | A galvanised grating, B green steel | the same |
| bridge, Futuristic | A white and cyan, B graphite and magenta | the same |
| heavy bridge | A cast slab, B box girders | follows the heavy jetty |

Jetties are drawn in the Industrial finish only. Prompts: `src/RimMandrake/FlowWorks/art_source/JettyBridgeRedesign/gen_prompts.py`.
Pieces (committed): `.../JettyBridgeRedesign/generated/`. Raw generations: `D:\ClaudeWork\rimmandrake\art\jetty_bridge_gen\raw\`.

## Validation [measured]

`python3 gen_tiles.py check` reads 0 of 14 decks rejected:

- every piece is 256 x 256 RGBA with real alpha, and no deck touches the top or bottom of its canvas;
- the deck runs to the piece edge wherever a piece meets another piece;
- the joints at 1, 2 and 4 cells, east/west and north/south, score 0.03 to 0.90 against a limit of 1.15. The score is
  the largest colour jump within 3 px of a joint, divided by the same statistic away from joints.

`python3 gen_tiles.py selftest` PASS. The check goes red on two planted faults: today's framed jetty pictures side by side
score inf (a transparent gap at the joint), and a TIP shifted 6 px scores 1.33 to 2.03. It stays green on clean cuts.

The check also found two real faults (a Futuristic panel line and a heavy-slab rail clamp within 25 px of a joint,
against design.md §2 rule 2). The cutter now takes the repeating piece where no cross-line falls near a joint.

## The judge (GPT, against `art_judge_brief.md` and the look briefs). Verdicts: `judge/` beside this page

| option | first verdict | repair | second verdict |
|---|---|---|---|
| steel jetty B | REDO: cable ends in midair | cables land on the deck at a bolted clamp (all options) | KEEP |
| steel jetty C | REDO: A-frame cables cross the walkway north/south | twin lattice masts | KEEP |
| heavy jetty A | KEEP | | |
| heavy jetty B | REDO: portal crossbeam reads as a gate | no crossbeam, twin box columns | KEEP |
| Scrapper A | REDO: reads as a wooden footbridge at default zoom | new deck (bare steel-grey plates), steel wire cables | KEEP |
| Scrapper C, Industrial A and C, Modern A, Futuristic A, heavy bridge A | KEEP | | |
| Modern B | REDO: heavy bolted joint plates read as Industrial | new deck, slim galvanised end angles | KEEP |
| Futuristic B | REDO: centre pylon cables cross the walkway north/south | twin slim pylons | KEEP |
| heavy bridge B | REDO: crossbar over the walkway; the cement does not show | no crossbar, concrete pylons | KEEP |

The first Futuristic decks had exposed bolts, which the look brief bars. They were generated again with flush couplings
before judging.

**The four-look bar FAILS** ("the four looks must be unmistakably different at default zoom"). The judge FAILED all eight
options together, and FAILED them again after a repair: each look now has its own structure (Scrapper low and slack,
Industrial massive with heavy cables, Modern slim and sparse, Futuristic tall and taut). The pairs it can confuse are
Industrial C with Modern A, Scrapper A with Industrial A, and Industrial C with Modern B. It also FAILED the recommended
one-per-look set (Scrapper C, Industrial A, Modern A, Futuristic B), because Industrial and Modern share the suspension
silhouette and differ mainly in finish. To pass, at least the Modern bridge needs a different structure, not a different
surface. That is a design change (§Next).

## Recommended picks

- Steel jetty **B** (open grating). It reads as steel at every zoom, and its cables run clear of the walkway.
- Heavy jetty **A** (cast slab). Its first verdict was KEEP, and it reads as concrete and steel.
- Bridges: Scrapper **C** (rusty chain), Industrial **A** (gunmetal diamond plate), Modern **A** (galvanised grating with
  yellow rails), Futuristic **B** (graphite and magenta). These are the judge's best fits for the looks. Heavy bridge
  **A**.

## Untested

- Nothing was seen in game. The scenes imitate the game's draw. The cable altitude over a moving pawn is the guess in
  `design.md` §3.
- North/south pieces are the east pieces turned by 90°. The painted light turns with them. The seam check is the same
  both ways; the light was judged only by eye.
- A bridge longer than 2 cells repeats MID once per cell. The heavy box-girder deck (jetty and bridge B) has panels
  shorter than a cell, so a faint panel joint repeats per cell on a long bridge.
- The anchor blocks on the ledges are the procedural placeholders, not generated art.
- The jetties were generated in the Industrial finish only. The other three looks of each jetty are not generated.

## Next

The owner picks one option per kind. The four-look bar of 61-64 stays open: a different structure for the Modern (and
perhaps Futuristic) bridge goes to the Designer.
