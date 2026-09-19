# AtmosphericBase — scheme catalog, DRAFT

**2026-09-16 · RimMandrake tier (campaign-agnostic) · binds nothing.** A creative catalog for the
owner to react to. No defs, no code, no engine claims.

⚠️ **Drafted mid-sitting, and three later rulings from that same evening reach back into it.**
`design/RimMandrake/atmospheric_base_mod_definition.md` is authoritative wherever they differ:

1. **The mod is `AtmosphericBase`, and it drives sound as well as light** — beds, stings and
   acoustic territory, on the same claims. So every scheme here is half a scheme; its acoustic
   half is unwritten.
2. **No hardware ships.** Where an entry says *strobe*, *beacon* or *floor strip*, read "a fixture
   this scheme picked to move fast". Fixtures are taken over by an opt-in button on anything
   already glowing, and the scheme chooses which of them flash.
3. **Full darkness is permitted** — §5's refusal on those grounds was overruled, and the anti-alias
   signal turned out to be motion rather than brightness.

The mod: a framework that takes a colony's or a ship's ambient channels — light and sound — and
animates them on behalf of other mods. A campaign layer (the Utinni) rides on top, in which nine
gods and the Narrator speak through the ship, and the player never picks a scheme himself.

---

## 0. The seven laws this catalog was written under

Owner rulings from today, restated so an entry can be checked against them. Every scheme below was
designed to pass all seven; two candidates could not, and are named in §5 rather than quietly fixed.

1. **Palettes are QUANTIZED** to a small fixed set of discrete colours per scheme. Load-bearing, not
   stylistic — §1.
2. **Two claimants blend BY ALLOCATION, never by colour-mixing.** Each holds real fixtures; the
   boundary between them moves. Claimants beyond two only perturb — "the tremor" — §2.
3. **Brightness is REAL light.** A dimmed ship genuinely darkens: work slows, plants suffer. Every
   entry therefore states **hours** (safe to run indefinitely) or **event** (inherently bounded).
4. **Fast blinking is the expensive axis** and belongs to a few designated fixtures — the mod ships a
   **strobe**, a **wall beacon** and a **floor strip**, and existing lights can be marked. The mass
   moves slowly. A scheme needing everything fast is inadmissible.
5. **Animation runs on REAL time, not game time.** Gestures keep playing while the game is paused.
6. **No power, no lights.** A blackout is silence, not a scheme.
7. **The lights are an output device only.** They never cause world effects. A god that wants raiders
   acts on the world directly.

> ⚠️ **Laws 3 and 7 sit against each other and the owner should settle it.** Brightness *is* a world
> effect — that is law 3's whole point. The reading this catalog assumes: the lights' only effect on
> the world is **illumination itself**, inherent to being a lamp, and they never spawn, summon,
> damage, attract, heal or alter anything else. That is an interpretation, not a ruling.

**How to read an entry.** Name · feeling · **Palette** (P = how many discrete colours) · **Pattern**
(the function of position and time) · **Brightness** · **Rate** (authored target, to be tuned by
LOOKING — not measured) · **Flashers** · **Says** · **Hours/Event** · **Partial** (how it reads
holding only some of the grid).

---

## 1. Quantization is the whole feasibility answer

From `infrastructure/state/items/closed/TWINKLE_FLORA_SPIKE_1.md`: a smoothly interpolated colour mints a
new cached Graphic/Material **forever**, one per distinct float value, never reusing one. That is an
unbounded leak, invisible in a five-minute test and bad after a week of play. Quantizing to a small
fixed step count bounds the cache to exactly that many entries, permanently.

So every palette below is **a small named set cycled** — the way real alarm panels actually work,
which is also why they read as instruments rather than as screensavers. Palettes here run P = 1 to 4.
None needs more.

🔴 **Do not blur two different things.** `TwinkleFloraSpike.cs` is a working quantized glow-pulse
comp and the right prior art for *cadence and quantization discipline* — rare-tick, quantized step,
dirty-only-on-change. But it changes a **plant's SPRITE tint** (via `GetColoredVersion`, whose cache
is the leak named above). DynamicLighting changes **the light a lamp CASTS**. Whether the cast-light
path shares that cache, or has its own, or has none, is a different question with a different answer.

`UNMEASURED — owed a Desktop check:` (a) whether changing a lamp's cast colour routes through the
same colour-keyed Material cache as a sprite tint; (b) whether a colour change alone touches the glow
grid, or only a radius/level change does; (c) what a glow-grid update costs and whether it is scoped
to the fixture's radius; (d) whether an off-tick real-time update hook exists that keeps running
while the game is paused (law 5 depends on it). This is a Mac laptop — no RimWorld install, no def
dump, no decompiler, and RimSage has never connected here. Nothing above was inferred from a doc.

---

## 2. Allocation, and the tremor

