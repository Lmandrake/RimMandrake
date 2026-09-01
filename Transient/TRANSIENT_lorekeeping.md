# The lore docs — is it a nightmare, and what would fix it

**2026-08-20. Nothing here is decided.** Measured across all 119 design docs / 46,488 lines.

---

## The short answer

**It is not a filing problem. It is an agreement problem — and reorganising the folders would fix
none of it.**

The structure is genuinely fine. What's broken is that **the same fact is written down in five
places and four of them are stale**, and nothing can tell. Every one of the worst contradictions
below is between files **already sitting in the same directory**. Moving them into a nicer
hierarchy does not make them agree.

**The one thing worth doing is extracting the numbers into a file a script can check.**
That is also, word for word, this project's own rule — `CLAUDE.md` already says: *"Single-source
only what a GENERATOR can enforce. Four hand-kept copies of one text is a drift machine; one source
plus a script is not."* It has simply never been applied to `design/`.

---

## What is already good — leave these alone

| | |
|---|---|
| **The tier doctrine exists and is sound** | `design/README.md` — intent vs fact, the Jawa/RimMandrake split, the promotion test in your own words |
| **The index is already generated** | `design/INDEX.md` is written by `doc_roster.py`, not by hand. The classic index-rot problem is solved |
| **The graph is well connected** | **507 cross-reference edges.** Only **2 true orphans** in 119 files |
| **Nothing is abandoned** | 90 of 119 docs (76%) touched in the last two days |
| **Design is deliberately unbudgeted** | `doc_budget.py:41` — *"their length is content, not accumulation."* That call is correct. A 2,591-line faction roster is not bloat |
| **One doc already does supersession right** | `bridge/INHABITED_DESIGN.md` keeps the dead sentence **visible**, *"because [it] is exactly what a later reader would otherwise act on."* **This is the pattern to copy** |

**Two five-minute fixes, unambiguous:**

1. **`doc_roster.py` already knows the index is stale.** It prints `OUT OF SYNC design/INDEX.md`
   and **exits 1** — and nothing runs it. `INHABITED_CAST_EMPIRE.md` and `INHABITED_CAST_TUSKEN.md`
   are on disk and missing from the index; that is the *entire* reason they scored as orphans.
   Run `--write`, wire it to a commit hook.
2. **`RimMandrake/save_authoring_pipeline.md` is marked `⛔ DEAD DOCUMENT`** — and is still linked
   from a live doc and still listed in `INDEX.md` with no marker.

---

## What is actually broken

Twenty-one contradictions found. These are the ones where **acting on the stale side builds the
wrong planet.** I verified the top two by hand.

### 1. Water: 8.1% or 25%? One file says both, 30 lines apart

- `the_one_map.md:100` — *"**Sea** — ~25% of tiles water, accept **22–28%**"*, written as a live constraint
- `the_one_map.md:130` — the owner's ruling that *"that spec and that number are both dead"*, target **~8.6%**
- `ASHKARR_WORLD_DEFINITION.md:92` — **8.1%**, measured off the painted map

Still on 25%: `tidally_locked_world.md:200`, `faction_world_spec.md:485`, `worldgen_interactive_def.md:29`.
**Even the survivors disagree** — 8.1% vs 8.6% vs 6.9%.

### 2. Terminator temperature: +14 °C or −37 °C — 51 degrees apart

- `tidally_locked_world.md:162` — *"0.5 → **+14 °C** — this is the terminator"*
- `ASHKARR_WORLD_DEFINITION.md:77` — read from the mod's own C#: the mod's curve gives **−37 °C**
  at the terminator; ours gives +14. *"Same endpoints, **51 °C apart at the terminator**."*

🔴 **And the error propagated.** `hydrology_and_fire_ecology.md:529` cites the wrong file and
concludes *"The active planet curve already agrees"* — exactly backwards. ASHKARR says the importer
**must overwrite temperature on every tile** or the world is uninhabitable where the people live —
*"exactly the kind of defect that passes every numeric check."*

