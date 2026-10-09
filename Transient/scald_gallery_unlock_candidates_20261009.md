# What the Scald's Return Gallery should hand you: five candidates

2026-10-09, FOUNDRY. Answers the owner's typed reply on the schematic card: *"Need a different tech to find. This makes no sense."* Item: `SCALD_GALLERY_SCHEMATIC_UNLOCK_1`. Nothing here is built.

## Where things stand

On the Scald's sea floor (reached only by flying the ship down), a broken coolant manifold from the Rust Cathedral lies half-buried. Colonists hook a gauge to each of its five branch outlets, read the pressure and flow, and mark the one branch that still carries warm water back. Getting it right opens a service locker. Getting it wrong jams the latch for a day. This is built (`src/RimMandrake/DivingInteraction/Source/RM_ReturnGallery.cs`). It is not yet proven in play.

The locker holds two items. One is a **heat log**, which is lore: it says the Cathedral dumps its waste heat into the Scald. The other is an **"immersion-engineering schematic"** that does nothing (`src/RimMandrake/DivingInteraction/Defs/ThingDefs_Items/RM_ReturnGalleryRewards.xml`). The card offered three cooling-themed answers: a cheaper way to keep a parked ship cool, a new hull cooler, or a keepsake. He rejected all three.

So each candidate below is a **different technology**, and each one reaches the player **a different way**. They also lean on what the project has already built. Five things already exist that a reward could plug into:

- **The Cathedral pass** (`src/RimUtinni/CathedralPass/`) is a flag on one colonist that makes the Cathedral's sentinel machines treat them as non-hostile, on Cathedral ground only. It is built. *What earns the pass* was left unbuilt on purpose.
- **The Cathedral's mood** (`src/RimMandrake/RustCathedral/Source/Hum/`) is a score per map that rises and falls (the "hum"), with a WARY / TOLERATED / VOUCHED ladder. It is built.
- **FlowWorks pumping stations** come in wrecked, kludged and repaired states, and lift liquid from up to four cells away (`src/RimMandrake/FlowWorks/Defs/Machinery/RM_PumpingStation.xml`). They are built.
- **The dark tower** in the Scald's crater lake (Rakatan high command) has a control console meant as the hook into the Cathedral. It is built as a structure.
- **Smart metal** is the Cathedral's lost self-assembling metal. Its nature is ruled ("mechanics owed"). Nothing in play uses it yet. The base game already has a slow self-repair part that buildings can carry (`CompSelfhealHitpoints`, confirmed in the decompiled 1.6 source).

None of the five touches heat, so the "one kind of heat" ruling has nothing to say about any of them. None gives a colonist a way to dive or climb out alone, so all five keep the rule that the ship is the only way down and back.

---

## 1. The maintenance crew's badge (the reward is access)

**What the player gets:** the locker holds a coolant-crew service token. A colonist who carries it to the Rust Cathedral is let through: the sentinels track them, pause, and look away. It works on Cathedral ground only. You solved the Cathedral's own plumbing, so its machines read you as crew.

- **Buys:** the puzzle's lesson (you understood this machine) becomes the reward (the machine accepts you). It opens a very different way to play the most dangerous biome: walk in, don't fight in. It has a clear payoff that a player can feel.
- **Costs:** it skips part of the Cathedral's planned trust ladder, where the pass was meant to come only at VOUCHED. Possible softening: the token counts as one step toward VOUCHED rather than the whole pass, or it only works while the hum is calm. The reward also happens far from the Scald, so it pays off only for players who go to the Cathedral.
- **How they get it:** found in the world (the locker), used by carrying it.
- **Build:** small. The pass, the hostility rule and a grant call all exist. New work is one item that grants the pass when used, plus a rule for when it is lost.

## 2. A scrap of living metal (the reward is a research path)

**What the player gets:** the locker holds a sealed sample of the Cathedral's smart metal, still trying to put itself back together. Studying it at a research bench opens a project for **self-mending plating**: a wall and hull plate that slowly repairs its own damage. It is expensive, and it is the first thing the player can build from the Cathedral's lost technology.

