# Jawa Xenotype + Ideoligion — Deep Dive & Buildable Spec

_Gravship Expedition campaign (RimWorld 1.6 / Odyssey). "Crashed Factory ship / Jawa stowaways" theme. Governed by the anti-exponential principle: the gravship + VFE-Factory are the ONLY scalable progression trees._

**Created:** 2026-08-03
**Status of the old open item** ("author a fixed Jawa xenotype if none exists"): **HALF-CLOSED.** A Jawa xenotype already ships in **Outer Rim Galactic Diversity 1.6** (`OuterRim_Jawa`), verified from local source. No authoring needed — the work is evaluation + a religion pairing, both below.

**Evidence tags used throughout:** ✅ verified from local source · �claim inferred (reasoning stated) · 🔎 needs in-game/source confirmation. Where I mark something inferred, I say what would confirm it.

---

## Part 1 — The Jawa Xenotype (evaluate, don't author)

### 1.1 What actually ships (✅ verified from source)

Read from `mod_sources/Outer-Rim-Galactic-Diversity-main/1.6/Defs/GeneDefs/Xenotype_Jawa.xml`:

```
XenotypeDef defName = OuterRim_Jawa
label = jawa
inheritable = true
combatPowerFactor = 1.0
iconPath = OuterRim/XenotypeIcons/Xenotype_Jawa
genes:
  Skin_InkBlack          (cosmetic — near-black skin)
  Hair_BaldOnly          (cosmetic — restricts to bald; hood-friendly)
  Beard_NoBeardOnly      (cosmetic — no beard)
  DarkVision             (no dark/light work-speed & move penalty)
  MaxTemp_SmallIncrease  (raises heat tolerance a little)
  Outland_Eye_Orange     (cosmetic — the glowing orange eyes)
  Outland_BodyScale_Small(small body / short stature)
  Outland_Pos1Metabolism (+1 metabolic efficiency → lower hunger rate)
```

It also ships **two pawnkinds** — `OuterRim_Jawa` (colony) and `OuterRim_JawaTribal` (tribal) — both at 999 xenotype-chance, i.e. always Jawa. Useful if you want tribal-flavored Jawa raiders/traders as well as industrial ones.

**Provenance note (updated 2026-08-03):** the three `Outland_*` genes belong to the **Outland Genetics** dependency (the Biotech gene library Galactic Diversity requires). **Status: ACCEPTED (pending in-game verification).** The GitHub repo (`O21-Outland/Outland-Genetics`) was pulled twice and confirmed **stale — only 1.4/1.5 folders**; the 1.6 build exists **only on the Steam Workshop** (WS 2910172297, changelog line "Updated to support 1.6"). So the exact stat magnitudes of `Outland_BodyScale_Small` and `Outland_Pos1Metabolism` **cannot be read from source** and remain **inferred from vanilla-equivalent conventions** — to be confirmed once the mod is actually installed (see the in-game verification checklist). `Outland_Eye_Orange` is cosmetic and safe regardless. Do NOT re-pull from GitHub — it won't help. The rest of the genes are vanilla Biotech.

### 1.2 Mechanical read (what it does to a colonist)

| Gene | Effect | Type |
|---|---|---|
| `Outland_BodyScale_Small` | Smaller body → ⚠️ typically **less carrying capacity, lower melee damage, smaller shooting/HP hitbox** (harder to hit). In vanilla the analogous effect is the Biotech "Body size" gene. Exact number: 🔎 confirm from Outland source. | trait-shaping |
| `Outland_Pos1Metabolism` | **+1 metabolic efficiency → eats less / hunger falls slower.** Directly on-theme (desert-frugal scavengers) and a scarcity-friendly bonus (less food pressure per Jawa). | mild buff |
| `DarkVision` | Removes the dark-work and dark-move penalties. Great for ruin-crawling and night raids; fits "burrow into vaults." | quality-of-life buff |
| `MaxTemp_SmallIncrease` | Small rise in max comfortable temperature. Partial desert adaptation. | mild buff |
| `Skin_InkBlack`, `Hair_BaldOnly`, `Beard_NoBeardOnly`, `Outland_Eye_Orange` | Pure cosmetics that produce the hooded-silhouette-with-orange-eyes look. | cosmetic |

