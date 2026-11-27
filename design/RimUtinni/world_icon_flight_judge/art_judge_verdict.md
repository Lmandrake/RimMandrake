# The Utinni's world-map flight icon: art judge verdict (2026-11-27, look 2)

Item: `UTINNI_WORLDMAP_FLIGHT_ICON_1`, part `icon_style_judged`.
Judge: claude-opus-5-5, a blind-judge subagent of the detached run for this item. This judge did not make the work and
did not make look 1.
Brief: `design/RimMandrake/art_judge_brief.md`@9ad7d729e5, and `design/RimMandrake/standing_rulings.md` §The judge
refuses flaws, not polish and §A refusal carries its path to pass. This is look 2 of at most 2. It checks the one named
flaw of look 1 ("our sprite does not draw in flight") and rules A2 and A3. There is no third look.

The ask: from the new in-flight globe captures and the live read-back, does the globe in flight show our icon, does
it read as our ring-hull ship under the faction tint, and is the icon's style acceptable?

## Verdict: KEEP

- A2 (the icon style is acceptable): KEEP.
- A3 (the globe in flight shows the icon, and it reads as our ring-hull ship): KEEP. The flaw of look 1 is fixed.

## Evidence

- `captures_2026-11-27/modcheck_UtinniPatches_20261127T164911Z.json`: the chain `world_icon_in_flight` ran on ArchBig
  on the UtinniPatches small list. All of its rows read PASS. The one live `Gravship` world object (id 106, faction
  PlayerColony, tile 118865, ticksGame 2299) reads `expandingIcon` = `RUT_Utinni`
  (`World/WorldObjects/Expanding/RUT_Utinni`) and `materialTexture` = `RUT_UtinniCaravan`
  (`World/WorldObjects/RUT_UtinniCaravan`). This is the live object's texture, not the def. So the cause that look 1
  could not name (the patch did not reach the drawn texture) is gone, in both zoom regimes.
- `captures_2026-11-27/close_crop_x4.png` (from `world_icon_in_flight_close_1795798142.png`, altitude 160, centred on
  the ship): the ship draws as OUR sprite. I see a toothed ring with the side bumps of the ship's hull, a dark-teal
  hull, a dark keel line and a bright cyan hub disc in the centre. There is no dome and there are no windows. The
  vanilla glyph that look 1 saw is not there. The player-faction cyan tint multiplies the sprite, and the ring and hub
  still read, because the art carries its reading in value. A dark rectangle covers the lower half of the ship. The
  full frame shows that it is the hover tooltip box at the screen centre, inside the tile hover square. It is not our
  sprite: both textures are 64x64 with real alpha. The upper half that is visible shows the ring, the hub and the
  bumps. That is enough to read the shape.
- Shape reference: `design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.png`. It shows a ring
  hull, an octagonal hub and a spoke to the west. The icon matches it: a ring, a central hub, the spoke stub and the
  bumpy outer edge. Side by side, in scratch: `D:\ClaudeWork\rimmandrake\judge_utinni_icon\art_vs_ref.png`.
- `captures_2026-11-27/world_icon_in_flight_mid_1795798146.png` (altitude 400), `mid_crop_x8.png` and
  `world_icon_in_flight_far_1795798148.png` (altitude 900): the ship is still on its origin tile at tick 2299. So the
  colony's cyan house icon draws over it, and no ship icon is visible at these zooms. These shots show neither our
  icon nor vanilla's. The zoomed-out regime therefore rests on the live `expandingIcon` = `RUT_Utinni` read-back.
  `RUT_Utinni.png` and `RUT_UtinniCaravan.png` are byte-identical (md5 324445cd…, measured on 2026-11-27). So the
  zoomed-out icon is the same picture that the close shot shows drawing.
- Art: `src/RimUtinni/UtinniPatches/Textures/World/WorldObjects/Expanding/RUT_Utinni.png` and
  `.../WorldObjects/RUT_UtinniCaravan.png`, 64x64 RGBA with real alpha. `placeholder_detect.py file` reads it as
  `real`, not as a script-drawn stand-in (E2). The shape is traced from the authored ship layout
  (`Source/make_utinni_worldicon.py`), not borrowed from vanilla (E1).

## How each criterion was decided

- A2, KEEP. The sentence that decided it: at globe size the icon reads as a few bold shapes (a dark ring and a bright
  hub, B2), and it is our own traced shape (E1, E2), not a donor or a stand-in. Its flat glyph style with a keyline
  is the style of vanilla's world-object icons (the colony house in the same capture). It is not a map sprite, so
  B1's painterly clause does not govern it.
- A3, KEEP. The sentence that decided it: in flight, the live Gravship's textures read as `RUT_Utinni` and
  `RUT_UtinniCaravan`, and the close capture shows that sprite drawn on the ship. It is a ring with a hub, a dark
  hull and no dome, and it reads under the cyan faction tint.
- Look 1's flaw, "our sprite does not draw in flight": FIXED. The vanilla dome glyph is gone, and our sprite draws.
  Look 1 suggested "captures, zoomed out and zoomed in, each centred on the Gravship's draw position" as one way to
  pass. By Rule 3 that suggestion binds only "close this hole". The live texture read-back closes the hole for the
  zoomed-out regime, and that read-back would have gone red on the fault that look 1 saw.

## Polish (advisory)

- polish: a zoomed-out capture taken when the ship has left its origin tile would show the expanding icon itself.
  The origin-tile house hides it in the mid and far shots. This is better evidence, not a missing promise.
- polish: in the close capture, move the cursor off the screen centre before the shot, so that the hover tooltip
  does not cover the lower half of the ship.
- polish: the ring's dark keel line is a keyline. B1a (no outlines) is written for sprites on the map. Vanilla's world
  icons carry outlines, so I note it only.

## History

- Look 1, 2026-11-27, refused A3 on the 2026-09-24 captures (`capture_2026-09-24_zoomout.png`,
  `capture_2026-09-24_icon_crop_6x.png`). The named flaw was "our sprite does not draw in flight": vanilla's dome
  glyph drew. Look 2 (this one), on the 2026-11-27 captures and the live read-back, finds that flaw fixed and keeps
  A2 and A3.