### 3. Everything else that has two answers

| fact | the answers | who's right |
|---|---|---|
| **Faction count** | 14 · 13 · 12 · 11 | **13** — the Unbound Hive was cut, and `faction_world_spec.md` still lists it live |
| **Settlement count** | 72 · 66 · 37 | **72** — 66 and 37 are measurements of dead generated worlds, unmarked |
| **Species count** | 42 · 44 · 54 · 70 · 79 · 80 | unresolved. `faction_roster_v2.md` cites a file as agreeing that says a different number |
| **Habitable ring** | 34–57° · 40–57° | ~700 tiles of disputed habitability |
| **Mod count** | **nine different stamps**, 568→587 | no doc carries an as-of date, so *"read from the live dump"* is unfalsifiable everywhere |
| **Biome survivors** | 36 · 37 · ~35, from a 66- or 57-def base | the build patch is specced against a count the decision file doesn't match |
| **Who holds the oases** | Hutts (roster, ASHKARR) vs Deepwater Compact (`FACTION_SPEC.md:224`) | inverts the campaign's water politics |
| **Jawa leader title** | First Bargainer (owner canon) vs Prime Trader (`FACTION_SPEC.md:294`) | the engine layer ticks the field ✅ correct while overwriting your canon |
| **`AB_GelatinousSuperorganism`** | cut 2026-08-04 · placed 2026-08-18 | the palette was never told it was un-cut |
| **`Lake`** | cut by you · **1.4% of the planet is Lake** | ~300 tiles of a biome you deleted |
| **The savanna** | the subject of a 701-line doc | `Savanna` is blacklisted; its carrier was cut to 2.0% and gated to riverbanks |

### 4. The shape of the failure, every time

```
   a better doc is written
        ↓
   it cites the doc it replaced          ← always happens
        ↓
   the replaced doc is never told        ← never happens
        ↓
   a reader arriving from the old doc gets the dead number
```

`worldgen_interactive_def.md` is the worst case: its banner kills the *pipeline* but then says
*"the DESIGN rulings and **measurements** are unaffected and still canon"* — **actively pointing
the reader at 6.9% water, 37 settlements and 11 factions, all superseded.**

---

## Your question: how much of it has become real?

**Counted, not estimated** — every named thing grepped against a 1,404-entry index of every
`defName` and `label` under `src/`.

| layer | named | built | rate |
|---|---|---|---|
| Settlements | 72 | 72 | **100%** |
| Faiths (current canon) | 12 | 12 | **100%** |
| Cast characters | 269 | 269 | **100%** |
| Species / xenotypes | ~70 | 71 | **~100%** |
| Factions | 14 (1 cut) | 13 | **93%** |
| World regions | 32 | 24 | **75%** |
| Ship hull designs | 15 | 1 | 7% — **correct**, 14 were candidates |
| **Cast places, as world entities** | 32 | 6 | **19%** |
| **Faiths in `faction_roster_v2.md`** | 12 | **0** | **0%** |
| **`Alien_Bestiary.md` creatures** | 78 | **0** | **0%** |

**Three honest headline numbers, depending on what counts:**

- **82%** if a name existing as free text inside a def counts
- **60%** excluding the two bulk machine-generated layers
- **51% ±8%** strict — a place must be an addressable world entity, not a string on a character record

🔴 **The two numbers I'd defend without qualification, because they were exact-matched:**
**0 of 78 bestiary creature names** and **0 of 12 superseded faith names** exist anywhere on disk.
I re-checked ten bestiary names by hand — *cinderak, kor'dak, ghorn, kraddak, grondar, karrakoth,
chakrir, vhaggan, sslarn* — all zero.

### Queue coverage, and why the raw number lies