**Net:** a small, frugal, dark-adapted, mildly heat-tolerant humanoid with a slight melee/carry penalty. Combat power factor 1.0 means the game doesn't treat them as inherently stronger or weaker for raid-point math.

### 1.3 Pillar fit (the 7-question test)

The xenotype is **fixed identity, not a progression system**, so it passes trivially — but here's the explicit read against your test:

- **Parallel ladder? No.** A xenotype is a fixed per-pawn trait set. As long as you honor the campaign's existing "genetics lab FORBIDDEN — xenotypes welcome but FIXED, no extractors/assemblers/xenogerms/breeding-for-genes" rule, there's no scaling loop. The Jawa genes are inherited (`inheritable=true`), which is fine — that's just heredity, not an optimization economy.
- **Trivializes scarcity? Slightly *helps* it, cleanly.** `+1 metabolism` reduces food pressure a little, and `MaxTemp` + `DarkVision` reduce environmental friction. None of these bypass fuel, deck space, or the "what to leave behind" decision. They make the *crew* fit the *fiction*, not the economy easier.
- **Makes the ship less necessary? No.** If anything the small-body carry penalty makes hauling/logistics marginally *harder*, reinforcing mobility-and-scarcity tension.

**Verdict: KEEP AS-IS.** It's well-designed for the theme and pillar-clean. Do not author a custom replacement.

### 1.4 Optional refinements (only if you want them — all are taste, not necessity)

1. **Add a heat/thirst *liability* to deepen the desert-crew fiction.** Your docs already decided "water scarcity as narrative — Jawa heat/thirst liability + rationing precept + RP" (context.md, forbidden_mods.md). The shipped xenotype currently leans *comfortable* in heat (`MaxTemp_SmallIncrease`), which is slightly the opposite of a thirst *liability*. Two clean ways to reconcile:
   - **(a, recommended) Keep the gene, move the liability to ideology + RP.** Jawa aren't heat-*weak* in canon — they thrive on Tatooine. The "thirst" tension belongs in the *rationing precept* and roleplay, not a biological penalty. This keeps the shipped xenotype untouched (zero patch) and is the more lore-accurate reading.
   - **(b) If you want a mechanical bite:** add a *water/thirst* need via RP-only rationing rules rather than a gene edit — you already ruled out Dubs Bad Hygiene, so there's no clean thirst-need mod anyway. Skip biological penalties; they'd fight the canon.
2. **Body-size spectrum you already wanted.** Your notes flag adding dedicated large + small race mods so body-size genes are richly in the pool (Big and Small / RedMattis was the candidate). The Jawa's `Outland_BodyScale_Small` already surfaces the small end; no action needed unless you want the *full* spectrum for other species.
3. **Nothing else.** Resist adding "Jawa" genes for cleverness/utility — that drifts toward gene-shopping, which the pillars discourage.

### 1.5 Dependencies to confirm at build time (🔎)

Galactic Diversity's Jawa needs **Biotech** (vanilla genes) + **Outland Genetics** (the `Outland_*` genes) + **HAR** + Outer Rim Core. All are already in your adopted stack per the campaign docs — just verify Outland Genetics is actually subscribed and 1.6-current, since the Jawa def hard-references its genes and will error red if it's missing.

---

## Part 2 — The Jawa Ideoligion (buildable spec)

### 2.0 Ground rules this spec obeys (from your existing docs)

Your campaign already locked an ideology philosophy — this spec is built to fit it, not override it:

- **FIXED ideology**, no fluid development (no dev points, no meme-adding-over-time). _(forbidden_mods.md)_
- **No production/combat specialist roles.** Leader + a moral-guide role are fine; nothing that multiplies research/shooting/crafting/plants/medical. _(forbidden_mods.md)_
- **Rituals = cohesion, not material rewards.** No ritual-generated recruits/goodwill/quest-sites/artifacts/psylinks. _(forbidden_mods.md)_
- **≤ 1 relic** of modest mechanical value. _(context.md)_
- **No Transhumanist meme / no routine biosculpting.** _(forbidden_mods.md)_
- **The Force / psycasts are FORBIDDEN** — so this is a *secular animist scrapper culture*, NOT a Force faith. _(required_mods.md, forbidden_mods.md)_
- **Water scarcity is narrative** — a rationing precept + RP, not plumbing. _(forbidden_mods.md)_

