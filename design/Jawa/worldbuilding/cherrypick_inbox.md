# Cherry Picker inbox — everything ruled OFF so far

_VISION, 2026-08-13. **Explicit defNames and source mods for every "turn it off"
verdict this session.** Owner's rulings unless marked as a recommendation._

---

## 🔴 Read this first — Cherry Picker's granularity decides what works

**Measured from `CherryPicker.dll` (ws `3521312241`), 1.6 build, decompiled:**

- **Removing a `PawnKindDef`** sets `combatPower = float.MaxValue`,
  `allowInMechClusters = false`, `canArriveManhunter = false`,
  `canBeSapper = false`, and strips the kind from every
  `CompProperties_SpawnerPawn`. ⭐ **This is what stops a creature spawning** —
  raids, ancient dangers, clusters and spawner buildings alike.
- **Removing a `ThingDef`** only zeroes market value, sets `tradeability: None`
  and clears categories. **It does NOT stop the creature spawning.**

⇒ 🔴 **For every creature below, the target is its `PawnKindDef`, not its race
`ThingDef`.** The race defNames are given because they are what the design
documents name; **CREATE must resolve each to its PawnKindDef(s) before
picking.** Several entities have more than one kind.

---

## A. Anomaly — `ludeon.rimworld.anomaly` (DLC stays ENABLED)

⚠️ **The DLC must remain enabled.** The owner's ruling is *storyline at zero,
creatures and abilities still ours to reskin* — the defs have to stay reachable.
**Anomaly content level is a playstyle/difficulty setting, not a cherry-pick.**

**OFF — creatures:**

| race defName | label | note |
|---|---|---|
| `Metalhorror` | metalhorror | has larva / juvenile / mature stages — check for multiple kinds |
| `Shambler` | shambler | ⚠️ **many kinds** — `ShamblerSwarm`, `ShamblerAssault`, deadlife-raised. Also check `DeathPall` and deadlife dust still reference it |
| `Ghoul` | ghoul | player-creatable via surgery — the **recipe** must go too, not just the kind |
| `Trispike` | trispike | ⚠️ **see the dependency warning below** |

**OFF — objects and items:**

| defName | label | type |
|---|---|---|
| `GoldenCube` | golden cube | ThingDef · its `baseChance` is already 0 |
| `WarpedObelisk_Duplicator` | corrupted obelisk | building |
| `WarpedObelisk_Abductor` | warped obelisk | building ⚠️ **this is the ONLY route into the Labyrinth pocket map** — removing it orphans `LayoutRoomDef LabyrinthObelisk`. Intended |
| `RevenantSpine` | revenant spine | item |
| `VoidNode` | void node | **disabled, artwork RETAINED** — do not delete the texture |

🔴 **DEPENDENCY WARNING, and it is a real one.**
**`Bulbfreak` is KEPT (renamed Genebulb) and its whole gimmick is bursting into a
horde of smaller fleshbeasts on death. `Trispike` is being REMOVED and splits into
fingerspikes.** Establish what Bulbfreak actually spawns before picking Trispike —
if it spawns trispikes, removing them breaks it; if it spawns **fingerspikes**,
note that fingerspike is being **repurposed as a tame pet (Scurrier)**, so a
Genebulb would burst into a shower of pets. **Neither outcome is intended.**

---

## B. Mods recommended OFF — `ModsConfig.xml`, not cherry-pick

| packageId | name | why | status |
|---|---|---|---|
| `Samael.NPCMechsAndAnimals` | Mechs and Animals for NPC Factions | patches `Mech_Militor/Pikeman/Scyther/Mechanitor` into **Empire, OutlanderFactionBase, OutlanderRoughPig, Pirate, PirateWaster, PirateYttakin, TradersGuild** pawn groups. **It is the one mod actually putting mechanoids in ordinary raids**, and unticking the Mechanoid faction does **not** suppress it | ⚠️ **VISION recommendation, not an owner ruling** |

**Keep ON, explicitly:** `matathias.ruthlessmechanoids` — despite the name it is
**Ruthless Faction Pursuit**, the gravship pursuer redirect. Owner re-enabled it.

---

## C. Not yet actionable — waiting on the owner

