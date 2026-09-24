# GREENTIDE_HUMMING_GROVE_1 — a grove that hums at differing pitches as you walk

## the question he asked

**Owner, 2026-09-22**, verbatim, on the humming tree (`RM_Thalquith`) in the jungle roster:

> *"Would it be mechanically possible in Rimworld to have different trees hum at slightly different
> frequencies, producing a soundscape that changes as you walk through the grove? that's pretty
> magical..."*

## ✅ ANSWERED AND UNBLOCKED — owner ruling 2026-09-22

Told that the shipped hum system is **camera-attached rather than world-positional**, and that this
was the gap between it and his idea, he ruled:

> *"It's ok if it were attached to the camera."*

🔑 **That collapses the hard part of this item.** The unknown was whether a `Sustainer` can hang off a
spawned `Plant` and behave positionally — an engine question, unmeasurable on the Mac, and the exact
shape of risk that cost the fire hawk a live test. **Camera attachment is already shipped, proven and
readable in this repo**, so the mechanism no longer needs an engine measurement at all.

⇒ **`needs` moved from `game-up` to `offline`.** This is now designable and buildable without the game
— what remains is content and tuning, not a capability question.

### The mechanism, now that camera attachment is allowed

Copy `RM_MapComponent_BiomeAttitude`'s proven shape: a plain `MapComponent` that each tick decides
**how many hum layers play and which**, each layer a `SoundDef` spawned via
`TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick))`. In the Cathedral a mood band drives
the layer count; here the driver is instead **what is near the camera** — how many humming trees are
in view, and of what kind. Walking into a dense grove adds layers; walking out sheds them. *"Different
frequencies"* becomes several authored `SoundDef`s at different pitches rather than runtime pitch
manipulation, which sidesteps per-instance pitch entirely.

⚠️ **The one caveat that survives** — and it is now a tuning problem, not a blocker: the recorded
finding below says sustainers expose no partial volume ramp, so layers may **pop in and out** rather
than fade. Mitigations that need no engine work: hysteresis on the layer count (the Cathedral already
implements de-escalation-only hysteresis, so copy it), and layer changes gated to a minimum interval.
⇒ Judge it by ear, then tune. ⛔ Do not report it as smooth until he has heard it.

## ✅ What IS established, from our own shipped code and a prior Desktop verification

### We already spawn and LAYER hum sustainers — it is shipped, in another biome

`src/RimUtinni/RustCathedralHum/Source/RM_MapComponent_BiomeAttitude.cs` (`RUST_CATHEDRAL_MECHANICS_1`
§1) runs a hum-mood system whose band *"drives (a) how many layered hum Sustainers play (0 at the
worst band — the sheet's 'when the hum drops, stop moving' survival tell)"*. It spawns them with
`layerSound?.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick))` (line 295).

⇒ **Layered, dynamically-counted hum sustainers are a solved problem here.** That is the encouraging
half of the answer.

### But that implementation is NOT positional, and positional is what his idea needs

`SoundInfo.OnCamera` attaches the sound to the camera — no world position, therefore no falloff and
no change as you move. His idea requires **per-Thing, world-positioned** sustainers so proximity to
individual trees is what shapes the mix. ⚠️ Whether a `Sustainer` can be attached to a `Plant` and
behave positionally is **UNVERIFIED** — do not assume it from the existence of the Cathedral system.

### 🔴 And there is one recorded obstacle that bears directly on "changes as you walk"

`RM_MapComponent_SilenceCue.cs` records, RimSage-verified against `Verse/Sound/Sustainer.cs`,
`SustainerManager.cs` and `RimWorld/AmbientSoundManager.cs`:

> *"neither Sustainer nor SustainerManager exposes a partial volume-ramp, so this ends the matching
> sustainers outright (may pop audibly — an accepted honest trade the kit spec itself names)"*

⇒ **If there is no partial volume ramp, a smooth crossfade as the player walks may not be available**,
and the effect could pop tree-by-tree instead of blending. That is the difference between *magical*
and *broken*, so it is the first thing to measure. ⚠️ Note that finding was made about **biome
ambient** sustainers; whether a per-Thing sustainer has its own volume/pitch handling is a separate
question and is exactly what needs checking.

