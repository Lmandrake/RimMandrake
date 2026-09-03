<!-- status: PROPOSAL — RESEARCH_TREE_NORMALIZATION_1 vision pass v3, 2026-09-03, on the
     owner's directive of the same day ("split out some racial specifics into their own
     trees... all things warcasket is uniquely [Junker]... the sonic weaponry is another
     of those for the [Geonosians]... please identify other 'faction ally locked' groups").
     Nothing here is ruled. Companion artifacts: restructured_model_v3.json (all 522 rows
     accounted), classify_v3.py (the generator + the coverage assertion),
     v3_coverage_assertion.txt (its printed output).
     Builds on twelve_trees_proposal.md (v2, thirteen trees) and does not supersede it:
     v2's tree grammar, cuts and re-costs stand except where a row moves here.
     Executes the faction-held half of infrastructure/state/items/TECHPRINT_FACTION_GATING_1.md,
     which is BLOCKED pending exactly the owner ruling this pass proposes. -->

# Faction-locked trees — research restructure, v3

> 🔴 **A CUT REMOVES A `ResearchProjectDef` AND NOTHING ELSE** — owner, 2026-09-03:
> *"I did not cut the anomaly content. I only cut the players ability to research
> that tech tree. Please restore the content for our own repurposing as before e.g.
> the sarlacc and assailant dungeons and terminator/night side creatures."*
> Every ThingDef, PawnKindDef, building, creature and piece of map content a cut row
> unlocked **stays in the game**. Where v1 or v2 read as though cut content is gone,
> they are wrong and this line governs. Cited docs are cited as corrected by it.

> 🔑 **The one-sentence version.** Faction-locking is a **row** property
> (`heldByFactionCategoryTags` + `techprintCount`), not a tab property. A locked
> **tree** is a presentation choice, and it only earns a tab when the group is big
> and coherent. Three groups earn one; fourteen more rows are locked in place.

---

## 1. The faction roster — who is actually on the planet

A tree gated on a faction that is not on the planet is a dead tree. This is not
hypothetical: **one such row already ships** (§4.1). So the roster comes first.

Sources, both `status: live` and in agreement:
`design/Jawa/worldbuilding/FACTION_SPEC.md` (the buildable/engine layer, wins on
field-level disputes) and `design/Jawa/worldbuilding/faction_roster_v2.md` (the
fiction layer). Cross-checked against the authored `FactionDef` XML on disk in
`src/SPLIT_Phase3/Jawa_Patches/Defs/FactionDefs/`.

