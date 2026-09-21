# Biome name drafts — 2026-09-21

Four biome names need a pick. The biome mod split is blocked until they land.
Each table: row 0 is the current working name (ships if you strike nothing) except
for Scarlands, which is already ruled out. Bold = recommendation.

**Label convention (MEASURED from the 32 BiomeDefs under `src/`):** 26 of 32 carry a leading
lowercase article and a capitalised proper noun — `the Greentide`, `the Pyrelands`,
`the Scarlands`, `the Forge`; 2 more carry the article over a lowercase generic
(`the arid shrubland`, `the gelatinous slime`); 4 carry no article (`Umbra`, `flooded canyon`,
`lantern deeps`, and `mineral water`, which is a background-water def, not a named biome).
Vanilla's own labels carry no article and are lowercase (`desert`, `extreme desert`,
`scarlands`). Every candidate below follows the majority house form, `the Xxx`. ⚠️ Flag:
your ruling today that REGIONS carry no article ("Dune Sea", not "The Dune Sea") sits beside
28 biome labels that do. Biomes and regions are different lists, so this is only a question
if you want them to read the same — say so and the article comes off every biome label in
one pass; nothing below depends on it.

**Two layers, one more than a creature has.** The RimMandrake mod ships the defName and a
generic label any RimWorld player can read. The CAMPAIGN label (e.g. "the Dune Sea") stays
a Utinni-tier patch over it (architecture §2a, "campaign label (stays in Utinni)"), so a
Tatooine name never has to be the RimMandrake name.

## 1. RM_DeepDesert  (today `RUT_ExtremeDesert`, "the Extreme Desert")

**What it is** (`deep_desert.md` + `dune_sea.md`): the ground past the last thing that burns —
the dayside terminus, 19–40° of arc from any water, where the fire cycle simply stops, nothing
ever renews, most of what lives is asleep under the sand waiting for water, and a predator that
feels your footfall does water-arithmetic instead of chasing (so a droid is invisible to the
food web).

**Tier: RimMandrake (`RM_`).** A distance-from-water terminus desert with things swimming
under the sand is a biome any RimWorld game can use; nothing in the sheet names Ash'karr or
Tatooine. "Dune Sea" IS Tatooine and stays the Utinni-tier campaign label patched over it.
Note row 0 is already not a vanilla label — vanilla's is `extreme desert`.

| # | defName | player label | why it fits this biome |
|---|---------|--------------|------------------------|
| **0** | **`RM_DeepDesert`** | **the Deep Desert** (ships if you strike nothing) | The sheet's own title. Plain, not a vanilla label, and a stranger reading a biome list instantly gets "further than desert". **Recommended — the working name is the right one here.** |
| 1 | `RM_Stillsand` | the Stillsand | Nothing here moves unless it has to and nothing renews: the shadow you cast never changes length, predators watch rather than pursue, what died is still lying where it fell. One coined word in the house style (Greentide, Webwork). |
| 2 | `RM_SleepingSands` | the Sleeping Sands | "It looks empty. It is not empty — most of it is asleep, and it is waiting for water." Names the twist rather than the heat. |
| 3 | `RM_DrySea` | the Dry Sea | "It ends the way an ocean ends", and things swim beneath its surface. Keeps the sea idea at the RimMandrake tier without using the Tatooine word. |
| 4 | `RM_Terminus` | the Terminus | The canon anchor (R-H6d) calls it the dayside terminus — the end of the ground. Strongest in-fiction, weakest on a biome list (says nothing about sand or heat). |

## 2. RM_ShadowDesert  (today `RUT_Desert`, "the Desert")

**What it is** (`desert.md`): the livable desert, arc 60–88°, where the sun sits a hand's width
above the horizon and never moves, so every rock throws a permanent shadow four times its own
height — life is a sprint between islands of shade across ground that kills in the open, and
the populations are small but steady enough for a colony to live off.

**Tier: RimMandrake (`RM_`).** A low-fixed-sun shade-patch desert is pure geometry, usable by
any tidally-locked or fixed-sun scenario; nothing campaign-specific in the sheet. Vanilla owns
`desert`, so the working name already had to move.

| # | defName | player label | why it fits this biome |
|---|---------|--------------|------------------------|
| 0 | `RM_ShadowDesert` | the Shadow Desert (ships if you strike nothing) | The spec's invention, from the sheet's "islands of shade". Accurate, but "shadow" reads sinister, and the sheet's whole point is that the shade is the GIFT — the reason this one can be lived in. |
| **1** | **`RM_LongShade`** | **the Long Shade** | The sheet's own thematic handle. Four-times-longer shadows cast by twice as many objects at half the temperature — "long" carries the low-sun geometry that makes this biome, and it is the kind of name we already ship (the Scald, the Rot). **Recommended.** |
| 2 | `RM_ShadeDesert` | the Shade Desert | Same idea as row 1 but keeps "desert" in the label so a list-reader knows the climate at a glance. Safer, plainer. |
| 3 | `RM_LowSun` | the Low Sun | Names the anomaly directly: not water, not heat — a 14° sun that never rises or sets. Distinctive; tells a stranger nothing about sand. |
| 4 | `RM_ShadowIslands` | the Shadow Islands | "Patches, not cover: discrete islands of survivable dark". Names the sprint economy — the gap between islands is the number that decides what lives here. Two words, a bit long. |

