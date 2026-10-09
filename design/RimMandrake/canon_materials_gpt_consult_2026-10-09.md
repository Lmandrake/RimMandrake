# GPT consult (gpt-6.1-sol, high) on canon_materials_design_2026-10-09.md — 2026-10-09, verbatim answer

Regenerated after the owner ruled plasteel its own canon material (no plasteel = durasteel equivalence). Question file: asked for a check of the plasteel/durasteel/plastoid split, the donor-durasteel dispositions, critique and repair of D1–D3, three designs of its own kept alive, roster advice, a review ranking, and card-ready owner questions.

The split is viable, but **separate identities do not yet produce separate gameplay**. Keep Core `Plasteel`; consolidate durasteel independently; give plastoid sealed-equipment consumers. Several claims need qualification, and D3 currently contradicts the ruled sourcing of doonium.

This review accepts the supplied measurements; it does not claim to have tested the live mod set.

**The split: what breaks in play**

| Issue | Failure in play | Concrete repair |
|---|---|---|
| **Stuff eligibility** | Plasteel’s `Metallic` category permits ordinary metallic stuff uses. If durasteel shares it, players can still build plasteel walls and wear durasteel armor. Labels cannot enforce “Shape/Hold.” | Keep generic construction permissive if these are preferences. For exclusive campaign jobs, use restricted stuff categories or fixed ingredient lists; adding a special category while retaining generic `Metallic` does not exclude generic consumers. |
| **Mass** | `statBases/Mass` measures resource-stack weight. Plasteel’s 0.25 versus durasteel’s 0.675 does **not itself** make finished armor lighter or heavier. The principal carried-gear distinction may disappear. | Give dedicated gear explicit masses, or add appropriate stuff mass factors. Weight alone also does not establish a movement penalty. Core plasteel stats can remain unchanged if dedicated products supply the distinction. [Game stat calculation](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/StatWorker.cs). |
| **Armor numbers** | The listed armor values are stuff armor powers, not universal final armor ratings. Fixed-cost armor, implants and droids need not inherit them. Heat protection also does not necessarily resist donor blasters. | Relabel §1a with the actual stat names; inspect each consumer’s stuff-effect multiplier and each blaster’s damage category. Test finished products against representative weapons. [Stuff armor calculation](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/StatPart_Stuff.cs). |
| **Durasteel’s advantage** | Its HP factor is only about 7% above plasteel’s, although it costs substantially less and takes less work. Its sharp armor power is below steel’s. “More resistant than steel” will disappoint against sharp-category gunfire. | Describe it as economical structural toughness. Either raise its sharp protection to at least steel’s or explicitly present the blunt/heat specialization as campaign balancing. |
| **Plastoid sealing** | Making a helmet or wall from plastoid cannot automatically create gas, toxin or vacuum protection. A plastoid club should not confer environmental resistance. | Put protection on sealed suits, helmets and their equipment rules. Separate apparel protection from Odyssey building airtightness. Verify plastoid’s actual categories and stats; they were not measured here. |

**Recipe substitution needs two separate audits.** Keep fixed `Plasteel` costs where the consumer needs plasteel; redirect only identified durasteel references. Then audit generic stuff recipes and broad ingredient filters, which can admit both materials despite the statement that no recipe substitutes them. Fixed-cost advanced components and implants need explicit recipe decisions; input material stats do not automatically transfer into their products.

**Salvage needs composition, not name-based conversion.** `ShipChunk_durasteel` yielding plasteel is not inherently impossible—a wreck contains several materials—but its loot should explain that: durasteel plating, plasteel shells, components. Give B1 remains plasteel recovery without also paying the same shell through corpse processing and another wreck recipe. Audit smelting, shredding and deconstruction separately. Fabrication and recovery yields must prevent profitable material loops; cheap steel–chemfuel plasteel can otherwise erase scavenging scarcity.

