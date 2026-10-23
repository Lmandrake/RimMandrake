# FlowWorks + Gimme Some Slack "Modern" look — style guide (2026-10-23)

Items `MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL` (folds in `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY`). This guide
extends `design/RimMandrake/flowworks_modern_art_brief.md` (tanks, reels, judge lines M1–M4, refs 1–18, F1–F12)
from the tanks and reels to the **whole** Modern family. Both are read by the generator (prompt material) and the
judge (`art_judge_brief.md` + M-lines + the S-lines below).

## The owner's words

- 2026-10-23, on the walk screenshot of the Modern solid pipe: *"solid pipe looks pretty horrible actually. We need
  a whole art review of the Modern style. You made it all enamel red. That was never the intention. See the comments
  from the Modern water tank critique. This is supposed to be stuff you can really see in the real world right now
  (modern), not just primary colors."*
- 2026-10-23: *"Modern should instead be thought of as "modern consumer / commercial" and industrial is "brutalist""*
- 2026-10-22 (tank critique): *"Modern water tanks. Modern hose reels. Like you would buy in home depot or find behind
  a modern store. Please re-examine the modern art to do much more than just paint things in primary colors. Search
  the web for real-world examples of modern versions of all this."*

**Style anchors (his picks, kept):** short tank A — white horizontal poly leg tank; tall tank B — dark-green vertical
poly tank; IBC tote (galvanised cage, white HDPE bottle); FA swinging-pedestal fire-hose reel (red is that product's
real colour). Every new Modern picture must sit beside those four as the same shop aisle.

## What Modern means

**Modern = what you can buy today at a home centre, an irrigation/plumbing supplier or see behind a store.** The
look comes from **product class, form and material**: extruded and moulded plastics (PVC, CPVC, HDPE, PEX, poly),
hot-dip galvanised or powder-coated steel, stainless, brass. Colour is whatever that product really is — mostly
white, grey, black, dark green, galvanised silver, brass — with small functional accents (a blue or red lever, a
printed spec line, a yellow gas-line stripe). The red-enamel repaint of the Industrial silhouettes is the defect.

## Judge lines (S = style; add to M1–M4)

- **S1. Product class first.** Each picture is recognisably one real product listed in §Per object. A silhouette
  that is another look's object recoloured is REDO (= M1). — Owner 2026-10-22/23
- **S2. No signature colour.** Modern has no house colour. Red appears only where the real product is red (fire
  reels, a valve lever, PEX-hot); the pipe network is never red. — Owner 2026-10-23 ("You made it all enamel red")
- **S3. Plastic reads as plastic.** Matte-to-satin sheen, soft rounded moulded edges, faint mould seam lines,
  socket bells at joins, printed spec text as a thin dash line (illegible). Glossy candy-chrome highlights read as
  toy enamel — REDO. — Lesson (this pass), from S1
- **S4. Clean-ish wear.** New-to-a-few-years-old: slight sun-chalking on plastic, dust at the base, galvanised
  spangle; **no rust, no rivets, no hazard stripes** (those belong to Scrapper/Industrial). — brief M2
- **S5. One network, one family.** Pipe, joins, under-collar, under-pipe, pipe span and pump ports share one pipe
  material so a run reads continuous; a join is visibly the same plastic as the pipe (a socket coupling), never a
  bolted coloured flange. — Owner 2026-10-23 screenshot (pipe run)
- **S6. Read at 32 px/cell on desert ground.** White PVC and black HDPE both read against the tan/brown ground;
  mid-grey on brown is the weak case — give it a darker keyline side and a lit top. — B2

## Palette (real product colours; options, never bans — B5)

| material | base | shade | light | notes |
|---|---|---|---|---|
| PVC Sch40 white | #ECEBE4 | #B9BAB2 | #FAFAF6 | satin; printed dash line #3B5A8C or #222 |
| PVC Sch80 / CPVC grey | #6B6F72 | #44484B | #9AA0A3 | commercial/industrial plumbing grey (CPVC is cream-tan #D9CDA8) |
| HDPE black poly | #232527 | #121314 | #4A4E52 | coloured ID stripe: blue #2E64B0 potable, purple #6B4C9A reclaimed, green #3D8A4A irrigation |
| PEX | red #B8322C / blue #2D5FA6 / white #EDEDE8 | | | crimp rings copper #B87333 |
| galvanised steel | #A7ACA8 | #7C817E | #CDD1CE | matte, spangle mottling, no gloss |
| stainless | #C3C8CC | #8E9499 | #E9ECEE | brushed, cool |
| brass | #B98E45 | #7E5E2A | #E2C27A | hose bibs, ball valves, couplings |
| poly tank green | #2F5A3A | #1E3D27 | #4B7A55 | owner pick B |
| resin taupe / peppercorn | #8A7F6E / #4A4744 | | | reel carts, valve boxes |
| garden hose green | #3E7B3A | #285226 | #69A35E | vinyl |
| rubber black | #2B2B2B | #161616 | #555 | commercial hose, gaskets |
| concrete (pads) | #9C978D | #77736B | #BDB8AE | precast pads only; raw massive concrete is Industrial |

