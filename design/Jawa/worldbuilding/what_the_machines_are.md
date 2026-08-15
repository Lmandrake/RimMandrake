# What the machines are

_VISION, 2026-08-13. **The owner asked the right question at the right moment:**
if we keep some mechanoids, what are they *in fiction* — a fourth invading
faction, an orbital exterminator, a dead civilisation's automatic defences, or
just more Empire?_

**Recommendation: the third. And the engine already agrees with it.**

---

## The four options, judged

### ❌ "Just more Empire — rename them Imperial Droids"

**Cheapest, and it contradicts the Empire we have already written.**

The Directorate's doctrine (`faction_roster_v2.md:603`) is that *"only one ordered
hierarchy — human, centralised, obedient — holds the chaos back. Every alien
species, every deviation, every act of independent thought is disorder to be
corrected."* **A human-supremacist state does not hand its wars to machines.**

It also reverses a settled ruling. The owner deleted the Imperial Droid Army on
2026-08-13 precisely because a machine antagonist sat badly with the campaign
(`gravship_pursuer_mechanism.md`). **Reviving it under a new label restores the
contradiction the deletion removed** — and it blurs the Empire's silhouette,
which is currently clean: stormtroopers, combat droids on leashes, and the rare
Sith.

### ❌ A thirteenth faction — the Techno Union, the Commerce Guild, whoever

**This is the bloat I am supposed to catch.** The roster already holds twelve
factions, of which **four are already about machines**: Free Droid Enclaves
(emancipated droids), Geonosian Foundry Hive (droid *manufacturer*), the
Separatist droid army, and KotOR's rogue droid collective. **A fifth machine
faction adds no register the player cannot already meet.**

The canon lineages are still worth having — but as **visual variety inside
factions that exist**, not as new polities.

### ❌ A vast ship in orbit exterminating everyone

**The "threat from above" slot is taken, and it is the campaign's spine.** The
Empire pursues from orbit; the sky ladder is how they reach the ground; going up
is how you get noticed. **Two separate orbital menaces halve the weight of each.**

### ⭐✅ This was their world. The defences still run.

> **The desert was somebody's holding before it was a desert. They are gone. The
> automated defence grid is not, and it is still deciding who is allowed to move.**

---

## Why this one is right — five reasons, and the second is decisive

**1. It explains the mechanoids' actual behaviour.** In RimWorld mechs sit
dormant in sealed complexes, hold no settlements, have no diplomacy and wake when
disturbed. **That is not an army. That is an automated defence grid**, and the
fiction has been available in the engine's own behaviour the whole time.

⭐ **2. It requires NO new faction, because ancient dangers are a different
mechanism from raids — measured today.** Ancient dangers and sealed complexes are
populated by a predicate over pawn kinds (`allowInMechClusters`, `isFighter`,
`combatPower`), **never by `pawnGroupMakers`**. 21 of 93 mech kinds already sit in
exactly that state: eligible for a sealed complex, present in **zero** raid
groups. **So we can empty the Mechanoid raid roster entirely and the ruins keep
their guards.** The fiction and the engine want the same thing.

⭐ **3. "Triggered by the player flying their ship about" is the best part of the
owner's version, and it should be built.** Movement is currently free. If flying
wakes things — a dormant grid noticing a gravship crossing a sector — then
**every hop costs a moment of hesitation**, which is exactly what a campaign built
on a ship needs and does not have.

**4. It gives the desert a history in one sentence.** Why is the world full of
wrecks, buried complexes and salvage? **Because it was inhabited by someone with
better technology than anyone alive.** That single fact justifies the Jawa
premise, the scavenging economy, the ancient dangers and the ruins — all of which
the campaign already contains and none of which it currently explains.

**5. It does not compete with the Empire — it is a different KIND of thing.** The
Empire is a *who*: it negotiates, escalates, pursues, and can be hurt. The grid is
a *what*: it does not want anything and cannot be bargained with. **Two
antagonists in different registers are worth more than two armies**, and this is
the "qualitative not quantitative" discipline the design already claims.

## The consequence for the mechs themselves

**They stop being a faction and become a hazard.** Concretely:

- **Out of the raid roster.** No mech raids arrive at the colony as an army.
- **Kept in ancient dangers, sealed complexes and clusters** — which is where the
  player meets them, on the player's initiative, by opening something.
- **Kept as wreckage.** Map decoration is a separate def type entirely
  (`AncientWarwalkerTorso`, `ChunkMechanoidSlag` and kin) — **dead war machines
  can litter the world with no live mech anywhere near them**, which is pure
  atmosphere at zero threat cost.
