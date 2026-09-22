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

Where (1) and (2) were the card's tie-break options. So the algorithm is:

1. **Exclude the deliberate carve-out set FIRST.** He named two mechanisms and widened one:
   a flier that **migrates from a wetter region into a hot one to lay eggs**, and **young sea
   creatures dwelling in the miasma** before moving on. A species in that set keeps its several
   homes and the reason gets RECORDED on its rosters — it is not a violation.
2. **Canon beast → its own description decides its one home.** The description is evidence and
   is not to be rewritten to suit a placement.
3. **Non-canon beast → the thinner roster keeps it, and we REGENERATE the description** to
   match where it landed. This is the asymmetry that makes the rule cheap: canon constrains us,
   our own cast adapts.
4. ⛔ **Confirm the moves with him before applying them** — *"to make sure nothing is getting
   messed up."* A move list is served for confirmation; it is not applied on this ruling alone.

⚠️ **Library membership is not a canon test.** `design/RimStarWars/canon_references/` holds 137
entries *by design* (45 creatures), so a beast absent from it may still be canon — `Mynock`,
`Worrt`, `Gelagrub`, `Urusai`, `LongtailGorg`, `Woolamander` and `Gornt` are canon Star Wars
creatures with no entry. Deciding step 2 vs 3 from `ls` on that directory would misroute all
seven into "regenerate the description", destroying canon text. Establish canon per species.

## what it applies to — MEASURED 2026-09-21

Parsed every `<wildAnimals>` block under `src/` (`ElementTree`, not grep). **299** species are
wired into one of our BiomeDefs. **58** appear in more than one — but two of those are
measurement artifacts and must not be counted:

- `RUT_Umbra` is a **compat duplicate** of `RUT_FuelSnows` (same biome, two defNames pending
  the terminal repaint), so a species in both has ONE home, not two. Aliased before counting.
- The `RM_` twins (`RM_FloodedCanyon`, `RM_Pyrelands`, `RM_Greentide`) carry a **deliberate
  generic vanilla-Core body** so a non-campaign RimWorld game gets ordinary wildlife — that is
  the pattern `FLOODEDCANYON_RM_MOD_BUILD_1` established. `Rat`/`Warg`/`Muffalo`/`Elephant`/
  `Hare`/`Dromedary` living in several of them is correct and out of scope. **6 excluded.**

⇒ **52 genuine multi-homed species.** Distribution: 1 in five biomes, 2 in four, 10 in three,
39 in two.

| homes | species |
|---|---|
| 5 | `AA_Helixien` (Contagion, Miasma, PoisonForest, Scarlands, Slime) |
| 4 | `Convor`, `Whisperbird` |
| 3 | `AA_Aerofleet`, `AA_BloodShrimp`, `AA_DecayDrake`, `AA_Slurrypede`, `AA_Terramorph`, `AA_Wildpod`, `Eopie`, `Kreetle`, `Nuna`, `VFEI2_Swarmling` |
| 2 | `AA_Eyeling`, `AA_InfectedAerofleet`, `AA_Murkling`, `AA_Needlepost`, `AA_OcularJelly`, `AA_Plasmorph`, `AA_RedGoo`, `AA_Swarmling`, `AA_Wildpawn`, `Anooba`, `Bantha`, `Beldon`, `Fambaa`, `Fox_Fennec`, `GR_Beetlefleet`, `Gelagrub`, `Gizka`, `Grank`, `Iguana`, `JOE_Cephalope`, `LongtailGorg`, `Mynock`, `RM_Titanoslime`, `RSW_Gembug`, `RSW_Gizka`, `RSW_GlowSlug`, `RSW_JewelBeetle`, `RSW_Kreetle`, `RSW_Screecher`, `RSW_Spineroller`, `RSW_Stoneback`, `RSW_TruffleMole`, `RUT_Sytheclaw`, `SW_Electrictick`, `Shiro`, `Urusai`, `VFEI2_BlackSwarmling`, `Worrt` |

## RE-MEASURED 2026-09-22 — same total, different membership, and the root cause

Re-parsed independently (`ElementTree` over all 1500 XML files under `src/`, both `<wildAnimals>`
on a BiomeDef and patched-in tables, aliases collapsed). **52 again** — but the agreement is
partly coincidence and the reconciliation the `Watch out` note demands is this:

- `RSW_Stoneback` has correctly **left** the set (reduced to one home at `4b068ea5d`).
- The generic `RM_` twin exclusion is **9, not 6** — `Cougar`, `Fox_Fennec` and `Iguana` are also
  vanilla-Core filler in the twins' deliberate generic bodies, on the same reasoning as the
  original six.
- Newly visible: `AA_SandSquid`, `CanCell`, `Gornt`, `Woolamander`.

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

⚠️ **The flier carve-out is UNMEASURABLE on the Mac laptop.** 41 of the 52 are donor-owned defs
(`AA_*`, `VFEI2_*`, `GR_*`, `JOE_*`, and bare Star Wars names) whose ThingDefs are not under
`src/`, so `MaxFlightTime` cannot be read here and flight cannot be confirmed the one correct way
(CLAUDE.md: the switch is the stat, never a `canFly` field). Of the 11 whose defs we do hold,
exactly one flies: **`RSW_Screecher`, `MaxFlightTime=35.0`** (`RUT_PoisonForest` + `RUT_Wasteland`)
— carve-out applies, pending only the migration reason being written onto its rosters. Settling
the other 40 needs the Desktop.

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
