# Messy Conduit — art round 5 (owner review of per-style map)

Status: DONE 2026-10-04 (art installed through the art ledger; nothing deployed or seen in game)

## 1. Owner's words (verbatim)
"Station 3: Power switch in modern style should look like something in the real world: a throw-switch to connect-disconnect power. Junction boxes should look like little square connector bricks you plug into (three prong). Power strips should be plugged into the top with three-prong plugs, like real life. Station 4 T and + power junctions look very poor quality: need to make the wires thinner, and ensure the junction box connectors are thicker to cover them. Make + and T connectors be relatively the same central size/center. Station 6: Make the lamps on the lamp masts like ordinary lights, not frozen bright sparkles. Make them the same as the wall lights normally used. Make the cybertek light look very futuristic, the modern lamp look like a streetlight, the industrial star wars one look angular and industrial, and the junker one look like a bare lightbulb in a crude reflector dish. Make the industrial black cables for the poles narrower: they are extremely thick right now. Station 11: The hose reel for modern should not itself be neon, but rather fire-hydrant-red painted metal and bare steel wheel. Make the power switches look appropriate for each of the chosen styles as well. Also redo the bare lamp on the floor the same way (art). station 23: clamp is too low res, looks bad and has strange metallic conduit sticking out its back. Fix."

Station map (KEYSHEET): 3 = ground cords Modern, 4 = ground cords Futuristic, 6 = overhead four looks, 11 = hose reels four looks, 23 = power tap (old 11). Screenshots read: 20261004204130 (tangle junctions + cross junction, standing lamps), 205753 (tap clamp: dark conduit stub out its back), 210108 (hose reel).

## 2. Slot inventory (what the code reads)

Root = `src\RimMandrake\MessyConduit\Textures\RimMandrake\MessyConduit\`. Looks: Scrapper | Industrial | Modern | Futuristic;
cable families (CordMaterials.Family): Jawa (root names) | StarWars | ExtCord | Cybertek.

| Owner ask | Slot(s) the code reads | Canvas |
|---|---|---|
| switch per look (Modern = real throw switch) | `PowerSwitch.png` (Scrapper), `Styles\<Look>\PowerSwitch.png` + `_Off` (ConduitStylePicker.cs:232) | 128 |
| junction bricks, T and + same centre (st.3, st.4) | `Junction_Tape.png`/`Junction_Tin.png` (Jawa), `Styles\<Family>\Junction_T.png`/`Junction_X.png`; ExtCord also `Styles\ExtCord\<Colour>\Junction_*` recolours | 128 |
| power strip plugged from the top (st.3) | `PowerStrip.png` (all families fall back to it; no per-family file existed), `Styles\ExtCord\PowerStrip_Off.png` | 64x32 |
| lamp-mast heads (st.6) | head is painted INTO `Aerial\Styles\<Look>\AerialLampMast.png` (256x512); `AerialLampMastTop.png` (256x128) is its exact top-128-row crop (measured: 100% equal pixels) | 256x512 / 256x128 |
| Modern hose reel red (st.11) | `Hose\Styles\Modern\Reel_PumpHookup.png`, `Reel_Deployed.png` | 256 |
| floor lamp per look | vanilla `StandingLamp` (texPath `Things/Building/Furniture/LampStanding`, 64x64 in resources.assets). The mod restyles NOTHING for it: no ThingStyleDef, not in ConduitStyles.SwitchDefs. Art goes to `Styles\<Look>\StandingLamp.png` (new paths, 128) | 128 |
| clamp (st.23) | `Aerial\TapClamp.png` (Scrapper; RM_MapComponent_Aerial.cs:128 reads ONLY this root path) + `Aerial\Styles\<Look>\TapClamp.png` | 128 |

Mast lamp glow: the round-5 code already removed the sparkle (Defs comment: CompProperties_Glower only, "the head is the look's art"), so the lamp ask is pure art.

## 3. Existing art check (artpipe)

`artpipe_state.py find StandingLamp LampStanding Junction_T Junction_X PowerStrip TapClamp LampMast PowerSwitch streetlight`:
0 hits for every slot except TapClamp (the original Jawa clamp job = the 64 px source of the current upscale) and LampMast
(the v1/v2 mast jobs = the art installed now). Nothing reusable: every slot below is generated fresh.

## 4. Generated / installed

Generator: `src\RimMandrake\Utils\mockups\messy_conduit\round5_art_jobs.py` (Codex $imagegen, 6 workers, own homes;
raw renders outside git at `D:\Luke\dev\_rmscratch\mc_r5\raw\`). Conform + install:
`src\RimMandrake\Utils\mockups\messy_conduit\round5_art_install.py` (artledger.install_image only; geometry rules in
its docstring). Wave 1 = 22 renders (switch On x4, junction + brick x4, power strip, mast heads x4, floor lamps x4,
clamps x4, Modern stored reel); wave 2 = switch Off x4 (edit of each new On: lever thrown open) + Modern laid reel.
T junctions are NOT rendered: each T is its look's + image shifted 19 px and cut above the brick, so T and + share one
brick size and centre exactly.

Installed (all through artledger.install_image, reason script:round5_art_install.py; validator PASS on every slot against
its shipped reference, the only finding the usual faint-alpha WARN 0.2-3%):
- switches x8: Scrapper copper knife switch on scrap plate; Industrial gunmetal disconnect box with angular throw lever and
  green lamp; Modern grey steel safety-disconnect box with a red throw handle (On = handle up, Off = handle down);
  Futuristic alloy breaker with a glowing slide lever. Off = an edit of the same On render with the lever thrown open.
- junctions x16: + and T per family + ExtCord Green/Brown/Yellow/Blue recolours (`Junction_Tin`/`Junction_Tape` for Scrapper).
- power strip: `PowerStrip.png` (white strip, black 3-prong plugs pushed in from the top, orange LED) + derived
  `Styles\ExtCord\PowerStrip_Off.png`. **Validator REJECT, shipped anyway, said here:** height 16 px vs the old 18 and
  aspect 3.69 vs 3.28 - the redesign (plugs on top, cord tails) is wider than the old bare strip at the same box; it is
  not squashed. Same 64x32 canvas, same draw (0.8 x 0.4 cell).
- lamp mast heads x4 (+ tops): Scrapper bare bulb in a dented reflector dish; Industrial angular gunmetal floodlight (retry:
  the first edit barely changed the old caged lantern); Modern cobra-head streetlight; Futuristic alloy blade with a cyan-white
  light strip (retry, same reason). Pole/crossarm/insulators byte-identical outside the head box.
- Modern reel stored + laid: fire-hydrant red painted housing, bare steel hand-wheel, green hose kept.
- tap clamps x4 at 256 (was a 64 render upscaled to 128): no cable stub behind the handles. Validated against the old clamp
  upscaled x2 with its stub columns cut (vs the raw old one it REJECTs on -18% width: that width IS the removed stub).
- floor lamps x4 at `Styles\<Look>\StandingLamp.png` (new paths, 128): Scrapper bulb in scrap dish on pipe stand;
  Industrial caged lantern on hazard-striped stand; Modern drum shade on black pole; Futuristic alloy column with a ring light.
  NOT DRAWN IN GAME until the code change in sec. 6 item 3.

## 5. Contact sheets (before = git HEAD at sheet time, after = installed candidate)

- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round5_switches.png`
- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round5_junctions.png`
- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round5_lamps.png` (mast heads + floor lamps)
- `D:\Luke\dev\RimMandrake\Transient\mc_style_art\round5_strip_reel_clamp.png`
(Rebuilt with `round5_art_install.py sheets`; in the lamps sheet Scrapper/Modern masts show identical before/after because
they were committed before the last rebuild.)