Working name for the ideoligion: **"The Articles of Passage"** (your existing phrase) — or in-fiction, **"The Keepers of the Second Hand"** (Jawa reverence for discarded machines given a second life). Pick either as the ideoligion name in the creator.

### 2.1 Meme structure (RimWorld has a meme-slot budget — usually 2–4 depending on complexity setting)

Memes are the load-bearing choice. Recommended set, in priority order:

1. **Tunneler** — _primary structural meme._
   - Why it fits better than you'd expect: Tunneler culture values **darkness, being underground/enclosed, and disvalues open sky.** Jawa live in sandcrawlers and burrow through ruins; `DarkVision` makes them literally good at it. It also gives a clean identity ("we belong inside the hull / inside the ruin, not under open sky") that reinforces the ship-as-home fiction.
   - ⚠️ Trade-off: Tunneler brings a *mood penalty for being outdoors / liking darkness*, which can bite on surface expeditions. That's actually **desirable friction** for your pillars (expeditions should cost something), but flag it as a deliberate choice, not an accident.
   - **Alternative if Tunneler feels too punishing:** **Nomad** (values frequent moving, disvalues long settlement) — extremely on-theme for a mobile scavenger crawler and pairs perfectly with the gravship. Nomad is the "safe" primary; Tunneler is the "flavorful" primary. _(See §2.6 for the pick.)_

2. **Raider** OR **Rancher** — _skip both._ Neither fits Jawa (not conquest-raiders, not herders). Listed only to say: don't take them.

3. **Pain Is Virtue / Nudism / Blindsight / Tree Connection etc.** — _skip._ Off-theme.

4. **Recommended second meme: Nomad** (if Tunneler is primary) **or** a light-touch meme like **Loyalist** (values authority/leader, disvalues social-fight) to model tight clan hierarchy under a chief.
   - **Nomad + Tunneler** is the strongest pure-theme pairing: "we are a burrowing people who never stop moving" = a sandcrawler in space. The two memes don't mechanically conflict; they stack identity.

5. **Explicitly AVOID:** **Transhumanist** (banned by your rules), **Bo016 / Progressivism-flavored "high tech good"** memes (drifts toward the tech-ceiling you constrain), **Supremacist/Xenophobe** (you *want* a heterogeneous galaxy of traders and reflavored species — a xenophobe meme would fight the "populated galaxy" design and the Empire-fusion cast).

**Recommended final meme set: `Nomad` (primary) + `Tunneler` (secondary).** Rationale in §2.6.

### 2.2 Precept-by-precept build

RimWorld precepts are grouped by category. Below is a concrete pick for each meaningful category, with the *reason* and a *pillar check*. Where a precept has intensity tiers, I name the tier.

**Scavenging / property / work identity (the heart of a Jawa faith):**

- **Raiding/looting → not applicable** (no Raider meme). Instead lean on:
- **Ancient ruins / relics:** set **"Ancient complexes: Revered"** or the closest available "exploration is holy" precept if your mod set adds one. In vanilla the nearest lever is a **role/ritual around ruins** (see §2.3). Fiction: entering a vault to reclaim machines is a *pilgrimage*, not mere looting.
- **Charity / trade:** Jawa are obsessive traders. Set **Trade-relevant precepts permissive/positive** — do NOT take precepts that make selling to outsiders taboo. This dovetails with your frequent-heterogeneous-trader plan (traders are the economic spine now that the slingshot is gone).

**Consumption / scarcity (your water-narrative hook):**

- **Water/food rationing precept:** vanilla doesn't have a literal "water" precept, so implement rationing as **RP + a food precept**: take **"Nutrition paste: Preferred/Acceptable"** and a low-expectations posture so the crew tolerates lean rations without mood collapse. Fiction = "the ration is sacred; waste is sin."
- **Cannibalism / corpses:** ⚠️ judgment call. Jawa scavenge *machines*, not flesh — recommend **cannibalism: Abhorrent** (keeps them from feeling like ghouls) but **"Machining/scavenging corpses of DROIDS"** framed as fine. There's no vanilla "droid-corpse" precept, so this is RP: strip mechanoids/droids freely, treat organic cannibalism as taboo.

**Aesthetics / apparel (cheap, high-flavor):**

