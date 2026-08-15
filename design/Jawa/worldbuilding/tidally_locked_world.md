# The world is TIDALLY LOCKED — and it explains everything

_VISION, 2026-08-14. **Owner's ruling, and it is the largest single piece of
worldbuilding this project has produced.** Recorded the hour it was made. Mods
installed for it: `Tidally Locked` plus two others._

> **One face of the planet never turns away from the sun. The other never sees
> it. Everything that lives does so in the band between.**

---

## The three worlds on one planet

| | **DAYSIDE** | ⭐ **THE TERMINATOR** | 🔴 **NIGHTSIDE** |
|---|---|---|---|
| light | perpetual, unmoving sun | **perpetual twilight** | **perpetual night** |
| heat | scorching, worse toward the centre | temperate | **cold** |
| water | **none at the centre** · rare oases in the near-deserts | ⭐ **all of it** — the seas, the rivers | frozen or absent |
| who lives there | **the Galactic Empire**, at the dead centre · **the neutral droid factions** in low mountains with poisonous volcanic springs · the Hutts at the oases · Tuskens and the Trade Moot in the near-desert | **the Deepwater Compact** on the seas · **the Wildsteam Clan** on the rivers, in the jungles and poison marshes · the Homestead on the arable margin | ⭐ **the Forsakens' leavings.** Terrible and strange creatures. The Forgotten Arsenal |
| the player's relationship | where the work is | where the water is | ⭐ **where you go when you cannot be found** |

---

## ⭐⭐ What this SOLVES — and it is most of the campaign

**This is not flavour. It retires four separate design problems at once.**

### 1. Hiding stops being a mechanic and becomes a PLACE

**Owner's ruling: Imperial pursuit is greatly extended or terminated while the
player is on the nightside.**

I had specced hiding as *"it must cost progress, not hit points"* and hunted for
a mechanism. **The tidal lock gives it geography instead.** Go dark — literally —
and the hunt loses you. And the price is not a number:

- **no sun** → no solar, no crops, nothing grows
- **cold** → a species evolved for the dune sea is wrong here
- **terrible fauna** → the refuge is inhabited
- **distance** → everything you trade for is on the other side of a planet

⭐ **A refuge you cannot farm is the perfect hiding place**, because staying is
its own punishment and nobody has to author a timer.

### 2. It explains the forsaken crags

`AB_RockyCrags` carries a **hardcoded 0.34 sun-glow multiplier** and can never
roll clear weather — I had recorded that as a biome quirk. **It is not a quirk any
more. It is physics.** The dark biome *is* the nightside, and its own description
already says an ancient race partly terraformed this world and left.

⭐ **The Forsakens tried to fix a tidally locked planet and failed.** That is why
the dark never lifted, and it is the best back-story this world has been offered.

### 3. It explains why the water is where it is

🔴 **This SUPERSEDES my latitude rule.** I had written *"water increases with
latitude; the poles hold the standing water."* **Wrong axis.**

> **Water follows the TERMINATOR, not the poles.** It is the only band where
> water is neither boiled nor frozen.

⚠️ **But the seas must not read as a literal ring** — owner's explicit
instruction. **Elongated natural blobs lying NEAR the terminator, and one of them
near a pole** to make the planet feel alien rather than diagrammatic.

### 4. It explains the Empire's position, and the droids'

**The Empire holds the dead centre of the dayside — the harshest desert, no water
at all, volcanoes and mountains — because nobody else could.**

⭐ **That is the Empire's whole character expressed as a map position.** Their
power is logistics: they truck their own water and can therefore be anywhere,
including the one place with none. **A faction that holds the worst ground on the
planet is more frightening than one that holds the best.**

**And the neutral droid factions sit in the low mountains among poisonous
volcanic springs** — a place that kills anything that breathes, held by things
that do not.

---

## The Hutts: BESIDE the oasis, never on it

🔴 **Owner's correction, and it is a playability rule, not a fiction one:**

> **The Hutts dwell BESIDE an oasis, never on top of one — or the player can
> never reach the water at all.**

**But the oasis tile itself is the prize and must look it:**

- ⭐ **very heavily augmented** — the most built-up tile type in the game
- **swarming with Hutt-loyal defenders**
- rare, in the **near-deserts** between the centre and the terminator

