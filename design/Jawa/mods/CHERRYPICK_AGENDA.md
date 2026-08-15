# CHERRYPICK_AGENDA.md — everything we review together, and in what order

DECIDE owns this. Chain step 1. It is the running agenda for the interactive
cherrypick sessions; tick a row when its pass is finished.

**The mechanism already exists.** Cherry Picker is live at load order 11 with 24
entries, and **every entry is reversible by editing one file**. Nothing here is
destructive, so we can be decisive and correct later.

## 🔴 The principle — owner, 2026-08-15

> *"We're doing a trimming pass right now to get rid of things we KNOW we won't
> need. Easy cuts, obvious cuts, so that we're working with smaller item sets and
> closing in on a playable game. But it still needs human verification."*

⇒ **Obvious cuts only, and every batch is verified by the owner.** The point is to
shrink the working set before the hard passes (weapons, armour), not to make fine
judgements now.

⛔ **A rejected principle, recorded so it is not re-proposed:** *"we cut the
faction, so cut its gear too."* **Wrong.** The owner: *"we often accept silly
races in order to get the gear from their mod. That's a bad assumption. We can
always rename things."* Fiction of a race or faction says nothing about whether
its gear is wanted.

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
| ☐ | 1 | **The fantasy / medieval block** | 8 mods, ~446 things | by mod | Dark Ages, dungeon and monster content. Nothing in it renames into Star Wars — the clearest "we know we won't need it" case |
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

## Holds — decided later, on purpose

| item | why it is held |
|---|---|
| **`[AB] Xenotype: Yautja`** | Owner, 2026-08-15: keep for now, revisit **after `D23`** builds our own xenotype set. Its 432 genes and 9 xenotypes are the cost; 13 melee weapons on a clean AP 0.60 tier are the benefit. Nothing external depends on it, and the `.rid`/`.xtp` references are mod-list stamps, not dependencies |
| **Megafauna** · **Mythic Ages: Megafauna Bestiary** | The design uses megafauna as the counter to Junker warcaskets. Big desert beasts fit the setting |
| **Onimods: Electric Torches and Braziers** | Sounds medieval, is lighting. Plausible on a scavenger world |

## Method

**Whole-mod removals go through `ModsConfig`**, not Cherry Picker — 446 def-by-def
entries would be absurd. Reversible by re-ticking, but needs a game-down window
and carries `Could not resolve cross-reference` risk.
**Cherry Picker is for surgical cuts inside mods we keep.**
