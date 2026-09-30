# The Stillsand — bedazzle review (movements 1–2), 2026-09-29

Item: `STILLSAND_BEDAZZLE_SITTING_1` · program row 9 of `infrastructure/state/items/BAROQUE_BEDAZZLE_PROGRAM_1.md`.
Builds on the ruled sitting `stillsand_bedazzle_2026-09-27.md` (14 questions, all ruled) and the
owner-reviewed `stillsand_roster_fillout_2026-09-27.md`. **Nothing ruled there is re-argued here.**
This pass scores what those rulings delivered, finds what they left open, and lays out the slate
for movement 3. Template: `longshade_bedazzle_review_2026-09-29.md`. Everything below was MEASURED
this pass (2026-09-29) from `src/`, the ledger shards (event key `id`), the two frozen sheets and the
committed artpipe stores, unless it is marked otherwise. The artpipe PNGs themselves sit in the shared
tree's gitignored `_artsrc/`. Art state here is read from the committed `registry.jsonl` and `done/`
manifests.

## 1. Name mapping confirmation

The biome goes by **four names, and they cover one def-pair**:

| where | name | evidence |
|---|---|---|
| program table row 9, ruled biome name | **Stillsand** | `src/RimMandrake/Stillsand/About/About.xml`, packageId `mandrake.rm.stillsand`, BiomeDef `RM_Stillsand`, label *"the Stillsand"* |
| frozen campaign twin | **`RUT_ExtremeDesert`** | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ExtremeDesert.xml` (frozen 2026-09-24; serves the saved world until the terminal paint) |
| the two frozen sheets that bind the one def (R22 union) | **`dune_sea.md`** + **`deep_desert.md`** | roster `rosters/dune_sea_deep_desert.json`; names batch 4d |
| owner/ruling shorthand | **"the Deep Desert"** | the Solar Heat ruling's *"sideways shade (deep desert)"*, and the `RM_Stillsand` def's own `RM_SunHeatExtension` comment: *"the Deep Desert (this def merges deep_desert.md + dune_sea.md)"* |

🔴 **The Dune Sea is a REGION label inside the Stillsand, not a biome** (owner, typed 2026-09-27:
*"Dune Sea is a region, not a biome. Be careful!"*). No doc may give it a def, a roster or a split.
The Utinni cast patch is `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Stillsand.xml`, and all
four of its `PatchOperationConditional` ops target `RM_Stillsand` by their own xpath. It is **not this
biome**: `RM_LongShade`/`RUT_Desert` (row 8, `desert.md`), `RM_BlueDesert` (row 3), or
`RM_LeaningScrub` (row 7). No pre-rename residue is owed. One label is drift, not a ruled name:
`RM_Ikee` now carries the label **"drageye"**. FOUNDRY chose it when the owner ruled
(`CONTAGION_IKEE_NAME_COLLISION_1`, 2026-09-29) that the Contagion keeps "ikee" and the Stillsand's
eye gets "a new distinct label". So the word is FOUNDRY's, and it is not in the Stillsand accent. It
goes on the card as a row (§5).

## 2. What's there

Sources read: all of `src/RimMandrake/Stillsand/` (biome, 10 race files, flora, mound, incident, 5 C#
files), `WildAnimals_Stillsand.xml` (ops resolved from their own xpath, `<wildAnimals>` parsed as
elements), `mandrake.rm.movingdunes` `BiomeBindings.xml`, the CreatureBehaviors sun/shade sources,
`DeepDesertTribes.xml`, the Sarlacc mod's About, both sheets plus their amendments, both 09-27 docs, the
closed items `STILLSAND_DESIGN_SITTING_1` / `STILLSAND_RULED_CONTENT_1` / `STILLSAND_RM_MOD_BUILD_1` /
`STILLSAND_KORRUM_HOLE_1` / `SANDBUSTER_CASTES_BUILD_1` / `DESERT_CAVERN_BEAST_EGGS_1` /
`DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1` / `SHADE_GEAR_FAMILY_1`, the live item `SOLAR_HEAT_EXPOSURE_1`,
and every ledger event on a STILLSAND_*, DUNESEA_*, EXTREME_DESERT_* or SANDBUSTER_* id.

### BiomeDef(s)

- **`RM_Stillsand`** (`Defs/BiomeDefs/RM_Stillsand_Biome.xml`). Hard deps: FlowWorks and
  creaturebehaviors, with DBH Lite in loadAfter. The worker is vanilla `BiomeWorker_ExtremeDesert`.
  `isExtremeBiome`, animalDensity **0.1**, plantDensity **0.008**, forageability **0.0**, and roads,
  rivers and farming camps are all off. Weather is Clear 95 / DryThunderstorm 1 / **Sandstorm 4
  (Odyssey's stock def)**, with every wet weather at 0. Terrain is all Sand plus **`RM_DeepSand`**
  patches at threshold 0.2 / perlin 0.03 / minSize 60, which is the ruled "Muchly" setting
  (`DEEP_SAND_WALKABLE_TERRAIN_1`). The def's one modExtension is **`RM_SunHeatExtension`
  `heatKind=lowSun`, heatOffsetC 35** (§3). `allowedPackAnimals` is empty on purpose (canon beasts
  only, Utinni-patched).
- **`RUT_ExtremeDesert`**: the frozen twin. It keeps its original RSW_ copies of every tier-moved
  row until Phase B.
- **Dunes engine bound** (Q12, done): `mandrake.rm.movingdunes`' `BiomeBindings.xml` now patches
  `RM_Stillsand`, so Werner slabs, `BuryThingsAt`, `RM_Dunes_BuriedCache` and plant choke run here.
  The engine buries and uncovers generic caches. **No Stillsand loot table, emergence set piece or
  bone field exists** (marquee #3's content half).

### Flora

**Free tier, inline (2 rows):** `RM_LightPipeNub` 0.1 (harvest → **`RM_Biosilica`**, built by
`STILLSAND_RULED_CONTENT_1`) · `RM_Ollim` 0.01 (fells to **`RM_OllimWood`**, which carries the ruled
fire-immune, hammer-weak stat signature). **Campaign, patch-added:** `RSW_Plant_Bloddle` 0.05 (canon).

**Ruled, art-reviewed, NOT BUILT:** hourbloom (KEEP), glasscrust (KEEP), kneel ollim (IMPROVE → `_b`
redo validated). No defs, and **no build item carries them** (§5).

### Fauna (def + patch-added, merged)

**Free tier, inline — 8 rows**, bodySize read from `race/baseBodySize`, behaviour from descriptions
and comps:

| row | comm | bs | what it is (from its description) | mechanism (live) |
|---|---:|---:|---|---|
| `RM_Oommok` | 0.0005 | **18.0** | the mirror-plated walking mountain | `RM_CompProperties_ShadowCaster` (commensal follow radius 5) |
| `RM_Siidda` | 0.15 | 0.15 | desiccated dust-animal that a sandstorm or a wound wakes | vanilla `CanBeDormant` + `WakeUpDormant` |
| `RM_ShadeMite` | 0.06 | 0.18 | grain scuttler that lives inside the giant's moving shadow | `RM_ShadowFollowerExtension` (third consumer, `eecf7d496`/`201896a5e`) |
| `RM_Ikee` "drageye" | 0.15 | 0.15 | a dragging eye on tentacles | none (Q8 shrink applied) |
| `RM_Vozzik` | 0.0005 | 5.0 | a barely-moving slug giant | `CompProperties_InnateAbility`, SWBestiary's comp, MayRequire-gated. The free mod's own giant borrows an RSW-tier comp |
| `RM_Vekka` | 0.5 | 2.0 | big-cat sand-swimmer, claws-first strike | none. Depth-arm annotated |
| `RM_Drazzik` | 0.05 | 2.2 | lies under the sand drumming "fat and wounded" | `RM_CompDrumLure`; lays **`RM_DrazzikEggFertilized`** (`ProximityHatch`, hatches **`RM_Nizzek`**, hostile from the shell) |
| `RM_Aurrok` | 0.15 | 4.0 | heat-sail grazer, grown to giant (Q8) | Milkable |

**Built, event-only (not in `wildAnimals`, by design):** the **sand busters**, `RM_Ruukka` (bs 5.0
eruptor), `RM_Oorrik` (bs 0.18 swarm) and `RM_SandBusterMound` (dormant, SpawnerPawn/SpawnerHives).
Behind them sit `RM_IncidentWorker_SandBusterEruption` + `RM_SandBusterTunnelSpawner`, and the
**planet-wide ban** of Core's `Infestation` lives in UtinniPatches
(`SANDBUSTER_CASTES_BUILD_1`, closed `0c6e84064`). Marquee #1 is **BUILT**.

**Built, wired NOWHERE:** `RM_Guzzka` (bs 5.5, the cavern beast) and its **`RM_GuzzkaEggFertilized`
/ `Unfertilized`**, which carry DBH `WaterExt`: *"the best drink of water a person could carry"*
(`DESERT_CAVERN_BEAST_EGGS_1`, closed `dac89fd18`). No BiomeDef, patch or genstep names it, because
the caverns it lives in are unauthored (§5).

**Campaign, patch-added (two `wildAnimals` ops):** canon `RSW_Kreetle` 0.2 · `RSW_WarWyrm` 0.2 (bs
15) · `RSW_KraytDragon` 0.15 (bs 12) · `RSW_GraniteSlug` 0.1 · `RSW_Scurrier` 0.1 · `RSW_Gizka` 0.01 ·
`RSW_GreaterKraytDragon` 0.001, plus **`RM_Qorrax` 0.5**. Its ThingDef still lives in Utinni-tier
`Absorbed_Cephaloids_Defs.xml`, so the invented sand-swimmer is patch-routed, not inline. Pack:
Bantha / Ronto / Eopie / Jamel / Falumpaset (Utinni only).

**Ruled, art-reviewed, NOT BUILT (the fill-out):** soorrak (REGEN → `_b` validated), gaanok, loomma
(IMPROVE → `_b` validated), liikka, duumma, veessa (KEEP). None has a def and no item carries them.
**vaalok**, the free-tier pack giant, was drafted and probe-clean. Q11 says it "rides the pack-animal
build", and that build does not exist. So **standalone `RM_Stillsand` still generates no trader
caravans.**

Totals: **free tier 8 wild + 3 event castes + 1 unwired**; campaign cast **16** wired species. With
the ruled-but-unbuilt fill-out, the free tier reaches **14 wild**.

### Terrain / weather / mechanics / C#

- **Terrain:** Sand + `RM_DeepSand` (walkable, pathCost 300). The dunes engine moves it. No owned
  yardang, cavern, brine or canyon terrain.
- **Weather:** no owned WeatherDef, GameCondition or sky lock. 🔴 **The sheet's first ban is broken
  as shipped:** *"⛔ No day-night cycle, no dawn/dusk lighting, no moving shadows"* (dune_sea §6).
  `RM_Stillsand` carries no `RM_PinnedSunExtension`, so the rendered light and shadows follow the
  vanilla day. The mechanical shade grid, meanwhile, already uses a fixed per-tile sun vector (§3).
  The 09-27 doc priced the fix in its §5 ("eternal noon — permanent glow lock") and it was never
  carded. The destructive, seeding sandstorm (deep_desert §8) is also unbuilt.
- **Mechanics live:** the sand-buster eruption and its planet ban · drum-lure predation · egg-trap
  clutches (proximity hatch) · dormancy (siidda, mound) · shadow-caster/follower (oommok → shade mite)
  · moving dunes + burial · deep sand · **sun heat** (lowSun: heat, sun-cost pathing, rest-dash-rest,
  sun-load readout, inherited from `SOLAR_HEAT_EXPOSURE_1`, which is planet-wide and not ours to
  claim as unique).
- **Mechanics ruled, unbuilt:** marquee #2, *the crossing with the giant*. The follow-a-moving-shadow
  keystone is built; the caravan/heat payoff is not. Marquee #3, *the buried record*: the engine is
  bound, but there is no loot register, no emergence set pieces and no bone fields. The eggs-as-water
  cheap swap: the eggs exist, and no carry/canteen economy or clutch placement uses them.
- **C# in this mod:** the eruption incident + tunnel spawner + settings (5 files). Everything else
  is kit.
- **Lore/ideology:** the **Sun-Debt** ideoligion is BUILT, on the Deep Desert Tribes reskin
  (`DeepDesertTribes.xml`: *"The sun lends and the sand collects… We take back what was drawn"*).
  Those tribes hold this biome (both sheets, §8). The Sarlacc's draft stage names echo it, and a
  Utinni-side "taken-and-returned" Sun-Debt patch is owed by `SARLACC_HABITAT_BUILD_1`. **Nothing
  ties the biome itself to the Sun-Debt**: no precept, ritual, incident or site. Sh'kaar (the evil
  sun) is PARKED at the Long Shade and is not ours to take.
- **Sound:** none. No SoundDef, no ambient, and no register in either sheet.
- **Ship:** no Stillsand row in `BIOME_SHIP_CONTRIBUTIONS_1`. The 09-27 doc's §6 (biosilica lens
  array, egg cistern, solar catch-yard) was never on the card agenda, so it is **unruled**.

### Art status per cast member

I resolved every `texPath` in the mod against every `src/*/*/Textures` tree (folder-aware), then
searched the artpipe registry, `done/`, `_artsrc/`, `pending/`, `active/`, `failed/` and
`_withdrawn/` by current AND prior spellings. Probes: `soorrak` 42 registry lines and `korrum` 6
`done/` files, so both instruments see.

| cast member | texPath state | artpipe |
|---|---|---|
| `RM_Ikee` | ✅ resolves (`Stillsand/Textures/.../RM_Ikee`, 3 facings) | `RM_Ikee_*` validated. Done |
| `RM_LightPipeNub`, `RM_Ollim`, `RM_OllimWood` | resolve via **SWBestiary's** `RSW_` texture paths. The free mod borrows campaign-tier textures | `rslpn_v1` / `rswollim_v1` / `rswollimwood_v1` done. Copy-only |
| `RM_Oommok` | `RM_MirrorGiant/...` → **NOWHERE** (magenta) | **`rmmirrorgiant_v1` done, 6 files**. Wire-only |
| `RM_Siidda` | `RM_DustHusk/...` → **NOWHERE** | **`rmdusthusk_v1` done, 6**. Wire-only |
| `RM_ShadeMite` | **NOWHERE** | **`rmshademite_v1` + `_v2` validated (6)**. Wire-only |
| `RM_Ruukka`, `RM_Oorrik`, `RM_SandBusterMound` | **NOWHERE** (the mound points at vanilla `Hive`, which renders) | `RM_Ruukka_*`, `RM_Oorrik_*` validated 3+3; `RM_SandBusterMound_south` 1. Wire-only |
| `RM_Aurrok` | `AA_SpinedGow/*`: **Alpha Animals' texture**. Magenta without `sarg.alphaanimals` | 0 under aurrok / spinedgow. **Owed** |
| `RM_Vozzik`, `RM_Vekka`, `RM_Drazzik`, `RM_Guzzka` | **NOWHERE** | 0 under current or port names (vozzik / vekka / sandlion / drazzik / guzzka / cavernbeast). **Owed** |
| `RM_Nizzek` | vanilla Chicken (placeholder) | none. Owed (small) |
| `RM_Biosilica` | **NOWHERE** | 0. Owed (icon) |
| egg items (drazzik, guzzka) | SWBestiary `swresource/EggScaled` | acceptable placeholder |
| fill-out six + three flora | no def | **all validated**, owner-ruled 2026-09-27; redo `_b` sets landed for soorrak / gaanok / loomma / kneel ollim |
| `RM_Qorrax` (patch-added) | Utinni def | `RM_Qorrax_*` validated, KEEP. Wire with its tier move |

## 3. Heat kind

**Declared and built: `lowSun`** (`RM_Stillsand` → `RM_SunHeatExtension heatKind=lowSun`,
heatOffsetC 35, first value). Three pieces of evidence agree:

1. **The owner's own words** on the Solar Heat ruling: *"…and there shade won't help you (in steam)
   or sideways shade (deep desert)"*. "The deep desert" is this def (§1).
2. **The sheet geometry.** deep_desert §0 puts its regions at **arc 50–72°**. The shipped shade grid
   takes elevation = 90 − arc per tile (`RM_MapComponent_ShadeGrid.ResolveSun`, via the heat
   extension's substellar geometry, clamped 5–60°). That gives the far ring a **sun at 18–40°**,
   which is a real low sun with long lee shadows.
3. **The code's semantics.** Under `lowSun`, `RM_SunHeatMath.Exposure` protects only on cast shade or
   a *thick* roof: `cover = max(thickRoof ? 1 : 0, castShade)`. A parasol, awning or thin roof over
   open ground does nothing, and a wall's lee, an ollim, a wreck, a rock face or an enclosed room
   does protect.

⚠️ **One tension to card, not to fix.** dune_sea.md places the Dune Sea *region* at **θ 0–40** and
calls its light *"directly overhead-ish"*, and deep_desert §9 says *"flat, vertical"*. The
grid's per-tile geometry already expresses this honestly: near the substellar point elevation
clamps to 60° and the lee shadows shrink toward nothing. So the Dune Sea region is the **shadeless**
end of a low-sun biome. That reads the sheet's own §7 *"Not water, not shade, not cover"* literally,
with one heat kind def-wide. **Recommendation: keep `lowSun` def-wide** (one def, one kind, as R22
and Q13 require). The owner should know that the Dune Sea region gets almost no cast shade by design.

**What shade gear does here** (`SHADE_GEAR_FAMILY_1`, closed; `RM_SunHeatMath.GearKindFactor`):

- the **sun shield** (a standing panel with a lee) is the one piece that works;
- the **parasol** and **shade tent** are weak (their `lowSunFactor`);
- the Long Shade's hide-cloth bonus carries over as a stuff bonus, but the Long Shade's hide is the
  Long Shade's.

⇒ The Stillsand's gear is a **wall you carry and plant**. In the Dune Sea region even the shield
throws a short shadow, which is why the giant's moving shade (marquee #2) is the only real road there.

## 4. Nine-mark scorecard

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **The planet's only infestation.** The sand-buster eruption (`RM_IncidentWorker_SandBusterEruption`, tunnel spawner, dormant mound, ruukka + oorrik castes) is built and biome-gated, and the Utinni layer bans Core's `Infestation` everywhere else (`0c6e84064`). No other biome can erupt under your colony. Seconded by the drum-lure + proximity-hatch trap pair (drazzik → nizzek). Caveat: every caste is magenta until its finished art is wired. |
| 2 | Discoverable technology | **MISS** | Nothing teaches. `RM_Biosilica` exists as a harvest item, but **no recipe, research or building consumes it** (`git grep RM_Biosilica` finds only the flora file). The sheet's promised "real lenses" have no use. The solar offer (§7 ⭐) has no build. Eggs-as-water exist as items with no carry economy. |
| 3 | Unique resources | **HIT** | `RM_Biosilica` (the only non-volcanic glass on the planet), `RM_OllimWood` (fire-immune, hammer-weak, shipped stat signature), `RM_GuzzkaEgg*` (DBH water in a shell), `RM_DrazzikEgg*` (water, or a trap). Caveats: the guzzka is wired nowhere, so its egg cannot be found, and biosilica has no icon and no use. |
| 4 | Surprising creatures | **HIT** | A predator that drums the ground to sound like a wounded meal (drazzik). Eggs that hatch *at* you (nizzek). A dust-animal a storm wakes (siidda). A colony-floor eruption (ruukka). The fill-out's gaanok (the follower that waits for you to fail) and soorrak are art-ruled but have no defs. |
| 5 | GIANT beast | **HIT (art caveat)** | `RM_Oommok` bs **18.0**, the largest wired body on the planet's free tier, with `ShadowCaster` live and the shade mite following it. Its face is **magenta**: `rmmirrorgiant_v1` (6 files) is done and unwired. The crossing-with-the-giant payoff (marquee #2) is unbuilt. Second tier: aurrok 4.0, vozzik 5.0, ruukka 5.0, and canon WarWyrm/krayts in the campaign. |
| 6 | Gravship touch | **MISS** | Nothing references the ship in this biome's voice. The 09-27 doc §6 proposed a biosilica lens array, an egg cistern and a solar catch-yard, and none was carded. `BIOME_SHIP_CONTRIBUTIONS_1` has no Stillsand row. |
| 7 | Soundscape | **MISS** | No SoundDef, no ambient, no register in either sheet. For a biome whose drum-lure and eruptions are *vibration*, the ear is its most unused sense. |
| 8 | Interesting weather | **MISS** | Stock Clear/DryThunderstorm/Odyssey Sandstorm only. The sheet's destructive, seeding sandstorm (deep_desert §8) is unbuilt, and 🔴 the vanilla day-night sky **violates** dune_sea §6's first ban (§2). The moving dunes are terrain physics, not sky. |
| 9 | Relationship to the gods | **PARTIAL** | The **Sun-Debt** ideoligion is built and belongs to the tribes who hold this biome, and its theology ("the sun lends and the sand collects") is a desert liturgy waiting for a place. But no biome content touches it. Sh'kaar is the Long Shade's parked hook, not ours. |

**Score as built: 4 HIT / 1 PARTIAL / 4 MISS.** That is up from the program table's "content today:
1", because the rank-1 marquee, the tier move, the dunes binding, the shade-mite commensal and the
cavern beast all landed between 09-25 and 09-28. **What sets this biome apart: the physics is
done and the presence is missing.** The biome's own threats are built, but its face is magenta (six
finished render sets sit unwired), its roster fill-out has no defs, its sky breaks its own first
ban, and its crossing and buried-record marquees have engines with no content on them. Movement 3
here should aim at **the ear, the sky, the ship and the tech** (the four MISSes) without adding
surface busyness. The admission test still binds: *if an idea makes a Stillsand map look busier,
it is wrong.*

## 5. Ruled-but-unbuilt debt

Each item here is ruled, has no build item, and is owed regardless of what movement 3 rules. They
become movement-4 tickets.

1. **The fill-out cast: 6 creatures + 3 plants.** The owner ruled the art sheet 2026-09-27 (soorrak
   REGEN; gaanok / loomma / kneel ollim IMPROVE; liikka / duumma / veessa / hourbloom / glasscrust
   KEEP), and the redo `_b` sets are validated in the registry. **No def and no item exists.**
   `STILLSAND_RULED_CONTENT_1` explicitly held them "gated on the owner's review sheet". That gate
   opened and nothing was filed (`git grep soorrak|gaanok|… src infrastructure/state/items` → 0).
2. **The presentation wave: six finished render sets unwired.** `rmmirrorgiant_v1` → oommok,
   `rmdusthusk_v1` → siidda, `rmshademite_v1/v2` → shade mite, `RM_Ruukka` / `RM_Oorrik` /
   `RM_SandBusterMound` → the busters. Each texPath resolves nowhere in the repo. New art is owed
   for vozzik, vekka, drazzik, guzzka, aurrok (off Alpha Animals' texture), nizzek and the
   biosilica icon. The nub, ollim and wood still borrow SWBestiary's textures.
3. **Caverns: filed in the ledger with no item file.** `STILLSAND_CAVERN_AUTHORING_1` was filed
   2026-09-28 (BENCH), but no `items/` or `items/closed/` file exists. So the built guzzka and its
   prize eggs spawn nowhere, and deep_desert §8's "serious authoring effort belongs here" stays
   unplaced.
4. **Smaller ruled rows with no carrier:**
   - **vaalok**, the free-tier pack giant: Q11 rides it on a build that was never filed, so the
     standalone mod generates no traders.
   - **eemmok**, the probe-clean name Q11 ruled "rides its build": the commensal shipped as the
     English "shade mite". Rename owed, or rule the English name.
   - **qorrax**: still a Utinni-tier ThingDef patch-routed into an RM biome, where Q1 moved the other
     invented rows inline.
   - **vozzik**: carries an SWBestiary comp in the free tier.
   - Card rows: **"drageye"** (FOUNDRY's label, not an accent coin), and the eternal-noon sky lock
     the sheet's ban requires (§2; §8 #2).

## 6. Roster gaps and proposed fills

pending

## 7. Art already generated (never re-queue)

pending

## 8. Candidate mechanics slate, ranked

pending
