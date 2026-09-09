# DROID_RETIRE_ABF_SYNCORE_1 — retire ABF + SynCore (wave R2)

## Spec (written by FOUNDRY, thin item — no spec/verify/criteria existed)
Retire ABF (`Killathon.ArtificialBeings`, "ABF: Artificial Beings Framework",
workshop `3284097810`) and SynCore (`Killathon.ArtificialBeings.SynCore`,
"ABF: Synstructs Core", workshop `3288463094`) — stop loading both donor
mods; confirm `DroidDonor_ABFGate` fires (its 9 `<nomatch>`-gated Removes,
dormant while ABF is active); remove `DroidsAreMachines.xml`'s ABF half.
Cold-load verification explicitly owed to a future batched restart, not this
pass.

## What's confirmed safe
- **packageIds confirmed from live workshop About.xml, not guessed**: ABF
  core = `Killathon.ArtificialBeings` (3284097810); SynCore =
  `Killathon.ArtificialBeings.SynCore` (3288463094, `modDependencies` on ABF
  core — SynCore cannot outlive ABF, matching `DroidDonor_ABFGate.xml`'s own
  header). Both confirmed **ACTIVE** in the live `ModsConfig.xml` (594 mods
  today) via direct grep.
- **`DroidDonor_ABFGate`** (`src/RimStarWars/StarWarsPatches/Patches/DroidDonor_ABFGate.xml`,
  built under `DROID_DONOR_PATCH_GATE_1`) covers sites 2–10 of that item's
  11-site catalog: 9 `PatchOperationFindMod` ops gated on ABF's **absence**
  (`<nomatch>`), dormant today, designed to fire automatically the moment
  ABF leaves `ModsConfig.xml`. Confirmed unchanged, still present, still the
  right mechanism for those 9 sites. **This part needs no new work.**
