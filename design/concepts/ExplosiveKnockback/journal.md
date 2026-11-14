# Explosive Knockback: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`). Code exists:
  `src/RimMandrake/ExplosiveKnockback/`.
- **Stage now:** Stage 1 finished by hand 2026-11-14 11:27 PST (pilot row 2); Stage 2 next.
- **Bars:** 59 (30 inventory rows of `record.json` + 29 leaves of `tree.json`). The test-and-stage table is
  `version/test_table.json` (read view `version/test_table.md`).
- **Measured 2026-11-14:** 46 of 59 bars have at least one test that runs today (an offline test that ran, or an
  in-game scene whose entry exists in the proof code); 21 have every deciding test runnable; 33 have all their offline
  deciding tests green. 20 of the 35 `scenes.json` scenes have no entry in the proof code. 5 offline tests are specified,
  not built. Detail: `version/test_table.md`.
- **Waiting on:** Stage 2's verdict on the table, then a builder for Stage 3 ("reconcile").
- **Open questions:** see "Questions" at the end of the history.

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

### 2026-11-14 11:27 PST, row 2 done: Stage 1 finished (the test-and-stage table)

- **What was done.** Every one of the 59 bars now names its deciding tests and the stage that proves it
  (`version/test_table.json`, read view `version/test_table.md`), built by a throwaway script whose bar-to-test
  placement is hand judgment and whose "runs today" column is measured by running every offline test
  (`D:\ClaudeWork\rimmandrake\maturation_pilot_ek\make_test_table.py`, 62 s per run, 60 s of it the tests).
  No bar's text was edited.
- **Offline tests run today:** kernel 142/142, fuzz 42001 cases, def lint, lint planted-defect 20/20, storage census,
  validation STATIC and mock (41/41 scenes staged), proof-build gate, FlowWorks cover breaks: PASS. Two known reds touch
  this mod: `selftest_settings_screens.py` (EK has 7 setting groups, expected 6; `debugDrawVectors` in no group;
  RIMMANDRAKE_REGROUP_SETTINGS_SCREENS_FOUR_MODS_OUTGREW_AUDIT) and `selftest_proof_restore_check.py` (two
  unrestored-on-throw leaks in `RM_KnockbackProof.cs`; RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS).
- **The six judge corrections** (g1 to g6) were already in the test text (`scenes.json`, commits dea7804728 and
  39886c4919); the table re-checks each by text match. **g4 is reopened** by the post-lock commit 92fe261f36: the
  colonist band in `sc_mass_and_power` widened to 45-76 kg because live colonists weighed 48.75 and 60.75 kg, and under
  63.5 kg the kernel throws a colonist 6 cells at damage 100, tying the capped light animal. The scene's expect still
  says "light > colonist", the leaf's oracle still says "the colonist 5", and kernel check K-19 still tests 64-76 kg.
  Not edited: it is a question (below).
- **The 2 held look statements are placed** in the table (`held_statements`): "Anything that draws its contents is
  open" on the storage census test (offline, runs today, PASS); "a shelf should be ruled as open, period … staged
  misleadingly" on sc_open_storage and sc_closed_containers plus a Stage 2 staging check. They are **not** removed from
  `design/RimMandrake/validation_holding/`: its README says nothing leaves until the ladder is "fully defined and
  regenerated", and spec question 12 (does accepting this map count as that?) is open.
- **The settings sweep is moved offline in the table:** `settings_scale_and_switch` and `inv_settings` are decided by
  the specified offline test T_SETTINGS_SWEEP_OFFLINE (its acceptance is the already-filed
  RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING); `sc_settings_sweep` keeps only the game-side wiring
  lines. The leaf text and the scene text are unchanged; Stage 3 shrinks the scene.
- **Cost:** about $1.2 (harness budget line, $1.9 to $3.1), 6 minutes wall.
- **Boring enough to automate:** running every offline test and recording rc, time and last line; listing each
  `scenes.json` entry point and checking it against `RM_KnockbackProof.Names`; checking the judge corrections by text
  match; rendering the read view.
- **Needed judgment:** which tests decide a bar and which only support it; which part of a bar an offline test can
  decide and why the rest needs the game (`why_game` per scene, to be re-asked by the Stage 4 challenger); spotting the
  reopened g4; the old proof-scene names (20 kept as support) versus the locked scene ids.

### Questions (open)

1. **g4, the colonist in `sc_mass_and_power`** (for the Conductor; his if it touches the leaf). Real colonists weigh
   about 45-61 kg as the kernel weighs them; the leaf oracle's "colonist 5 at twice the damage" needs 64 kg or more.
   Smallest fix that keeps the bar's meaning: a proof hook stages a colonist of 64-76 kg (Stage 3, test code only).
   The other way, admitting a tie at the cap, changes the leaf's oracle and is his call.
2. **Held statements:** does this pilot's placement count as the ingest his 2026-11-12 ruling waits for (spec
   question 12)? Until then they stay in the holding store as well.
3. **`record.json` state fields are stale** (not bar meaning): `inv_creature_mass_limit` and `inv_blast_power_damage`
   say `impl: absent` though both were built in 40f4e85120 (K-18 to K-20 pass); `inv_big_corpse_spared` names skip
   reason `too_big`, which the mass rule replaced (its scope note says the 75 kg goods limit now spares it, so the
   journal line would read `too_heavy`). Stage 3 "reconcile" should correct these fields.
4. **Three bar lists** (the 59, the 16 north-star bars, the 30 walk rows) are unreconciled; `validation.py` still reads
   the walk. Which one does Stage 6 report against? The table answers "the 59".