Already canon, and stronger than expected. `infrastructure/state/canon.yml` (`in_front`, owner
2026-08-30): the loudest god is IN FRONT and holds the ship's **actuator priority — lights, doors,
subsystem behavior — which is scheduler allocation on the Cradle's substrate, no magic**, read by the
Jawa as favor. And: *"More than one god can be 'active' at a time, though it will move between them,
and the corridors will show this in different colored areas even perhaps that slowly move throughout
the ship."* The silent eight express through *"door hesitations, hum shifts, flickers in their
palettes."*

So allocation is not a compromise the framework makes — it is the fiction, exactly. Two claimants get
territory with a moving boundary. Everything beyond two gets **the tremor**: a faster jitter, a stray
colour at one fixture, an unsettled edge. Each entry's **Partial** line says whether the scheme
survives holding half a ship. The ones that read best partial are the ones with a **front** (a wave, a
trail, a coil) — a front confined to a region reads as the thing being *in that region*. The ones that
read worst are the ones needing a whole contiguous field.

Also canon and worth carrying: divine effects run **on the ship's map only** (attenuation, F2). So the
fixture count this mod ever animates is bounded by a hull, not a planet.

---

## 3. The families

### I. ALARM — the ship telling you something is wrong

Four variants, deliberately distinct instruments rather than four intensities of one. Owner's item (1).

**I-1 · Bloodtrail** — *something is hunting the corridors and it knows the way.*
- **Palette** P=4: `Dark` (near-off) · `Clot` (deep red) · `Blood` (mid red) · `Signal` (hot red).
- **Pattern** A trail head walks the light **adjacency graph** — corridor topology, not Euclidean
  distance, so it goes around walls the way a thing would. Each fixture it touches snaps to `Signal`,
  then decays `Blood → Clot → Dark` over the following few steps: a comet tail. Two or three heads may
  run, and heads bias their walk toward the threat, the breach, or the door being battered.
- **Brightness** Floor is genuinely dark; the trail is nearly the only light. Mean level LOW.
- **Rate** Medium — head advances one fixture per ~0.5–0.8 s; a corridor ring in ~10–20 s. A given
  fixture changes ~4 times as the trail passes, then rests. Looks fast, costs little (§6).
- **Flashers** No. Optionally the beacon nearest the head brightens, to give the trail a nose.
- **Says** Warning **with a direction** — the only scheme here that points. A hunt in progress;
  Ishko's prepared dark turned against the clan.
- **Event.** The mean level is a real work penalty and pawns will path badly in it.
- **Partial** Best in the catalog. A trail existing in only half the ship reads as the hunt being in
  that half, and the boundary reads as the edge of the safe part.

**I-2 · Watchbeat** — *a ship holding its breath in time with you.*
- **Palette** P=2: `Alarm` (red) · `Ward` (dim white).
- **Pattern** Every room flips as a unit between the two, with a **per-room phase offset** so the flip
  sweeps across the deck instead of snapping in unison. Variant for large rooms: adjacent fixtures take
  opposite phase, reading as an alternating grid rather than a flat flash.
- **Brightness** **Constant mean.** The white half carries working light, so total illumination barely
  moves across the cycle. That is the entire point of this scheme.
- **Rate** Slow-medium, ~1.5–3 s per half-cycle. Two changes per fixture per cycle.
- **Flashers** No.
- **Says** Sustained alert. Elevated readiness, a siege underway, "this is not over" — the alarm that
  does not panic. Mob'Unloo's ledger left unbalanced reads well here.
- **Hours — safe.** The only alarm in the catalog that is, by construction, and therefore the one a
  god can hold a whole reign in.
- **Partial** Strong. Half the grid beating red/white against a neighbour's steady palette reads as a
  ship with an argument going on in it.

**I-3 · Standing Red** — *the decision is made; the ship is committed.*
- **Palette** Mass P=1: `Alarm`, held. Flashers P=3: `Alarm` · `Amber` · `Off`.
- **Pattern** **No spatial function on the mass at all** — a flat red field, static. All motion lives
  in the designated fixtures: strobes at door thresholds and the airlock beacon cycle red and amber
  *out of phase with each other*, and the floor strips run a fast chase pointing toward the muster
  point. The stillness of the mass is what makes the flashers read as urgent.
- **Brightness** Flat, moderate. (Red at any level is poor working light — that is a statement, not a
  defect.)
- **Rate** Mass = **zero changes/second**. Flashers = fast, ~2–5 Hz.
- **Flashers** **Required.** This is the flasher showcase, and — see §6 — the *cheapest* scheme here
  despite looking the most frantic.
- **Says** General quarters. Raid inbound, the commitment moment, Sh'kaar's attention arriving.
- **Hours** Tolerable for a long siege (nothing dims), but red is a deliberate mood and work irritant.
- **Partial** Best of the alarms. A red block with amber flashers inside another god's palette reads
  precisely as a quarantined emergency zone.

**I-4 · The Narrowing** — *time is being taken from you and you can watch it go.*
- **Palette** P=4: `Amber` · `Blood` · `Signal` · `Dark`.
- **Pattern** A **shrinking region**: red territory advances one fixture-ring per beat, inward from the
  hull or outward from the threat, converting each ring `Amber → Blood → Signal`. The boundary IS the
  clock — the player reads remaining time off how much ship is left.
