# ATMOSPHERIC_BASE_BUILD_PROGRAM_1 — the ambient framework the gods speak through

Design is DONE and is not to be re-derived: `design/RimMandrake/atmospheric_base_mod_definition.md`
holds fifteen laws, the object model, and §9's verbatim record of every ruling from the owner's
sitting on 2026-09-16. The DRAFT north star is
`design/validation_walks/RimMandrake/AtmosphericBase.md` (18 lines; DRAFT binds nothing until he
validates). Candidate schemes to react to:
`Transient/dynamiclighting_scheme_catalog_DRAFT_2026-09-16.md`.

🔴 **Read the laws before writing a line.** Four of them will be violated by the obvious
implementation: colour must be quantised (L4), blending is by allocation and never by
colour-mixing (L5), only changed emitters may be written and dirtied (§2.6 step 6), and darkness
must carry motion (L8).

## spec

**Both channels ship together** — his ruling, against light-first. So nothing here is releasable
until Phase 6 lands; the phase order below is build order, not release order.

### Phase 0 — DESKTOP ONLY. Eight questions, no code.

Spec §8 is the whole of this phase. Nothing else starts until it answers, because two of the
eight can void a law:

1. 🔴 Does a per-frame hook exist that runs **while the game is paused**? **L10 falls if not** —
   every gesture would freeze the instant a letter pauses the game, including the Narrator's.
   If the answer is no, stop and bring the owner the choice between game-time gestures and a
   different trigger point; do not silently build game-time.
2. 🔴 What does changing a **live glow colour** cost, at 10 / 100 / 500 emitters? The whole cost
   model rests on it. ⚠️ `TWINKLE_FLORA_SPIKE_1` measured a *sprite tint*, not a cast glow —
   different subsystem, and its numbers do not transfer. Do not cite them as if they did.
3. Can glow colour and radius be set at runtime on the fixtures the live mod stack actually
   ships (glowstoneforked, floorlights2, ledlightsstrip, nightlights, plus vanilla)?
4. Does 1.6 vanilla support coloured light at all, or does it come only from those mods?
5. Do positioned looping Sustainers behave acceptably when the mix changes as the camera moves?
6. What happens to lights and Sustainers during gravship **flight**?
7. Is a fully-dark fixture distinguishable from an unpowered one to the game's own light grid?
8. Do Sustainers support a partial volume ramp, or only start and stop? `RM_MapComponent_SilenceCue`
   reportedly holds a Desktop-verified finding that they do not — confirm it, because if beds
   cannot fade then every acoustic mood change is a cut rather than a swell, and §3 needs rewording.

Deliverable: answers recorded on this item with the instrument used for each, plus an explicit
go/no-go on L10.

🔴 **Two items block this programme regardless of Phase 0**, and both are the owner's:
`ATMOSPHERIC_BASE_CANVAS_1` (the ship has 11 light-capable things out of 2002, measured) and
`NINEFOLD_LOUDNESS_FRONT_1` (nothing computes rank). Phases 1-2 can proceed without them; Phase 3
onward cannot.

### Phase 1 — the skeleton and the take-over

Mod scaffold at `src/RimMandrake/AtmosphericBase` (`mandrake.rm.atmosphericbase`, namespace
`RimMandrake.AtmosphericBase`, prefix `RM_`, `loadAfter` Ludeon.RimWorld only, no Harmony patch
that alters any def). Capability discovery (§2.1) — never a def whitelist. The per-thing opt-in
button, and the scenario-decides path. The exclusion list is a hard bar: glowing animals, worn
equipment, plants, holograms are never touched. Release must restore the fixture's prior colour
and radius exactly.

### Phase 2 — one mood, quantised, cheap

Groups (§2.2), schemes as data (§2.3), and the compositor driving ONE mood. This is where L4 and
the dirty-only-on-change rule are proven, and where question 2's cost is re-measured against
real code rather than predicted.

### Phase 3 — territory

Two moods, allocation over the union of their groups, and a boundary that moves on its own slow
clock. This is the mod's signature and the thing canon already describes; if it does not read as
two presences, nothing later will save it.

### Phase 4 — the tremor

Moods ranked third and below, capped at three, each in its own palette (L6). It must never grow
loud enough to be mistaken for territory.

### Phase 5 — gestures, and the Narrator

Finite claims that composite above moods and restore the substrate exactly (L13). The reserved
white and its enforcement (L11). The Narrator above everything including a live alarm (L12).
Save/reload mid-gesture must restore correctly.

### Phase 6 — sound