| item | what is pending |
|---|---|
| **Mechanoids** | The owner will cherry-pick per mech. **80 mechs are laid out for review with art** — `design/Jawa/worldbuilding/review/mech_register.html`. **No per-mech verdicts exist yet.** Do not pick any mech until they land |
| 🔴 **Star Wars xenotypes** | **Three overlapping mods are loaded** — `[BTD] Xenotype REMIX: Star Wars` (70), `Star Wars Xenotypes` guy762 (58), `Outer Rim – Galactic Diversity` (44). **80 species across 172 defs**, so Jawa exists three times with different heat genes and generation will roll all three. **This is the largest cherry-pick job in the project** and it needs a canon-per-species ruling first. Register: `review/species_register.html` |
| **Biomes** | Review sheet being built now; verdicts are off / rare / common / abundant |
| **Non-SW xenotypes** | ~170 of them — giants, trolls, demons, phytokin, Yautja, plus **1,073 auto-generated `HL_*` animal-people** from `redmattis.sapientanimals`. ⚠️ The `HL_*` set never spawns in pawn generation, so it is **noise, not a threat** — pick only if it pollutes something measurable |

---

## D. Already handled elsewhere — do NOT cherry-pick these

- **21 fiction-breaking factions** — handled at the Configure Factions screen
  during worldgen, ratified in `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`.
- **`OuterRim_RebelAlliance`** — already suppressed by our own
  `RebelAlliance_Suppress.xml`. Cherry-picking it as well would be redundant.
- **Mechanoids out of the RAID roster** — that is a `pawnGroupMakers` patch on
  `FactionDef[Mechanoid]`, **not** a cherry-pick. Ancient dangers read a
  different mechanism entirely and must keep their guards
  (`what_the_machines_are.md`).

---

## ✅ RESOLVED — the Genebulb / Trispike dependency. Remove Trispike.

_CREATE, 2026-08-13, read from `Data/Anomaly/Defs/ThingDefs_Races/Races_Fleshbeasts.xml:63-70`
and confirmed against the live dump._

**Bulbfreak's `race.deathAction` is `DeathActionProperties_Divide`, count 4,
options `{Toughspike, Trispike}`. Never Fingerspike.** So:

- **Removing Trispike degrades Genebulb, it does not break it.** The pick list
  drops to one entry and a Genebulb bursts into **4 Genespikes**.
- ⭐ **That is a flavour GAIN, not a loss.** A gene-cult's failed batch bursting
  into four of *the same experiment* reads better than a mixed horde — **one
  gene-line, one mistake, four copies.** The Helix owns both names.
- ⭐ **And removing Trispike CLOSES the pet leak rather than opening it.**
  Trispike is itself a Divide, count 3, spawning **Fingerspike** — so keeping it
  is what would produce a shower of tame Scurriers two hops down. **Remove it.**

### ⚠️ Three follow-ons, all from the same finding

1. **`Dreadmeld` (kept as Genemeld) carries a FORCED list** —
   `dividePawnKindAdditionalForced` = Toughspike, **Trispike**, Bulbfreak. Forced,
   not weighted. 🔴 **Do not rely on graceful degradation: strike Trispike from
   that list explicitly** when it is culled.
2. 🔴 **Two GENES spawn fingerspikes from a living pawn**, and they reopen the pet
   leak from a different direction: `AG_MeatBurst` (Alpha Genes) forces **3 ×
   Fingerspike**, and `Turn_Gene_FleshbeastBurster` (Integrated Genes) weights
   Fingerspike 5 / Trispike 2.5 / Toughspike 0.5. **A pawn bursting into three
   tame Scurriers is nonsense.** ⇒ **Cull both genes** unless something in the
   roster is found to need them.
3. ⚠️ **`FleshmassHeart` picks its defender kinds in C#, not in any def** — so
   **what the adult Sarlacc spawns cannot be established offline.** It is the
   centrepiece of the sarlacc line and the one part of it nobody can read.
   **Live check, next session.**

---

## E. BIOMES — owner's verdicts, 2026-08-14. **29 REMOVE, 4 explicit KEEP.**

**Every defName resolved against the live def dump. Source mod given because
several removals are duplicates of each other under different names.**

### REMOVE

