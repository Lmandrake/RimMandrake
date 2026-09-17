# AtmosphericBase — mod definition

**`mandrake.rm.atmosphericbase` · namespace `RimMandrake.AtmosphericBase` · def prefix `RM_`**

A RimMandrake-tier (campaign-agnostic) **framework and resource mod**: it takes over the
ambient channels of a colony or a gravship — **light** and **sound** — and animates them on
behalf of other mods. It ships schemes of its own to show what it can do, but its reason to
exist is that something else drives it.

Named by the owner, 2026-09-16, after he expanded the scope from lights alone: *"Include the
hooks for different background sound effects (hum, ambient noise) as part of this."* The
working name through the design sitting was DynamicLighting.

status: DRAFT — designed in one bench sitting with the owner, 2026-09-16. Nothing is built.

---

## §0 What this document is, and what it cannot tell you

Every design decision below is the owner's, made in a sitting on 2026-09-16, and §9 records
his words. Where a line says *ruled*, he ruled it; where it says *derived*, it follows from a
ruling and he has not seen it stated this way.

🔴 **The sitting happened on the Mac laptop, which can measure nothing about the game.** No
RimWorld install, no def dump, no decompiler, and RimSage has never connected there. So this
document asserts **no engine facts** except those already recorded in-repo from a Desktop
session, and §8 registers everything a build must confirm before relying on it. Two of those
are load-bearing enough that laws fall if they come back no.

---

## §1 The laws

Seventeen invariants. Everything else in this document derives from them, and a change to one
of them is a redesign rather than a tweak.

### The nature of the thing