⭐ **The design consequence is a genuine tactical choice, which "they own it" would
have foreclosed:** the water is reachable, guarded, and *not* the same tile as the
settlement. **You can raid the well without besieging the town** — and that is a
far better decision than a binary.

---

## Faction positions, revised

| faction | where, now |
|---|---|
| **Galactic Empire** | ⭐ **dead centre of the dayside.** No water, volcanoes, mountains |
| **neutral droid factions** | low mountains, **poisonous volcanic springs** |
| **Hutt Cartel** | **beside** the rare near-desert oases |
| **Deep Desert Tribes** | the near-desert, between centre and terminator |
| **Jawa Trade Moot** | the same band — circuits across the near-desert |
| **the Junkers** | wreck fields, wherever things fell |
| **Homestead Defense League** | the arable margin of the terminator |
| ⭐ **Wildsteam Clan** | **the rivers** — the wild jungles and poisonous marshes |
| ⭐ **Deepwater Compact** | **the seas of the twilight band** |
| **Geonosian Foundry Hive** | subterranean, dayside rock |
| **Ascendant Helix** | isolated, cold — **nightside edge** suits them |
| **Blackstar Company** | everywhere; they follow the money |
| 🔴 **the Forgotten Arsenal** | ⭐ **the nightside.** It is where the Forsakens left it |

---

## 🔴 What must change, urgently

1. **The sea spec is now wrong.** `worldgen_sea_spec.md` says *"three oddly-shaped
   bodies at HIGH LATITUDE, centroid nearer a pole than the equator."*
   **It must become: elongated blobs lying near the TERMINATOR, with one near a
   pole.** ⚠️ **CREATE is building to the old test right now.**
2. **`faction_world_spec.md` §4 geography** — the latitude bands are superseded by
   day / terminator / night. Rewrite.
3. **The biome verdicts shift**: cold biomes are no longer "poles only", they are
   **nightside**. And the harshest desert is **not** at the equator — it is at the
   **subsolar point.**

## ⚠️ One design caution, stated so it is deliberate

**If the nightside terminates the pursuit, a player could simply move there and
stay.** The ruling already prevents it — no sun, cold, terrible fauna, and every
trading partner a planet away — **but that must remain true in the numbers, not
just in the prose.** ⛔ **The moment the nightside becomes farmable, the campaign's
central tension is over.**

---

# ✅ THE MOD READ. It does far more than expected — and my axis correction was wrong.

_VISION, 2026-08-14, read from the mod's own defs and C# source. **PROJECT was
right to hold the spec before CREATE wrote code.**_

**`Alien Worlds - Tidally Locked`** — `7f.alienworlds.tidallylocked`, **ACTIVE**,
on the framework **`7f.alienworlds`**, also ACTIVE. Ships full source.

## 🔴 Correction: LATITUDE IS THE AXIS. I was wrong twice.

**The mod does not build a day face and a night face geographically. It remaps
TEMPERATURE onto LATITUDE.** Its whole planet def is one curve:

| latitude | avg temperature |
|---:|---:|
| **0.0** | ⭐ **+70 °C** — the subsolar point |
| 0.1 | +65 °C |
| ⭐ **0.5** | ⭐ **+14 °C — this is the terminator** |
| 1.0 | −37 °C |
| 1.3 | −70 °C |
| 2.0 | **−80 °C** — deep night |

⇒ **Low latitude is the burning dayside. Mid latitude is the twilight band. High
latitude — the poles — is the nightside.**

**So my original spec was accidentally half-right and my correction made it
worse.** I told CREATE *"not latitude, the terminator"* — **but the terminator IS
a latitude band on this planet.** The real target is **mid-latitude, around 0.4–0.6**:
not the equator, not the poles.

⚠️ **And the owner's "one body near a pole to feel alien" now means something
much better than a quirk: a sea on the NIGHTSIDE, frozen or freezing.**

## ⭐⭐ The framework can do most of this from XML, and it changes the build

**`PlanetTypeDef` exposes — all settable in a def, no C# required:**

