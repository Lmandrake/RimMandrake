# Graffiti: where the last pass got to

Pass 16 (2026-11-08, ~04:00-04:40 PST, game B). Retired on context. Committed and pushed. RATCHET.md is current.

## Game and machine
- Game B again (`ralph/GAME` = b, Conductor switch 04:01). Saves now in game B's Saves: `graffiti_p15_ash_lit`, `graffiti_p15_brick_dead` (copied from game A's folder) and the new **`graffiti_p16_ash_lit`**: Ashgate day 18 noon, after the load migration below and with the Dirt stage built at (10,40). Load that one next.
- **Deploy trap:** game A (FlowWorks in a pass) was still running OUR pass-15 tier, so it held `Mods/Graffiti/Assemblies/RimMandrakeGraffiti.dll` open and deploy failed ("locked by the running game", Errno 22). I did not touch game A: I moved our own old DLL out of the folder (`D:\ClaudeWork\rimmandrake\instances\b\displaced_dll\RimMandrakeGraffiti_p15_0414.dll`; Windows allows renaming a loaded DLL, and the running game keeps its copy), then deploy worked. If deploy says STILL DIFFERS on the DLL again, check whether game A's ModsConfig still lists `mandrake.rm.graffiti` and do the same.
- Weather: 1 failed `up` ("BLIND: cannot read the command line of game pid"), the retry worked. 0 crashes. One vanilla "Illegal characters in path" texture error at startup (bad_cpus=[2], same as pass 15). No ssh drops. 5 deploy+up cycles, ~25 s each.

## Done this pass (the judge's pass-15 list, items 1-6)
- **Weathering chalks, not greys** (WallPlane.Weathered, Filth_Mark): what's left goes paler in its own hue (`BleachPerStep` 0.07/step, the bare stain chalked by 0.5), eats less per step (55% at W4, was 68%), the stain kept stronger (0.30-0.45), alpha barely thinned, wall show-through +0.1 per fade (was 0.2). Offline sim first (`/tmp` script, not kept): old rows went grey-brown, new rows pale paint.
- **No mud** for awful/poor hands (Kernel.CraftLook). Ugly shows in wobble, the slipped second go and thin coat.
- **Stencil heads** (WallPlane.PaintedPortrait(pawn, pigment)): three values split at the head's own middle, black, the mark's pigment (ochre if the pigment is dark), and a pale; overspray in the colour; weathered with the frame; wall comes back through it.
- **Soot needs a pale wall** (Kernel.PigmentReads, wall luma >= 0.58 for a pigment under 0.3). Old marks re-pick on load (`Filth_Mark.RepickUnreadPigment`): the corridor soot tally went orange.
- **Old edge-on pictures** (MapComponent_GraffitiSocial.MoveOffEdges, first tick after load): moved to the nearest free face within 8.9 cells, own room first, then any; with none, taken down quietly. Ashgate: 10 moved, 4 taken down, trace in `p16/01_load_migration_trace.txt`.
- **Art** (manifest.py, bake.py: new `mute`, `drop_grey`, `fill` options): fist without its disc and the cog with a hammer, both one-colour pigmented stencils; halo frame one sprayed loop; rude_3 thumbs his nose (its generator haze floored out, it was a faint blob); throw-up A dusty magenta; all six Vandals in clashing dusty pink, teal, mustard and violet (no green, olive, brown or grey). My regeneration script lived in /tmp and is gone; the manifest's own `gen` still points at the dead codexhome_w0/w1, so call `skills/generating-images/scripts/codex_image.py generate` directly, one at a time (each ~1.5 min; a background job dies at 10 min unless you give it a timeout).