## 3. RM_FogShrubland  (today `RUT_AridShrubland`, "the arid shrubland")

**What it is** (`arid_shrubland.md`): knee-high silver-green fuzz at eerily even spacing to
every horizon, all of it leaning sunward and all of it moving in a wind that never stops; no
rain ever falls — the only water is fog carried in on the ground-wind from the stormwall — and
it is mild, which is the trap: cover is everywhere, for everything, so the danger becomes each
other and whatever is under the fuzz.

**On "arid" vs "fog":** the sheet is titled after the vanilla def it currently borrows
(`AridShrubland`); its §2 names the biome's anomaly as FOG outright ("Terminator approach ×
the anomaly of FOG … each shrubland is the plume of the sea upwind of it"). So "Fog" is the
sheet's mechanism, not a disagreement with it — and `arid shrubland` is a vanilla label a
RimMandrake mod should not reuse (architecture §7 Q2). Every row below keeps the fog.

**Tier: RimMandrake (`RM_`).** Fog-fed, rainless, wind-combed scrub on a terminator approach
is a climate, not a campaign; nothing in the sheet is Star Wars or Ash'karr-only.

| # | defName | player label | why it fits this biome |
|---|---------|--------------|------------------------|
| 0 | `RM_FogShrubland` | the Fog Shrubland (ships if you strike nothing) | The spec's invention. Accurate; half of it is still vanilla's word, and two words is the longest label form we ship. |
| **1** | **`RM_Fogscrub`** | **the Fogscrub** | One coined word in the house style (Greentide, Webwork, Pyrelands): fog is the water source, scrub is the plant form — both halves true from the first screen. **Recommended.** |
| 2 | `RM_Hush` | the Hush | The sheet's thematic handle: the first mild ground on the dayside, sightlines gone, everything hidden and quiet. Most evocative; tells a stranger nothing about what grows there. |
| 3 | `RM_LeaningScrub` | the Leaning Scrub | The sheet's gesture — "everything leans toward the light" — is the single most visible thing about the place. |
| 4 | `RM_DewScrub` | the Dew Scrub | The fog arrives and condenses; the shrubland's own regions are already called Dew Belt / Dew Horn, so the word is in the fiction. ⚠️ Same word as two region names, which the article ruling would then make read differently ("Dew Belt" vs "the Dew Scrub"). |

## 4. RUT_Scarlands — rename (ruled today; collides with Odyssey's `Scarlands`)

**What it is** (`the_scarlands.md`): the wound that never closed — crater fields and slag hills
on shattered megastructure floors, bunkers, embankments and turret rings of a colossal ancient
defence all facing outward against an enemy nobody can name, ground poisoned in a way that
never fades, mad animals, beautiful lethal pools, and machines that still defend it for reasons
they do not give.

**The collision, MEASURED:** Odyssey ships `Defs/Odyssey/BiomeDefs/Scarlands.xml` with
defName `Scarlands`, label `scarlands` (lowercase, no article); ours is `RUT_Scarlands`, label
`the Scarlands`. Same word in the same list, so the collision stands even though the two
strings are not byte-identical. Every row below changes BOTH layers.

**Tier: RimMandrake (`RM_`)** — where the architecture already puts it (`mandrake.rm.scarlands`
→ now `mandrake.rm.<newname>`). A poisoned ancient battlefield built on Odyssey's own ruins,
craters and megastructure floor is any-RimWorld content (it needs Odyssey either way); the
campaign truths — who fought here, the Sentinels, the Cathedral — are §GM and stay Utinni.
**§6.1 check:** no candidate names the Rakata, the Assailants or the Cathedral; every name
below is drawn from the §P register the players are allowed to hear.

| # | defName | player label | why it fits this biome |
|---|---------|--------------|------------------------|
| **1** | **`RM_Warscar`** | **the Warscar** | Keeps the "scar" root the sheet was built on and adds the one thing that makes it a place — the war anomaly ("owes nothing to climate and everything to a single day at the end of an ancient war"). Singular-noun house form (the Scald, the Rot, the Forge); nothing in a vanilla list looks like it. **Recommended.** |
| 2 | `RM_Slaglands` | the Slaglands | Slag hills on megastructure floors; the closest in shape to the old name. ⚠️ Two letters from "scarlands" in a biome list — fixes the collision on paper, not by eye. |
| 3 | `RM_LastStand` | the Last Stand | The sheet's thematic handle and the story every bunker tells; §P-safe. Reads as an event rather than a place — fine as flavour, odd in a biome column. |
| 4 | `RM_Craterlands` | the Craterlands | The L/M/S craters are the donor's most visible gen-step and the first thing the map shows. Plain, generic, a little flat for the wound-that-never-closed. |
| 5 | `RM_CursedGround` | the Cursed Ground | The Jawa's flat testimony ("the place is cursed", §P). Best as the Utinni campaign label over a plainer RimMandrake name (e.g. row 1 or 4) rather than as the RM name itself. |

## How to answer

Pick a number per biome — e.g. `1: 0, 2: 1, 3: 1, 4: 1` — or write your own name in place of
any row (a defName is derivable from a label, so the label alone is enough). Partial answers
work: each biome's mod split runs on its own the moment its name lands. Strike nothing on
biomes 1–3 and row 0 ships; Scarlands has no row 0 and waits for a pick.
