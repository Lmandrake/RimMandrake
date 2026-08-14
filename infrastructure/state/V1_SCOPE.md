# V1_SCOPE.md — what ships in the alpha, and what waits

_Owner's scope decision, 2026-08-13. **PROJECT holds the MVP seat**: PROJECT sets
the v1/v2 line, the other four own execution. Appeals go to the owner, not to
PROJECT._

**Read this before adding anything to a seat queue or `NEXT_RELOAD.md`.** If an item
is not v1 by the rule below, tag it `[v2]` and move on. *(`TODO.md` is a retired
pointer stub — work is filed at `infrastructure/state/queue/<SEAT>.md`.)*

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

### ✅ ROW 8 CLOSED — built, exported, boardable, deck-plan-faithful. `6909ecb`

31 steps · 4,057 foundation + 4,057 floor cells · 1,053 things · exported to
`design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml` (2.0 MB) with
`Gravship_v1.png` beside it. **Doors in the outer hull confirmed by the owner.**

> **Row 8 closed on an ARTIFACT, not a map state** — which is why a quicktest
> counted. Built-but-unexported would have closed nothing.

✅ **The floor contradiction is CLOSED and the exporter's README was wrong.** 4,057
`terrainDef` cells survived the round trip (3328 MetalTile, 507 SterileTile, 197
WoodPlankFloor, 25 CarpetMarine), matching exactly what was laid. **Anyone about to
hedge a design on "floors cannot be saved" should stop.**

⚠️ **Two things row 8 does NOT claim:** no pawn has walked aboard, and **the ship
cannot fly** — the deck plan ships no thruster, fuel tank or controls, and the engine
reads *"Requires: Thruster, fuel tank, controls."* **Flight was ruled OUT of row 8's
bar and stays out.** *"The gravship is done"* and *"the gravship cannot move"* are
both true. → **Is flight v1-adjacent or v2? VISION and CREATE's call, not mine.**

🔴 **FLOORS DO NOT COME WITH A MID-GAME SPAWN.** Terrain is re-applied by the
*arrival* patch, which does not run for a Sketch spawned mid-game. **Structure lands,
floors do not, and nothing errors.** Replay the layout's `terrainDef` cells through
`jawa/set_terrain_batch` after the spawn.

📌 **A lesson of mine, kept because it recurs:** I found a capability in an assembly
and described what it would *enable* rather than what it *does*. **Reading a symbol
is not reading the call path. State what you measured; the inference is a separate
sentence.**

### ➕ RIDERS ON ROW 4 — both owner-ruled, neither a new row

1. **The deconstructible-only filter.** A filtered palette of wreck props that are
   actually deconstructible, excluding `NonDeconstructibleAncientBuildingBase`.
   **An ingredient, not a feature** — any wreck we place is unstrippable garbage
   without it. ✅ **LANDED:** 181 ruins defs, **167 deconstructible**, but only **55
   carry a `costList`** — over half the kit is scenery, not salvage, which is where
   the v2 economy actually lives.
2. **The hulk IMAGE** (the *system* — tiers, cross-section, salvage economy — is v2,
   unconditionally, no appeal). It rides `Patches/JawaResource_Scrapfields.xml`
   inside row 4: same `GenStep` mechanism, already proven and deployed.

**✅ APPROACH RULED: stamp BRIDGE's exported `ShipLayoutDefV2`, do NOT write a shape
generator.** Scrapfields *scatters*; a hulk has a *shape*, and random placement gives
confetti. A parser we already own beats a generator we would have to invent — and it
is better fiction, because the hulk is the same class of vessel the clan flies.
⚠️ **Accepted risk:** this couples row 4's rider to the export format.

| | |
|---|---|
| who picks WHICH fragment | **VISION** — a fiction question |
| who crops and stamps | **CREATE** |
| hard ceiling | 🔴 **1,200 cells.** A ceiling, not a target — the crop size *is* the work size |