- **Brightness** Rises as red territory grows.
- **Rate** Slow — one ring per ~5–15 s; whole gesture 1–5 minutes.
- **Flashers** Optional, and earned: the final ring triggers the strobes.
- **Says** A deadline with a known end. Sh'kaar's inevitability; a demand expiring; a countdown to
  forced launch.
- **Event**, inherently — it terminates. That is its meaning.
- **Partial** Weakest of the four. It needs contiguous territory to read as a boundary; scattered
  allocation turns the clock into noise. Suppress it below some contiguity threshold rather than
  running it badly.

### II. THE LIVING SHIP — the vessel as an animate thing

**II-1 · The Writhe** — *something alive is loose in the walls and it is enjoying itself.* Owner's
item (2), and the most ambitious entry here.
- **Palette** P=4: `Void` (near-off) · `Bile` (dark green) · `Rot` (mid green) · `Sick` (bright
  yellow-green).
- **Pattern** Two or three **coils**. Each coil is a phase-advancing travelling wave along the light
  adjacency graph, but each coil's *path* is a **persistent random walk** — biased strongly to
  continue straight, occasionally turning — so the coils wander, cross, and recombine instead of
  orbiting a fixed centroid. That is what makes it writhe rather than rotate. Where two coils overlap,
  the fixture takes the brightest entry (`Sick`), so crossings **flare** — that is the dance. Every
  fixture is `Void` when no coil is on it, so the base state is black and the green is always a
  moving *body*, never a wash.
- **Brightness** Low mean, bright moving highlights, peaks at the crossings.
- **Rate** Medium — a coil head advances ~2–4 fixtures/sec. A circuit of the ship in ~30–90 s, and by
  construction never exactly repeating.
- **Flashers** **No — and this is a rule, not a preference.** The writhe's life comes from coil
  *geometry*. Hand it to blinking fixtures and it degrades into a fault light.
- **Says** Zizzik awake and fed — glee, malfunction, betrayal in the air. Or Ohm dreaming. Delight,
  of the wrong kind: the scheme should feel like being *inside* something's good mood.
- **Event or a short reign.** Low mean level, and green light on pawns' faces is a strong statement
  that fatigues fast.
- **Partial** Excellent. Coils confined to a region read as an infestation contained to that region,
  and the boundary leaking is exactly right. Best pairing with the tremor of any scheme here.
- ⚠️ **Most expensive mass scheme in the catalog** — many fixtures changing several times per pass,
  plus the overlap rule letting a fixture change on a neighbour's account. §6.

**II-2 · Ohm's Current** — *the machine is thinking and you are standing inside the thought.*
- **Palette** P=3: `Cold` (deep blue) · `Current` (cyan) · `Arc` (blue-white).
- **Pattern** Travelling pulses that follow the **power conduit topology**, not room adjacency — so
  the light moves the way the ship's wiring actually runs, branching at junctions and arriving at
  extremities last. Pulses originate at the reactor/battery bank and propagate outward.
- **Brightness** Steady mid with travelling highlights; barely moves overall.
- **Rate** Medium-slow, a pulse every ~4–10 s, each crossing the ship in a few seconds.
- **Flashers** No, though junction beacons pulsing as a pulse passes is a strong optional detail.
- **Says** Ohm attentive and content. The ship working *well*. Also the correct scheme for research
  completing, a droid coming online, power restored after a brownout.
- **Hours — safe.** Level barely changes; blue-white is decent working light.
- **Partial** Good, and structurally interesting: allocation along a *circuit* rather than a region is
  the natural boundary for this one, which is a different territory shape from every other scheme.
- `UNMEASURED — owed a Desktop check:` whether conduit adjacency is cheaply enumerable at runtime. If
  not, degrade to room adjacency and the scheme still reads.

**II-3 · Spore** — *a stain in the ship that grows while you are not looking at it.*
- **Palette** P=3: `Dim` (low white) · `Bloom` (sickly amber) · `Bright` (yellow).
- **Pattern** Pure **nearest-neighbour spread** from one seed fixture: the region grows a ring at a
  time, holds, then recedes the same way. No wave, no rotation — just a stain with an area.
- **Brightness** Rises with the stain's area, falls as it recedes.
- **Rate** Slow — a ring per ~10–20 s; a full grow-and-recede over minutes.
- **Flashers** No.
- **Says** Something spreading that has not been named yet. Contamination, an infestation, a rumour
  moving through the clan, Zizzik testing a door.
- **Event**, but a long, quiet one — safe for far longer than the Writhe.
- **Partial** Good — a stain bounded by another god's territory reads as containment holding.

### III. HEARTH — the everyday, safe to run for hours

The reigns a god spends most of its time in. These must be *pleasant to live under*, because the
player will live under them; a scheme that is only good for five minutes cannot be a reign.

**III-1 · Fireflies** — *a sleeping ship that is still, quietly, alive.* Owner's item (3).
- **Palette** P=3, and all one hue: `Dim` · `Warm` · `Spark` — only level varies, so this is a
  *brightness* palette rather than a colour one, and mints the fewest cached variants of anything here
  (`UNMEASURED` whether level and colour share a cache path — §1).