**Odyssey requires an explicit allowlist.** Remove forbidden entries from both measured generation paths; zeroing ordinary mineable commonality alone may leave explicitly selected deposits. Audit surface veins, deep deposits, meteorites, quests and donor generators too. Orbital wreck salvage remains **S**, distinct from asteroid mining **A**. Gold, silver, jade and new precious commodities must obey their approved home-biome placement; “space” is not automatically a permitted home. Preserve legacy mineable defs for saves without permitting fresh generation.

**Canon fidelity**

The supplied examples support three distinct identities. They do **not** establish every proposed property:

- **Plasteel’s polymer–metal formulation is presented in the document’s Legends evidence.** §§2a/2c should identify “composite,” exceptional lightness and formability as campaign interpretations unless a canon source explicitly establishes them. “Shape” can mean precision fabrication, consistent with slow working; “easy to shape” would contradict the measured work factor.
- **Plastoid’s vacuum capability is overstated as a material property.** Complete stormtrooper equipment includes survival systems; bare plating does not establish a spacesuit. [Official stormtrooper description](https://www.starwars.com/databank/stormtroopers).
- **“Lightsaber-proof” phrik is too absolute.** Use “lightsaber-resistant.” Likewise, cortosis thought concealment should not become blanket immunity to Force powers.
- **Beskar’s weapon prohibition is a cultural restriction, not universal canon.** Its armor-only campaign role is legitimate, but canon also includes weapons and forge tools. Cortosis fragility supports specialization, not a universal strength ladder. [Official metals comparison](https://www.starwars.com/news/the-acolyte-cortosis-the-mandalorian-beskar).
- Coaxium’s cold-chain hazard should specify **raw** coaxium; distinguish refinement from fuel consumption. Asteroid sourcing and gravship-range effects are campaign proposals. [Official coaxium description](https://www.starwars.com/databank/coaxium).
- Zersium being critical to durasteel does not establish that it is the sole ingredient. Use zersium **plus steel** in a deliberately invented alloying recipe.

**Donor dispositions**

| Choice | Judgment | Save and tier consequences |
|---|---|---|
| **(a) Keep `KOTOR_AlloyDurasteel`** | **My pick:** existing stuff identity and processing chain minimize disruption. | Retains existing references to our alloy. Record its prefix as a legacy naming exception and assign clear tier ownership. Moving ownership must preserve availability and dependency order. |
| **(b) Create `RSW_Durasteel`** | Worthwhile if canon-tier dependency independence requires it; cosmetic naming alone is insufficient. | Requires migrating our existing alloy as well as donor stock and references. A clean prefix does not supply migration. |
| **(c) Leave donors** | Useful only as a temporary compatibility state. | Duplicate stacks, filters, stats and recipe eligibility persist; disabling mining does not stop trade, salvage or generated equipment. |

For **all three**, “old defs remain loadable” requires shipping compatibility definitions after donor-mod retirement. Loose-stack conversion recipes do not migrate building/gear `Stuff`, inventories, unfinished items, bills or saved filters. A save can load while retaining a fragmented economy.

Treat ore and alloy separately: verify what `LKDurasteel_Ore` actually represents before choosing conversion yields. Do not silently repurpose `KOTOR_MineableDurasteel` as zersium: existing deposits would change meaning. Prefer a new zersium vein with the old def retained as compatibility content.

**Repairs to the three existing designs**

| Design | Main critique | Concrete repair |
|---|---|---|
| **D1: ladder** | Duranium and doonium become numerical upgrades; “apex” hides three different combat behaviors. Its iron wording also obscures the ruled everywhere-iron deep drilling. | Make tiers gate **projects**, not universal superiority: duranium frames plus doonium reactor containment for appropriate large builds, with durasteel cladding and plasteel control/droid assemblies. Present beskar, phrik and cortosis as specialties. Clarify surface versus deep iron placement. |
| **D2: one job each** | Exclusivity is artificial: durasteel and duranium overlap at turret mounts, while many unique verbs require new systems. Transparisteel needs actual visibility behavior; coaxium needs a range hook. | Allow shared structural projects with different required parts. Give each launch material a named implemented consumer before adding it; defer unsupported verbs. Begin with the trio, ruled duranium/doonium and established kyber/tibanna systems. |
| **D3: provenance** | Origins are attractive but uses remain vague. Doonium in the A/T endgame contradicts salvage-first, rare trade; gravship-gated supplies can prevent building the first gravship. | Return doonium to offworld-manufactured **S first, rare T**, with orbital wrecks counted as S. Give every local ore one consumer and guarantee an accessible ground salvage route for first-ship necessities. |

Also fix the shared introduction: it names “five” channels before adding F. There are six.

**Three additional designs remain alive**

For these proposals, the common roster is **steel, plasteel, durasteel, plastoid, duranium, doonium, beskar, cortosis, kyber, tibanna and existing rhydonium**. Common channels: steel from L iron; plastoid F/S; duranium/doonium S with rare T; beskar S; cortosis S/T; kyber L Lantern Deeps; tibanna H; rhydonium its existing manufactured fuel chain.

| Alternative | Roster and placement | Origin channels | Main weakness |
|---|---|---|---|
| **E1: assemblies** | Common roster only. Materials cooperate within machines: **durasteel** outer structure, **plasteel** insulated housings/droid shells, duranium frame, doonium containment. Most rare metals are fixed ingredients rather than universal stuff. | Durasteel S/T, optional L zersium→F alloying; plasteel S/T and limited F. Reclaimed assemblies can be dismantled or installed directly. | Intermediate assemblies add bills and stockpile complexity; recipes can become shopping lists. |
| **E2: restoration** | Common roster plus **phrik and stygium**. The main reward is damaged equipment. **Plasteel** repairs droids and personal equipment; **durasteel** repairs doors, turrets and hulls. Rare materials restore specialist relic functions. | Plasteel/durasteel predominantly S, backed by T; phrik S/L Stillsand, stygium S/T. Existing-item restoration dominates new manufacture. | Players may feel denied creative construction; requires a substantial damaged-item catalogue. |
| **E3: industrial contracts** | Common roster plus **bronzium and aurodium**. **Durasteel** supports bulk construction orders; **plasteel** supports precision droid/prosthetic orders. Material demand follows buyers and contracts rather than progression or exclusive verbs. | Durasteel S/T plus optional local alloying; plasteel S/T, limited F. Bronzium F/T; aurodium T and approved home-biome traces. Duranium/doonium remain salvage-first. | Contract tuning can turn scavenging into repetitive quota work; purchase backstops may dominate expeditions. |

These are different governing loops: assembling systems, restoring finds, and supplying an economy.

**Roster discipline and review priority**

Fold **functions**, not canon identities: omit separate quadanium/alusteel/ferrocarbon commodities while durasteel covers ordinary structure. Duranium and doonium remain separate and required.

Defer transparisteel/lommite until windows work; stygium until cloaking works; coaxium/carbonite until fuel and preservation systems exist. Defer chromium, thorilide and dolovite until named consumers justify them. Fold hyperbaride, corusca and aurodium’s wealth function into existing trade rewards unless distinct demand warrants separate stacks. Bronzium can remain a small decorative branch.

Do not add the rejected exotic-metal list or promote agrinium/zersium name-only equipment into commodities merely because names exist.

Resolve generation leaks, recipe eligibility, migration and first-ship access first. **Design review order only:** D3 → E1 → D2 → E2 → D1 → E3, based on scavenger fit, clarity and implementation uncertainty. This is not a design selection.

1. Durasteel identity: **(a) legacy def** | **(b) new canon-tier def** | **(c) temporary donor coexistence**?
2. Material roles: **preferred uses with generic freedom** | **exclusive campaign consumers**?
3. Plasteel supply: **salvage/trade only** | **salvage/trade plus costly fabrication**?
4. Local durasteel: **zersium–steel alloying** | **salvage/trade only**?
5. New commodities: **implemented consumer required first** | **reserve selected dormant defs now**?
6. Next prototype: **D1** | **D2** | **D3** | **E1** | **E2** | **E3**?