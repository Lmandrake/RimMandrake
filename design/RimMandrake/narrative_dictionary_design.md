<!-- status: approved-design, pilot not built -->
# Narrative Dictionary — design spec

**Status: design approved by the owner at the bench, 2026-09-15. Nothing built.**
Pilot is filed as `NARRATIVE_DICTIONARY_PILOT_1`.

**Tags**, following `beautiful_tilemap.md`'s convention:
`CONCEPT` = the owner's idea as given · `VERIFIED` = measured against files in this
repo, on the machine and date named · `SOURCED` = grounded in a fetched source, cited ·
`ANALYSIS` = added reasoning, decided in this session.

---

## 1. The concept — `CONCEPT`

Owner, 2026-09-14, verbatim: *"Run through every object in the game for its LOOKS…
and decide from a NARRATIVE point of view why you might use it. Compile a 'narrative
dictionary' for the Rimworld agentic system to use to construct tile-based maps with
meaning."*

His two worked examples, which turn out to sit on established vocabulary (§4):

> Stencilled text on the ground looks governmental, authoritarian, industrial,
> old/worn, powerful, organized, but it also can be used to make SPACES, DIRECTION,
> WARNINGS, or FORBID things. Potted plant looks homey, kept, comfy, nurturing,
> decorative, life-affirming, welcoming, but it can also be used to define
> BOUNDARIES, CORNERS, EDGES, or SPECTACULAR SHOWPIECE.

The component fills a real hole: it is the step that turns an abstract room graph into
concrete dressed tiles.

## 2. What was decided in this session — `ANALYSIS`

Five rulings, each the owner's choice among presented options.

| # | Decision | Consequence |
|---|---|---|
| 1 | **Claim-primary, mood as filter.** One index, two entry points. | Primary query is `claim + mood → candidates`; mood ranks and constrains, it never forms a second vocabulary. |
| 2 | **Vertical slices in lockstep.** Each batch = object sheets + the vignettes using them + a dressed room + a test result. | Every batch is independently judgeable. No wide-then-deep phase split. |
| 3 | **Contact-sheet vision + def text**, with per-field provenance. | Vision is authority on looks; def text on function. Which signal produced which field is recorded. |
| 4 | **Blind naive-reviewer test against a control**, bar pre-registered. | The project can fail. See §7. |
| 5 | **defNames, no intermediate role layer.** Lives in RimMaster; promote later if ever. | §3. |

### 2a. Why there is no role layer — `ANALYSIS`

An abstract role vocabulary (`CONTAINER_LARGE`, `MARK_FLOOR`) was proposed and the
owner rejected it: *"This is the piece that goes from gamecontentdesign to the actual
tilemap, so I'd need to be convinced we need yet another intermediate representation
with the roles specified."*

He was right, and the arguments for it did not hold:

- **Promotion to a generic repo was YAGNI** — he had already ruled "build here,
  promote later."
- **The gap ledger does not need roles.** A gap is "this claim has no adequate
  candidate, or all candidates fail legibility" — computable directly over defNames.
- **RimWorld already ships a role taxonomy**: `thingCategories`
  (`ThingCategoryDef`), `designationCategory`, `stuffCategories`, `tradeTags`. A
  hand-maintained parallel vocabulary would be a worse duplicate.

**The generalisation lives in the query, not in a new file.** A vignette specifies a
*predicate over the featurization axes*; the query resolves it to concrete defNames.
Output is defNames — terminal, exactly what the placement engine consumes.

Staleness is handled where it already is: `rimplace verify` checks every defName
against `DefDump/defs.sqlite` and explicitly refuses to trust its own `palette.json`
`VERIFIED` (per `rimplace` CLI, 2026-09-15). `objects.jsonl` is therefore a *function
of the live mod set*, regenerated when the set changes rather than defended against
change.

## 3. Pipeline position — `VERIFIED`

Both neighbours exist and are not to be reimplemented.