- **Pattern** No wave, no structure, no centroid. Each fixture independently sits at `Dim` and, at
  random intervals, rises `Dim → Warm → Spark → Warm → Dim` over a couple of seconds. Optional
  neighbour rule: a spark slightly raises its neighbours' chance for a few seconds after, so sparks
  gently cluster and drift without any explicit wave existing anywhere in the code.
- **Brightness** Low but *steady* mean, with sparks adding a little. See the caveat.
- **Rate** Slow. A given fixture sparks perhaps once per 20–60 s; each spark is a 4-change gesture.
- **Flashers** **No, explicitly.** A firefly that blinks like a strobe is a fault light. If the
  strobes want in, they get one slow lazy spark each and nothing more.
- **Says** Peace. Night watch. A ship at rest and content, the Narrator present but not speaking. Also
  the right neutral for "nobody is loud today" — the pantheon's resting face.
- **Hours — safe, with one real caveat.** Safe *only if* `Dim` sits at or above genuine working-light
  level. Set `Dim` truly dim and this becomes an invisible colony-wide work and plant penalty that no
  player will ever attribute to the lights. **Recommendation:** ship the default with `Dim` at working
  level, and let a *god's* version of Fireflies go darker as a deliberate bane.
- **Partial** Fine but weak — fireflies in half a ship look like fireflies. That makes it the polite
  scheme and the correct default for the silent eight's territory.

**III-2 · Lamplight** — *someone keeps this place, and has for a long time.*
- **Palette** P=3: `Tallow` (warm low) · `Lamp` (warm mid) · `Hearth` (warm high).
- **Pattern** Per-room phase offset on a very slow drift, so each room breathes on its own clock and
  no two rooms are ever quite together. Nothing travels.
- **Brightness** Comfortable mid throughout; the drift is small.
- **Rate** Slow, ~60–180 s per room cycle. Changes per fixture per minute: a handful.
- **Flashers** No.
- **Says** Nothing is wrong. The baseline. This is the scheme the Narrator's signature returns *into*
  most often, and it should be the mod's shipped default for a player who never touches a god.
- **Hours — safe**, and the reference case for "safe".
- **Partial** Reads as ordinary lighting, which is the point — it is the neutral ground any other
  claimant's territory shows up against.

**III-3 · Tidewater** — *the ship breathing slowly, and counting.*
- **Palette** P=4: `Deep` (dark blue-green) · `Ebb` (mid teal) · `Flood` (bright teal) · `Foam` (pale
  green-white).
- **Pattern** A very slow travelling wave along one ship axis, running bow-to-stern and back — a tide,
  not a pulse. The whole grid participates but only the wave front changes at any moment.
- **Brightness** Rises and falls gently with the tide; mean is comfortable.
- **Rate** Slow — a full sweep in 2–5 minutes.
- **Flashers** No.
- **Says** Oomo the Unspilled, content: water held, rationing observed. Reads as discipline rather than
  plenty. A good reign scheme for a lean, well-run ship.
- **Hours — safe.**
- **Partial** Good. A tide that only covers part of the ship reads as the water reaching only so far,
  which is thematically free.

**III-4 · Ledger Gold** — *the books balance and someone is pleased about it.*
- **Palette** P=3: `Brass` · `Gold` · `Coin` (pale bright gold).
- **Pattern** A slow **rotation about the ship's centroid** — a bright arm sweeping like a lighthouse
  beam but taking a minute to come round, so it reads as a slow turning rather than a scan.
- **Brightness** Warm and bright overall; this is one of the more generous schemes.
- **Rate** Slow, ~45–120 s per revolution.
- **Flashers** No; the beacon may take a single gold pulse per revolution as a chime.
- **Says** Mob'Unloo the Ever-Owed, satisfied. Debt paid, a trade concluded well. Delight of the
  respectable kind.
- **Hours — safe**, and actively pleasant.
- **Partial** Good — a rotation clipped to a sector still reads as a rotation.

### IV. NARRATOR — reserved, and not a claimant

**IV-1 · The Butler Rises** — *the lights come up and the world politely waits.* Owner's item (4).
- **Palette** P=2, and deliberately **colourless**: `Held` (bright neutral white) and
  *whatever-was-running*. White is his signature precisely because canon gives him **no mood** — no
  ego, no self-description, no moods-of-the-ship (`canon.yml` `narrator`, owner 2026-08-30) — and he
  owns the voice. The **absence of a palette IS his palette.** No god may be assigned neutral white.
- **Pattern** Three phases, and the middle one is the signature.
  1. **RISE** — a fast nearest-neighbour spread of `Held` outward from the speaker or comm fixture
     nearest whatever is being narrated, reaching the whole grid in under a second.
  2. **HOLD** — flat, and **absolutely motionless**, for exactly as long as the text is up or the voice
     plays. The stillness is the effect: the ship stops gesturing while he talks. Canon backs this —
     he is heard *through the ship's speakers*, a real voice in the world (butler_register, owner
     2026-09-11), so the ship attending to him is diegetic.
  3. **RETURN** — a slow dim from `Held` back into the previous scheme, which resumes **at the phase it
     would have reached had it never stopped**, so a travelling wave does not visibly rewind.