## 🔴 A collision to settle before building: the Rust Cathedral already owns "the hum stops"

The Cathedral's hum dropping to zero layers **is that biome's signature survival tell** — *"when the
hum drops, stop moving."* Two biomes whose signature is a hum that goes silent would dilute both.

⇒ They are distinguishable if made so deliberately, and the distinction should be designed, not
hoped for:

| | Rust Cathedral | Greentide grove (proposed) |
|---|---|---|
| mechanism | map-wide, camera-attached | per-tree, positional |
| what it encodes | a threat/mood state | **where you are standing** |
| the player reads | *"something changed"* | *"I have moved"* |

🔑 So the Greentide's version should be about **place and navigation**, not danger. ⛔ And it must not
reuse "the hum stops means a predator" — that meaning is taken, and the Greentide already has its own
silence cue (`RM_MapComponent_SilenceCue`, which hushes biome ambience when a predator hunts near
home) that would directly contradict it.

## ⛔ SUPERSEDED — the five engine questions this item was filed to answer

Camera attachment being acceptable removes all five. They are deleted rather than left standing, so
nobody spends a Desktop session on them: they asked whether a `Sustainer` can attach to a `Plant`
positionally, whether a per-Thing sustainer supports per-instance pitch, whether it has its own volume
ramp, what N simultaneous positional sustainers cost, and whether they survive save/load. **None is
needed now** — the camera-attached route answers the capability question by already working.

⚠️ The one thing still worth confirming is cheap and is a *tuning* check, not a gate: how audible the
layer pop is in practice. That is settled by listening, not by reading the engine.

## 🔨 BUILT 2026-09-23 — written, registered; COMPILED the same day on the Desktop (section below), NOT deployed, NOT proven

Two files in `mandrake.rm.creaturebehaviors`, generic per his ruling — this assembly still names no
plant, no biome and no sound:

- **`RM_ProximitySoundscapeExtension.cs`** — a `DefModExtension` a content mod puts on its own ThingDef:
  `groupKey`, `humLayers` (several authored SoundDefs at different pitches, so no runtime pitch
  manipulation), `radius`, `thingsPerLayer`, `checkIntervalTicks`, `dropHysteresisThings`,
  `minLayerChangeIntervalTicks`. Full `ConfigErrors` on every field.
- **`RM_MapComponent_ProximitySoundscape.cs`** — counts tagged Things near the listener each interval,
  converts the count to a layer total, and syncs `TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick))`
  exactly as `RM_MapComponent_BiomeAttitude` does. De-escalation-only hysteresis, plus a minimum
  layer-change interval as the only available mitigation for the no-volume-ramp pop.
- **Registered:** both added to `RM_CreatureBehaviors.csproj` (it sets `EnableDefaultCompileItems false`
  and lists all 75 files, so an unregistered file compiles into nothing silently), and
  `proximitySoundscapeEnabled` added as field, `Scribe_Values` entry and settings checkbox.
- ✅ `run_selftests.py`: **61/73, identical with these changes stashed** — the 3 failures pre-exist
  (`selftest_codex_image`, `selftest_frozen_dumps`, `selftest_handoff`).

🔴 **One call is UNVERIFIED and it is isolated on purpose: reading the camera's current map position.**
`Find.CameraDriver` itself is proven live in this repo (our bridge calls `JumpToCurrentMapLoc(IntVec3)`
and `.shaker.DoShake(...)`), so the driver exists and speaks in map cells — but the **member that reads
its position** is not verified from our own source, and the Mac has no game, no def dump and no
decompiler. ⇒ It sits alone in `TryGetListenerCell`, marked `❓ CONFIRM ON THE DESKTOP`, and a false
return makes the whole mechanism silent rather than throwing every interval. ⛔ Confirm that member
before this ships.

⛔ **Nothing here is compiled.** There is no RimWorld assembly to reference on this machine, so
"written and brace-balanced" is the strongest claim available. ⚠️ And per the `## verify` below, it is
not *working* until he has heard it.

### Two deliberate departures from the Cathedral, both required by this item

1. **Zero layers never means danger here.** In the Cathedral, silence is the survival tell. Here zero
   only ever means "nothing tagged nearby", which is the ordinary state of most of a map — so the two
   cannot be confused, and it does not contradict `RM_MapComponent_SilenceCue`'s predator hush.