- **Apparel — Desired:** the Outer Rim Core garb gives you real defNames (✅ verified): `OuterRim_DesertGarb`, `OuterRim_DesertHood`, `OuterRim_Cloak`, `OuterRim_Hood`. If your Ideology apparel-requirement precept can point at these (via a style or a "desired apparel" mod), set **hooded/cloaked as the expected look**. Otherwise enforce via RP + colonist outfit policy. This produces the iconic hooded silhouette and pairs with `Hair_BaldOnly`.
- **Style:** if you run a style mod or the vanilla style system, bias toward **rough/spacer/tribal salvage** aesthetics, not spacer-chic.

**Social structure:**

- **Leader title:** **"Chief"** or **"Captain"** (your docs already say Captain + a moral-guide role are allowed). This is the clan/ship head.
- **Skill passions / role veneration:** ⚠️ **do NOT take precepts that venerate a production skill** in a way that creates a specialist economy — that bumps the no-specialist rule. Venerating *crafting* as an identity is fine as flavor; a *Production Specialist role* is not. Keep it identity, not multiplier.

**Taboos that reinforce the theme (all cheap, all cohesion-not-material):**

- **"Automation reverence, not automation dependence":** RP precept — droids/mechs are *revered relics to be repaired*, not mass-produced. This is the ideological spine of the anti-exponential principle expressed as faith: **"We give the second hand to what others discarded; we do not breed new hands."** Mechanically nudges you away from Droid Depot mass-production (which your docs already self-limit).

**Precepts to explicitly leave neutral/off:**

- Anything granting **ritual material rewards, recruits, or goodwill** → off (violates your ritual rule).
- **Biosculpting/bionics veneration** → off (Transhumanist-adjacent; your bionics are salvage/quest-earned rare).
- **Skull-spike / execution / slavery intensity precepts** → taste; default off unless you want a darker Jawa clan. (Slavery is arguably on-theme for a scrapper culture that "acquires" labor, but it adds management surface — recommend off for a first campaign.)

### 2.3 Roles (keep it to two — both non-multiplying)

RimWorld Ideology roles are where the "no specialist" rule matters most. Take **only**:

1. **Leader role → "Chief" / "Captain."** Vanilla Leader role. Its abilities are morale/social (Work Drive, etc.), not production multipliers — acceptable, and you likely want the leadership abilities for a small crew. ⚠️ If you're being *strict*, even the Leader's work-speed-buff ability edges toward "multiply production." Recommend: **take the Leader role but treat its production-buff ability as off-limits by self-restraint** (same discipline shape as Droid Depot / Ancient Mining), OR pick the Leader's social/mood abilities only.
2. **Moral Guide role → "Keeper of the Articles" / "Rememberer."** Vanilla Moral Guide. Its role is *conversion/proselytizing/preaching* = identity and cohesion, not economy. **Clean fit.** This is your "constitution enforcer."

**Do NOT take:** the **Production Specialist**, **Combat/Skullspike specialists**, or any modded role that multiplies a work type. The flagged mod **"Ideology Scavenger Role" (WS 3565039115)** is a *great flavor model* — its "walk, burrow, pry, carry, flee, endure; don't craft or store knowledge" ethos is pure Jawa — but ⚠️ **evaluate it carefully before adopting**: if it grants work-speed or acquisition *multipliers* it bumps the no-specialist rule; if it's purely a *restrictive identity role* (a set of taboos + appearance, no production buff) it's adoptable and excellent. 🔎 Read its def before installing. Even if you don't install it, **mine its precept text for RP flavor.**

### 2.4 Rituals (cohesion only — no material payouts)

Design rituals so their reward is **mood/cohesion/social**, never goods, recruits, or quest sites:

- **"The Reckoning" (salvage-return ceremony):** held when the ship completes a major salvage haul or launches to a new tile. Reward = a mood buff ("we honored the leaving / the taking"). Fiction: the crew formally decides *what to leave behind* — literally ritualizing your core pillar. This is the single most on-theme ritual you can build.
- **Funeral / machine-rites:** when a droid/mech is permanently destroyed, a "retirement of the second hand" observance. Mood cohesion only.
- **Leader-led speech / conversion rituals:** vanilla, fine — social cohesion.
- ⚠️ **Avoid** any ritual with an outcome table that yields items, silver, animals, recruits, or quest unlocks. If a modded ritual offers those, disable that outcome or skip the ritual.

### 2.5 The one relic (≤ 1, modest value)

Your docs cap this at one relic of modest mechanical value. Recommended:

- **"The First Fusioncutter"** (or "The Founding Ion Blaster") — a single named tool/weapon treated as the clan's founding relic. Modest stats, high sentimental/ideology value. Fiction: the tool the first Jawa used to open the crashed Factory ship's hull. If you want zero mechanical creep, make it a **cosmetic/low-value melee tool** rather than a strong weapon — the *meaning* is the point, not the damage.
- ⚠️ Do not stack multiple relics or a relic that grants a strong buff — that reintroduces a mini-progression reward.

### 2.6 Recommended final build (the "just tell me what to pick" summary)

> **Ideoligion name:** The Articles of Passage _(in-fiction: Keepers of the Second Hand)_
> **Structure:** Fixed (no fluid development)
> **Memes:** **Nomad** (primary) + **Tunneler** (secondary)
> **Leader:** Chief / Captain (Leader role; self-limit its production-buff ability)
> **Moral guide:** Keeper of the Articles (Moral Guide role)
> **Signature precepts:** ruins-as-pilgrimage; trade permissive/celebrated; ration-as-sacred (nutrition paste acceptable + low expectations); organic cannibalism abhorrent but droid-salvage free; hooded/cloaked desired apparel (`OuterRim_DesertGarb`/`_DesertHood`/`_Cloak`/`_Hood`); "repair the discarded, don't mass-produce new hands" (automation reverence).
> **Rituals:** The Reckoning (salvage/launch cohesion rite); machine-retirement funeral; leader speeches. **No material-reward rituals.**
> **Relic:** one — The First Fusioncutter (modest/cosmetic).
> **Banned by design:** Transhumanist meme, production/combat specialist roles, fluid development, Force/psycast anything, ritual loot payouts.