- **Brightness** Rise to bright, hold bright, ease back. A *brightening* is gameplay-harmless where a
  dimming is not — which is why this may fire as often as he speaks, and why it is the only
  event-scheme here with no work penalty at all.
- **Rate** Rise <1 s · hold = the speech · return ~4–8 s. **Real time throughout (law 5): it plays,
  holds and releases while the game is paused.** That is most of its charm.
- **Flashers** **None — and the hold SUPPRESSES them.** A strobe blinking through the butler's hold
  destroys the whole gesture.
- **Says** Attention, and nothing else. The butler has cleared his throat. If it ever reads as a mood,
  a warning or a verdict, it is wrong and should be retuned until it reads as neutral.
- **Event**, bounded by a speech.
- **Partial** **Never partial.** This is the one scheme allowed to preempt the entire grid regardless
  of allocation — because he is not a claimant, he is the voice, and the gods yield the floor.
  **Recommendation:** model it as a **preemption layer above allocation**, never as a competitor for
  territory. Reserve it: nothing else in the mod may use flat neutral white held still.
- ⚠️ **The one hazard.** It visually cancels an alarm. A raid alarm going white-and-still for six
  seconds while the butler quips is a legibility risk with real gameplay cost. Three options for the
  owner: (a) exempt the ALARM family from preemption entirely; (b) let flashers alone keep running
  when the underlying scheme is an alarm; (c) accept it as a dramatic beat and let the raid land.

**IV-2 · The Aside** — *he is muttering to himself, not addressing the room.*
- Subordinate variant for the lore-leak lines that do not deserve a full hold. **One** fixture — the
  nearest, or a single beacon — rises to `Held` and dims back over a few seconds. The rest of the ship
  keeps running its scheme untouched. P=2, no flashers, no preemption, real time, harmless.
- **Says** A remark. Use it for the history the player has not learned yet, where a full hold would
  over-announce it.

### V. PROCESSION — transitions, arrival, departure

**V-1 · Handover** — *the ship changes hands and you can watch the border move.*
- **Palette** P = the two claimants' palettes, unchanged. This scheme has no colours of its own.
- **Pattern** **The canonical allocation gesture**, and the one the framework should demonstrate
  itself with: the incoming palette's territory advances across the ship as a moving boundary,
  fixture-ring by fixture-ring, displacing the outgoing one until it holds the share it has won. The
  boundary is deliberately ragged, and it may stall, back up a ring, and push again.
- **Brightness** Whatever the two schemes carry; the transition itself adds nothing.
- **Rate** Slow — 30–90 s for a full handover. It should be long enough for a player to notice mid-task
  and walk over to look.
- **Flashers** Inherited from whichever side owns each flasher at the moment.
- **Says** The front has changed. Canon reckons the front at each landing and on a violent mid-map
  swing (a massacre, a great feast, a betrayal) — this is the sound of that happening.
- **Event.**
- **Partial** It *is* the partial case, made visible.

**V-2 · Landfall** — *we are down, and the ship is opening.*
- **Palette** P=3: `Dust` (dim warm) · `Sun` (warm mid) · `Open` (warm bright).
- **Pattern** Light rolls **inward from the hull**, ring by ring, arriving last at the core — the
  inverse of every alarm's direction, which is why it reads as welcome rather than threat.
- **Brightness** Rises from low to comfortable across the gesture and stays.
- **Rate** Medium — the whole roll-in over ~10–20 s.
- **Flashers** Airlock beacon takes a slow triple pulse as the doors release.
- **Says** Arrival. A new map, a landing survived, the gods' reckoning concluded and not badly.
- **Event**, and it ends by handing off to a Hearth scheme.
- **Partial** Good; a partial landfall reads as only part of the ship waking up, which is a fine thing
  for a contested landing to mean.

**V-3 · Unmooring** — *the ship is leaving and did not ask.*
- **Palette** P=3: `Slate` (cold dim) · `Steel` (cold mid) · `Flare` (cold bright white).
- **Pattern** Repeated travelling waves sweeping toward the **thrust axis** — every wave in the same
  direction, each faster than the last, so the ship reads as accelerating. Never reverses.
- **Brightness** Rising through the sequence, peaking at launch.
- **Rate** Starts slow (~8 s per sweep), compresses to ~1 s by the end. Whole gesture 30–60 s.
- **Flashers** **Yes, in the last third only** — floor strips chase toward the bow, beacons hard and
  fast at the end. Earned escalation rather than a constant.
- **Says** Ta'Baa the Unrooted taking the ship. Canon's image is exact: *"with a wave the ship
  launches of its own accord yet again, out of pilot control."* This is that, in light.
- **Event.**
- **Partial** Fine — Ta'Baa holding only part of the grid and launching anyway reads as a god acting
  over objections, which is correct.

### VI. MOURNING — grief, shame, vigil