Beds first, then stings, then acoustic territory, on the same claims (§3). Camera is the
listener. ⛔ `src/RimUtinni/RustCathedralHum` is **not to be touched** — the overlap is accepted
by ruling, and the mitigation is a volume control in this mod's own settings.

### Phase 7 — the witness ledger

§2.7, narrow by design. Exists so a god's letter can never claim a witness that was not there
(L14).

### Phase 8 — the two hook doors

Code API, then the def-driven API (§2.8). The def half is what lets an XML-only mod join.

### Phase 9 — the library and the showcase

The scheme catalog's admissible entries, and Mod Settings per spec §5: per-channel toggles, the
gentle default, group selection, the showcase, and this mod's own bed volume.

### Phase 10 — the consumers

Wire what already exists: `Ninefold` as the loudness/rank source, `Oracle` for the Narrator's
gesture (and its authored-letter equivalent, since canon says v1's Narrator is pre-authored
prose, not the LLM), `Aftermath`/`AftermathRites` for omen telegraphs, `GravshipLanding` for the
reset. `RaidRedesigner` is deliberately NOT a consumer — it is the other half of L2, acting on
the world directly. Detail: `Transient/atmosphericbase_hook_ecosystem_DRAFT_2026-09-16.md`.

## verify

- Phase 0: each answer names its instrument. An unanswerable question is recorded `UNMEASURED`,
  never guessed, and never inferred from a doc — several repo docs assert engine facts that trace
  to an earlier agent's prose.
- Phases 1-5: the walk's steps 1-9 in `design/validation_walks/RimMandrake/AtmosphericBase.md`,
  which cannot be authored concretely until Phase 0 answers.
- L4 has a mechanical check available and it should be built early: assert that every colour ever
  handed to an emitter is a member of a declared palette. A visible smooth fade is the leak's
  symptom, so the check and the north star's `never_interpolated_colour` line are looking at the
  same defect from two sides.
- Cost is re-measured at the end of Phase 2 and again at the end of Phase 6, on the owner's real
  mod list, not on the minimal one.

## criteria

Done means: both channels working; two gods legibly sharing a hull with a moving boundary; the
tremor present and never mistakable for territory; the Narrator's gesture unmistakable on first
encounter and restoring exactly; a chosen blackout that cannot be read as a power fault; nothing
driven that was not handed over; the code and def hooks both exercised by a real consumer; and
Mod Settings that degrade to indistinguishable-from-absent with everything off.

## watch out

- ⚠️ **The design doc supersedes its own earlier ruling and says so.** An earlier decision in the
  same sitting had this mod shipping alarm hardware — a strobe, a wall beacon, a floor strip. It
  was replaced outright by the take-over button, and the flasher role moved to the scheme (L7).
  Build no fixtures.
- ⚠️ **Rank is read, never computed here.** Canon's `in_front` already rules that loudness decides
  actuator priority, and `Ninefold` already computes satiation from deeds. A second ranking
  system inside this mod would be a competing answer to a settled question.
- ⚠️ **L2 is a boundary, not a limitation.** If a god should attract raiders, that belongs in
  `RaidRedesigner` and not here. The lights are an output device.
- ⚠️ **L1 is the law a good demo hides.** Everything must read as tenants using the wiring, never
  as the ship having feelings — canon forbids moods-of-the-ship. A beautiful ambience that reads
  as the ship emoting is a failure even if it is liked.
- ⚠️ The sound half is unbindable by the north-star system: it has a show axis and a read axis
  and nothing for audio, and per the owner's ruling on `NORTH_STAR_HEAR_AXIS_1` (dropped
  2026-09-17, no hear axis owed) it stays that way — sound is validated by PLAYTESTING, never
  by the automated script. Do not let Phase 6 ship believing a walk covers it.
- 📐 `RUT_HumLayers.xml` claims no audio pipeline exists in this repo. Measured false 2026-09-16:
  1048 custom audio files, including six ship-ambience sustainer defs and metal-creaking loops in
  `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/SoundDefs/`. Phase 6 needs no commissioned
  audio to start.

## Phase 0 — the eight engine questions, 2026-09-19, FOUNDRY (desktop, RimSage decompile + live mod XML)

Every answer below cites the exact class/method/field read. No answer is inferred from a doc's
prose. Instrument: `mcp__rimsage__*` against the 1.6/Odyssey decompile, plus direct XML reads of
the four fixture mods under the live Steam workshop folder.

### 1. 🔴 LOAD-BEARING — does a per-frame hook run while paused? **CONFIRMED: YES.**

