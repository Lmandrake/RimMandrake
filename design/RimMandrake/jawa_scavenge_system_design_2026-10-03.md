# Jawa scavenging system: synthesis design (DRAFT for owner decisions)

BENCH design pass, 2026-10-03. Item: `SALVAGE_WRECKAGE_EVERYWHERE_1`. Design only; nothing built.

## 0. What the owner ruled, and what this document does

Owner, 2026-10-03, by question card with typed answers (full text in the item's ledger notes):

1. **The FULL scavenging process.** *"rooms filled with 'salvage pieces awaiting sorting, stripping,
   processing' back in the ship. SUPER Jawa. I really didn't like how vanilla rimworld just popped out
   components or metal or 'chunks' that you lugged back... Big, nasty, complex pieces of tech or systems
   brought back that you work on/work down. Or you give up on them and just smelt them, but that's
   unholy (literally)."*
2. **Leaning to a new Salvaging skill** that replaces every recycle/disassembly skill use, because
   *"taking things apart is NOT the same thing as building them"*, but *"careful not to let this turn
   into a total conversion... planning first... then make the decision together."*
3. **Appraisal for rare finds only.**
4. **Tools help, droids help, and a whole scavenger setup at the ship**: a messy, rounder
   "scavenger's nest", not a rectangular bench. Incompatibility with other recycle/repair mods declared
   *"immediately and loudly in code"*.

This document is the synthesis: one loop that uses every ruling, built from the pitch
(`design/RimMandrake/jawa_scavenge_system_pitch_2026-10-03.md`, options A-H), the placement law
(`design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md` §3d-i), and three research notes
in `Transient/scavenge_research/` (mod survey, Jawa canon, skill feasibility). It replaces the pitch's
"recommended core", which the owner overruled upward. The skill is **not decided**: §4 lays out the
narrow version and §11's first card is the decision he asked to make together.

**One finding the owner has not heard yet.** Ninefold already charges **Rekko a Large penalty for
every deconstruction a player pawn finishes**
(`src/RimMandrake/Ninefold/Source/Patch_BuildingDeconstructed.cs`, postfix on
`JobDriver_Deconstruct.FinishedRemoving`), on the reading "scrapping something still repairable". In a
game whose core loop is stripping wrecks, that makes the god of salvage hate the clan for salvaging.
The design below moves the large penalty to where his doctrine actually puts it: **smelting** and
**scrapping the repairable**, while careful stripping of a dead wreck becomes the doctrine's
*"careful parts-deconstruction where repair is truly impossible (mourned)"*, a small or neutral delta
(`design/Jawa/divine_satiation_engine.md` §⑤ and §8b.A).

## 1. The loop in one picture

```
 WRECK on a hostile map (placement law)                     ARRIVALS (falls, ablation, recede)
   |  survey (optional, short): hazards, loot tier, which big pieces are inside, repairable?
   v
 STRIP ON SITE (cut plan: Careful / Quick / Gut-one-piece)  -> wreck becomes slag + SALVAGE PIECES
   |  pieces are big, heavy items with visible condition (HP) and a hidden worth
   v
 HAUL HOME to the SALVAGE HOLD (a room in the ship; pieces rot outdoors, keep indoors)
   v
 THE SCAVENGER'S NEST works each piece DOWN, one stage per job:
   SORT (what is it?) -> STRIP (pull sub-parts) -> PROCESS (clean into usable stock)
   |         \-- a rare few come out UNIDENTIFIED -> APPRAISAL at the nest's seat -> named, graded part
   |  or KEEP WHOLE (feed a Wrecked Machines repair, a droid job, or sell as-is)
   v
 OUTPUTS: steel, plasteel, components, graded parts, Star Wars parts (RUT_ layer)
   ...or GIVE UP: carry it to the FURNACE NOOK and smelt it. Fast, flat, skill-free, and unholy.
```

Three things this loop deliberately does: nothing usable pops out of a wreck on site (the owner's
complaint about vanilla); every decision has a cheaper, worse alternative the player can take
(Quick cut, smelting, keeping whole); and the home base gains a place that looks like Jawa live there.

## 2. The loop, stage by stage

### 2a. Find

Wrecks are where the placement law puts them (salvage design §3d-i: riddled deep nightside, high sea
floors, moderate/low hostile land, eroded Contagion, cleaned travelled land, fresh Fall Line) plus the
arrivals already built (Blue Desert ablation, Cracked Lands recede, ScavengerEvents, `Jawa_TheClaim`).
Nothing new here. The one dependency: every wreck family (salvage design §3a) gains a **piece list**
(§2c), so the family abstract defs are where this system plugs in.

### 2b. Survey (optional, short)

A right-click or gizmo on a wreck: **Survey**. A short job (about a tenth of the strip time) that reads
**Salvaging** (§4). It reveals, on the wreck's inspect pane:
- the loot tier (Scrap / Hull / Tank / Carapace / Sealed, salvage design §3c);
- **which big pieces are inside** and roughly what condition (a skilled surveyor sees more of the list
  and narrower condition ranges; an unskilled one sees "something heavy, maybe a drive");
- hazards: a vermin nest (`RM_CompProperties_VerminNest`), a live charge, a collapse risk;
- whether this is one of the **rare repairable few** (salvage design §8 ruling 2), so nobody strips a
  machine that could have been rewoken (Rekko's large sin, §3).

Skipping the survey is always allowed: strip blind and take your chances. Lore fragments and leads
(pitch option E's second half) are **not** in this build; they wait until there are quests to point at
(§12).

### 2c. Strip on site (the cut plan)

Stripping replaces vanilla deconstruction **for wreck-family buildings only** (player-built buildings
keep vanilla behaviour, §8). It is still the Deconstruct designation, so nothing new to learn; a gizmo on
the wreck sets the **cut plan**, default **Careful**:

| plan | time | what comes out | when you want it |
|---|---|---|---|
| **Careful** (default) | full | every piece on the list, condition rolled with skill and tools | normal |
| **Quick** | about half | the same pieces, condition lowered, each has a chance to break into slag; hazards fire more | a lethal map, a raid coming, a storm |
| **Gut one piece** | about a third | the one piece you pick (say the drive) at best condition; the rest becomes slag | you need one thing and cannot stay |

The wreck leaves **slag** (vanilla `ChunkSlagSteel`, or a weathered variant) and **salvage pieces**.
It does **not** leave steel, components or chunks you "lug back". The only raw stock on site is slag,
and slag is the cheap, bad answer.

Hazards fire during the strip job, with odds that fall with Salvaging skill: a live charge arcs
(a small EMP/burn), a nest bursts, a panel falls (a hit to the stripper). This is what makes Quick a
real gamble and the survey worth doing.

### 2d. Salvage pieces: the new item family

A salvage piece is the owner's *"big, nasty, complex piece of tech"*. Examples per family (names
INVENTED for tuning; Star Wars names live in the `RUT_` layer per Q11a):

| family | pieces (2-5 per wreck) |
|---|---|
| Hull | hull plate section, drive assembly, wiring loom, power coupling bank, sensor mast |
| Tank | tank shell section, valve-and-pump cluster, pressure manifold |
| Frame / speeder | repulsor pod, steering column, chassis spar, control console |
| Carapace (droid/mech) | limb assembly, torso shell, motivator housing, head cluster |
| Sealed | a cargo pod (contents rolled on sorting, one tier up) |

Each piece is a single, heavy item (mass 15-80 kg; one per stack), with:
- **condition = vanilla HitPoints.** No new number: it already shows on the inspect pane, already
  rots outdoors through vanilla deterioration, already burns. That rot is what makes the salvage hold
  (§2e) worth building.
- **a hidden worth**, rolled when the piece is cut out, from the family tier, the cut plan, the
  stripper's skill and tools, and the weathering. Until sorted the piece shows a flat "unsorted
  salvage" market value, so you cannot read its worth off the trade screen.
- **provenance**: a flag set only when map generation or an arrival placed the wreck it came from.
  Rebuilding, repairing, reinstalling or re-deconstructing anything never rolls pieces or rare loot
  again (GPT critique: closes the rebuild-farming loop).
- **one conserved recovery budget**: the piece carries its total recoverable material from the moment
  it is cut. Strip outputs, Process outputs, slag and smelting all debit that one pool, so Strip then
  Smelt cannot double-dip (GPT critique).
- **a work-down track** (§2f): the stages left on it. The graphic gets barer as stages complete
  (2-3 sprites per piece).

Hauling: a pawn carries one piece (stack limit 1, so carrying capacity cannot batch them; GPT
critique, `Pawn_CarryTracker.MaxStackSpaceEver`). Vanilla does not slow a carrier by mass, so heavy
pieces slow the carrier through a **`StatPart` on MoveSpeed** that reads the carried thing's mass (not a
hediff, which can outlive an interrupted job). A long walk back is a real cost, and the salvage sled
(§5) and hauling droids are worth having. Pieces are
ordinary items, so caravans, pods and the gravship move them as they move anything; their mass is
what makes a big haul a decision.

### 2e. The salvage hold

A room in the ship (or any roofed room) holding salvage racks. **No custom room role in the first
build** (GPT critique: decorated storage plus a capped thought delivers the hoard cheaply); a role is a
later polish if the thought needs a room to key on. Its effects:
- pieces inside do not deteriorate (vanilla indoor rule; nothing new);
- the room does not count as "messy" for Jawa: a gene-gated, capped thought, *"good salvage, piled high"*,
  positive for Jawa in a room with enough pieces in it, while non-Jawa get vanilla's ordinary clutter reaction;
- the **salvage racks** are a storage building drawn as heaps, not shelves, so a full hold looks like
  the owner's picture: rooms of pieces waiting to be worked.

### 2f. The nest: sort, strip, process

All work-down happens at the **scavenger's nest** (§5c). Revised after the GPT critique: Sort, Strip
and Process are **visible, resumable phases of one nest job per piece**, not three separate fetch
jobs, so 300 pieces are 300 jobs, not 900. Progress lives on the piece's comp (`PostExposeData`), so
a meal or a draft never restarts work and a hazard rolled at a checkpoint is never rerolled. The job
pauses after Sort only when the nest's policy asks for a keep/sell decision.

The player steers the **nest**, not each piece: a nest-level policy built on vanilla's
`BillStack`/`ThingFilter` conventions (which families to accept, an input radius, suspend, "keep
whole any piece of quality X or better", "smelt anything below Y% condition"), plus bulk Keep/Smelt
commands on a selection. The WorkGiver order is: finish a started piece, then pieces the policy
requests, then the nearest eligible piece; it reserves both the piece and the nest's interaction
cell, and respects forbidden items, allowed areas and danger. One interaction cell is one worker, so
facilities add speed and a second nest adds throughput.

The phases:

1. **Sort** ("what is it?"). Reveals the piece's identity and worth; a sealed pod opens. The clan's
   word for junk changes here: the Sorting Wheel's 27 bins (canon: 27 Jawaese words for junk, words
   unrecorded, so we coin them). The bins are flavour and facility art, not 27 mechanical categories (GPT critique). Sorting is the
   *Scrap Shrine* rite made true:
   *"nothing taken from the sand is junk until the clan says so"* (`RUT_Rites_ScrapShrine`).
2. **Strip** ("pull what is good"). The piece yields its **sub-parts**: smaller items (a component, a
   wiring bundle, a plasteel plate, a power cell, a graded part). **No child pieces**: a piece never
   spawns another piece (GPT critique: recursive pieces multiply value and jobs). Rare-tier rolls come
   out here, **unidentified** (§2g).
3. **Process** ("make it stock"). What is left is cleaned into usable stock: steel, plasteel, a
   component or two. This is where the bulk metal finally appears, **at home, after work**, never on
   site.

Per-piece gizmos (and the same commands in bulk) override the policy: **Keep whole** (the piece stops at Sort; it is a Wrecked
Machines repair input or a sale item, §2h), **Strip only** (stop before Process to keep sub-parts),
**Smelt** (give up, §3).

Skill effect, per stage: speed (all stages) and yield (Strip and Process), under the cap in §4c.
Every stage gives Salvaging XP.

### 2g. Appraisal (rare finds only)

Only **rare-tier rolls** come out as an **unidentified part** (GPT critique: a routine one-in-twenty
across hundreds of pieces is an appraisal factory, which is what the owner's "rare finds only" ruled
out): "a corroded drive assembly", "a fused motivator". It sells as scrap and does
nothing until appraised. **Appraisal** is a job at the nest's appraiser seat, built on the Antiquities
examine pattern (`src/RimUtinni/Antiquities/Source/JobDriver_ExamineAntiquity.cs`): duration from a
skill curve, and the result is:
- what the part truly is: a dead part (slag), an ordinary component, or a prize (in the `RUT_` layer, a
  hyperdrive motivator shard, a repulsorlift coil, a restraining bolt);
- its **quality**, using the vanilla quality roll Droidworks already uses for droid parts
  (`CompDWPartDropper.cs`). Revised after the GPT critique: the true quality is rolled **when the part
  is cut**, from the stripper's skill, tools and cut plan; appraisal **reveals** it and does not change
  it.

The appraiser's skill sets speed and the chance to succeed. A failed appraisal leaves the part
unidentified for a better appraiser to try, rather than grading it low forever (which would teach
players to hoard everything until a master is born). Ordinary
pieces never need appraisal; that keeps the reveal special (the owner's ruling 3).

### 2h. Outputs and where they go

| output | goes to |
|---|---|
| steel, plasteel, components | ordinary crafting |
| graded parts | Droid Repair Jobs (a superior part buys reputation), Droidworks repairs, sale |
| whole pieces kept at Sort | a **donor assembly**: an ordinary recipe ingredient. Keep one whole drive for a repair, or crack it at the nest for several components now (GPT idea; the opportunity cost is visible in the recipe) |
| whole pieces kept at Sort | Wrecked Machines: a matching piece is the **Kludge** input for a Wrecked machine (`src/RimMandrake/WreckedMachines/`), so repair and salvage share one economy |
| Star Wars parts | the `RUT_` layer's recipes and quests |
| sale | traders; the Bazaar's grade-aware price and the bluff wait for its haggle screen (§12) |

## 3. Smelting: the unholy fallback

Any piece, at any stage, can be **given up on**: the Smelt gizmo hauls it to the **furnace nook**, a
small, separate building (canon: the crawler's reactor melted scrap and droids; Legends: "energy
furnaces"). Smelting is:
- **fast and flat**: 25% of the piece's **remaining** recovery budget (§2d) as steel and slag, the same
  fraction vanilla uses. Vanilla's `Thing.SmeltProducts` applies 25% to a thing's cost list and adds
  `smeltProducts` unchanged; it knows nothing of a half-worked piece, so the nook computes the
  remainder itself (GPT critique). No skill reads it and no XP comes from it. Smelting is
  *"dumb labor"*, vanilla's own words for it, and that is the point.
- **unholy**, through what is already built: Ninefold's Rekko delta. The large penalty
  (`EventMagnitude.Large`) moves from every deconstruction to smelting a piece, scaled by the **recoverable value thrown away** and by repairability, never by piece count, per Rekko's taboo list (`design/Jawa/divine_satiation_engine.md`: *"smelting/scrapping above half
  condition"* is the small sin, *"destroying a repairable machine"* the medium one): a 10%-condition
  husk is mourned, a 90% piece is a sin, a piece from one of the repairable few is the worst.
  The penalty reads the condition **recorded when the piece was cut**, so damaging a piece first does
  not launder the sin (GPT critique).
  Jawa pawns also take a short thought, *"we unmade it"*.
- **kept apart**: the furnace nook cannot be placed within a few cells of the nest core (a place
  worker). The clan does this, but not in the nest.

The same Rekko re-scoping applies to the existing Ninefold hook: stripping a wreck that the survey (or
the family def) marks **not repairable** becomes a small or neutral delta ("mourned"); stripping one
of the **repairable few** keeps the large penalty. This is a change to
`src/RimMandrake/Ninefold/Source/Patch_BuildingDeconstructed.cs`, owned by whoever owns Ninefold, and it
is in the build plan (§9 phase 1) because shipping the loop without it would punish the core loop.

Vanilla smelting of **weapons and apparel** at the electric smelter stays available and stays skill-free
(25%). The holy alternative is the nest's **strip for parts** bill on weapons and apparel: slower,
Salvaging-scaled yield up to about 40% (under the cap), no Rekko penalty. That is the Recycle This
replacement (§6), inside the nest rather than a new designation.

## 4. The Salvaging skill

### 4a. What the feasibility study found

(`Transient/scavenge_research/salvaging_skill_feasibility_2026-10-03.md`, RimSage-read 1.6 source.)
- A `SkillDef` is XML-addable and the engine iterates all of them: every pawn gets a record, old saves
  add it on load with a warning, pawn generation rolls it, the Biotech aptitude and passion genes for
  it are **generated automatically**, and neurotrainers and skill books pick it up.
- What it does not get for free: **a 13th row on the character card** (one extra row very likely fits
  with about 4 px to spare on the vanilla card; with Vanilla Skills Expanded, RimHUD and Numbers
  redrawing skills, UNMEASURED), five gene icons, and meaning: every taking-apart act is hardcoded to
  Construction or Crafting and must be re-pointed.
- **No installed mod adds a SkillDef** (MEASURED across both roots; the whole-tree grep finished and
  confirmed it). We would be the first: no precedent, no collision.
- Vanilla's most salvage-shaped acts carry almost no skill today: deconstruct yield is a flat 50%,
  smelting a flat 25% and deliberately skill-free. So the skill **invents** skill play there rather than
  replacing it. That is where its identity lives and where its balance risk lives.
- The alternatives (a stat only, a pseudo-skill hediff, a work type on existing skills) cannot give
  salvage a talent of its own that grows with use without either tying it to Construction/Crafting
  (the "good builder = good salvager" outcome the owner rejected) or writing our own skill system.

### 4b. The narrow version this design proposes (revised after GPT)

`RM_Salvaging`, in the franchise-free `RM_` mod (§9), with **one** WorkType, *Salvage*
(`relevantSkills` Salvaging), placed after Construction in the Work tab. The jobs never read the skill
directly; they read two stats, `RM_SalvagingSpeed` and `RM_SalvageYield`, whose `skillNeedFactors`
name Salvaging. That keeps the stat route open as a fallback with no job rewritten (GPT critique).

The draft re-pointed **all** deconstruction to the new skill. GPT's sharpest point, taken: that is the
biggest blast radius in the whole design, and it is optional. Stripping a wreck already runs through
our own job and our own WorkGiver (§2c), so the skill can own every salvage act **without touching
ordinary deconstruction at all**. The recommended scope is therefore:

| act | today | with the skill (recommended) |
|---|---|---|
| strip a wreck (wreck families) | vanilla deconstruct | its own job, Salvaging throughout (§2c) |
| survey, nest work-down, appraise | new | Salvaging |
| strip weapons/apparel for parts (nest bill) | new; replaces Recycle This | Salvaging-scaled yield |
| shred a mechanoid (`ButcherCorpseMechanoid`) | Crafting XP and yield stat | Salvaging: pure XML re-point of the recipe and both stats |
| deconstruct your own buildings | Construction XP and speed, flat yield | **unchanged** in the recommended scope; the wider scope moves it to Salvaging (§11 card 1) |
| smelt anything (vanilla smelter, furnace nook) | no skill | **still no skill.** Smelting is the unholy fallback; giving it a skill would make it a craft |

Left exactly where they are in every scope: **building, uninstalling and moving (minify), repairing
buildings and mechs, hacking (Intellectual), disassembling your own mechs (Biotech), extracting slag
to steel, destroying weapons/apparel, removing floors.** Repair stays with Construction/Crafting
because the owner's distinction is *taking apart* versus *building*; Wrecked Machines repair is building.

If the wider scope is chosen, the deconstruct patch must not go on `JobDriver_RemoveBuilding`'s shared
toil (that also drives Uninstall, GPT critique); it goes on the Deconstruct driver and WorkGiver only,
and the yield change on `GenLeaving`'s Deconstruct branch keeps each def's own
`resourcesFractionWhenDeconstructed` as its base, not a universal 50%.

**The Jawa become legendary** by data, not code: the xenotype carries the auto-generated
`AptitudeRemarkable_RM_Salvaging` gene (plus a passion gene), and Jawa backstories gain Salvaging
`skillGains`. That also makes the xenotype's own words true: *"an unmatched instinct for salvage"*
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml`). Other factions' pawns
roll the skill like any other (0-4 plus backstory).

### 4c. Yield, and why the cap is not the safeguard

Wreck yield is governed by the conserved recovery budget (§2d): skill shifts piece condition, true
quality and the rare chance, and how much of the budget Strip and Process recover (about 50% for a
novice to 80% for a master with tools). The budget, not a stat's `maxValue`, is what stops loops (GPT
critique), and provenance (§2d) stops rebuild farming.

Only in the wider scope does ordinary deconstruction change: each def's own fraction up to that
fraction x 1.3 at skill 20, never below vanilla for anyone. With refund mods and rounding this is
plausible, not proven exploit-proof (GPT); the functional script must try a build-teardown loop.

### 4d. What changes for Construction

In the recommended scope, **nothing**: Construction keeps every job and all its XP, including tearing
down your own buildings. Jawa still do not become builders by stripping wrecks, because wreck stripping
was never vanilla deconstruction in this design. That delivers the owner's *"taking things apart is NOT
the same thing as building them"* where it matters (salvage) without a quiet nerf to every colony that
trains builders by teardown. The wider scope buys the full statement at that cost.

### 4e. Proof before commitment

Phase 0 (§9). Screenshots alone are not enough (GPT critique); the proof is a short functional script on
the quicktest list that checks: the Bio tab on a busy pawn (titled, ideoligion, extra faction rows); VSE
skill rows; RimHUD; Numbers; Character Editor; a recruited pawn and a newly generated one; an old save
loading (the per-pawn warning); passions and the auto-generated aptitude genes; a pawn whose work tags
disable the Salvage work type; a neurotrainer and a skill book; and one real strip job awarding XP. If
any of the UI four cannot show the row, the choice is a UI patch or the stat route (§11 card 1).

**A skill cannot be switched off live.** Once loaded, pawns, genes and backstories reference it. The
settings toggle (§7) is therefore restart-only, and "off" means the def still loads but no job reads it
and the stats fall back to Construction; the row stays visible. Removing the mod from a running save is
the vanilla missing-def path and is unsupported, like any mod that adds defs.

## 5. Tools, droids and the scavenger's nest

### 5a. Tools (one stat family, research-gated)

Vanilla has no tool system, so tools are **utility-slot apparel** (belts and goggles), which vanilla
already handles: worn, swapped, shown on the pawn. Each adds offsets to the two stats
`RM_SalvagingSpeed` and `RM_SalvageYield`, plus survey and appraisal accuracy, never a new number. All
unlocked in the existing *Jawa Scavenging* research tab (53 rows,
`src/RimUtinni/ResearchRetag/Defs/ResearchTabDefs/RUT_Tree_Defs.xml`), so the tab finally has things to
unlock.

| tool | helps | canon anchor |
|---|---|---|
| cutting torch | on-site strip speed; Quick cuts break fewer pieces | invented |
| hydrospanner | nest strip and process yield | canon ship-repair tool |
| scanner goggles | survey reads more of the piece list; appraisal quality shift | invented |
| salvage sled (repulsor) | removes the heavy-piece slowdown (§2d); carrying capacity cannot help, pieces stack to 1 | the crawler's repulsorlift suction tube |

### 5b. Droids

Two helps (the draft's third, an idle "nest assistant" droid at a dock, is cut on GPT's advice: new
idle-pawn logic for a speed bonus a facility already gives):
1. **Hauling pieces home.** Mechs and droids that haul already do it; the pieces are items.
2. **Strip droid**: the *Salvage* WorkType goes in a Droidworks droid's enabled work types, so a droid
   strips wrecks on a lethal map where a colonist would die. Whether droids shrug off the strip
   hazards (burn, EMP, collapse) is **unproven**, not automatic (GPT); an EMP arc should in fact be
   worse for a droid, which is a fair trade. Mechs fall back to `mechFixedSkillLevel` (10) for every skill check, so a droid
   salvager is middling, never legendary. **UNMEASURED** whether Droidworks droids are mechs (fixed
   level) or pawns with skill records; one read of the race defs settles it.

### 5c. The scavenger's nest

Canon gives no Jawa workshop (canon research §0); the shape is ours. It combines the research's
three strongest concepts: the **Sorting Wheel** (a central appraiser's stand with radiating bins: the
27 words for junk), the **Hung Hoard** (parts hanging from a ridge line) and the **Droid Corral**.

RimWorld footprints are rectangles, so roundness is built from **pieces, not one building**:
- **nest core** (3x3 footprint, art drawn larger and round, ragged rim): the Sorting Wheel's centre,
  the appraiser's seat, and the workstation every work-down job uses;
- **facilities**, linked to the core by the vanilla facility system (within a radius, any placement):
  sorting bins (each adds sort speed), a hung-hoard rack (keeps more pieces whole and raises true
  quality), a parts heap (process yield: bulk stock), an appraiser's lamp (appraisal), a droid corral
  rail (cosmetic, the canon droid pen). The player places them
  around the core freely, so every clan's nest is a messy ring, never a rectangle;
- **nest floor**: a buildable sand-and-oil floor terrain, so the ring reads as a place;
- the **furnace nook** is *not* a facility and must sit away from the core (§3).

**Specialisation, a GPT idea taken:** the core links at most **four** facilities, so a nest is built
for something: bins plus heaps is a bulk-metal nest, racks plus the lamp an intact-parts and appraisal
nest. Placement becomes an economic decision, and a clan with two nests runs two specialities. This is also the "whole setup at
the ship" the owner asked for, using a system players already understand from research benches.
Art cost: core, four or five facility sprites, floor texture, furnace nook.

## 6. Incompatibility, declared loudly

Two layers, both in the `RM_` mod:
1. **About.xml `incompatibleWith`** for the hard list. The vanilla mod manager shows a red warning
   when both are active.
2. **A startup check in code**: a `[StaticConstructorOnStartup]` class walks the hard and soft lists
   with `ModLister.GetActiveModWithIdentifier`. For each hard hit it logs a red `Log.Error` naming the
   mod and what conflicts, and the first time the main menu opens it shows a dialog: *"Recycle This
   (Continued) replaces the same jobs as Scavenger's Nest. Both are active. Remove one."* For each soft
   hit it logs a yellow warning and lists it on the settings page. The dialog has a "do not show again
   for this mod list" checkbox, keyed to the list's hash.

**Hard** (replace our feature head-on; from the mod survey §7):
`Mlie.RecycleThis`, `sneaks.recycle`, `SoulRetextured.RecycleThis`, `arvkus.simplerecycling`,
`futurplanet.disassemblemechanoid`, `Romyashi.Scavenging`, `Og.Repair.Your.Gear`.

**Soft** (touch the same defs or yields; warn, do not block):
`VanillaExpanded.Recycling`, `moja.salvagerubble`, `proxyer.dismantleancientjunk`,
`Meteores.AncientUrbanRuinsAllDeconstructible.AURAD`, `Hol.SmeltPatch`, `Thumb.BetterCremation`,
`xelnigma.mechanoidslagtoplasteel`, `gunseeker.repairstation`, `Teiwaz.TAAJG`,
`Memegoddess.ReplaceStuff` (its in-place replace refunds through deconstruct and would read our yield
curve).

GPT advised against declaring incompatibility "without demonstrated conflicts". **Rejected for the
hard list**: the owner ruled the declaration, and every hard entry replaces the same act we replace
(recycling, mech disassembly, scavenging spots, gear repair), which is the demonstrated conflict.
**Taken for the soft list**: those only warn, and each warning names the overlapping def or method so
a player can judge it.

**One consequence the owner should know:** `Mlie.RecycleThis` is **active on the campaign list now**,
so shipping this removes it from the list (its job moves to the nest's strip-for-parts bill). Five of
the soft list are active too; they only warn.

## 7. Mod Settings

Per the every-mod rule: defaults are shipped behaviour, all-off degrades to vanilla.

| setting | default | off means |
|---|---|---|
| Salvaging skill (**restart**) | on | the def still loads, no job reads it, the stats read Construction (§4e) |
| Skill covers your own teardown (**restart**) | per §11 card 1 | ordinary deconstruction stays Construction and vanilla yield |
| Wreck pieces | on | wrecks deconstruct to costList plus the salvage design's loot roll (§3c there) |
| Cut plan gizmo | on | every strip is Careful |
| Survey | on | no survey job; strips are always blind |
| Hazards during strip | on | none fire |
| Appraisal | on | rare parts arrive identified |
| Heavy-piece slowdown | on | carrying a piece costs nothing |
| Facility cap per nest (slider) | 4 | |
| Smelting penalty (Rekko) | on | smelting is neutral (only matters with Ninefold active) |
| Rare-part rate (slider) | tuning | |
| Incompatibility dialog | on | log lines only |

## 8. Total-conversion guard: exactly which vanilla behaviours change

The owner's line: a new system, not a total conversion. In the **recommended scope** (§4b), with every
setting at default, **these and only these** vanilla behaviours change for every player, Jawa or not:

1. **Every pawn has a 13th skill, Salvaging**, rolled at generation like any skill, with its row on the
   character card, its aptitude genes, neurotrainer and books.
2. **Mech shredding reads Salvaging, not Crafting** (the recipe's skill and its two stats).
3. **Wreck-family buildings** (ours, and the vanilla junk once reskinned under
   `STARWARS_JUNK_RESKIN_1`) strip into pieces and slag instead of metal. Player-built buildings never
   do.
4. **Seven recycle/repair mods are declared incompatible**, including the active Recycle This.
5. A **Salvage** column appears in the Work tab.

The **wider scope** adds two more, both reaching every colony: deconstructing your own buildings
trains Salvaging instead of Construction, and its yield rises with skill above each def's vanilla
fraction (never below).

Unchanged in every scope: building, uninstall/minify, repair, hacking, mech disassembly, the electric
smelter (still 25%, still skill-free), destroy-item bills, slag extraction, floors, every other skill,
traders and quests. With Ninefold active, the Rekko deconstruct penalty moves (§3); that is a
campaign-layer change, not vanilla.

Of the list, only item 1 is felt by a colony that never meets a wreck. It is the single reason the
skill is a decision rather than a default.

## 9. Build phases

Mod: one franchise-free mod, working name **Scavenger's Nest**, packageId `mandrake.rm.scavengersnest`
(prefix `RM_`, namespace `RimMandrake.ScavengersNest`), depending on nothing of ours; the Star Wars
parts, Jawa genes/backstories, the Ninefold re-scope and the Jawa thoughts sit in the `RUT_`/`RSW_`
layers per Q11a. The salvage design's loot comp (§3c there) becomes this mod's fallback path when
pieces are off. Every phase ships its functional script first (`design/RimMandrake/debug_process.md`).
Sizes: S under a day of FOUNDRY work, M a few days, L a week or more, art counted.

Reordered after the GPT critique: a **vertical slice** (two wreck families, wreck to nest to stock)
proves the loop before anything global is rewired.

| phase | what | size | gate |
|---|---|---|---|
| 0 | **Proof**: the §4e functional script on the quicktest list; read whether Droidworks droids carry skill records | S | owner's skill decision (§11 card 1) |
| 1 | **Vertical slice**: `RM_Salvaging`, the two stats, Salvage WorkType, gene icons; piece comp (budget, provenance, resumable stages); strip-to-pieces for Hull and Carapace; Careful cut only; racks; nest core plus two facilities; the one resumable work-down job with the nest policy; furnace nook with budget accounting; Ninefold Rekko re-scope; incompatibility declaration and dialog; settings | L (art: about 7 pieces x 2-3 stage sprites, core, 2 facilities, nook) | phase 0 and the salvage design's family defs |
| 2 | **Choices on site**: Quick and Gut plans, hazards with checkpoints, heavy-piece slowdown, sled; strip-for-parts bill on weapons/apparel; mech shredding re-point; donor-assembly recipes | M | phase 1 played once by the owner |
| 3 | **Appraisal and survey**: unidentified rare parts, appraisal on the Antiquities pattern, survey readout with expedition triage (piece masses); scanner goggles, cutting torch, hydrospanner and their research rows | M (art: 3 tools, unidentified sprites) | phase 1 |
| 4 | **Remaining families and the nest's full kit**: Tank, Frame/speeder, Sealed piece sets; remaining facilities and the cap; strip droid work type; `RUT_` Star Wars parts; Jawa aptitude gene and backstory gains | M-L (art) | phase 2 |
| 5 | **Wider skill scope**, only if chosen: ordinary deconstruction on Salvaging with its yield curve and the teardown-loop script | M | §11 card 1 |

Total: about four FOUNDRY weeks, most of it piece art and phase 1 balance. Later, not in this build:
salvage commissions (§10), lore leads from survey, the Bazaar's grade-aware price and bluff (§12).

## 10. GPT critique

Consulted 2026-10-03 through `src/RimMandrake/Utils/gpt_consult.py` (model `gpt-6.1-sol`, high effort),
on the draft of this document, asking for critique of the loop, the skill decision and missed
mechanics. GPT cited a public decompile of an older RimWorld (not the installed 1.6) for its engine
points; the ones taken are design guards that hold either way, and the API claims marked below are for
FOUNDRY to confirm in RimSage, not facts.

**Taken, and where they landed:**
| point | landed in |
|---|---|
| Three stages as three jobs means 900 jobs for 300 pieces; make them resumable phases of one job, progress on the comp | §2f |
| Steer the nest with a policy (filters, radius, suspend, bulk keep/smelt), not 300 gizmo decisions | §2f |
| Reserve piece and interaction cell; respect forbidden, areas, danger; one cell is one worker | §2f |
| Pieces stack to 1, so carrying capacity cannot batch them; vanilla has no mass slowdown; use a stat part, not a hediff (API claim: confirm) | §2d, §5a |
| One conserved recovery budget across strip, process, slag and smelt, or Strip then Smelt double-dips | §2d, §3 |
| Provenance: rebuild, repair or reinstall never re-rolls loot | §2d |
| Appraisal reveals quality, does not change it; a failed appraisal is retryable, so players do not hoard | §2g |
| Vanilla `SmeltProducts` does 25% of the cost list plus fixed `smeltProducts`; compute the piece remainder ourselves (API claim: confirm) | §3 |
| Rekko penalty by value thrown away, condition read at cut time so damage cannot launder it | §3 |
| **Do not re-point ordinary deconstruction by default**: the skill can own salvage through our own job | §4b, §4d, §8, card 1 |
| Keep stats as the interface, so the stat fallback costs no job rewrite | §4b |
| Patching `JobDriver_RemoveBuilding` also hits Uninstall; keep each def's own deconstruct fraction | §4b |
| Screenshots are not proof; test recruitment, old saves, genes, disabled work, books, a real job | §4e |
| A loaded skill cannot be toggled off live; make the toggle restart-only and define "off" | §4e, §7 |
| Cut recursive child pieces, 27 functional bins, routine unidentified parts | §2f, §2g |
| Cut the custom room role for now; storage plus a capped thought | §2e |
| Cut idle droid-assistant logic | §5b |
| Droid hazard immunity is unproven | §5b |
| Idea: donor assemblies (keep whole for a repair or crack for components now) | §2h |
| Idea: capped facility links so nests specialise | §5c |
| Idea: expedition triage (survey shows piece mass; pods and caravans force a choice) | §9 phase 3 |
| Build a two-family vertical slice before global rewiring | §9 |

**Taken as later work:** salvage commissions (a trader asks for three intact sensor assemblies, so
preserving competes with consuming). Good, cheap on vanilla trade-request quests, but it needs the
piece families to exist; filed in §9's "later".

**Rejected, and why:**
- *No blanket incompatibility without demonstrated conflicts*, for the hard list: the owner ruled the
  declaration, and every hard entry replaces the same act (§6). Taken for the soft list.
- *"Survey must not become compulsory insurance"*: agreed in spirit, already true (blind strips are
  allowed and Careful hazards are rare); no change needed beyond checkpointing.
- *Wealth timing* (cheap unsorted stock postpones colony wealth, and unsorted lots could be bought as
  lottery tickets from traders): traders never stock unsorted pieces, so the lottery cannot be
  bought; the deferred wealth is intended (raids scale on wealth, and a hold of unsorted salvage
  is exactly the scavenger's low profile). Noted for the balance script, no design change.

## 11. Decisions for the owner

Nine questions on three cards in `Transient/jawa_scavenge_cards2_2026-10-03.json` (each element of
`cards` is one AskUserQuestion payload). The skill is first, as he asked.

- **Card 1, the Salvaging skill:** how far it reaches (salvage only, every teardown, or no skill and a
  hidden rating); how much more a master gets; what happens if the 13th row does not fit the UI.
- **Card 2, the loop:** moving Rekko's anger from every teardown to smelting and the repairable;
  heavy-piece slowdown; Recycle This leaving the list; capped versus unlimited nest facilities.
- **Card 3, carried over:** the desert hulk against the placement law (unanswered from the first
  cards); build order (vertical slice first versus skill first).

Nothing is built until card 1 is answered. FOUNDRY's build item is filed from the answers.

## 12. Retired and folded questions from card 2 of the first set

`Transient/jawa_scavenge_cards_2026-10-03.json` card 2 was never asked. Its four questions:

| question | outcome |
|---|---|
| Cut plan (quick / careful / gut one part) | **Folded in.** The owner chose the full process; Careful/Quick/Gut is §2c, built in phase 2 |
| Reading the wreck (survey) | **Folded in** for hazards, loot tier, pieces and repairability (§2b); **lore and leads retired for now**, since a lead with no quest to point at is a tooltip |
| Desert hulk vs the placement law | **Still open**; carried to card 3 of the new set |
| Grade sets price, and bluffing in the haggle | **Retired for now.** Grades raise market value through vanilla quality; the bluff waits on the Bazaar's haggle screen, which is filed and unbuilt, and returns as a question when it lands |
