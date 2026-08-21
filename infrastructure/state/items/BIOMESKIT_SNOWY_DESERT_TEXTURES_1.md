## spec
`Player.log` from the 2026-08-21 session carries missing-texture errors of exactly four
shapes, and nothing else of the kind:

    Could not load Texture2D at 'WorldMaterials/BiomesKit/ExtremeDesert/Hills/Mountains_VerySnowy'      ×13
    Could not load Texture2D at 'WorldMaterials/BiomesKit/ExtremeDesert/Hills/Mountains_FullySnowy'     ×13
    Could not load Texture2D at 'WorldMaterials/BiomesKit/ExtremeDesert/Hills/Impassable_VerySnowy'     ×11
    Could not load Texture2D at 'WorldMaterials/BiomesKit/ExtremeDesert/Hills/Impassable_FullySnowy'    ×7

A texture RimWorld cannot load renders **magenta**, which is what the owner saw on the
globe: *"some extreme desert has magenta artwork."*

### What is established, by reading disk rather than guessing

✅ **The owner of those paths is `ReGrowth.BOTR.Core` (ReGrowth 2)**, workshop `2260097569`,
at `Textures/WorldMaterials/BiomesKit/`.

🔴 **NO biome in that mod ships a `_VerySnowy` or `_FullySnowy` variant.** `ExtremeDesert/Hills`
ships exactly six files — `Impassable`, `Impassable_SemiSnowy`, `LargeHills`, `Mountains`,
`Mountains_SemiSnowy`, `SmallHills` — and `AridShrubland/Hills`, a biome with no complaints
against it, ships **exactly the same six**. So this is not a gap peculiar to ExtremeDesert
and it is **not caused by our map**: any biome would fail identically once BiomesKit asked
for a snowier variant than `_SemiSnowy`.

🔴 **And snow is impossible on the tiles complaining.** Our 3,581 `ExtremeDesert` tiles run
**19.1 °C to 64.3 °C, with ZERO below freezing** — including all 345 at Mountains or
Impassable hilliness (22.9 °C to 63.8 °C). Whatever makes BiomesKit ask for a fully-snowy
desert, it is not our temperature column.

⚠️ **UNRESOLVED, and do not guess it:** why the request is made at all. Candidates, none
tested — BiomesKit computing snow from something other than tile temperature; a variant
probe that tries every level and tolerates misses; or a symptom of the render state that
session, which had also lost its button icons and labels.

⚠️ **"Yesterday had zero" is weaker evidence than it looks.** The 2026-08-20 session never
finished loading a world, so it never drew a planet — these errors are written when the
world map renders, so zero may mean *nothing was drawn*, not *nothing was wrong*.

## verify
The next clean load settles it. Load `WORLDMAP_gen`, let the planet draw, then:

    grep -c "WorldMaterials/BiomesKit" <Player.log>

- **0** ⇒ the errors belonged to the broken session, and there is nothing to fix.
- **~44 again** ⇒ they are normal for this mod stack drawing this biome-and-hilliness mix,
  and the fix is a mod-side one: supply the two missing variants, or stop BiomesKit asking.

## criteria
- the count is read off a load that actually drew the planet, and recorded either way
- if non-zero: name whether any biome other than `ExtremeDesert` appears, because that
  decides "our map's fault" versus "the framework's"
- ⛔ do not ship a hand-made `_FullySnowy` desert texture to silence it before that is known

## notes
Filed for CHECK 2026-08-21. ⚠️ The magenta is real and the owner saw it; what is NOT
established is that our map caused it, and the disk evidence points away from us. Added as
decision string 10 in `RELOAD_CHECK.md`.