`Verse/Root_Play.cs Update()` calls `Current.Game.UpdatePlay()` on every Unity frame, gated only
by `LongEventHandler.ShouldWaitForEvent` — never by `TimeSpeed.Paused`. Inside
`Game.UpdatePlay()` (`Verse/Game.cs` line 660), `tickManager.TickManagerUpdate()` runs first and
early-returns `if (Paused)` (`Verse/TickManager.cs` line ~321) — so tick-based logic genuinely
freezes. But the very next lines call `maps[i].MapUpdate()` **unconditionally**, which calls
`MapComponentUtility.MapComponentUpdate(this)` → every `MapComponent.MapComponentUpdate()` on
that map, every frame, regardless of pause state. `TickManager.Paused` (line 130) is `true` for
`curTimeSpeed == Paused` **and** every force-pause path (`ForcePaused`: window force-pause,
`LongEventHandler.ForcePause`, tile picker, gravship landing confirmation) — none of these gate
`MapUpdate`/`MapComponentUpdate` either. **L10 stands**: a `MapComponent.MapComponentUpdate()`
override is the per-frame hook the Narrator's gesture (and any other real-time-driven effect)
needs, and it keeps running through a letter-triggered pause. Go: build gestures against
`MapComponentUpdate()`, not against ticks.

### 2. 🔴 LOAD-BEARING — cost of a live glow-colour change at 10/100/500 emitters. **MEASURED (structural, from source — not a profiled ms figure; see caveat).**

Vanilla's own runtime colour-change path (`CompGlower.SetGlowColorInternal`, `Verse/CompGlower.cs`
— the method behind the in-game color picker and the darklight toggle) does **not** touch a
"colour" field in place: `GlowLight` (`Verse/Glow/GlowLight.cs`) bakes `glowColor` into an
immutable struct at registration time, so a colour change is a
`GlowGrid.DeRegisterGlower(this)` + `GlowGrid.RegisterGlower(this)` cycle on that one emitter
(`Verse/GlowGrid.cs`). Per-emitter cost, read directly from the methods:
- `DeRegisterGlower` calls `GetGlowerIndex`, a **linear scan of every light on the map**
  (`for (int i = 0; i < lights.Length; i++)`), then `NativeList<GlowLight>.RemoveAt` (shifts
  subsequent elements) — both O(total registered lights on the map), not O(changed emitters).
- `RegisterGlower` is an O(1) amortized append, then marks the shared `anyDirtyLight = true` and
  dirties the cells in that emitter's own `AffectedRect` (`GlowGrid.DirtyCell`).
- On the *next* `GlowGridUpdate_First()` (called once per map per frame from `Map.MapUpdate`),
  **one** `ComputeGlowGridsJob` is dispatched over `lights.Length` (all registered lights on the
  map) — but `Execute(index)` (`Verse/Glow/ComputeGlowGridsJob.cs`) is a no-op unless
  `light.dirty`, so the real flood-fill work (bounded by that light's own `diameter²`, e.g.
  ~29×29 cells for a 14-tile lamp) happens only for the emitters that actually changed. **One**
  `CombineColorsJob` is then dispatched over `indices.NumGridCells` (every map cell) but
  early-returns per-cell unless `dirtyCells.IsSet(i)`.
- Net effect: changing 10, 100 or 500 emitters' colours **in the same frame** costs one
  full-map-sized job dispatch of each kind (not one per emitter — `anyDirtyLight`/`anyDirtyCell`
  are single flags for the whole grid), Burst-compiled and Job-System-parallelized, doing real
  work only on the union of the changed emitters' footprints — **plus** N × O(total lights on
  map) for the register/deregister list scan-and-shift, which is the term that scales worst: at
  N≈total lights (e.g. 500 changes on a map carrying ~500 registered lights) that's on the order
  of hundreds of thousands of struct copies for the scan/shift alone, still native/Burst code but
  no longer O(N).
- ⚠️ **Caveat, honestly stated**: this is a structural complexity read from the algorithm, not a
  stopwatch number — Phase 0 is desktop-only and there is no live game to profile against. The
  item's own `## verify` already schedules a real re-measurement "at the end of Phase 2 and again
  at the end of Phase 6, on the owner's real mod list" — this analysis is what that re-measurement
  should be checked against, not a replacement for it. It does **not** transfer from
  `TWINKLE_FLORA_SPIKE_1` (sprite tint, a different subsystem) as the item warned.
