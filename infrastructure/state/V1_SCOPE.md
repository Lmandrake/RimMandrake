# V1_SCOPE.md — what ships in the alpha, and what waits

_Owner's scope decision, 2026-08-13. **PROJECT holds the MVP seat**: PROJECT sets
the v1/v2 line, the other four own execution. Appeals go to the owner, not to
PROJECT._

**Read this before adding anything to `TODO.md` or `NEXT_RELOAD.md`.** If an item
is not v1 by the rule below, tag it `[v2]` and move on.

---

## The problem this fixes

Measured 2026-08-12: **spec ~78% written, build ~10%, verify ~5%**. Concretely —
**25** worldbuilding specs against **50** authored XML files, most of which are
patches and bug-fixes. **Zero** custom quests. **Zero** authored factions. **No
item of world structure has ever been seen in a game.**

The cause is structural, not effort: the seats split by territory — live game
(BRIDGE, OPS), new content (CREATE), design (VISION), repo (PROJECT) — and **the
campaign itself had no seat.** Everyone optimised their own patch and nobody owned
"is this playable". That seat now exists and is PROJECT's.

---

## The rule

> **Everything ships THIN, except the gravship, which ships DEEP.**

Breadth is preserved — v1 contains the whole premise, so you are playing *your*
campaign, not a generic one. **Depth is cut to "the thinnest thing that reads
correctly in play."** v2 deepens each system.

**This inverts the current failure.** Breadth of spec with no depth of build
becomes breadth of build with no depth of anything — which is what an alpha is.

### The gate

> **Every v1 item must be seen working in-game once.** Not "the log is clean" —
> **seen.** A faction on the map, a quest fired, terrain visible, the ship
> boarded.

When every v1 row below is verified, **v1 is closed.** Anything found after that
is v2, including things we would rather fix.

⚠️ **Verification rides the BRIDGE, not the reload.** A cold load is ~23–30 min;
an item-by-item gate would be unaffordable at that price. The live bridge exists
precisely to check things without restarting, so **BRIDGE's tooling is on the
critical path, not beside it.** Batch anything that genuinely needs a load.

---

## v1 content — thin

| system | v1 bar (thin) | deferred to v2 |
|---|---|---|
| **Factions — authored** | **One**: the Imperial Desert Directorate, on `OuterRim_GalacticEmpire` as vessel. Label-level reskin only — name, leader title, colour. | The other 11 dossiers. `pawnGroupMakers`, memes, ideoligions, the relations matrix. |
| **Factions — subtractive** | **Untick the fiction-breakers on vanilla's Configure Factions page during the worldgen run.** Not config — Faction Control has no suppression field. List proposed by OPS, ratified by VISION. | Per-faction density tuning, biome weighting, `CenterPoint` clustering. |
| **Quests** | **One** `QuestScriptDef` that fires and resolves. Any premise. | Quest chains, faction-linked arcs, the Hutt extortion loop. |
| **Resources / terrain** | **Three** terrain or resource overrides that are visible on the map. | The full resource-terrain matrix, biome palette, water doctrine. |
| **Xenotype / crew** | ⚠️ **WHICH Jawa xenotype spawns** — three are live, so "a Jawa appeared" does not close this. | Crew personas, dialogue, per-pawn backstory wiring. |
| **Weapons / gear** | What the mods already ship, plus our 6 live mods. | The energy-density explosion model. Ion/droid balance passes. |
| **World** | **Generate a new world** on the desert-world settings. The owner keeps no savegames, so the current one is not the shipping one. | Authored world layout, settlement placement, landmark pinning. |

**Rule of thumb for "thin":** if a v1 row needs more than **one day** of work,
it is still too thick — cut it again.

---

## v1 flagship — the gravship, DEEP

**The owner's explicit exception: a beautiful, detailed ship with reasoned design
and size.** This is the one place spec-completeness is wanted, because it is the
thing the player looks at every session and the campaign's whole premise.

**The design is already written — 1,481 lines**, and should be *built*, not
re-designed:

- `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_deck_plan.md` (302)
- `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_designs.md` (570)
- `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_distinctive_features.md` (609)

**The tooling is already live** — this is the strongest position of any v1 item:

| mod | load | why it matters |
|---|---|---|
| Odyssey | 9 | gravships at all |
| Bigger Gravships | 78 | size ceiling for a "reasoned size" |
| **Gravship Exporter** | **161** | ⭐ export/import a built ship — the delivery artifact |
| **[BTD] Gravship Blueprints** | **419** | ⭐ blueprint authoring route |
| Gravship Storage / Crashes / Raids | 36/160/440 | campaign texture |