```
GameDesignContent/tools/picker/          ← exists. plan.py scores room graphs,
  ROOM_KINDS × GATES → bubble diagram      renders bubble diagrams for curation.
                                           Its README: "It does not make maps."
            ↓
  area brief with CLAIMS                 ← commissions/S01-stage2-sample.md format
  owner / purpose / act
  when it ran / when it fell / as found
            ↓
┌──────────────────────────────────────┐
│  NARRATIVE DICTIONARY  (this spec)   │
│  claim + mood + ROOM_KIND            │
│        ↓ vignettes as predicates     │
│        ↓ resolve over objects.jsonl  │
│  dressing plan: defName+state+place  │
└──────────────────────────────────────┘
            ↓
  rimplace flat plan → verify           ← exists. Lua → BuildPlan IR → flat text
            ↓
  GenStep_RimplacePlan  /  KCSG         ← exists. Replays at real mapgen time,
                                           per-item error isolation
```

Existing vocabulary the dictionary keys into rather than re-inventing `VERIFIED`
(`tools/picker/plan.py`, 2026-09-15):

- `ROOM_KINDS`: entry, hall, service, territory, chokepoint, cache, vault,
  deadend_payoff, hub, flooded, control
- `GATES`: open, minable, keyed, oneway, powered, knowledge

## 4. The axes — `SOURCED`

Sources fetched 2026-09-14/15 into
`GameDesignContent/sources/object_semantics/` (668 KB, 40 files, `FETCH.log` records
each). File numbers below cite that folder.

| Axis | Vocabulary | Source |
|---|---|---|
| **Connotation** | free tags, controlled list, grown | ⚠️ no established structure — see 4a |
| **Spatial function** | Paths · Edges · Districts · Nodes · Landmarks | Lynch, *Image of the City* (001) |
| **Communicative act** | Prohibition · Mandatory · Warning · Safe-condition · Fire-safety; severity Danger→Warning→Caution→Notice | ISO 7010 (009), safety sign (011) |
| **Message depth** | Rudimentary → Cautionary → Basic → Complex | Sandia 1993 (010) |
| **State / time** | *in situ · disturbance · killed object · midden · assemblage · fill*; patina: *acquired vs applied · verdigris · distressing · repatination* | archaeology (014), patina (015) |
| **Legibility / salience** | measured footprint, contrast, silhouette; *perceivable / hidden / false* | Gaver, Norman (005, 006) |
| **Stewardship** | is anyone maintaining this | broken windows (024) |
| **Abundance** | how resourced this place is | owner's ruling, §4c |
| **Emergent use** | designed-for vs worn-in by behaviour | desire paths (023) |

### 4a. Connotation has no principled structure, and that is the finding — `SOURCED`

The sources say there is no orthogonal dimensional system to be had, so the axis is
labelled ad hoc rather than dressed up. Colour symbolism inverts across cultures —
red is luck in China and Denmark, danger in Chad and Nigeria; green is safety almost
everywhere and *danger* in Malaysia (038). *Genius loci* is treated
phenomenologically as a holistic unity explicitly resistant to decomposition into
independent factors (020). Material culture grounds connotation in social use and
relationship rather than intrinsic property (012).

⇒ **Mood-filtering must be fuzzy over this axis, never an equality match**, and one
importable register does exist: wabi-sabi's named traits — asymmetry, roughness,
simplicity, economy, austerity, modesty, intimacy (039).

### 4b. Two axes the literature added that the concept lacked — `SOURCED`

- **Stewardship** is read fast and pre-verbally and is *orthogonal* to style: an
  unrepaired thing signals "no one is watching" regardless of what it otherwise
  connotes (024). A tended shrine and a neglected shrine make opposite claims from
  identical props.
- **Emergent use** separates *someone was here once* from *someone is here
  habitually*; a desire path forms after as few as ~15 passages (023). No single
  object can make that claim — only a worn track can.

### 4c. Stewardship and abundance are independent — owner's ruling — `CONCEPT`

Broken-windows critics show "disorder" is judged differently depending on who is held
responsible (024). Mapping "squalid" onto a scavenger clan and "orderly" onto an
Empire would import a real-world prejudice structure into a dictionary that then
generates at scale.