**VI-1 · Ashfall** — *the ship is grieving and does not care to hide it.*
- **Palette** P=4: `Soot` (near-off) · `Ash` (grey) · `Pale` (grey-white) · `Bone` (dim warm white).
- **Pattern** A slow **downward** travelling wave — bright at the top of the deck plan and falling,
  fixture row by fixture row, endlessly. Falling, never rising: the direction is the grief.
- **Brightness** Low mean, and here that is the *statement*: the ship is dimmer while it mourns.
- **Rate** Slow, a fall taking ~20–40 s, repeating.
- **Flashers** No. A flasher in a grief scheme is a joke.
- **Says** Ozzik the Shamed. Grief, a death that mattered, a shame the clan has not answered.
- **Event, or a bounded reign with a floor.** Because the level is a real penalty, a god holding this
  for days is a genuine bane — which is good design and needs an explicit cap so it cannot become a
  silent death spiral the player never diagnoses.
- **Partial** Good — mourning confined to one quarter of the ship reads as a wake in a room.

**VI-2 · The Long Dim** — *the ship has stopped caring whether you can see.*
- **Palette** P=2: `Ember` (very low warm) · `Dark` (near-off).
- **Pattern** Almost none, deliberately. Fixtures drop to `Ember`; a slow random subset falls to `Dark`
  and comes back. Nothing travels, nothing sweeps.
- **Brightness** The lowest in the catalog and **the single most gameplay-consequential entry here.**
- **Rate** Very slow. Changes per fixture per minute: near zero.
- **Flashers** No.
- **Says** Wrath by neglect — a god that has stopped attending rather than one that is angry at you.
  Colder than Ashfall, and worse.
- **Event, and it MUST be capped.** Left running it is a colony-wide work and plant penalty with no
  visible cause. **Recommendation:** hard duration ceiling in Mod Settings, plus a floor that keeps
  `Ember` above pitch dark — see §5 for why it may never reach zero.
- **Partial** Reads well and is genuinely unsettling next to a lit neighbour: half the ship abandoned.

**VI-3 · Nine Candles** — *a vigil, and everyone knows the count.*
- **Palette** P=2: `Candle` (warm bright) · `Ember` (very low warm).
- **Pattern** **Static.** Exactly nine fixtures — chosen for spread, one per compartment where
  possible — hold `Candle`; every other fixture holds `Ember`. Nothing moves at all. When a god is
  being mourned or has withdrawn, its candle goes to `Ember` and the count visibly drops.
- **Brightness** Low overall with nine bright points.
- **Rate** **Zero** in steady state. It only changes when the count does.
- **Flashers** No.
- **Says** Ritual. A rite in progress, a reckoning being held, the pantheon assembled. And it *counts*
  — the player learns to glance at the number, which makes it the most readable scheme here.
- **Event**, though cheap enough and low enough to hold through a whole rite.
- **Partial** Distinctive: fewer candles than nine because another claimant holds those fixtures reads
  as gods absent from the vigil. Accidentally perfect.

### VII. OMEN — attention, dread, the tell

**VII-1 · The Prepared Dark** — *you are being watched from inside your own ship.*
- **Palette** P=3: `Dark` (near-off) · `Coal` (very dim red) · `Eye` (dim red).
- **Pattern** A single narrow **sightline** rotates slowly about a centroid — one line of fixtures at
  `Eye`, its neighbours at `Coal`, everything else `Dark`. Not a sweeping searchlight: a slow turn of
  attention, and it sometimes stops and holds on a bearing for a while before resuming.
- **Brightness** Very low. Dread is cheap in light and expensive in gameplay.
- **Rate** Slow — a revolution in 2–4 minutes, with pauses.
- **Flashers** No. Ishko does not blink.
- **Says** Ishko the Unmaskable, attentive. Ambush prepared — yours, or someone's on you.
- **Event.** Level too low to hold for long without a work cost.
- **Partial** Excellent, and better partial than whole: a sightline that only exists in the dark half
  of the ship is the best version of this scheme.

**VII-2 · Searing** — *there is too much light and it is not kind.*
- **Palette** P=3: `Glare` (white-hot) · `Bleach` (pale yellow-white) · `Sun` (harsh yellow).
- **Pattern** The whole grid rises together, then a slow high-amplitude pulse of the *entire field* at
  once — no travel, no front, nowhere to stand outside it. Occasional brief drops to `Sun` that read
  as the light gathering itself for more.
- **Brightness** **Above** normal, and rising. Notable as the only scheme whose gameplay pressure is
  not a dimming — bright light is not a work penalty, so this one is an *assault on the player's eye*
  rather than on his colony's output. Whether that is enough of a bane is an owner call.
- **Rate** Slow pulse, ~10–20 s per cycle. Few changes per fixture.
- **Flashers** No, and it would be wrong: Sh'kaar is not a strobe, he is an excess.
- **Says** Sh'kaar the All-Searing, pleased — which is bad news. Exposure, killing light, attention
  from the wrong god.
