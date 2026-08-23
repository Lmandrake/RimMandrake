# What our creatures can already DO — the strange-behaviour inventory

_DECIDE, 2026-08-22. Closes `STRANGE_ABILITIES_INVENTORY_1`._

**Owner:** *"Optionally it would be fun to make a list of the 'strange animal behaviors or
abilities' we have access to that we might want to propagate further than currently
implemented."*

Censused over the **967 wildlife-eligible creatures**, from the live def dump's comps and
ability grants. **Reported by what it DOES**, because `AA_Aaroxis` is not decidable and
*"burrows and ambushes from below"* is.

⚠️ **Read the counts as SCARCITY, not as importance.** The high-count comps
(`RunAndGun` 977, `SidearmMemory` 977, `MobRank` 979) are framework blankets applied to
every pawn by mods that patch all of them — they are noise. **Everything below is rare on
purpose, which is exactly why it is worth spreading.**

## A. Behaviours that would change how a place FEELS — the ones to spread

| what it does | comp | carriers | who has it now |
|---|---|---|---|
| ⭐ **Changes appearance to match the ground it stands on** | `CompProperties_GraphicByTerrain` | **3** | chameleon yak, pestigator, sand prowler |
| ⭐ **Lures prey in, then takes it** | `CompProperties_LurePrey` | **3** | mantrap, mucklurker catfish, smog moth |
| ⭐ **Lives on light instead of food** | `CompProperties_LightSustenance` | **5** | crystalline caracal, mantrap, needlechicken |
| **Glows** | `CompProperties_Glower` | 3 | glowtail, mucklurker catfish, smog moth |
| **Burrows when hungry** / **periodically** | `DigWhenHungry` / `DigPeriodically` | 9 / 4 | aiwha, bearwolf · catbear, molebear, toxafox |
| **Lies dormant, then wakes** | `CanBeDormant` + `WakeUpDormant` | 44 | bearded troll, bunker bug, cave spider |
| **Leaves a filth trail you can follow** | `MakeFilthTrail` | 8 | acid slug, chem snail, giant slug |
| **Prefers mountains** | `MountainPreference` | 3 | ironcasket beetle, rock troll, silver mole |
| **Floats** | `CompProperties_Floating` | 41 | Aurora sylph, Empress butterfly, Peko-peko |

🔑 **The top three are the prize.** Three creatures each, out of 967. A desert where *some*
things are the colour of the ground they are on, and *some* things sit still and wait, is a
different planet from one where everything simply walks at you.

## B. Defensive and reproductive strangeness

| what it does | comp | carriers |
|---|---|---|
| **Reacts when attacked** (quills, spray) | `DefensiveReaction` | 8 |
| **Vents gas when damaged** | `GasOnDamage` | 5 |
| **Produces gas continuously** | `GasProducer` | 3 |
| **Hunts / defends in packs** | `PackHunter` / `PackDefense` | 6 / 5 |
| **Regenerates** | `Regeneration` | 20 |
| **Highly flammable** | `HighlyFlammable` | 4 |
| **Reproduces asexually** | `AsexualReproduction` | 13 |
| **Metamorphoses at a fixed age** | `EvolveAtFixedAge` | 4 |
| **Spawns swarmlings** | `SpawnSwarmlings` | 3 |
| **Spawns things** (generic) | `Spawner` | 5 |
| **Cannot be tamed, ever** | `Untameable` | 7 |
| **Eats things nothing else eats** | `EatWeirdFood` / `CustomThingEater` | 13 / 5 |
| **Changes the mood of pawns near it** | `ThoughtEffecter` | 3 |

## C. Actual ABILITIES — 94 creatures carry `VEF.AnimalBehaviours.CompInitialAbility`

The framework is **Vanilla Expanded Framework's AnimalBehaviours**, and the grants are:

**Ranged attacks:** `AA_RedPoisonBolt` (4) · `AA_BlackHiveBolt` (2) · `AA_Bullet_Rock` (2,
*gallatross throws rocks*) · `AA_Quill` (3) · `VFEI2_InsectAcidSpew` · `VFEI2_LargeAcidSpew`
· `VFEI2_FlameSpew` · `VFEI2_ChemfuelSpew` / `ChemfuelSpit` · `DA_ToxicBarbspike`
**Control:** `AA_Web` (2) · `AA_FireWeb` (2) · `GR_PoisonBlast` (5) ·
`GR_PoisonBreathAnimated` (2, *thrumbolizard*)
**Movement:** `VFEI2_InsectGlide_Short/Medium/Far` · `DA_FrogLeap` · `GR_AdrenalineRush` (9)
**Terrain-changing:** ⭐ `VFEI2_CreateSmallBurrow` / `Medium` / `Large` and
`VFEI2_WideTunnels` — *the patriarch and the silverfish dig the map itself.*

## 🔴 What is portable and what is not

✅ **Every comp in sections A and B is XML.** Adding
`<li Class="AnimalBehaviours.CompProperties_GraphicByTerrain">` to another creature is a
patch, not code — **the behaviour travels.**
⚠️ **But its MOD must be active**, because the C# lives there: `AnimalBehaviours` ships in
Vanilla Expanded Framework, `VFEI2_*` in Vanilla Factions Expanded — Insectoids 2, `GR_*` in
Vanilla Genetics Expanded, `AA_*` in Alpha Animals. A `MayRequire` is mandatory or the def is
discarded at load.
🔴 **`CompProperties_PlastemmothInstinct` (4) is NOT portable** — a bespoke comp named after
one creature. Assume anything named after a species is welded to it.

## Recommended, if this is ever picked up
1. **`GraphicByTerrain` on the desert cast.** Three carriers is a waste of the single best
   idea in the list, and camouflage is what desert fauna *does*.
2. **`LurePrey` + `LightSustenance` on the cave and jungle casts.** Both already co-occur on
   `mantrap`, which is the proof they compose.
3. **`CanBeDormant` on the HorrorWastes cast.** Bioweapon ground that is quiet until it is
   not is better than bioweapon ground that charges you.
⛔ **Do not spread `Untameable`, `HighlyFlammable` or `ThoughtEffecter` casually** — those
change the player's relationship with an animal rather than its behaviour.