- **Whole-active-mod-list sweep for ABF/SynCore dependents** (per this
  item's own instruction, not trusting the stated scope —
  `WEAPONS_DONOR_RETIREMENT_1`'s incident is exactly why): grepped
  case-insensitive `artificialbeings` across the full Steam workshop content
  tree (1268 subscribed mod folders, not just the 594 active) plus the
  deployed `RimWorld/Mods` and `RimWorld/Data` copies. 7 distinct workshop
  mods hit: kotorcore (3254370945), kotorweapons (2938932438, already
  inactive), kotordroids (3047371944), ABF itself, SynCore itself,
  `FrozenSnowFox.ComplexJobs` (active, `frozensnowfox.complexjobs`) and
  `guy762.StarWarsXenotypes` (not active, irrelevant). ComplexJobs' ~dozens
  of references are **all `MayRequire="Killathon.ArtificialBeings"`-guarded**
  — safe, self-silencing once ABF is gone. Our own `mandrake.rut.pawnflavor`
  (`PawnFlavorPhase2_MentalBreak.xml`) also references SynCore-owned
  `ABF_MentalBreak_Synstruct_*`/`ABF_MentalState_Synstruct_*` defs, but
  every operation is wrapped in `PatchOperationFindMod` gated on "ABF:
  Synstructs Core" being present — also safe. **No new unguarded dependent
  found anywhere outside the already-catalogued kotorcore/kotordroids
  cluster.**
- **`DroidsAreMachines.xml`'s ABF half identified**
  (`src/RimUtinni/Doctrine/Patches/DroidsAreMachines.xml`): two
  `PatchOperationFindMod` blocks — one gated on `Asimov` (Outer Rim droids,
  untouched by this item), one gated on `ABF: Synstructs Core` targeting
  `FleshTypeDef[defName="ABF_FleshType_Synstruct_Base"]` (the KotOR droids'
  flesh type, sets `isOrganic:false` for ion/EMP to work on them). This
  second operation is the "ABF half." It is itself already
  `PatchOperationFindMod`-guarded, so it would just silently stop firing if
  SynCore retired — not itself an error risk — but removing it cleanly
  (rather than leaving permanently-dead code) is the stated scope of this
  item once retirement is actually safe.

## 🔴 STOPPED — confirmed live dependent outside a safe retirement window, do not touch ModsConfig

**`retirement_order.py`'s own `DROID_RETIREMENT_ORDER_ASSERT_1` constraint
fires the moment ABF/SynCore are removed from the live mod list.** This is
not a new finding — it is `DROID_DONOR_PATCH_GATE_1`'s own **Site 1**,
deliberately left unpatched (see `DroidDonor_ABFGate.xml`'s header, "NOT
included: Site 1 ... that one is a live mechanic plus an inheritance-chain
dependency that needs the Droidworks `Need_Power` replacement ... ported
onto guy762.KotORDroids first; that port hasn't happened yet") — re-verified
fresh, tonight, not trusted from the old doc:

- `guy762.mm.kotorcore`'s `_DroidsBase` folder (loaded only while
  `guy762.KotORDroids` is active) defines the abstract
  `AlienRace.ThingDef_AlienRace Name="guy762_KotORDroidBase"
  ParentName="ABF_Thing_Synstruct_HumanlikeBase"` — an abstract def **owned
  by ABF core**, not by any donor mod.
- All 12 of `guy762.kotordroids`' 1.6 race `ThingDef`s inherit
  `ParentName="guy762_KotORDroidBase"`.
- `guy762.mm.kotorcore` and `guy762.kotordroids` are **both confirmed
  ACTIVE** in tonight's live `ModsConfig.xml`.
- No `PatchOperationFindMod`/`MayRequire` can gate an inheritance
  (`ParentName`) resolution — only removing the dependent mod no later than
  what it requires prevents it. If ABF retires while kotorcore+kotordroids
  stay active, `ABF_Thing_Synstruct_HumanlikeBase` stops existing,
  `guy762_KotORDroidBase` silently fails to resolve, and (per the
  `WEAPONS_DONOR_RETIREMENT_1` 2026-08-31 incident's proven failure shape)
  the WHOLE parent def and all 12 downstream race `ThingDef`s are discarded
  — **no Config error, no log line**, exactly the "stuck at an error debug
  console" class of break that incident produced.
- Ran the actual instrument, not just read the doc: `retirement_order.
  check_order()` against the live `ModsConfig.xml` reports **no violations
  today** (ABF/SynCore still active, so the `requires_active_all` side is
  satisfied); simulating the live active set with
  `killathon.artificialbeings` + `killathon.artificialbeings.syncore`
  removed reproduces the violation cleanly:
  ```
  VIOLATION kotordroids_needs_abf_while_kotorcore_active:
    ['guy762.kotordroids', 'guy762.mm.kotorcore'] active with
    ['killathon.artificialbeings', 'killathon.artificialbeings.syncore'] absent
  ```
- **Corroborating, independent evidence this is not theoretical**: the
  sibling item `DROID_RETIRE_KOTORDROIDS_1` (wave R1, retiring
  `guy762.kotordroids` alone) attempted exactly this cluster on 2026-09-08,
  found 4 NEW `Could not resolve cross-reference` errors on a real cold
  load (a *different* two-hop chain through the same `_DroidsBase` folder),
  and was **reverted** — left `doing`, blocked, unclosed. This whole
  kotorcore/kotordroids/ABF/SynCore neighborhood has already broken a live
  cold load once from an angle nobody had catalogued in advance; Site 1's
  inheritance chain is the *known* remaining trap in the same neighborhood.

**Per this item's own instruction #7: do not remove ABF or SynCore from
`ModsConfig.xml`.** No `<li>` was touched, no backup was needed (nothing was
about to be written), `DroidsAreMachines.xml` was left untouched (its ABF
half is dead-once-retired but not itself unsafe to leave in place).

## What actually needs to happen before this item can proceed
Exactly what `DROID_DONOR_PATCH_GATE_1` and `DROID_SYSTEM_BUILD_1` already
say: either (a) the Droidworks `Need_Power` port lands on
`guy762.KotORDroids`'s race tree and `guy762_KotORDroidBase`'s `ParentName`
is reclassed off `ABF_Thing_Synstruct_HumanlikeBase` onto a Droidworks base
(`DROID_SYSTEM_BUILD_1`'s open "port manifest ... waves 1-3" criterion,
still `[ ]`), or (b) `guy762.kotordroids` itself retires first (blocked, see
`DROID_RETIRE_KOTORDROIDS_1`'s own unresolved 4-ammo-def finding). Either
one clears `retirement_order.py`'s constraint; until then, this item stays
blocked on the same upstream work those two items already name.

## Verify (once unblocked)
1. Re-run `python3 src/RimMandrake/Utils/retirement_order.py` against the
   live `ModsConfig.xml` — must report "no violations" *before* removing
   ABF/SynCore's `<li>` entries (i.e., the dependent side must already be
   clear, not just about to be made clear by the same edit).
2. Back up live `ModsConfig.xml` to `infrastructure/state/modlists/`, remove
   `<li>killathon.artificialbeings</li>` and
   `<li>killathon.artificialbeings.syncore</li>` by exact-tag match, re-grep
   to confirm both absent.
3. Remove `DroidsAreMachines.xml`'s ABF-gated `Operation` (the
   `ABF_FleshType_Synstruct_Base` block), leaving the `Asimov` operation
   untouched.
4. Cold-load-verify (batched restart, not a dedicated one) against
   `infrastructure/state/facts/config_error_baseline_2026-09-06.json`
   (or its current successor): zero NEW `Config error in` /
   `Could not resolve cross-reference` lines; confirm
   `DroidDonor_ABFGate`'s 9 sites fired (their `<nomatch>` Removes actually
   ran) and no `guy762_KotORDroidBase`-rooted def vanished.

## Criteria
- [x] Real packageIds for ABF/SynCore confirmed from live workshop About.xml
      (not guessed).
- [x] `DroidDonor_ABFGate` located and confirmed as the correct, already-built
      mechanism for sites 2–10; needs no new work.
- [x] `DroidsAreMachines`'s ABF half identified precisely (the `ABF:
      Synstructs Core`-gated `FleshTypeDef` operation).
- [x] Whole active (594-mod) list swept for ABF/SynCore dependents beyond
      this item's stated scope — one new mod found (`FrozenSnowFox.
      ComplexJobs`), confirmed safe (`MayRequire`-guarded throughout).
- [ ] **BLOCKED**: `retirement_order.py`'s `DROID_RETIREMENT_ORDER_ASSERT_1`
      constraint (Site 1's `ParentName` chain) fires if ABF/SynCore retire
      while `guy762.kotordroids` + `guy762.mm.kotorcore` stay active — both
      are active today. Not safe to remove either `<li>` this pass.
- [ ] ModsConfig edit — not done, per the block above.
- [ ] `DroidsAreMachines.xml` ABF-half removal — not done (would be
      premature to edit ahead of the mod-list change it depends on).
- [ ] Cold-load verification — owed to a future batched restart once
      unblocked, per this item's own instruction not to trigger one now.

## Watch out
Never remove ABF/SynCore from `ModsConfig.xml` without first re-running
`retirement_order.py` clean — it is the one machine check that already knows
this exact trap. A clean sweep of "who references the ArtificialBeings.*
namespace" is necessary but **not sufficient**: this blocker is an
inheritance (`ParentName`) dependency, which throws no error and appears in
no grep for the C# class names — it only shows up if you check the
inheritance chain itself, which is exactly what `retirement_order.py` exists
to do.
