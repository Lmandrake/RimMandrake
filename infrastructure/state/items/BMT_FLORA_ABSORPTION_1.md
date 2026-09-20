# BMT_FLORA_ABSORPTION_1 — the absorption did fauna only; the flora was left behind

## the gap, MEASURED 2026-09-20

`BMT_FAUNA_ABSORPTION_1` ported 68 Biomes! Team defNames into our own `RSW_`
defs. Its name is literal: **fauna**. The flora was never absorbed, and
`biomesteam.biomescaverns` is **absent from the 621-mod active list**.

So **14 `BMT_` flora defs are still named in 8 live biome tables, and not one has
an `RSW_` equivalent anywhere in `src/`** (checked per defName, not by prefix):

| def | max weight | biomes |
|---|---:|---|
| `BMT_Plant_TreeTanglerootMangrove` | **1.5** | Miasma |
| `BMT_GiantLeaf` | **1.0** | Greentide 1.0, FeverWood 0.8 |
| `BMT_Plant_SewerReed` | 0.8 | Miasma |
| `BMT_Plant_TreeTwistingThornwood` | 0.6 | PoisonForest 0.6, CrackedLands 0.2 |
| `BMT_RainbowTongue` | 0.6 | Miasma |
| `BMT_FireLavender` | 0.6 | TheForge |
| `BMT_Plant_TwistingThorngrass` | 0.5 | CrackedLands |
| `BMT_Plant_Snaketails` | 0.5 | Miasma |
| `BMT_Plant_TreeMartyr` | 0.5 | PoisonForest |
| `BMT_Plant_TwistingThornweed` | 0.4 | CrackedLands |
| `BMT_Sagecrust` | 0.4 | TheForge |
| `BMT_Dewshrooms` | 0.4 | WeepingStones |
| `BMT_Plant_ScorchedStars` | 0.25 | Scarlands |
| `BMT_HeatsinkFungus` | 0.2 | TheForge |

🔴 **`BMT_Plant_TreeTanglerootMangrove` is the single heaviest plant in the
Miasma**, and the Miasma's whole identity is its mangroves. **`BMT_GiantLeaf` is
the heaviest in the Greentide.** These are not marginal rows — they are the
flagship flora of three biomes, and they cannot spawn.

⚠️ They are `MayRequire`-guarded, so there is **no crash and no error** — the
plants are simply absent. Same silent failure mode as
`BIOME_ROSTER_DEAD_SPECIES_REFS_1`.

## why this is different from the droids

The 21 desert droids looked identical to this and were NOT a real gap: Droidworks
had already absorbed them as `RSW_DW_OuterRim_*`, and a repoint fixed all 21.
🔑 **That check was run here first and came back empty** — `RSW_GiantLeaf`,
`RSW_Dewshrooms`, `RSW_FireLavender`, `RSW_Sagecrust`, `RSW_HeatsinkFungus`,
`RSW_Boneblade`, `RSW_Rocktooth`, `RSW_RainbowTongue` — none exists. There is
genuinely nothing ported to point at.

## spec