- **The Mechanoid faction gets a name that says what it is** — *the automata*,
  *the standing garrison*, *the caretakers*. Label-only, one operation.

## 🔴 The open question: whose world was it?

The owner asked for a canon match and **there are two good ones, with a real
trade-off:**

| | **Rakata / the Infinite Empire** | **Techno Union** |
|---|---|---|
| canon standing | ⚠️ **Legends, not Disney canon** — but the KotOR mods we already run are built on it | ✅ **Disney canon**, Clone Wars era |
| fits "dead precursor"? | ⭐ **Perfectly.** A galaxy-spanning precursor empire whose ruins and automated systems outlive it is what they are *for* | ✖️ Poorly. The Techno Union is a corporation with a factory, not a vanished civilisation |
| already in our roster? | ⭐ **Yes** — Rakata appear in the Ascendant Helix and the Geonosian Hive, and as Imperial "relic-recovery specialists" | no |
| what the ruins then are | a precursor holding, its garrison still standing to orders nobody remembers | an abandoned production world |

**My recommendation: Rakata**, and the reason is that the roster already contains
them in exactly the right role — *relic recovery* is already a thing the Empire
does here. **The ruins gain an owner without a single new noun.**

⚠️ **But the owner has said canon must hold, and Rakata are Legends.** That is
their call, not mine. **If Disney-canon-only is the rule, the Techno Union
abandoned-factory-world reading works** and costs only the elegance of the
precursor idea.

⭐ **A third route if neither satisfies: leave them unattributed.** *Nobody knows
who built the compounds.* The Jawas certainly do not, and a clan of scavengers
finding a door they cannot explain is a better scene than one where a codex entry
tells them. **The unattributed version is the only one that cannot be
contradicted by canon**, and it is the one I would ship if the choice were mine
alone.

---

# ⭐⭐ THE ANSWER WAS ALREADY IN THE STACK — the Forsakens

_2026-08-13, from a full read of Alpha Biomes' `AB_RockyCrags`._

**The dark biome ships its own dead precursor civilisation, and nobody had
noticed.** Its own description, verbatim:

> *"This desertic landscape appears to be perpetually covered in an unnatural fog
> that seeps all light from the sun. **In the ancient past it was partly
> terraformed by a mysterious humanoid alien race simply known as Forsakens.**"*

## Why this settles the open question

**Whose world was it? The Forsakens'.** And they are better than either canon
option:

| | Rakata | Techno Union | ⭐ **the Forsakens** |
|---|---|---|---|
| canon risk | ⚠️ Legends, not Disney | ✅ canon | ⭐ **none — they are not Star Wars at all, so they cannot contradict it** |
| dead precursor? | yes | no, a corporation | ⭐ **yes, by definition** |
| already in the stack? | as a *race* only | no | ⭐ **as a biome, a rock type, a terrain set, a weather system and a fauna roster** |
| explains the darkness? | no | no | ⭐ **yes — the dark IS their failed terraforming** |

⭐ **One noun now carries the entire back-story**: the world was terraformed by
somebody, they failed, they left, the light never came back, and **their
automatic defences are still standing.** The mechanoids are the Forsakens'
garrison. The ancient dangers are Forsaken compounds. The salvage economy is
Forsaken debris. **The Jawas are picking over a dead civilisation's estate**,
which is the most Jawa sentence this design has produced.

**And it costs nothing.** The name already exists in a def a player can read
in-game. We are not inventing lore, we are *noticing* it.

⚠️ **The Jawas still do not know who the Forsakens were.** Keep the player-facing
ignorance from the earlier ruling — a clan finding a door they cannot explain is
the better scene. The name exists in the world; the explanation does not.

## What follows mechanically

- **Rename the Mechanoid faction to the Forsakens' garrison** — one label
  operation, and it now *means* something.
- **"Secret Compound" becomes "Forsaken compound"**, answering the owner's
  naming instinct with a word the game already uses.
- **The dark biome is their heartland**, not a random hazard tile.

---

⭐ **The planet's HISTORY is in `design/Jawa/worldbuilding/the_forgotten_war.md`** (owner, 2026-08-15): the Forsakens' war, the Forgotten Arsenal as sand-buried self-replicating vault guardians, the three things inside a vault, the one and only mega-structure patch (sacred to the Free Droid Enclaves), and the ruling that **The Utinni is a Forsaken initiator vessel** that was present at the founding of this world.
