# SCENARIO_SPEC.md — how the campaign starts

DECIDE owns this file. Chain step 12. It had no document at all until now.

**Owner's ruling, 2026-08-14:** *"The pawns emerge upon the broken gravship after
having brought it to life. We may create a custom map with other broken ships in
v2, but for v1 it's just a ship on a map ready to go. Fixed pawns. Fixed ship.
Fixed map."*

## R25 · The scenario is a SAVED GAME, not a `ScenarioDef`

`ScenPart_ConfigPage_ConfigureStartingPawns` sets a pawn **count**. It cannot
force named pawns with authored skills, traits and backstories — no `ScenarioDef`
part can. Forcing exact pawns needs either C# or a save.

The owner has already ruled the world is hand-made and shipped as a resource we
enable. ⇒ **The same save carries the map, the ship and the six founders.** One
artifact, no new code, and "fixed" means fixed.

**Who does what:**

| step | who |
|---|---|
| make the world, pick the tile, save it | **owner** |
| place the exported gravship on the landing map | BUILD, via the bridge |
| author the six founders | BUILD, via Character Editor |
| set starting gear and stock | BUILD |
| save, and that save IS v1's campaign start | **owner** |

🔴 **Every `FactionDef` and ideo block must be deployed BEFORE the owner makes
the world.** Both are read once at world creation.

## 🔴 The save goes IN THE REPO, or it does not exist

**Owner's ruling, 2026-08-15:** *"There is no map protection! There's no
protection of any asset not in the repo! Stop treating things as precious."*