- **19 of 69** lore docs (28%) are named by any queue item
- **42 of 69** (61%) have never been named by a queue item **or** a commit body

⚠️ **That undercounts real traceability by 5–8 docs**, and the reason matters: the generators cite
their source docs **in file headers instead of in queue items.** All 10 cast docs were mechanised
into 269 CharacterDefs by `cast_to_xml.py` without a single queue item naming them. `faction_religions.md`
produced every `<ideoName>` on disk and appears in no queue. `v1_quest_the_claim.md` has a shipped
`QuestScriptDef` and appears nowhere.

**So "unmentioned" does not mean "unused."** But it does mean **nothing records that it was used** —
which is the same defect in a different coat.

### Where the genuinely unconsumed prose is

`Alien_Bestiary.md` · `water_doctrine.md` · `orbital_towers_and_the_sky_ladder.md` ·
`gravship_pursuer_mechanism.md` · `hiding_the_gravship.md` · `tile_augmentation_catalogue.md` ·
`setting_physics.md` — **~2,000 lines with no artifact and no mention.**

⚠️ One caveat I'd hold to: `hydrology_and_fire_ecology.md` is on that list, but ASHKARR §4's
hydrology is marked *"ruled"* and clearly descends from it. Its conclusions were absorbed; only the
**link** is missing. Judge these by inspection before deleting anything.

---

## Three options

| | what it does | cost |
|---|---|---|
| **A. Canon file + checker** | Pull the ~40 numbers that get repeated into one machine-readable file. `check_canon.py` scans every design doc for a conflicting value and fails. Fix the 21 findings. | **1–2 days** |
| **B. A + status headers** ⭐ | Every design doc gets one header line: `status: live` / `superseded-by: X` / `dead`. The checker refuses a link *into* a dead doc; `INDEX.md` renders the status. | **+1 day** |
| **C. Restructure the tree** | Rename, renumber and merge the 119 files into a hierarchy. | **~a week** |

**Why C is the one I'd skip:** all four faction docs are already in `worldbuilding/`. All the world
docs are already in `worldbuilding/`. **The contradictions are inside topics, not across folders** —
a better tree relocates them without resolving one of them. And a big rename breaks 507 cross-links
and every `git log --follow` at once.

---

## What I'd do

**A + B, in this order:**

1. **Today, 5 minutes.** Run `doc_roster.py --write` — the index is out of sync and the tool already
   knows it. Wire it to a commit hook so it can't drift again.
2. **`CANON.yml`** — the ~40 repeated numbers in one place: water %, the temperature curve, faction
   count, settlement count, arc bands, biome census, the mod count **with an as-of date**.
   Every one of them currently has 2–9 answers.
3. **`check_canon.py`** — scans all 119 docs for a number that contradicts canon and fails with
   `file:line`. This is the piece that makes it stay fixed. Without it, this document describes a
   condition that will simply regrow.
4. **`status:` headers**, then make the checker refuse links into dead docs. That structurally kills
   the "nobody reads backwards" failure, which is the single mechanism behind almost every finding above.
5. **Fix the 21 findings** — worth doing in one pass, since they're now located.
6. **Decide about the bestiary.** 78 creatures and 288 lines: either it becomes queue items or it
   moves to `V2_DREAMS.md`. Right now it's neither, and it reads as canon.

**One thing I'd deliberately not do:** delete the untraced docs. `hiding_the_gravship.md` and
`water_doctrine.md` have no artifact because **the campaign hasn't reached them yet**, not because
they're dead. The fix for those is a `status:` line, not a `git rm`.

---

## The honest counter-argument

The world freeze is ahead of you and this is a game, not a documentation system. **Step 1 is five
minutes and step 2–3 is a day**, and together they catch the class of bug that would otherwise put
25% water or a −37 °C terminator into the one world you get to build by hand.

Steps 4–6 are a further two days that buy tidiness and future-proofing. If the freeze is close,
**do 1–3 and stop.**
