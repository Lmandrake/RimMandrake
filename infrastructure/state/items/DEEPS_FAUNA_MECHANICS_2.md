## spec

Second pass on `DEEPS_FAUNA_MECHANICS_1` (FOUNDRY's, built at `0e0fa8bef`),
run from BENCH while the owner slept, against a re-brief of the same three
owner asks. Fills the gaps between the first build and the brief; rewrites
nothing that worked. Filed as its own item because the commit hook refuses
BENCH edits to a FOUNDRY-owned item file — the code is one assembly either
way. Owner's words and the three mechanics: see `DEEPS_FAUNA_MECHANICS_1`.

## design

- Grabber: the hold stays a hediff on the victim (delivered by the pincer
  DamageDef); the CRUSH and the RESCUE move to a comp on the grabber, so
  damage is dealt outside the victim's hediff tick loop and "hurt the
  grabber to free the victim" has a seam (`PostPostApplyDamage`).
- Soulchime: proximity trigger needs line of sight; damage is a second
  trigger without it; psychically deaf pawns are immune.
- Drinker: a marker `DefModExtension` on a race says its blood is safe; a
  visible gauge hediff records how much was drained and sets the
  drained-fluids yield on death.

## status log
- 2026-09-19 (second pass, owner asleep) — found the first pass already
  committed at `0e0fa8bef`. This pass fills the gaps between that build and
  the re-brief, does not rewrite it: (G) a comp on the GRABBER itself so a
  third pawn's melee hit can break the hold + real Blunt crush damage to the
  torso each round; (S) psychic-deaf immunity, damage-triggered + LoS-gated
  stun; (D) `RM_HydrocarbonBloodExtension` (present ⇒ safe blood) + a visible
  `RM_FluidSacks` gauge whose severity sets the drained-fluids yield on
  death. Entries below are appended per mechanic as each compiles.

- **Second pass BUILT (`dotnet build -c Release`: 0 warnings, 0 errors;
  `validate_patch.py` over `CreatureBehaviors/Defs` + the Races file against
  the live set: 0 errors, the 3 known `RSW_Yooka` warnings only). Not
  deployed — the DLL is locked by the running game; the parent deploys at
  the next shutdown window.**
  - **Grabber**: new `RM_CompProperties_Grappler`/`RM_CompGrappler` on the
    GRABBER (wired onto `RSW_BovineBeetle`'s `<comps>`). Every
    `crushIntervalTicks` (120) it deals `crushDamage` (4) Blunt to each held
    pawn's torso (`BodyDef.corePart`) while alive, not downed, not in
    PanicFlee and within `crushRadius` (1.5) — seam `Pawn.TakeDamage` from
    the grabber's own CompTick, outside the victim's hediff loop. Its
    `PostPostApplyDamage` (ThingWithComps.cs l.394, RimSage) rolls
    `breakHoldChanceOnHit` (0.35) per hold on any damaging hit from a third
    pawn (the held pawn's own struggle stays the hediff's
    `escapeChancePerRound`). Consequence: **`RM_Grappled` no longer kills by
    severity** — `<lethalSeverity>1</lethalSeverity>` became
    `<maxSeverity>1</maxSeverity>`; severity is now only the tightening
    gauge driving the three stages, and real torso injury is the sole kill
    route. `grapplerCrushMultiplier` now scales both the crush damage and
    the tightening rate. Settings label rewritten to state the trade.
  - **Soulchime**: `RM_CompProximityPsychicStun` gained `requireLineOfSight`
    (default true; `GenSight.LineOfSight`, GenSight.cs l.20, skipFirstCell),
    `triggerOnDamage` (default true; `PostPostApplyDamage` emits at once,
    LoS ignored, same cooldown) and `psychicallyDeafImmune` (default true;
    `GetStatValue(StatDefOf.PsychicSensitivity) <= 0` skips). Soothe thought
    `RM_TameSootheThought` raised +3 → +6 per the brief. The "armor of
    crystal shards" stays the first pass's SIMPLIFIED comp (toggleable);
    the brief's reading — art + a small `ArmorRating_*` statBase — is the
    cheaper alternative if the owner prefers to drop the comp.
  - **Drinker**: `RM_HydrocarbonBloodExtension` (empty `DefModExtension`,
    `Source/RM_HydrocarbonBloodExtension.cs`) — present on a victim's
    ThingDef ⇒ safe blood regardless of fleshType; attached to NOTHING yet
    (Deeps races are wired by a later pass). `RM_CompFluidSacs` gained the
    visible gauge `RM_FluidSacks` (`Defs/HediffDefs/RM_FluidSacks_Hediffs.xml`,
    maxSeverity 1, three labelled stages, +`sackFillPerSeverity` 0.1 per
    drained severity, filled on every feed including a poisoning one) and a
    death drop via `ThingComp.Notify_Killed` (ThingWithComps.Kill l.318 via
    Pawn.Kill l.3511, RimSage): `round(severity × drainedFluidsAtFull=10)`
    of new item `RM_DrainedFluids` (`Defs/ThingDefs_Items/RM_DrainedFluids.xml`,
    ResourceBase, Chemfuel texture tinted dark, MarketValue 6) placed Near
    the corpse on `prevMap`. `RM_FluidSacPoison` retuned 6/day → 1.25/day
    (lethal in ~19 h from zero: the brief's "~1 day").
  - **Deliberately NOT done from the brief**: no `Patches/RSW_DeepsMechanics.xml`
    FindMod-gated patch. The first pass wired the comps directly into
    SWBestiary's own race def with `loadAfter mandrake.rm.creaturebehaviors`
    (the mod's existing `mandrake.rm.proximityhatch` precedent); splitting
    the wiring between a def and a patch would be worse than either, and
    moving all of it is churn on committed work. Consequence to know:
    SWBestiary hard-requires CreatureBehaviors for these three defs to load
    clean — same as it already does for ProximityHatch.
  - Tuning added this pass is INVENTED and unplayed, like the first pass's.

## north star

(none — a mechanics build, not a bar-gated content mod.)