- **Hours — technically safe** (no dimming, no penalty), which makes it a nastier long reign than the
  dark ones: unpleasant without being measurable. Flag for the owner as possibly *too* comfortable.
- **Partial** Weakens badly. Its power is having nowhere outside it, so at half the grid it is just
  bright. **Recommendation:** require a large allocation share, or suppress it below one.

**VII-3 · The Tell** — *the ship is calm and something in it is not.*
- **Palette** P = the host scheme's palette **plus exactly one foreign colour** — the intruding god's
  signature, and only one.
- **Pattern** This is **the tremor made into a scheme of its own**, and canon named it first: the
  silent eight express through *"flickers in their palettes."* An otherwise ordinary Hearth scheme
  runs untouched, and at long random intervals a single fixture takes the foreign colour for a beat and
  returns. Rarely two at once. Never a pattern, never a front — the player is never sure they saw it.
- **Brightness** The host's, unchanged.
- **Rate** Very slow and stochastic — one fixture, once every ~30–120 s.
- **Flashers** No, though a *single* out-of-place beacon blink is the strongest version of this.
- **Says** A third, fourth or fifth claimant is present and has no territory. Also the best available
  foreshadowing channel: the colour that keeps appearing is the god about to take the front.
- **Hours — safe**, and it is the intended always-on layer rather than a standalone scheme.
- **Partial** It is *made of* partial. It has no territory by definition.
- 🔑 **Design note:** this doubles as the framework's answer to "more than two claimants". Rather than
  a fourth god getting a thin slice nobody can read, it gets the tell — which is more legible *and*
  cheaper than any slice would be.

---

## 4. What the families are for, in one line each

| Family | Count | Role |
|---|---|---|
| I. Alarm | 4 | Something is wrong. One of them (Watchbeat) is safe to live in. |
| II. The Living Ship | 3 | The vessel is animate. Highest cost, highest impact. |
| III. Hearth | 4 | The reigns. Safe for hours, pleasant to live under. |
| IV. Narrator | 2 | Not a claimant. Reserved neutral white, preempts everything. |
| V. Procession | 3 | Transitions: the front changes, arrival, departure. |
| VI. Mourning | 3 | Grief and withdrawal. The gameplay-expensive family. |
| VII. Omen | 3 | Attention and dread, plus the tremor channel itself. |

**22 schemes.**

---

## 5. Two candidates I could NOT make admissible

Reported rather than quietly redesigned, per the house rule about grading your own work.

**REFUSED · Whiteout** — every fixture on the ship strobing hard and out of phase, a total sensory
break. It fails law 4 and cannot be rescued: its entire content is *every* fixture moving fast, so
handing the speed to a few designated flashers does not produce a weaker version of it, it produces a
different scheme (which already exists — Standing Red, I-3). Dead, not deferred.

**REFUSED · Total Dark** — the mourning family taken to zero: every fixture off, the ship silent. It
fails law 6 in a way I did not expect and that is worth the owner's attention: **it is
indistinguishable from an actual blackout.** A scheme that cannot be told apart from a power failure
cannot carry meaning — the player will read a god's deepest statement of grief as a battery problem
and go check the conduits. So the Mourning family **floors at `Ember`** (VI-2) and never reaches zero,
and that floor is a semantic requirement, not a brightness preference. A corollary worth ruling on:
**the framework should probably never drive a fixture fully off in a scheme where neighbours are also
off**, precisely so darkness stays the exclusive vocabulary of law 6.

---

## 6. Cost — the formula, and which schemes sit where

**No measured numbers appear here. None can: this is a Mac laptop with no RimWorld install, no def
dump and no decompiler, and RimSage has never connected here.** What follows is the shape of the cost
and the constants that must be measured on the Desktop before any of it is a number.

### The terms

Let, on one map (bounded by the hull — attenuation, F2):

- **L** — fixtures under the mod's control
- **F** — designated fast fixtures (strobe, beacon, floor strip, marked existing), `f = |F|`
- **M** — the mass, `m = L − f`
- **r_m** — mean colour-changes per second *per mass fixture*, averaged over the cycle
- **r_f** — the same, per flasher
- **k** — cost of one colour change on one fixture · `UNMEASURED`, and the dominant unknown
- **b** — brightness/level changes per second across the grid
- **g(ρ)** — cost of one glow-grid update for a fixture of radius ρ · `UNMEASURED`, and plausibly
  area-scoped, i.e. growing with ρ²
- **P** — distinct colours in the scheme's palette (1–4 throughout this catalog)
- **V** — distinct fixture graphics using that palette

**Steady-state cost per second:**

```
cost/sec  ≈  m · r_m · k   +   f · r_f · k   +   b · g(ρ)
             \___mass___/      \_flashers_/       \_light_/
```

**Bounded one-time memory (NOT per second):**

```
cached variants  ≈  P · V        — constant, forever, because palettes are quantized
```

Unquantized, that second formula has no bound: it grows with elapsed play time and never stops. That
is the leak `TWINKLE_FLORA_SPIKE_1` documents, and the reason law 1 exists.

### The structural insight