| defName | label | mod |
|---|---|---|
| `ZBiome_CoastalDunes` | coastal dunes | More Vanilla Biomes |
| `ZBiome_Sandbar_NoBeach` | sandbar | More Vanilla Biomes |
| `ZBiome_Iceberg_NoBeach` | ice floes | More Vanilla Biomes |
| `SeaIce` | sea ice | **Core** |
| `ZBiome_Marsh` | marsh | More Vanilla Biomes |
| `TropicalRainforest` | tropical rainforest | **Core** |
| `ColdBog` | cold bog | **Core** |
| `COMIGO_GreaterSwamp_Cold` | greater cold bog | Comigo's Greater Swamps |
| `COMIGO_GreaterSwamp_Temperate` | greater temperate swamp | Comigo's Greater Swamps |
| `TemperateSwamp` | temperate swamp | **Core** |
| `TropicalSwamp` | tropical swamp | **Core** |
| `Wetland` | wetland | Advanced Biomes (Continued) |
| `Labyrinth` | labyrinth | **Anomaly** |
| `MetalHell` | metal hell | **Anomaly** |
| `Savanna` | savanna | Advanced Biomes (Continued) |
| `ZBiome_Grasslands` | ⚠️ **stormy savanna** | More Vanilla Biomes |
| `Grasslands` | ⚠️ **grassland** | **Odyssey** |
| `AB_GelatinousSuperorganism` | gelatinous superorganism | Alpha Biomes |
| `AB_IdyllicMeadows` | idyllic meadows | Alpha Biomes |
| `TemperateForest` | temperate forest | **Core** |
| `GlacialPlain` | glacial plain | **Odyssey** |
| `AG_NereidPocketPlane` | nereid pocket plane | Alpha Genes |
| `AG_PocketPlane` | pocket plane | Alpha Genes |
| `ZBiome_AlpineMeadow` | alpine meadow | More Vanilla Biomes |
| `BorealForest` | boreal forest | **Core** |
| `ZBiome_CloudForest` | cloud forest | More Vanilla Biomes |
| `ZBiome_GlacialShield` | glacial shield | More Vanilla Biomes |
| `IceSheet` | ice sheet | **Core** |
| `Tundra` | tundra | **Core** |

⚠️ **"Stormy savanna" and "grassland" are two different defs in two different
mods** — `ZBiome_Grasslands` is *labelled* "stormy savanna" and Odyssey's
`Grasslands` is *labelled* "grassland". **Both are on the list; do not resolve
either by label.**

### KEEP — explicit, with placement

| defName | label | why it survives |
|---|---|---|
| `RG_BoilingForest` | boiling forest | **Hold until we can explore it.** Not endorsed, not cut |
| `AB_TarPits` | tar pits | **Hold until explored** — and it is the donor for the tar-pit augmentation |
| `AB_PropaneLakes` | propane lakes | ⭐ **Place along the terminator, before it turns fully into forsaken crags.** A chemical margin between twilight and permanent night |
| `AB_MechanoidIntrusion` | mechanoid intrusion | ⭐ **The Forgotten Arsenal's home.** The owner named it — this is where the Forsakens' automata are |

### Three consequences worth stating

1. ⭐ **Every surviving jungle and marsh is ALIEN.** Vanilla's rainforest and all
   three vanilla swamps are gone, so what the Wildsteam Clan lives in is
   `AB_FeraliskInfestedJungle`, `AB_MycoticJungle` and `AB_MiasmicMangrove`.
   **The wet places are not Earth-like — they are wrong, and that is now
   structural rather than decorative.**
2. ⚠️ **`COMIGO_GreaterSwamp_Tropical` was NOT named and survives.** Cold and
   temperate were cut; tropical was not. **Assuming that is deliberate** — it is
   the one conventional marsh left, and it fits the river country. **Flagging so
   it is a decision rather than an oversight.**
3. ⚠️ **`SeaIce` is being removed, and it was our worked example.** It is
   vanilla's proof that a **water-covered tile can be settleable and
   map-generating** — the template for anything that goes on or under water.
   **Removing the biome is fine; do not lose the knowledge.** It is recorded in
   `hiding_the_gravship.md`.

---

## 🔴 CORRECTION OF THE RECORD — the Anomaly picks were NEVER withdrawn by the owner

_2026-08-14. **A withdrawal was relayed to me and to CREATE as an owner ruling. It
was not one.** The owner's actual position, in their words:_