## Blind judge, pass 16
`p16/blind_judge_p16.md` (it read only the 9 `shots/p16_*`). Dirt: **yes**. Worse than a tally: **yes**. Register: **mixed**. Gone since pass 15: rock chunks, UI portraits, the olive Vandal, the scorched-hole memorial, the invisible soot tally. The full list is in RATCHET. The pattern I read in it:
- **Faint = stain.** Every weak mark it flagged is faint, thin or low-contrast: a W3 throw-up, the pale weathered gear and scribble, a poor Vandal in the dim storeroom, a faint smudge. "The weak ones read as stains, not as clumsy paint." Chalking helped (no more grey or ash), but a faint mark of any colour still reads as a stain. Ugly needs to be bold and opaque but clumsy, and old marks should go before they're faint (die at W3, or flake crisply with no low-alpha stain at all).
- **Dark edges = burn.** The black overspray dusting and black blots (warning glyph, mockery's pointing hands, the wolf glyph's black) read as soot. The portrait's overspray is now coloured; the frames' soot parts aren't.
- **The art's own green is moss.** HighLife (oxide green and soot) at awful read as mould: recolour it (like the Vandals: no green, olive or brown).
- **Sideways tags** on edge-on walls read as "rust or blood runs" and "moss". Tags are still allowed edge-on (Kernel.ReadsEdgeOn). Consider: no new marks edge-on at all, and take old ones down like the pictures.
- **Clean single silhouettes = icons** (the fist now reads as an emoji fist; five fists in view). A stencil needs stencil character: misregistration, a second colour layer offset, bridges cut through, a tag or scrawl beside it, and fewer repeats.

## GPT `stuck` call, pass 16 (not yet acted on)
Asked: `ralph/live/stuck_ask_pass16.md` with the judge's verdict and four p16 shots. Answer: `/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/gpt_help_pass016.md`. Its leads, each with a cheap test:
1. **The wall drawn back over the paint may be what kills weak marks' edges.** Test: the same weak mark twice on identical walls, with and without the wall overdraw (WallPlane.Print `through`); if the bare one reads as paint, cut the overdraw over surviving paint cores and let mortar interrupt only some areas.
2. **Show a bad hand in its geometry, not in degraded material.** A faint whole-shape stain keeps the area and loses the stroke; the translucent second go reads as rubbed material. Control: a crooked tally through the same awful + W3 settings beside a failing mark. Change: uneven spacing, overshoots, lopsided loops at full opacity; weather by removing pieces of strokes with clean gaps, no pale footprint.
3. Narrow faces and wall ends change what a mark reads as (the orange tally on the door stub, the X on a wall-end cap): restrict marks to faces that keep their strokes.
4. **Stencils read as icons by composition, not cleanliness.** Test: the fist alone vs the same fist inside a crooked painted slogan/tag with overlapping strokes. Change: stencil pieces (symbol plus scrawl, an interruption), fewer identical repeats near each other.
Its acceptance check: recognition at native play size before inspection.

## Do next
Try GPT leads 1 and 2 first (each is one staged A/B on the Dirt wall), then:
1. Faint = stain: in WallPlane.Weathered drop the low-alpha stain (or make it crisp flakes only), and let a mark go at W3; for awful/poor drop `CraftLook.through` and the 0.28 second go, and show the bad hand by bolder wrongness (overloaded drips, a blob where the can stalled, crooked doubled strokes at full opacity). Re-shoot the Dirt stage (`st Dirt BlocksGranite`, rects below).
2. Recolour HighLife and AnimalPersonhood (and any glyph whose art is green/olive or mostly black) via manifest `fill`/`mute` or a regenerate.
3. Dark overspray: find the soot parts in the frames (warning glyph blot, mockery hands) and the dark overspray in PaintedPortrait (now coloured) and PaintedIcon.
4. Register: stencil character for the fist/cog (two-layer misregistered stencil, cut bridges), fewer fists (pool weight or a repeat penalty near the same def), the ideo sigil frames.
5. Then a fresh blind judge with `p15/judge_brief_template.md` on the same frames.

## Traps (kept)
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with Write/Edit. `g.py` is the driver; `ralph/steve.sh sync` after editing it. `so Ledger trace` prints the trace once and clears it: capture it to a file, don't `tail` it.
- Rects: z grows north. South wall west `101,107,20,10`, east `121,107,20,10`, corridor `109,116,20,9` / `126,116,20,9`, storeroom `126,123,18,14`, west edge `92,126,20,12`, dirt `10,41,17,7` / `26,41,17,7`; tributes at 128 `110,114,8,4`. At 128 px a shot holds 8 cells across.
- Local hour in Ashgate: ((ticks - 2983) % 60000)/2500. Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/`.