🔑 **`r_m` is not the scheme's apparent speed.** A travelling wave that visibly crosses the whole ship
in ten seconds changes each fixture only about P times *as the front passes*, and leaves it alone the
rest of the cycle. So **apparent motion is nearly free**, and what actually costs is the number of
distinct transitions each fixture makes per second. Cost tracks the size of the **front**, not the
size of the grid. That is why the frantic-looking schemes here are cheap and the slow-looking Writhe
is not.

### Cheapest → most expensive

1. **Nine Candles** (VI-3) — static, `r_m = 0`, `b = 0`. Free in steady state.
2. **Standing Red** (I-3) — mass `r_m = 0`; cost is `f · r_f · k` with `f` small by construction. The
   fastest-*looking* scheme in the catalog is close to its cheapest. This is what law 4 buys.
3. **The Butler Rises** (IV-1) — a bounded burst, then `r_m = 0` through the hold. Near-free while
   held, which is why it can fire on every line he speaks.
4. **The Tell** (VII-3) — one fixture, occasionally. Cheaper than any territory slice would be, which
   is an argument for the tremor beyond the aesthetic one.
5. **Lamplight · Ledger Gold · Tidewater · The Long Dim** (III-2, III-4, III-3, VI-2) — low `r_m`,
   slow cycles. The Long Dim is cheap in *computation* and by far the most expensive in *gameplay* —
   two different axes that must never be conflated.
6. **Fireflies** (III-1) — low `r_m`, but every fixture is an independent stochastic source, so there
   is no coherent front to bound the work. `cost ≈ m · (sparks/sec) · (4 changes per spark)`. Still
   low; just structurally different from the wave schemes.
7. **Watchbeat** (I-2) — two changes per fixture per cycle across all of `m`. Moderate, and predictable.
8. **Front-scoped waves** — Bloodtrail, Handover, Landfall, The Narrowing, Ashfall, Spore, Ohm's
   Current, The Prepared Dark. `r_m ≈ P / (pass period)`, and only front fixtures change at all.
   Moderate, and each scales with front size rather than `L`.
9. **Unmooring** (V-3) — a wave whose period compresses, so `r_m` rises through the gesture, plus
   flashers in the last third. Peaks near the end, by design.
10. **The Writhe** (II-1) — **the most expensive.** Several coils, many fixtures changing several times
    per pass, and the overlap rule lets a fixture change on a *neighbour's* account. If any scheme
    needs a measured budget before shipping, it is this one.

**Sitting outside the ranking:** any scheme with a real brightness envelope adds `b · g(ρ)`, and
**if glow updates are area-scoped, that term may dominate everything else in the formula.** Searing,
Landfall, Ashfall, The Long Dim and The Narrowing are the exposed ones. `UNMEASURED` — and it is the
first thing to measure, because it could reorder this entire list.

---

## 7. UNMEASURED register — owed a Desktop check

Every engine-dependent assumption in this document, in one place.

1. Whether a lamp's **cast-light colour** routes through the same colour-keyed Material cache as a
   sprite tint (§1). Law 1 is prudent either way; the *magnitude* of the leak depends on this.
2. Whether a **colour** change alone touches the glow grid, or only a level/radius change does.
3. The cost of one glow-grid update, and whether it is **area-scoped** (§6 — could reorder the ranking).
4. Whether an **off-tick real-time update hook** exists that keeps running while the game is paused.
   **Law 5 depends entirely on this**; if it does not exist, every gesture here degrades to game time
   and the pause behaviour the owner asked for is not available.
5. Whether **power-conduit adjacency** is cheaply enumerable at runtime (II-2; degrades gracefully).
6. Whether **level** and **colour** share a cache path (III-1's claim to be the cheapest palette).
7. The count of colour-adjustable fixtures on a real Utinni — that is the player's build, not a
   constant, and `L` should be read at runtime rather than assumed anywhere.

---

## 8. What the owner should rule on

1. **Laws 3 vs 7.** Is "illumination is the lights' only world effect" the right reading? (§0)
2. **The Butler's preemption vs alarms.** Exempt the alarm family, exempt only the flashers, or accept
   the beat? (IV-1)
3. **Fireflies' `Dim` default.** Working level by default with darker reserved as a god's bane, as
   recommended? This is the difference between a beloved ambient scheme and an undiagnosable colony
   penalty. (III-1)
4. **Duration ceilings on Mourning.** The Long Dim and Ashfall need caps, or they become silent death
   spirals. (VI-1, VI-2)
5. **Searing may be too comfortable.** It is the only unpleasant scheme with no mechanical cost — is
   an assault on the player's eye a sufficient bane for the evil sun god? (VII-2)
6. **Reserving neutral white.** No god may ever be assigned flat neutral white, so the Narrator's
   signature stays unambiguous. (IV-1)
7. **Never fully dark.** Confirm that no scheme drives neighbouring fixtures fully off, so darkness
   remains the exclusive vocabulary of law 6. (§5)
8. **Suppression thresholds.** The Narrowing and Searing read badly below some allocation share.
   Suppress-and-substitute, or run them degraded? (I-4, VII-2)