### ✅ ANSWERED 2026-08-13 by CREATE, offline — **YES. The deep build is unblocked.**

`b7e49db`. Established without a game, from the mod's own shipped example
(`1.6/Defs/Advanced_Starter_Ship.xml`, 4,816 lines) and the assembly symbols:

- Format is `GravshipExport.ShipLayoutDefV2` — a cell grid carrying
  `foundationDef`, `terrainDef`, and a things list of `defName`/`stuffDef`/`rotInteger`
- `ExportShipAsMod` writes its own `About.xml`
- `Page_ChooseGravship` / `ScenarioUsesGravshipStart` start a new game on a chosen ship

**So the ship is a reusable artifact: build once, keep it in the repo.** Pawns and
items are **not** included — measured (zero pawn/item entries in the example), not
taken from the README.

⚠️ **The live test is now for ONE contradiction, not for the question.** The
README's Known Issues claim floors cannot be saved — *"you can only place one
TerrainDef and that has to be the Substructure"* — while the author's own shipped
example contains **204 non-null `terrainDef` cells** (128 MetalTile, 38
SterileTile, 22 WoodPlankFloor, 16 CarpetMarine). Resolve that before trusting
floors to survive a round trip.

**Deep does NOT mean unbounded.** The ship ships when it is built, boardable, and
matches the deck plan's intent. Art polish, per-room detailing and distinctive
features beyond the plan are v2.

---

### ⚠️ CORRECTION — "offline design loop" was MY overstatement, not a capability

I told CREATE and BRIDGE that import unblocks *"author XML, import, look,
iterate — no live session per iteration."* **That is not available today**, and
CREATE caught it before anyone planned around it.

**The only import route is NEW-GAME SETUP.**
`Setup/Patch_Scenario_GetFirstConfigPage.cs:9` patches
`Scenario.GetFirstConfigPage`; the Postfix inserts `Page_ChooseGravship` **after
`Page_CreateWorldParams`**, gated on the scenario using gravship arrival. The
author states the limit himself: *"I won't be adding any major features like
delayed ship spawning etc."*

⇒ **One iteration = one new game start.** Cheaper than a campaign load, **not
free**, and it cannot put a ship on the map you are already standing on.

⭐ **What WOULD make it true is a small addition to OUR companion DLL.**
`ShipSketchBuilder.BuildFromLayout` is `public static` and returns a `Sketch`,
and a Sketch spawns onto a live map. The licence permits it outright. **Until
that is written, the offline loop is a plan and not a capability** — filed at
BRIDGE.

✅ **RESOLVED AT SOURCE by BRIDGE (`75d39e5`): the loop IS achievable.**
`ShipSketchBuilder.cs` contains **zero** references to `Find.`, `Current.`,
`GameInitData`, `Scenario` or `Map` — `BuildFromLayout` is a pure function, layout
in and Sketch out, with `DefDatabase` lookups only. **The scenario page is its
only CALLER, not a constraint.** So CREATE and BRIDGE are both right: as the mod
ships, one iteration costs one new game; with our companion addition, it does not.

🔴 **The catch, and it is the seventh silent failure today: FLOORS DO NOT COME
WITH A MID-GAME SPAWN.** Terrain is re-applied by
`HarmonyPatch_DoGravship.cs:~157` during *arrival*, and that patch does not run
for a Sketch spawned mid-game. **Structure lands, floors do not, and nothing
errors.** The fix is already ours: replay the layout's `terrainDef` cells through
`jawa/set_terrain_batch` after the spawn. **Anyone building mid-game import who
does not know this will ship a floorless ship and see no warning.**

✅ **Floors, verified at BOTH ends** (CREATE, source-read rather than inferred
from a cell count): the exporter captures non-substructure terrain at
`Exporter/GravshipExporter.cs:182-184`, and the arrival Postfix re-applies it via
`terrainGrid.SetTerrain`. The README's claim is stale, and now we can say *why*.

📌 **The lesson is mine:** I found a capability in an assembly and described what
it would *enable* rather than what it *does*. Reading a symbol is not reading the
call path. **State what you measured; the inference is a separate sentence.**

### 📊 ROW 8 STATUS — 3 of 4. **Built and exported; NOT closed.** `6909ecb`

BRIDGE, on a quicktest map. *(Reported at the time as "campaign untouched" — no
longer a virtue: the owner has ruled that no map or campaign is to be preserved.
The map is recorded because it changes what the result CLAIMS, not because
anything needed protecting.)*