## Per object (texPath stems under `Textures/`)

### Pipe — `RimMandrake/FlowWorks/Pipe/Modern/UniversalPipe_Atlas` (+ `_MenuIcon`)
Procedural: `src/RimMandrake/FlowWorks/art_source/pipe/build_pipe_atlas.py` cuts `raw/modern_strip.png` (a
straight top-down pipe) and `raw/modern_fittings.png` (LEFT a four-way junction, RIGHT an end cap) into the 4×4
linked atlas; geometry (18 px pipe = 0.136 cell, 36 px hub, palindromic period) is fixed by the script — only the
raw pieces change. **Chosen: white Sch40 PVC** (GPT round: strongest value separation on the desert ground at
32 px/cell, ties to the white tank/IBC anchors; black HDPE second, mid-grey third) — satin warm-white tube, cool
grey underside shade, **no printed line** (at 18 px the dash read as perforation, pipeline r1/r2); junction = a
white PVC **socket cross**, cut to a flat-sided tee where only three pipes meet; elbows carry a **white socket ring**
at each leg; end cap = a short **socket cap**; a lone pipe is a short length capped at both ends. Candidate builder:
`src/RimMandrake/FlowWorks/art_source/ModernStyle/pipe_candidate.py` (wraps the atlas script; geometry unchanged).
Real refs: P1–P4.

### Joins — `RimMandrake/FlowWorks/Joins/Modern/{Coupler,Flange,Saddle,UnderCollar,UnderPipe}`
Sizes come from the C#: Flange and Coupler are drawn at `LiquidJoinRule.FlangeSize` 0.5 cell on a 128 px canvas
(256 px/cell, so the 0.136-cell pipe is 35 px there); Saddle at `SaddleLength/Width` 1.0 cell on 256 px (35 px pipe).
- Coupler: a PVC **socket coupling** — a sleeve about 1.3× the pipe, same white, faint bell edges.
- Flange: a PVC **flange plate** (about 2× the pipe) with a socket hub and small stainless bolt heads, flush to the port edge.
- Saddle: a white PVC **clamp-on tapping saddle** (two straps, stainless bolts) on the continuous pipe, outlet sized
  to the hose (0.18 cell flat).
- UnderCollar: a light-grey moulded **wall sleeve** (matte plastic, not gunmetal); UnderPipe: the network's white PVC.
  Canvases and anchor positions stay identical (they are placed by C#).

### Pipe span — `RimMandrake/FlowWorks/PipePole/Modern/PipeSpan`
The same pipe material as the run (white PVC or grey) with one **galvanised pipe hanger strap**; seamless ends.

### Faucet — `RimMandrake/FlowWorks/Faucet/Modern/RM_PipeFaucet`
A **brass hose bib / ball-valve spigot**: brass body, quarter-turn lever (vinyl-dipped, blue or yellow) or a small
round handwheel in die-cast silver; threaded hose outlet pointing down-front; sitting on a white PVC riser stub with
a socket. Ref P5 (frost-free sillcock / hose bibb listings).

### Sprinkler — `RimMandrake/FlowWorks/Sprinkler/Modern/RM_SprinklerHead`
A **brass impact sprinkler** on a short black riser in a white PVC socket (the iconic arm and deflector — the
clearest small-scale silhouette, GPT round). Ref S1–S2 (Rain Bird 25BPJ impact; 12SA/22SA/5000, 8005 rotors).

### Pump — `RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump` (1×1 cell, 512 px, four ports N/E/S/W)
A **compact electric booster pump** (ribbed charcoal motor, thermoplastic pump housing, small pressure switch and
gauge, black base) **plus a separate PVC manifold**: an ordinary pump with four equal casing ports is not credible
(GPT round). The four port stubs are the network's own pipe, **exactly the drawn pipe width** (0.136 cell = 70 px on
512), with slim union rings (1.25×), ending at the four edge midpoints — owner 2026-10-23: *"We should
unfortunately regen the pumps and such to have connectors that match the more modern pipe and hose sizes. looks a
bit silly."* Builder: `ModernStyle/pump_stubs.py`. Refs: brief ref 18; Pentair/Flotec thermoplastic jet pump.