| field | what it gives us |
|---|---|
| ⭐ **`elevationRange`** | **patches `WorldGenStep_Terrain.ElevationRange` directly — this is the ocean-share dial.** The 25% target may be one number in XML |
| ⭐ **`biomes` / `biomeBlacklist`** | **a per-planet-type biome whitelist and blacklist.** The owner's 29 removals may not need Cherry Picker at all |
| ⭐ **`biomeConfigs`** | per-biome **`scoreOffset`**, a **`workerClass` OVERRIDE**, and arbitrary `defFields` — the mod's own example is setting `inVacuum` |
| `globalBiomeConfig` | the same, applied to everything |
| `oceanBiome` / `lakeBiome` | ⭐ we can name **our own** ocean biome |
| `avgTempByLatitudeCurve` | the day/night gradient itself |
| `rainfallCurves` / `defaultRainfallCurve` | rainfall by world setting |
| `permaIceScoreOffset` · `sunlightFactor` · `steamGeyserFactor` | ⭐ **`sunlightFactor` is a global light multiplier** |
| `scenParts` · `hideWorldRivers` · textures | scenario and presentation |

## 🔴 What this does to the sea step

**The job shrinks to one thing.**

| need | route |
|---|---|
| **25% ocean** | ⭐ **XML — `elevationRange` on our own planet type.** Not code |
| **biome removals (29)** | ⭐ **XML — `biomeBlacklist`.** Possibly no Cherry Picker |
| **biome mix / commonality** | ⭐ **XML — `biomeConfigs.scoreOffset`**, and `workerClass` where a worker is the real gate |
| **three ragged blobs at mid-latitude** | 🔴 **the ONLY remaining code.** `elevationRange` sets how much sea there is, not where or what shape |

⇒ **We author our own `PlanetTypeDef` — a Jawa-world variant of the tidally locked
one — and the custom `WorldGenStep` reduces to arrangement alone.** That is a much
smaller build than the one PROJECT put a one-day kill condition on, and most of it
stops being C# entirely.

⚠️ **The mod's own description says "generating at least 50% of the planet is
recommended."** That is a worldgen-screen setting and it belongs on the checklist.

---

## ✅ OWNER'S RULINGS, 2026-08-14 — three answers that close open items

**1. 🔴 The pursuit is GREATLY EXTENDED on the nightside, never terminated.**

> **The player can always buy time. They can never buy safety.**

⭐ **This is the stronger design and it removes a whole class of problem.** A
pursuit that stops would mean a player who solves the nightside's problems has
solved the campaign's central threat — and it would force us to detect and price
"has the player cheated the hunt". **Extended-but-never-stopped needs no state, no
detection and no escalation ladder: the nightside is a reprieve, and reprieves
expire on their own.**

**2. 🔴 Jawa heat tolerance: RE-POINT the faction xenotypeSets at `BTD_Jawa`
(+20 °C).**

The sets currently name `OuterRim_Jawa`, which grants only +10 °C. **On a planet
whose subsolar point is +70 °C, halving the clan's heat tolerance would have
quietly made the deep dayside impassable to the player faction** — a balance
change nobody chose, arriving through a mod-priority accident.

⚠️ **This is a patch on every faction that fields Jawa**, and it must land
**before worldgen**, because `xenotypeSet` is read when pawns generate.

**3. Royalty's progression is ACCEPTED as lost.** A permanently hostile Empire
switches off titles, permits, honour and imperial favour. **A Jawa scavenger clan
earning imperial knighthood reads badly anyway**, and the Empire being
un-negotiable is the point. Recorded so nobody re-proposes it as a bug.

---

## ✅ ANSWERED FROM SOURCE — the blacklist HARD-EXCLUDES. And a whitelist is better.

_VISION, 2026-08-14, read from `PlanetTypeManager.cs:108-125` and
`PlanetTypeDef.cs:17-31`. The background agent died twice on server errors; this
was one grep._

**`GetBiomeScorePrefix` is a Harmony prefix on `BiomeWorker.GetScore`:**

```
if (activePlanetType == null ||
    (!biomeBlacklist.Contains(biome.defName) && (!biomes.Any() || biomes.Contains(biome.defName))))
        return true;          // run the original
__result = -1000f;
return false;                 // skip the original entirely
```

⭐ **So a blacklisted biome is forced to −1000 and the real worker never runs.**
That is a hard exclusion in practice — **nothing in the game scores anywhere near
−1000** — and it replaces 29 Cherry Picker keys with one list in one def.

### ⭐ And `<biomes>` is a WHITELIST — which is the better tool

`PlanetTypeDef.biomes` is *"biomes that can generate"*, and the code shows that
**if it is non-empty, anything absent is excluded.** So we have a choice:

| | blacklist 29 removals | ⭐ **whitelist ~35 survivors** |
|---|---|---|
| maintenance | every new mod's biomes leak in **by default** | ⭐ **new biomes are excluded by default** |
| failure mode | silent contamination — a biome we never chose appears | **silent absence** — a biome we wanted is missing, and we notice |
| review | 29 lines that must stay in sync with the install | **one list that IS the design** |

⇒ **Whitelist. `<biomes>` naming exactly what belongs on this planet.** It fails in
the direction we can see, and the owner has already added mods twice today —
**a blacklist would have to be revisited every time.**

⚠️ **If we whitelist, our ocean biome MUST be on the list.** The def's own comment:
*"oceanBiome / lakeBiome also have to be specified in `<biomes>`, otherwise they
won't spawn."*

### 🔴 Two limits of this lever, and the first one bites

1. **It patches `GetScore` — so it cannot touch anything not assigned by scoring.**
   ⚠️ **`Ocean` and `Lake` are `isBackgroundBiome` and are assigned by the
   ELEVATION threshold, not by a biome worker.** Blacklisting them would do
   **nothing**. Ocean share stays an `elevationRange` job, exactly as specced.
   *(`SeaIce` **is** score-based and can be excluded this way.)*
2. **`scoreOffset` is a postfix ADD to the vanilla score** — so it is a genuine
   commonality dial, not an override. **That is the biome-mix lever**, and it
   composes with the whitelist rather than replacing it.

---

## 🔴 THREE CORRECTIONS from CREATE — two of them to me, and one reverses my own advice

### 1. ⚠️ **BLACKLIST, not whitelist. I was wrong, and the reason is the layer biomes.**

I argued for whitelisting the ~26 survivors because a blacklist lets new mods leak
in. **That argument ignored 11 biomes that are not surface tiles at all** —
`Space`, `Orbit`, `Underground`, `Undercave`, `CQF_Undercave`,
`AM_UndergroundSpace`, `VQEA_AncientComplex` and kin.

🔴 **A whitelist excludes anything absent from it — and those are precisely the
entries nobody thinks to list.** Whitelisting the surface would silently break
space maps, the gravship's orbital layer and every pocket map in the game.

⭐ **So the failure directions are the opposite of what I claimed.** A blacklist
fails toward *"an unwanted biome appeared"* — visible, and one line to fix. **A
whitelist fails toward *"a pocket map does not generate"*** — invisible until
something the player needs is missing.

⇒ **Blacklist the 29. Leave `<biomes>` empty**, which the framework reads as *all
allowed*. Confirmed: blacklist wins over whitelist and an empty whitelist is
permissive.

### 2. 🔴 **PATCH the shipped def. Do NOT author our own planet type.**

**Only one `PlanetTypeDef` is active at a time** — `activePlanetType`, chosen in
mod settings and scribed per save. **So authoring a "Jawa world" would REPLACE
`TidallyLocked` and silently drop its temperature curve** — the one thing the
whole design now rests on.

⭐ **`<biomes>`, `<biomeBlacklist>`, `<biomeConfigs>` and `<elevationRange>` are
base-class fields, so a `PatchOperationAdd` into the shipped def gives us all of
it with tidal lock intact** and no selection question at all. **Much smaller than
a new planet type.**

⚠️ Patch by **`defName`**, not by class — the shipped def is a *subclass*,
`AlienWorlds.TidallyLocked.PlanetTypeDef`.

### 3. 🔴 **`elevationRange` is NOT the 25%-ocean dial. Stop calling it one.**

The mod author's own comment, verbatim:

> *"useful if you want more/less ocean. **note: I have absolutely no clue how it
> actually works**, but reducing the second number while keeping the first one at
> −500 seems to do things"*

**A knob its author does not understand, with no stated mapping to an ocean
fraction.** ⇒ **Coarse nudge only.** The **`WorldGenStep` measures the actual
fraction and hits the number** — that stays the mechanism, and my "the dial is in
XML" claim was too strong.

### What survives unchanged

✅ **The axis** — confirmed from the shipped curve: latitude, with **0.5 = +14 °C =
the terminator.**
✅ **`biomeConfigs[x].scoreOffset`** is the soft commonality dial and is exactly
what the owner's abundance verdicts become.
⚠️ **`oceanBiome` / `lakeBiome` must ALSO appear in `<biomes>`** if a whitelist is
ever used — a reason to keep `<biomes>` empty.