The owner ruled the two axes independent: **poverty never implies neglect.** Jawa
spaces read as intensely maintained but materially poor — nothing wasted, everything
repaired, salvage sorted. Imperial ruins read as resourced and abandoned. This makes
the clan's competence visible instead of its poverty.

### 4d. Affordance vs signifier — `SOURCED`

Gibson's affordance is what the environment permits; Norman's signifier is what
communicates it — *"Affordances determine what actions are possible. Signifiers
communicate where the action should take place"* (005, 006). Spatial function is the
affordance side; communicative act is the signifier side. Gaver's taxonomy adds that
a signal can be **false** (looks constraining, isn't) or **hidden** (real, unnoticed)
— both waste the placement budget, and a false one is worse than nothing.

## 5. Vignettes — the unit of meaning

Meaning is not a property of an object. A potted plant in a barracks and in a throne
room make different claims; a flat per-object attribute table implicitly denies this
and yields tonally flat output. The S01 rows show the real unit is a small
composition: *"straps cut rather than unbuckled"* is object+state; *"the sled left
where it fell"* is object+placement.

```
VIGNETTE  "interrupted departure"
  claim       they meant to leave and did not
  fits        entry, service, territory          (ROOM_KINDS)
  premise-compatible  any                        (§6)

  ingredients — predicates over the axes, never role names:
    A  function=CONTAINER ∧ footprint ≥ 2×2 ∧ openable
       state=open, contents disturbed
       traceability=HIGH        (an open container encodes being opened)
    B  portable ∧ value=high ∧ count 3–6
       placement=strewn along vector(A → nearest EXIT)
       traceability=MED         (position encodes direction of flight)
    C  function=DOOR ∧ state ∈ {open, breached}

  registers    state + placement          → satisfies §5b
  legibility   ≥ MED required on A
```

### 5a. Traceability is a required field — owner's ruling — `CONCEPT`

Owner, 2026-09-15: *"This should protect against 'I put a bunch of stone blocks on the
floor because that represents the broken doorway' (no it doesn't, there's no
traceability between the deconstructed door blocks and the violence of its death in
the image)."*

**An observable must encode its own cause, readable without knowing the author's
intent.** Stone blocks do not encode violence. A scorch mark encodes heat. A cut
strap encodes a blade and haste. Every ingredient carries a traceability grade, and a
claim may not rest solely on low-traceability ingredients.

🔑 **This is the deep reason the event-trace props library matters**
(`EVENT_TRACE_PROPS_LIBRARY_1`): blaster scars, scrapes and drag trails are precisely
the class of object that cannot be misread about its cause. Their absence (§6a) is a
hole in the *causal* half of the vocabulary, not a cosmetic one.

### 5b. Redundancy across registers, not repetition — `SOURCED`

Sandia insists a message ride categorically different channels at once — architecture
that reads as wrong pre-linguistically, pictograms, layered text in concentric rings —
because no single channel is trusted to survive language loss or institutional
collapse (010). Warning-placement research found a label weakest as pure information
and strongest when it also *physically obstructed* the wrong action (011).

⇒ **A claim must be carried by ≥ 2 signals in different registers** (e.g. a state cue
*and* a placement cue), never two instances of one register. Checkable in `query.py`.

Sandia also supplies ready-made archetypes for "this place should feel wrong before
anything is read": Landscape of Thorns, Spike Field, Menacing Earthworks, Black Hole,
Rubble Landscape, Forbidding Blocks (010).

## 6. The generation algorithm comes from the streamer study — `VERIFIED`

`research/RimMandrake/samuel_streamer_study/02_TECHNIQUE_ANALYSIS.md` Part 2, studied
from a human world-builder, independently states the algorithm the owner chose as
"mood as a filter":

> **Trick 1: One-sentence premise, then subtract everything that contradicts it.**
> **Trick 2: Constraint as narrative engine.**

⇒ Dressing is **premise-then-subtract**, not accumulate: establish one legible
premise for the room, then *remove* every candidate that contradicts it. This is also
the antidote to the clutter failure (§8).

### 6a. What we actually have to dress with — `VERIFIED`