Follows `DONOR_DEFS_PORT_TO_OURS_1` (owner: *"Everything should be moved t our
own thing defs"*, *"Yes replace everything"*), and copies
`BMT_FAUNA_ABSORPTION_1`'s own method — read that port's header comment in
`src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
before starting; it is the operating manual.

1. **Source the donor XML.** ⚠️ `biomesteam.biomescaverns` is not in the active
   list — confirm whether its files are still in the Workshop folder before
   planning. If they are gone, these 14 must be authored from scratch against
   each biome's own card, which is a much larger job. **Establish that first**;
   it decides the shape of everything after.
2. **Port with reference closure** — the plant ThingDef and everything it pulls
   in. A ported plant with a dangling harvest ThingDef is broken.
3. **New art**, per the standing ruling — donor textures are not reused. Jobs
   through `fill_queue.py` only.
4. **Names**: these are plants, so `NONCANON_BEAST_RENAME_1` (beasts) does not
   bind them. Each biome already has a names doc pattern
   (`rot_flora_fauna_names.md`, `lantern_deeps_flora_names.md`) — follow it.
5. **Repoint the 8 biome tables** last, dropping the `MayRequire` since they
   become ours.

## Watch out

- 🔴 **Do not parse the donor XML as text** — the Alpha Biomes
  `<descriptionHyperlinks><ThingDef>` trap understated 11 rows by up to 6× and
  forced the owner to re-judge. `xml.etree.ElementTree`.
- 🔴 Plant mature size is `drawSize.x × visualSizeRange.max`; `drawSize` is 1.0
  across this project, so `visualSizeRange` is the knob.
- ⚠️ Three of these (`TwistingThornwood`/`Thorngrass`/`Thornweed`) are a family;
  `RUT_TwistingThornweed` ALREADY exists in `UtinniPatches`
  (`POLLUTED_LANDS_FLORA_PORT_1`, art landed) — check the overlap before
  authoring a fourth thornweed.
- ⚠️ Do not re-add `biomesteam.biomescaverns` to the mod list to "fix" this.
  `CAVERNS_PARITY_BUILD_1` retired it deliberately.

## verify

Zero `BMT_` names remain in any biome table; each of the 8 biomes still generates
with its flagship flora present; confirmed from a post-load def dump.

## criteria

The Miasma has its mangroves, the Greentide its giant leaf, and no biome's
headline plant depends on a mod we removed.

---

## 🔴 CORRECTIONS — BENCH, 2026-09-20, after FOUNDRY picked this up

Three things above are WRONG. Re-measured this window; act on these, not on the
original text.

### 1. It is NOT one donor, and mostly not Caverns

Only **5** of the 14 come from `biomesteam.biomescaverns`. **9 come from
`BiomesPollutedLands`** — a different mod, also ABSENT from the 621-mod active
list. Sources located in the repo's own vendored tree:

| from | defs |
|---|---|
| `vendor/mod_sources/BiomesCaverns_src/1.6/Defs/Plants/` | `BMT_GiantLeaf`, `BMT_FireLavender`, `BMT_Sagecrust`, `BMT_HeatsinkFungus`, `BMT_Dewshrooms` (⚠️ its file is `BMT_Seadew.xml` — name mismatch) |
| `vendor/mod_sources/BiomesPollutedLands/BiomesPollutedLands-main/1.6/Defs/ThingDefs_Plants/` | `BMT_Plant_TreeTanglerootMangrove`, `BMT_Plant_SewerReed`, `BMT_RainbowTongue`, `BMT_Plant_TreeMartyr`, `BMT_Plant_Snaketails`, `BMT_Plant_ScorchedStars`, `BMT_Plant_TreeTwistingThornwood`, `BMT_Plant_TwistingThorngrass`, `BMT_Plant_TwistingThornweed` |

### 2. ✅ The source IS available — this is a PORT, not from-scratch authoring

The spec's step 1 asked whether the donor files still exist and warned that
from-scratch authoring would be "a much larger job". **They exist.** All 14 were
located in `vendor/mod_sources/` (paths above). That risk is closed — do not
spend a pass re-establishing it.

### 3. 🔴 13 of the 14 are UNGUARDED — this is the CRASH class, not the silent one

The original text said these are `MayRequire`-guarded and therefore fail
silently. **Only `BMT_GiantLeaf` carries a guard.** MEASURED:

- **GUARDED (1):** `BMT_GiantLeaf` (`biomesteam.biomescaverns`) — fails silently.
- **UNGUARDED (13):** every other one, all in `<wildPlants>` — `BMT_Plant_TreeTanglerootMangrove`
  (Miasma 1.5), `BMT_Plant_SewerReed` (Miasma 0.8), `BMT_Plant_TreeTwistingThornwood`
  (PoisonForest 0.6, CrackedLands 0.2), `BMT_RainbowTongue` (Miasma 0.6),
  `BMT_FireLavender` (Forge 0.6), `BMT_Plant_TwistingThorngrass` (CrackedLands 0.5),
  `BMT_Plant_Snaketails` (Miasma 0.5), `BMT_Plant_TreeMartyr` (PoisonForest 0.5),
  `BMT_Plant_TwistingThornweed` (CrackedLands 0.4), `BMT_Sagecrust` (Forge 0.4),
  `BMT_Dewshrooms` (WeepingStones 0.4), `BMT_Plant_ScorchedStars` (Scarlands 0.25),
  `BMT_HeatsinkFungus` (Forge 0.2).

**All 14 MEASURED as 0 in the live dump** (`measure find --type ThingDef`,
`defs.sqlite mods=617/6a41e05c828eed67`, captured 2026-09-20T07:47:24Z) — a
measured absence, not a lookup failure.

⚠️ An unresolved cross-reference in a biome table is the failure mode
`BIOME_CAST_REFS_BREAK_MAPGEN_1` records, and it is exactly why
`WYYYSCHOKK_FERALISK_MERGE_1` removed `AA_Dunealisk` rather than leaving it: its
commit says *"an unresolved cross-ref in wildAnimals is a known crash"*. These 13
are the `wildPlants` equivalent and have been sitting unguarded across **7
biomes**. 🔑 **Establish whether `wildPlants` actually crashes mapgen the way
`wildAnimals` does before deciding urgency — I have not verified that, and the
two tables may not behave the same.** If it does, this stops being a content port
and becomes a live defect.

### 4. Not affected, do not chase

`BMT_Boneblade` and `BMT_Rocktooth` appear in a raw text grep of the BiomeDefs
folder but are NOT entries in any `wildPlants`/`wildAnimals` table — they are
prose in comments. 14 is the real count.
