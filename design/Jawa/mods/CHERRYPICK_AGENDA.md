# CHERRYPICK_AGENDA.md — everything we review together, and in what order

DECIDE owns this. Chain step 1. It is the running agenda for the interactive
cherrypick sessions; tick a row when its pass is finished.

**The mechanism already exists.** Cherry Picker is live at load order 11 with 24
entries, and **every entry is reversible by editing one file**. Nothing here is
destructive, so we can be decisive and correct later.

## The three kinds of row

Not every category can be reviewed the same way. The honest split:

| kind | meaning |
|---|---|
| **PASS** | we go through it together and rule. It is small enough to be real. |
| **TARGETED** | far too large to review. No pass — we cut named things on sight, in play or when one offends. |
| **DERIVED** | not reviewed at all; it follows from a decision made elsewhere. |

## Done — do not re-open

| ✔ | category | how it was settled |
|---|---|---|
| ✅ | **Factions** | 21 untick / 6 keep, ratified, plus our own 13. Spent at the world screen |
| ✅ | **Biomes** | 29 removals + 4 keeps, via `PlanetTypeDef.biomeBlacklist`, not Cherry Picker |
| ✅ | **Anomaly content** | your 9 creature/object picks + 2 genes — the live 24 keys |
| ✅ | **Mod list** | 585 frozen, two files, `deployed/config/v1_freeze/` |

## PASS — the real work, in the order I recommend

| ✔ | # | category | size | the unit we decide in | why this order |
|---|---|---|---|---|---|
| ☐ | 1 | **Already-cut factions' gear** | ~70 items | by mod | Easiest possible start. We removed the faction; its gear still circulates in trade and loot |
| ☐ | 2 | **Weapons** | **845** | by mod first (60), then by tier | The hardest and the most load-bearing — pawn types cannot be equipped until it lands |
| ☐ | 3 | **Armour / apparel** | **886** | by mod, then by layer | No list exists at all today. Same blocker as weapons |
| ☐ | 4 | **Creatures / beasts** | **2,387** | by mod and by theme | Fiction-visible on the map. Your dinosaur review sits here |
| ☐ | 5 | **Mechs** | 80 | one sheet, name + role | Art on disk for 55; the other 25 need photographing first |
| ☐ | 6 | **Drugs & medicine** | subset of 4,393 | by class | Small real subset; most ingestibles are meals and raw food |
| ☐ | 7 | **Incidents & quests** | 358 / 243 | by name | Fiction-breakers arrive as events. Cheap to scan, high visibility |
| ☐ | 8 | **Traits** | 268 | one sheet | Stat-multiplier creep is the known risk here |
| ☐ | 9 | **Ideology styles** | 1,615 | by category | Low priority, but they decide what buildings LOOK like |

## TARGETED — no pass, ever. Cut on sight.

Reviewing these per-def is not possible and pretending otherwise wastes sessions.

| category | count | how it gets handled |
|---|---|---|
| **Buildings / furniture** | **8,742** | Cut only when one offends. `designationCategory` clearing hides a whole mod's menu cheaply |
| **Genes** | **4,833** | DERIVED — follows the xenotype decision |
| **Food & meals** | most of 4,393 | Only the fiction-breakers; nobody audits a meal list |
| **Recipes** | 2,951 | DERIVED from whatever items survive |
| **Hediffs** | 2,754 | DERIVED |
| **Terrain** | 1,240 | Handled by biome work, already done |

## DERIVED — decided elsewhere

| category | where it is decided |
|---|---|
| **Xenotypes / races** | 🔴 **Not a cherrypick.** Owner's ruling: build our OWN set as an amalgam of what exists, for total control. See `D23` |
| **Pawn kinds** | Follows weapons + apparel; that is chain step 3 |
| **Research** | Follows whatever items survive |

## How the sessions run

- I bring a **cluster** with the principle stated first, so you can agree with the
  principle rather than adjudicate every line.
- Default batch is **8–12 decisions**. Say *"smaller groups"* or *"bigger groups"*
  and I recalibrate.
- A principle you accept once is applied to everything it covers, and I list what
  it swept so you can spot-check rather than re-read.
- Anything you are unsure about goes to a **hold** list rather than a guess.