**Why Nomad-primary over Tunneler-primary:** Nomad is the cleaner mechanical fit for a *mobile gravship* (it rewards the thing you'll do constantly — move) and carries less risk of chronic mood penalties than Tunneler's outdoor/darkness aversion, which fights against surface expeditions you *need* to run. Tunneler as secondary still delivers the burrowing-scavenger flavor and leverages `DarkVision`. If you'd rather maximize flavor and accept the expedition mood-tax as deliberate friction, swap them (Tunneler primary, Nomad secondary) — both are pillar-legal.

### 2.7 Comedy-via-precepts — strange scrapper behavior (user greenlit 2026-08-05)

The user **loves the ideoligion-expansion route as the home for Jawa comedy** — the belief system is where the humor becomes *diegetic* ("these little guys genuinely worship working machinery") rather than a bolted-on gag. This slots directly onto the "automation reverence" spine already in §2.2 and the meme-expansion mods promoted in `required_mods.md` (🃏 COMEDY / LEVITY LAYER). Design intent: use extra precept slots from **meme-expansion mods (Alpha Memes / More Memes-type, 🔎 1.6 confirm via Fetcher `2026-08-05_jawa_flavor_confirm_1p6`)** to hang *charming scrapper gags* that stay pillar-clean —

- **Reverence for scrap / functional machinery** — a "the working part is sacred" precept; wasting a repairable component is sin (reinforces "repair the discarded, don't breed new hands").
- **Haggling as ritual** — trade isn't just permitted, it's a *devotional act*; a bad trade is a minor moral failing. Compounds the frequent-heterogeneous-trader plan.
- **Droid veneration** — functional droids treated as revered relics (funeral rites for a dead droid; §2.4 machine-retirement funeral already exists — lean comedic here).
- **Junk-hoarding taboos** — taboo on discarding "still-good" scrap; comedic clutter as faith.

**Guardrail (unchanged):** comedic precepts must remain *identity/mood* flavor — no precept may grant a production multiplier, specialist role, ritual material payout, or fluid-development hook (§2.0 / §2.2 rules still bind). The joke is that they *worship* scrap, not that worship *manufactures* scrap. Any meme-expansion mod adopted gets the same 7-question pass as everything else; we take the precept *slots + flavor*, not any economic precept the pack ships.

---

## Part 3 — Decision translation

**Decision this doc supports:** adopt the shipped `OuterRim_Jawa` xenotype unchanged; build a fixed "Articles of Passage" ideoligion on **Nomad + Tunneler** with two non-multiplying roles, cohesion-only rituals, and one modest relic.

**Viable alternatives:**
- Xenotype: author a custom Jawa (rejected — the shipped one is clean and pillar-fit; authoring is wasted effort and a maintenance burden).
- Memes: Tunneler-primary (more flavor, more mood-tax) or a single-meme Nomad build (simplest, least identity).
- Religion depth: run it as pure RP with no formal ideoligion (rejected here since you asked for a buildable spec, but valid — Ideology is optional).

**Tradeoffs:** Nomad+Tunneler maximizes theme but Tunneler's darkness/outdoor aversion taxes surface expeditions — deliberate friction that fits the pillars but will occasionally cost mood. The no-specialist discipline means passing up Ideology's economic multipliers (that's the point).

**Dependencies:** Ideology DLC (present); Biotech + Outland Genetics + HAR + Outer Rim Core for the xenotype (🔎 confirm Outland Genetics subscribed + 1.6-current — the Jawa def hard-references its genes).

**Principal risks:** (1) Outland Genetics missing/stale → red errors on the Jawa def (🔎 verify at build). (2) A modded ritual or role sneaking in a material reward or production multiplier → re-check each against the no-specialist / no-ritual-loot rules. (3) `Outland_BodyScale_Small` combat/carry penalty magnitude unknown → could be more punishing than expected (Fetcher filed to ground it).

**Missing info (being gathered):** exact biostats of `Outland_BodyScale_Small` / `Outland_Pos1Metabolism` / `Outland_Eye_Orange` — Fetcher `2026-08-03_outland_genetics_source` filed. And 🔎 whether the "Ideology Scavenger Role" mod (WS 3565039115) is a restrictive-identity role (adoptable) or a multiplier (rejectable) — read its def before installing.

**Recommended next steps:** (1) at build time, confirm Outland Genetics is loaded and the Jawa def resolves clean in a dev world; (2) build the ideoligion in the Ideology creator per §2.6; (3) decide Nomad-primary vs Tunneler-primary once you know how expedition-heavy the playstyle feels; (4) when the Outland Genetics Fetcher lands, update §1.2's inferred stat magnitudes to verified.

---

## Part 4 — Jawa Society: slavery, reproduction, and the life-cycle (user lore, 2026-08-04)

_These rules define how the clan grows, acquires labor, and disposes of it. They are a tightly interlocking system — the reproduction engine and the aging/exile sink are a **matched pair** that MUST be balanced together (see §4.5, the pillar analysis). This part OVERRIDES the earlier §2.2 note that recommended leaving slavery off "for a first campaign" — slavery is now a **core, load-bearing** part of the Jawa identity, not optional._

### 4.1 The clan boundary — no recruitment, only clan-birth or love

The defining social rule: **the Jawa clan does not recruit. Membership comes from exactly two sources — being hatched into the clan (§4.3), or a slave earning acceptance through love (§4.2).** There is no "prisoner → talked into joining" path. Fiction: the Clan is kin and covenant, not a hiring hall; an outsider cannot simply be *persuaded* to belong.

- **Mechanic:** RP-enforced first — **never use the "Recruit" option on a prisoner; only "Enslave."** 🔎 Fetcher filed to check whether a mod cleanly *removes* the recruit interaction for a faction/ideoligion (so the rule can't be violated by a stray click); if none exists, this stays an RP discipline (easy — it's a single UI choice you just don't make).
- **Ideology hook:** take a **Slavery precept = Acceptable or Honorable** (Ideology DLC) so enslaving carries no mood penalty and slave-owning is normalized. This is the precept that §2.2 previously left off — now ON.

### 4.2 Non-Jawa vs other-clan Jawa slaves — two different fates

The clan enslaves **anyone outside the Clan**, but what happens next depends on *what* they are:

- **Non-Jawa slaves → sold as soon as possible.** They may be worked as slave labor in the interim, but they are **inventory, not future members** — the intent is always to sell them to the next trader. This dovetails perfectly with the frequent-heterogeneous-trader economy (the Hutt cartel of `desert_world_design.md` §4 is the natural buyer — and the "sells your own kind" tension is good fiction). *Mechanic:* pure RP + the slave-trade system; no mod needed. Slaves already do forced labor and are sellable to slavers/traders in vanilla Ideology.
- **Other-clan Jawa slaves → may earn Clan acceptance, but ONLY through love.** A Jawa taken from a *different* clan can, over time, become a full member — but the sole gateway is **an existing clan member falling in love with them.** Romance is the naturalization ceremony. *Mechanic:* RP-gated — you only free-and-accept a Jawa slave into the colony once a romantic relationship has formed with a colonist. ⚠️ **Feasibility flag:** vanilla RimWorld restricts slave social/romance interactions, so a colonist spontaneously romancing a slave may be rare or blocked. Routes if the organic path is too rare: (a) accept it's rare-by-design (love is precious — very on-theme); (b) a mod that enables slave romance; (c) **RimMaster/RimBridge or a Tier-2 save-edit to author the romance + freeing** when the story calls for it (this is exactly the kind of narrative beat the enrichment tooling exists for). 🔎 Fetcher checking for a slave-romance-enabling mod.

### 4.3 Reproduction — all-male, homosexual, egg-laying, fast-growing

The clan's growth engine (this is the reason recruitment isn't needed):

- **All Jawa are male and homosexual.** *Mechanic:* force male pawn generation + the Biotech **Gay gene** (or equivalent) in the xenotype/pawnkind. Forcing 100% male at generation may need a pawnkind `<fixedGender>Male` patch or a mod; 🔎 confirm the cleanest route.
- **Male–male "pregnancy" producing eggs.** Two males can conceive; the result is an **egg** that is laid, then **hatches a baby Jawa.** *Mechanic:* needs a **same-sex/male-pregnancy mod + an egg-laying (oviparous) birth mod or gene.** 🔎 Fetcher filed for both — this is the single most mod-dependent piece of the whole design; if no clean 1.6 combo exists, fallbacks are (a) egg-laying via a Biotech-style custom gene, (b) a HAR reproduction hook, or (c) narrative-only with dev/RimBridge-spawned "hatchling" pawns.
- **Exceedingly fast growth to adulthood.** *Mechanic:* Biotech growth/age-rate genes (accelerated growth vats-free, or a custom lifespan gene). Biotech already models child growth stages and has age-factor genes → likely a clean gene edit. 🔎 confirm magnitude.

### 4.4 Rapid aging + the exile of the spent

The counterweight to fast breeding: **Jawa age rapidly**, and when one is **too old or too badly injured to benefit the clan beyond the resources it consumes, there is a societally acceptable banishment/exile.** The infirm are not murdered in anger — they are *released from the covenant* when they become a net drain. Fiction: a harsh scarcity ethic where the clan's survival outranks the individual's.

- **Rapid aging mechanic:** a lifespan/age-rate gene (Biotech or modded) that shortens the productive span and brings on age-decline fast.
- **Exile mechanic:** RP-driven **banishment** (caravan the pawn away / "release" them) framed as an accepted rite, ideally paired with a **ritual or precept that removes the mood penalty** for sending off the aged/infirm (so the colony doesn't grieve a *correct* act). 🔎 vanilla has no clean "euthanize/exile elder" precept; check whether an Ideology precept or a mod supports "banishment as honorable," else it's a ritual we author + RP. *Anomaly-free* — do not reach for Anomaly mechanics (benched).

### 4.5 PILLAR ANALYSIS — why this is anti-exponential-SAFE (the crucial read)

At first glance "fast reproduction + fast growth" looks like an **exponential population/labor engine** — the exact thing the pillars forbid. It is not, **and the reason is structural: this is a churn system, not a growth system.** The design has three built-in sinks that hold population at a rough steady state rather than letting it compound:

1. **Rapid aging + exile of the spent (§4.4)** — the death/removal rate scales *with* the population (more Jawa → more reaching the exile threshold), which is precisely the negative-feedback term that turns exponential growth into a bounded equilibrium.
2. **No recruitment (§4.1)** — the clan can't *also* bolt on outsiders to accelerate; growth is capped to the birth rate alone.
3. **Gravship deck space + food scarcity + the desert-world threat/scarcity axes** — a mobile crawler has hard room/nutrition limits, and `desert_world_design.md`'s water/heat threat axes (④) punish an oversized crew. The environment itself caps headcount.

**So the matched pair (fast birth ⇄ fast death/exile) is the whole point — and it must be TUNED as a pair.** The pillar-safety is *conditional*: if reproduction is fast but the aging/exile sink is weak or forgotten, it becomes a genuine exponential violation (a labor army that trivializes scarcity). Conversely, this churn actually *reinforces* the pillars — it produces constant hard "who do we keep, who do we let go" scarcity decisions (the emotional core of the campaign, at the population level) and it means the clan is **demographically unable to snowball into a mega-colony**, so mobility stays necessary. Verdict: **✅ pillar-safe AS A SYSTEM, conditional on the sink being tuned to match the source.** Flag for Phase-A playtest: watch the population curve; if it trends up unbounded, strengthen aging/exile; if it collapses, soften them.

### 4.6 Implementation summary & feasibility ladder

| Rule | Cleanest mechanic | Feasibility | Route |
|---|---|---|---|
| No recruit, only enslave | RP (don't click Recruit) + Slavery: Acceptable/Honorable precept | ✅ trivial (RP + vanilla precept) | CONFIG/RP; 🔎 mod to *hard-remove* recruit is a bonus |
| Sell non-Jawa slaves | RP + vanilla slave trade (Hutt buyer) | ✅ trivial | RP/CONFIG |
| Other-clan Jawa → clan via love | RP-gate freeing on a romance | ⚠️ vanilla limits slave romance | RP + 🔎 slave-romance mod, else AUTHOR (RimBridge/save-edit the beat) |
| All-male + homosexual | fixedGender Male + Gay gene | 🔎 likely clean (gene + pawnkind patch) | MOD/patch |
| Male-male egg-laying birth | same-sex-preg + oviparous-birth mod/gene | ⚠️ **most mod-dependent** | MOD (Fetcher); fallbacks = custom gene / HAR hook / authored hatchlings |
| Fast growth | Biotech growth/age-rate gene | 🔎 likely clean | MOD/gene |
| Rapid aging | lifespan/age-rate gene | 🔎 likely clean | MOD/gene |
| Honorable exile of the spent | ritual/precept + RP banishment | 🔎 no clean vanilla precept | AUTHOR ritual + RP |

**Evidence tags:** all rows are **user-specified lore** (established as design intent). The *mechanics* are **reasoned inference** about the cleanest route; every 🔎 is a to-be-verified mod/def question now in Fetcher `2026-08-04_terrain_treasures_and_jawa_lore`. Nothing is asserted as confirmed-buildable yet. The pillar analysis (§4.5) is **reasoned inference** and its balance is **speculation pending playtest** (flagged as such).

### 4.7 "Salvage-debt" crew rotation — a PARKED alternate churn model (◇ my concept, autonomy sweep 2026-08-05; OPEN, deferred to user)

*Promoted from autonomy.md so it isn't lost, but flagged as **in tension** with the established kin-only clan rule (§4.1) — do not treat as decided.* The idea: instead of (or alongside) the birth⇄exile demographic churn, tie crew turnover to the *scavenging* fiction via a **claim/obligation rhythm** — a pawn joins the ship as a *debt-passage* (you salvaged something they needed, or pulled them off a fouled tile) and **leaves when the obligation is discharged**, taking a cut of salvage and departing at the next trade contact. Net headcount stays flat by design (pillar-safe: not a growth ladder), but *who* is aboard rotates, so a skill you rely on can walk away and force adaptation — the "decide what to leave behind" pillar applied to *people*, not cargo.

**Why it's PARKED, not adopted:** it collides head-on with §4.1 ("the Jawa clan does not recruit; membership is kin-birth or a slave earning love"). A rotating debt-passage crew implies *taking on non-kin members*, which the current lore forbids. **Two ways to reconcile if the user ever wants this:** (a) make the debt-passengers explicitly **non-clan passengers/guests** (not clan members) — hitchhikers the clan ferries and drops off, distinct from the kin roster, which preserves §4.1; or (b) treat it as a **rival-Jawa-clan** mechanic (§4.2's other-clan Jawa), where debt-bonded outsiders can only become kin via the love-gate, otherwise they leave. **Implementation (review-only):** authorable with existing sanctioned tools — ideology precept (departure as honorable, not desertion) + RimMaster-scripted "obligation discharged, pawn leaves with caravan" events; a dedicated mod is likely *not* needed (and a recruitment-*expanding* mod would fail the 7-Q). **Evidence:** ◇ my design proposal; the pillar-safety is reasoned inference; the §4.1 conflict is established. **→ Open question for user:** keep crew churn purely demographic (birth⇄exile, §4.3–4.5), or layer in a non-kin salvage-debt passenger rotation? (This is the "crew-churn model: mechanical vs roleplay" item flagged open in `context.md` 2026-08-05.)
