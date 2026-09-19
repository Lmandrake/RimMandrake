## spec

canon.yml `in_front.core_src` (owner, 2026-08-30, canonizing the 2026-08-29 sketch), the exact
rule this item builds against:

> engagement (positive or negative, per-god via the satiation tracks) makes a god LOUDER; the
> loudest is IN FRONT and holds the ship's actuator priority - lights, doors, subsystem behavior
> - which is scheduler allocation on the Cradle's substrate, no magic, read by the Jawa as favor.
> The front is reckoned at each LANDING (judgement of the past map) AND can shift MID-MAP on a
> sufficiently violent engagement swing (a massacre, a great feast, a betrayal) - the landing
> judgement is the scheduled reckoning, not the only one. The silent eight express through
> ambient micro-gestures (door hesitations, hum shifts, flickers in their palettes).

`in_front.scorecard_src` adds: deed counters -> satiation deltas -> judgement ranking at landing
(and the mid-map flip). No light/sound output is in scope here — that is
`ATMOSPHERIC_BASE_BUILD_PROGRAM_1`'s job as a *consumer* of this derivation layer; this item is
purely the read/compute surface Ninefold owes.

**Built, in `src/RimMandrake/Ninefold/Source/GameComponent_Ninefold.cs`:**

- `GetLoudness(God god)` — pure derived read, `Mathf.Abs(satiation[god])`. Loudness IS engagement
  magnitude and satiation already IS the engagement track (§9 safe core), so this is a
  computation over EXISTING state, not a second tracked value that could drift from it.
- `GetLoudnessRank()` — every god, loudest first, deterministic tie-break by enum ordinal (never
  RNG). Exists so a consumer needing "top two" (territory, Phase 3) or "third and below" (tremor,
  capped at three, Phase 4) slices this list rather than building a second ranking computation —
  the repo has a standing warning against exactly that duplication.
- `GetFront()` — the OFFICIATED front (`God?`), distinct from `GetLoudnessRank()[0]`. Only moves
  at a landing or a qualifying mid-map swing, matching "the landing judgement is the scheduled
  reckoning, not the only one" (i.e. front is not simply "whoever is loudest this instant").
- `ReckonFrontAtLanding()` — recomputes and stores the front. Called from `FinalizeInit` (a
  baseline reckoning for a fresh colony / a save predating this item, since there is no past map
  to judge yet) and from the new `Patch_GravshipLanded.cs` postfix on
  `GenStep_GravshipMarker.Generate` — the same real arrival choke point
  `RimMandrake.GravshipLanding` already patches to unfog the new map. Gated on
  `RM_NinefoldSettings.engineEnabled`, matching every other mutator on this component.
- `MaybeFlipFrontOnViolentSwing(god, rawAmount)` — private, called from inside `ApplyDelta` (every
  one of the ~20 event hooks already funnels through it, so no new hook is needed for this half).
  Flips the front mid-map only when `|rawAmount| >= EventMagnitude.Large` AND the newly-loudest
  god differs from the current front. `EventMagnitude.Large` is this codebase's own existing tag
  for "massacre/great-feast/betrayal"-class events (Ta'Baa's launch, Ozzik's research
  breakthrough, Zizzik's mental break, Rekko's demolition all already use it) — reused rather than
  inventing a second, competing definition of "violent." `rawAmount` is captured in `ApplyDelta`
  BEFORE `eventMagnitudeMultiplier` scaling, so the violence threshold tracks the event's authored
  weight, not the owner's tuning slider.
- `frontGod`/`frontReckoned` persisted via `ExposeData` (`ninefoldFrontGod`/
  `ninefoldFrontReckoned`) so a mid-map flip survives save/reload.

**Scope line drawn on purpose:** the landing hook covers gravship arrivals only (the colony's one
"the ship lands" event, matching the Cradle-substrate framing) — a base-game caravan/pod arrival
at a site with no map is NOT reckoned as a landing here. If that path is ever needed, it is a
separate hook, not silently folded into this one.

**No new Mod Settings.** Every number this feature needs already exists and is already tunable:
the violence threshold reuses `EventMagnitude.Large`, and its scaling is already covered by the
existing `eventMagnitudeMultiplier` slider (via the raw/scaled split above). Adding a second,
overlapping slider here would just be a duplicate knob on the same underlying number.

## verify

- `dotnet build` on `Ninefold.csproj` (via Windows `dotnet.exe`, WSL cannot pass it a `/mnt/...`
  project path): **0 warnings, 0 errors**, 2026-09-19.
- No XML touched — `validate_patch.py` not applicable.
- 🔴 **Owed, not done here:** live-quicktest proof that loudness/front actually derive correctly
  in a real running game (does `GetFront()` return the right god after a scripted landing; does a
  Large-magnitude event actually flip it mid-map). This item is pure offline C# per its own
  instructions ("do NOT touch the bridge"); the runtime check is separate follow-up work, likely
  during `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` Phase 10 wiring or its own quicktest pass.
- Also owed, separately: the ~20-hook-count comment in `RM_NinefoldMod.cs` ("eighteen
  Patch_*.cs event hooks") is already stale independent of this item (Patch_KillManner.cs and
  Patch_Lovin.cs were added after that comment was written) — noted, not fixed here, out of scope.

## build log

- 2026-09-19 (FOUNDRY, BELT): claimed and started. Read canon.yml `in_front` (lines
  1598–1648) and the full `GameComponent_Ninefold.cs` source. Added the loudness/rank/front
  derivation layer described in `## spec` above, plus `Patch_GravshipLanded.cs`. Build clean.
  Left `doing` — live-quicktest verification not performed (see `## verify`).
