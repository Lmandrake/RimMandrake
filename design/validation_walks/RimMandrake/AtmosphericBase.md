# RimMandrake: AtmosphericBase — validation walk

subject: src/RimMandrake/AtmosphericBase  (packageId `mandrake.rm.atmosphericbase`)
deps: none intended (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: 🔴 **NOT BUILT.** Designed in one owner sitting 2026-09-16; the definition is
`design/RimMandrake/atmospheric_base_mod_definition.md`. A framework mod driving two ambient
channels — light and sound — on behalf of other mods, with a compositor that gives territory
to the top two moods, a tremor for the rest, gestures on top and the Narrator above all. This
walk exists so the VISION is bound before the code, per the WreckedMachines precedent
(2026-09-16, "the owner chose to bind a vision he has not built yet"). Its `## the walk` steps
cannot be authored concretely until the build exists and Phase 0's seven engine questions are
answered.

## must be true

*Written against the definition's laws, not against code. Every line here is a claim about
behaviour a build must satisfy; none has been observed.*

- Only emitters explicitly handed to the framework are ever driven — a glowing animal, a worn
  item, a plant and a hologram are never touched, no matter what claim is live.
- With no consumer registered and no player selection, the mod drives nothing and the colony
  is lit exactly as vanilla would light it.
- A gesture always restores the state underneath it exactly, including when it is interrupted
  by a higher-ranked gesture, and including across a save and reload mid-gesture.
- No live claim survives a landing: the reset is total.
- With power lost, no emitter is driven and no bed plays.
- Every colour an emitter is ever set to comes from its scheme's declared palette — the
  framework never produces an interpolated value, so the Graphic/Material cache is bounded by
  the sum of the palettes in play and never grows with time.
- Only emitters whose quantised value changed on a given evaluation are written and dirtied.
- Turning either channel off in Mod Settings leaves the other working, and turning both off
  leaves the game indistinguishable from the mod being absent.
- No Harmony patch alters a vanilla or third-party def; the take-over is additive and
  reversible per thing.

## the walk

⛔ **Not authorable yet.** Concrete steps need (a) the build and (b) Phase 0's answers, since
what is observable depends on whether a paused-frame hook exists at all. What the walk will
have to prove, in order:

1. [D] Take over one light by its own button, confirm the framework drives it, release it,
   confirm the light returns to its prior colour and radius.
2. [B] Push one mood on one group; read back what the compositor says is showing; confirm it
   matches and that untaken lights nearby are unchanged.
3. [B] Push a second mood at a lower rank and confirm **territory**, not colour-mixing — every
   driven emitter must hold a colour from exactly one of the two palettes.
4. [B] Push a third, fourth and fifth mood; confirm at most three tremor contributors, each in
   its own palette.
5. [B] Play the Narrator's gesture over a live alarm; confirm it wins, and that the alarm is
   exactly restored afterwards.
6. [L] Pause the game mid-gesture; confirm the gesture continues (or record that L10 is void).
7. [B] Cut power; confirm silence in both channels.
8. [B] Land; confirm every claim is gone.
9. [D] Save mid-gesture, reload, confirm the substrate is what it was.

## north star

state: DRAFT
validated-hash:

⚠️ **DRAFT — BINDS NOTHING.** Per `design/RimMandrake/north_star_validation_spec.md` §3, a
DRAFT checklist cannot fail a mod and cannot green one. Written 2026-09-16 on the **Mac
laptop** — no game, no def dump, and RimSage has never connected there — so every line traces
to the owner's own words in that evening's sitting, to `canon.yml`, or to a file on disk. Only
the owner promotes a line to a bar.

🔴 **This walk names a mod that does not exist.** Validating it binds a vision, not a build,
and every line will fail on the day the code first runs. That is the intended state, and the
WreckedMachines precedent covers it.

⚠️ **One axis this system does not have.** The spec provides a **show** axis (visual) and a
**read** axis (text). AtmosphericBase's entire sound channel — beds, stings, acoustic
territory — is judgeable by neither: nothing is shown and nothing is read. A `must hear` axis
is owed, or the sound half ships permanently unbindable. Filed as
`NORTH_STAR_HEAR_AXIS_1`.

Provenance tag per line: 🗣 his verbatim words or a ruling of his · 📐 measured from a file on
disk this pass · 🤔 my inference, weakest, cut freely.

### the experience  (OWNER'S WORDS — verbatim)

2026-09-16, commissioning the mod:

> *"It treats the grid of player lights as a tapestry to swirl patterns around creatively."*
>
> *"Onboard the Utinni, the players don't change the color of the lights, the gods do."*

The image he reached for when asked what makes the Narrator unmistakable — and the reason the
whole framework needs a restore-what-was-underneath layer:

> *"The narrator, I was imagining now, might suddenly bring up the brightness of the lights to
> a bright white... he speaks... and then slowly dim back to whatever was going on."*

And the sentence that decides what darkness means here:

> *"Let it go absolutely black, but there will almost be a little motion, a little flickering,
> a writhing that lets you know that it's not a power outage. It's there for a reason. Figure
> it out."*

🔑 The through-line: **the ship is not alive, and it must still feel inhabited.** Canon forbids
a ship with moods of its own (`canon.yml` `narrator`, 2026-08-30 — no integrating self, no ego,
no self-description). So every effect this mod produces has to read as *somebody using the
wiring*, never as the building emoting. A pretty ambience that reads as a mood of the ship is a
failure of this mod even if the player likes it.

### must show

1. **Two gods hold visibly separate territory, and the boundary moves.** 🗣 ruled — "a pattern
   that swirls between one and the other"; 📐 canon.yml `in_front`: "the corridors will show
   this in different colored areas even perhaps that slowly move throughout the ship". A player
   looking at the ship can point at where one ends and the other begins.
2. **A third presence is visible without being identifiable as territory.** 🗣 ruled; 📐 canon:
   the silent eight express through "flickers in their palettes". The tremor must read as
   *someone else is stirring*, in a palette that is that god's own.
3. **A chosen darkness is never mistakable for a power failure.** 🗣 ruled. Motion in the dark,
   and uncontrolled light left standing.
4. **The Narrator's arrival is unmistakable on first encounter**, with no text required to
   explain it. 🗣 ruled — reserved bright white, a rise, a hold, a slow return.
5. **The lights return exactly to what they were doing before he spoke.** 🗣 ruled — this is the
   half of the gesture that makes the other half legible.
6. **A god is identifiable by hue and by motion independently** — the same god recognisable in a
   dim scene by how it moves, and in a still frame by its colour. 🗣 ruled.
7. **An alarm reads as an alarm at a glance**, in the first second, with no learning required.
   🤔 inferred from the omen brief that created this mod.
8. **A few fixtures carry the speed and the mass moves slowly** — and it reads as a real alarm
   panel rather than as a uniform strobe. 🗣 ruled.
9. **The ship looks inhabited by tenants, not animated by itself.** 📐 canon's no-moods-of-the-ship
   law, made visual: no effect may read as the building having a feeling.
10. **Nothing the player did not hand over is ever driven.** 🗣 ruled — a glowing animal, worn
    gear, a plant and a hologram keep their own light in every scene.
11. **The default scheme at install is restrained enough to live under** — it must not read as a
    light show in an ordinary colony. 🗣 ruled (gentle by default), 🤔 the "restrained" bar is mine.

### cannot show

1. **No interpolated colour, ever.** 📐 `TWINKLE_FLORA_SPIKE_1`: a continuously varying colour
   mints a cached Material per value forever. A smooth fade is the signature of the bug, so a
   visible smooth fade is itself a violation.
2. **No effect that reads as the ship expressing itself.** 📐 canon `narrator` — the inverse of
   must-show 9, stated separately because it is the one failure a pleasing demo can hide.
3. **No white used as a dominant colour by anything but the Narrator.** 🗣 ruled and enforced.
4. **No alarm the Narrator cannot interrupt**, and no gesture that leaves the alarm broken
   afterwards. 🗣 ruled.
5. **No claim visibly surviving a landing.** 🗣 ruled — the reset is a story beat, so a mood that
   bleeds through it is a visible lie.

### candidate lines  (NOT his — agent-drafted, bind nothing until promoted)

- 🤔 A scheme holding only part of the grid still reads as itself, rather than as a fragment of
  something.
- 🤔 Two simultaneous gods are distinguishable at play zoom without moving the camera.
- 🤔 The tremor never grows loud enough to be mistaken for territory.
- 🤔 An omen's arrival is distinguishable from an ongoing mood within one cycle of the pattern.
