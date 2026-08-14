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