| criterion | state |
|---|---|
| **built** | ✅ 31 steps, 4,057 foundation + 4,057 floor cells, 1,053 things, ~1s of calls |
| **exported** | ✅ `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml`, 2.0 MB |
| **matches deck plan intent** | ✅ — and that is the problem, see below |
| **boardable** | ⬜ **BLOCKED, not merely untested.** The bridge cannot order a pawn to walk anywhere — needs `B-v3 order_pawn`, which is a companion-DLL deploy and therefore needs the game **DOWN**. BRIDGE's UI is also designator-jammed, so no inspect panel. **Row 8 cannot close this session at any price.** |

✅ **The floor contradiction is CLOSED and the README was wrong.** 4,057
`terrainDef` cells survived the round trip — 3328 MetalTile, 507 SterileTile, 197
WoodPlankFloor, 25 CarpetMarine, matching exactly what was laid. The exporter's
own Known Issues claim that only Substructure can be saved is false. **Anyone
about to hedge a design on that limitation should stop.**

### 🔴 THE FINDING: the deck plan ships NO thruster, NO fuel tank, NO controls

The engine's inspect panel reads *"Connected substructure: 4057 / 633"* and, in
red, *"Requires: Thruster, fuel tank, controls."* **The ship cannot fly, and the
design is why — not the build.** BRIDGE built the plan faithfully; the plan omits
all three.

**MVP ruling: flightworthiness is NOT in row 8's v1 bar.** The bar is *built,
boardable, matches the deck plan's intent* — and a stationary hull that reads
correctly satisfies it. **v1 is not blocked by this.**

⚠️ **But it is recorded loudly, because "the gravship is done" and "the gravship
cannot move" are both true right now, and only one of them is what anyone will
hear.** The campaign's whole premise is a salvaged gravship. A ship that cannot
fly is a building. **→ VISION and CREATE: is flight v1-adjacent or genuinely v2?
That is a design call and not mine to make silently.**

**Two unchased discrepancies, filed at CREATE:** the export holds 1,094 things
against 1,053 spawned (it swept up 32 RiverRock and glacial ice inside the
footprint), and 5 heatsinks exported against 6 spawned. **Neither errored** —
sixth instance today of a silent mismatch.

### ⚖️ Row 8's gate, ruled 2026-08-13 — **the EXPORT is what makes a quicktest count**

BRIDGE is building the ship on a **quicktest** map, not the campaign. By the
general rule that would prove nothing about v1 — *"a quicktest answers does this
work, never is this true of our campaign"* (`skills/rimworld-debug-testing`).

**Row 8 is the exception, and the reason is Gravship Exporter.** CREATE
established offline (`b7e49db`) that a built ship exports to a
`GravshipExport.ShipLayoutDefV2` — a cell grid of foundation, terrain and things.
**So the ship is a reusable ARTIFACT, not a map state.** Where it was first
assembled does not matter.

> **Row 8 closes on: built, boardable, matches the deck plan's intent, AND
> exported to a layout def committed to the repo.** The export is not paperwork —
> it is the thing that survives the map it was built on.

⚠️ **Built-but-unexported on a quicktest closes NOTHING** and is one map-swap away
from being lost entirely. If the session runs short, **export before you polish.**

⚠️ **One contradiction still unresolved:** the exporter's README claims floors
cannot be saved, while its own shipped example carries **204 non-null `terrainDef`
cells**. A round-trip that silently drops floors would make the artifact
incomplete without erroring — this project's usual failure shape. **Verify the
export re-imports with its floors** before calling the row done.

**Seat split, as BRIDGE stated it and it is the right one:** CREATE keeps
authorship, BRIDGE owns proving. A disagreement between plan and game pulls
CREATE in rather than being resolved unilaterally.

### ➕ ADDED TO v1 BY THE OWNER, 2026-08-13 — the deconstructible-only filter

> *"I would like to build a first version of the deconstructible-only filter for
> v1."* — the owner, relayed by VISION. **Recorded, not argued.**

**What it is:** a filtered palette of wreck/ruin props that are actually
**deconstructible**, excluding everything descending from
`NonDeconstructibleAncientBuildingBase` — which the player can only remove with
explosives. RimWorld ships ~170 pre-rusted wreck props and an unknown share are
in that family.

**Why it belongs in v1 on its merits, not just by ruling:** it is an
**ingredient, not a feature**. Any wreck, ruin or salvage field we ever place is
**unstrippable garbage to the player** unless the palette is filtered first. It
is cheap, offline, needs no game, and it prevents a whole class of player-facing
defect rather than adding a surface. **A rider inside row 4, like the hulk image
— not a new row.**

✅ **FIRST VERSION LANDED:** 181 ruins defs, **167 deconstructible**. But only
**55 carry a `costList`** — 89 return nothing at all when stripped. **Over half
the kit is scenery, not salvage**, which is precisely where the v2 economy work
actually lives. Good to know before designing an economy around it.

