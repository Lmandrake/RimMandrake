# Graffiti: where the last pass got to

Pass 17 (2026-11-08, ~04:50-05:15 PST, game B). Retired on context, and because game B stopped starting (below). Committed and pushed. RATCHET.md is current. `ralph/NEED_GAME` is set.

## Game and machine
- Game B crashed in Unity startup twice in a row after the last deploy, at Player.log line 22, right after `Initializing input` and before any mod loads, so it isn't the build. bad_cpus=[2] all pass (same as passes 15-16). Before that: 5 deploy+up cycles, all fine, ~23 s each. No ssh drops.
- Built and deployed but **not seen live**: `47c6566629` (two-cell face rule). The first thing next pass: `deploy`, `up`, `g.py load graffiti_p16_ash_lit @ so Ledger trace`, then check that the trace says `off an edge-on wall or a stub` for the storeroom's stub X (126-ish,133) and the flyer at (128,130), and shoot `storeroom 126,123,18,14`.
- Save: still `graffiti_p16_ash_lit` (migration runs on every load; not saved, so nothing to redo).

## Done this pass (GPT's pass-16 leads 1-4, all tried)
- **No marks on walls seen edge-on, at all** (Kernel.PaintsEdgeOn, finders use OnFace, designator refuses with a message). Old ones move to a free face or come down quietly on load: Ashgate lost 4, moved 7. The `edgeOn` def field is gone.
- **A mark needs at least two cells of face** (GraffitiJobUtility.FaceRun/OnFace): a fitted flyer had gone onto the one-cell stub beside a door. Unseen live (above).
- **Weathering takes clean pieces out and leaves no stain** (WallPlane.Weathered: EatenClean 9-33%, mostly rain's vertical runs and grit chips, hard edges, bleach 0.045/step). Side by side with pass 16's look (`st Look p16|p17`, a proof switch), the W3 throw-up and W4 fist are now red paint with chips, where they had been pale stains.
- **A clumsy hand is a full coat that runs** (Kernel.CraftLook through 0 for awful/poor; WallPlane.Dripped: full-strength drips with beads and stalled blobs; first go at 0.9 not 0.28). The judge: worst-made "looks like a ruined attempt", worse than the tallies. That re-check is recorded in RATCHET.
- **Signatures** (Kernel.Signed, Filth_Mark.PrintSignature): stencils, sigils, portraits, meme glyphs and marks about someone carry their writer's tag in a contrasting pigment at the lower right. **The judge didn't mention them**: at play zoom they don't register. Either make them bigger and beside the shape (not under it), or drop them.
- Ideo icons drift as if copied by hand (PaintedIcon). Fist pool weight 1 -> 0.6. The olive tag pigment is dusty pink now. Art: HighLife magenta, NaturePrimacy orange, TreeConnection blue; the warning blot, the wolf and the mockery's pointing hands deep blue (bake.py `hue`, `dark_to`); StencilBox frame regenerated as a ring of believers' strokes (no crosses).
- Unstaged day on the new build (`/tmp`, gone; numbers here): 4 natural paints (flyer, cross-out, Mo's tribute to Fringe, Lark's mockery of Karen), reads and opinions as before, 74 marks and none edge-on.

## Blind judge pass 17 (`p17/blind_judge_p17.md`, read only the 9 `shots/p17_*`)
Dirt **yes**, but with a new list (RATCHET item 1). Worse than a tally: **yes**. Register: **mixed** (RATCHET item 2). What I read in it:
- **Scratches can't win this bar as gouges.** The art is "no paint at all", and a gouge reads as damage. Either drop Scratches from the pool (poolWeight 0, keep the def for saves) or regenerate them as something only a person scratches (a scratched eye or name-scrawl).
- **Pale-on-pale is ash.** memorial_2 (chalk white and ash grey wings) and half-weathered white paint read as ash, mould or chalk dust. Memorials need one clear colour; chalk-white marks might skip the bleach and lose bigger chips.
- **Badges are the ideo icon and symmetric emblems** (halo sigil, winged skull, tribute crown with sparkles, cogs, fists). Regenerating the halo frame like the StencilBox one, and a repeat penalty for the same sigil on one wall, are the cheap next steps.

## Do next
1. Bring game B up and verify the stub rule (above).
2. Scratches: decide (drop from pool or regenerate), memorial_2 recolour, pale-paint weathering. Re-shoot the 9 judge frames (rects below) and run a fresh blind judge with `p15/judge_brief_template.md` (brief filled in `/tmp` this pass; rebuild it from the template).
3. Register: halo frame regen; signatures bigger and beside the shape, or cut; fewer fists (old ones are in the save).
4. Owed fix checks: confront over painted-out work; wrong-faction visitor.
5. Before DONE.md: a `broaden` call (the last one was pass 14).

## Traps (kept)
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with Write/Edit. `g.py` is the driver; `ralph/steve.sh sync` after editing it. `so Ledger trace` prints the trace once and clears it.
- A g.py chain stops at the first failing shot (one failed silently this pass; rerun the rest). A 128 px shot holds 8 cells across, not 9.
- The Dirt stage's wall is at z=45: close-ups `10,43,8,4` and `32,43,8,4` at 128. Rects: south wall `101,107,20,10` / `121,107,20,10`, corridor `109,116,20,9` / `126,116,20,9`, storeroom `126,123,18,14`, west edge `92,126,20,12` (no marks there now: they were all edge-on), dirt `10,41,17,7` / `26,41,17,7`.
- Generating art: `skills/generating-images/scripts/codex_image.py generate --out ... --timeout 800 --prompt ...`, ~1 min each; put the prompt in manifest.py too (it must equal BASE + text).
- Local hour in Ashgate: ((ticks - 2983) % 60000)/2500. Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/`.
