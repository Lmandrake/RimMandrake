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
