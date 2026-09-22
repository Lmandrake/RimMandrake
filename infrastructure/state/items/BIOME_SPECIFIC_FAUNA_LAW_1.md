# BIOME_SPECIFIC_FAUNA_LAW_1 — one animal, one biome, unless the game says otherwise

## the law

**Owner, 2026-09-21, verbatim:**

> *"Animals sound be biome-specific unless there is an in-game reason (e.g. flyers that
> migrate, young versions that grow in the miasma then migrigate to the sea later, etc.) So
> stonebacks hould have one home. We have plenty of creatures left to fill rosters if there
> are holes."*

Two halves, and the second is the one that gets forgotten: **a thin roster is filled with a
NEW creature, never by borrowing a neighbour's.** There is surplus cast.

## 🔴 The carve-out is NARROW — habitat is not a licence (owner, 2026-09-22)

BENCH read his stoneback placement ("any arid biome where it's needed — desert, extreme
desert, or other hot arid day-side") as meaning a shared **habitat class** is itself an
in-game reason, and put the card to him. He corrected it flatly:

> *"you are not understanding. I meant pick one arid home."*

⇒ **A list of biomes he names is the CANDIDATE set, not an assignment.** Being the same kind
of place — arid, nightside, sea — is **not** an in-game reason. The carve-out is only the
mechanism cases he actually gave: a **flier that migrates**, or a **life stage that moves**
(grows in one biome, leaves for another). Nothing else seen so far qualifies.

🔑 So the adjudication below is the STRICT one, and the 52 do not mostly resolve as
legitimate. Worked precedent, same day (`STONEBACK_DEFNAME_COLLISION_1`): two animals, each
given exactly one home — the bokka the Long Shade, the korrum the Scarlands — with the
other candidate biomes' admissions **withdrawn into `evictions`**, not kept as second homes.

⚠️ And the second half of the law binds here: each withdrawal leaves a hole, and a hole is
filled with a **new** creature. *"We have plenty of creatures left to fill rosters if there
are holes."*

## 🔑 The tie-break is ruled, and it forks on CANON (owner, 2026-09-22)

Decision taken by question card; the words below are his own, typed into the card:

> *"As a reminder, there are some animals we WANTED to be in multiple biomes: fliers that
> migrate from wetter regions into hot places to lay their eggs, young sea creatures dwelling
> in the miasma, etc. As long as you know this, and are asking about animals that don't have
> any such relationship, then I will answer your question in that context. If the beast is
> canon (1). If not, (2) and we regenerate the description to match. Likely should confirm
> with the user when you're moving animals in this way, to make sure nothing is getting
> messed up."*

Where (1) and (2) were the card's tie-break options. **Amended the same day by a second card
ruling — "Where it was created wins"** — after the first version was found to evict the sytheclaw
from the Pyrelands, the biome it was purpose-built for. The algorithm in final form:

1. **Exclude the deliberate carve-out set FIRST.** He named two mechanisms and widened one:
   a flier that **migrates from a wetter region into a hot one to lay eggs**, and **young sea
   creatures dwelling in the miasma** before moving on. A species in that set keeps its several
   homes and the reason gets RECORDED on its rosters — it is not a violation.
2. 🔑 **PROVENANCE FIRST — the biome a creature was authored or ported FOR keeps it**, whatever
   the roster sizes say, and its description is left alone. This outranks both branches below.
   Provenance is a fact on disk, not a taste call: the port item names the biome (e.g.
   `PYRELANDS_DONOR_PORT_4` — *"our own re-authors of the four Pyrelands creatures"* — which is
   what settles `RUT_Sytheclaw` for the Pyrelands over two thinner rosters).
   ⚠️ For a donor animal we never authored there is no provenance to find, so this step is
   **silent on 38 of the 55** and the branches below decide those.
3. **Canon beast → its own description decides its one home.** The description is evidence and
   is not to be rewritten to suit a placement.
4. **Non-canon beast → the thinner roster keeps it, and we REGENERATE the description** to
   match where it landed. This is the asymmetry that makes the rule cheap: canon constrains us,
   our own cast adapts. ⚠️ Roster "thinness" is only trustworthy where
   `DUPLICATE_CANON_DEFNAME_PAIRS_1` has not inflated the count — `RUT_AridShrubland` carries
   four double-cast animals.
5. ⛔ **Confirm the moves with him before applying them** — *"to make sure nothing is getting
   messed up."* A move list is served for confirmation; it is not applied on this ruling alone.
   Earned its keep immediately: of the eleven moves confirmed on 2026-09-22, **two were confirmed
   against a wrong home count** and had to be withdrawn and re-served.

### Rulings taken on the eleven owned species, 2026-09-22

| species | outcome | state |
|---|---|---|
| `RSW_Screecher` | flier migration **approved**, keeps Poison Forest + Wasteland | reason owed on both rosters |
| `RM_Titanoslime` | not a violation — the Slime twin, one home under two defNames | nothing to do |
| `RSW_Gizka` | 🔴 **WITHDRAWN** — confirmed on a 2-home picture; really in 4, and double-cast | blocked on `DUPLICATE_CANON_DEFNAME_PAIRS_1` |
| `RSW_Kreetle` | 🔴 **blocked for the same reason** — the animal kreetle is in 5 places under 2 defNames | blocked on `DUPLICATE_CANON_DEFNAME_PAIRS_1` |
| `RUT_Sytheclaw` | **Pyrelands** keeps it on provenance; evict from Greentide + Contagion; **fire text kept** | approved, ready |
| `RSW_Spineroller` (kudda) | **Extreme Desert**; description corrected — no eclipses, *"sustained shade kills a herd"* | description done at `1340f5977` |
| `JOE_Cephalope` | **Extreme Desert**; regenerate description | approved, ready |
| `RSW_TruffleMole` | **Extreme Desert**; regenerate description | approved, ready |
| `RSW_JewelBeetle` | **Webwork**; regenerate description (its "desert shallows" fits neither) | approved, ready |
| `RSW_Gembug` | **Lantern Deeps**; ⛔ must become a **hydrocarbon lifeform** to live there | approved, conversion owed |
| `RSW_GlowSlug` | **Lantern Deeps**; ⛔ same hydrocarbon conversion | approved, conversion owed |

🔑 The hydrocarbon requirement is his, verbatim: *"Gembug must become hydrocarbon lifeform if it
moves into lantern deeps. Glowbulb same."* That is a def change, not a prose change — check the
Deeps' established hydrocarbon design language (`DEEPS_FAUNA_REPOPULATION_1`) before writing it.

⚠️ **Library membership is not a canon test.** `design/RimStarWars/canon_references/` holds 137
entries *by design* (45 creatures), so a beast absent from it may still be canon — `Mynock`,
`Worrt`, `Gelagrub`, `Urusai`, `LongtailGorg`, `Woolamander` and `Gornt` are canon Star Wars
creatures with no entry. Deciding step 2 vs 3 from `ls` on that directory would misroute all
seven into "regenerate the description", destroying canon text. Establish canon per species.

## what it applies to — MEASURED 2026-09-22, and the count is 55

🔴 **The figure is 55, not 52.** Two earlier passes (2026-09-21, and a re-measure earlier on
2026-09-22 that wrongly reported "52 again") both used an instrument that could not read a
patched-in roster. Both wrong numbers are deleted rather than kept beside this one; `git log` on
this file carries them. **The two instrument bugs, because either will recur:**

1. **A patched-in `<wildAnimals>` was attributed by hunting for a nearby `<xpath>` element.**
   That mis-assigns silently. It put `RUT_Sytheclaw` in `RM_Greentide` (whose roster is pure
   vanilla filler and does not contain it) and **missed `RM_Pyrelands` entirely** — the biome
   whose fire is the sytheclaw's whole description. Resolve a patch's target from the
   PatchOperation's **own** `xpath`, and read species from its `<value>`.
2. **The `RM_FloodedCanyon` / `RUT_CrackedLands` twin was not collapsed**, inflating the set with
   four species that have one home: `AA_SandSquid`, `CanCell`, `Gornt`, `Woolamander`.

🔑 **The RM_ twin mechanism is why this matters.** An `RM_` twin's BiomeDef carries only the
deliberate generic vanilla-Core body (`RM_Greentide` = Warg/Muffalo/Elephant/Cobra/Megaspider/
Rat/Hare); the campaign cast is added **on top by a patch** (`UtinniPatches/Patches/
WildAnimals_<Biome>.xml`, `MayRequire` the twin's mod). So reading BiomeDefs alone sees a twin's
generic half and none of its real roster. Twins collapsed here: Greentide, Pyrelands,
CrackedLands, Slime, FuelSnows(`RUT_Umbra`).

⇒ **55 genuine multi-homed species** after twin collapse and after excluding vanilla-Core filler
(`Rat`, `Warg`, `Muffalo`, `Elephant`, `Hare`, `Dromedary`, `Cougar`, `Fox_Fennec`, `Iguana`,
`Cobra`, `Megaspider`). Instrument: `/tmp/homes2.py` shape, documented above — rebuild it, do not
trust a scan.

**Species the broken instrument had never surfaced** — all of them patch-cast into an `RM_` twin,
so all of them were invisible: `RSW_Clodhopper`, `RSW_Dalgo`, `RSW_Falumpaset`, `RSW_Iriaz`,
`RSW_Nuna`, `RSW_ShiroTrap`, `RSW_Worrt`, `RSW_Zeer`. And two counts were badly understated:
`RSW_Gizka` is in **4** places (Greentide, Pyrelands, Desert, Extreme Desert) and `RUT_Sytheclaw`
in **3** (Greentide, Pyrelands, Contagion).

`RSW_Stoneback` has correctly **left** the set (reduced to one home at `4b068ea5d`).
`RM_Titanoslime` has left it too — `RM_GelatinousSlime` + `RUT_Slime` is the Slime twin, one home.

## The root cause of the multi-homing

🔑 **Root cause — nobody was careless.** `design/Jawa/fauna/cast_assignment.csv` carries one row
per (biome, species); **73** species hold rows in more than one biome, and **60 of those 73 carry
a DIFFERENT habitat token per row** (`the_miasma` / `poison_forest` / `the_slime`), each with its
own stated reason. So the casting pass ran biome-by-biome and no pass could see an animal already
admitted elsewhere. Only 9 rows show a combined token (`dune_sea + deep_desert`, the cephalope's
shape). ⇒ This is a constraint the CSV was never built to satisfy, not a batch of mistakes — and
the fix belongs partly upstream in how a casting pass is run.

🔴 **The columns that would settle it are empty.** That CSV has `belong` and `standout` columns —
per-biome fit scores, exactly the mechanical tie-break — and they are **blank in all 419 rows**
(`promoted` is `0` in all 419 too). There is no recorded basis for ranking a species' fit between
two biomes, which is why the tie-break had to be ruled rather than computed.

⚠️ **The flier carve-out is UNMEASURABLE on the Mac laptop.** **38 of the 55** are donor-owned
defs (`AA_*`, `VFEI2_*`, `GR_*`, `JOE_*`, `SW_*`, and bare Star Wars names) whose ThingDefs are
not under `src/`, so `MaxFlightTime` cannot be read here and flight cannot be confirmed the one
correct way (CLAUDE.md: the switch is the stat, never a `canFly` field). Of the **17** whose defs
we hold, exactly one flies: **`RSW_Screecher`, `MaxFlightTime=35.0`** (`RUT_PoisonForest` +
`RUT_Wasteland`) — carve-out approved by the owner 2026-09-22, pending only the migration reason
being written onto both rosters. Settling the other 37 needs the Desktop.

## 🔴 This is an adjudication, not a sweep

The carve-out is real and several of these are **already** the cases it protects:

- **Fliers** — `Convor`, `Whisperbird`, `Mynock`, probably `AA_Aerofleet`. A migrating flier over
  four biomes is exactly his example of a legitimate reason. ⚠️ Check flight the right way: the
  switch is the `MaxFlightTime` **stat**, not a `canFly` field (CLAUDE.md).
- **Life-stage movement** — the Miasma's `RSW_*Juv` nursery entries are literally his second
  example ("young versions that grow in the miasma then migrate to the sea later"). Any
  juvenile/adult split across biomes is presumptively fine and may be the *intended* design.
- **Contiguous-desert pairs — NOT exempt after the 2026-09-22 correction.** Six species sit in `RUT_Desert` + `RUT_ExtremeDesert`
  (`RSW_Gizka`, `RSW_Kreetle`, `RSW_Spineroller`, `RSW_Stoneback`, `RSW_TruffleMole`,
  `JOE_Cephalope`). Those two are becoming **separate mods** (`RM_LongShade`, `RM_Stillsand`),
  so "it's all desert" was never an answer and is now explicitly not one — `RSW_Stoneback` was one of these six and has been reduced to a single home.
- **Twin pairs** — `RM_Titanoslime` in `RM_GelatinousSlime` + `RUT_Slime` is the twin, i.e. ONE
  biome in two defs. Same artifact class as `RUT_Umbra`; resolve with the twin, not here.

⛔ So: no bulk un-wiring. A species removed from a roster to satisfy this law leaves a hole,
and the law's own second half says that hole is filled with a **new** creature — which is
authoring work, not a deletion.

## spec

1. **Bucket the 52 first, cheaply**: flier / juvenile-line / twin-or-alias artifact / desert-pair
   / genuinely duplicated. Only the last bucket needs a real call. Publish the buckets before
   changing anything.
2. For each genuinely duplicated species, **pick its one home** on the sheets' evidence (which
   biome's law actually calls for it), and record the choice in the losing roster's `evictions`
   with the reason.
3. **Count the holes** each eviction opens, per biome, and file the fill as its own work — new
   creatures, per his second half. Do not leave a roster thinner than it was without saying so.
4. Re-check `ECOSYSTEM_PYRAMID_LAW_1` per touched biome afterwards: removing a small animal can
   invert a pyramid that was passing.

## verify

Every species wired in more than one of our BiomeDefs either has a stated in-game reason
recorded on its rosters (flier/migration/life-stage) or has been reduced to one home with an
eviction record naming the losing biome. No biome newly fails the pyramid law. No roster is
left with an unfiled hole.

## criteria

A player who learns an animal in one biome has learned something about that biome — not a
planet-wide filler list.

## Watch out

- ⛔ **Do not "fix" a species that is cut in one biome's review sheet and alive in another** —
  a sheet's cut is scoped to its own biome (owner, 2026-09-21). That is a different rule and it
  does NOT make the survivor a multi-homing violation.
- ⚠️ The count is 52, not 58 and not the 182 a naive donor-name scan reports. If a future pass
  gets a different number, reconcile before acting: the aliases and the generic `RM_` bodies are
  the two things that move it.