**L1 — The ship has no self.** The channels carry the *gods'* moods, never the ship's. Nine
tenants fight over wiring; the Utinni feels nothing. *(canon.yml `narrator`, owner
2026-08-30: no integrating self, no ego, no self-description, no moods-of-the-ship. The
Oracle's own register blocks already enforce the same line in text.)*

**L2 — The channels are an output device.** The only world effect that may flow from them is
the physics of the medium itself: light really illuminates, so work, growth and fighting feel
it. A god that wants to attract raiders acts on the world directly. *(ruled: "don't act
through the lights, act directly on the world")*

**L3 — Aboard the Utinni the player never chooses.** Elsewhere a gentle scheme runs from
install. *(ruled; canon.yml `in_front`: "The lights happen of their own accord")*

### How it is allowed to look and sound

**L4 — Palettes are quantised.** A small fixed set of discrete colours per scheme, cycled.
Not a style choice: RimWorld caches a Graphic and Material per *exact* colour value, so a
smoothly varying colour mints a new one forever — an unbounded leak that looks fine for five
minutes and bad after a week. *(`TWINKLE_FLORA_SPIKE_1`, verified against Source on the
Desktop)*

**L5 — Two claimants blend by allocation, never by colour-mixing.** Each holds territory over
real fixtures and the boundary between them moves. *(ruled: "a pattern that swirls between
one and the other"; canon.yml `in_front`: "the corridors will show this in different colored
areas even perhaps that slowly move throughout the ship")*

**L6 — Beyond two, a claimant only perturbs.** The tremor carries the two or three most
agitated silent gods, each **in its own palette**, never a generic unsettledness. *(ruled;
canon.yml `in_front`: the silent eight express through "ambient micro-gestures (door
hesitations, hum shifts, flickers in their palettes)")*

**L7 — Speed lives in a few fixtures the scheme picks.** The mass moves slowly; a scheme
declares how many fast flashers it wants and the framework chooses which fixtures play that
role. Fast blinking is the expensive axis, so it is never the whole grid. *(ruled)*

**L8 — Darkness must never be still.** Full black is permitted, and a chosen dark always
carries motion — a flicker, a writhe — so it can never be read as a power fault. The lights
the framework does *not* control stay lit and prove the black was chosen. *(ruled: "Let it go
absolutely black, but there will almost be a little motion... It's there for a reason. Figure
it out.")*

**L9 — No power, no channels — but the gods do not go away.** A power blackout is silence
from the light and sound emitters, not a scheme. The gods themselves remain visible through
it, because their holograms need no power (L16). *(ruled; narrowed by the owner's hologram
ruling 2026-09-17 — the original law said only "a blackout is silence", which read as the
gods being absent from their own ship whenever the lights failed)*

### Who speaks, and when

**L10 — Everything runs on real time.** Gestures play through a pause, because a letter
pauses the game and that is exactly when the gesture matters. *(ruled)*

**L11 — Bright white belongs to the Narrator**, reserved and enforced: no god signature and
no scheme may take it as a dominant colour. *(ruled)*

**L12 — The Narrator outranks everything**, including a live raid alarm. *(ruled)*

**L13 — A mood is a state; a gesture is a performance.** A gesture always restores what was
underneath it — that restoration *is* the Narrator's slow dim back. *(ruled)*

**L14 — Nothing may claim a witness that did not happen.** *(ruled)*

**L15 — Look and cost may disagree, deliberately.** A cruel god may bathe the ship in
excellent working light. *(ruled)*

**L16 — A god's body is a hologram, and it runs on nothing.** The gods manifest as holograms
that work by themselves, without power. A hologram is therefore **never an emitter** — it is
not discovered, not claimed, not driven, and not extinguished by a blackout. This is why §2.1
excludes holograms from framework control, and it is what leaves something to see in a dark
ship. *(ruled 2026-09-17: "the gods will also be holograms that work by themselves, without
power")*

**L17 — Degrading the channel is an offence, and the gods feel it.** A power blackout angers
them, and so does stripping the ship of fixtures: removing lights below a threshold angers the
gods. The channel is their voice, so damage to it is not a neutral engineering event.
*(ruled 2026-09-17: "The gods REALLY don't like blackouts" and "Removing lights below a
threshold will anger the gods")*

⚠️ L17 is the **only** inbound effect in the design — everything else in this document flows
outward from the gods to the channels. It does not weaken L2: the channels remain an output
device, and this is the player acting on the fixtures, not a god acting through them.

---

## §2 The object model

### 2.1 Emitter

One thing the framework drives. Two kinds today: a **light emitter** (a fixture whose glow
colour and brightness can be set) and a **sound emitter** (a positioned ambient bed).

**Discovered by capability, never by a def whitelist.** The live mod list carries at least
four separate lighting mods, so a whitelist would rot inside a month. The test is whether the
thing exposes a settable glow.

**Taken over by an explicit opt-in, per thing** — a clickable button on anything glowing that
hands its glow to the framework, unless a scenario has already decided for that map. *(ruled:
"an opt-in clickable button on anything glowing that allows the mod to take over its glow.
That's only if the scenario allows it, otherwise the scenario decides for itself.")*

**In scope**, on the owner's own list for the Utinni: wall lights, lighting furniture, floor
lighting — "the obvious ones". **Never**: glowing animals, worn equipment, plants, holograms.
That exclusion is load-bearing twice over — it keeps the framework out of things whose glow
means something else, and it is what leaves reference light alive during an L8 blackout.

🔑 **The hologram exclusion is now the strongest of the four**, because a hologram is what a
god *is* (L16), not a lamp a god might borrow. Its glow means something else in the most
literal way available: it is the speaker, not the channel. A framework that dimmed a god's
own body during a scheme would be driving the thing it exists to express.

Each emitter carries a position, its current quantised value, and a role: **mass** or
**flasher** (assigned per-scheme, L7).

### 2.2 Group

A named set of emitters. Three sources, in precedence order:

1. **A hooking mod registers one**, with any membership it likes and a name it chooses. The
   Utinni will register Shrine, Rooms, internal and external. *(ruled)*
2. **The player selects one in settings** — whole ship, individual rooms, halls versus rooms.
   *(ruled)*
3. **The framework derives defaults** — rooms, corridors, exterior.

Groups may overlap; the compositor resolves which claim owns a contested emitter.

### 2.3 Scheme

The authored look, and exactly the four axes the owner named: *"There are color(s),
movements/patterns, brightness levels, speed of movement... a rich tapestry to paint with for
meaning."*

| axis | what it is |
|---|---|
| **palette** | an ordered small set of quantised colours (L4 — this is the cache bound) |
| **pattern** | a pure function of *(emitter, group, time)* returning a palette index |
| **brightness envelope** | level across the cycle, and whether it may go fully dark (L8) |
| **rate** | period for the mass, and separately for flashers, plus how many flashers |

A scheme is **data, not code**. That is what makes the declarative hook possible at all, and
it is why the pattern must be a pure function: it has to be expressible as a named,
parameterised kind rather than arbitrary logic.

Every scheme must still read when it holds only part of the grid, because L5 guarantees it
often will.

### 2.4 Claim

A request to show a scheme on a group. Two kinds, and they are genuinely different things
(L13):

- **Mood** — indefinite, held until replaced or released, carries a claimant identity (for
  the campaign, a god).
- **Gesture** — finite, with a duration; plays over whatever is underneath and on completion
  restores the substrate exactly.

A claim carries: claimant id, group, scheme, kind, rank, and whether it may cross into full
darkness.

### 2.5 Rank is loudness, and the framework does not compute it

`canon.yml` `in_front` (owner, 2026-08-30) already rules that engagement makes a god **louder**
and the loudest holds "the ship's actuator priority — lights, doors, subsystem behavior —
which is scheduler allocation on the Cradle's substrate, no magic". `src/RimMandrake/Ninefold`
already turns deeds into per-god satiation.

So **rank is read, never invented here.** A consumer supplies it; the framework orders by it.

### 2.6 Compositor

The single thing that decides what every emitter shows, evaluated on a real-time clock (L10):

1. Collect live claims.
2. The **top two moods** by rank take **territory** over the union of their groups, with the
   boundary advancing on its own slow clock (L5).
3. Moods ranked **third and below** become **tremor** contributions — perturbing a palette
   index or a flicker in their own palette, capped at three (L6).
4. **Gestures** composite on top in rank order; the Narrator's above all (L12).
5. Emit a quantised *(value, brightness)* pair per emitter.
6. 🔑 **Write and dirty only the emitters whose pair actually changed.**

Step 6 is what makes the whole design affordable, and it is inherited rather than invented:
`TWINKLE_FLORA_SPIKE_1` measured that a quantised pulse skips the dirty call on most ticks
because the quantised step usually has not moved. Cost therefore tracks the size of the
moving *front*, not the size of the grid.

### 2.7 Witness ledger

For each gesture and each mood transition, whether **an awake colonist was present in an
affected group**, recorded against the event. A consumer must consult it before referring to
the event in prose (L14).

The definition is deliberately narrow — awake, on the map, in a room containing an affected
emitter — and everything else counts as unwitnessed, because that is the honest direction to
be wrong in. This exists because the owner ruled that the player learns the vocabulary by
**discovery, with the gods eventually telling them**: a letter saying *"you saw my current run
green and did nothing"* is a lie if nobody was there, and one such lie costs more than the
line was worth.

🔑 **Presence, not illumination — and a blackout is witnessed absolutely.** The test is being
there, not being able to see by the framework's own light. Ruled 2026-09-17, resolving §9a C3:

- **A darkness is witnessed by anyone standing in it.** Light level does not enter the test.
  The god's own hologram is lit and needs no power (L16), so a colonist in a pitch-dark
  affected room genuinely has something in front of them — there is no case where the room is
  affected, a pawn is awake in it, and nothing is perceivable.
- 🔴 **A blackout is the referent, not merely a witnessed event.** It is the one thing the
  gods most want to talk about (L17), and it becomes referable **once resolved** — the gods
  speak about the dark after the power is back, not during it.
- The original rule required a *lit* affected room, which made the most dramatic thing the
  framework can do the one thing no god could ever mention. That was backwards and is deleted.

### 2.8 Two hook doors

*(ruled: both a code interface and an XML-declared one)*

**Code** — register and release a group; push a mood; play a gesture; query the witness
ledger; ask what is currently showing.

**Defs** — declare a group by room role or by emitter marking; bind a named signal to a
scheme + group + kind. Enough for an XML-only mod to make the ship answer an event with no
assembly of its own.

---

## §3 The sound channel

Ruled in full on 2026-09-16: **beds, stings, and acoustic territory.**

- **Beds** — layered looping ambient whose mix and pitch a claim bends. This is canon's "hum
  shifts" (`in_front`, 2026-08-30).
- **Stings** — short authored one-shots for the moments light is too slow to carry: a shock, an
  arrival, the Narrator drawing breath.
- **Acoustic territory** — sound obeys the same claims as light, so two gods can split the hull
  audibly and walking between them crosses a boundary. It rides the compositor already being
  built rather than a second system.

**The listener is the camera** — *you hear where you look* (ruled). Scrolling across the ship
walks the player through the gods' territories.

**Sound is what survives an L8 blackout.** A power failure kills the hum too, so a dark ship
that still hums wrong cannot be a fault. Light's writhe and sound's persistence are two
independent proofs that the darkness was chosen — and the framework should never rely on only
one of them.

**Accepted overlap, ruled deliberately.** `src/RimUtinni/RustCathedralHum` already drives
layered hum Sustainers off an irritation band (`RM_MapComponent_BiomeAttitude`), and the owner
ruled 2026-09-16 to **leave that mod entirely alone**: AtmosphericBase builds its own sound
path. Both may therefore play at once aboard a ship in that biome. ⛔ Do not "fix" this by
refactoring the hum mod; the mitigation is a Mod Settings control in *this* mod that lets a
player quiet its own beds.

**There is far more audio to hand than the repo believes.** `RUT_HumLayers.xml` states that "no
audio pipeline exists anywhere in this repo (confirmed by search)". That was false when
measured 2026-09-16: **1048 custom audio files** live under `src/`, including six ship-ambience
sustainer defs (Action VI, YT-1300, a raider corvette, three Gozanti variants) and
metal-creaking loops in `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/SoundDefs/`. The first
pass needs no commissioned audio.

---

## §4 The campaign layer, and what it owns

Ruled: the framework owns **behaviours and primitives**; the campaign owns **which god gets
which**, and may define new ones. So the split is by who owns the *meaning*.

**God identity is carried on two channels at once** — hue *and* motion (ruled). Each god owns
both a colour family and a characteristic way of moving, so identity survives losing either:
a dim scene still reads as motion, and a colourblind player still reads hue.

**The Narrator is not a god.** He has no mood (canon: no ego, no self-description), which is
precisely why his signature is the absence of a palette: a sudden rise to bright white, held
while he speaks, then a slow dim back to whatever was running. *(the owner's own image,
2026-09-16)*

⚠️ **In v1 the Narrator is pre-authored letter prose, not the LLM** (canon.yml `narrator`). So
his gesture must be triggerable by an authored letter, not only by an Oracle call.

**Landing is a RESET** — "a moment of RESET and contemplation of how/what was left and where
they are now" (ruled). Nothing carries across, which matches canon's reckoning of the front at
each landing. No persistence machinery is owed.

The nine signatures, the omen looks and the Narrator's exact gesture parameters are **an owner
sitting**, not agent work. Candidate schemes to react to are drafted in
`design/RimMandrake/atmospheric_base_scheme_catalog.md`.

---

## §5 Mod Settings

Per the standing rule that every mod ships a real settings screen (owner, 2026-09-12), and
because the owner's framing is that *the settings exist to show off what it can do*:

- On/off per channel — light, sound.
- The default scheme, **on** at install with something restrained (ruled). ⚠️ Because
  brightness is real light (L2), the shipped default must be authored to stay bright enough to
  work under; the framework enforces no floor, so this is a constraint on the default, not on
  the engine.
- Group selection for a player with no hooking mod: whole ship, individual rooms, halls versus
  rooms.
- A showcase that cycles the flagship schemes.
- Volume for this mod's own beds (the L8/§3 overlap mitigation).
- Every worldgen-irrelevant toggle here is safe mid-save; none of it is.

---

## §6 What must hook in

Measured to exist in this repo, 2026-09-16. Detail and ranking in
`design/RimMandrake/atmospheric_base_hook_ecosystem.md`.

| mod | what it pushes |
|---|---|
| `RimMandrake/Ninefold` | the pantheon's loudness — **the rank source**; moods per god |
| `RimMandrake/Oracle` | the Narrator's gesture, and its authored-letter equivalent |
| `RimMandrake/Aftermath` + `RimUtinni/AftermathRites` | omen telegraphs — "the coming of Omens made quite distinct" |
| `RimMandrake/GravshipLanding` | the landing RESET |
| `RimMandrake/RaidRedesigner` | nothing — it is the *other* half of L2, acting on the world directly |
| the Utinni scenario layer | Shrine / Rooms / internal / external group registration |

Canon also names **doors**, **subsystem behavior** and later **holo-emitters** as actuators the
front god seizes. None of those is in scope here; they are the siblings this design is shaped
to accommodate without being built for.

---

## §7 Why this is one mod and not two

The owner ruled both channels ship **together from the start**, against the option of light
first. The reason it is defensible: a claim, a rank, a group, a territory boundary and a
witness are identical for both channels, and a compositor proven on one channel would have
been re-opened by the second. The cost he accepted is that nothing is visible until both work.

---

## §8 UNMEASURED — owed a Desktop check before anything is built

🔴 **Two of these are load-bearing: a law falls if the answer is no.**

| # | question | what falls |
|---|---|---|
| 1 | 🔴 Does a per-frame hook exist that runs **while the game is paused**? | **L10 entirely.** Without it, every gesture freezes the moment a letter pauses the game — including the Narrator's. |
| 2 | 🔴 What does changing a **live glow colour** cost the light grid, at 10 / 100 / 500 emitters? | The whole cost model. `TWINKLE_FLORA_SPIKE_1` measured a *sprite tint*, not a cast glow; they are different subsystems and its numbers do not transfer. |
| 3 | Can a fixture's glow colour and radius be set at runtime at all, on the fixtures the mod stack actually ships? | §2.1's capability discovery. |
| 4 | Does 1.6 vanilla support coloured light, or does it come only from the lighting mods in the list? | What "adjustable-colour light" means in practice, and the shipped default. |
| 5 | Do positioned looping Sustainers behave acceptably when their mix changes as the camera moves? | Acoustic territory (§3). |
| 6 | What happens to lights and sustainers during gravship **flight**? | Whether flight needs any handling at all, given landing is a reset. |
| 7 | Is a fully-dark fixture distinguishable to the game's own light grid from an unpowered one? | Nothing — but it decides whether L8's writhe needs to be brighter than zero. |
| 8 | Do Sustainers support a **partial volume ramp**, or only start and stop? | §3's bed-bending. `RM_MapComponent_SilenceCue` reportedly already carries a Desktop-verified finding that they do not — if so, beds cannot fade, and a mood's acoustic change is a cut rather than a swell. Added by §9a C5. |

Phase 0 of the build programme is these eight, and nothing else.

---

## §9 The rulings, verbatim

All owner, 2026-09-16, in one bench sitting, unless dated otherwise.

**The origin.** The mod was born from a different decision: a checklist line requiring an omen
to read as a warning was cut, and the burden moved to the lights.

> *"Cut the line, but then we dedicate ourselves to making the ship lights truly dramatic in
> indication... unmissable. Speaking of, I'm not sure we have established the mod responsible
> for mood lighting and reactive light pulses and dancing/swirling lights acting alive, have
> we?"*

Measured that day: nothing did. Zero such directory in `src/`, zero ledger items, zero
design-doc mentions; the installed list carried only static light sources, one darkness mod and
one power-saver. Filed as `REACTIVE_SHIP_LIGHTING_1`.

**The commission.**

> *"It treats the grid of player lights as a tapestry to swirl patterns around creatively."*
>
> *"Onboard the Utinni, the players don't change the color of the lights, the gods do."*

**Groups.**

> *"A mod can hook however it wishes (Utinni will have distinct Shrine, Rooms, internal,
> external lights). Without external hook, the player can set in the mod settings a few
> selections (individual rooms, whole ship, halls vs rooms, etc)"*

**The four axes, and the Narrator's gesture.**

> *"There are color(s), movements/patterns, brightness levels, speed of movement... a rich
> tapestry to paint with for meaning. The narrator, I was imagining now, might suddenly bring up
> the brightness of the lights to a bright white... he speaks... and then slowly dim back to
> whatever was going on."*

**Two gods at once.**

> *"It would mix between the gods: a pattern that swirls between one and the other."*

**The boundary of the mod's authority.**

> *"...as far as this mod's concerned, but the gods that would scream and attract attention
> WILL affect raids directly independent of these lights (don't act through the lights, act
> directly on the world)"*

**Darkness.**

> *"Let it go absolutely black, but there will almost be a little motion, a little flickering, a
> writhing that lets you know that it's not a power outage. It's there for a reason. Figure it
> out. There will be other sources of light that aren't similarly controlled (holograms, lights
> that aren't recognized by the mod)"*

**Scope, and the name.**

> *"You're right. Include the hooks for different background sound effects (hum, ambient noise)
> as part of this, and now it should be called DynamicAmbients (maybe suggest a better name?)"*

Named **AtmosphericBase** by him a round later, from a card of four candidates.

**Landing.**

> *"landing is a moment of RESET and contemplation of how/what was left and where they are now"*

**Take-over, instead of new hardware.**

> *"no, it should be an opt-in clickable button on anything glowing that allows the mod to take
> over its glow. That's only if the scenario allows it, otherwise the scenario decides for
> itself. For the Utinni, it will take over nearly any wall light, lighting furniture, floor
> lighting... the obvious ones. It won't touch glowing animals or worn equipment, plants,
> holograms, etc."*

**Ruled by card, same sitting:** the player never has a scheme aboard the Utinni · both a code
and an XML hook · a gentle scheme on by default · god identity on hue *and* motion · learning by
discovery with the gods eventually telling you · mood and gesture are different kinds · the
witness ledger, and gods may only reference what was seen · white reserved and enforced · the
tremor identifiable a few at a time · the Narrator outranks a live alarm · look and cost may
disagree · brightness is fully real and the gods can hurt you · the scheme picks its flashers ·
beds, stings and acoustic territory · leave `RustCathedralHum` alone · the camera is the
listener · both channels ship together.

**Superseded within the sitting**, recorded so nobody rebuilds it: he first ruled that the mod
would **ship its own alarm fixtures** (a strobe, a wall beacon, a floor strip) alongside marking.
The take-over-button ruling replaced that outright — there is no new hardware, and the flasher
role moved to the scheme (L7).

### Second sitting — owner, 2026-09-17

Three cards, answering §9a's open corrections. **These added two laws and narrowed a third**, so
they are a redesign of the darkness rules rather than a tweak.

**On the canvas** (C1 — the ship had 11 light-capable things in 2002):

> *"We will add some lights for sure, and they will be irregular. The player can add more lights.
> Removing lights below a threshold will anger the gods."*

**On the blackout and the witness ledger** (C3 — a blackout was unreferable):

> *"The blackout IS the thing referred to. The gods REALLY don't like blackouts. Fix that right
> now! It becomes absolutely witnessed and referencable once resolved. And the gods will also be
> holograms that work by themselves, without power."*

**On the sound channel's judgeability**, choosing a third `must hear` axis for the north-star
system over binding only sound's fixed parts, with one condition attached:

> *"but don't block on it, it's just part of the playtest"*

🔑 **What the second sitting changed, in one line each**: L16 (a god's body is a hologram running
on nothing) and L17 (degrading the channel angers the gods) are new; L9 no longer implies the gods
vanish in a blackout; §2.7 tests presence rather than illumination; the canvas is authored in and
irregular by requirement; and the sound axis is real but never a gate.

---

## §9a Corrections — what the repo says back to this design

A hook census was run over the repo after the sitting
(`design/RimMandrake/atmospheric_base_hook_ecosystem.md`). It contradicted this document in five
places. **Four are now settled — C1, C3 and C4 by the owner's rulings of 2026-09-17, C2 by
measurement — and the laws above have been changed accordingly.** Only C5 is still owed a
Desktop check.

### ✅ C1 — RULED: the canvas is authored in, irregularly, and defended by the gods

The newest exported ship layout, `design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml`,
holds **2002 things, of which 11 are light-capable: 6 `Brazier` and 5 `AncientLamp`.** Verified in
this window by parsing the layout, after a first query returned a wrong zero.

A framework that treats a grid of lights as a tapestry has, on the ship it was designed for, no
grid. And the Utinni ships as a **frozen savegame** — the player never builds it, so no amount of
in-game construction fixes it. Braziers are fire, so it is not even certain that 5 of the 11 can
take a colour at all.

**Ruled 2026-09-17, verbatim:** *"We will add some lights for sure, and they will be irregular.
The player can add more lights. Removing lights below a threshold will anger the gods."*

Three consequences, all binding:

1. **Fixtures are authored into the shipped layout** — the ship arrives with a canvas rather
   than acquiring one. So the canvas is real from the first hour and does not depend on the
   player choosing to build anything.
2. 🔑 **The placement is IRREGULAR, and that is a design requirement, not a licence to be
   sloppy.** A regular grid is the thing being ruled out. This has teeth for §2.6: the
   compositor's territory boundaries and the "front" that moves between two claimants must read
   as moving across an uneven scatter of fixtures, not as a wave crossing a lattice. Anything
   that assumes even spacing is wrong.
3. **The player may add more, and subtraction is punished, not prevented.** Removing fixtures
   below a threshold angers the gods (L17) — so the canvas has a floor defended by consequence
   rather than by a build restriction, which is what keeps L3 true (aboard the Utinni the player
   never *chooses* the scheme) while still letting them own the ship.

⚠️ **Two numbers are still unruled and are owed before Phase 1**: how many fixtures get authored
in, and where the anger threshold sits. Both belong to the build programme, not here.
Tracked as `ATMOSPHERIC_BASE_CANVAS_1`.

### 🔴 C2 — MEASURED: §2.5's rank supplier does not exist

`GameComponent_Ninefold`'s entire public read surface is `GetSatiation`, `GetMood`, `GetBand` and
`IsUnveiled`, plus `ApplyDelta`, `TryFirstContact`, `NotifyViolentDeath` and `Notify_Launched`.
Verified this window.

There is **no loudness, no front, and no change notification** — it is pull-only. So §2.5's "rank
is read, never invented here" is correct as a law and has nothing to read from. Canon rules that
engagement makes a god louder and the loudest is in front; satiation and mood are the engagement,
but the derivation from them to loudness has never been written, and neither has the mid-map flip
or the landing reckoning.

**The law stands and the work moves**: loudness belongs in Ninefold, which owns the pantheon's
state. Tracked as `NINEFOLD_LOUDNESS_FRONT_1`. Until it exists, AtmosphericBase cannot rank
anything, and a compositor built against a rank it computes itself would be a second answer to a
settled question.

### ✅ C3 — RULED and FIXED: the blackout is the referent, and the gods light themselves

A witness used to require an awake colonist **in a lit affected room**, so a blackout was the one
thing a god could never afterwards refer to — backwards, since it is the most dramatic thing the
framework can do.

**Ruled 2026-09-17, verbatim:** *"The blackout IS the thing referred to. The gods REALLY don't
like blackouts. Fix that right now! It becomes absolutely witnessed and referencable once
resolved. And the gods will also be holograms that work by themselves, without power."*

He gave more than the narrow fix. **Fixed in the laws above, same day:**

- §2.7 now tests **presence in an affected group**, not illumination.
- A blackout is witnessed **absolutely**, and is referable **once resolved** — the gods speak
  about the dark after the power returns.
- **L16 is new**: a god's body is a hologram that runs on nothing. This is what makes the
  presence test honest rather than a fudge — there is always something lit to perceive, because
  the god is lit and the blackout cannot touch it.
- **L17 is new**: blackouts anger the gods, which is the same law that punishes stripping
  fixtures (C1). The two rulings turned out to be one mechanic.
- **L9 was narrowed** — it used to say a blackout is simply silence, which read as the gods
  being absent from their own ship whenever the power failed.

🔑 The hologram ruling also *strengthened* an exclusion that was already in §2.1: holograms were
already barred from framework control for being things "whose glow means something else." They
are the gods. The framework must never drive a god's own body.

### ✅ C4 — SETTLED: canon is the fiction, L6 is the rendering

`canon.yml` `in_front` says the silent eight express through flickers in their palettes. L6 caps
the tremor at three, on his ruling that more than that reads as mud.

**Both stand, because they describe different things.** Canon states the fiction: all eight silent
gods are present and pressing on the channel at all times. L6 states the rendering: at most three
are legible at once, and the framework picks which. Neither is wrong and neither needs amending.

⛔ **Do not "fix" either one to match the other.** Raising L6's cap to eight makes mud, which he
ruled out; cutting canon to three makes the pantheon smaller than it is. This paragraph exists
because the mismatch looks like a bug to anyone reading only one of the two files.

*(Put to him 2026-09-17 with the fiction/rendering reading stated; he did not contest it. If he
ever wants it the other way, this is the line to replace.)*

### ⚠️ C5 — the sound half collides with four systems, not one, and beds may not be able to fade

§3 records one accepted overlap (`RustCathedralHum`). The census names **four more ambient systems
in the live list** — `swablu.ambience`, `neronix17.outerrim.core`, `dorbo.watersfx`, and RimTunes'
dynamic music — and reports that `RM_MapComponent_SilenceCue` already carries a Desktop-verified
finding that **Sustainers have no partial volume ramp**. If that holds, beds cannot fade in or out,
only start and stop, which changes what §3's mood-bending can be.

⚠️ Not verified in this window. Added to §8 as an eighth Phase 0 question. Also from the census,
and relevant to L8: `juanlopez2008.lightsout` writes the same glow field the compositor would,
which could make a chosen darkness unprovable.

🔑 **Narrowed 2026-09-17 by L16, but not closed.** The *player-facing* half of "unprovable" is
answered: a chosen dark no longer needs surviving lit fixtures to prove it was chosen, because
the god's hologram is lit through any darkness and needs no power. What remains is purely
technical — two mods writing one glow field is still a collision, and which write wins is still
UNMEASURED from the Mac. That belongs in Phase 0 on the Desktop.

## §10 Still open

Nothing blocks the build programme, but these are unruled:

1. **The nine god signatures** — hue and motion per god, plus the omen looks. An owner sitting
   against the pantheon canon; candidates exist in the scheme catalog.
2. **The Narrator's exact gesture parameters** — how fast the rise, how long the hold, how slow
   the return.
3. **What the tremor's cap of three selects on** — the three loudest, or the three most recently
   changed.
4. **Whether the framework's own showcase ships a demo map** rather than running on a live
   colony.