### 📈 SCOPE MOVED TWICE IN TEN MINUTES — saying so is this seat's whole job

v1 gained the **hulk image** (conditional) and the **deconstructible filter** in
the same ten minutes. **Both are cheap, both are riders rather than rows, and one
is owner-ruled outright — so neither is a mistake.** But:

- **v1 is 2 of 8 closed.** Growth while two-thirds is unfinished is the shape
  that turns a thin scope thick, and it never announces itself.
- The rule this file opens with is *"in-flight detail work must not add to v1."*
  **The owner may override it and did; a peer may not.** That asymmetry is the
  whole point of writing it down.
- ⚙️ **The honest accounting: v1 is no longer 8 items.** It is 8 rows plus 2
  riders, and the riders are real work regardless of where they are filed.

**Nothing here blocks. This is the burn-down refusing to be flattering.**

### ⚖️ THE REST OF THE HULK — ruled 2026-08-13. **Conditional v1, as a RIDER on row 4.**

VISION declined to set this and routed it here; CREATE priced it and asked me not
to rule blind. Ruling the *shape* now so neither waits on me.

**⛔ The SYSTEM is v2, unconditionally.** Tiers, cross-section, salvage economy,
deep deposit. A big authored map feature is not thin, and v1 is thin by rule.
No appeal, and it is not a close call.

**🟡 The IMAGE is v1 — CONDITIONALLY, and it does NOT become row 9.**

> **It rides `Patches/JawaResource_Scrapfields.xml`, inside row 4.** Same
> `GenStep` registered into `Base_Player`, same file shape, different contents —
> a mechanism **proven and deployed today** (`73ca76c`). Row 4's gate already
> covers it: *visible on a newly generated map.*

**Why a rider and not a row:** v1 is at 2 of 8 closed with six open. **Adding a
ninth row while six are unfinished is how a thin scope stops being thin** — and
`V1_SCOPE`'s own standing rule is that in-flight work must not add to v1. Adding
*contents* to a proven row costs nothing structurally; adding a row costs a gate,
an owner, and a line in every report from now on.

**Why it earns v1 at all:** the campaign's premise is a Jawa scavenger clan, and
**v1 currently contains nothing that says scavenger.** Breadth of premise is the
one thing v1 explicitly preserves — *"you are playing your campaign, not a
generic one."* The first thing the player ever sees is the ninety percent of the
hulk that never flew. That is the premise, in the opening frame, for an
afternoon.

#### ✅ APPROACH RULED — stamp the exported layout, do NOT write a shape generator

CREATE flagged the thing that would have quietly broken this: **scrapfields
SCATTERS; a hulk has a SHAPE.** Random placement produces confetti, not a wreck,
and writing a hull-outline generator is *"the v2 cross-section arriving early
wearing v1's clothes."* Correct, and it would have been discovered halfway
through the afternoon.

**The approach is APPROVED: read BRIDGE's exported `ShipLayoutDefV2` and stamp
broken substructure where it has substructure.** 88×135, 4,057 cells,
round-trip-proven with zero differences. **A parser we already own instead of a
generator we would have to invent.**

⭐ **And it is better fiction, not a compromise:** the hulk is the same class of
vessel as the one the clan flies, because it *is* the same ship. The premise
writes itself.

**Accepted risk, stated rather than buried:** this couples row 4's rider to
BRIDGE's export format, where scrapfields had no dependency at all. Low —
the format is committed and round-trip-proven — but real. **If that format
churns, the rider churns.**

#### 📐 THE CROP — ruled, because "somebody should pick it" is how it grows

CREATE is right that 88×135 is enormous for a starting map and that the crop must
be chosen deliberately rather than discovered at 4,057 cells. So:

| | |
|---|---|
| **who picks WHICH fragment** | **VISION** — it is a fiction question: which part of the ship stayed on the ground |
| **who crops and stamps** | **CREATE** |
| **hard ceiling** | 🔴 **1,200 cells.** Not a target — a ceiling. |

**Why a ceiling at all:** the crop size *is* the work size, and an unbounded crop
is kill condition 2 arriving by accident. 1,200 cells is roughly a quarter of the
hull — large enough to read unmistakably as a ship section at a glance, small
enough that stamping and prop placement stay an afternoon. **If VISION's chosen
fragment exceeds it, crop harder rather than negotiate the ceiling.**

#### ✅ KILL CONDITION 1 — PASSED, 2026-08-13, on all four tests

`BrokenSubstructure` (Gravship Crashes, `Arcjc007.GravshipCrashes`, ACTIVE):