- **Buys:** it is the most "found a technology" of the five. It is a real new building, it is useful on the ship and the base alike, and it gives the ruled smart metal its first mechanic.
- **Costs:** smart metal is a major story element. The owner may want its first mechanic to come from the Cathedral itself rather than a side puzzle on another biome's sea floor. Plating that repairs itself also needs a careful price so it doesn't make walls worry-free.
- **How they get it:** found item, then research.
- **Build:** medium. The base game's self-repair part does the mending. New work is a research project, one wall and one plate definition, art, and a "study this item to unlock research" step (the Scarlands' wall-panel transcription already does something similar).

## 3. The Cathedral's circulation pump (the reward is a better machine you already know)

**What the player gets:** the schematic is how the Cathedral moved coolant across kilometres. Reading it unlocks a **high-pressure circulation pump** in FlowWorks. It is the next step after the repaired pumping station: much longer reach, and it can push liquid uphill or along a long canal run instead of only lifting from four cells away.

- **Buys:** it matches the puzzle exactly (trace a circulation system, learn circulation). It uses the existing pump ladder, so players already understand it. It is useful in every biome that has liquids, not just the Scald. Nothing about it is cooling.
- **Costs:** it is the least surprising of the five. It reads as an upgrade more than a discovery. Its value depends on how much the player already uses FlowWorks.
- **How they get it:** found item, read it to unlock (like a techprint).
- **Build:** small to medium. The pumping station and its states exist. New work is one research gate, one new pump definition with a longer reach, and art.

## 4. Where the heat goes (the reward is a place, then a quest)

**What the player gets:** the schematic and the heat log together turn out to be a route map. Solving the gallery offers a **quest**: the Cathedral's heat-dump outflow leads to a sealed pump-house on the planet, or to the water gate of the dark tower in the crater lake. The technology waits there, behind defences.

- **Buys:** the gallery becomes the first step of a story rather than a vending machine. It ties the Scald, the Cathedral and the dark tower together, all of which the lore already links. The thing found at the end can be any of candidates 1 to 3, picked later.
- **Costs:** this is the biggest build here, and it postpones the actual "what tech" question instead of answering it. A quest also has more ways to fail silently than an item does.
- **How they get it:** quest reward.
- **Build:** medium to large. The dark tower structure and its console exist. New work is the quest (offer, site, payout), the site's map, and whatever the final reward is.

## 5. Only the Jawas can read it (the reward is a trade)

**What the player gets:** the schematic is written in the Cathedral's engineering code, and no colonist can read it. Jawa salvage traders can. They will swap it for **one technology of the player's choosing** from a short list they carry, or buy it for a high price.

- **Buys:** the player chooses, so the reward is never useless. It fits the trading-clan setting and the salvage crew trade already ruled tonight. It needs no new building at all.
- **Costs:** the technology is not really *found* in the gallery. It is bought with something found there, which weakens the "discover it here" idea the gallery was invented for. Its value depends on whether a trader is around.
- **How they get it:** trade.
- **Build:** small. The item exists. New work is a trade rule that accepts it, and a list of offerable research.

*(A sixth shape was considered and left out: a ritual to the forge god to "awaken" the schematic. The Scald's one rite is already ruled as the pilgrims' bathing rite, and a second rite for the same biome would compete with it.)*

---

## Side by side

| | What you get | How it arrives | Build size | Main risk |
|---|---|---|---|---|
| 1. Crew badge | Cathedral sentinels let one colonist pass | found, carried | small | skips the Cathedral trust ladder |
| 2. Living metal | self-mending plating | found, studied | medium | spends a major story element on a side puzzle |
| 3. Circulation pump | long-reach FlowWorks pump | found, read | small–medium | feels like an upgrade, not a discovery |
| 4. Where the heat goes | a quest to a sealed site | quest | medium–large | defers the real choice; biggest build |
| 5. Jawa readers | pick a technology by trade | trade | small | the tech isn't really found here |

## Recommendation

**Candidate 3, the circulation pump.** It is the only option where the thing you learn is the thing the puzzle taught you (how the Cathedral moves water), and it is mostly built already. **If he wants it to feel like a bigger discovery,** take 1 (the crew badge) instead, gated on a calm hum so it does not replace the Cathedral's trust ladder.
