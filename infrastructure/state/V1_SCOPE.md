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
| **Xenotype / crew** | Jawa xenotype spawns and plays. Already largely live. | Crew personas, dialogue, per-pawn backstory wiring. |
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

| # | v1 row | built | verified | owner | needs a load? |
|---|---|---|---|---|---|
| 1 | Empire reskin (labels only) | 🟩 **BUILT** | 🟩 **SEEN LIVE** | CREATE | ✅ done |
| 2 | Faction exclusion at worldgen | ⬜ **0** | ⬜ | **OPS** + VISION | 🔴 **YES — it happens DURING the worldgen run** |
| 3 | One `QuestScriptDef` | ⬜ **0** | ⬜ | **CREATE** | 🟢 **NO — closable offline today** |
| 4 | Three terrain overrides | ⬜ **0** | ⬜ | **CREATE** | 🟢 **NO — closable offline today** |
| 5 | Jawa xenotype plays | 🟩 largely live | ⬜ | **BRIDGE** | 🔴 verify only |
| 6 | Weapons/gear | 🟩 6 mods live | 🟩 partly | **BRIDGE** | 🔴 verify only |
| 7 | Ordinary worldgen | ⬜ **0 — now a DO** | ⬜ | **BRIDGE** | 🔴 **YES — we generate the world** |
| 8 | ⭐ **Gravship (DEEP)** | ⬜ design only | ⬜ | **CREATE** | 🔴 **build wants the game** |

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

**Build ≈ 0 on every authored row.** Rows 5 and 6 are inherited from the mod
stack, not built by us.

⚠️ **AMENDED 2026-08-13 overnight — the owner reassigned CREATE to the Bantha
reskin** (`TODO_v2.md` §0c: finish the eopie sled, then Banthas for four
horse/ox vehicles, desert art). **That is v2 work pulled into v1 time by the
owner — their call, not an appeal, and recorded rather than argued.**

**Consequence, stated honestly because the burn-down is worthless otherwise:**

- **Row 3 (`QuestScriptDef`) — not started, and now unowned in practice.**
- **Row 8 (gravship build) — not started.** The *spec* is unaffected and complete
  (`b7e49db`); only the build slips. CREATE still anchors the next live session.
- **Net: v1 build is still 0, and the two rows that moved were both CREATE's.**

**This is the drift the MVP seat exists to make visible, not to prevent** — the
owner may spend v1 time on v2 work; PROJECT's job is to say so plainly.

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
