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
**Colour is purple** (deep purple skin, purple-staining tea) — owner-confirmed 2026-09-23.

## tier — and the free-tier occupant is the SEKKULAATH

🔴 Ours in the `RM_` tier, mapped to the dianoga when the campaign layer is active (owner: *"map
it to the Dianoga when Utinni is active"*). ⇒ The free mod needs its own invented captive, so
this building must not name a canon creature in the franchise-free tier.

🔑 **Owner, 2026-09-23 — that captive is now named.** Verbatim: *"we need more generic eldritch
tentacled horror creatures put in the tank in the vanilla game, similarly related to the big
version down in the ground. Let's call it a Sekkulaath."*

⇒ **`RM_Sekkulaath` is the species name for our invented eldritch tentacled horror** — one
species at two scales, exactly the dianoga's own relation: **the tank holds a juvenile, and the
adult is the thing below the Fever Wood.** It is not a second creature invented for the tank.

✅ **This closes a gap rather than opening one.** §6m stage 3 already says an escapee *"left alone
in water can mature into the real thing"* — which only coheres if the captive and the thing below
are one species. The naming makes that explicit. And `FEVERWOOD_TENTACLE_BESTIARY_1` carried the
`RM_` creature **unnamed**, so the next agent to build it would have invented a name; fixed there
in the same change.

🔑 **An invented exotic name is not IP** (CLAUDE.md Q11a), so Sekkulaath lives in the
franchise-free `RM_` tier and is cast inline. ⛔ It does **not** route through the Utinni patch
layer, and ⛔ it gets no `canon_references/` entry — there is no canon to reference.

⛔ **The free tier is not a thin fallback.** The Sekkulaath is the centrepiece the free mod
actually ships, with the dianoga *mapped over it* when the campaign layer is active — never an
impoverished substitute for it.

## 🔴 build it GENERIC — it is the model for a whole class

**Owner note, 2026-09-23:** the tank is **a high-prize item with many uses**, and it **will serve
as the model for other similar storage/prison systems for living ingredients.**

⇒ ⛔ **Do not hard-code this to one creature.** The first implementation is the pattern every later
one copies: a vessel that is a **cell**, upkeep that is **feeding**, **repeat harvest from a live
animal**, **escape as the failure mode**, and a **placement decision** that matters because escape
consequences depend on it.

⇒ Candidates already named for the same pattern (unruled): venom from a kept venomous creature,
eggs from a captive layer, blood from something that must stay alive, and sap-drinkers kept for
nectar. 🔑 That last one already interacts — `FEVERWOOD_SAP_SUCKER_GUILD_1` rules that **taming buys
access, never obedience**, so a tamed occupant still triggers its defence when mishandled.

Cuisine is the consuming system and records the pattern at
`design/Jawa/proposals/high_cuisine_deep_design.md` §4a. The mod that receives the food half is
`mandrake.rsw.cuisine` (`src/RimStarWars/Cuisine/`), which its own `About.xml` already names as the
intended home for the rest of that design's build ladder.

## open

- ⚠️ **Whether *"more generic … creatures"* (plural) means a CAST** of several distinct tentacled
  horrors for the tank class in the free tier, or simply "more-generic, i.e. non-IP" — the reading
  recorded, and the one the singular *"a Sekkulaath"* supports. ⛔ Do not invent a second species on
  the strength of the plural alone. 🔑 Note the bestiary may already satisfy the plural instinct:
  its **six limb-types deliberately read as separate pseudo-species** while belonging to one
  animal, which is variety without a second creature.
- ⚠️ **Tier grammar of the shipped code.** The deep thing's built types are
  `RUT_MapComponent_TheTenant` and `RUT_TenantEmergenceSpawner` — **campaign prefix on
  franchise-free content**, now that the creature is `RM_Sekkulaath`. `RM_TenantTruceExtension`
  is already correct. Renaming shipped C# is real work and FOUNDRY's; flagged here rather than
  done, and ⛔ not a reason to delay the creature.
- **How long stage 3 takes**, and whether it is interruptible once begun.
- Feed rates, product rates, tank materials, and what damage level triggers a release.
- **What the generic abstraction actually is** — one comp parameterised by occupant and product, or
  a base ThingDef others inherit. Unset, and it is the first real decision of the build.