Measured on this repo, macOS laptop, 2026-09-15, by parsing every `Defs/**.xml`
(848 files, 0 unparseable; 5,249 top-level def nodes; 1,553 ThingDefs, 1,443 with
defNames; 4,307 PNGs across 88 mods with a `Textures/` dir):

| Category | Count |
|---|---|
| TerrainDef (floors, ground coloration) | **101** |
| Filth / marks | **11** — mostly slime, ink, ash |
| Motes / effects | 10 — nearly all weapon beams |
| Rubble / wreck / debris | **4** |
| Art / decor buildings | **1** |

🔴 **We have essentially no "signs of something happening"** — not one blaster scar,
scorch mark, scrape, drag trail or impact spall. The owner proposed the event-trace
props library before this was counted; the count confirms it is the largest hole in
the object universe for narrative purposes. Terrain is our one real strength, which
suits the owner's stated interest in ground coloration.

## 7. The pilot and its test — `ANALYSIS`

Designed so it can fail. A single nicely-dressed room proves nothing; a room can look
good and carry no claim.

**One room plan, two claim sets differing only in stewardship:**

- **A** — *poor but tended*: someone lives here, has little, repairs everything.
- **B** — *rich but abandoned*: this was resourced, nobody has been here in a long time.

Same footprint, same room kind, same object budget. Four dressings: A-dictionary,
A-control, B-dictionary, B-control, where **control = random within the correct job
category** — i.e. what `structure_procedural_spec.md` does today.

Each is composited to an image with PIL at play zoom, order shuffled, condition
hidden, **filenames and defNames withheld from the reviewer** (otherwise the blinding
is theatre). The reviewer is naive — no brief — and is asked the general question the
owner specified:

> *"Describe this room."* and *"What does it appear happened here in the past to
> explain this room?"*

Scored on intended claims recovered and false claims invented.

**Pre-registered bar, written before the first dressing:** the dictionary must recover
**≥ 2×** the control's claims with **no more** false claims. A failure means the
dictionary is decoration, and that is a real possible outcome.

### 7a. Two proxy layers, and how the proxy gets validated — `ANALYSIS`

1. A **PIL composite is not the game renderer** — no lighting, terrain blending or fog.
2. A **model reader is not a human player** — it may reason its way to answers a player
   would never see, inflating the score.

⇒ **Validate the proxy once.** One pair of dressings built in the real game on the
owner's machine, screenshotted, read by him. If his read agrees with the offline
verdict, the proxy is trusted for iteration. If not, the offline loop is measuring
something else and we learn that at batch 1. Owner's sequencing: the naive-reviewer
gate comes first — *"If it passes that, THEN it's worth showing the human for
refinement."*

### 7b. Metric-driven iteration, and its two regimes — owner's ruling — `CONCEPT`

The owner raised iterative local-model optimisation against the score as an
experiment, and ruled on how much caution it deserves. Verbatim: *"YES, eventually,
it becomes a micro-increment metric optimizer. But at first that metric gets rid of a
sea of junk and provides excellent goal-based guidance to get you most of the way.
It's in the fine scale adjustment that you can't just rely on single metric
optimization to bring you all the way home, especially when there are many decisions
all weakly affecting the gradient. We'll deal with that when we get there… and that's
normal and acceptable."*

| regime | what the metric does | posture |
|---|---|---|
| **Coarse** | culls a sea of junk; strong goal-based guidance; gets most of the way | optimise freely — this is the regime the loop is built for |
| **Refinement noise** | many decisions each weakly affecting the gradient; metric increase decouples from real improvement | bring in a held-out reviewer and the owner's eyes |

⇒ **Build the loop and run it.** The refinement-noise regime is an expected later
stage, not a precondition, and the transition is **detected rather than assumed** —
his criterion: watch for *measurable positive influence* diverging from *metric
increase*. Something to notice together, not a reason for up-front ceremony.

(Unchanged and unrelated: never fabricate a verifier's output, never edit a grader to
pass. Those are honesty rules, not calibration.)

## 8. Guard rails from the sources — `SOURCED`

