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

### ✅ The campaign-layer occupant is ALREADY BUILT — MEASURED 2026-09-23

⇒ **Yes: with the Star Wars layer active the tank holds a dianoga, and it costs nearly nothing,
because `RSW_Dianoga` already ships** (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dianoga.xml`)
with its own BodyDef and four SoundDefs. ⛔ Do not author a dianoga for this.

| measured on the shipped def | value | why it matters here |
|---|---|---|
| life stages | **3** — *"dianoga larva"* `drawSize 0.8`, mid `2.6`, adult `3.8` | 🔑 the **larva stage is the tank's juvenile already** — no new art, no new def, and it matches the canon "Toothy" display tank |
| `baseBodySize` | 4.0 | an adult is genuinely big; the larva is what a tank can hold |
| body parts | **left tentacle / right tentacle** | the creature is already tentacled at the BodyDef level |
| `foodType` | Carnivore, Omnivore, Ovivore, **AnimalProduct** | ✅ the §6j feeding loop (fed corpses or meat) needs no new food wiring |
| `trainability` | **Advanced** | 🔴 see the conflict below |

🔑 **And the adult's sprite is irrelevant to the thing below**, because the deep adult is *never
rendered* (bestiary item: only tentacles are ever drawn). ⇒ The dianoga art is only ever seen **in
the tank**. That is a clean split and it is why one def can serve both roles.

### 🔴 all three questions RULED — owner, 2026-09-23

#### 1. The dianoga lives in ONLY two places

**Owner, verbatim:** *"It's a mistake to have dianoga in the GreenTime. It belongs only in tank
prisons and the Fever Wood. Create something new and terrifying for the Green Tide."*

⇒ **Two homes, total: the tank, and the Fever Wood.** ✅ This is not a new position — an earlier
owner review had *already* ordered it out of the Greentide: `rosters/the_greentide.json` carries
`"disposition": "move:AB_MiasmicMangrove"` on that row. **The move was decided and never executed
in the defs**, because `WildAnimals_Greentide.xml` was built by copying `RUT_Greentide.xml`'s
roster *verbatim* ("nothing rescaled, added or dropped"), which carried the row along with it.

⚠️ **The Miasma placement was HIS OWN earlier decision and this ruling retires it.** Its recorded
reason: *"would be awesome if we could add tentacle pulling capabilities like the lasso power or
future sarlacc mod, put it in the maiasma."* 🔑 **That intent is now delivered where he wants the
creature instead** — `FEVERWOOD_TENTACLE_BESTIARY_1`'s **snare** limb *grabs and drags*, which is
exactly the tentacle-pulling he was reaching for. So the wish is satisfied by the Fever Wood, not
abandoned. Flagged for his veto rather than quietly dropped.

⇒ **The Greentide keeps the hole until a NEW creature fills it** — never a neighbour's species
(CLAUDE.md fauna law). Tracked as its own item.

#### 2. SWAP, not add — and gated on the StarWars tier

**Owner, verbatim:** *"Swa[p]s the Dianoga in, replacing the Sekkulaath, when RimMandrake.StarWars
is present."*

⇒ 🔴 **One creature, one def-slot. The dianoga REPLACES the Sekkulaath** — the two never coexist,
which is what §1's *"two layers, one creature"* always meant. ⛔ Do not spawn both.

🔑 **Note the gate he named: the StarWars tier, not the campaign layer.** Earlier prose said "when
Utinni is active"; his words are *"when RimMandrake.StarWars is present."* That is the **more
correct** gate, because `RSW_Dianoga` lives in the StarWars tier
(`src/RimStarWars/SWBestiary/`, packageId **`mandrake.rsw.swbestiary`** — MEASURED, not guessed).
⇒ The swap is `MayRequire="mandrake.rsw.swbestiary"`, and it must NOT be gated on a `RimUtinni`
packageId. ⚠️ Whether the swap is a def-replace patch or a runtime substitution is still an
implementation choice; the **gate** is settled.

#### 3. Advanced training stays — but the tank is not where it happens

**Owner, verbatim:** *"It should have advanced training, but you would have to train it by
releasing it from the tanks, letting it calm down, and then trying to train it normally. If there
are still pools, it plops down into them and installs itself as a new tentacled horror (small one),
so it's no longer trainable. But if it gets out on a map without such pools, it will escape and
simply wander wild. Advanced training is fine, but it should have large wildness, be very
challenging to tame, and have a high chance of attacking if you fail. It remembers the tank..."*

⇒ 🔴 **`trainability: Advanced` is CORRECT and stays.** The contradiction with
"prisoner-not-livestock" dissolves because **you cannot train it in the cell** — taming requires
*releasing* it first, and release is the dangerous act.

**The release has exactly two outcomes, decided by the map, not by a roll:**

| map state | what happens |
|---|---|
| ⭐ **pools present** | it **plops into a pool and installs itself as a new tentacled horror — a SMALL one** → 🔴 **no longer trainable, ever.** The taming attempt has instead *created a threat* |
| **no pools** | it **escapes and wanders wild** — a tameable wild animal on the map, which is the only path to actually training one |

🔑 **This is the same event as §6m's escape, read from the other side.** Stage 2 ("if it reaches a
pool it establishes") and this release are one mechanism; the player's *intent* differs, the
outcome does not. ⇒ ⛔ Do not build two systems. And 🔑 **it re-prices "build the prison away from
the pools"**: that placement rule is no longer only about surviving a disaster, it is the
precondition for ever taming one.

**Stat direction ruled, numbers unset:** **large `wildness`**, very challenging to tame, and a
**high chance of attacking on a failed taming attempt**. ⚠️ ⛔ Do not guess the three numbers.

🔴 **"It remembers the tank…"** — ruled in spirit, mechanism deliberately unset. It means a
released dianoga's hostility is **not neutral**: captivity leaves a mark that makes the animal that
was imprisoned harder or more dangerous to win over than one that never was. ⚠️ Whether that is a
hediff, a per-pawn flag lowering tame chance, a manhunter bias on failure, or a memory of the
*specific* colony is **open** — see `open`. ⛔ Do not implement a generic wildness bump and call
this delivered; the flavour he is naming is *grudge*, not difficulty.

⚠️ Two rosters cite the dianoga as bare **`Dianoga`** (`the_greentide.json`, `the_miasma.json`)
against the shipped `RSW_Dianoga` — two more instances of the bare-name class noted on
`ROSTER_DEAD_BMT_NAMES_SWEEP_1`.

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
- 🔴 **What "it remembers the tank" actually IS.** Ruled in spirit (see ruling 3), mechanism unset:
  hediff, per-pawn tame-chance penalty, manhunter bias on failed taming, or memory of the specific
  colony that held it. ⛔ A plain wildness increase does not deliver it — the flavour is *grudge*.
- **The three taming numbers** — `wildness`, tame difficulty, and the attack-on-failure chance.
  Direction ruled (large / very challenging / high), values unset. ⛔ Do not guess them.
- **Whether the small pool-installed horror can mature** into the real thing, as §6m stage 3 says
  an escapee can. If yes, a failed taming attempt is on a timer to become the biome's worst threat.
- **How the swap is implemented** — a def-replace patch on the Sekkulaath vs a runtime
  substitution. The *gate* is settled (`MayRequire="mandrake.rsw.swbestiary"`); the mechanism is not.
- **How long stage 3 takes**, and whether it is interruptible once begun.
- Feed rates, product rates, tank materials, and what damage level triggers a release.
- **What the generic abstraction actually is** — one comp parameterised by occupant and product, or
  a base ThingDef others inherit. Unset, and it is the first real decision of the build.
