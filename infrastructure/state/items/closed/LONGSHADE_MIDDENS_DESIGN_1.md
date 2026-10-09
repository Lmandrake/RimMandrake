# LONGSHADE_MIDDENS_DESIGN_1 — lee-side middens: what they are, before anything is built

Split from `LONGSHADE_GPT_ENRICHMENT_1` §4 (owner-picked by card 2026-09-30). The pick names the
idea; the GPT consult (`Transient/bedazzle_gpt_enrich_2026-09-30/longshade.md` §10, ~14-day shelf
life) supplies everything else, and none of that is ruled. Nothing was built, because every part
below would be invented content.

The picked spec: *"A GenStep puts surface middens at the down-sun end of old rocks; a map component
adds layers from patch occupants. Searchable for minor salvage, samples, study progress; an
unnaturally clean patch warns of a mirrak or rooted sarlacc."*

What exists to build on: the directional shade grid gives the down-sun end of every caster
(`RM_MapComponent_ShadeGrid`, pinned sun on the Long Shade); the patch graph gives patches and their
occupants (`RM_ShadePatchGraph`); Odyssey's `Building_Crate` is a vanilla open-it-for-contents
building; the gloomcast already drops persistent dung (`RM_Filth_Gloomcast`, 45–50 days).
`longshade_bedazzle_review_2026-09-29.md` proposes the **vrekka** as the midden-worker. It was never
ruled (see `LONGSHADE_BEDAZZLE_CONTENT_1` part 8).

## open questions (the owner's)

1. **What a midden is in game.** It could be a searchable building (open it once, like an ancient
   crate), a filth or terrain layer you dig or clean, or a heap that grows and is searched again.
2. **What searching yields.** Vanilla items only, or a new "biological sample" item? The consult's
   list is bones, cracked water vessels, dung, shed scales and wind-sorted scrap. Vanilla has no bone
   item.
3. **"Study progress"** depends on how shade gear is learned (`SHADECRAFT_LESSONS_DESIGN_1`). Should
   a midden feed it at all?
4. **The clean-patch warning.** How does the player see it: an inspect line on the patch, a message
   when a colonist passes, or something visible on the ground?
5. **The vrekka.** Is the midden-worker in or out? If it is in, its heaps are the middens' visible
   surface.
6. **Art.** No midden art exists in artpipe (`registry.jsonl` and `_artsrc` were searched on
   2026-10-01; the only hits are the Wasteland's middenshell).

## criteria

- The owner answers 1–5. Then a build item is filed with the answers as its spec.
