<!-- status: live -->
# GOAL SHEET — everything that has to be true before we can play

**One line per thing the game is made of.** If every box below could be ticked honestly,
you could start the campaign and it would hold together. That is the only test this file
applies. It is not a plan, a queue or a schedule — it is the inventory.

🔑 **Why it is worth being strict.** Players receive a savegame with a fixed world. Nothing
in it regenerates on their machine. **Anything absent when you freeze is absent from every
player's game forever**, with no roll-again behind it.

**Legend**

| mark | meaning |
|---|---|
| 🔒 | **baked at world creation.** Getting it wrong means building a new world, not editing this one. Freeze these FIRST. |
| 🎨 | needs a human to *look* at it. A passing number is not a tick. |
| ⚙️ | settled by measurement or a def; an instrument can tick it. |

**How to tick a box honestly:** you have seen the thing itself — the def, the render, the
pawn on the ground — not a document asserting it. A doc is evidence of a decision, never
evidence of a state.

---

## 1. 🔒 THE PLANET

- [ ] **Geometry** — the tile grid, and it is the one we ship
  - [ ] 🔒 planet coverage / tile count is final and named
  - [ ] 🔒 the shipping **savegame is identified by filename** and backed up
  - [ ] ⚙️ the authored bundle and the shipping save agree tile-for-tile
- [ ] **Surface**
  - [ ] ⚙️ elevation — every tile has one, and nothing floats or sinks wrongly
  - [ ] ⚙️ biome on every tile; no tile left on a default
  - [ ] 🎨 hydrology — seas, lakes, rivers; rivers start somewhere and reach somewhere
  - [ ] ⚙️ temperature and rainfall bands per tile
  - [ ] ⚙️ hilliness / terrain roughness
  - [ ] ⚙️ roads, and where they connect
- [ ] **Dressing**
  - [ ] tile **mutators** placed (or deliberately none)
  - [ ] **landmarks** placed and named
  - [ ] **named regions / gazetteer** — every place the fiction mentions exists on the map
  - [ ] 🎨 the map reads as a real planet at a glance
- [ ] **Climate & sky**
  - [ ] weather roster per biome — what can fall, and how often
  - [ ] game conditions — storms, eclipses, flares, anything setting-specific
  - [ ] day/night and season behaviour is what the setting claims
- [ ] 🔒 **The landing site** — the tile the campaign starts on, chosen and defensible

---

## 2. 🔒 FACTIONS

- [ ] **Roster** — exactly who exists in this world
  - [ ] 🔒 every faction we want is present; every one we do not want is gone
  - [ ] 🔒 hidden / permanent-enemy factions (insects, mechanoids, empire-likes) decided
  - [ ] 🔒 settlement **count and placement** per faction on the map
- [ ] **Identity**
  - [ ] faction **names** are authored, not dice-rolled
  - [ ] leader titles and leader names
  - [ ] faction **colours, icons and banners** exist and are not placeholders
  - [ ] 🎨 description text a player will actually read
- [ ] **Relationships**
  - [ ] 🔒 the **hostility matrix** — who starts hostile, neutral, allied, permanent
  - [ ] the player's starting standing with each
  - [ ] which relationships can move in play, and which must not
- [ ] **What they field**
  - [ ] pawn kinds per faction, per group (combat, trade, settlement, peaceful)
  - [ ] **items allowed to each faction** — weapons, apparel, armour by tag
  - [ ] tech level, and that their gear matches it
  - [ ] ⚙️ nobody generates **bare-handed** or in the wrong century's kit
  - [ ] raid strategies and arrival modes available to each
- [ ] **Trade**
  - [ ] trader kinds per faction — who buys, who sells, what
  - [ ] caravan and orbital trader roster
  - [ ] the player can actually buy what the campaign assumes they can

---

## 3. 🔒 RELIGION — ideoligions

- [ ] 🔒 every faction that should have its own faith **has** one (not a generated stand-in)
- [ ] 🔒 the **player's** ideoligion
- [ ] per faith:
  - [ ] memes — and no silent exclusion-tag collision
  - [ ] precepts that actually change play, not only a tooltip
  - [ ] deities / pantheon, with names
  - [ ] rituals
  - [ ] ideo **roles**
  - [ ] style — apparel, hair, art, naming
  - [ ] ⚙️ it survives world creation as authored, and is not overwritten by a preset
- [ ] 🎨 the faiths read as different from each other in play, not only on paper

---

## 4. PAWNS — who walks around

- [ ] **Races / xenotypes**
  - [ ] the roster of playable and NPC xenotypes
  - [ ] genes per xenotype, and what they do
  - [ ] 🎨 each one has a **face** — head, body, hair, skin; nothing magenta
  - [ ] xenotype chances per faction — who fields whom
