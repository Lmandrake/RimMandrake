# Owner look defects, FlowWorks liquid look, 2026-11-13 evening (HELD, not yet ingested into any validation ladder)

These are his words, said live at the game on Fri 2026-11-13 between ~10:00 and ~10:25 PM PST and relayed by the Conductor. The save is EVENING_20261113_FLOWWORKS_LIQUID_LOOK. Items: RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE (rows 1-3) and RIMMANDRAKE_SINK_COOLER_ARROW_UNDER_TAR (rows 4-5).

None of these fixes has been seen live yet. Each one stays HELD until the UNRUN capture in its row has been run and looked at.

| # | his words (verbatim) | save / capture | fixed by | a check would assert (kind) | proof hook, and what tests it today |
|---|---|---|---|---|---|
| 1 | "Bubbles are centered on vent itself, yes. They are too large and too transparent. It should be bubbling water, not faint ghost bubbles rising up." | G2 64,98 (1 m) | the new fleck RM_Fleck_VentBubble (opaque 64 px art, 0.08-0.16 cells, 0.5 s life, 0.35-cell cluster) at 24/s spraying and 8/s between, x(1+0.25*min(m,4)), tinted in the liquid's own colour | count, size and alpha are in bounds; other liquids use their own colour; the switch off gives none (offline) | C# GeyserTub_plume_is_bubbling_water and GeyserTub_every_liquid_bubbles_in_its_own_colour; census bubble_art. LIVE UNRUN |
| 2 | "No, the vent does not appear to be under water. The blue seems to fade away, and the vent looks on top of the water. But you could see that for yourself." | G2 64,98 (1 m), G2h 36,149 (2 m), Gbrim 111,230 (4 m) | the geyser and other things lying flat on the floor draw under the sheet (UnderSheetQueue), so the sheet tints them like the floor: Seen 0.70 / 0.44 / 0.10 | the vent is below the sheet and tinted at 1, 2 and 4 m (offline) | C# Submerge_flat_vent_is_tinted_like_the_floor. LIVE UNRUN. "Not visible at 4 m" goes past the law's 0.10 plateau; this is flagged, not changed |
| 3 | "The ancient shopping Cart isn't shown as under the water. Not sure if the chunks are either. And the chunks don't honor the pit, they overlap its edges unphysically. But the pits altogether, the murk looks really good. If it gets even deeper it keeps getting more murky right?" | images/2.png (G2 carts and chunks), images/3.png (big pit) | drowned bands draw the thing whole, then a cover in the liquid colour at 1-q/32. Sprites larger than the pit are clipped to the dug cells when printed | every draw path is enumerated; a sprite stays inside the pit; murk rises to the plateau (offline) | census THING_CLASSES and OVERLAY_PATHS; C# Submerge_drowned_part_reads_as_under_the_liquid, Submerge_rim_clip_keeps_sprites_in_the_pit, Submerge_murk_keeps_rising_to_the_plateau. LIVE UNRUN |
| 4 | "I keep telling you that the Cooler still keeps its little red arrow icon above the surface... the tar shows it cleanly." | BP6 tar | the cooler and vent count as 1.0 m tall (wall slot), and overlays are seen as the middle of their thing is | overlays follow the depth rule (offline) | C# Submerge_overlays_follow_their_thing; census OVERLAY_PATHS. LIVE UNRUN |
| 5 | "And yes, if we could put the yellow power disconnect icons under the water too when the item is under water that would be great" | an unpowered building at 1 m and at 4 m | every OverlayDrawer.Render*(Thing) and DrawBatch.DrawMesh is patched: vanilla's FadedVersionOf sets an absolute alpha and was undoing our fade. GSS has no unplugged marker [measured] | NeedsPower and PowerOff fade with depth (offline) | census OVERLAY_PATHS pins. LIVE UNRUN |

KEEP (row 3, his words "the murk looks really good"): the look of the big pit series in images/3.png must not change. Water murk from model/underliquid.py (seen, then murk = 1 - seen):

- 0.5 m: 0.847 / 0.153
- 1 m: 0.702 / 0.298
- 2 m: 0.441 / 0.559
- 3 m: 0.229 / 0.771
- 4, 6, 10 and 20 m: 0.100 / 0.900

So the answer to "keeps getting more murky right?" is no: the murk stops rising at 4 m and holds at 90%.

UNRUN live command. Load save EVENING_20261113_FLOWWORKS_LIQUID_LOOK. Take a zoomed capture of G2 64,98, G2h 36,149, Gbrim 111,230 and BP6 tar, and of an unpowered building at 1 m and at 4 m, first paused and again after 300 ticks.
