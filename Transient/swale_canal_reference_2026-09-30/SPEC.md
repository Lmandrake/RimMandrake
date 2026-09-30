# RM_Swale art spec, from a live FlowWorks canal (SWALE_CANAL_ART_REFERENCE_1)

Shot 2026-09-30 on a regenerated RM_FloodedCanyon map: a 3-wide, 30-long channel cut with the
real excavation component (`RM_MapComponent_Excavation`, depth 2) and filled. `swale_full_frame.png`
is the whole screen at play zoom; `swale_canal_crop_2x.png` is the channel.

What a FlowWorks canal looks like in game:
- Top-down, flush with the ground. It is terrain, not a raised object: no walls standing up, no cast shadow.
- Water is a flat slate/steel blue with a faint diagonal ripple, much bluer than the surrounding
  ochre sand and red-brown cracked mud, and it fills the cell edge to edge.
- Edges are crisp and cell-stepped: the run jogs a cell sideways where the path bends. No rounded banks.
- The channel reads as a tile you can extend in a line. One tile's art must tile seamlessly left/right and up/down.

So the swale (the Cracked Lands' seep canal) should be that same flush, cell-filling channel tile,
with its own identity added on top, not a free-standing structure:
- The fitted stone/clay lip is a thin inset border at the cell edge, not a wall.
- A brown-clear, red-tinged water surface (the biome's water) instead of vanilla blue.
- Weep-holes along the lip, and a darker, moss-green seep line just outside the lip on both sides.
- Top-down, full-bleed, seamless on all four edges. No centred "object on transparent" composition.

The v1 render (`infrastructure/artpipe/done/RM_Swale.json`, a centred stone-channel object) stays as the
placeholder until the v2 job below passes review.