| test | result |
|---|---|
| sits on ordinary desert ground | ✅ `terrainAffordanceNeeded: Walkable`, **no `placeWorkers`** — unlike Odyssey's `Substructure`, which carries `PlaceWorker_InSubstructureFootprint` and IS confined to a ship footprint |
| walkable | ✅ `passability: Standable`, `pathCost: 0` |
| reads as broken at 64 px | ✅ **and it is the only one of three candidates that does** — `VGE_DamagedSubstructure` reads as patina, `VGE_GravshipSubscaffold` as flat grey |
| spawn-only | ✅ `designationCategory` nulled, `WorkToBuild` 60000 — right for a map-gen feature. **The clan did not build it.** |

⭐ **Unlooked-for bonus: it carries `<tags><li>Substructure</li></tags>`, so it
CONNECTS and counts toward capacity.** Visually ruined, structurally sound — so
the *flying* hull can be scarred too, not only the ground wreck.

⚠️ **Author's caveat:** the motif is large and high-contrast, so a big unbroken
field tiles visibly and reads as wallpaper. It wants interleaving with intact
substructure — which is also the better fiction.

**⇒ The rider is CONFIRMED v1.** KC1 is passed; KC2 (one afternoon) holds on the
layout-stamp approach ruled above, and CREATE has said it would call KC2 itself
without that.

#### 🪤 TRAP, recorded because it inverts the answer and the two look identical

> **Read the `tags`, never the `affordances`.**

`BTD_QuestSiteSubstructure` carries `Substructure` in its **affordances** but
**not** in its **tags**. So things build on it and it does **not** connect to the
grav field. Anyone authoring against the wrong field gets a confident, wrong,
silent answer — the eighth instance of that shape today.

#### 🔪 The kill condition, stated before the answer arrives

**If CREATE's live check fails — `BrokenSubstructure` cannot sit on ordinary
desert ground, is not walkable, or does not read as broken at 64 px — this is v2
immediately and without appeal.** At that point it is an art commission, not an
afternoon, and an art commission is v2 by definition.

⏱️ **Second kill condition: one afternoon.** If it exceeds that, it is v2 —
`V1_SCOPE`'s own rule of thumb is that a v1 item needing more than a day is still
too thick. **Estimates have been wrong all day; this one gets a hard stop rather
than a hope.**

## ⚠️ Sequencing — the two dependencies that can cost a whole cycle

### 1. `jawa/list_factions` needs a SHUTDOWN window, not a startup

The gate requires **seeing a faction on the map**, which needs
`jawa/list_factions` — companion-DLL work, and therefore gated on a **shutdown**
rather than a startup (`skills/rimworld-load-round/SKILL.md` §6).

> **Whoever calls the next shutdown tells BRIDGE BEFORE the game closes.**
> Miss the window and the v1 faction row waits a full ~25–30 min cycle.

BRIDGE has it ranked #1 and V1-CRITICAL (`b2a0a36`); rotation, style and xenotype
setters are tagged `[v2]`.

### 2. ✅ Gravship round-trip — ANSWERED, and answered offline

**Resolved by CREATE in `b7e49db`, from the mod's shipped example and assembly
symbols. No game needed.** Reusable artifact; the deep build is unblocked. Detail
in the flagship section above.

**The lesson worth carrying:** I filed this as needing *"a live session and a
built ship"*. It needed neither — the answer was in files on disk the whole time.
**Before booking the scarcest resource we have, check whether the question is
answerable offline.** A ~25–30 min load was queued for something that took a read
of an XML file.

**The residual live test is narrow:** one README-vs-example contradiction about
whether floors survive export.

## 📐 Ranking rule for the MVP seat

**Rank by the gate, not by cost-to-build.** BRIDGE originally ordered four bridge
tools by build cost, which put rotation first and `list_factions` third — and
noted that *cheapest-to-build* and *most-needed* are different questions, one of
which had been answered silently.

**That is the default failure of a competent agent working without a gate**, and
it is the whole reason this seat exists. Every v1 queue is ordered by *what the
gate needs next*, and a cheap item that no v1 row depends on is **v2**.

## 📊 BURN-DOWN — measured 2026-08-13, game down

**PROJECT owes this and it is honest, including where the answer is zero.**

> ⭐ **ROW 1 IS THE FIRST v1 ITEM EVER TO PASS THE GATE.**
> `OuterRim_GalacticEmpire` renders **"Imperial Desert Directorate"** in the live
> game. The gate is *"seen working in-game once"*, and it is met.
>
> ⚠️ **Verified, not finished.** The Directorate reads live as `hostile=false`,
> `goodwill=0`, `permanentEnemy=false`, against a design calling it the sole
> permanent enemy — and there are **two** empires with the split backwards ("The
> Fallen Dominion" holds 4 settlements to the Directorate's 1). The **label**
> ships; the **antagonist does not exist**. That gap is VISION's (`infrastructure/state/queue/VISION.md`
> V6/V7), not this row's checkbox.