> **"I did NOT agree to that anomaly ruling! I want to use some of those
> creatures… please leave them in with Anomaly set to zero but enabled, so we can
> still spawn them. And add my cherrypicks! Do not revert them!"**

**⇒ Both halves stand, and they were never in conflict:**

| | |
|---|---|
| **Anomaly** | **`Disabled` playstyle — content at zero — but the DLC stays ENABLED**, so every creature and ability remains spawnable and reskinnable |
| **The cherry-picks** | ⭐ **stand as given. Add them. Do not revert them.** |

### ⭐ Why there was never a conflict, which is the part that got lost

**The objection raised was that deleting defs destroys the reskin donor library.
True in general — and irrelevant here, because the two sets are DISJOINT.**

- **The donor library is what the owner KEPT:** sandscreamers, noctols, the
  revenant, the twisted obelisk, the kybersphere, the sarlacc line, the Helix's
  three, the scurrier.
- **The cherry-picks are what the owner REJECTED:** metalhorror, shamblers,
  ghouls, the golden cube, the corrupted and warped obelisks, the revenant spine,
  trispike.

🔴 **"Do not delete the donors" was generalised into "do not delete anything."**
Those are different instructions and only the first was ever true.

### The list, unchanged and standing

`Metalhorror` · `Shambler` · `Ghoul` · `Trispike` · `GoldenCube` ·
`WarpedObelisk_Duplicator` · `WarpedObelisk_Abductor` · `RevenantSpine` ·
`VoidNode`

⚠️ **One genuine nuance, and it is the only caveat I would keep:** the owner ruled
`VoidNode` *"disabled but keep the artwork, perhaps as a power-holding ore."*
**The texture file stays on disk regardless of what happens to the def** — a new
ore def can point at the same `texPath`. **So picking it is safe, but record the
texture path before you do**, because the whole point of keeping it is to reuse it.

✅ **Trispike is confirmed correct to remove** — CREATE established Bulbfreak
divides into `{Toughspike, Trispike}` and Trispike divides into `Fingerspike`, so
**removing Trispike closes the tame-pet leak rather than opening it.**


---

## 📸 EVIDENCE — `ZBiome_CoastalDunes`, confirmed by sight, 2026-08-14

**Already on the removal list** — the owner named it first of the 29. **This is the
picture of why**, taken on a live quicktest map:

`design/Jawa/worldbuilding/evidence/2026-08-14_coastal_dunes_is_not_a_desert.jpg`

**What the tile shows:** water on **two** edges of one map · marsh · palms and
broadleaf trees · grass, flowers and mushrooms · and the status line reading
🔴 **fertility 100%**. Clear, 26 °C, "Permanent summer".

⭐ **"Coastal dunes" is a wet, fertile, wooded biome with a sand texture.** On a
thirst world it is not a desert with a beach — **it is a garden that has been
labelled a dune.** The name is the only arid thing about it.

⇒ **Confirms the cut.** ⚠️ **Route note:** this now goes in the
**`biomeBlacklist`** on the patched `TidallyLocked` def rather than through Cherry
Picker — same outcome, and it leaves the def alive so nothing that references it
dangles. **No change to the verdict, only to the lever.**

📌 **And it is a reminder worth keeping: the 29 removals were judged from def
fields and labels. This is the first one anyone has LOOKED at, and looking
confirmed it in about two seconds.** Where a cheap look is available, take it —
`PoisonForest` is already filed for exactly that treatment.

🔴 **Sharpened 2026-08-14 by BRIDGE, and it is worse than "un-looked-at": the
fields were never readable in the first place.** `Scalars()`, the reflective
reader behind `jawa/get_defs`, walks **public instance FIELDS only**. On
`BiomeDef`, `wildAnimals`, `coastalWildAnimals`, `pollutionWildAnimals`,
`diseases` and `allowedPackAnimals` are **private**, and `AllWildAnimals` /
`AllWildPlants` are **properties** — neither form is visible to it. ⇒ **The other
28 are not wrong; they are UNEVIDENCED, which is a different verdict.** Do not
cite "the def says" for any of them until `jawa/biome_probe` has run (built, not
yet deployed, and not yet called).

📌 **Generalises past biomes — same shape as `strings -a` vs `strings -a -el`:
before trusting a conclusion drawn "from the def", check the instrument can SEE
the field. An absent reading and an unreadable one are not the same answer.**
