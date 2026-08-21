## spec
_not recorded in the source queue_

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
**from:** 🔴 THE OWNER, 2026-08-20, in his own words: *"Please ask DECIDE to spec out Art for
all the factions and give them to BUILD for implementation. That's a GREAT idea.
Search Star Wars canon for inspiration here."*
Raised because `AM_EnemyPirate` (the Blackstar Company) shipped with a NULL
`settlementTexturePath` and threw `ArgumentNullException` once per settlement per
frame — TPS 60 → 3.7. The crash fix is filed separately to BUILD as
`BLACKSTAR_HAS_NO_SETTLEMENT_ART_1` and must NOT wait on this spec.

**what:** Every faction that holds ground on Ash'karr needs art that reads at a glance on the
world map. Right now eleven of twelve share `World/WorldObjects/DefaultSettlement`
— the same generic hut — and the twelfth has nothing at all.
THE TWELVE, with their holdings, in size order:
  Homestead Defense League 13 · Deep Desert Tribes 9 · Hutt Cartel 8 ·
  the Junkers 8 · Jawa Trade Moot 7 · Geonosian Foundry Hive 5 ·
  Deepwater Compact 5 · Blackstar Company 4 · Wildsteam Clan 4 ·
  The Galactic Empire 3 · Free Droid Enclaves 3 · Ascendant Helix 3

**decide:** For each faction, a written art brief BUILD can implement without asking twice:
1. **settlementTexturePath** — the world-map icon. This is the one that matters
   most: it is what the player reads a hundred times a session.
2. **factionIconPath** — the roster/relations icon.
3. Whether the faction warrants its OWN sprite or can share a themed vanilla one.
   ⚠️ Be honest about which ones are worth the art. Twelve bespoke icons is a lot
   of sprite work and the Empire and the Hutts earn it more than a three-holding
   enclave does.
4. The CANON hook per faction, since the owner asked for it explicitly — Hutt
   Cartel, Geonosians, the Empire and the droid enclaves all have real Star Wars
   visual language to draw on. The Jawa Trade Moot and the Homestead Defense
   League are ours and need inventing.

**constraints:** 🔑 **A faction absent when he builds the world is absent from every player's game
forever** — but ART is not in that class. A texture path can be patched later; it
is not frozen at worldgen. So this is not a worldgen blocker and must not be
treated as one.
📌 `generating-rimworld-sprites` is the skill for producing them, and it has the
canvas and alpha constraints that make a sprite actually load.
⛔ Do not spec art for `AM_EnemyPirate` that BUILD cannot ship — it is a
THIRD-PARTY def and must be reached by patch, not by editing the mod.

**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready
