# Jawa scavenging system: inventory and pitch (DRAFT, for owner cards)

BENCH design pass, 2026-10-03. Design only. Item: `SALVAGE_WRECKAGE_EVERYWHERE_1`.

The owner, 2026-10-03, answering the smash-versus-care card: careful salvage gives loot and the
rare-part chance scales with skill, and *"It's so important we might even think about if we can
expand this into a richer system. Jawa SCAVENGE. It's what they do, and they're good at it."* This
pitch answers the second half. Placement and the wreck families are in
`design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md` (the "salvage design" below).

## 1. What already exists

Read from source 2026-10-03. Paths are under `/home/mandrake/rm/bench` (Windows mirror
`D:\Luke\dev\RimMandrake\`). The finding up front: **the clan's identity promises salvage skill that no
mechanic delivers.** The Jawa xenotype's own short description reads *"an unmatched instinct for
salvage"* and *"they will strip a wreck to its frame and make it run again"*
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml`), and none of its genes
touches salvage. Its nearest genes are `AptitudeStrong_Construction` and `AptitudeStrong_Crafting`, and
vanilla deconstruction reads no skill at all.

### 1a. Engine facts (RimSage, decompiled 1.6, read 2026-10-03)

- Deconstruct yield is `count × def.resourcesFractionWhenDeconstructed`, with no skill or pawn term
  (`GenLeaving.GetBuildingResourcesLeaveCalculator`). Smashing (`KillFinalize`) returns 25%.
- `JobDriver_Deconstruct` trains **Construction** at 0.25 XP per tick, and its work is
  `WorkToBuild` clamped to 20-3000. `FinishedRemoving()` is the one place that knows both the pawn and
  the building, just before `Destroy(DestroyMode.Deconstruct)`.
- So **every skill-scaled option below needs one Harmony hook** at `FinishedRemoving` (a prefix that
  stashes the pawn). Ninefold already patches that method with a postfix
  (`src/RimMandrake/Ninefold/Source/Patch_BuildingDeconstructed.cs`), so the hook point is proven.

### 1b. Salvage and scavenging pieces already built or designed

| piece | what it does | where | state |
|---|---|---|---|
| **Wrecked Machines** | three-tier repair ladder (Wrecked → Kludged → Repaired) for big machines; one pilot (`RM_WM_AutomatedSmelter_*`), research-gated Repaired tier, Mod Settings | `src/RimMandrake/WreckedMachines/` (`DESIGN.md`, `MACHINES.md`); doctrine `design/Jawa/wrecked_machines_resurrection.md` | pilot built; resurrection design ruled 2026-08-31: *"repair existing broken machinery ... about all the Jawa can do"*, study via Research Reinvented "Analyse", sacred scrap as a clan policy |
| **Ancient machines grade ladder** | Wrecked / Kludged / Refurbished at a 0.75 ceiling for every ancient thing; worth scales with size | `design/RimMandrake/ancient_machines_design.md` | design; notes a Wrecked relic *"appraises at nothing"* today |
| **Salvage loot comp** (proposed) | Deconstruct-only loot roll by family tier, smash gives slag | salvage design §3c | designed, unbuilt |
| **Droidworks part drops** | a killed droid drops each legal part at 60% with a **quality** roll (`QualityUtility.GenerateQualityTraderItem`) | `src/RimStarWars/Droidworks/Source/Droidworks/CompDWPartDropper.cs`, `CompDWHeadDropper.cs`, `Defs/ThingDefs/Parts_Droidworks*.xml` | built; the one place salvaged parts already carry a grade |
| **Droid Repair Jobs** | neighbours bring broken droids; the part you fit decides reputation versus silver | `src/RimUtinni/DroidRepairJobs/` | built; a ready buyer for graded parts |
| **The Bazaar** | trade window with intel layers gated by Social and by found artifacts; `RM_HagglerModule`, `RM_ManifestDecoder` (goods provenance, stolen or fall-salvage), `RM_PriceAlmanac` | `src/RimMandrake/TheBazaar/`; `design/RimMandrake/bazaar_trade_window_design.md` §4 | slice 1 built; price engine and intel items filed (`BAZAAR_PRICE_ENGINE_1`) |
| **Antiquities** | artifacts examined at a Reading Station; duration scales with an Intellectual+Artistic average (skill 0 → 1.5×, 20 → 0.5×); unlocks the 17th research tree | `src/RimUtinni/Antiquities/Source/JobDriver_ExamineAntiquity.cs`, `CompAntiquity.cs` | built; **the working precedent for an examine-to-learn job with a skill curve** |
| **Jawa Scavenging research tab** | 53 research rows under "Jawa Scavenging"; the first rite, `RUT_Rites_ScrapShrine`: *"nothing taken from the sand is junk until the clan says so"* | `src/RimUtinni/ResearchRetag/Defs/ResearchTabDefs/RUT_Tree_Defs.xml`, `src/RimUtinni/Rites/Defs/RUT_Rites_Research.xml` | built; the rite's sentence is an appraisal step in lore form |
| **Salvage that arrives** | Blue Desert ablation incidents; Cracked Lands recede drops; `Jawa_TheClaim` quest; ScavengerEvents (pod crash, ship break, survival pod) | `src/RimMandrake/BlueDesert/Source/RM_AblationSalvage.cs`, `src/RimMandrake/FloodedCanyon/Source/RM_MapComponent_RecedeAftermath.cs`, `src/RimUtinni/ScavengerEvents/Source/` | built |
| **Placed wrecks** | Scald wrecks, scrapfields slag, ground hulk, crawler-road wrecks, crashed ship, AssailantSalvage props (22, unwired) | salvage design §1a | built |
| **Wreck hazards** | vermin nests on wrecks (`RM_CompProperties_VerminNest`); scrap-hoarding creatures (`CompScrapHoarder`) | `src/RimMandrake/ShipVermin/`, `src/RimStarWars/SWBestiary/Source/BeastMechanics/CompScrapHoarder.cs` | built |
| **Salvage palette** | which defs actually yield anything when stripped (315 usable) | `design/Jawa/art/SALVAGE_PALETTE.md` | built instrument |
| **Lore** | the meet's *"finest appraiser of drive systems"*; a Jawa who *"keeps the good salvage. All of it. On himself"* | `design/Jawa/bridge/INHABITED_CAST_JAWA.md:142,191` | cast text only |

**Not found anywhere:** an appraisal or identify step, a hidden-value part, a salvage tool or gear
stat, a salvage trait, a scavenging work type, or any stat that a salvage outcome reads. Vanilla has
none either. Every one of those is new.

## 2. Options

Each option is a separate piece that can be built alone unless it names a dependency. Costs are rough
(S under a day of FOUNDRY work, M a few days, L a week or more) and count art where art is owed. Every
option ships behind its own Mod Settings toggle, and all-off is the ruled baseline (option A).

### A. Skill-scaled stripping (the ruled baseline)

The salvager's skill sets the rare-part chance on the salvage design's loot roll, and can also lift the
bulk yield from a poor hand's ~50% to a master's full `resourcesFraction`. Work speed stays vanilla.
- **Buys:** the owner's ruling, nothing more. A good Jawa visibly brings home more.
- **Costs:** S. One Harmony prefix at `FinishedRemoving`, one curve in the loot comp. No art.
- **Limit:** invisible until the loot lands; the player never *decides* anything.

### B. Sorting the haul (appraisal)

Stripping a wreck yields its bulk metal at once plus a **salvage lot** (a crate item, "unsorted
salvage from a scalded hull"). A Jawa sorts lots at a bench, a job built on the Antiquities examine
pattern, and sorting is where the loot roll happens. The bench is the Scrap Shrine the rites tree
already names: *"nothing taken from the sand is junk until the clan says so"*, now true in play.
- **Buys:** a second skill moment (sorting can read Crafting while stripping reads Construction), a
  home-base ritual after every expedition, and loot that can be carried home unsorted and sorted in safety.
- **Costs:** M. One item family (per loot tier), one bench, a WorkGiver and JobDriver, settings. Art: one
  bench, three crate tiers.
- **Limit:** extra hauling. A lot that just turns into the same loot on the bench is busywork unless C
  or H gives the sort something to reveal.

### C. Hidden-value parts (identify)

Some rolls come out **unidentified**: "a corroded drive assembly". It sells as scrap and does nothing
until appraised. Appraisal reveals what it truly is (a dead part, an ordinary component, or a rare
part such as a hyperdrive motivator shard in the Star Wars layer) and its **quality**, using the vanilla
quality roll Droidworks already uses for droid parts. A better appraiser reveals more value from the
same part, so a master sees a "good" part where a novice saw an "awful" one.
- **Buys:** the treasure-hunt moment a scavenger game lives on; makes the appraiser a specialist role;
  feeds Droid Repair Jobs (a superior part buys reputation) and the Bazaar.
- **Costs:** M. A per-tier unidentified item plus an identify step (rides B's job, or a standalone job
  if B is not built). The skill-to-quality curve is a balance number. Art: one generic "corroded part"
  sprite per size.
- **Limit:** depends on B or its own job. Must never make every find a mystery, or players stop caring.

### D. Salvage tools and droid help

One new stat, **salvage yield**, that A and C read, fed by: tools (a hydrospanner, a cutting torch,
scanner goggles as apparel or gear), and a Droidworks salvage module so a droid can strip slowly but
safely. A Jawa gene and traits (option F) feed the same stat.
- **Buys:** a progression path through research and crafting, not only through skill; gives the
  Jawa Scavenging research tab something to unlock; a use for droids on hostile maps where colonists die.
- **Costs:** S for the stat and two or three tools; M with the droid module. Art per tool.
- **Limit:** stat creep; needs one shared stat so the option F and D bonuses do not stack into nonsense.

### E. Reading the wreck (survey)

Before stripping, a Jawa **surveys** a wreck (Intellectual, a short job). The survey reveals its loot
tier, its hazards (a vermin nest inside, a live charge, a structural collapse risk) and, sometimes, a
**lore fragment or lead**: a ship's name, a manifest line pointing to cargo still out there (the
unruled `FALLZONE_LOST_CARGO_QUESTS_1` idea), a log for the Antiquities tree.
- **Buys:** turns a wreck from a resource node into a place with a story; lets the player choose which
  wreck is worth the trip on a lethal map; links salvage to quests and lore.
- **Costs:** M for the job and readout; the real cost is **writing**: fragments per weathering, and each
  lead needs a quest to point at. Without content it is a tooltip.
- **Limit:** adds a step on every wreck unless it stays optional (strip unsurveyed and take your chances).

### F. Salvage specialists

A Jawa xenotype gene ("junk sense": salvage yield up, so the xenotype's own description becomes true),
and two or three traits (a "scrapper's eye" who appraises well, a "smasher" who strips fast and breaks
rare parts). Optionally a separate **Salvaging work type**, so the player assigns scavengers apart from
builders.
- **Buys:** the identity claim made mechanical; colonists who are known as the clan's appraiser;
  cheap, because it is mostly XML.
- **Costs:** S for gene and traits (they need D's stat to act on). A new work type is S-M and moves
  deconstruction of wrecks out of Construction, which players will notice.
- **Limit:** a gene on the xenotype changes every Jawa, including NPC Jawa traders.

### G. The cut plan (choosing how to strip)

A gizmo on each wreck picks how it is taken apart: **Quick** (fast, full bulk, rare parts can break),
**Careful** (slow, the rare chance and the skill bonus apply in full), or **Gut for one part** (aim at a
single named part such as the drive or the power cell, and wreck the rest). Hazards fire during the job
(a live charge sparks, a nest bursts, a panel falls) with odds that fall with skill.
- **Buys:** the closest thing to a scavenging minigame inside RimWorld's job model: a real decision on
  every wreck, which ties the lethal-map tension to time spent on site.
- **Costs:** M-L. A comp with a gizmo, three job variants or one job with modes, hazard events, and
  balance. No new art beyond icons.
- **Limit:** micromanagement at scale; the default mode must be right so players can ignore it.

### H. Selling what you found

Identified, graded parts carry their grade into trade: an honest grade raises the price, and in The
Bazaar a Jawa can **pass junk off as better** in the haggle duel, at a reputation risk when the buyer
finds out. Fall-salvage provenance already reads as "unowned, safe" in the Bazaar's manifest decoder.
- **Buys:** the Jawa trader fantasy completed: find it, name it, sell it for more than it is worth.
- **Costs:** S if the Bazaar price engine and haggle duel exist; they are filed, not built
  (`BAZAAR_PRICE_ENGINE_1`, `BAZAAR_HAGGLE_DUEL_1`). Needs C.
- **Limit:** blocked on the Bazaar slices; until then grades only change vanilla market value.

### Summary

| option | cost | depends on | what the player gets |
|---|---|---|---|
| A skill-scaled stripping | S | the salvage loot comp | better Jawa, better haul (ruled) |
| B sorting the haul | M | A | a home-base sorting ritual |
| C hidden-value parts | M | B or its own job | treasure-hunt reveals, an appraiser role |
| D tools and droid help | S-M | none | progression through research and gear |
| E reading the wreck | M + writing | none | wrecks with stories and leads |
| F specialists | S | D's stat | the xenotype claim made true |
| G cut plan | M-L | A | a decision on every wreck |
| H selling finds | S | C, Bazaar slices | profit from naming things well |

## 3. Recommended core

**A + B + C + D's stat with F's gene.** In play: a Jawa strips a wreck on a lethal map (Construction
sets the bulk), carries home unsorted lots, and at the Scrap Shrine bench the clan's best appraiser
(Crafting) turns a few of them into named, graded rare parts that the rest of the clan would have
called junk. One stat, salvage yield, takes the skill, the Jawa gene and the first tools, so the
xenotype's promise is finally a number.

Why this core: it is the smallest set where the player **makes a choice and sees a reveal**, it reuses
three proven patterns (the Antiquities examine job, the Droidworks quality roll, the Ninefold
deconstruct hook) and needs little art (one bench, crate tiers, one corroded-part sprite per size).
Rough total: M to L, about two FOUNDRY weeks with the salvage design's engine.

**Next, in order:** G (the cut plan) once players have hauls worth protecting; E (reading the wreck)
when the lore leads have quests to point at; H when the Bazaar slices land. The order is a
recommendation; each is its own card.

**What it touches in the salvage design:** the loot comp (§3c) stops dropping the rare roll on the
ground and drops a salvage lot instead when B is on; with B off it behaves exactly as §3c says.

## 4. Questions for the owner

Eight questions on two cards in `Transient/jawa_scavenge_cards_2026-10-03.json` (each element of `cards` is
one AskUserQuestion payload). Card 1 settles the core: its size, which skill strips, whether rare finds
come out unidentified, and how the clan improves beyond skill. Card 2 settles what comes after: the cut
plan, reading the wreck, the desert hulk's conflict with the placement law (salvage design §3d-i), and
whether grades change trade prices. Nothing here is built until card 1 is answered; FOUNDRY's build
item is filed from the answers.
