## spec
`bd5dad0` dropped the Scald's 312 tiles from **+1411 m to −30 m** and closed with
*"⚠️ Judged by looking, not by the number. **Rendering next.**"*

⚠️ **`world/view/` holds nothing newer than 2026-08-18.** The render was not done.

A **1,441 m** change across 312 contiguous tiles is the largest single elevation edit this
map has taken. It also removed 32 cliffs along the shore. ⇒ **the relief view will look
different and nobody has seen it.**

```
# regenerate the elevation and biome views from the paint, then LOOK at them
world/view/ASHKARR_WORLDMAP.elevation.equirect.png
world/view/ASHKARR_WORLDMAP.biome.equirect.png
```

**What to look for, in order:**
1. 🔑 **The Scald reads as a lake in a caldera, not as a hole.** It sits inside a 2,050 m
   rim; the rim must still read as a rim.
2. **The 15 surviving cliffs are the rim** and the 32 that went were the shore. On the
   render the rim should still be drawn and the jungle/oasis shoreline should not.
3. **The Scald Spine and the rain shadow** — `ASHKARR_WORLD_DEFINITION.md` builds the
   drainage story on this massif. CHECK's warning was that the elevation field feeds it.
   ⭐ The paint is unchanged outside the 312, so this should be *visibly untouched*; if it
   is not, something re-derived more than it should have.
4. **The Dew Horn and Dune Sea deltas** (tiles `18267`, `19358`) are nowhere near the Scald
   and must look exactly as before.

⛔ **This is a LOOK, not a measurement.** The numbers already agree — water 8.14%, cliffs
104, all 312 at −30. `CLAUDE.md`'s rule is the point: *a number that says the world is fine
while the picture shows compass circles is the number being wrong.*
⚠️ **If the relief now reads wrong, do not re-raise the water question** — that is settled
and was settled for good reasons. Raise the relief.

## verify
both views regenerated with an mtime after `bd5dad0`, and a human has looked at them and
said so in this item.

## criteria
The Scald reads as a caldera lake on the render, and nothing outside its 312 tiles moved.