**Seats are BRIDGE · OPS · CREATE · VISION · PROJECT.** Owners below are assigned
by what the *remaining* work is: authoring XML/defs/art → **CREATE**; config and
live-stack → **OPS**; driving the live game to verify → **BRIDGE**.

| # | v1 row | built | verified | owner | what is left |
|---|---|---|---|---|---|
| 1 | Empire reskin (labels) | 🟩 **BUILT** | 🟩 **SEEN LIVE** | CREATE | ✅ **CLOSED** |
| 2 | Faction exclusion at worldgen | — | ⬜ | owner + VISION | 🔴 the campaign worldgen, list ratified and waiting |
| 3 | One `QuestScriptDef` — *The Claim* | 🟩 **BUILT**, deployed | ⬜ | CREATE | fire it and reach an end state |
| 4 | Three terrain overrides | 🟩 **BUILT**, deployed | 🟨 **1 of 3 SEEN** — `Jawa_SaltCrust` passed live | CREATE | two more, on any fresh map |
| 5 | Jawa xenotype plays | 🟩 live | 🟨 **genes render on scratch** | BRIDGE | see it on a naturally-spawned campaign Jawa |
| 6 | Weapons / gear | 🟩 6 mods live | 🟩 **`JawaIonWeapons` PROVEN** `ad3e9b0` | BRIDGE | ✅ **CLOSED** |
| 7 | Ordinary worldgen | ⬜ | ⬜ | BRIDGE | 🔴 the campaign desert world |
| 8 | ⭐ **Gravship (DEEP)** | 🟩 **BUILT + EXPORTED** | 🟨 **3 of 4** | CREATE/BRIDGE | **boardable — never tested** |

### 🔴 THE HEADLINE: the campaign world has still not been generated

**Everything proven today was proven on a QUICKTEST map.** The game came up, a
scratch colony was made, and enormous work landed on it — but the one
irreversible step this session existed for, **worldgen with the ratified
tick-list, has not happened.** Rows 2 and 7 are that step; rows 3, 4 and 5 all
want the map it produces.

⇒ **Nothing is lost** — the tick-list is ratified and committed, the ship is an
exported artifact, the quest and terrain are deployed. **But v1 closed 1 row
today (row 6) and the gate for four more is still one screen away.**

**Score: 2 of 8 closed** (rows 1, 6). Rows 3, 4, 8 are *built and unverified* —
which is a genuinely better position than this morning, when the build was 0.

🟢 **Rows 3 and 4 need no game at all to BUILD — they are at 0 because nobody
saw they were closable, not because they are hard.** Their *verification* rides
the next live session with everything else (see the sequencing rule below).

🔴 **Row 2 is no longer offline work of any kind, and row 7 stopped being a
checkbox.** Two corrections in one hour, both from OPS reading the mod properly
and then the owner ruling on top:

1. **There is no suppression setting.** `FactionDensity` serialises `faction`,
   `density` and `enabled`, and none of the three removes a faction; `density` is
   a clumping radius. The row had been written against the mod's own English
   string — *"setting to 0 disables the faction"* — a pre-1.3 leftover for a UI
   that no longer exists (`27159ac`). Faction exclusion is **vanilla's Configure
   Factions page**, which Faction Control unlocks rather than replaces.
2. ⭐ **Owner's ruling, relayed via OPS: _"We are keeping no savegames at this
   time."_ So v1 REGENERATES the world** (`14700f7`, `OWNER_DECISIONS` #11,
   closed). That saves the row: exclusion is reachable, because we are running a
   worldgen — but it is reachable **only during that run**, as a checklist
   someone ticks on the Configure Factions page. VISION ratifies the exclusion
   list; OPS proposes it (`infrastructure/state/queue/OPS.md`).

⛔ **The old world is DELETED, not merely superseded.** On the same ruling the
owner ordered every savegame removed and OPS did it — 27 `.rws`/`.bak`, 764.7 MB,
irreversible (`acc3261`). **So "53 factions and 107 settlements" below is history,
not a fact you can check**, and every measurement taken against that save is now
its own only record. Any queue item whose evidence step was "look in the save" has
to be re-scoped onto the worldgen run; there is nothing left to open.

**The consequence for row 7 is the one that changes planning.** "Ordinary
worldgen" was carried as *verify only* — look at the map, confirm desert. It is
now something we **DO**, once, deliberately, and rows 2 and 7 are the same event.
A regenerated world is also the moment every other thin row wants to be present,
because they are cheaper to see in a world we just made than in one we inherited.

