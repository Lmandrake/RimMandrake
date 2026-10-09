# Fall-zone lost-cargo quests: design draft (2026-10-09)

Item `FALLZONE_LOST_CARGO_QUESTS_1` (proposed, kind design, filed by the owner 2026-09-20: *"Make a note
that the injected wreckage in the fall zone can lead to quests about lost cargo of interest"*).
BENCH design helper, owner asleep. **Draft for his review. Nothing was built, and no design/ file was edited.**

The item says the design pass owes three things: **what makes a manifest yield a lead**, **how a lead
becomes a quest**, and **which existing wreckage injection it reads**. It must connect to The Bazaar's
scanner modules (`BAZAAR_STOLEN_GOODS_PROPERTY_1`) without being built into them. Standing constraint
from the item: 🔴 *"The player did not fall from space"*. The fall's wrecks belong to someone else, so
a lost-cargo quest is a claim on another party's property.

All paths are under `/home/mandrake/rm/bench` (Windows mirror `D:\Luke\dev\RimMandrake\`).

## 1. What exists (survey, read from source 2026-10-09)

### 1a. The injection this reads: the Wreckage engine and its Fall Line layer (built)

| piece | path | state |
|---|---|---|
| Wreckage engine `mandrake.rm.wreckage`: wreck families, weathering, density classes, `RM_GenStep_WreckField` scatter, `RM_CompSalvageLoot` (loot roll on careful deconstruct only) | `src/RimMandrake/Wreckage/` | built |
| `RM_IncidentWorker_WreckFall` + `RM_WreckFallExtension` (list, count 1-4, skyfaller, spread, optional `requiredMutators` gate) + public `RM_WreckFall.Drop(...)` that returns the first landing cell | `src/RimMandrake/Wreckage/Source/RM_IncidentWorker_WreckFall.cs` | built. **It has no manifest payload.** Design §3e of `design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md` names "a manifest note (`FALLZONE_LOST_CARGO_QUESTS_1`)" as a payload it *could* carry |
| `RUT_FallLineWreckFall` incident on that worker, list `RUT_WreckList_FallLine` | `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_FallLineWreckFall.xml` | built, **`baseChance 0` (debug-fire only)**. Making it fire on Fall Line tiles is a named, unbuilt follow-up |
| Fall Line wrecks `RUT_FallLineWreckHull`, `RUT_FallLineWreckCarapace` (patch-added children of the families; placeholder art) | `src/RimUtinni/UtinniPatches/Patches/RUT_FallLineWrecks.xml` | built |
| Weathering `RUT_WreckWeathering_FallLine` ("fresh-fallen", loot tier +1, `extraLoot RUT_SalvageLoot_Imperial`) | `src/RimUtinni/UtinniPatches/Defs/RM_WreckWeatheringDefs/RUT_WreckWeatherings.xml`, `.../ThingSetMakerDefs/RUT_SalvageLoot_Imperial.xml` | built |
| Fall Line tile mutator `RUT_FallLine` + the arrivals incidents `RUT_FallArrival` (2.0), `RUT_FallSurvivor` (0.8), `RUT_LabRatFalls` | `src/RimUtinni/FallLineArrivals/` | built |

Lore that binds it (`design/Jawa/worldbuilding/biomes/fall_line.md`, ruled 2026-09-05): wreckage is
**fresh and renewable**, "a slow rain of other people's ruined machinery"; "**Exogenous organics** — falling
stores and cargo"; salvager camps, "nobody's faction"; and **"The Empire claims the salvage rights … It cannot
enforce any of it past bowshot of the garrison"** (Ashgarrison).

### 1b. Quest machinery we already ship that this can copy

| precedent | path | what it gives |
|---|---|---|
| **Swallowed Navigator log** (`ROT_NAVIGATOR_LOG_SITES_1`): a log reads out entries as letters, and chosen entries call `QuestUtility.GenerateQuestAndMakeAvailable(RM_NavigatorSalvageSite, slate)` with `map`, `points` and an optional preset `siteTile` | `src/RimMandrake/TheRot/Source/RM_NavigatorLog.cs` (`TryRevealSite`), quest in `src/RimMandrake/TheRot/Defs/Misc/RM_NavigatorLog.xml` | **the exact "lead becomes a quest" call**, already proven in our code, including the `script.CanRun` guard. The quest is a vanilla item-stash site: `GetSiteTile`, `GetSitePartDefsByTagsAndFaction`, `GetDefaultSitePartsParams`, `Util_GenerateSite`, `SpawnWorldObjects`, `AddItemsReward`, `End` |
| **The Claim** (`RUT_Jawa_TheClaim`): "Something came down past the ridge", walk to an item-stash site | `src/RimUtinni/UtinniPatches/Defs/QuestScriptDefs/Jawa_TheClaim.xml` | a pure-XML fallen-salvage site quest, provenance-commented node by node |
| **Salvage rumour item** (`RUT_Jawa_ClaimRumour`): read it and it hands you The Claim, via vanilla `CompProperties_Usable` + `UseEffectGiveQuest` + `UseEffectDestroySelf` | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/Jawa_ClaimRumour.xml` | **an item-as-lead with zero C#**. Its header records a ruled two-lane supply, *bought* (Hutt Cartel) and *found* (wreck loot), "purchase-only is explicitly forbidden"; neither lane is wired yet |

### 1c. The property and Bazaar side (connect, do not build into)

| piece | path | state |
|---|---|---|
| RimProperty ledger: `GameComponent_PropertyLedger`, `ClaimEngine`, `ClaimRecord` (claimant pawn/faction/commons, strength, basis, time), `ClaimBasis` `Stolen / Purchased / ClaimFeePaid / Gifted / Inherited / Looted` | `src/RimMandrake/RimProperty/Source/` | built |
| Salvage claim fee: pay a fee on a thing and record `ClaimFeePaid` (`FloatMenuOptionProvider_PaySalvageClaim`, `PropertyEngine.Fire`) | `src/RimMandrake/RimProperty/Source/SalvageClaim/` | built |
| Bazaar droid modules `RM_ManifestDecoder` (registry of lost and stolen goods) and `RM_TransponderScanner`, intel layers `RM_BazaarIntel_D2_Registry` / `_D3_TransponderScan` | `src/RimMandrake/TheBazaar/Defs/Modules/RM_BazaarModules.xml`, `.../Intel/RM_BazaarIntel.xml` | the defs exist; the stolen-goods mechanic behind them is **unruled** (`BAZAAR_STOLEN_GOODS_PROPERTY_1`, needs owner) |

### 1d. Pitches that already point here (unruled)

- `design/RimMandrake/jawa_scavenge_system_pitch_2026-10-03.md` option **E, "Reading the wreck (survey)"**:
  an Intellectual survey job that sometimes yields "a manifest line pointing to cargo still out there". Its
  own warning: *"each lead needs a quest to point at. Without content it is a tooltip."*
- `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §3e lists fall-zone lost cargo as a hoist site.

**So:** the injection (wreck fall + Fall Line wrecks + Imperial loot), the lead-to-quest call (Navigator log),
an item-as-lead with no C# (rumour item), a site quest template (The Claim / Navigator site), and an ownership
ledger (RimProperty) all exist. What does not exist is the **manifest** itself and the rule that turns one
into a lead.

## 2. Options

**The decision.** What a "manifest" *is* in play, which decides everything downstream. Three axes are
legitimate here: **how much it costs to build**, **whether the lead is tied to a particular wreck and owner**
(the thing that makes it a claim on someone's property, per the owner's warning), and **who starts it**,
the player by acting or the world by falling. The most decision-relevant axis is the second, because the
item exists to make *someone else's lost cargo* a story.

**Floor every option must clear:** reads an injection that already exists; produces a quest that is
offerable without the storyteller (a deterministic trigger for testing); uses vanilla quest nodes for the
quest itself; does not put code into The Bazaar; and never assumes the player came from the fall. All three
below clear it.

### Option A: The manifest is a loot item (a "cargo chit")

**Question it answers:** what is the cheapest thing that makes the idea real?

- **Player flow.** A colonist carefully strips a fresh-fallen Fall Line wreck. Sometimes the haul includes a
  *cargo chit*, a data slate from the wreck's hold. A colonist reads it: a letter says a cargo pod from this
  ship came down some distance away, and a quest appears. Chits can also be sold or bought (the rumour item's
  "found" and "bought" lanes, finally wired).
- **Manifest → lead.** The chit **is** the lead. It enters through `RUT_SalvageLoot_Imperial` (the Fall Line
  weathering's `extraLoot`) as a low-chance `ThingSetMaker_Sum` option. Because `RM_CompSalvageLoot` only rolls
  on **careful deconstruct**, a smashed wreck never yields one.
- **Lead → quest.** The chit is a copy of `RUT_Jawa_ClaimRumour`'s shape: `CompProperties_Usable` +
  `UseEffectGiveQuest` (quest `RUT_FallCargoSite`) + `UseEffectDestroySelf`. The quest is an item-stash site
  cloned from The Claim / `RM_NavigatorSalvageSite`: `QuestNode_GetMap`, `GetSiteTile`,
  `GetSitePartDefsByTagsAndFaction`, `GetDefaultSitePartsParams`, `Util_GenerateSite`, `SpawnWorldObjects`,
  `WorldObjectTimeout` (`isQuestTimeout`), `End`. `isRootSpecial`/`rootSelectionWeight 0`, so only the chit
  fires it.
- **Which injection.** The Fall Line weathering (`RUT_WreckWeathering_FallLine` → `RUT_SalvageLoot_Imperial`)
  on any fresh-fallen wreck, whether it fell (`RUT_FallLineWreckFall`) or was ever scattered. Works today with
  the wreck fall at `baseChance 0`.
- **Bazaar connection.** None in code. A chit is an ordinary tradeable item, so a Hutt trader can stock it
  later (one stock line) and the Bazaar's registry layer can flag recovered cargo by **its own** rules if
  they are ever ruled.
- **Build cost.** S. XML only: one item, one quest def, one loot-table row, text. No C#.
- **Risks.** The lead is **generic**: the chit does not know which wreck it came from or who owned the cargo,
  so the owner warning ("a claim on another party's property") lives only in the text. The quest repeats if
  chits are common, so it needs `minRefireDays` thinking and a low chance.
- **Unique contribution.** The only option that ships with zero C# and completes the rumour item's ruled
  "found and bought" supply.

### Option B: The manifest is a record on the wreck (survey, owner and claim)

**Question it answers:** what makes the lead a real claim on someone's property?

- **Player flow.** A fresh-fallen wreck carries a manifest: whose ship it was (the Empire, a Hutt freighter,
  an independent hauler) and what its hold carried. A colonist **surveys** the wreck (scavenge pitch option E,
  a short Intellectual job). The wreck's inspect pane then names the owner, and sometimes says *"Hold manifest:
  2 cargo pods unaccounted for."* Choosing to follow it offers a quest. The cargo site is labelled with that
  owner. Picking it up records it in RimProperty as **Looted from <owner>**; paying the owner's salvage fee
  first (the existing `PaySalvageClaim` verb, at the site) records **ClaimFeePaid** instead. That is the
  choice: cheap and owned-by-someone, or paid for and clean.
- **Manifest → lead.** A small comp on the Fall Line wreck families, `RM_CompWreckManifest`, rolls its
  manifest **when the wreck spawns** (owner faction picked from a weighted list in XML, a cargo kind, and a
  lead chance), and saves it. Surveying reveals it. A lead exists when the roll says "pods unaccounted for".
- **Lead → quest.** Exactly the Navigator-log call: `QuestUtility.GenerateQuestAndMakeAvailable(RUT_FallCargoSite, slate)`
  with `map`, `points`, the owner faction as `owner`, and the cargo `ThingSetMakerDef` preset, behind
  `script.CanRun`. The quest is the same vanilla item-stash shape as A, plus an end node carrying
  `goodwillChangeAmount` / `goodwillChangeFactionOf $owner` if the player is caught (that consequence chain is
  the Bazaar item's to rule; here it is a single, switchable goodwill line).
- **Which injection.** The Fall Line wreck defs (`RUT_FallLineWreckHull`, `RUT_FallLineWreckCarapace`) through
  their families, however they arrive. Any other biome's family can opt in later by adding the comp.
- **Bazaar connection.** RimProperty is the hand-off, not The Bazaar: recovered cargo carries a
  `ClaimRecord` (`Looted` or `ClaimFeePaid`, with the owner). If the Bazaar's `RM_ManifestDecoder` is ever built,
  it **reads that record**; this design writes nothing into The Bazaar.
- **Build cost.** M. One comp + one survey JobDef/JobDriver + one C# offer call (copy of `TryRevealSite`), one
  quest def, a RimProperty write on pick-up, Mod Settings toggles, text per owner.
- **Risks.** Builds half of scavenge-pitch option E, which the owner has not ruled; adds a step on every wreck
  unless survey stays optional. Collides with Bazaar ruling 6 (*"fall-salvage provenance reads as SAFE"*): if
  fall salvage is safe, a `Looted` record on it is wrong. That needs his word (Q2 below).
- **Unique contribution.** The only option where the lead belongs to a specific wreck and a specific owner,
  so the owner warning becomes play, and the only one that feeds RimProperty.

### Option C: The fall itself brings the lead (news of scattered cargo)

**Question it answers:** what if the world starts it, with no player step at all?

- **Player flow.** A wreck fall lands on the map. Some falls are *break-ups*: the letter says the ship broke up
  on the way down and its cargo pods came down past the horizon, and a time-limited quest is offered at once.
  Somebody else heard it too: the site may hold a salvager camp, or the Empire's recovery crew from
  Ashgarrison, racing you to it. A race, not a scavenger hunt.
- **Manifest → lead.** There is no manifest object. The **fall event** is the lead. A new optional field on
  `RM_WreckFallExtension`, for example `followUpQuest` + `followUpChance`, is read after `RM_WreckFall.Drop`
  succeeds.
- **Lead → quest.** The incident worker calls the same `GenerateQuestAndMakeAvailable` with `map`, `points`;
  the quest is the item-stash site with a short `WorldObjectTimeout` and a rival site part (vanilla site parts
  via `GetSitePartDefsByTagsAndFaction`, tag chosen to suit the rival).
- **Which injection.** `RUT_FallLineWreckFall` (and through the shared worker, any future fall: Miasma flotsam,
  the Cracked Lands flood strike). **Needs the wreck fall made to fire on Fall Line tiles**, which is the
  already-named unbuilt follow-up; at `baseChance 0` nothing ever offers it.
- **Bazaar connection.** None. The rival is an existing faction, so the consequence is ordinary goodwill.
- **Build cost.** S–M. ~20 lines in the shared Wreckage worker (an engine change in `mandrake.rm.wreckage`, so a
  DLL rebuild and its review) + one quest def + the renewal turned on.
- **Risks.** Couples a quest to an engine shared by every biome; the race reads like vanilla's "item stash"
  offers, so it needs strong text to feel like *this* place. Nothing ties the cargo to an owner beyond the rival.
- **Unique contribution.** The only option that needs no player action and that makes the renewal (the Fall
  Line's signature, "salvage taken is replaced") produce story as well as steel.

**Why only three.** A fourth candidate, "the Hutt Cartel sells cargo leads", is option A's *bought* lane, not
a new question, so it is folded into A.

## 3. Recommendation

**Option A first, built so that B can replace the chit's generic text later.** It is S-cost XML that reuses
the rumour item and the Navigator site wholesale, works today without turning the wreck fall on, and touches
neither The Bazaar nor the unruled survey pitch. B is the richer end state, but it waits on two rulings he has
not made (the survey job, and whether fall salvage counts as owned).

Cheapest real test (when built, not now): dev-spawn the chit, read it, confirm the quest appears and its site
spawns; run `skills/rimworld-quests/scripts/validate_quest.py` on the quest def before any load.

## 4. Questions for the owner (card-ready, plain language)

1. **Which way should a lost-cargo lead start?** (a) a data chit that sometimes turns up when you strip a fresh
   wreck, and that can also be bought or sold; (b) your colonist surveys a wreck and learns whose ship it was and
   what's missing; (c) a falling ship breaks up and you race others to its cargo. Or a mix?
2. **Is cargo from the fall someone's property, or free salvage?** Your Bazaar ruling says fall salvage reads as
   *safe*. Your note on this item says lost cargo is *a claim on another party's property*. Should recovered fall
   cargo count as owned by the ship's owner (so selling it can draw trouble), or as free?
3. **Who owns the fallen ships?** Mostly the Empire (they claim the salvage rights), or a mix of the Empire,
   Hutt freighters and independent haulers?
4. **If you take cargo the owner wanted back, what happens?** Nothing; a goodwill hit with that owner; or an
   option to pay their salvage fee at the site and keep it clean?
5. **How often?** Rare and memorable (a few per year), or regular enough to be a steady side income?
6. **Fall Line only, or any wreck?** Should only the Fall Line's fresh wrecks carry leads, or older wrecks in
   other biomes too (with older, colder leads)?
