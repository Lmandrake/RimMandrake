# The Webwork egg black market and the assassination quests (design draft)

_Fable design subagent, 2026-09-24. Ledger item: `WEBWORK_EGG_BLACKMARKET_1`._

**Status: DESIGN PROPOSAL. Nothing authored. Every mechanism below is PROPOSED unless it cites a
ruling; open calls are collected in §5.**

## READ FIRST

**The commission** is the owner's own typed words, recorded verbatim in
`webwork_owner_and_nest_2026-09-23.md` §6 ruling 5 (2026-09-24):

> *"Totally add the black market trader (likely hutt / bounty hunter faction related) and some
> quests that have opyionalnimmoral solutions to adsassinate someone by planting an egg in their
> room to hatch in the night."*

That sentence is the ONLY owner decision in this document. It establishes: (a) a black-market egg
trader exists, in the campaign layer; (b) it is likely Hutt / bounty-hunter faction related;
(c) quests exist with **optional immoral** solutions; (d) the named example is assassination by
planting an egg in the target's room to hatch in the night. Everything else below — every
mechanism, number, faction assignment and quest shape — is PROPOSED, and §5 collects the calls
that need his ruling.

**What binds this design:**

- `webwork_owner_and_nest_2026-09-23.md` — the sitting record. Especially §4a (the egg item
  `RM_OllathrixEgg`, deliberately **no `CompHatcher`** in the free tier — an egg that hatches is a
  tamed Ollathrix by the back door, ban 1), §4c (the carried-eggs mark), §4b (the offworld route),
  §6 rulings 2 (Wildsteam egg *bounty* — they pay to destroy), 3 (a nest on every map), 4 (a
  living nest re-lays every 20–30 days), and §0 ruling 2 (**ONE race, ONE kind** — no second
  `PawnKindDef` without an owner card).
- `design/RimMandrake/biome_mod_architecture.md` §7 **Q11/Q11a**: the tier line is IP provenance.
  "Hutt", "Gamorrean", "Blackstar-as-bounty-hunter-outfit" are Star Wars IP, so **nothing in this
  document touches the `RM_` tier**. The free-tier Webwork and its egg are complete without any of
  this (sitting §4b: sell to the sky); this design is pure campaign-side addition on top.
- `skills/rimworld-quests/SKILL.md` — quest specs are written prose-first (§2's six-line spec and
  ten questions), defs are the second half and are not authored here. Convention copied from
  `design/Jawa/quests/cathedral_surveyor_misdirection_quest.md`: **no defNames are coined** — every
  `<RUT_...>` token below is a placeholder that binds at build time under
  `design/NAMING_SCHEME_PLAN.md`.
- `design/Jawa/worldbuilding/FACTION_SPEC.md` — the campaign factions named below: **Hutt Cartel**
  (`Jawa_HuttCartel`, §2 — transactional, owns the oases and the only non-Imperial orbital node,
  ideo *the Reckoning of Debts*, `permanentEnemy false`, high caravan frequency), **Blackstar
  Company** (§10 — the bounty hunters: "one dangerous person with a name", vanilla `Pirate` reskin,
  🔴 `permanentEnemy true` stands by R12), **Wildsteam Clan** (§6 — *the Green Oath*, reveres
  living ecosystems; the mandible- and egg-bounty payers).
- Worked precedent for the campaign trade machinery:
  `src/RimUtinni/ShokkweaveEconomy/Patches/ShokkweaveTraderStrip.xml` (the sole-source strip, with
  its MEASURED engine finding restated in §1c below) and
  `src/RimUtinni/UtinniPatches/Defs/TraderKindDefs/RUT_HuttCartel_Captives.xml` (a dedicated
  Hutt-Cartel TraderKindDef already ships — this design copies that shape).

## §1 The trader

### 1a. Who runs it — PROPOSED: the Hutt Cartel fronts it; Blackstar flavours it

The commission says *"likely hutt / bounty hunter faction related"*. The campaign has exactly one
of each, and the mechanics decide who can actually hold the stall:

| candidate | fiction fit | mechanical fit |
|---|---|---|
| **Hutt Cartel** (`Jawa_HuttCartel`) | exact. The Cartel owns the only non-Imperial orbital node — *the door off-world* — and the eggs' whole value is "smuggled offworld" (sitting §4b). Its ideo is *the Reckoning of Debts*; a contract killing is debt collection by other means | ✅ `permanentEnemy false`, `canRequestTraders true`, high caravan frequency, and a dedicated TraderKindDef precedent already ships (`RUT_HuttCartel_Captives`) |
| **Blackstar Company** | the bounty-hunter outfit by name | ⛔ `permanentEnemy true` (R12, ruled to stand). A permanently hostile faction never sends traders and can never be a quest asker through vanilla machinery. Fronting the market with Blackstar means new C# or a faction-law change — both out of proportion |

**PROPOSED:** the market is a **Hutt Cartel channel**. Blackstar appears in the *fiction* — the
contract quests' text can name Blackstar hunters as the people who would otherwise be hired, the
comparison that makes the egg route attractive ("a hunter is loud and billed hourly; an egg is
quiet and biodegradable") — but every mechanical asker, trader and goodwill ledger is the Cartel.
§5-Q1 asks the owner to confirm the fronting.

### 1b. What form it takes — PROPOSED: a caravan kind plus the broker, no fixed seat

**A dedicated `TraderKindDef`** (placeholder `<RUT_HuttCartel_EggMarket>`), same shape as
`RUT_HuttCartel_Captives`, reachable two ways:

1. **A rare Hutt Cartel caravan variant** — the market comes to you, occasionally. Low
   `commonality` in the Cartel's trader rotation; it should feel found, not scheduled.
2. **The Bazaar's broker tab** (the broker is a Bazaar tab — decision by question card, 2026-09-13,
   memory `bazaar-trade-window-ruled`) as the *selling* channel: the broker premium is where the
   smuggler's jackpot cashes out without waiting for a caravan roll.

⛔ **No fixed black-market settlement seat** is proposed. A fixed site makes the egg run a
milk-run; the sitting's whole §4c design prices the eggs in *carry risk*, and a static buyer next
door deletes the risk. (If the owner wants a physical den later, the Cartel service houses —
FACTION_SPEC: 11 waterless service houses — are the natural hosts; parked, not proposed.)

### 1c. Tier and mod placement — PROPOSED: RUT, in the ShokkweaveEconomy mod

**Recommendation: `RUT` (campaign), living in `mandrake.rut.shokkweaveeconomy`** — the mod that
already owns every campaign-side egg/silk economy patch (rename, trader strip, yields, nest
scatter). Reasons:

1. **The commission itself says campaign layer** (§6 ruling 5 "overrides the 'nests are the only
   source' default **for the campaign tier**").
2. **The trader names `Jawa_HuttCartel`**, a campaign-authored FactionDef. An RSW mod is for
   any-Star-Wars-scenario content and cannot depend on this campaign's faction roster; a
   black-market kind with no faction to ride is dead XML.
3. **One mod owns the egg's campaign economy.** Splitting the buyer from the strip that created
   the scarcity invites the two to drift (doc-rot law: single-source what a generator can enforce).

⛔ Explicitly NOT `mandrake.rsw.shokk`: `SHOKK_SKIN_SHRINK_1` (§6 ruling 1) shrinks that mod to
the Wyyyschokk skin patch only. Nothing here widens it back.

### 1d. How it coexists with the free tier's Sellable-only default

🔴 **The engine fact that shapes this, MEASURED in the trader strip** (ShokkweaveTraderStrip.xml,
against `TradeabilityUtility.cs`/`StockGeneratorUtility.cs`): `Tradeability.Sellable` means
`TraderCanSell()` is false — **no trader of any kind can ever STOCK a Sellable item**. The free
tier's egg (`tradeability: Sellable`, sitting §4a) is therefore un-stockable by construction,
which is correct there: in `mandrake.rm.webwork` the only source is a nest.

**PROPOSED campaign patch, two lines:**

1. `PatchOperationReplace` the egg's `tradeability` → `All`. ⚠️ This is safe against leakage into
   ordinary stock because reaching a def requires a StockGenerator route: the egg's only trade tag
   is `RM_Contraband` (sitting §4a), which no vanilla `StockGenerator_Tag` reads, it belongs to no
   stocked category route, and nothing lists it by SingleDef — so `All` opens exactly the routes
   the campaign then adds, and no other. A build-time sweep of live TraderKindDefs proves it
   (§5-Q5 asks the owner to accept the `All` mechanism at all).
2. The `<RUT_HuttCartel_EggMarket>` kind stocks **1–3 eggs** (❓) via
   `StockGenerator_SingleDef`, and **buys** on the `RM_Contraband` tag at the §4b premium.

The free mod never sees either patch. A player without the campaign layer keeps exactly the
sitting's economy: nests are the source, orbitals are the sink.

### 1e. Prices — PROPOSED, relative to §4a's market value

Sitting §4a sets the egg's `MarketValue` at ❓350–500 silver. The black market prices around that
number, in both directions:

| transaction | price | why |
|---|---|---|
| black market **sells** you an egg | market value ×❓1.6–2.0 (the trader kind's `priceFactorSell` premium) | you are buying a murder weapon with no questions asked; it must cost meaningfully more than raiding a nest, or the nest raid — the biome's designed centrepiece — is dead content |
| black market **buys** your eggs | market value ×❓1.5 (the §4b `RM_Contraband` premium, restated not re-ruled) | the smuggler's jackpot. Best price on the planet |
| ordinary orbital/exotic trader buys | market value ×1.0 | the free tier's route, unchanged |
| **Wildsteam bounty** (destroy) | ❓ market value ×0.5–0.7, paid as goodwill-plus-silver | §6 ruling 2: the lower-paying **legal** outlet. It must stay clearly below the black market — the whole point is that virtue pays less |

### 1f. Coexistence with the Wildsteam bounty route

The two routes are deliberately the same choice the assassination quests pose, expressed as
economy: the Wildsteam pay less, openly, and like you for it; the Cartel pays more, quietly, and
owns you a little. Both consume the same inventory, so every clutch is a decision.

⚠️ One interaction is not designable without a ruling: **do the Wildsteam react to black-market
egg sales?** The Green Oath reveres the web's living ecosystem; selling eggs to smugglers is
exactly what they pay bounties to prevent. But "faction A loses goodwill when you trade with
faction B" is a surveillance mechanic vanilla does not have, and building one is a real cost.
§5-Q4 poses it; the default if unruled is **no reaction** (the sale is private, like every other
RimWorld trade).

## §2 The assassination quest family

The commission asks for *"some quests"* with *"optional immoral solutions"*. **The load-bearing
word is optional**: every quest below has at least one clean solution path, and the egg is never
the only door — it is the cheap, quiet, damnable one. PROPOSED family of three: one built fully
(2a), two sketched (2e), all sharing the machinery §3 resolves.

### 2a. The core quest — "The Reckoning" (skill §2 spec, prose first)

| spec line | answer |
|---|---|
| **The ask** | A named pawn at a nearby outpost owes the Cartel and will not pay. The Cartel wants the debt *closed* — how is your business. The quest site is a small settlement/outpost (quest Site, standard machinery) where the target lives, sleeps at night, in a room |
| **The reason** (no reward named) | The Cartel controls the door off-world and the water on the way to it; when the Reckoning of Debts asks a favour, "no" has a price of its own — and the target's outpost sits on ground your caravans cross |
| **The choice** | three defensible answers, below |
| **The failure state** | the target learns and flees (timer expiry), or the plant is discovered and the site turns hostile with the quest failed. Survivable: goodwill damage and a lost reward, never a campaign end |
| **The reward** | Cartel silver + Cartel goodwill; the immoral path additionally *keeps* the fee that a clean path spends. No egg is ever a reward (sitting §4b: the strip's no-quest-reward law covers the egg in both tiers) |
| **The deadline** | offer window `expireDaysRange` ❓4–8; completion timer ❓10–15 days before the target moves on |

**The three solution paths:**

| path | what you do | cost | consequence |
|---|---|---|---|
| **1. Pay it yourself** (clean) | hand the Cartel the debt, ❓ roughly 2× the quest's silver reward | pure silver — the rich colony's exit | Success. Cartel goodwill up; target's faction never knows; small positive history event |
| **2. Collect in person** (clean, hard) | travel to the site, convince or capture the target and deliver them to the Cartel alive (vanilla shuttle/caravan-delivery machinery) | a real expedition against a defended outpost, in the open | Success, larger reward. Target's faction goodwill **down** (you visibly abducted their pawn) — legal-adjacent, not deniable |
| **3. The egg** (immoral) | buy or bring one `RM_OllathrixEgg`, infiltrate the site at night, plant it in the target's room, walk away. It hatches in the night (§3); the target dies "of the biome" | the egg, the infiltration risk, the carry risk (2c) | Success **with no goodwill loss if undiscovered** — the death reads natural. Discovered: 2d. Either way a negative `HistoryEventDef` fires for the colony's own ideoligion to judge (murder-precept reactions — the deed is deniable to factions, never to your own conscience mechanics) |

Path 3 is the owner's named example, one-to-one: *assassinate someone by planting an egg in their
room to hatch in the night*.

**Giver and firing route (skill §7):** PROPOSED route 3 — `givenBy` the Cartel trader channel
(the black-market kind of §1 hands you the contract while you browse; `randomlySelectable false`),
with route 1 (low `rootSelectionWeight`, gated `rootMinPoints`, `minRefireDays` ❓30+) as the
fallback so the family fires for colonies that never meet the trader. Deterministic dev trigger
either way, per the skill's rule — never storyteller-gated verification.

### 2b. Planting mechanics — PROPOSED

The plant is: **deliver the egg to a marked cell in the target's room while the site is not
alerted.** Concretely: the quest marks the target's bedroom (the site generator places the target
with a bed in a roofed room); a colonist carrying the egg who reaches the marked cell drops it
there and the plant is done — modelled as a haul-to-cell job plus a quest part watching the egg's
position. ⚠️ Skill §9 honesty: *"deliver an item covertly to a cell inside an enemy site"* has no
vanilla `QuestNode` — this is the family's one **C# verb** (a small QuestPart watching
thing-position + site-alert state). Everything else in the family is stock nodes.

"While not alerted" is the whole stealth model — **no new vision/stealth system**. If the site's
pawns are hostile-alerted (combat started, planter seen and engaged) before the plant lands, the
covert branch is dead and the quest falls through to open outcomes (fight it out = a messy
path 2, or withdraw = failure). Night matters because the site sleeps; that is vanilla behaviour,
not new code.

### 2c. The carried-eggs mark as the infiltration tax

Sitting §4c: a pawn carrying eggs is *felt* — map-wide FeltMark, every Ollathrix converges —
wherever the SenseWeb runs. This design adds nothing to that mechanism and spends it twice:

- **The approach:** if the caravan route to the target crosses Webwork maps, the murder weapon in
  your packs marks you on every one of them. The cheap assassination has an expensive commute —
  exactly *"marks you to every web you pass"* made into quest pressure.
- **The alibi:** the planted egg sits in the target's room. If the outpost is on or near Webwork
  ground, the *target's own map* now has a felt-marked room… and §3's hatch does not care, but any
  later Webwork creep reaching that outpost converges on the corpse's quarters. Flavour text may
  wink at this; no mechanism is owed.

### 2d. Discovery and consequences

| event | consequence |
|---|---|
| planter seen and engaged before the plant | covert branch closed (2b); site hostile now, quest still completable the loud ways |
| egg found before hatch (site alerted after a completed plant, ❓ small chance per remaining hour) | quest **Fail**; target faction goodwill ❓−25 and a raid-grade grudge — attempted assassination is worse than abduction; Cartel goodwill unchanged (they were never here) |
| hatch kills the target, undiscovered | **Success**. Zero target-faction goodwill change — total deniability is the path's entire value (§5-Q6 asks the owner to confirm it stays total) |
| hatch fails to kill (the target survives the spider — §3 stages a real fight, not a scripted death) | quest **Fail** by timer as the target flees; no attribution, no goodwill loss. The immoral path can *whiff* — skill §2 Q4, failing is survivable and the egg is spent |
| colony ideoligion | every path-3 completion fires `<RUT_HistoryEvent_EggAssassination>` regardless of discovery — precepts and moral-guide mechanics see what factions cannot |

### 2e. The rest of the family, sketched

- **"Fragile Cargo"** — the smuggling escort: the Cartel pays you to move a clutch of eggs from a
  Webwork-adjacent pickup to their caravan/broker, across ❓2+ Webwork map crossings, against the
  §4c mark. Clean throughout (it is only smuggling); the immoral option is *selling the cargo out*
  to the Wildsteam bounty mid-quest — betraying the Cartel for goodwill with the Green Oath.
  Mirror-image morality to 2a: here the *Cartel* path is the contract-keeping one.
- **"Something in the Walls"** — the defensive inversion: a warning (or a discovered plant) that
  someone paid to put an egg in **your** colony — find it before nightfall. Teaches the mechanism
  from the victim's side, makes the world symmetrical (the Cartel sells to your enemies too), and
  costs almost nothing: it reuses the §3 hatch staging on the player's own map. ❓ Whether the
  planter is ever identified (Cartel deniability cuts both ways) — left to build.

## §3 The hatch tension, resolved as a design

**The tension, restated from the sitting** (§6 ruling 5's own ⚠️ flag): the free-tier egg
deliberately has **no `CompHatcher`** — an egg that hatches is a tamed Ollathrix by the back door
(ban 1: no tamed, traded or negotiated). But the commission's quest egg *hatches in the night*.
Two candidate mechanisms:

| | **A. Campaign hatch comp** — patch `CompHatcher` (or a variant egg item) in the campaign layer | **B. Staged quest event** — the egg item never hatches anywhere; the *quest* spawns the spider |
|---|---|---|
| item integrity | ⛔ needs either a second egg def (breaks the one-def economy — the black-market egg and the nest egg must be the same contraband, or smuggling has two prices) or a global comp on `RM_OllathrixEgg` (every stockpiled egg in the campaign becomes a hatch timer — the farm-a-spider back door, reopened in the tier where most players live) | ✅ `RM_OllathrixEgg` stays exactly the sitting's item, both tiers. No comp, no variant, no back door |
| ban 1 (no tamed) | `CompHatcher` hatches to `hatcheeFaction` — even null-faction hatching hands players a repeatable wild-spawner they control | ✅ the spider exists only where a quest stages it |
| the fiction | an egg that hatches on a shelf timer contradicts §4a's "inert cargo" and the 15-day rot | ✅ the fiction is the *Cartel's* craft: a viable egg, kept warm and turned, hatches when placed — the player buys the service, not a mechanism |
| build cost | a comp patch plus safeguards against the shelf-hatch | one quest part: at the night tick after a completed plant, spawn one hostile `RM_Ollathrix` at the egg's cell, despawn the egg, wake the room |
| skill fit | — | ✅ quests already own delayed one-shot events; this is a `QuestNode_Delay`-shaped part with a C# spawn (the same small assembly as 2b's plant-watcher) |

**PROPOSED: B, the staged quest event.** The item is inert everywhere forever; hatching is a
thing quests do, not a thing eggs do. This also answers the obvious exploit cleanly: ⛔ a player
cannot buy eggs and free-plant them as weapons outside quests — there is no hatch to trigger
(§5-Q7 confirms this is intended; if the owner wants free-planting as a colony weapon someday,
that is mechanism A's cost sheet, revisited then, not a default).

**What hatches — the one-kind ruling, kept.** §0 ruling 2 is ONE race, ONE kind, and a
"juvenile Ollathrix" `PawnKindDef` would be a second kind. PROPOSED: the quest spawns the one
`RM_Ollathrix` kind **at a juvenile life-stage age** — RimWorld scales animal `bodySize`, health
and damage by life stage on the same kind, so "a night-hatched young spider" is an age parameter,
not a def. It is genuinely dangerous to a sleeping pawn in a closed room and genuinely losable
against an armed, woken one (2d's whiff row). ⚠️ Two flags: (a) this presumes `RM_Ollathrix`'s
race authoring gives it real `lifeStageAges` — it will, races need them, but the scaling numbers
are build-time; (b) if the owner would rather the night-hatcher be *mature* (instant lethality,
no whiff), that is §5-Q3 — and ⛔ under no answer does a new PawnKindDef appear without its own
owner card.

**The night.** The hatch part arms on plant-complete and fires at the next ❓23h–02h window —
*"to hatch in the night"* is literal. The spawned spider is faction-of-none hostile (the kit's
"hostile to everything" — it does not check the contract), attacks the nearest sleeper, and is
then an ordinary wild animal on that map: the site deals with it or it deals with the site.
⚠️ Skill §6: nothing schedules after `QuestNode_End` — the hatch, the kill-check window and the
outcome all resolve **before** the End node; the surviving spider needs no quest to keep being a
problem.

## §4 Item impacts

| item (state today) | what it owes or gains from this design |
|---|---|
| **`WEBWORK_NEST_EGG_ECONOMY_1`** (FOUNDRY, proposed — builds nest, egg, re-lay, Wildsteam bounty per §6 rulings 2/3/4) | **Gains two authoring constraints, no scope growth:** (1) `RM_OllathrixEgg` ships with `tradeTags` `RM_Contraband` and *without* an explicit `tradeability` element only if the C# default (`All`) is overridden to `Sellable` explicitly — the campaign patch of §1d is a `Replace` and must have a node to match (the trader strip's own lesson: a Replace on an absent element silently matches nothing); (2) the egg stays comp-free — mechanism B means this item never grows a hatch. The Wildsteam bounty it builds should price per §1e's table so the two outlets land in the ruled order |
| **`WEBWORK_RM_MOD_BUILD_1`** (FOUNDRY, owed — builds `mandrake.rm.webwork`) | **Nothing.** Confirmed by design: no line of this document touches the RM tier (Q11 — Hutts and bounty hunters are IP). The free mod's egg economy is complete without it, which is the Q11a wholeness test passing |
| **`SHOKK_SKIN_SHRINK_1`** (FOUNDRY, proposed — shrinks `mandrake.rsw.shokk` to the skin patch) | **A boundary confirmation:** the black market does NOT land in the shrinking mod (§1c). Whoever executes the shrink should not park any of this content there "since the file is open" |
| **`SHOKKWEAVE_SOLE_SOURCE_1`** (ready/needs game-up) | Its mod (`mandrake.rut.shokkweaveeconomy`) is §1c's proposed home, so the build lands beside its patches — and its trader-strip proof run gains a sibling assertion: with the campaign layer up, exactly ONE trader kind stocks eggs |
| **`WEBWORK_EGG_BLACKMARKET_1`** (BENCH, proposed — this item) | This document is its design deliverable. On acceptance it owes a **build successor** (FOUNDRY): the TraderKindDef + stock/buy generators + tradeability patch, the quest family defs, and the one small C# assembly (2b plant-watcher, §3 hatch part). Quest defs go through `skills/rimworld-quests/scripts/validate_quest.py` before any load |

## §5 Needs owner ruling

Seven calls, each one card. Everything else in this document is proposed detail under §6 ruling 5
and needs no card unless he objects on read.

1. **Fronting.** The black market is mechanically a **Hutt Cartel** channel (Blackstar cannot
   trade or ask — `permanentEnemy true` stands by R12); Blackstar appears in quest fiction only.
   Confirm, or name a different front?
2. **Hatch mechanism.** PROPOSED: the egg item never hatches anywhere; quests stage the hatch as
   an event (§3 option B). The alternative (a campaign `CompHatcher`/variant egg) reopens the
   farm-a-spider back door and splits the egg into two items. Accept B?
3. **What hatches.** PROPOSED: the one `RM_Ollathrix` kind spawned at a **juvenile life-stage
   age** — dangerous to a sleeper, beatable by the armed, so the assassination can fail honestly.
   Alternative: spawn it mature (near-certain kill, no whiff). ⛔ Either way no new PawnKindDef
   (§0 ruling 2). Juvenile or mature?
4. **Wildsteam reaction.** Do the Wildsteam react to black-market egg *sales* (goodwill hit when
   you sell to the Cartel)? Default if unruled: no — vanilla has no trade surveillance and the
   sale is private. React, or blind?
5. **Tradeability patch.** The campaign patches the egg's `tradeability` → `All` so the one
   black-market kind can stock it (Sellable items are un-stockable by any trader — MEASURED,
   trader strip). Leak-checked at build against every live TraderKindDef. Accept the mechanism?
6. **Total deniability.** An undiscovered egg assassination costs **zero** goodwill with the
   target's faction — deniability is the path's entire value; only your own ideoligion ever
   knows. Confirm zero, or should rumours leak a small hit?
7. **No free planting.** Bought eggs cannot be planted as weapons outside quests (a consequence
   of mechanism B — there is no hatch to trigger). Confirm intended, or file the
   colony-weapon version as future work with mechanism A's costs?