---

## ⭐⭐ THE NIGHTSIDE IS GRADED — owner, 2026-08-14. A fourth zone.

_Answering the three open biomes, the owner invented structure the design did not
have._

> **`HorrorWastes`** — *"might be a night-side area where some light remains so
> it's not quite the crags yet."*
> **`Glowforest`** — *"makes sense there too, like little oases of light in the
> middle of the dark."*
> **`PoisonForest`** — *"I want to experience it so I can judge it. Could be more
> weird dark-terminator terrain."*

⭐ **The nightside is no longer one thing. It has a gradient**, and that fixes a
problem I had not flagged: **a hemisphere of nothing but forsaken crags would be
monotonous.** A graded dark side has internal structure, and it gives the player
**landmarks in the dark**, which is exactly what a dark map needs most.

| band | biome | reads as |
|---|---|---|
| terminator | the seas, the jungles, the marshes | twilight and water |
| ⭐ **dark margin** | **`HorrorWastes`** · **`PoisonForest`** · `AB_PropaneLakes` | **dim and strange — light failing, not yet gone** |
| deep night | **`AB_RockyCrags`** | **glow 0.34, permanent. The Forsakens' heartland** |
| ⭐ **inside the dark** | **`Glowforest`** | ⭐ **oases of LIGHT** |

### ⭐ The symmetry, and it is the best thing in this ruling

> **On the dayside, an oasis is water in a desert of heat.**
> **On the nightside, a glowforest is light in a desert of dark.**

**Same shape, opposite substance** — and the player will feel the rhyme without
anyone explaining it. **Both are the thing you cross a hostile expanse to reach,
and both are worth fighting over.** ⭐ It also means the nightside has something to
*want*, not only something to survive, which is what stops a refuge from being a
punishment.

### Verdicts

| biome | verdict | placement |
|---|---|---|
| `HorrorWastes` | **rare** | the dark margin — between terminator and full crags |
| `Glowforest` | **rare** | ⭐ **inside the deep night**, as isolated points |
| `PoisonForest` | ⭐ **rare — HELD FOR JUDGEMENT** | dark terminator, provisionally |

⚠️ **`PoisonForest` carries an explicit "see it before ruling" flag.** The owner
wants to stand in it. **File it for the next live session** — it is a look, not a
test, and it costs one map.

✅ **All 26 surface biomes now carry a verdict.** The biome mix is ratified and
becomes `biomeConfigs[x].scoreOffset` values on the patched `TidallyLocked` def.

---

# ✅ THE BIOME MIX IS RATIFIED — owner, 2026-08-14

_"Otherwise I like your frequencies." **All 37 survivors accounted for. This is the
list `biomeConfigs[x].scoreOffset` implements.**_

| tier | biomes |
|---|---|
| ⭐ **ABUNDANT** | `ExtremeDesert` · `Desert` |
| **COMMON** | `ZBiome_Badlands` · `AridShrubland` · `Wasteland` · ⭐ `AB_RockyCrags` |
| **RARE** — 22 | `ZBiome_DesertOasis` · `AB_FeraliskInfestedJungle` · `AB_MiasmicMangrove` · `AB_MycoticJungle` · `COMIGO_GreaterSwamp_Tropical` · `AB_OcularForest` · `AB_TarPits` · `AB_PropaneLakes` · `AB_MechanoidIntrusion` · `AB_GallatrossGraveyard` · `AB_PyroclasticConflagration` · `Volcano` · `LavaField` · `Scarlands` · `IronScruff_PrimordialGeysers` · `RG_BoilingForest` · `BMT_CrystalCaverns` · `BMT_EarthenDepths` · `BMT_FungalForest` · `HorrorWastes` · `Glowforest` · `PoisonForest` |
| 🔴 **NOT by scoreOffset** | `Ocean` · `Lake` — `isBackgroundBiome`, assigned by the **elevation threshold.** The sea step owns these |
| **no verdict needed** | `Space` · `Orbit` · `Underground` · `Undercave` · `CQF_Undercave` · `AM_UndergroundSpace` · `VQEA_AncientComplex` — layer and pocket biomes, never surface tiles. ⚠️ **and the exact reason we blacklist rather than whitelist** |

**Two entries carry notes rather than plain frequencies:**