| # | faction | `FactionDef` | `categoryTag` today | settlements | can deliver techprints? |
|---|---|---|---|---|---|
| 1 | Galactic Empire | `Empire` (vanilla, patched) | `Empire` | 3 surface | ✅ trade + quest (Royalty traders) |
| 2 | Hutt Cartel | `Jawa_HuttCartel` | `Outlander` | 19 | ✅ trade + quest |
| 3 | Homestead Defense League | `OutlanderCivil` (vanilla) | `Outlander` | 13 | ✅ trade + quest |
| 4 | Deep Desert Tribes (Tusken) | `TribeCivil` (vanilla) | `Tribal` | 9 | ✅ trade + quest |
| 5 | Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | `Outlander` | 12 | ✅ quest-routed (raids suppressed) |
| 6 | Wildsteam Clan | `Jawa_WildsteamClan` | `Outlander` | 4 | ✅ trade + quest |
| 7 | Deepwater Compact | `Jawa_DeepwaterCompact` | `Outlander` | 5 | ✅ quest-routed (raids suppressed) |
| 8 | Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | `Outlander` | 5 | ✅ trade + quest |
| 9 | Ascendant Helix | `Jawa_AscendantHelix` | `Outlander` | 7 | ✅ trade + specialist quests |
| 10 | Blackstar Company | `Pirate` (vanilla, patched) | **none** | 4 | ⚠️ needs a tag (§5.3) |
| 11 | Jawa Trade Moot | `Jawa_IndigenousTribes` | `Tribal` | 7 | ✅ trade (the clan's own kin) |
| 12 | the Junkers | `Jawa_Junkers` | `Pirate` | 8 | ⚠️ raid loot only (§5.2) |
| 13 | the Forgotten Arsenal | `Mechanoid` (vanilla, patched) | none | 0, `hidden` | ❌ never — structurally excluded |

**Not on the planet, and this matters below:** "the Unbound Hive" (vanilla `Insect`)
is CUT — `startingCountAtWorldCreation 0` (`FACTION_SPEC.md:56`). Insect *creatures*
and infestations remain; the *faction* does not. Mandalorians, the Republic, Czerka,
the Exchange and the Echani have **no faction on this planet at all** — they exist
only as equipment names inherited from the KotOR mod. The Sith are pawn kinds inside
Imperial escorts (`faction_roster_v2.md:321`), never a faction. The Jedi are
explicitly factionless hidden wanderers (`:309-317`).

**Canon confirmed on the owner's two examples.** Both his phonetic spellings check out:
- *"junket"* = **the Junkers**, `Jawa_Junkers`. *"Their signature is the warcasket —
  steel welded around a body, a suit that is never removed"* (`faction_roster_v2.md:2274`),
  and the dossier names `OskarPotocki.VFE.Pirates` as the dependency by packageId. The
  seven warcasket research rows in the model are all `VFEP_*` from that mod. **Verified.**
- *"genosians"* = **the Geonosian Foundry Hive**, `Jawa_GeonosianFoundryHive`. Warrior
  Drone carries a *sonic blaster* (`:1667`); the faction equipment table reads
  *"Geonosian: sonic weapons plus mass-produced droids"* (`:359`); `FACTION_SPEC.md:388`
  names the hive **the campaign's authored insectoid power**. **Verified.**

---

## 2. How gating actually works — VERIFIED / HYPOTHESIS

Read from the RimWorld 1.6 decompile via RimSage. Every claim marked.

1. **`ResearchProjectDef.heldByFactionCategoryTags` (`List<string>`) is the gate, and
   `FactionDef.categoryTag` is the key it matches.** `TechprintUtility.
   GetResearchProjectsNeedingTechprintsNow()` drops any project whose list does not
   `Contains(faction.def.categoryTag)`. **VERIFIED** — `Source/RimWorld/
   TechprintUtility.cs:24`, `Source/Verse/ResearchProjectDef.cs:51`.
2. **The pair is mandatory in both directions.** `ConfigErrors()` errors on
   `techprintCount == 0` with tags set, AND on `techprintCount > 0` with no tags.
   A techprinted project with no tags is therefore never offered by any faction.
   **VERIFIED** — `ResearchProjectDef.cs:406-412`.
3. **Techprints require Royalty.** `TechprintCount` returns 0 unless
   `ModLister.RoyaltyInstalled`, and `ConfigErrors()` says so. Royalty is active in this
   campaign (its 19 research rows are in the model). **VERIFIED** — `:204-212, :422`.
4. **Three delivery routes, all keyed on `makingFaction`:** trader stock
   (`StockGenerator_Techprints` inside a `TraderKindDef`), quest/reward loot and
   raid loot (`ThingSetMaker_Techprints`, and `ThingSetMakerUtility` filters the same
   way at `:63`), and books (`ThingSetMaker_Books`). All pure XML. **VERIFIED.**
5. **"Visible but locked" is native and it advertises the alliance by name.**
   `MainTabWindow_Research.DrawTechprintInfo()` prints *"Techprints from factions:"*
   and then draws the **icon and name of every faction present in the world** whose
   `categoryTag` matches. The locked project itself renders in its tab with an
   `x / n` techprint counter and the reason `InsufficientTechprintsApplied`.
   **VERIFIED** — `MainTabWindow_Research.cs:1410-1447, :544, :1070-1082`.
   ⇒ This is why the design chooses **visible-and-locked** everywhere: the game
   already turns a locked row into a poster for the faction that holds it.
6. **The dead-tree failure mode is exactly visible here too**: if no present faction
   carries the tag, the header renders with an **empty list** and the project can
   never be started. **VERIFIED** by the same code path. §4.1 is a live instance.
7. **`ResearchTabDef` can be hidden (`visibleByDefault`) but not revealed.** The field
   is real; there is no vanilla data-only route to flip it mid-game
   (`minMonolithLevelVisible` is Anomaly-only). Hiding-then-revealing a locked tab
   needs C#. **VERIFIED field, HYPOTHESIS that a reveal needs code** — and the design
   does not want it anyway (point 5).
8. **The random-loot leak is real.** When `makingFaction` is `null` the faction filter
   is skipped entirely (`TechprintUtility.cs:24`, `ThingSetMakerUtility.cs:63` both
   guard on `!= null`), and vanilla's own ancient-complex map-gen loot is commented
   *"intended to ignore player needs entirely, it gives entirely random techprints"*
   (`Defs/Core/ThingSetMakerDefs/ThingSetMakers_MapGen.xml:171`). ⇒ **A player who
   never allies anyone can still find a locked techprint in a ruin.** **VERIFIED.**
   Treat it as a designed pity-drop, not a hole; it is slow and unaimed. If the owner
   wants the lock absolute, those three map-gen `ThingSetMaker_Techprints` nodes are
   patchable out — one xpath each.
9. **Starting-known research is a separate, proven, pure-XML class.**
   `ScenPart_StartingResearch` (per-project, in `Scenario_Utinni.xml`) for untechprinted
   rows; `FactionDef.startingTechprintsResearchTags` + a `ResearchProjectTagDef` grants
   the techprints themselves at tick 0 for techprinted rows. **VERIFIED** —
   `Source/Global/ResearchUtility.cs:32-45`. This is how `jawa-special` ships.

**What does NOT exist in vanilla, and would need code:** a per-faction *goodwill
threshold* gate ("allied, not merely met"); a tab that hides until first contact;
a targeted "reveal project X when event Y fires". The first two are wanted-but-not-needed;
the third is already carried as the open half of `TECHPRINT_FACTION_GATING_1`.

---

## 3. The decision rule — how a group was judged lockable

A group is faction-locked only if it passes **all three**. Stated so the owner can
overturn the rule rather than argue thirty rows.

| test | it means |
|---|---|
| **T1 · Holder** | a faction **on the planet** whose own design canon names this content as **its signature** — not merely "would suit them". |
| **T2 · Route** | that faction can actually deliver a techprint: it is not hidden, not structurally trade-less without a fix, and has a trader, a quest line, or an authorable `raidLootMaker`. |
| **T3 · Deprivation** | a player who never earns it loses a **distinct capability, not a necessity** — nothing that gates survival, medicine, food, power, **or the prerequisites of an ungated row**. |

T3's last clause is machine-checked: `classify_v3.py` refuses to write the model if any
`common` / `jawa-special` / `ship-only` row requires a locked row (**gate leak**), or if
a locked row requires a *differently*-locked row (**cross-lock**). Both are 0 in v3.

---

## 4. What is already built — and one live defect

**The Armoury already ships a faction techprint economy, and nobody knew.**
`TECHPRINT_FACTION_GATING_1.md` records *"None of the 12 campaign `FactionDef`s
currently set `categoryTag` (checked `src/RimStarWars` — zero hits)"* and *"no per-row
faction assignment was guessed."* Both readings were of the wrong directory. Measured
in the deployed mod folder:

- **Eight campaign `FactionDef`s do set `categoryTag`** — in
  `src/SPLIT_Phase3/Jawa_Patches/Defs/FactionDefs/`, six as `Outlander`, one `Tribal`,
  one `Pirate`.
- **Eighteen research rows in `Mods/Armoury` already carry `techprintCount` +
  `heldByFactionCategoryTags`** — the whole KotOR maker-equipment catalog, inherited
  from the original mod author with his arbitrary vanilla tags.

So v3 is a **re-aiming of a live system**, not a new build. And it must be, because:

### 4.1 The defect: two rows are gated on nobody

Vanilla sets `categoryTag` on very few factions — `Outlander`, `Tribal`, `Ancient`,
`Empire`, and a handful of DLC one-offs. **No faction anywhere carries `Raider`.**

- `guy762_ResearchKotOR_tusken` (Tusken Raider equipment) is held by **`Raider`** →
  **no holder exists, in vanilla or in this campaign.** The research screen shows the
  techprint header with an empty faction list. It is unreachable by trade or quest
  today, and only the random-ruins leak (§2.8) can ever finish it. **This is the exact
  failure mode the whole pass exists to avoid, already shipped.**
- `Ancient` (the uncraftables row, `techprintCount 999`) — the `Ancients` faction is
  hidden and never on the map. That row is cut in v2 anyway.

### 4.2 The accident: four rows are secretly Junker-held

Because **vanilla's `Pirate` FactionDef sets no `categoryTag` at all**, and
`Jawa_Junkers` sets `<categoryTag>Pirate</categoryTag>` explicitly, the tag `Pirate`
resolves to **exactly one faction on this planet: the Junkers.**

⇒ `guy762_ResearchKotOR_mando`, `_exchange`, `_hutts` and `_disruptor` are **already
Junker-locked by accident** — and the Junkers descend from `PirateBandBase`, which has
**no `baseTraderKinds`, no `caravanTraderKinds`, no `visitorTraderKinds`**, and a
`raidLootMaker` (`PirateRaidLootMaker`) whose `fixedParams.filter.thingDefs` is a nine-item
whitelist of silver, medicine, meals and drugs — **no techprints**. So those four rows
have no delivery route either. Four more effectively dead rows.

This is also the **good news**: the owner's *"earning those tech prints from the junkets
themselves"* needs **no new tag at all** — `Pirate` is already unique to them. It needs
a loot maker (§5.2).

---

## 5. The three locked trees

### 5.1 The Junker Yards — `Jawa_Junkers`, tag `Pirate` (unchanged)

*"The bottom of the scrap heap given weapons and a grudge."* Six rows: everything
warcasket except removal.

| tier | row | cost |
|---|---|---|
| T2 | `VFEP_WarcasketWeaponry` | 2,000 |
| T2 | `VFEP_Warcaskets` (salvaged shells only) | 3,000 |
| T2 | `VFEP_SpacerWarcasketWeaponry` | 3,000 |
| T3 | `VFEP_AdvancedWarcaskets` | 4,000 |
| T3 | `VFEP_SpecialisedWarcaskets` | 5,000 |
| T4 | `VFEP_SpacerWarcaskets` | 6,000 |

**Access rule — you take it off the dead.** No trade, ever: the Junkers are *reviled*
in canon and `PirateBandBase` gives them no traders. The techprint route is **raid loot
and quest reward**:

- Author `RUT_JunkerRaidLootMaker` (a `ThingSetMakerDef` with a `ThingSetMaker_Techprints`
  child) and point `Jawa_Junkers.raidLootMaker` at it. `IncidentWorker_RaidEnemy.
  GenerateRaidLoot()` sets `makingFaction = parms.faction`, so the `Pirate` tag filter
  applies correctly and only Junker-held prints drop. **VERIFIED mechanism, not wired.**
- `Jawa_Junkers` already restates `permanentEnemy false` (deliberately, against
  `PirateBandBase`), so quest rewards are reachable if relations are ever repaired.

**What a player who never fights them gets:** no warcaskets. That is the whole point —
warcaskets are the campaign's only thick-armour class, and now the only way to wear one
is to have beaten someone wearing one.

**One prereq re-point, PROPOSED.** `VFEP_WarcasketRemoval` (T4, 6,000) **stays common in
The Shell** — freeing a pawn welded into a casket must not require allying the welders —
so its prereq moves `VFEP_SpecialisedWarcaskets` → `Machining`. Without this the model
fails its own gate-leak assertion. No defName is renamed.

### 5.2 The Foundry Hive — `Jawa_GeonosianFoundryHive`, tag `GeonosianHive` (NEW)

The hive's two named products, per its own dossier: **sonic** and **mass-produced droids**.
Five rows.

| tier | row | cost | why the hive |
|---|---|---|---|
| T1 | `VFEI2_BasicHivetech` | 1,000 | `FACTION_SPEC.md:388` — the campaign's authored insectoid power |
| T1 | `VFEI2_StandardHivetech` | 1,000 | " |
| T2 | `VFEI2_ExoticHivetech` | 2,000 | " |
| T2 | `guy762_ResearchKotOR_sonic` | 2,000 | the owner's own example; Warrior Drone's sonic blaster |
| T2 | `OuterRim_BattleDroids` | 2,000 | *"sonic weapons plus mass-produced droids"* (`:359`) — Geonosian foundries built the droid army |

**Access rule — you trade for it.** The hive descends from `OutlanderFactionBase`, whose
`baseTraderKinds` / `caravanTraderKinds` / `visitorTraderKinds` already carry
`StockGenerator_Techprints` (`TraderKinds_Base_Outlander.xml:122` et al). The moment the
hive carries a unique tag and these five rows name it, techprints appear in its stock with
no further wiring. Plus quest rewards.

**Costs, stated plainly.** ⚠️ Two real objections:
- **`OuterRim_BattleDroids` is the contestable row.** It leaves The Waking Mind, which v2
  built deliberately as the Ohm/Oomo flashpoint. Alternative: leave it, and the Foundry
  Hive is four rows. Recommendation: move it — the lore is exact, and the tree needs the leg.
- **This tree is flat (T1–T2, top cost 2,000) and it is the smallest at five.** Sonic is
  thin by ruling — `research_tree_taxonomy.md:156` already flags *"Sonic school KEPT thin
  (creative expansion later: `SONIC_WEAPONS_EXPANSION_1`)"*. The honest position: five rows
  is a *branch* wearing a tab, and it becomes a real tree when that expansion lands.
  Recommendation: ship it anyway — a five-row tab that says *"the hive holds this"* does
  more work than five rows scattered across Scavenger and Strange Schools.

### 5.3 The Ascendant Ladder — `Jawa_AscendantHelix`, tag `AscendantHelix` (NEW)

The one the owner did not name, and the strongest of the three. The Helix is the
*"wealthy research enclaves"* faction (`faction_roster_v2.md:443`), routed by *"specialist
medicine/genetics quests + trade"* (`:387`), buying bulk water *"for growth vats and
biosculpters"* (`:216`), under an ideoligion literally called **the Ascendant Genome**.
Eight rows — the flesh crown lifted out of The Reach.

| tier | row | cost |
|---|---|---|
| T0 | `GrowthVats` | 500 |
| T1 | `Xenogermination` | 1,000 |
| T1 | `FertilityProcedures` | 1,000 |
| T1 | `Biosculpting` | 1,500 |
| T1 | `NeuralSupercharger` | 1,500 |
| T1 | `GeneProcessor` | 1,500 |
| T2 | `Archogenetics` | 2,500 |
| T3 | `Bioregeneration` | 4,000 |

plus two Helix-held rows that stay where they are: `KOTOR_Research_Kolto` (The Refinery)
and `guy762_ResearchKotOR_czerka` (The Shell — *"expensive security equipment, few
combatants"* is Czerka's job description).

**Access rule — you buy it, and buying it is the temptation.** Trade + the Helix quest
line. This is the campaign's theology made mechanical: v2 built The Reach as *"the trap,
priced brutally"*, and pricing a trap in research points is weak — **the player just
grinds it in the background.** Pricing it in *who you had to befriend* is not weak. The
transhumanists are on the planet, they are rich, they are willing, and the price of the
gene ladder is a standing relationship with them.

**What stays common:** `Prosthetics` (600), `Bionics`, `Cryptosleep`, `ScuttlebugsBiology`,
`GravBionics`, `KOTOR_Research_AdvPhysiology`, `_Implants`, `_AdvImplants`. A peg leg and
a bionic eye are survival, not ambition; T3 forbids gating them. Verified clean: none of
the eight locked rows is a prerequisite of any of these eight.

---

## 6. Fourteen more rows, locked in place (no new tab)

A one-row "tree" is not a tree. These carry `access3` and keep their v2 tab. Nine of them
already have techprints today and are only being **re-aimed**; the corrections are the
point.

| row | tab | holder | today → v3 |
|---|---|---|---|
| `guy762_ResearchKotOR_sith` | The Shell | **Empire** | `Outlander` (7 holders) → `Empire`. Canon: *"Sith appear only in Imperial Sith-escort pawn kinds"* (`:321`) |
| `guy762_ResearchKotOR_tusken` | The Shell | **Deep Desert Tribes** | `Raider` (**NO HOLDER — dead**) → `Tribal`. Fixes §4.1 |
| `guy762_ResearchKotOR_hutts` (Kajidic) | The Shell | **Hutt Cartel** | `Pirate` (→ Junkers, no route) → `HuttCartel` |
| `guy762_ResearchKotOR_exchange` | The Shell | **Hutt Cartel** | `Pirate` → `HuttCartel`. The Exchange is absent; the Cartel *is* this planet's syndicate. Reflavor, no rename |
| `guy762_ResearchKotOR_wookiee` | The Shell | **Wildsteam Clan** | `Outlander` → `WildsteamClan`. The clan's core xenotype is Wookiee-kin |
| `guy762_ResearchKotOR_mando` | The Shell | **Blackstar Company** | `Pirate` → `BlackstarCompany`. Mandalorians are absent; Blackstar are the planet's elite hunters, *"high quality, small numbers, mixed specialist weapons"* |
| `guy762_ResearchKotOR_disruptor` | Blasterworks | **Blackstar Company** | `Pirate` → `BlackstarCompany` |
| `guy762_ResearchKotOR_czerka` | The Shell | **Ascendant Helix** | `Outlander` → `AscendantHelix` |
| `KOTOR_Research_Kolto` | The Refinery | **Ascendant Helix** | `Empire` → `AscendantHelix` |
| `KOTOR_Research_cloaking` (Stygium) | Strange Schools | **Empire** | unchanged — already correct |
| `KOTOR_Research_Lobot` (Positronic Brain) | The Waking Mind | **Empire** | unchanged |
| `guy762_ResearchKotOR_jedi` | The Shell | **Empire** | unchanged — confiscated robes; the Jedi have no faction to sell them |
| `guy762_ResearchKotOR_republic` | The Shell | **Empire** | unchanged — the Republic is 4,000 years dead; its successor state keeps the archives |
| `guy762_ResearchKotOR_echanishields` | The Shell | **Empire** | unchanged — Echani absent |
| `guy762_ResearchKotOR_lightsabers` · `_advsabers` · `_saberparts` | Strange Schools | **Empire** | `_advsabers` gains a gate it lacks today, for chain consistency |

**Two rows become `jawa-special` (known at colony start, `ScenPart_StartingResearch` /
`startingTechprintsResearchTags`):** `guy762_ResearchKotOR_jawa` (the clan's own gear —
today absurdly held by seven Outlander factions) and `RSW_JawaIon_Weaponry` (canon:
the JawaIon vocabulary is the clan's own ion doctrine). **Three stay `ship-only`:** the
Memory Core ship-design trio, unchanged from v2.

**`categoryTag` changes required — five, all one line of XML each:**
`Jawa_GeonosianFoundryHive` `Outlander`→`GeonosianHive` · `Jawa_AscendantHelix`
`Outlander`→`AscendantHelix` · `Jawa_HuttCartel` `Outlander`→`HuttCartel` ·
`Jawa_WildsteamClan` `Outlander`→`WildsteamClan` · vanilla `Pirate` (Blackstar) gains
`BlackstarCompany` where it has none.
**Unchanged on purpose:** `Jawa_Junkers` keeps `Pirate` (already unique — §4.2), and
`TribeCivil` / `Jawa_IndigenousTribes` keep the shared `Tribal`, because **`Tribal` is
the only `categoryTag` value vanilla itself keys on by name** (ten role-apparel precept
lines, four apparel `ideoDesire` lists, one reward `ThingSetMaker`) and re-tagging a
tribal faction breaks them. Two tribal peoples both selling desert gear is a fine outcome.

⚠️ **Residual risk, HYPOTHESIS:** a sweep of the installed mod set found `Outlander`
referenced on the order of fifty times and `Pirate` around eighteen, across the six
faction-category fields (counts are a grep tally, not a per-field audit). Nothing named a
campaign faction specifically, but a faction dropping out of the `Outlander` bucket may
silently change some other mod's targeting. **Each of the four `Outlander` re-tags needs
one grep at execution time before it ships.** Not a blocker; a checklist item.

---

## 7. Rejected candidates — and why

| group | rejected because |
|---|---|
| **Lightsabers as a "Jedi tree"** | The Jedi are **explicitly factionless** — *"Jedi generate as hidden wanderer pawns... not as members of... any other faction"* (`faction_roster_v2.md:309-317`). Nobody can sell you a lightsaber techprint. T1 fails. They stay Empire-held (confiscated) in Strange Schools. |
| **The whole droid branch → Free Droid Enclaves** | Tempting and **wrong-way-round in canon**: *"Jawas acquire droids using restraining bolts, which the Free Droid Enclaves define as slavery. The player's core progression loop is the Enclave's central atrocity"* (`:2671`). The Enclaves would not sell droid-making techprints; being their friend would forbid the loop, not fund it. T1 fails hard. |
| **Republic / Czerka / the Exchange / Mandalorians / Echani as trees** | **No faction on the planet.** They are equipment names inherited from the KotOR mod. Where a present faction plausibly inherits the role (Exchange→Hutt Cartel, Czerka→Helix, Mando→Blackstar) the ROW is re-aimed; where none does (Republic, Echani), it stays Empire-held archaeology. |
| **Insectoid hivetech → an insectoid faction** | The insectoid *faction* (`Insect`, "the Unbound Hive") was CUT at worldgen (`FACTION_SPEC.md:56`). Wild insects remain as a hazard, and a hazard cannot trade. Re-aimed to the **Geonosian Foundry Hive**, which canon names the authored insectoid power. |
| **The Forgotten Arsenal (`Mechanoid`)** | `hidden true`, zero settlements, no traders, no quests. T2 fails structurally — it can never deliver a techprint. |
| **Deepwater Compact · Homestead Defense League · Free Droid Enclaves** | Real, present factions with **no distinct research group** in the 522. Their dossier signatures (*"disciplined industrial rifles, EMP, Gungan shield belts"*, *"civilian industrial gear"*) map onto rows other people also make. T1 fails: "would suit them" is not "is their signature". |
| **`KOTOR_Research_Spice` → Hutt Cartel** | T1 passes beautifully (spice *is* the Hutt trade) and **T3 fails**: `KOTOR_Research_AdvImplants` in The Reach requires it, so a Hutt lock would leak into an ungated tree. Caught by the gate-leak assertion. Stays common. Revisit if `_AdvImplants` is re-pointed. |
| **`VFEP_WarcasketRemoval` → Junkers** | Deliberately excluded from an otherwise complete block. Removing a welded casket from a rescued pawn is a mercy, not Junker doctrine; gating it behind allying the welders is the wrong story and fails T3. |
| **Hiding a locked tab until first contact** | No vanilla data-only reveal (§2.7), and undesirable anyway: the research screen already names the holding faction with its icon (§2.5). Visible-and-locked *is* the advertisement. |

---

## 8. What it costs — before / after

Only the five changed trees are listed; the other seven are untouched from v2.

| tree | v2 | v3 | Δ | note |
|---|---|---|---|---|
| Scavenger | 44 | **41** | −3 | hivetech → The Foundry Hive |
| The Shell | 39 | **33** | −6 | warcaskets → The Junker Yards |
| The Waking Mind | 27 | **26** | −1 | battle droids → The Foundry Hive |
| The Strange Schools | 11 | **10** | −1 | sonic → The Foundry Hive |
| The Reach | 16 | **8** | −8 | the gene crown → The Ascendant Ladder |
| *new* The Ascendant Ladder | — | **8** | +8 | locked |
| *new* The Junker Yards | — | **6** | +6 | locked |
| *new* The Foundry Hive | — | **5** | +5 | locked |
| unchanged | Workshop 54 · Refinery 52 · Hearth 49 · Powder & Slug 36 · THE SHIP 29 · Droidsmith 29 · Blasterworks 16 | | | |
| **total placed** | **402** | **402** | 0 | no row gained or lost |

**Viability.** Three trees now sit under ten rows: The Foundry Hive (5), The Junker Yards
(6), and — the one that actually worries me — **The Reach at 8**. Stripped of genes and
biosculpting, "the trap, priced brutally" is now eight workaday prosthetics-and-bionics
rows with no trap left in it. Its identity moved to The Ascendant Ladder.

**Tree count: v2 13 → v3 15** (16 if The Rites ships). But the useful count is different:

> **The general research economy is exactly TWELVE trees** — Scavenger · The Hearth ·
> The Refinery · The Workshop · Powder & Slug · Blasterworks · The Strange Schools ·
> The Shell · Droidsmith · The Waking Mind · THE SHIP · The Reach.
> **Three more are not bought with research points at all.** They are shop windows for
> alliances. The owner asked for ~12 and, after the split, that is what the points buy.

---

## 9. Trade-offs for the owner

1. **Fifteen tabs vs twelve-plus-three.** Recommended: **fold The Reach's eight survivors
   into The Workshop** (bionics and prosthetics are machining) and let The Ascendant Ladder
   *be* the temptation tree. That lands **14 tabs, 11 open + 3 locked**, sharpens the
   theology, and removes the only tree I think is now below viability. The v3 JSON ships
   the conservative 15-tab version; this is one line of `classify_v3.py` to change.
2. **`OuterRim_BattleDroids` out of The Waking Mind.** The lore is exact; the cost is one
   row off the Ohm/Oomo flashpoint tree. Recommended: move it.
3. **The Foundry Hive is five flat rows.** Ship it thin, or hold it until
   `SONIC_WEAPONS_EXPANSION_1`. Recommended: ship it thin.
4. **The Ascendant Ladder locks vanilla Biotech/Ideology content behind a faction.** This
   is the biggest playability change in v3 and the one I am least entitled to decide.
   Recommended: do it — it is the ruled inversion (*the world gates tech*) applied where
   it bites hardest.
5. **The random-ruins techprint leak (§2.8).** Leave it as a pity-drop, or patch out three
   map-gen nodes to make the locks absolute. Recommended: leave it.
6. **Absolute locks vs goodwill-scaled locks.** Vanilla has no "must be allied" gate — a
   *hostile* faction's techprints still generate in quest loot and raid drops. If the
   owner wants "ally them or nothing", that is C#. Recommended: don't; hostility is a
   fine way to earn a Junker print.
7. **Four `Outlander` re-tags need a mod-stack grep each** before execution (§6). Cheap,
   but it is a real step and must not be skipped.

---

## 10. Two pre-existing defects this pass surfaced but did not fix

Inherited from v2, reported by the v3 assertion (`orphans: 2`), out of scope here:

- `MM_Research_AncientShipDesigns` (THE SHIP, surviving) requires `MM_Research_Repulsor`,
  which v2 **cut**. The ship-design trio would be unreachable.
- `VAE_MilitaryClothing` (The Hearth, surviving) requires `VAE_SterileAttire`, cut in v1.

Both need a prereq re-point at manifest draft. Neither is caused by faction locking.

---

## 11. Contracts this pass keeps

No defName renamed — not one. Tier bands unchanged (T0 ≤600 · T1 ≤1,600 · T2 ≤3,000 ·
T3 ≤5,000 · T4 5,000+) and every placed row re-checked against them. No costs changed by
this pass; v2's 28 re-costs stand untouched. Coverage-or-refuse asserted by
`classify_v3.py`, which prints its proof and refuses to write a partial model. Cuts remain
`ResearchProjectDef`-only — **the content a cut row unlocked stays in the game.**
Nothing here executes.
