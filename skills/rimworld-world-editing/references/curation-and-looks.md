# Curation posture, the frozen whitelist, and making the planet look right

## 12. 🔴 Curation posture: WHITELIST — owner's ruling, 2026-08-15

**Default is EXCLUDE.** No tile mutator and no landmark appears on our planet unless it
has been explicitly whitelisted. "Not yet reviewed" therefore means **stripped**, not
"pending" — a half-finished review yields a bare planet, never a polluted one.

**Why, in one line:** a whitelist stays correct when a mod updates and adds new content;
a blacklist silently lets the new content in. With **336 `TileMutatorDef`s across 9 mods**
plus **113 `LandmarkDef`s**, that is the difference between a planet that stays curated
and one that drifts every time the Workshop updates.

⛔ **We are NOT using Cherry Picker for this.** Owner's ruling: *"we won't use Cherrypicker
here, but simply clean the map."* Mutators and landmarks are stored **in the save**, so
the decision is applied as a **world edit** — strip everything unwhitelisted out of
`tileMutatorDefs` / the landmarks dict. That is strictly better than removing the def:
Alpha Biomes keeps contributing its biomes, plants and animals while its
`AB_DessertTrees` (yes, dessert — they are candy trees) never appear on our world.

⇒ Any export from the review sheet MUST carry its posture explicitly
(`{"posture": "whitelist", "whitelisted": [...] }`) so a consuming tool can never
misread a sparse file as "strip only these few".

📌 Scale check for whoever runs the strip: **Vanilla Landmarks Expanded 144 mutators ·
Odyssey 82 · Alpha Biomes 48 · Geological Landforms 44**, and the same four dominate the
landmark list. Review by MOD, not alphabetically.

---

## 14. Making the planet LOOK right (researched 2026-08-15)

- 🔑 **There is no separate "WMB core".** World-map beautification for VANILLA biomes is
  built into **ReGrowth 2** (`ReGrowth.BOTR.Core`), which we already run — its
  `Textures/WorldMaterials/BiomesKit/` carries `Desert`, `ExtremeDesert`,
  `AridShrubland`. Nothing to add.
- ⛔ **Do NOT install World Map Beautification Project (Continued)** (`zal.wmbp`).
  ReGrowth 2's `About.xml` lists it under `incompatibleWith`, and WMBP's own page says it
  is unnecessary alongside ReGrowth. It also adds forests and hills — wrong for a desert
  planet.
- ✅ **Free coverage we are missing:** `noxilie.regrow.wmb.morevanillabiomes` is INSTALLED
  but INACTIVE while `zylle.MoreVanillaBiomes` is ACTIVE.
- The three worth adding for an orbital look: **RW - Planet Atmosphere** (3272330410,
  atmospheric-scattering shader — the actual "from space" effect), **World Map Enhanced
  (Continued)** (3599967849, repaints the ground texture ReGrowth's sprites sit on; load
  AFTER all biome mods), **Smart Odyssey** (3522762411, lowers landmark/mutator
  commonality — the only real declutter lever).
- ⚠️ **No mod hides world-map icons.** Vanilla 1.6 has its own world-object and
  landform-text toggles — use those. Our clutter comes from **Vanilla Landmarks Expanded**
  (+59 landmarks, cannot be disabled per its FAQ) and **MutatorWorldIcons**.
- ⚠️ **Map Mode Framework does not hide anything** — it only recolours hexes, and it is
  what makes the planet read as flat political hexes. Switch OFF Faction Territories mode
  before judging how the world looks.
- ✅ **My Little Planet (`Oblitus.MyLittlePlanet`, workshop 1117406550) SUPPORTS 1.6 and is
  ACTIVE.** Its `About.xml` lists 1.6 and it ships a `1.6/Assemblies` folder — an earlier
  note here read "1.5 max, leave it off" and was wrong by 2026-08-16, corrected against the
  files. **It is the only lever on tile count**: `TileSize.cs` transpiles the Create World
  page next to `PlanetCoverageTip` and adds a slider writing
  `PlanetLayerSettingsDefOf.Surface.settings.subdivisions`, range **6–10** (10 = vanilla
  default). Each step down is roughly **÷4 tiles**. Measured anchor: subdivisions 10 at
  coverage 0.05 = **3,787 tiles**.

---

## 15. ✅ FROZEN: the world-map element whitelist — owner, 2026-08-16

`design/Jawa/worldbuilding/review/worldmap_elements.prefill.json` now holds the
**shipping curation decisions** and carries `"frozen": true`.

```
296 whitelisted   52 rejected   2 left undecided   332 notes
```

⚠️ **The 2 undecided are STRIPPED, deliberately** — `VEE_Cactus_Barrel` and
`VEE_Cactus_Beavertail`, both occurring 0 times in the current world. Under whitelist
posture, undecided means excluded; the owner froze with them open, so that is the call.

🔴 **`worldmap_prefill.py` now REFUSES to run.** It would regenerate CHECK's original
guesses over the owner's work. It requires
`--i-know-this-overwrites-the-owners-decisions` to proceed. `worldmap_review.py` is
unaffected — regenerating the SHEET is safe and reads the frozen file.

⇒ The whitelist is now an input to the world build, not an open question. Anything not in
those 296 gets stripped from the planet when the strip pass runs.