📌 **The lesson, because it will recur:** a row sat at "0, closable offline today"
for a full day on the strength of a *mod's own UI label*. Reading the label is
not reading the mechanism. **A v1 row whose build step is "change a setting" must
have that setting's effect confirmed in the assembly or the source before it
earns a row.** This one had no effect to confirm.

**Row 7 stopped being an observation and became an act.** It read "BRIDGE confirms
desert worldgen on the map and it closes" — true while v1 shipped the existing
save. Under the no-savegames ruling BRIDGE *generates* that world, and row 2 is
ticked on the Configure Factions page inside the same run. **Rows 2 and 7 are one
event and must be scheduled as one.**

✅ **SUPERSEDED — this block said "v1 build is still 0" and contradicted the
table above it by 70 lines.** It was written this morning and was true then. Rows
3, 4 and 8 have since been BUILT. Kept only as the record of a real drift, and
because a burn-down that quietly overwrites its own bad news is worth nothing.

> **The morning position:** the owner reassigned CREATE to the Bantha reskin
> (`TODO_v2.md` §0c), which was v2 work pulled into v1 time — their call, recorded
> rather than argued. The stated consequence was that rows 3 and 8 were not
> started and v1 build was 0.
>
> **What actually happened:** CREATE built row 3 (`47733f8`) and row 4
> (`73ca76c`) offline within the hour once the owner re-ordered them ahead of the
> art, and row 8 was built and exported the same evening (`6909ecb`). **The drift
> was real and it was also reversed the same day.**

📌 **The lesson is about this document, not about CREATE.** A burn-down carries
two things that rot at different speeds: a TABLE that gets updated because people
look at it, and PROSE that does not, because nobody re-reads a paragraph they
already agree with. **The prose outlived its truth by a full day and was found by
a doc-budget sweep, not by me** — and I am the seat accountable for this file
being honest. **When the table moves, re-read the prose.**

### ⚠️ Row 5's gate was wrong — BRIDGE, `01f95a8`

**Three Jawa xenotypes are live at once:** `BTD_Jawa` (ours, patched),
`OuterRim_Jawa` (what the Jawa pawnKinds actually pin), and
`guy762_xenotype_jawa`. So **"a Jawa spawned" is not evidence** — the row closes
only on *which* one, and the answer must be `OuterRim_Jawa` or our patch is
decorating a xenotype nothing spawns.

⚙️ `list_pawns` does not return xenotype. The read comes off
`set_pawn_xenotype`'s read-back instead. **A gate whose evidence cannot be
collected is not a gate**, which is why this had sat as "verify only" all day.

### ⚖️ Row 5 RULED — it closes on `BTD_Jawa`. **Our tuning is NOT inert.**

🔴 **This reverses the ruling that stood here for an hour, and the reversal is the
lesson.** I ruled row 5 closes on `OuterRim_Jawa` and filed "our Jawa tuning may
be doing nothing in play" at VISION as v2. **Both were wrong.**

**BTD Xenotype Remix rewrites the xenotype set AT LOAD**, measured live by BRIDGE
from `Player.log`:

```
Current xenotype count: 250
Remapped 552 xenotype chances across 9 factions and 99 pawnkinds
Successfully removed 100 duplicate xenotypes (BTD preference active)
Final xenotype count: 150
```

**`BTD_Jawa` is what survives the dedup, and the pawnKind pins were remapped onto
it.** `OuterRim_Jawa` does not exist at runtime. Our patches target `BTD_Jawa` —
i.e. they target exactly the right thing. **Closed as checked-and-fine; the v2
item at VISION is withdrawn.**

📌 **THE TRAP, and it is general: a def dump is DISK, not RUNTIME.** The
three-Jawa finding came off a dump captured *before* the dedup ran. Any mod that
mutates defs at load — dedup, remap, implied-def generation — makes every
disk-derived conclusion about those defs unsafe. **When a claim is about what the
game HAS, only the live game or the log can settle it.**



BRIDGE raised the sharp version: **`OuterRim_Jawa` is what the pawnKinds pin;
`BTD_Jawa` is what our tuning patches target.** So a row 5 that closes on
`OuterRim_Jawa` closes on a pawn **our patches never touched**.

**MVP ruling (SUPERSEDED — see above): row 5 closes on `BTD_Jawa`.** The v1 bar is *"a Jawa
spawns and plays"*, and it does. Tuning depth is explicitly v2 under
"everything ships THIN".