- **Design implication**: batch colour writes per map per frame (never re-register the same
  emitter twice inside one evaluation), and avoid a compositor shape where every emitter
  re-registers every tick — the O(N × total-lights) term makes "quantised, changed-only" (already
  the north star's own must-show line) the only affordable pattern at hundreds of emitters.

### 3. Can glow colour and radius be set at runtime on the fixtures the mod stack ships? **CONFIRMED: YES, uniformly.**

`CompGlower.GlowColor` and `CompGlower.GlowRadius` (`Verse/CompGlower.cs`) are both **public
virtual properties with public setters** — `GlowColor`'s setter calls
`SetGlowColorInternal` (de/re-register cycle above); `GlowRadius`'s setter just writes
`glowRadiusOverride` directly (no re-register — read `GlowLight`'s constructor again: radius is
also baked in at registration, so a **radius** change needs the same de/re-register cycle as
colour, via `CompGlower.ForceRegister(Map)`, to actually take effect in the grid — the bare
setter alone does not by itself trigger recomputation). Read the live mod XML for the four named
fixtures directly from `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`:
  - Night Lights (`2149276108`) — `CompProperties_Glower`, `colorPickerEnabled=true`
  - Floor Lights 2 (`2882927601`) — `CompProperties_Glower`, `colorPickerEnabled=true`
  - `[ZAV] Glowstone` ("glowstoneforked", `3231900626`) — `CompProperties_Glower` (no
    `colorPickerEnabled`, i.e. no vanilla gizmo, but the comp and its public setters are identical)
  - LED Lights Strip (`3476135064`) — `CompProperties_Glower`, `colorPickerEnabled=true`
  All four ship the **stock vanilla `CompGlower`** — none defines a custom comp subclass — so
  `thing.TryGetComp<CompGlower>()` followed by setting `.GlowColor`/`.GlowRadius` (then
  `.ForceRegister(map)` for a radius change) works identically across all four plus vanilla
  lamps, with **no Harmony patch needed** (this is public API, not gizmo-gated — the
  `colorPickerEnabled` flag and the `ColoredLights` research only gate the player-facing UI
  affordance, never the property itself).

### 4. Does 1.6 vanilla support coloured light, or only the mods? **CONFIRMED: vanilla, base game.**

`ResearchProjectDefOf.ColoredLights` (`get_def_details`) is a base-game
`ResearchProjectDef` (`techLevel: Industrial`, prereq `Electricity` only — no DLC `MayRequire`),
and vanilla `StandingLamp` (`Defs/.../ThingDefs`) already carries
`CompProperties_Glower colorPickerEnabled=true` gated behind it. Coloured light is a vanilla
1.6 mechanic; the four fixture mods add more colour-capable lamp shapes on the same mechanism,
they don't invent it.

### 5. Do positioned looping Sustainers behave acceptably as the camera moves? **CONFIRMED, structurally — vanilla already ships the exact mechanism this needs.**

`SustainerManager.UpdateAllSustainerScopes()` (`Verse/Sound/SustainerManager.cs`) groups all live
`Sustainer`s by `SoundDef`, sorts each group by `CameraDistanceSquared`
(`Verse/Sound/Sustainer.cs`), and keeps only the nearest `SoundDef.maxVoices` "in scope" — this
is called every `SustainerManagerUpdate()` cycle (every frame while unpaused) and again whenever
a new sustainer registers. Instances that fall out of scope don't cut; `SustainerScopeFader`
(`Verse/Sound/SustainerScopeFader.cs`) ramps `inScopePercent` up 0.05/frame or down 0.03/frame —
a ~20–33 frame crossfade, not a pop. This is the same mechanism vanilla already uses for e.g.
multiple torches/campfires, so many positioned ambient beds panning in/out of camera range is a
solved problem at the engine level, **provided AtmosphericBase's authored `SoundDef`s set a
sane `maxVoices`.** ⚠️ Whether the *resulting mix* is pleasant is a judgement call, not a
measurement — consistent with the north star's own ruling that the hear axis is "part of the
playtest," never a gate.

### 6. What happens to lights and Sustainers during gravship flight? **CONFIRMED: nothing to drive — there is no live Map during travel.**

Traced `WorldComponent_GravshipController` (`Verse/WorldComponent_GravshipController.cs`):
takeoff converts the ship into a `Gravship` data object
(`GravshipUtility.GenerateGravship(engine)`), and `TakeoffEnded()` then calls
`GravshipUtility.AbandonMap(map)` (or `UpdateBillDestinations` if a grav anchor keeps a rump map)
followed by `GravshipUtility.TravelTo(gravship, takeoffTile, landingTile)` — travel happens on
the **World** layer (like a caravan), with `map = null` for the duration. The ~10-second
takeoff/landing cutscenes the player sees (`WorldComponentUpdate`, `timeLeft`/`progress`,
`DrawGravship`) render a **captured texture snapshot** (`GravshipCapturer`/`Capture`) — dozens of
call sites (`DynamicDrawManager`, `SectionLayer_Things`, `FleckSystem`, etc.) explicitly check
`WorldComponent_GravshipController.GravshipRenderInProgess` to suppress the live mesh/glow/fleck
draw paths in favor of that snapshot. So: no GlowGrid, no registered Sustainers exist for the
travelling ship at all — the framework needs **zero** flight-specific handling, exactly as the
item's own phrasing hinted ("given landing is a reset"). The only thing that must be correct is
the existing landing-reset requirement (`never_a_claim_surviving_a_landing`), which Phase 1
already owns.

### 7. Is a fully-dark fixture distinguishable from an unpowered one to the game's own light grid? **CONFIRMED: NO at the grid level — YES at the component level.**

`GlowGrid.CombineColorsJob.AddColors` (`Verse/GlowGrid.cs`) explicitly skips accumulating
anything when `colorInt.r > 0 || g > 0 || b > 0` is false — a registered `GlowLight` whose colour
is exactly `(0,0,0)` contributes **nothing** to `accumulatedGlow`, byte-identical to a fixture
that was never registered at all (`DeRegisterGlower`'d on power loss via `CompGlower.UpdateLit`).
So `GlowGrid.PsychGlowAt`/`GroundGlowAt` — what the game's own light level and pawn-mood checks
read — **cannot tell the two states apart** when the colour is literally zero. They ARE
distinguishable in code: `CompGlower.Glows` (the `glowOnInt` bool) is `true` and the fixture
stays in `litGlowers` for the driven-dark-but-registered case, `false`/absent for genuinely
unpowered. **Design consequence, confirmed rather than assumed**: the owner's "writhe/flicker,
never a static black" requirement isn't just an aesthetic choice — it's load-bearing. A literal
`(0,0,0)` blackout scheme is invisible to the light grid; the chosen-darkness effect needs at
least an intermittently nonzero colour (even very dark) for the grid to register anything a
player-visible glow could be built on, or the "writhe" needs to live entirely in a channel other
than glow colour (fixture graphic swap, a hologram's own separately-lit sprite, etc.).

### 8. Do Sustainers support a partial volume ramp? **REVISES the prior finding: YES, via SoundDef authoring — not via a one-line API call.**

`RM_MapComponent_SilenceCue.cs`'s header comment ("neither Sustainer nor SustainerManager
exposes a partial volume-ramp") is narrowly true — there is no `Sustainer.SetVolume(float)`
convenience method — but it undersells what exists one layer down. `SubSoundDef.paramMappings`
(`Verse/Sound/SubSoundDef.cs`) is a `List<SoundParameterMapping>`
(`Verse/Sound/SoundParameterMapping.cs`) applied to every `Sample` every frame
(`SoundParameterMapping.Apply`, `paramUpdateMode = Constant`). `SoundParamSource_External`
(`Verse/Sound/SoundParamSource_External.cs`) reads an arbitrary named float straight out of
`sustainer.externalParams[key]` (`Verse/Sound/SoundParams.cs`, a plain string-keyed dictionary
any caller can write every tick), and `SoundParamTarget_Volume`
(`Verse/Sound/SoundParamTarget_Volume.cs`) feeds that through a `SimpleCurve` into
`Sample.MappedVolumeMultiplier` (`Verse/Sound/Sample.cs` line ~152) — this is the exact
mechanism vanilla already uses to continuously drive volume from fire size / wind speed / etc.
**Beds CAN fade smoothly** — but only for `SoundDef`s that are authored with such a mapping.
Since Phase 6 already commits to authoring this mod's own bed `SoundDef`s (§6 "beds first"),
this is not a blocker: give every bed a `paramMappings` entry (`SoundParamSource_External` with
an agreed `inParamName` → `SoundParamTarget_Volume`) and drive it from the compositor each
frame/tick via `sustainer.externalParams["intensity"] = 0..1`. A **third-party** sustainer whose
`SoundDef` was never authored with such a mapping still cannot be ramped without editing its def
— which matches L2/L7's existing boundary (this mod drives its own claims, not arbitrary
third-party audio) and needs no new workaround.

**Go/no-go on L10**: **GO.** Question 1 confirms the per-frame hook exists and survives every
pause path the engine has. Phase 1 can proceed.