**✅ KILL CONDITION 1 PASSED on all four tests.** `BrokenSubstructure` (Gravship
Crashes): sits on ordinary desert (`terrainAffordanceNeeded: Walkable`, **no
`placeWorkers`**, unlike Odyssey's `Substructure`), walkable, reads as broken at
64 px — **the only one of three candidates that does** — and is spawn-only.
⭐ It carries `<tags><li>Substructure</li></tags>`, so it **connects and counts
toward capacity**: visually ruined, structurally sound.
⏱️ **KC2 stands: one afternoon, hard stop.** Over that and it is v2.

#### 🪤 TRAP — read the `tags`, never the `affordances`

`BTD_QuestSiteSubstructure` carries `Substructure` in its **affordances** but **not**
in its **tags**. Things build on it and it does **not** connect to the grav field.
**Anyone authoring against the wrong field gets a confident, wrong, silent answer.**
### ✅ ANOMALY IS AT ZERO — owner's ruling 2026-08-13, ticked during the worldgen run

**Anomaly content is set to zero, for certain.** It is a setting on the same
irreversible run as rows 2 and 7, so **whoever drives that run ticks it there** —
it is not separate work and it is not a v1 row.

⭐ **Creatures and abilities stay ours to reskin.** The DLC remains enabled; only the
storyline is off. **A reskinned Anomaly creature in our own content is unaffected by
this setting** — do not treat the zero as a ban on the assets. It also resolves
`HoraxCult` and `Entities` in `WORLDGEN_FACTION_CHECKLIST.md` §3, which were carried
as an open proposition.

**The setting is `Disabled`, and it is editable mid-campaign** (Options → Gameplay →
storyteller/difficulty → Anomaly settings). Proven by IL xref of every reader of
`enableAnomalyContent`: it gates incident firing, study, the threat budget and
thing-set/trader-stock inclusion, and **never touches the def database, textures or
map generation.**

### ✅ THE ANOMALY CHERRY-PICKS STAND — owner, 2026-08-14, correcting me

> *"I did NOT agree to that anomaly ruling! I want to use some of those creatures…
> leave them in with Anomaly set to zero but enabled, so we can still spawn them.
> And add my cherrypicks! Do not revert them!"*

**All three of the owner's positions hold together and always did:** playstyle
`Disabled` so content is at zero · **DLC enabled** so the assets stay reachable ·
**and the rejected creatures removed.**

🔴 **I withdrew the picks on a false premise and it cost the owner nine verdicts they
had already given.** I read the removal list, recognised Anomaly creature defs, and
called them "the donor library" — **the two sets are DISJOINT.** The picks are what
the owner *rejected* (metalhorror, shamblers, ghouls, golden cube, corrupted and
warped obelisks, revenant spine, trispike). The donors are what the owner *kept*
(sandscreamers, noctols, revenant, twisted obelisk, kybersphere, the sarlacc line,
the Helix's three, the scurrier). **Nothing in the picks touches a donor.**

📌 **The lesson is not the one I wrote here first.** *"Deleting defs destroys
donors"* is a sound principle, reasoned from evidence — **it simply did not describe
these defs.** A correct general principle applied to the wrong set is more dangerous
than a wrong principle, because the reasoning survives review.

> ⭐ **The check that would have caught it, and it takes two minutes: does the
> removal list INTERSECT the keep list?** It was never run. Run it before arguing
> that a removal is unsafe.

*(The suppress-scope-delete rule stands on its own merits and is unaffected — the
biome reroute to `PlanetTypeDef.biomeBlacklist` was right for its own reasons.)*

## 🔴 BEFORE THE NEXT WORLDGEN — things that cannot be patched in afterwards

**Worldgen is HELD by the owner (2026-08-14) until the sea is shapeable.** That hold
is not free time — it is a window, and these must land inside it. **Each is read
once, at world or pawn generation; a patch after the fact does not fix an existing
world.**

| # | item | owner | why it cannot wait |
|---|---|---|---|
| W1 | **The sea** — **patch the shipped `TidallyLocked` `PlanetTypeDef` by defName**, plus a step that arranges three ragged blobs and *measures* to 25% | VISION specs · CREATE builds | ocean is elevation at step 0 |
| W2 | ✅ **DONE** — `Jawa_Patches/Patches/JawaXenotype_Repoint.xml`, deployed and verified. The two Galactic Diversity `PawnKindDef`s (`OuterRim_Jawa`, `OuterRim_JawaTribal`) now point at `BTD_Jawa` at weight 999. ⛔ **Settles those two kinds only** — the three competing Jawa xenotypes are still VISION's larger ruling | CREATE | was: **read at pawn generation** — an existing world's colonists stay wrong |
| W3 | ✅ **RATIFIED** `6370746` — 2 abundant · 4 common · 22 rare · Ocean/Lake by elevation · 7 layer biomes needing no verdict. Owner added a fourth zone: a graded nightside, `Glowforest` as oases of light in the deep dark. **Blacklist, never whitelist** | VISION | biome scoring runs once |
| W4 | The ratified faction tick-list, unspent | OPS at the screen | the page is seen once |

### ⚖️ THE SEA STEP RE-SCOPED — smaller than when I ruled it v1, and still v1

**VISION corrected its own axis correction, and the second one is the mechanism:**
`Tidally Locked` maps temperature onto **latitude** — 0.0 = +70 °C subsolar, **0.5 =
+14 °C, the terminator**, 1.0 = −37 °C, 2.0 = −80 °C. ⇒ **the target is mid-latitude
0.4–0.6**, not the poles and not the equator. The owner's *"one near a pole"* now
reads as **a sea on the freezing nightside**, which is better fiction than it was as
a shape note.

⭐ **Much of it is XML, not C#** — `AlienWorlds.PlanetTypeDef` (`7f.alienworlds`,
active) exposes `elevationRange`, `biomeConfigs`, `biomeBlacklist`, `oceanBiome`,
`sunlightFactor` and `rainfallCurves`.

🔴 **Two corrections to what this section first said, both VISION's and both mine to
have recorded wrong:**
1. **Do NOT author our own `PlanetTypeDef` — only ONE is active at a time.** A Jawa
   world would *replace* `TidallyLocked` and drop the temperature curve the whole
   design rests on. **Patch the shipped def by defName.**
2. **`elevationRange` is NOT a reliable ocean dial.** The mod author's own comment
   reads *"I have absolutely no clue how it actually works."* Treat it as a coarse
   nudge; **the step measures and hits 25%** rather than trusting the field.
3. **Blacklist, never whitelist.** A whitelist silently excludes `Space`, `Orbit`,
   `Underground` and the undercaves, breaking every pocket map.

⇒ **The code shrinks to ONE job: arranging three ragged blobs.** The one-day kill
condition stands and is now comfortable rather than tight. ⚠️ **Registration is still
required and still silent** — a `WorldGenStepDef` absent from `PlanetLayers.xml`
loads, validates and never runs, with no log line.

## ⚠️ Sequencing — the two dependencies that can cost a whole cycle

### 1. `jawa/list_factions` needs a SHUTDOWN window, not a startup

The gate requires **seeing a faction on the map**, which needs
`jawa/list_factions` — companion-DLL work, and therefore gated on a **shutdown**
rather than a startup (`skills/rimworld-load-round/SKILL.md` §6).

> **Whoever calls the next shutdown tells BRIDGE BEFORE the game closes.**
> Miss the window and the v1 faction row waits a full ~25–30 min cycle.

BRIDGE has it ranked #1 and V1-CRITICAL (`b2a0a36`); rotation, style and xenotype
setters are tagged `[v2]`.

### 2. ✅ Gravship round-trip — ANSWERED offline, `b7e49db`

Reusable artifact; the deep build was unblocked without a game. **The lesson worth
carrying:** this was filed as needing *"a live session and a built ship"* and needed
neither — the answer was in files on disk. **Before booking the scarcest resource we
have, check whether the question is answerable offline.**
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
| 4 | Three terrain overrides | 🟩 **BUILT**, deployed | 🟨 **2 of 3 SEEN** — salt pans + dune seas | CREATE | 🔴 **scrapfields is a measured DEFECT, not a blank** — 11 chunks against a predicted 75–125. OPS **O15**, `a82f50b` |
| 5 | Jawa xenotype plays | 🟩 live | 🟩 **CLOSED — checked-and-fine** | BRIDGE | ✅ **CLOSED.** `BTD_Jawa` survives BTD's load-time dedup and the pawnKind pins were remapped onto it, measured live from `Player.log`. Our patches target the right xenotype |
| 6 | Weapons / gear | 🟩 6 mods live | 🟩 **`JawaIonWeapons` PROVEN** `ad3e9b0` | BRIDGE | ✅ **CLOSED** |
| 7 | Ordinary worldgen | ⬜ | ⬜ | BRIDGE | 🔴 the campaign desert world |
| 8 | ⭐ **Gravship (DEEP)** | 🟩 **BUILT + EXPORTED** | 🟩 **SEEN — 4 of 4** | CREATE/BRIDGE | ✅ **CLOSED** |

> ### 📊 SCORE: **4 of 8 closed** — rows 1, 5, 6, 8.
>
> **Row 4 moved 1-of-3 → 2-of-3 on 2026-08-14, and its last item turned into a
> defect.** ✅ **Dune seas CLOSED** on a live `jawa/get_def defType=BiomeDef` read
> needing no map: `Desert` SoftSand min **0.55** (was 0.65), `ExtremeDesert`
> **0.5**, and `AridShrubland` gained a patch maker at maxFertility 0.45 / min
> 0.70 matching `JawaTerrain_DuneSeas.xml:112-117` exactly — so it is ours, not
> vanilla. **The no-eyeball gate was right and was honoured.**
>
> 🔴 **Scrapfields did NOT pass, and this is the honest reading: it is worse than
> unverified, because it was measured.** 11 `ChunkSlagSteel` over 62,500 cells —
> one per 5,700 — against a prediction of **75–125** put on record *before* the
> look. ⭐ **The prediction is what makes this a finding rather than a shrug.**
> `Filth_MachineBits` sits at 433 cells in 52 clusters, and the ~3-per-chunk ratio
> implies **~137 chunks were placed**, so ~126 went missing by tick 485 — or the
> filth has another source on the stack. **No `could not find cell` warning fired.**
> Splitting test is OPS **O15**, `a82f50b`. **Do not green row 4 until it resolves.**
>
> ⚠️ **Row 3 is not "awaiting verification" — it is BLOCKED on a missing tool**
> (`NEXT_RELOAD.md` §7: the rumour needs a float menu, `rimworld/right_click_cell`
> is measured broken). A `jawa/fire_quest` proposal is with BRIDGE.
>
> 🔴 **Rows 2 and 7 are ONE event, and it is HELD by the owner** until the sea is
> shapeable. They are not blocked on us and not late — they are deferred by choice,
> and the ratified tick-list is unspent.


### ⚠️ ROW 4's THIRD ITEM HAS THE WRONG GATE — corrected by CREATE at wrap

**Dune seas is a DENSITY change, 0.65 → 0.55.** It was written as a look-at-the-map
check and that is unjudgeable: **nobody can eyeball a 15% density difference
without a control map.** A seat could stare at a correct result and call it
failed, or at a failed one and call it passed.

> **Correct gate: a live `BiomeDef` read.** Confirm the value the game holds, not
> what the sand looks like.

📌 **Eleventh instance today of the same defect: a gate whose evidence cannot be
collected as specified.** Rows 2, 5, 7 and now 4 all had one. **When writing a
gate, name the CALL that produces the evidence** — if you cannot name it, the
gate is a wish.

### 🪤 DO NOT READ ROW 2 OFF A QUICKTEST — it nearly cost a regeneration today

**A debug quicktest never visits the Configure Factions page**, so **all 54
factions are present by default** on one. Seeing them there proves *nothing*
about the tick-list, and reading it as failure nearly triggered a needless
25–30 minute world regeneration.

> **Row 2 is UNEXECUTED, not failed.** The checklist is ratified, committed and
> ready. It can only be spent on a real worldgen.

📌 Same shape as every other trap today: a true observation — *54 factions are on
this map* — read as a false conclusion. **Ask what the observation could NOT have
shown before acting on it.** (OPS, at wrap.)

### 🔴 THE HEADLINE: the campaign world has still not been generated

**Everything proven so far was proven on a QUICKTEST map.** Rows 2 and 7 are the one
irreversible step and they have not happened — now **held by the owner** until the
sea is shapeable (see the pre-worldgen gates above).

⇒ **Nothing is lost.** The tick-list is ratified and committed, the ship is an
exported artifact, quest and terrain are deployed. **But the gate for four rows is
still one screen away, and that screen is deferred by choice.**

🔴 **Row 7 stopped being an observation and became an ACT.** It read *"BRIDGE
confirms desert worldgen and it closes"* — true while v1 shipped an existing save.
Under the no-savegames ruling BRIDGE *generates* that world, and **rows 2 and 7 are
one event that must be scheduled as one.**

📌 **The lesson, because it will recur:** a row sat at *"closable offline today"* for
a full day on the strength of a **mod's own UI label**. Reading the label is not
reading the mechanism. **A v1 row whose build step is "change a setting" must have
that setting's effect confirmed in the assembly or the source before it earns a
row.** This one had no effect to confirm.
### ✅ Row 5 — CLOSED as checked-and-fine. Do not re-investigate.

**BTD Xenotype Remix rewrites the xenotype set AT LOAD** — measured live from
`Player.log`: 250 xenotypes in, 552 chances remapped across 9 factions and 99
pawnKinds, 100 duplicates removed, 150 out. **`BTD_Jawa` is what survives and the
pawnKind pins were remapped onto it**, so our patches target exactly the right
thing. `OuterRim_Jawa` does not exist at runtime.

📌 **THE TRAP, and it is general: a def dump is DISK, not RUNTIME.** The
three-Jawa finding came off a dump captured *before* the dedup ran. Any mod that
mutates defs at load makes every disk-derived conclusion about those defs unsafe.
**When a claim is about what the game HAS, only the live game or the log settles
it.**
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

### Row 2's mechanism, settled — Faction Control has NO suppression field

`FactionDensity` serialises `faction`, `density`, `enabled`; **`density` is a
clumping radius, not a count**, and none of the three removes a faction. The row had
been written against the mod's own English string, a pre-1.3 leftover. **Faction
exclusion is vanilla's Configure Factions page**, which Faction Control unlocks
rather than replaces — reachable only during a worldgen run.
## What v1 explicitly does NOT contain

Named so nobody re-proposes them:

- The 11 unbuilt faction dossiers, and all of Stage 3 / Stage 4 authoring
- The **energy-density explosion model** (`TODO_v2.md` §1) — large, self-contained, pure v2
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

That covers the fail-toward-success tooling sweep (now
`skills/rimworld-modding/references/traps-tooling.md`), W8, the deploy hold-list,
and the traps logs. **The one piece explicitly on the critical path is BRIDGE's live
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
