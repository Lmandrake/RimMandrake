# The Utinni's world-map flight icon: art judge verdict (2026-11-27)

Item: `UTINNI_WORLDMAP_FLIGHT_ICON_1`, part `icon_style_judged`.
Judge: rm-detached-bench-utinni-worldmap-flight-icon-1-1795789966 (claude-opus-5-5). This judge did not make the work.
Brief: `design/RimMandrake/art_judge_brief.md`@9ad7d729e5, and `design/RimMandrake/standing_rulings.md` §The judge
refuses flaws, not polish and §A refusal carries its path to pass. Look 1 of at most 2.

The ask: from the in-flight globe captures (zoomed in and out), does the icon read as our ring-hull ship under the
faction tint?

## Verdict: NAMED FLAW: our sprite does not draw in flight

The only in-flight captures that exist show vanilla's glyph, not our ring-hull sprite. The art itself is not refused.
The delivery to the screen is the flaw.

## Evidence

- `capture_2026-09-24_zoomout.png` (here; also `Transient/utinni_flight_2026-09-24/utinni_flight_far_zoomout_2026-09-24.png`
  at 6168adf820): the globe zoomed out with a live `Gravship` world object in flight (FOUNDRY's note of
  2026-09-24T00:57Z: `jawa/world_objects_get def=Gravship` gave a count of 1). Next to the colony, the ship is a cyan
  saucer with a dome and two windows. That is the vanilla `World/WorldObjects/Expanding/Gravship` glyph under the
  player-faction tint. There is no ring and no hub.
- `capture_2026-09-24_icon_crop_6x.png` (here): the same icon at a 6x crop. A flat hull, a raised dome and windows.
  It is the "little pale blue dome-shaped thing" that the owner described on 2026-09-12.
- `Transient/utinni_flight_2026-09-24/utinni_flight_far_zoomin_2026-09-24.png` (at 6168adf820, not copied here): the
  globe zoomed in. No ship icon is visible in the frame. The capture was centred on the origin tile, not on the ship's
  draw position, so the zoomed-in regime (the `texture` field) has no evidence at all.
- These captures still stand for the current build. I measured on 2026-11-27 that the repo and the ArchBig deployed
  copy are byte-identical: `Patches/UtinniWorldIcon.xml` md5 8507f5f9…, and both PNGs md5 324445cd… The patch and the
  art have no commit since eaccb6bc00 (2026-09-12). `PatchOperationSettingGate.cs` had one 3-line commit (cbfe271eb0,
  2026-09-26) for another setting. So no change touches what these captures show
  (CLAUDE.md §After a change, only the checks that the change touches run again).
- I did not take new captures. ArchBig was free, but no scene stages a gravship flight on the UtinniPatches small list
  yet. The 2026-09-24 flight used the canonical campaign save on the full list, which is retired. The live part
  `our_icon_draws_on_the_globe_in_flight_live` (work bundle WB-game-ship-20261126-164518, step 3) builds that scene.
  A new capture before the cause is found would show the same glyph again [guess ~80%].

## Offline aside (advisory, decides nothing)

`offline_sprite_under_cyan_multiply.png`: `RUT_Utinni.png` (64x64) on the left, and the same sprite multiplied by an
approximate cyan faction colour on the right, at 2x on desert ground. The ring and the hub still read under the
multiply, because the art is value-led. This does not stand in for the in-flight capture (the part's `fooled_by` line
forbids that). It only says that once the sprite draws, the art is likely to read as our ship.

## Refusal record

- clause: A3: "The globe in flight shows the icon, and it reads as our ring-hull ship."
- observed: in flight, the zoomed-out globe draws vanilla's dome glyph. The zoomed-in capture shows no ship.
- would_pass: in-flight captures, zoomed out and zoomed in, each centred on the Gravship's draw position. In each one,
  a ring-hull silhouette with a hub (`RUT_Utinni.png` / `RUT_UtinniCaravan.png` under the faction tint) is on the ship.
- smallest_fix: first find out why the patched texPaths do not draw. The live part must read the live Gravship's
  `def.expandingIconTexture`, `def.texture`, `ExpandingIcon` and `Material` texture names mid-flight. These candidates
  are untested: the setting `utinniWorldIconEnabled` read back as false at patch time; the `ExpandingIcon` texture
  cached before the patch; another mod that patches or overrides the Gravship def after ours. Fix that cause, then
  capture both zooms on the ship. Attainable: yes. Cost: new instrument (the bridge reach that the bundle plans), then
  a rerun.
- criterion_verdict: sound. The clause asks what the owner asked on 2026-09-12, and a working patch can pass it.

## Polish (blocks nothing, files nothing)

- polish: when it draws, look again at whether the ring's dark keyline (B1a, no outlines) reads heavy at globe size.
  A world-map icon is not a sprite on the map. Note it only.
