# FEVERWOOD_DIANOGA_PRISON_1 — a prison tank, not a pen

## spec

Authority: `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md` §6j, §6m.
🔴 Depends on §0 — the owner's 2026-09-23 rulings **superseded hard ban 1** of the frozen sheet,
so the creature is now ambient and **named**.

**Owner, verbatim:** *"1+2+3 and it is TOUGH. That's why they're not farmed, they're
imprisoned."*

🔴 **It is a CELL, not a pen. The occupant is a prisoner, not livestock.** ⛔ Do not write, name
or art this as animal husbandry. Everything harvested comes from something held against its will
and strong enough to be a real threat.

## what it does — all three

| | |
|---|---|
| **teaches** | seeing it names the creature; hearing the hum up close is how a player learns to recognise the real warning before it kills them. This is the *"learn the lore at last"* payoff |
| **produces** | fed corpses or meat, it yields the canon product line — meat for **pie**, **spleen chemicals** for the narcotic **tea**, **cream** |
| ⭐ **escapes** | a neglected or damaged tank **releases it** — a disaster the player built |

## the escape escalates through three stages

1. It gets out and **it is TOUGH** — water-bound and drying, it makes for the nearest water and
   hurts whatever is between.
2. **If it reaches a pool it establishes** — the map permanently gains a new occupied pool.
3. ⭐ **Left alone in water it can mature into the real thing** — the player will have created
   the biome's worst threat themselves.

🔑 **Stage 2 costs almost nothing to build:** hand the escape to systems already shipped — the
pool registry in `RUT_MapComponent_TheTenant`'s terrain scan, and `RUT_GenStep_ScatterPools`.

## 🔴 the tension, and its resolution

"The escape must be survivable or nobody builds the tank" pulls against "it is TOUGH." ⛔ **Do
not resolve this with a difficulty number.** The resolution is that **containment is the
player's job**: canon water dependency (*"survives only brief stretches in open air"*) means an
escapee is **racing for water**, so the defence is distance and blocking, not out-fighting it.

⇒ ⭐ **Build the prison away from the pools.** That is the real decision this feature is about,
and it is what a player should learn from it.

## canon — sourced, see the entry

`design/RimStarWars/canon_references/dianoga/description.md` (expanded 2026-09-23). The tank has
direct canon precedent: **"Toothy," a juvenile dianoga kept in a display tank**, and canon
dianoga living in the **SoroSuub refinery's water tanks on Sullust**. ⭐ The owner's 2026-09-14
ruling on that entry already assigned the food material to the **Star Wars Cuisine mod**, so the
product half has a home.

⚠️ **"Dianoga cheese" is UNCONFIRMED** — named by the owner, but no page was pulled for it.
⚠️ **"Lavender" is NOT canon** — zero occurrences across 13 pages. Purple is sourced.

## tier

🔴 Ours in the `RM_` tier, mapped to the dianoga when the campaign layer is active (owner: *"map
it to the Dianoga when Utinni is active"*). ⇒ The free mod needs its own invented captive, so
this building must not name a canon creature in the franchise-free tier.

## open

- **How long stage 3 takes**, and whether it is interruptible once begun.
- Feed rates, product rates, tank materials, and what damage level triggers a release.