2. **State is not Scribed.** Every input is re-derivable from spawned Things and the camera, and a
   `Sustainer` cannot be saved — the `SenseWeb`/`DreadField` posture, deliberately not
   `LivingRegrowth`'s.

## ✅ Desktop step done 2026-09-23 — camera accessor confirmed, assembly compiled, NOT deployed

- `Find.CameraDriver` exposes **`public IntVec3 MapPosition`** (Verse/CameraDriver.cs:184, MEASURED from the decompiler).
  The code already used it; the `❓ CONFIRM` marker in `TryGetListenerCell` is replaced by the measured citation.
- `dotnet build RM_CreatureBehaviors.csproj -c Release` (user-local SDK 8.0): **0 warnings, 0 errors**;
  `Assemblies/RimMandrake.CreatureBehaviors.dll` rebuilt (97,280 → 103,424 bytes) and committed.
- ⛔ **Not deployed** — RimWorld was running (the DLL in `Mods/` is locked while loaded). `deploy_custom_mods.py --mod
  CreatureBehaviors` dry run shows exactly one drift line, the DLL; run it with `--apply` at the next shutdown window,
  then the `## verify` walk (he has to HEAR it) is the remaining owed work.

## spec

1. **Copy `RM_MapComponent_BiomeAttitude`'s shape** — plain `MapComponent`, per-tick layer decision,
   `TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick))`, de-escalation-only hysteresis.
   ⛔ Do not invent a new audio system; that file is the working reference.
2. **Drive the layer count from what is near the camera**, not from a mood state — that is what makes
   this about *place* rather than threat, and what keeps it distinct from the Cathedral.
3. **Author several hum `SoundDef`s at different pitches** as the "different frequencies", rather than
   manipulating pitch at runtime.
4. ✅ **BUILD IT GENERIC — owner ruling 2026-09-22.** Asked whether to build it for this one tree or as
   something any future biome can use, he ruled **reusable by any biome**: a plant or biome gets a
   proximity-driven soundscape by tagging its content, with no new C# per biome.
   🔑 **His reasoning is the one I put to him and he took:** this is the *second* time the idea has
   come up in this project — `RustCathedralHum` is the first — and a second occurrence is the signal to
   generalise rather than to copy. ⚠️ Accepted cost: the configuration has to be designed rather than
   hardcoded, which is more work now for a benefit that may never be claimed.
   ⇒ So it belongs in the **shared behaviours assembly** (`mandrake.rm.creaturebehaviors` is where
   generic cross-content behaviour lives — `RM_JobGiver_SeekShade`, `RM_MapComponent_SilenceCue` and
   `RM_CompPlantAlarm` are all there), configured by a `DefModExtension` on the content, exactly the
   comp-plus-extension pattern `RM_CompPlantAlarm` and `RM_CompWoundLink` already set.
   ⛔ Do **not** follow `RustCathedralHum`'s precedent of living in its own biome mod — that is the
   thing this ruling changes. ⚠️ Whether the Cathedral's existing hum should later be migrated onto
   the generic version is **not ruled**; do not refactor it uninvited.
5. **Mod Settings toggle**, per the standing every-mod-ships-settings rule. An ambient audio effect is
   exactly the kind of thing a player may want off.

## verify

The grove's hum changes as the camera moves through it, the layer count changes without an obtrusive
pop, and it is distinguishable from the Rust Cathedral's hum in both mechanism and meaning. ⛔ **No
claim that it works until he has heard it in play** — this is an experiential effect and his ear is the
authority. ⚠️ Ship it as a savegame he can walk, per the standing rule for anything he must judge by
experiencing it; a description of a soundscape proves nothing.

## criteria

Walking through the grove is a reason to walk through the grove.

## Watch out

- ⛔ **Do not report this as possible because the Cathedral hums.** Different mechanism, different
  attachment, different question. That inference is the exact shape of the flight-animation mistake.
- ⚠️ If it turns out impossible, say so plainly — the tree is already justified without it, and the
  hum can stay as description. It was filed as *"flavour, or a real mechanic"* and flavour is a
  legitimate outcome.
