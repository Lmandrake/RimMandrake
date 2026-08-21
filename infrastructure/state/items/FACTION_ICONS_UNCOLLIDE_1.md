## spec
Full reasoning, mechanism and the LOOK step: `design/Jawa/art/FACTION_ART_SPEC.md` §1–§4.
This item is the four edits.

Edit `src/Jawa/Jawa_Patches/Defs/FactionDefs/` in place — these are **our own defs**, so
change the `<factionIconPath>` element, do not write a patch.

| file | line | from | ⇒ to |
|---|---|---|---|
| `JawaTribes.xml` | 59 | `OuterRim/WorldObjects/MoistureFarmers` | `World/WorldObjects/Expanding/Salvagers` |
| `JawaHuttCartel.xml` | 61 | `World/WorldObjects/Expanding/Town` | `World/WorldObjects/Expanding/TradersGuild` |
| `JawaDeepwaterCompact.xml` | 63 | `World/WorldObjects/Expanding/Village` | `World/WorldObjects/Expanding/TownRough` |
| `JawaAscendantHelix.xml` | 64 | `World/WorldObjects/Expanding/Empire` | `World/WorldObjects/Expanding/HoraxCult` |

**Why each one is not optional:**
- `MoistureFarmers` is **dead in 1.6**. Its only copy is under Outer Rim - Core's
  `Common_Old`, which that mod's `LoadFolders.xml` loads under `<v1.4>`/`<v1.5>` only.
  `FactionDef.cs:375` falls back to `BaseContent.BadTex` ⇒ a magenta square for the Jawa
  Trade Moot's seven settlements.
- The other three each share a glyph with a faction that **holds settlements on this map**
  — Empire, `OutlanderCivil`, `TribeCivil` — and two of those three inherit theirs from
  `OutlanderFactionBase` / `TribeBase`, which is why it was invisible. `Settlement.cs:40`
  makes `factionIconPath` the zoomed-out world marker, so this is map legibility, not a
  faction-screen cosmetic.

⛔ **Do not touch the four reskins** (`Empire`, `OutlanderCivil`, `TribeCivil`, `Pirate`) —
they keep the vessel's art. When an authored faction collides with a vessel, the authored
faction moves.
⛔ **Do not add `settlementTexturePath`** to any of our defs; all eight already inherit it.
⛔ **Do not change any `colorSpectrum`.**

## verify
- `grep -rn factionIconPath src/Jawa/Jawa_Patches/Defs/FactionDefs/` shows the four new
  values and no duplicates among them
- resolve `OutlanderCivil`, `TribeCivil` and `Pirate` through their abstracts
  (`Expanding/Town`, `Expanding/Village`, `Expanding/PirateOutpost`) and confirm none of the
  eight authored paths equals one of those, nor `Expanding/Empire`
- for each of the four new paths, confirm the texture is reachable in the **1.6** load path
  — all four are vanilla, so they are in `resources.assets`
- ⚠️ **`MoistureFarmers` was searched to depth 6 across the workshop and found only in
  `Common_Old`.** If a deeper search finds another active mod shipping that exact path, say
  so before making the Trade Moot change — the collision fixes stand regardless.

## criteria
No faction marker on the world map is magenta, and no two factions that hold settlements
draw the same glyph.