## 6. Code changes owed by other agents (no C#/Defs edited here)

1. **Overhead cable width (st.6 "industrial black cables ... extremely thick")** - `Source\Aerial\AerialMaterials.cs`
   `WidthOf(look)`: Industrial **0.17** cells, Scrapper 0.14, Modern/Futuristic 0.095 (span texture for Industrial, Modern
   and Futuristic is the same `Styles/StarWars/Strand_BlackRubber`). Suggest Industrial 0.17 -> ~0.09 (Modern's 0.095 or a
   hair under); the global `SpanWidth = 0.17f` default (line 38) follows the default look and needs no separate edit.
2. **Per-look tap clamp** - `Source\Aerial\RM_MapComponent_Aerial.cs:128` loads ONLY `Aerial/TapClamp` (one static
   `tapMat`), so the three `Aerial\Styles\<Look>\TapClamp.png` files are never drawn. Needs a per-look material keyed
   on the run's look of the conduit the tap hooks (fallback root). `TapSize 1.5`, `TapBiteX -0.40` unchanged by this art.
3. **Per-look floor lamp** - vanilla `StandingLamp` is not styled at all. Needs (a) four ThingStyleDefs
   `StandingLamp_<Look>` with graphicData texPath `RimMandrake/MessyConduit/Styles/<Look>/StandingLamp`, Graphic_Single,
   drawSize (1,1) (vanilla's), in `Defs\Aerial\RM_ConduitStyles.xml`; (b) `StandingLamp` added beside `PowerSwitch` in
   `ConduitStyles.SwitchDefs`-style membership so a lamp wired into a run takes the run's look (or a separate list if a lamp
   should not join runs); (c) the picker/selftest counts (`StyleStage2Checks` asserts KeysFor(PowerSwitch)==4).


## 7. Owed / not done

- Floor lamp and per-look clamp art are NOT drawn until the code changes in sec. 6 (items 2, 3). The root `Aerial\TapClamp.png`
  (Scrapper) IS what the code draws today, so station 23's clamp changes on the next deploy.
- Overhead Industrial cable width is code (sec. 6 item 1).
- ExtCord colour recolours: `recolor_extcord_pieces.py --check` reports 0 stale of 24 against the new orange sources.
- Junction T has no separate render: derived from the + (sec. 4). Old root `Aerial\AerialLampMast.png` (unstyled legacy
  def texture, 3 green dots) untouched: every look draws `Aerial\Styles\<Look>\` art.
- Nothing deployed; no live check (offline only, as briefed).
