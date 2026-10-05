# MessyConduit per-style art fill (Stage 4)

2026-10-04, FOUNDRY helper.

## 1. Census (table vs disk vs artpipe)

Disk (2026-10-04): the Scrapper set is complete except the table's "laid" reel, and that one exists too:
`Hose/Reel_Deployed.png` (256 px, round 3, bb887728e) IS the laid/empty-drum look; hose round 4 (another agent,
`Transient/mc_hose_round4_report.md` sec. 2 "pale strip on emptied reel") owns its rework, so it is not touched here.
artpipe `find` (Industrial/Modern/Futuristic, Hose_*, PowerSwitch, TapClamp, FrayedEndLive, PowerStrip) and a full
`_artsrc` listing of every MessyConduit job: every hit is the Scrapper/Jawa art already installed (hose v1/v2, clamp,
live end) or the aerial masts/brackets. **No per-style render exists for any slot below: all 40 are real gaps.**

| Slot (canvas) | Industrial | Modern | Futuristic |
|---|---|---|---|
| live frayed end (64) | gap | gap | gap |
| power strip dark (64x32) | - | gap | - |
| switch on / off (128) | gap x2 | gap x2 | gap x2 |
| tap clamp (128) | gap | gap | gap |
| reel stored / laid (256, 2x2) | gap x2 | gap x2 | gap x2 |
| hose strand flat / plump (256x64) | gap x2 | gap x2 | gap x2 |
| binding (82x40), coupling, nozzle, end cap (128), mouth (64) | gap x5 | gap x5 | gap x5 |


## 2. Generation

Route: Codex `$imagegen` EDITS (`skills/generating-images/scripts/codex_image.py edit`, 6 parallel workers, own codex
homes) of the shipped Scrapper piece, so pose/framing/canvas carry over and only materials change; one style sentence per
look, reused in every prompt (Industrial: gunmetal/charcoal steel, black ribbed rubber, hazard-stripe accents, black
rubber hose, steel camlock fittings; Modern: off-white powder coat + safety-orange accents, green vinyl garden hose,
chrome/orange quick-connects; Futuristic: silver-white alloy + graphite, cyan light strips, white segmented hose with a
cyan stripe, silver fittings with a cyan ring). Live frayed ends are edits of each family's own dead end. Raw renders
and conformed candidates: `D:\Luke\dev\_rmscratch\mc_style_art\{raw,conformed}\` (outside git; installed bytes are
archived in the art store). Conform: `conform_sprite.py` (mask registration onto the Scrapper slot), strips by band crop
+ wrap crossfade + seam test. Derived, not generated: switch Off (lamp darkened) and Modern dark power strip (LED off),
in the installer. Pilot (3 stored reels): ~80 s per edit, validator PASS with the same faint-alpha WARN (~0.5%) the
round-3 reel carried.

Results: 36 generated slots (12 per look) all conform with no REJECT (only the faint-alpha WARN, 0.2-2%, same as the
shipped round-3 reel). Fixes on the way: the laid reels are edits of the SAME look's stored reel (the first laid renders,
edited from the Scrapper laid art, drifted: Industrial got a brass inlet), so stored -> laid swaps nothing but the drum;
anchored pieces (binding, coupling, nozzle, end cap, clamp, live end) are fitted exactly onto the Scrapper piece's alpha
box (a restyle changes aspect by up to ~25%; the hose/bite anchor must not move); Modern's first live end came back as a
64 px non-render with boxy glow and was regenerated. Hose strands: band crop + wrap crossfade, seam test ok on all 6.


## 3. Install (art ledger)

`src/RimMandrake/Utils/mockups/messy_conduit/wire_style_pieces_art.py` installs every candidate through
`artledger.install_image` (reason `script:<that path>`), 40 PNGs, 80 ledger lines (variant + live) in
`infrastructure/state/art/events/BENCH.jsonl` (the ledger's default seat; no RIMFLOW_SEAT in this shell). All new paths,
nothing displaced. Re-run with `--only Look/Slot` after replacing a conformed candidate.

## 4. Naming scheme for code agents

Rule (the Aerial rule generalised): a piece shipped at `<folder>/<Name>.png` has its style version at
`<folder>/Styles/<Look>/<Name>.png`, Look = Industrial | Modern | Futuristic; Scrapper stays the root file. Cable decal
slots keep CordMaterials' family folders (Industrial = StarWars, Modern = ExtCord, Futuristic = Cybertek).
All under `Textures/RimMandrake/MessyConduit/`:

| Piece | Path (per Look) | Canvas |
|---|---|---|
| switch on / off | `Styles/<Look>/PowerSwitch.png`, `Styles/<Look>/PowerSwitch_Off.png` | 128 |
| tap clamp | `Aerial/Styles/<Look>/TapClamp.png` (bite line unchanged at -0.375 of width) | 128 |
| reel stored / laid | `Hose/Styles/<Look>/Reel_PumpHookup.png`, `Hose/Styles/<Look>/Reel_Deployed.png` | 256 |
| hose strands | `Hose/Styles/<Look>/Strand_Flat.png`, `Strand_Plump.png` (tile along u) | 256x64 |
| hose pieces | `Hose/Styles/<Look>/Binding.png` 82x40; `Coupling_Bare.png`, `Nozzle_Bare.png`, `EndCap_Bare.png` 128; `Mouth.png` 64 | as Scrapper |
| live frayed end | `Styles/{StarWars,ExtCord,Cybertek}/EndFrayed_Live.png` | 64 |
| dark power strip (Modern) | `Styles/ExtCord/PowerStrip_Off.png` | 64x32 |

Every file sits on the Scrapper file's canvas and anchor box, so the code can swap the path and keep every offset.
The design's two-layer reel (drum + coil overlay) is NOT drawn: each look ships the same stored/laid pair the code
already swaps (`Reel_PumpHookup` / `Reel_Deployed`); a coil overlay would be extra art.

## 5. Contact sheets

`D:\Luke\dev\RimMandrake\Transient\mc_style_art\Industrial.png`, `Modern.png`, `Futuristic.png`: each slot as Scrapper
(shipped) beside the new look, large plus a true-size inset; strands shown tiled twice so the seam shows.

## Owed / weak

- Modern live frayed end was regenerated once more (second render read pale with no glow); the installed third render has
  hot glowing tips. Still the smallest-reading live end of the three at true size.
- Scrapper laid reel: not touched (hose round 4 owns `Hose/Reel_Deployed.png`'s pale-strip rework).
- Coil overlay layer (design sec. 4 two-layer reel): not drawn, see sec. 4.
- Per-style overhead span wire: optional per the design, not drawn.
- Nothing is wired: the code reads none of these paths yet (code agents), and nothing is deployed or seen in game.