### Hose parts — `RimMandrake/FlowWorks/Hose/Styles/Modern/*`
The FA fire-hose reel is kept, so hose parts stay **fire/commercial**: Strand = red-or-black commercial rubber
hose or white lay-flat fire hose (current cream canvas is acceptable); Coupling/EndCap = brass or anodised
aluminium Storz / NST couplings (less chrome mirror, more cast-metal satin); Nozzle = lever shutoff or fog nozzle
(already fine); Binding = stainless hose clamp band. **A hose lies flat on the ground, so its end is seen from
above with no bore** (C6) — owner 2026-10-23 on the free end: *"the end of this hose looks horrible."* The bare free
end (`Mouth`, drawn 0.30 × 0.86 of the hose width on the wrap's outer face, `RM_MapComponent_Hoses.DrawEnds`) is a
canvas lip, never a dark ring; couplings end in a flat side-on edge. The same bore-at-the-camera `Mouth.png` ships
in **every** look: `Hose/Mouth.png` (Scrapper/default), `Hose/Styles/Industrial/Mouth.png` (black ring),
`Hose/Styles/Futuristic/Mouth.png` (cyan ring) — listed on item `HOSE_END_REDRAW_STARES_AT_CAMERA`.
**Connector sizing (all fixtures):** pipe 0.136 cell (`build_pipe_atlas.W_PIPE`), hose 0.18 cell flat
(`HoseMath.FlatVisible`); a fixture's pipe connector is the pipe width, a hose outlet the hose width.

### Containers — `Things/Item/Resource/FlowWorks/Modern/RM_{Barrel,Bottle,Bucket}` (+ `_m`)
Barrel: a **plain blue HDPE 55-gal drum** (two bung caps on top, moulded rings, no stripes). Bucket: a **5-gal
HDPE bucket** — orange (the Home Depot "Homer") or white, wire bail handle with a black grip. Bottle: clear PET
with a plain one-colour label band. The `_m` masks must be re-derived with the picture.

### Weir — `RimMandrake/FlowWorks/Weir/Modern/RM_BankWeir_*`, `RM_BankWeirCap`
A removable weir board is an irrigation **stoplog**: extruded aluminium boards stacked in a **galvanised guide
channel**; the cap is the channel's galvanised head fitting (GPT round: sheet piling is a retaining wall, the wrong
mechanism). Spill overlays are water and stay. Not redrawn this pass.

### Bridges — `Drawbridge/*_Modern*`, `SuspensionBridge/Modern/*`
**Hot-dip galvanised** steel frames and anchors (matte spangle grey), **composite decking** (grey/brown boards)
or **FRP / galvanised bar grating**, black powder-coated railing, and safety yellow only on real edge markings.
Red rails and red anchor blocks go. Winches: a galvanised trailer/utility winch with a black motor can (the steel
winch) or a hand-crank boat winch with a strap (timber winch).

### Gimme Some Slack — `GimmeSomeSlack/{Styles,Aerial/Styles}/Modern/*`
Already consumer/commercial: galvanised pole with cobra-head LED (ref P7), grey weatherproof disconnect box, drum-
shade floor lamp, orange-handled clamp. Extension cords are the ExtCord strands (orange/yellow/green — real cord
colours) and are not look-specific. No redraw proposed.

## Industrial = brutalist (keep the two apart)

Industrial is **brutalist**: raw board-marked concrete, massive cast iron, heavy plate steel with exposed bolts,
monolithic blocky forms, dark weathered greys, weight over finish. Where Modern is a light moulded product off a
shelf, Industrial is a heavy object cast or poured in place. So: Modern never uses concrete as the body of a thing
(only as a precast pad), never cast iron, never heavy bolt circles; Industrial never uses moulded plastic, product
colours, or thin consumer forms. Today's Industrial art reads as *"industrial safety"* — black steel and yellow-
black hazard stripes — rather than brutalist; the mismatches are listed in the item filed for it
(`INDUSTRIAL_BRUTALIST_AUDIT_POUR_THE_CONCRETE`) and in
`Transient/modern_style_20261023/industrial_mismatches.md` (not redrawn in this pass).

## References (web; reference only, never traced)

- P1 Charlotte Pipe white Sch40 PVC tee, Home Depot — https://www.homedepot.com/p/203812195
- P2 UPVC pipe and fitting (Commons, CC BY-SA 4.0) — https://commons.wikimedia.org/wiki/File:UPVC_pipe_and_fitting.jpg
- P3 HDPE pipe installation (Commons, CC BY-SA 3.0) — https://commons.wikimedia.org/wiki/File:Hdpe_pipe_installation.jpg ;
  HDPE irrigation pipe with green ID stripe — https://dvs-beregnung.de/25m-pe-tube-pn16-25mm-green-stripe_1