- [ ] **Pawn kinds** — the roles, not the individuals
  - [ ] the full kind roster exists and each is reachable in play
  - [ ] ⚙️ every kind **spawns holding something** appropriate
  - [ ] apparel per kind, and it survives the biome's temperature
  - [ ] skills, ages and traits per kind
  - [ ] combat power / points cost is sane against the raid curve
- [ ] **Character**
  - [ ] backstories — spawnable, and written for this setting
  - [ ] name banks per faction and per race
  - [ ] traits allowed / banned, and no impossible pairs
  - [ ] 🎨 speech, nicknames, flavour text
- [ ] **The named cast** — anyone the fiction names
  - [ ] each exists as a real pawn definition
  - [ ] ⚙️ each loads without being silently discarded
  - [ ] each is **placed** — a faction, a settlement, or a spawn route
- [ ] 🔒 **The player's starting colonists** — who they are, and their gear

---

## 5. ITEMS — what exists to be held, worn and built

- [ ] **Weapons**
  - [ ] the allowed list — melee and ranged, per tech level
  - [ ] what is cut, and ⚙️ **nothing was disarmed by the cut** (tags reduced to zero)
  - [ ] 🎨 art exists for every survivor
  - [ ] damage, range and armour penetration are sane against each other
- [ ] **Apparel and armour**
  - [ ] the allowed list, and the temperature range it covers
  - [ ] faction and ideo style requirements are satisfiable from it
  - [ ] 🎨 art exists, and layers do not clip
- [ ] **Consumables**
  - [ ] food and its sources; the colony can feed itself here
  - [ ] medicine tiers available
  - [ ] drugs — allowed, and who uses them
- [ ] **Materials and resources**
  - [ ] what can be mined, grown, scavenged or bought on this world
  - [ ] ⚙️ every recipe's inputs are obtainable here
- [ ] **Buildings and furniture**
  - [ ] the buildable list
  - [ ] power, defence, production, comfort — each has a route
  - [ ] 🎨 art exists; nothing is a pink box
- [ ] **Research**
  - [ ] the tree, and that it terminates somewhere meaningful
  - [ ] nothing required is unreachable on this planet
- [ ] **Special kit** — anything the campaign's fiction promises the player can find

---

## 6. CREATURES — what else is alive

- [ ] wild animal roster **per biome**, and it is not empty anywhere the player will walk
- [ ] predators and their danger level
- [ ] tameable animals; pack animals; livestock
- [ ] ⚙️ insects / burrow fauna
- [ ] mechanoids or their replacement — what the hostile machine threat is
- [ ] 🎨 art and sound for each; nothing generic standing in
- [ ] anything setting-specific that must be encounterable

---

## 7. 🔒 THE START

- [ ] 🔒 **Scenario** — the ScenParts, in order
  - [ ] starting pawn count and how they are chosen
  - [ ] starting items, animals and structures
  - [ ] anything permanently disabled or forced
- [ ] 🔒 the **gravship** / starting vessel — built, placed, and it flies
- [ ] **Storyteller** and difficulty chosen (and known to be changeable later)
- [ ] Anomaly / DLC playstyle settings decided
- [ ] the opening moments are authored — what the player sees, reads and does first
- [ ] 🎨 someone has actually played the first ten minutes

---

## 8. EVENTS — what happens to the player over time

- [ ] the incident roster — what can occur, and nothing setting-breaking can
- [ ] raid points curve against the faction roster
- [ ] quest roster — which shipped quests can fire here
- [ ] the campaign's own **spine quests**, if it has them
- [ ] ⚙️ every quest that can fire has a route to fire and can be completed
- [ ] endgame — what winning or leaving looks like

---

## 9. PRESENTATION

- [ ] 🎨 **no magenta, anywhere** — every texture the player can see resolves
- [ ] sounds exist for the things that make them
- [ ] music, if it is being changed
- [ ] UI text, tooltips and descriptions read as ours, not as three mods arguing
- [ ] 🎨 the colony looks like the setting from the standard zoom

---

## 10. THE LAST MILE — it has to actually run

- [ ] 🔒 the **mod list** is final, and the load order with it
- [ ] curation config (Cherry Picker et al.) is frozen and deployed
- [ ] ⚙️ repo and the game's Mods folder agree — deployed, not merely written
- [ ] ⚙️ the game **loads clean**: no red errors, no unresolved cross-references
- [ ] ⚙️ the shipping savegame loads to a playable state, twice, from cold
- [ ] a fresh machine with the same mod list can open it
- [ ] the save is backed up somewhere that is not one disk
- [ ] 🎨 someone who is not us has started it and not been confused

---

## The order to freeze in

Freeze outward from what cannot be undone:

```
1.  the mod list          nothing below survives changing it
2.  the planet            baked into the save
3.  factions + faiths     baked at world creation, per faction
4.  the start             scenario, ship, cast, landing site
5.  everything else       defs; changeable later, so freeze last
```

⚠️ **Anything marked 🔒 that is still open is blocking more than it looks like.** The rest
can be edited after the world exists; those cannot.
