# Explosive Knockback: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`). Code exists:
  `src/RimMandrake/ExplosiveKnockback/`.
- **Stage now:** Stage 1 being finished by hand (pilot row 2), 2026-11-14.
- **Bars:** 59 (30 inventory rows of `record.json` + 29 leaves of `tree.json`). The test-and-stage table is
  `version/test_table.json` (read view `version/test_table.md`).
- **Waiting on:** a builder for Stage 3 (the missing tests and the missing pieces), and two answers from him (below).
- **Open questions for him:** see "Questions" at the end of the history.

### The vision (his root paragraph, approved by card 2026-11-11, OWNER:1794468835221748501)

> Every blast in RimWorld now throws what it hits. A mortar shell beside a colonist hurls them three cells straight away
> from it, clean over sandbags, until a wall stops them hard; anything light goes too, so loose goods and corpses fly
> through the air, spinning and rebounding off walls, and no open shelf keeps them safe. When gas catches, it goes off
> clump by clump, each small burst scattering whatever lies near it, as the fire whooshes through the whole cloud. And
> where a blast meets a pit, its cover breaks and whoever it throws in falls.

The nine-line version vision (mass limit, blast power, shields, flagship, Mod Settings) is `version/vision.md`; it adds
his cards of 2026-11-13 and nothing inferred.

### His words on this mod (verbatim; full list with ledger ids in `sheet.md` "his words" and `record.json` decisions)

- 2026-10-06: "You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall."
- 2026-11-10: "1:1 totally. Even better if they can bounce inelastically off walls and rotate while they fly."
- 2026-11-11: "(1) but the closed containers may themselves get shoved a bit" · "2 and remember the gas in the Cauldron"
- 2026-11-12, the flagship: "Just put a bomb into a storeroom with people in it beside a pit. Shows some items falling
  into the pit and some people as well."
- 2026-11-12, 4:05 PM PST: "1: Anything that draws its contents is open. … 4: I am confused. Items should be blown off a
  shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly. No blockers."
- 2026-11-13: "We really shouldn't blow back creatures beyond a certain mass, and the heavier something is, the less it
  should fly. That should also be a function of the explosive damage itself as well." · "with a single scene we can
  check ALL these things together" · "Melee shove is a great idea, but it belongs in FlowWorks, not here."
- 2026-11-13, the lock: "Yes, fix it like that, and then please record this as an actual Pass." (OWNER:1794608649743135329)
- 2026-11-13, on the settings sweep: "can't we actually simulate that settings check offline? That seems a gratuitous use
  of the game, unless that's actually a very fast check?"

### Oddities (things a reader would otherwise get wrong)

1. **Three bar sets exist.** The 59 coverage checklist rows are the bars of 0.1.0. The 16 "north-star bars" (his card
   2026-11-12, "Approve as written") and the 30 "must be true" rows of
   `design/validation_walks/RimMandrake/ExplosiveKnockback.md` are older lists that `validation.py` still reads. They are
   not reconciled with the 59.
2. **The locked files moved after the lock.** `version/bars.md` pins blobs at `237b791167`; since then `scenes.json`
   (sc_spared, sc_mass_and_power, sc_settings_sweep), `record.json` (decisions) and `tree.json` (the owner-certify
   stamp only) changed. The scene edits are test text (creatures chosen by mass, never named; the g1 mass pin), not bar
   meaning. `tree.json` leaves are byte-identical in content to the lock. [measured 2026-11-14]
3. **Judge round count has three answers** (12 / 13 / 19); not reconciled (spec §10).
4. **97.2 million tokens** were charged to the Designer stage, 86.5 million of them estimates (`version/VERSION.json`).
5. **Proof build versus release build.** Most live scenes exist only in the proof build (`RM_KnockbackProof.cs`,
   `proof_build_gate.py`); the test queue cannot deploy a proof build today (RIMMANDRAKE_ROUTE_TESTQ_PROOF_BUILD_JOBS_TO_STEVE).
6. **The scene ids in `scenes.json` are not the scene names in the proof code.** `scenes.json` entry points name 35
   scenes by proof method; `RM_KnockbackProof.Names` holds 41 older names, and only some of the 35 are among them
   (measured in Stage 2 below).

## History (dated, added to only)

### 2026-11-14 11:14 PST, pilot begins (rm-builder, detached, offline only)

Brief from the Conductor: do pilot rows 1 to 3 by hand (journal, finish Stage 1, Stage 2), throwaway scripts only, stop
before Stage 3. Owner, 2026-11-14: "We need to get this going."

### 2026-11-14 11:21 PST, row 1 done: journal started

- **Cost:** about $1.9 of model spend (the harness budget line; tokens not separately measured), 7 minutes wall.
  Almost all of it reading: the spec, the version folder, `record.json`, `tree.json`, `scenes.json`, the verdict.
- **Boring enough to automate:** collecting "his words" (already in `sheet.md` and `record.json` decisions with ledger
  ids; a program can render them); the post-lock drift check (blob hash per pinned file against `bars.md`).
- **Needed judgment:** which oddities a cold reader would trip on; noticing that `scenes.json` and the proof code use two
  scene vocabularies.