🔴 **But it does NOT close silently, and this is the part that matters:** if our
patches target a xenotype nothing spawns, **our Jawa tuning is doing nothing in
play** — the same shape as seven art mods sitting deployed and inert. That is a
real finding, not a checkbox caveat. **Filed as v2, owned by VISION** (which
xenotype the campaign's Jawas should actually be) with CREATE re-pointing the
patches once ruled.

**Evidence path is two-deep, so the row is closable either way** — BRIDGE,
unprompted:

| | |
|---|---|
| primary | `jawa/set_pawn_xenotype` read-back — unproven, now first mutation in the batch |
| fallback | `rimworld/save_game` then grep the `.rws` — proven method, zero new code, costs one save |

**A gate with a proven fallback is a real gate.** The earlier re-word is
withdrawn.

### ⭐ THE SEQUENCING CONSEQUENCE — author everything, verify once

**Two of eight rows are still fully offline-authorable — 3 and 4.** That is down
from three, and the reason is worth keeping: row 2 was never offline, we had
misread the mechanism. So the expensive resource is not authoring time, it is
*verification passes* — and the way to spend one well is:

> **Author rows 3 and 4 offline → deploy → then run ONE session that generates
> the world, ticks the exclusions, builds the ship, and verifies everything.**

⛔ **Do not verify rows one at a time.** Each pass costs a load or a bridge
session, and the thin rows are independent — a faction label, a quest, and three
terrain overrides do not interact.

⭐ **THE ANCHOR MOVED, and this is the scheduling fact of v1.** It was the
gravship build. It is now **worldgen**, because worldgen is the one step that is
*upstream of everything else*: rows 2 and 7 happen only during it, and every other
row is cheaper to see in a world we just made than in one we inherited. The
gravship build (row 8) still wants the game and still anchors the *content* half
of that session — but it now runs **after** the world exists, not instead of it.

**So the next live session, in order:** generate the world with the exclusion list
in hand (rows 2, 7) → build and export the ship (row 8) → confirm rows 3, 4, 5, 6
on the new map. **Rows 3 and 4 must be authored and deployed BEFORE it starts**,
or that session cannot close them and we buy a second one.

### Faction Control is live but has NO SUPPRESSION FIELD — row 2 is at zero

Measured in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_2882785581_Controller.xml`:
**41 faction entries, all bare** `<faction>NAME</faction>` with no settings, and
`masterDensity` **0**. *(Was written here as 32 and as a repo-relative path that
resolves to nothing; both corrected 2026-08-13, re-counted at the real path.)*

⚠️ **Do not read `masterDensity: 0` as "zero factions".** A `Mod_*.xml` records
what was *changed*, never what the mod *does* — and the mod's own English label
is *"Master Density Slider (careful: edits all faction sliders!)"*, i.e. a bulk
convenience control, not a kill switch. **The config is untouched, not
configured.**

**So U1's mechanism is confirmed available and has never been used.** Row 2 is
unstarted, not partially done.

## What v1 explicitly does NOT contain

Named so nobody re-proposes them:

- The 11 unbuilt faction dossiers, and all of Stage 3 / Stage 4 authoring
- The **energy-density explosion model** (`TODO.md` §1) — large, self-contained, pure v2
- **Water and thirst doctrine** — the declared master resource, zero implementation, v2
- The **two-Empire aristocracy design** beyond a label reskin
- **Free Droid Enclaves** (U3), the Homestead Jedi wiring (U4)
- Custom resource-terrain matrix beyond three visible overrides
- Deck-plan detailing past "built and boardable"

**None of these are cancelled.** They are the v2 register, and v2 starts the day
v1's gate passes.

---

## Ongoing work that is NOT frozen

**The owner chose not to freeze in-flight work.** It continues alongside v1, with
one condition:

> **In-flight detail work must not add to v1.** Anything it turns up is filed
> `[v2]` unless it blocks a v1 row.

That covers `TODO.md` §12's remaining sweep, W8, the deploy hold-list, and the
traps logs. **The one piece explicitly on the critical path is BRIDGE's live
tooling**, because the gate depends on it.

---

## How the seat works

**PROJECT sets scope; the other four own execution.**

- PROJECT declares v1/v2 and may tag any item deferred.
- BRIDGE, OPS, CREATE and VISION decide **how** to build their part — PROJECT does not
  touch their files, tools or methods.
- **Disagreement goes to the owner**, not to PROJECT. A peer may not add to v1
  unilaterally; PROJECT may not halt work.
- Rule 0.5 is unchanged: findings outside scope get **filed**, never dropped.

**PROJECT publishes the burn-down** — the v1 table above, with each row's
verification state — and is accountable for it being honest, including when the
answer is "no progress this session".