| Caution | Rail |
|---|---|
| Overwarning and clutter dilute signal; signage clustering exists to prevent overload (002, 011) | A density **ceiling per claim**. Note `structure_procedural_spec.md` sets a clutter *floor* — both are needed. |
| Decorated ≠ lived-in (032, 039). Lived-in is asymmetry, accumulated imperfection, wear following use; decorated is symmetry, matched sets, pristine curation | Independently confirms the owner's own R3 (furniture must break grid regularity by wall-hugging and jitter), reached by rejecting 21 templates. |
| Symbols do not transfer across cultures (038) | Jawa and Imperial conventions must be taught in-fiction, redundantly, on first appearance — never borrowed and assumed legible. |
| False and hidden affordances waste the budget (005) | Legibility is checked on every claim-bearing placement, not only on landmarks. |

## 9. Relationship to `beautiful_tilemap.md` — `ANALYSIS`

That spec is `[v2]` concept, terrain-and-beauty focused; this one targets v1 and is
things-and-claims focused. They are complementary and **its ruling is not reopened
here.** Two of its structures are adopted directly because they are right:

- **Hard gates first, veto on failure; score only what survives.** No weighted sum
  where narrative buys off unplayability.
- **Smallest useful first version proves measurability before anything is generated.**
  Its §10 stops the project if the metric cannot separate populations; §7 here is the
  same discipline applied to claims instead of beauty.

### 9a. Correction: its corpus is not reachable from this machine — `VERIFIED`

`beautiful_tilemap.md` §2a marks as `VERIFIED` a 44-map hand-authored `.rws` corpus at
`research/RimMandrake/hand_authored_maps/`, decoded 44 of 44. **On this macOS laptop
that corpus holds 0 `.rws` files** — the path is gitignored (`.gitignore:57`, "~470MB")
and only `README.md` stubs are present. The measurement was taken on the owner's
Windows box and remains true there. It is simply not an asset the offline pilot can
use.

## 10. What this component does not do — `ANALYSIS`

- **It does not place tiles.** It emits a dressing plan; `rimplace` owns placement and
  `GenStep_RimplacePlan` owns replay.
- **It does not score rooms.** `synthesis/DUNGEON_RUBRIC.md`'s "Storytelling through
  space" (15 pts: *"the place narrates with objects and damage, no text needed"*) and
  the `rimworld-scene-composition` skill's five metrics already grade. This produces
  evidence *for* them.
- **It does not serve room-quality mechanics.** RimWorld's Beauty/Wealth/Comfort and
  room roles are a different goal from carrying a claim; conflating them would make
  the schema serve two masters.

## 11. Deliverables of the pilot

| Artifact | Contents |
|---|---|
| `objects.jsonl` | ~30 rows, per-field provenance (`VISION`/`DEF_TEXT`/`MEASURED`/`OWNER`) |
| `vignettes/` | ~8 compositions, predicates + traceability grades + register check |
| `query.py` | claim + mood + ROOM_KIND → ranked dressing plan, seeded |
| `compose.py` | PIL composite at play zoom, defNames withheld |
| `evaluate.py` | blind naive-reviewer harness, bar quoted not moved |
| **`GAPS.md`** | every claim we could not evidence → scopes `EVENT_TRACE_PROPS_LIBRARY_1` |
| verdict | pass · fail · proxy-untrustworthy |

## 12. Open questions — for the owner, not assumed

1. Which room and biome does batch 1 dress? Terrain is our strength (101 TerrainDefs)
   and event traces are absent, which argues for a space where floors and wrecks carry
   most of the claim.
2. Who is the naive reviewer — a subagent on a fresh context, or a different model
   entirely? A different model is the stronger blind.
3. Does the dictionary ever run at mapgen time, or only at authoring time with
   defNames baked into a flat plan? (Authoring-time is assumed throughout §3.)
4. Four web topics came back **SILENT**, not thin — the first-batch searches for
   dungeon-map craft, environmental storytelling, Dark Souls and Valve's level-design
   language all returned unrelated results. A retry with known URLs landed 12/12
   (Don Carson's original article, Valve's `Leading the player`, the Three Clue Rule,
   Liz England's "The Door Problem") and is **not yet read into this spec.**