⇒ **The campaign-start save is the one artifact v1 actually ships, so it is
committed.** Anything left only in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves`
is disposable by definition and will be treated that way.

Measured 2026-08-15: saves run **~30 MB**. That clears the repo's ~50 MB per-file
rule and GitHub's 100 MB hard reject, so this is viable — but git stores each
binary revision whole. **Commit the finished start, not every iteration.** This
history was already re-initialised once to shed a 278 MB `.git`.

⛔ **Do not build a backup or preservation mechanism for anything outside the
repo, and do not infer that play has begun.** The owner will say when it has.

## The opening

The clan has just brought a dead gravship back to life. The campaign begins the
moment it sets down and the hatch opens — the ship is already the home base, and
it is already theirs. **What they have not got is the hardware to fly it again:**
thruster, fuel tank and pilot console are the v1 flight capability made into a
v2 goal, exactly as the flight ruling has it. The ship is a house that used to be
a vehicle, and getting it airborne again is the campaign.

## Fixtures

| | |
|---|---|
| **map** | the tile the owner picks, on the world he saves. Desert / ExtremeDesert / AridShrubland |
| **ship** | `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml` — 4,057 substructure cells, 1,053 things, already boardable |
| **pawns** | the six founders below. No random colonists, no random gear |
| ⚠️ floors | **terrain does NOT come with a mid-game spawn.** Replay the layout's `terrainDef` cells through `jawa/set_terrain_batch` after placing the ship, or the deck lands bare |

## The six founders

All six: xenotype **`MandrakeJawa`**, apparel locked to the Jawa robe and hood
(`apparelRequired`), gender male (the clan is all-male by lore). Skill spreads
follow `jawa_crew_personas.md` §5.6; **traits, passions, ages, work disables and
gear are decided here.**

### Nekko Vok — "Captain of the Opened Hull" · age 47

The living clock on the succession arc: oldest founder, deliberately near the
aging threshold, so the clan's harsh covenant will eventually be tested on the
pawn the player likes most.

```
Social 9 (Major passion) · Intellectual 5 (Minor) · Crafting 1 · Shooting 1
traits         Iron-Willed · Fast Walker
workDisables   Mining
gear           Jawa robe + hood · ion sidearm · "The First Fusioncutter" (relic)
```
⚖️ **Disable Mining, not Violence.** The lore offers either. With so few pawns, a
leader who cannot pick up a rifle in an emergency is a colony-ending liability;
one who will not dig is merely characterful.

### Tobb Nkik — "Keeper of the Articles" · age 38

```
Intellectual 9 (Major) · Social 6 (Minor) · Medicine 1
traits         Ascetic · Slow Learner
workDisables   Violent
gear           Jawa robe + hood · no weapon
```
Kept pure to his written role. The food gap he would otherwise have had to fill
is Sekki's — see the sixth founder below.

### Griz Utinn — "The Hands" · age 34

```
Crafting 8 (Major) · Construction 6 (Major) · Mining 6 (Minor)
traits         Industrious · Greedy
workDisables   Social
gear           Jawa robe + hood · ion sidearm · toolbelt
```
The industrial spine and the protagonist of the droid-theft arc. `Greedy` ties
haggling-as-devotion to a real mood need and will cost the player a good bedroom.

### Yeku — "First-Hatched" · age 19

```
Shooting 8 (Major) · Animals 5 (Minor) · Melee 1
traits         Trigger-Happy · Volatile
workDisables   Intellectual
gear           Jawa robe + hood · the crew's one real rifle · pack animal
```
Just-turned-adult, so the fast-growth engine is visible on screen from minute
one. The only violence-capable pawn, and `Volatile` means he will pick fights
with the Captain — which is the succession arc warming up.

### Sekki Vosh — "The Long Pot" · age 29 · THE SIXTH FOUNDER

Added on the owner's ruling, 2026-08-15. The five as written carry **zero**
Cooking and **zero** Plants between them, which on a desert world is a starvation
start rather than a difficulty choice. The owner chose a sixth founder over
diluting Tobb's concept.

```
Cooking 7 (Major) · Plants 5 (Minor) · Construction 2 · Social 2
traits         Gourmand · Neurotic
workDisables   Intellectual
gear           Jawa robe + hood · knife · no gun
```

He runs the still and the kitchen, and he is the clan's hauler — the one who
knows where everything is.

⭐ **`Gourmand` is deliberate, and it fits the faith rather than fighting it.**
The approved ideoligion ships **`NutrientPasteEating_Disgusting`**: Jawas prize
delicacies and merely *tolerate* paste because of the world they live on. So the
cook is not a servant of an austerity — he is the reason the clan does not have
to eat the thing it despises, and the one member whose appetites most openly
express what everyone else quietly wants. When food quality drops, Sekki is the
first to say so.

⚖️ **He can hold a gun but is not a soldier** — no Shooting skill, `Violent` NOT
disabled. This keeps Yeku the only real gun while adding a body for a crisis, so
the crew is easier to *feed* without becoming easier to *defend*.

### Wim Ateeka — "The Twice-Kin" · age 31

```
Medicine 9 (Major) · Intellectual 5 (Minor) · Social 3
traits         Kind · Wimp
workDisables   Violent
gear           Jawa robe + hood · medicine ×15
```
Born to another clan, taken as a slave, made kin through the love-gate — the
living precedent that the mechanic exists before the player ever meets it.

### Why this six plays well

**Covered:** leadership, research, crafting/construction/mining, shooting,
medicine, food. **Deliberately absent:** any second fighter, any artist, any
second builder. Losing Griz or Yeku genuinely hurts, which is the point.

⚠️ **Two pawns have `Violent` disabled** (Tobb, Wim), Yeku is the only real gun
and Nekko is a poor one. **This is a hard start and the owner ruled 2026-08-15
that it STAYS hard** — a scavenger clan is not a war party. The sixth founder
feeds the crew without defending it, so adding him did not soften the opening.
If a live session proves it unsurvivable, the cheapest fix is giving Nekko
Shooting 4, **not** re-enabling anyone's violence.

## Starting stock

Salvage-flavoured and thin. Steel and components from stripping the ship, not
from a supply drop.

```
steel 300 · components 20 · packaged survival meals 30 · medicine 15
ion sidearm ×2 · one rifle · pack animal ×1
NO advanced components, NO glitterworld medicine, NO prebuilt turrets
```

## Open, and deliberately not decided here

- **Egg-laying and the clan's growth engine** ride `Outland_EggLayer`. The
  founders exist and play regardless; the mechanic layers in when confirmed.
- **The xenotype-death mourning thought** has no off-the-shelf mod and stays
  hand-authored `[v2]`.
- ✅ **The sixth founder question is CLOSED** — the owner took the sixth founder
  over diluting Tobb. Sekki Vosh is specced above.

---

## 🔴 The ship is `The Utinni` — owner, 2026-08-15

The hull's original name was **`Kolyska`** ("Cradle"). The Jawa rename it **`The Utinni`** on taking it — the grandest find there could ever be. **The starting save must ship with the new name already applied**; it is not a later patch. `Kolyska` survives only inside the hull, in the Cradle nursery and in the Cradle-Mind, which never accepted the rename. Full ruling in `design/Jawa/worldbuilding/ship_distinctive_features.md`.

---

## 🔴 MANY PATHS TO FUEL, or the ship starves — owner, 2026-08-15

**A structural requirement of this campaign, recorded here because it constrains
the SCENARIO and not just the resource tables.**

This is a gravship arc: the design assumption is *keep moving, react to what the
galaxy throws at you*. That makes fuel the one resource whose absence does not
produce a setback — it produces **a dead save**. A colony that runs out of steel
rebuilds. A ship that runs out of fuel stops being a ship, and the campaign
stops with it.

⇒ **Fuel must have MANY independent paths**, and the redundancy is deliberate
insurance rather than untidy design. The planet currently offers three, ruled
separately and now confirmed as a set (`hydrology_and_fire_ecology.md`):

- **helixien gas pockets** — volcanic and deep-desert tiles; the price is holding
  a hazardous tile.
- **propane lakes** — deep night past the terminator; the price is surviving a
  cold expedition.
- **tar pits** — the Pyrelands margin; the price is working beside the fire.

**They differ in ACCESS COST, not in yield.** Three prices for the same
commodity, so the player chooses by circumstance — dug in, on the move, or
desperate — rather than by arithmetic.

⚠️ **Consequences for the scenario and the starting save:**

- **The starting stock must not assume a particular path.** The founders begin
  with fuel, not with a fuel *strategy*.
- **No quest, faction or event may gate the last remaining path.** Anything that
  can cut the player off from fuel must leave at least two others standing.
- 🔴 **Never balance one of the three into irrelevance.** Each is somebody's only
  option at some point in the campaign. A path that is merely bad has been
  deleted, whatever the numbers say.
- **The Pyrelands earn a second reason to exist**: they are the fuel source you
  can reach *without* leaving the good farmland, which is exactly the kind of
  bargain the high-risk/high-reward tile should be offering.

---

## 🔴 NAMES — ruled by the owner, 2026-08-15

| the thing | its name |
|---|---|
| **the planet** | **`Ash'karr`** — translated, **"The Sundered"** |
| **the scenario** | **`Flight of the Utinni`** |
| **the ship** | **`The Utinni`** (was `Kolyska`, "Cradle" — see `ship_distinctive_features.md`) |
| **the burning savanna** | **`The Pyrelands`** |
| **the one mega-structure** | **`The Rust Cathedral`** |

⭐ **`Flight of the Utinni` is the right title because it is a pun that is also a
thesis.** *Flight* is the gravship — and it is also fleeing, which is the campaign:
keep moving, react, never hold. And **`Utinni!` is the cry raised when salvage is
found**, so the scenario's name says *the discovery is the escape* — that a
scavenger clan's greatest find and its way out are the same object.

⚠️ **Build notes, because names are load-bearing in more places than people
expect:**

- **The scenario name is player-facing text** and appears in the scenario list,
  the save, and the game's own UI. Set it once, in the scenario, and do not let a
  quest or letter spell it differently.
- **The ship must already be named `The Utinni` in the STARTING SAVE**, not
  renamed later.
- **`Ash'karr` carries an apostrophe.** Check it survives every place a name is
  written — XML, translation keys, save data, and any filename derived from it.
  An apostrophe is the character most likely to be silently stripped or to break a
  string.
- **The translation "The Sundered" should appear in player-facing text at least
  once**, or the meaning never reaches the player. `GameStartDialog` is the
  obvious place — it is the opening narration and costs nothing.
