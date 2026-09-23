# GREENTIDE_HUMMING_GROVE_1 — a grove that hums at differing pitches as you walk

## the question he asked

**Owner, 2026-09-22**, verbatim, on the humming tree (`RM_Thalquith`) in the jungle roster:

> *"Would it be mechanically possible in Rimworld to have different trees hum at slightly different
> frequencies, producing a soundscape that changes as you walk through the grove? that's pretty
> magical..."*

⚠️ **This is a QUESTION, not yet a ruling.** He is asking whether the engine can do it. ⛔ Do not
design the mechanic until it is answered — and do not answer it from reasoning.

## ⛔ It is UNMEASURABLE on the Mac laptop — this item needs `game-up`

No RimSage, no def dump, no running game there, so engine audio internals cannot be read. 🔴 The
project has already paid for guessing an animation mechanism once: the fire hawk shipped a wing
render-tree that the owner's own live test found broken, because the approach was assumed rather than
measured. **Audio is the same class of risk.** Answer it on the Desktop.

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

## what to measure on the Desktop — the specific checks

1. Can a `Sustainer` be attached to a spawned `Plant` and play **positionally** (with distance
   falloff relative to the camera)? Name the `SoundInfo` overload that does it.
2. Does a per-Thing sustainer support **per-instance pitch**, and is it set on the `SoundDef`, on the
   sustainer, or by a mapped parameter?
3. Is there any **volume ramp** available to a per-Thing sustainer, or does the no-partial-ramp
   finding apply there too? ⇒ If not, does natural distance falloff supply the blend instead?
4. What is the **cost** of N simultaneous positional sustainers? A grove is many trees, and this
   biome is ruled *"choked with foliage"* — the count could be large.
5. Does it survive save/load and camera jumps without stuck or duplicated sustainers?

## verify

A recorded answer to each of the five questions above, each naming what was read or run. Then, only
if it is possible: an owner ruling on whether to build it, and a distinction from the Cathedral's hum
written down. ⛔ No claim that it works until he has heard it in play — this is an experiential effect
and his ear is the authority.

## criteria

Walking through the grove is a reason to walk through the grove.

## Watch out

- ⛔ **Do not report this as possible because the Cathedral hums.** Different mechanism, different
  attachment, different question. That inference is the exact shape of the flight-animation mistake.
- ⚠️ If it turns out impossible, say so plainly — the tree is already justified without it, and the
  hum can stay as description. It was filed as *"flavour, or a real mechanic"* and flavour is a
  legitimate outcome.