- ⭐ **`AB_RockyCrags` is COMMON, revised up from rare.** On a tidally locked
  planet the nightside is a hemisphere and the crags are what it looks like — **the
  temperature curve confines them to the dark side on its own**, so "common"
  produces a dark half rather than a scatter of dark tiles.
- ⚠️ **`PoisonForest` is rare and HELD FOR JUDGEMENT.** The owner wants to stand in
  it before ruling. **One look, next live session.**

⇒ **W3 is unblocked. BUILD owns the def work: one `PatchOperationAdd` on
`TidallyLocked` carrying the 29-entry blacklist and these offsets.**

---

## ⭐⭐ THE COLD IS THE MECHANIC — owner, 2026-08-14. And it is MEASURED.

> *"The night side should be REALLY cold, disturbingly so, and the poor Jawa just
> can't handle cold… unless they've invested in dramatic heater technology they'll
> have to move on rapidly. Though their factories make quite a lot of heat."*

### ✅ Confirmed from the def dump: no Jawa variant has ANY cold-tolerance gene

| variant | heat | ⭐ **cold** |
|---|---|---|
| `OuterRim_Jawa` | `MaxTemp_SmallIncrease` (+10) | 🔴 **none** |
| `guy762_xenotype_jawa` | `MaxTemp_LargeIncrease` (+20) | 🔴 **none** |
| `BTD_Jawa` | `MaxTemp_LargeIncrease` (+20) | 🔴 **none** |

**All three buy heat. None buys cold.** So on a nightside running **−37 °C at
latitude 1.0 and −80 °C at 2.0**, the clan sits at **baseline human cold
tolerance** — which is not survival, it is a countdown.

### ⭐ And the loop closes on itself, which is why this is the best mechanic yet

> **The clan's own industry is the only thing keeping it alive in the dark — and
> that industry is how it makes money.**

Smelters, forges and the salvage line **throw heat**. So the nightside refuge is
survivable **exactly as long as the factory runs**, and the factory runs on
feedstock hauled from the dayside.

⭐ **That closes the hiding loop without a single new system:**

- **hiding costs FUEL**, and fuel is the same resource as production
- **you can smelt or you can not freeze** — and early on, not both
- **the refuge has a running cost**, so it expires on its own with no timer
- ⭐ **and the thing that saves you is the thing you already built to get rich.**
  The clan does not need a survival mechanic bolted on; **its economy IS the
  survival mechanic**, pointed sideways.

### What this makes true, and it is a lot

- **The pursuit ruling holds** — extended, never terminated — and now the *cold*
  supplies the pressure that a stopped clock would have removed.
- ⭐ **"Dramatic heater technology" becomes a real progression tier**, and it is the
  first thing the clan would want that is not a weapon or a wall.
- **`AB_RockyCrags` grows plants at glow 0.34 — nothing.** So the nightside has no
  food either. **Cold, dark, hungry, and running on imported fuel.**
- ⚠️ **A Wildsteam pawn would be FINE out there** — Wookiees, Ewoks, Nelvaanians
  are all furred and cold-adapted. **The species that cannot use the dayside are
  the ones who could live in the dark**, which is a trade the player can actually
  make: recruit the wrong-for-here people to hold the place you hide in.

---

⭐ **The water cycle, the burning savanna and the terminator poison forest are specced in `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md`** (owner, 2026-08-15). It rules that rain falls ONLY on the unlandable peaks, that condensation on the shade side of the terminator is the planet's second and opposite water mechanism, that the seas are hypersaline and nutrient-overcharged (hence gigantism), and that freakish plant growth plus dry thunderstorms make the savanna a self-sustaining fire.

---

⭐ **The planet's HISTORY is in `design/Jawa/worldbuilding/the_forgotten_war.md`** (owner, 2026-08-15): the Forsakens' war, the Forgotten Arsenal as sand-buried self-replicating vault guardians, the three things inside a vault, the one and only mega-structure patch (sacred to the Free Droid Enclaves), and the ruling that **The Utinni is a Forsaken initiator vessel** that was present at the founding of this world.

---

🔴 **THE PLANET IS `Ash'karr` — "The Sundered". Owner, 2026-08-15.** The name is geography, history and elegy at once: the world split about its terminator, the world the Forsakens broke, and the people the war sundered. Full ruling in `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md`.
