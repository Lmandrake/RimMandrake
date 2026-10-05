# MessyConduit art round 6

Owner (station 11): "The hose reel for the scrapper needs to look hacked together out of piecemeal [scrap parts]. The modern hose should not be neon, it should look like a real firehose."

## 1. Inventory (in progress)

## 2. Scrapper reel

## 3. Modern hose

## 4. Install / commits

### Inventory findings
- Slots: Scrapper reel = root `Hose/Reel_PumpHookup.png` (stored) + `Hose/Reel_Deployed.png` (laid), 256x256.
  Modern hose = `Hose/Styles/Modern/{Strand_Flat,Strand_Plump}` 256x64, `Binding` 82x40, `Coupling_Bare`/`Nozzle_Bare`/`EndCap_Bare` 128, `Mouth` 64.
  Modern stored reel `Hose/Styles/Modern/Reel_PumpHookup.png` carries the green hose coiled on its drum: it must follow the new hose colour.
- Before: Scrapper reel was a tidy rusty cast reel (not junk-built); Modern hose is saturated green garden hose with orange/white plastic garden fittings.
- Artpipe `find` (firehose, fire_hose, hosereel, hose_reel, Reel_): only the two Scrapper PumpHookup v1/v2 jobs already installed. No reusable art; all generated fresh.
- Colour choice: real fire-hose off-white/cream woven jacket (muted), so it contrasts the hydrant-red Modern reel instead of vanishing into it.

## Method (in progress)
- Generated (Codex $imagegen, `src\RimMandrake\Utils\mockups\messy_conduit\round6_art_jobs.py`): Scrapper stored reel (junk-built edit of the old one), Scrapper laid reel (edit of the NEW stored reel: drum emptied, inlet at drum centre), Modern coupling / nozzle / end cap / binding (edits of the old Modern pieces, so pose and anchors hold).
- Procedural (`round6_art_install.py`): Modern Strand_Flat / Strand_Plump (old Modern shading with highlights compressed to matte, a 4 px diagonal twill weave, cream jacket, thin red tracer line; every pattern period divides 256 so the u-tiling stays seamless), Modern Mouth (green ring recoloured cream), Modern stored reel coil (green coil recoloured to the same cream; housing untouched).
- wave1 started 2026-10-04 (5 jobs).
- wave1: 5/5 OK (~55-61 s each). Procedural strands tuned twice: first pass lost the dark outline and read glossy; now outline kept, highlights capped, cream lifted to match the generated binding's jacket.
- wave2: laid Scrapper reel OK (53 s), edited from the new stored reel: same scrap parts, barrel drum emptied, hose inlet socket at the drum centre.

## Result (DONE 2026-10-04, installed through artledger.install_image; nothing deployed or seen in game)

| slot | what it is now |
|---|---|
| `Hose\Reel_PumpHookup.png` (Scrapper stored, 256) | junk-built: blue tin patch panel riveted on the pump body, mismatched end plates (rusty red rim / grey-green wheel rim), bent crank handle, wire and rope lashings, welded angle-iron frame; brown hose coiled |
| `Hose\Reel_Deployed.png` (Scrapper laid, 256) | same reel, empty rusty barrel drum with the hose inlet at the drum centre |
| `Hose\Styles\Modern\Strand_Flat.png`, `Strand_Plump.png` (256x64) | cream woven fire-hose jacket, matte, twill weave, thin red tracer line; seamless along u |
| `Hose\Styles\Modern\Binding.png` (82x40) | cream fire hose with a bare aluminium hinged hose-jacket repair clamp |
| `Hose\Styles\Modern\Coupling_Bare.png`, `Nozzle_Bare.png`, `EndCap_Bare.png` (128) | aluminium Storz coupling with brass ring; aluminium branch nozzle with brass coupling, black bale lever and rubber bumper; Storz blank cap on chain over a cream hose stub. Fitted into the old Modern alpha boxes, so anchors are unchanged |
| `Hose\Styles\Modern\Mouth.png` (64) | cream hose rim around the dark bore |
| `Hose\Styles\Modern\Reel_PumpHookup.png`, `Reel_Deployed.png` | hydrant-red housing and bare steel wheel untouched; green coil (and the laid reel's green inlet post) recoloured to the same cream, so reel and hose match |

Contact sheets (before | after):
- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round6_scrapper_reel.png`
- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round6_modern_hose.png`
- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round6_modern_context.png` (red reel + strands tiled 5x)

Not done / open: no Source or Defs touched (another agent owns the C#); not deployed; not seen in game.