- P4 PEX tools and fittings (Commons, CC BY-SA 3.0) — https://commons.wikimedia.org/wiki/File:PEX_installation_tools_and_fittings.jpg ;
  Uponor AquaPEX red — https://www.supplyhouse.com/Wirsbo-Uponor-F2061000-1-AQUAPEX-Red-300-ft-coil
- P5 Frost-free brass sillcock — https://www.doitbest.com/product/454920/proline-chrome-plated-brass-1-2-in-pex-x-3-4-in-mht-6-in-frost-free-sillcock-454920
- P6 2" water transfer pump, Honda GC160 — https://www.barrplastics.com/products/water-transfer-pump-with-gas-powered-5hp-honda-wp-2050hl ;
  Honda WX10 — https://www.russopower.com/collections/pumps/products/honda-wx10k1at-1-in-water-pump
- P7 NYC davit pole, galvanised, LED cobra head — https://www.nycstreetdesign.info/node/598
- S1 Rain Bird 12SA pop-up rotor (black body) — https://www.acehardware.com/departments/lawn-and-garden/watering-and-irrigation/underground-sprinklers/7014750
- S2 Rain Bird 8005 commercial rotor (black, green rubber cap) — https://shop.horizononline.com/Product/rotor-pop-up-sprinkler-pool-rbd-58-1761
- H1 Continental commercial red rubber hot-water hose, brass couplings — https://www.homedepot.com/p/Continental-Premium-5-8-in-Dia-x-100-ft-Commercial-Grade-Rubber-Red-Hot-Water-Hose-21174685/328778760
- H2 Hose reel with nozzle (Commons, CC BY-SA 4.0) — https://commons.wikimedia.org/wiki/File:Hose_reel_with_hanging_water_nozzle.jpg
- B1 Home Depot 5-gal orange Homer bucket — https://homedepot.com/p/The-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2/100087613
- Tanks, reels, pumps: refs 1–18 and F1–F12 in `flowworks_modern_art_brief.md`.

Local reference copies (Commons only, licences in `LICENCES.txt`): `Transient/modern_style_20261023/refs/`.

## Inventory (98 Modern textures, 2026-10-23)

Full table: `Transient/modern_style_20261023/inventory.md`; composites `Transient/modern_style_20261023/inventory/`.
Summary: **42 read NOT as a real product** (pipe atlas, joins, span, faucet, sprinkler, pump, weir, drawbridge,
most suspension parts, barrel), **25 partly**, **27 yes** (the four owner-picked tanks, the fire reel set, GSS
aerial/switch/lamp/clamp, bucket, nozzle), 4 look-neutral water overlays. 23 are ledger-PROTECTED (owner keeps),
including the pipe atlas, pump, sprinkler, joins Coupler/Flange/Saddle and the containers — the owner ruled
2026-10-23 06:42 that the pipeline may redraw kept art it judges really bad, shown on the next shadow sheet.

## Redraw pass 2026-10-23 — what was made and where it stands

GPT critique round (`gpt_consult.py`, composites + this guide): `Transient/modern_style_20261023/gpt_critique.md`;
its corrections are folded in above (one product per asset, PVC first, pump + manifest, stoplog weir, impact
sprinkler, hose colour independent of the reel, safety colours only as real markings).

Candidates (round 3, not installed): pipe atlas + menu icon, Coupler, Flange, Saddle, UnderCollar, UnderPipe, PipeSpan,
faucet, sprinkler, pump (owner-kept, redrawn under the 06:42 ruling), hose Coupling_Bare and Mouth — in
`Transient/modern_style_20261023/cand_r3/`; before/after mock `composites/before_after_{32,128}.png` and
`composites/before_after_hose_end_128.png`. Scripts: `src/RimMandrake/FlowWorks/art_source/ModernStyle/`.

Art-eval pipeline (runs `modern_style_20261023`, `_r2`, `_r3`; three rounds): **none ACCEPTED**. By round 3 Opus called
the pipe, pump, faucet and sprinkler *good* (the pump with no blocking finding), but every GPT second look answered
*unsure* because the assembled panel is an offline mock: the machine template requires an in-game capture, and
without one a machine cannot reach ACCEPT. Next step is one batched in-game capture of the candidates (no bridge was
used in this pass). Review sheet: `Transient/biome_ffar/modern_style_redraw_sheet_2026-10-23.html` (+ prereview).

Not redrawn (proposals above): containers (barrel stripes), weir, drawbridge, suspension bridge, hose binding.
