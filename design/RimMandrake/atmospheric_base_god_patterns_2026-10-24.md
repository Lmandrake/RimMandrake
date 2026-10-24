# AtmosphericBase: god patterns (2026-10-24)

**Design only. Binds nothing until the owner rules.** It answers owner decision 2 of
`atmospheric_base_review_package_2026-10-24.md` §9, his words as recorded: *"The various gods should [be]
associated with many such patterns. In the [Utinni]-aligned version they will be player settings."*

## 0. Sources and status

- Grammar candidates: package §6 (A tides, B update-on-change, C drawn layer); the GPT review's five novelties
  (`atmospheric_base_review_package_2026-10-24.gpt_review.md:23-29`); catalog schemes (`atmospheric_base_scheme_catalog.md`).
- The Nine: forms and moods are canon in `design/Jawa/divine_satiation_engine.md` §2.0b (~line 750) and
  `nine_voices_cast_bible.md` §2. Accent hues are BENCH motifs (`design/Jawa/art/gods/god_render_prompt_spec.md:37-56`).
  **Every RGB value, pattern choice and anchor below is a proposal (inference)** for the owner sitting the definition
  reserves (`atmospheric_base_mod_definition.md` §4: "the nine signatures ... are an owner sitting, not agent work").
- Built today: `Steady`, `RoomBreath`, `Sparks`, flashers, the tremor, the wedge territory
  (`src/RimMandrake/AtmosphericBase/Source/Kernel/RM_SchemeKernel.cs:18-24`, `RM_TerritoryKernel.cs`).
- Honoured: L4 quantised palettes (at most 8), L5 allocation not mixing, L8 darkness carries motion, L11 and decision 5
  (one white token, near-white banned), decision 4 (drawn layer only for embers in black and the Narrator wash),
  decision 10 (reload restarts gently), aesthetics first, gentle by default, decision 11 (no accessibility planning).

## 1. Pattern grammar

A **pattern** is a stack of **layers**. Each layer is one **primitive** with params, a scope and a palette slice; it
returns a palette *index* (never a colour) or "pass". Layers combine by `over` (top non-pass wins) or `max` (higher index
wins: flaring crossings). **Phrase modifiers** reshape a layer in time or space. Nine primitives and four modifiers
cover every catalog scheme and every god below.

**Strip legend** (rows = fixtures or rooms, columns = time): ` ` black, `.` ember (dim, nonzero), `-` low, `+` mid,
`#` high, `x` a foreign god's colour.

**Cost classes** under engine B (cost scales with changes; T = taken fixtures). Rates are arithmetic for T = 200 at
about 10 fixtures per room (inference), not measurements. Today's loop is O(T) every 6 frames for all of them alike.
- **S** still: zero events at steady state. **L** light: T x changes-per-cycle / period, bursts at most one room.
- **F** front: events scale with front size x speed, not with T. **H** heavy: many heads; needs B's per-frame write
  budget, and aliases on the 10 Hz loop (K6). **D** drawn: per-frame draw cost while active (unmeasured); decision 4 only.

### 1.1 Primitives

**P1 BREATH** (built: `RoomBreath`). Each scope unit walks the palette up and back on its own phase. Params `period` s,
`scope` room | group | field (field = all in sync), `phaseSpread` 0-1. Cost **L**: T(2P-2)/period = 200x4/120 s =
6.7 events/s. A `field` scope bursts the whole territory at once and needs the B budget.
```
R1  - + # + - + # + - + # +     scope=room, phaseSpread=1
R2  # + - + # + - + # + - +
```
**P2 SPARK** (built: `Sparks`). Each fixture rests at [0] and at random slots rises and falls. Params `slot` s, `oneIn`,
`rise` s, `neighbourLift` (>0 raises neighbours' odds briefly, so sparks drift in clusters, catalog III-1).
Cost **L**: T(2P-2)/(oneIn x slot).
```
F1  - - - + # + - - - - - -
F2  - - - - - - - - + # + -
```
**P3 TIDE** (proposal A). A front through the room-and-door graph from an `anchor`; a threshold θ(t) oscillates between
bounds, with hysteresis and stable tie-breaks (GPT: so equal-distance rooms do not flip together). Params `anchor`
shrine | medoid | core | threshold | open | power | grandest, `period` ≥ 240 s, `ragged` 0-0.2, `hysteresis`.
Cost **F**: about 2 x band / period = 200/900 s = 0.44 events/s. It is both a **territory shape** and a layer (Tidewater).
```
room by door-distance from anchor ->   A  1  2  3  4  5
t=+120s                                #  #  #  #  +  -     then it ebbs back
```
**P4 RIPPLE.** A ring out from (or in to) a seed by graph distance. `fill` = shell (a thin ring: a rise, a landfall) or
bloom (area grows, holds, recedes: Spore). Params `seed` fixture | anchor | hull, `direction` out | in, `speed` hops/s,
`width`, `hold` s, `repeat` s (0 = one-shot). Cost **F** running, **S** held. A Narrator rise over 200 fixtures in 0.8 s
is a 250 events/s burst; the B budget caps it near 50 per frame.
```
F1(seed) # # + - - -      fill=shell, out
F2       - # # + - -
```
**P5 SWEEP.** A wave along a direction field: `axis` (Ashfall falling, Unmooring), `turn` (rotation about a centre:
Ledger Gold, the Prepared Dark sightline, the wedge) or `toward` (down a distance field, e.g. nearest exterior door).
Params `field`, `period`, `width`, `pauseChance`/`pause` s (the sightline that stops and holds), `accelerate`. Cost **F**.
```
F1(far)  # + - - # + - - # +     field=toward exits: every wave runs outward, never back
F3(door) - - # + - - # + - -
```
**P6 PROCESSION.** k heads move along a path graph, each with a tail. Params `graph` rooms | adjacency | conduits,
`heads`, `hop` s, `dwell` s, `step` walk | jump (vanish, reappear elsewhere), `tail`, `overlap` (the next lamp lights
before the last goes out: GPT novelty 5), `trace` 0 | +1 (a visited lamp keeps one step up), `pair` (two adjacent heads
as one). In true black the head is an **ember**: real grid light at the dim nonzero entry, and the drawn layer may add
a glow travelling between fixtures (decision 4). Cost **F**, independent of T: 1 head, tail 2, hop 0.6 s = 5 events/s.
```
F1  . # + .                 heads=1, tail=2, overlap: the "dark procession"
F2    . # + .
```
**P7 COIL** (catalog II-1, the Writhe). 2-3 travelling waves on persistent random walks; crossings take `max` and
flare. Params `coils`, `hop` s, `turnChance`, `length`. Cost **H**: 3 coils x 4 changes / 0.3 s = 40 events/s plus
crossings. Never exactly repeats, by construction.
```
F1  # + - . . . . - + # # +
F2  + # + - . . - + # # + -     two coils crossing flare to #
```
**P8 TELL** (built: the tremor, catalog VII-3). One fixture takes a foreign entry for a beat, then returns. Params
`interval` s, `beat` s, `cap` (L6: at most 3 claimants; integer cap for small fleets, 1 when T ≥ 8, else 0, per GPT's
4%-of-11 point). Cost **L**: about 0.1 events/s.
```
F1  + + + x + + + + + + + +     the stray colour, once; the player is not sure he saw it
F2  + + + + + + + + x + + +
```
**P9 COUNT** (catalog VI-3, Nine Candles). A marked set of n fixtures (spread: one per room where possible) holds one
entry, the rest another; changes only when n or membership changes. Params `n`|`perRoom`, `markEntry`, `restEntry`,
`pick` spread | brightest | nearestAnchor, `tremble` (marked fixtures alternate two adjacent entries every 0.8-1.5 s:
Oomo's droplet), `accumulate` (add one marked fixture per `beat` until the room is full, then clear: a tally).
Cost **S**; **L** with `tremble` or `accumulate`.
```
room, accumulate, beat=8s:   - - - - | # - - - | # # - - | # # # - | # # # # | - - - -
```

### 1.2 Phrase modifiers (GPT novelties 1-4; novelty 5 is P6 in black)

**M1 ECHO** (call-and-response). A second group replays the layer after `delay` s, optionally `invert`ed; the wing
nearest the caller answers first. Cost x2. GPT's risk is conspicuous synchrony, so `delay` jitters ±20%.
```
wing A  - + # + - - - - - - + #
wing B  - - - - + # + - - - - -     delay = 4 steps
```
**M2 APPROACH** (approach-pause-withdraw). Envelope on a front primitive (P3-P6): advance `reach` hops, hold `pause` s,
withdraw. Invitation withdraws slowly; warning withdraws fast. Cost: the layer's own.
**M3 SCAR.** A fixture that changes hands keeps the previous owner's rhythm on its lowest entry for `linger` s (short
history buffer, +2 events per transfer). GPT's risk is muddled ownership: `linger` ≤ 30 s, except Rekko (§2.5).
**M4 HUSH** (listening hush). A room's layers slow and narrow to one held mid entry over `settle` s, hold, recover.
Triggered only by a consumer's witness-gated event (L14). Not the Narrator's HOLD (that is white and ship-wide; a hush
is coloured and one room). A dark room keeps one ember breathing under a hush (L8).

### 1.3 Territory shapes (now per god)

`WEDGE` (built: rotating sector about the centroid); `TIDE(anchor)` (P3 as the boundary, needs A); `CIRCUIT` (P3 over
the conduit graph; conduit adjacency cost is UNMEASURED, catalog II-2; falls back to `TIDE(power)`). Each god names one
shape plus `ragged`, `minShare`, `hysteresis`. When the two front gods' shapes differ, see Q4.

## 2. Pattern library: the Nine (proposals for the owner sitting)

Each god has three **readings**: *resting* (the reign; pleasant for hours), *pleased*, *angry*; the campaign maps
satiation bands and L17 anger onto them. Identity rides hue **and** motion (definition §4), so each primary motion is
unique (§2.10). Palettes run low to high; RGB is to be judged by eye on real floors (GPT: RGB distance proves nothing).

### 2.1 Ishko the Unmaskable: the eyes in the dark
- **Palette** `Black (0,0,0)`, `Smoulder (26,10,4)`, `Coal (64,26,8)`, `Eye (205,98,24)`. Canon form: "a pair of
  glowing orange eyes in the dark"; BENCH accent near-black.
- **Primary: THE EYES**: P6 with `pair`, `step=jump`, `dwell` 8-20 s; they open, stare, close, open elsewhere. Under it
  P1 BREATH `field` Smoulder-Coal, period 300 s, the slowest of the Nine. **Territory** `TIDE(core)`: farthest from any
  exterior door. He holds the inside.
- **Resting**: Coal rooms breathing almost imperceptibly, one pair of eyes per territory. **Pleased**: true black, eyes
  rarely open; the drawn ember layer carries the writhe; the stillest legal look in the mod. **Angry**: the Prepared
  Dark sightline (P5 `turn`, Eye, pauses), and every room's eyes open and close together, one long stare.
- *Why*: two warm points in black is the oldest horror image and exactly his canon form; near-zero motion is his
  character ("Ishko does not blink", catalog VII-1).

### 2.2 Ohm the All-Current: the current in the wire
- **Palette** `Cold (18,40,112)`, `Current (40,150,212)`, `Arc (150,205,255)`. BENCH accent arc-blue.
- **Primary: CURRENT**: P6 on `graph=conduits`, heads spawned at power sources every 4-10 s, `hop` 0.15-0.3 s, tail 2;
  **M1 ECHO** at junctions. **Territory** `CIRCUIT` (fallback `TIDE(power)`): what the wiring reaches.
- **Resting**: Cold mass, occasional pulses; decent working light. **Pleased**: regular pulses; a machine waking is a
  P4 RIPPLE of Arc out of that fixture. **Angry** (blackout, droid scrapped): pulses stall halfway and run back to source
  (M2, fast withdraw); one junction stutters as a flasher.
- *Why*: light following the real wiring makes the ship's anatomy visible: the living machine shown as current, not as
  a face (cast bible: he never speaks as the hull).

### 2.3 Oomo the Unspilled: the tide and the droplet
- **Palette** `Deep (14,52,60)`, `Ebb (40,110,120)`, `Flood (90,170,170)`, `Bead (170,216,206)`. BENCH accent water-silver.
- **Primary: THE DROPLET**: P9, n = 1 per room, `tremble` Bead/Flood; trembles, never falls (canon: "a single trembling
  droplet that never falls"). Under it P5 SWEEP `axis` (catalog Tidewater), a 3-5 min tide. **Territory**
  `TIDE(medoid)`; anchoring on water sources would need a consumer group (inference).
- **Resting**: slow tide, one droplet per room. **Pleased**: after each tide the droplets pulse once per family member,
  capped at 9 (canon: "counts the family aloud"); optional, the count is consumer-supplied. **Angry** (thirst): the
  mirage, a P4 bloom running *inward* that pulls the lit area back to one room, leaving Deep, with a shimmering edge.
- *Why*: water reads as slow and patient; the bead is a tiny constant tension; the receding mirage is his canon form.

### 2.4 Mob'Unloo the Ever-Owed: the tally
- **Palette** `Verdigris (30,82,60)`, `Copper (172,92,40)`, `Coin (232,172,82)`. BENCH accent copper/green.
- **Primary: THE TALLY**: P9 `accumulate`: per room one lamp at a time steps to Coin on a **strict** 8 s beat; when full,
  all return together. The only god on an exact metre (no jitter, ever). **Territory** `WEDGE`, `ragged = 0`: the ledger
  column, the cleanest boundary in the mod. This gives the built wedge a meaning instead of retiring it.
- **Resting**: tallies filling and clearing. **Pleased** (debt paid): the full tally chimes; the territory steps to Coin
  for one beat. **Angry** (unpaid): an unbalanced entry, one lamp per room held at Copper off the beat, and the tally
  restarts one short each time.
- *Why*: accounting made visible; the strict beat sets him apart from every organic god; an unpaid line needs no words.

### 2.5 Rekko of the Second Hand: the mender
- **Palette** `Patina (60,44,26)`, `Bronze (150,100,50)`, `Burnish (200,146,74)`. BENCH accent salvage-bronze. Burnish
  is near vanilla amber, so his identity rides on motion (Q2).
- **Primary: THE MENDING**: P6, one head, `step=walk`, `dwell` 6 s, `trace=+1`: a slow visitor goes lamp to lamp, each
  left one step warmer, until the room is whole; it then sleeps one step back over minutes and the walk resumes.
  **M3 SCAR** is his: a lamp he wins keeps its previous owner's colour for minutes ("I keep what was").
  **Territory** `TIDE(shrine)`, falling back to medoid.
- **Resting**: the mending walk. **Pleased** (a restoration): the restored room is mended at once and holds. **Angry**
  (a repairable thing scrapped): the unmending, his lamps return to Patina one by one in reverse order, and one lamp per
  room stays at Patina: the missing thing.
- *Why*: the only comforting god gets the only pattern that *improves* a room as you watch; grief reads slowly.

### 2.6 Ta'Baa the Unrooted: always toward the door
- **Palette** `Dusk (70,70,82)`, `Wind (128,130,140)`, `Dawn (220,170,92)`, `Horizon (250,202,112)`. BENCH wind-grey/gold.
- **Primary: OUTWARD**: P5 SWEEP `toward` the nearest exterior door, period 20-40 s; waves only ever run outward; the
  quickest gentle god. **Territory** `TIDE(threshold)`: the rim. With Ishko on `core`, the two meet *at the threshold*,
  as canon has it ("tolerates Ishko only at the threshold, hand in hand").
- **Resting**: wind-grey waves leaving. **Pleased** (a launch): Dawn waves flaring Horizon at the door, then the
  catalog's Unmooring accelerating to the thrust axis. **Angry** (rooted too long): waves run to the door, **pause**,
  come back (M2), quickening.
- *Why*: direction is meaning: light that always leaves feels like hope; light pacing at a door says "we stayed too long".

### 2.7 Zizzik the Spark-Maker: the wrong spark
- **Palette** `Void (0,0,0)`, `Bile (22,52,10)`, `Rot (72,140,30)`, `Sick (182,232,62)`. BENCH accent spark-green.
- **Primary: THE WRITHE** (P7 COIL, `max` crossings) when awake. Asleep (canon's slumber clock) he is almost nothing: a
  P8 TELL in his own territory, one lamp twitching wrong about once a minute. **Territory** `TIDE(medoid)`,
  `ragged` 0.2 and islands allowed: he infiltrates rather than holds.
- **Resting**: asleep, the gentlest god by accident. **Pleased** (awake, fed): the Writhe. **Angry**: wrong sparks, P2
  with irregular rises and entry jumps (Void to Sick, nothing between), 1-2 irregular flashers. **MIMIC**, his alone:
  for 20-40 s he plays a rival's pattern in his green at the wrong tempo, then drops it (cast bible: "does flat
  impressions of the others, badly"); a scheme switch, not a new primitive.
- *Why*: the most alive pattern for the god of glee; sleeping and waking give the player a rhythm of dread.

### 2.8 Sh'kaar the All-Searing: nowhere outside it
- **Palette** `Brass (200,148,40)`, `Glare (255,212,92)`, `Blaze (255,236,150)` (Blaze is 106 from the white token,
  just outside today's provisional 100 radius; Q2). BENCH accent white-gold, over-exposed.
- **Primary: THE FIELD**: P1 BREATH `field`: the territory rises and falls together, no front anywhere. Heat-shimmer: P2
  in the top band only (Glare/Blaze), a random tenth, `rise` 0.5 s. **Territory** `TIDE(open)`: largest rooms and
  exterior first, `minShare` 0.4; weak at a sliver (catalog VII-2), so below 0.4 he becomes a TELL.
- **Resting**: slow field at Brass: excellent working light, cruel in look (L15). **Pleased** (bad news): Glare with
  shimmer. **Angry** (hunting): a Blaze P5 `turn` beam that pauses over the darkest room it finds; when Ishko holds
  territory that room is Ishko's ("hunts the hider").
- *Why*: the one god without motion through space; his menace is totality, best seen beside a moving god.

### 2.9 Ozzik the Shamed: the broken crown
- **Palette** `Mourning (40,20,62)`, `Royal (100,50,142)`, `Tarnish (168,128,52)`, `Crown (232,182,72)`. BENCH accent
  faded royal purple and tarnished gold.
- **Primary: THE CROWNING**: a P4 bloom built outward from his anchor in tiers (`hold` 10 s per step: architectural,
  never smooth), with a P9 COUNT of one Crown per room on its brightest fixture; in each territory one crown is always
  Tarnish, the wound showing. **Territory** `TIDE(grandest)`: the most impressive room (using the vanilla room
  impressiveness stat as an anchor is a proposal).
- **Resting**: purple rooms crowned in gold, one crown tarnished. **Pleased** (Exalted is exposure in canon): every crown
  blazes and the bloom overreaches its share, magnificent and dangerous. **Angry** (grief-pall): the catalog's Ashfall
  in his colours (P5 `axis` downward), crowns tarnishing one by one.
- *Why*: grandeur in tiers with one flaw kept on purpose, for the finest rhetoric in the cast.

### 2.10 Distinctness, the Narrator, the default

| god | primary motion | tempo | territory | darkness |
|---|---|---|---|---|
| Ishko | paired jump, long stare | slowest | core | true black + drawn embers |
| Ohm | fast pulses on the wiring | medium-fast | circuit | never |
| Oomo | tide + trembling bead | slow | medoid | never (Deep floor) |
| Mob'Unloo | tally on a strict beat | metric | wedge, ragged 0 | never |
| Rekko | single walker leaving warmth | slow | shrine | never |
| Ta'Baa | waves only outward | quick | threshold | never |
| Zizzik | coils, or asleep | irregular | ragged, islands | Void between coils |
| Sh'kaar | field, no front | vast | open, minShare | never |
| Ozzik | tiered bloom + crowns | stately | grandest | never (Mourning floor) |

The **Narrator** is not in the library: he stays the reserved preemption layer (catalog IV-1: RISE = a P4 shell from the
nearest fixture, a still HOLD, RETURN to pure-time phase); his wash may use the drawn layer (decision 4). With no god
present, **Lamplight** (P1, widened warm palette, decision 3) is the shipped default.

## 3. Player settings (off the Utinni)

L3 stands: aboard the Utinni the player never chooses (who exactly gets this page is Q1). Off the Utinni there is no
satiation engine and no rank, so the settings supply both. One page, kept small:
```
 ATMOSPHERIC BASE - VOICES                                   [live preview strip per row, in palette]
 ( ) Ishko      reading [Resting v]  tempo [Shipped v]  intensity [Gentle v]   ▮▮▯▯▮ ...
 (x) Ohm        reading [Resting v]  tempo [Shipped v]  intensity [Gentle v]
 ...nine rows...
 Front: [Ohm v] then [Oomo v]    Drift: [Off | 1 h | 6 h | 1 day]    Shape: [Each god's own | Wedge | Tides]
```
- **Present**: present gods take the front by the Front picks; the rest become the tremor (L6, at most 3).
- **Reading**: Resting, Pleased, Angry (plus Mimic for Zizzik): each the authored scheme for that mood.
- **Tempo**: Slow (x1.5 periods), Shipped, Lively (x0.67). Periods only, never palettes, so the cache bound holds.
- **Intensity**: *Gentle* clamps to inner entries, keeps a working-light floor (no full black, drawn embers off) and
  keeps Angry out of drift. *Full* is as authored.
- **Drift**: rotates the front among present gods; readings wander resting/pleased (angry only at Full).
- **Defaults** (the shipped gentle): no god present, so Lamplight. A god switched on starts Resting, Shipped, Gentle,
  own shape.
- The **preview strip** is the page's beauty: each row draws its pattern as a moving swatch (UI drawing, not lamps). It
  also serves as the definition's "showcase that cycles the flagship schemes" (§5).
- The page lists whatever signature defs are loaded; the Nine are those the campaign tier ships, so AtmosphericBase
  stays campaign-agnostic (definition §4).

## 4. Data model: patterns are XML, primitives are C#

Rule: **a new pattern is XML; only a new primitive is C#.** The nine primitives and four modifiers are the closed
vocabulary. Each implements `int Index(ctx, emitter, t)` (pure, like today's `PaletteIndex`) and
`double NextChange(ctx, emitter, t)` (for B), declares its cost class, and validates params in `ConfigErrors`. A C# mod
may add one through `primitiveClass` (a workerClass-style hook). Everything in §2 is composition.
```xml
<RimMandrake.AtmosphericBase.RM_AtmosphericSchemeDef>
  <defName>RUT_Scheme_Ishko_Resting</defName>
  <palette><li>(0,0,0,0)</li><li>(26,10,4,0)</li><li>(64,26,8,0)</li><li>(205,98,24,0)</li></palette>
  <mayGoDark>true</mayGoDark>
  <layers>
    <li><primitive>Breath</primitive><scope>Field</scope><entries>1~2</entries><period>300</period></li>
    <li><primitive>Procession</primitive><combine>Over</combine><entries>0~3</entries>
        <heads>1</heads><pair>true</pair><step>Jump</step><dwell>8~20</dwell><drawnInBlack>true</drawnInBlack></li>
  </layers>
</RimMandrake.AtmosphericBase.RM_AtmosphericSchemeDef>

<RimMandrake.AtmosphericBase.RM_SignatureDef>          <!-- framework type; the Nine ship in the campaign tier -->
  <defName>RUT_Signature_Ishko</defName>
  <territory><shape>Tide</shape><anchor>Core</anchor><ragged>0.04</ragged><minShare>0</minShare></territory>
  <readings><resting>RUT_Scheme_Ishko_Resting</resting><pleased>RUT_Scheme_Ishko_Pleased</pleased>
            <angry>RUT_Scheme_Ishko_Angry</angry></readings>
  <tell>RUT_Scheme_Ishko_Tell</tell>                    <!-- what he looks like as a tremor -->
</RimMandrake.AtmosphericBase.RM_SignatureDef>
```
- **Backward compatible**: an old `<pattern>RoomBreath</pattern>` parses as one `Breath` layer; shipped Lamplight and
  Fireflies defs and their tests are untouched.
- **Index-only composition**: layers combine on indices, never colours; the palette stays the cache bound (L4).
- **Graph substrate** (rooms/doors, conduits, axis projection, exterior-door distance, anchors): one cached per-map
  structure shared by P3-P7, invalidated on topology change, not membership change (GPT). Code, built once.
- **Palette guard** already checks the Narrator token distance (`RM_SchemeKernel.cs:52-65`); every layered scheme
  passes it in `ConfigErrors`, so a modder's near-white is refused at load with a reason.
- **Player choices** live in mod settings as `(signatureDefName -> present, reading, tempo, intensity)`; no save data
  (decision 10).

## 5. Proof implications

**Per primitive, offline (selftest, kernel only).** (a) `NextChange` agrees with an independent brute evaluator at every
analytic boundary ±ε (GPT: brute sampling alone misses boundaries). (b) Own property: BREATH room phases distinct; SPARK
rate within ±10% of `1/oneIn`; TIDE front ≤ band, no room-wide flip beyond `hysteresis`, every band fixture flips once
per period; RIPPLE monotone in graph distance; SWEEP `toward` never changes a fixture before its outward neighbour within
a wave; PROCESSION exactly k heads, hops graph-adjacent unless `jump`, overlap honoured; COIL no repeat within 10
periods, crossings show `max`; TELL integer cap for 0-25 fixtures; COUNT zero changes at steady state; HUSH monotone
settle with an ember kept in black. (c) Geometry: ring, branch, open plan (TIDE degenerates to WEDGE), single room;
0, 1, 2, 7, 11, 25 fixtures.

**Per god, offline.** (a) **Two-channel identity**: a hue-free motion feature vector per reading (changes/min, spatial
autocorrelation, direction bias, burstiness, beat regularity); every pair of resting readings must differ by a set
margin. This makes definition §4's hue-and-motion law a test. (b) Hue: the palette guard, Narrator distance, pairwise hue
separation of the nine resting palettes (proposal; the eye decides). (c) L8 for every reading that may go dark: in every
4 s window, every dark room shows an ember or a change.

**Live (`src/RimMandrake/AtmosphericBase/proof_atmosphere.py`).** It has `m_palette`, `m_writes`, `m_lead`, `m_boundary`,
`m_tremor`, `m_dark`, `m_restore` and `V_ROWS`. Add one measure per primitive (`m_tide_front`, `m_procession_heads`, ...)
with rows `P<n>.<primitive>.<property>`; a god row `G.<god>.<reading>` composes primitive rows rather than re-proving
them. The drawn layer needs a screenshot-judge row (no bridge read sees a draw, package §6 C); a screenshot cannot
prove motion (GPT), so motion stays on series rows.

**Fairness under time dependence.**
- Sample at the analytic change times from `NextChange`, not a fixed interval, so a 0.8 s event is neither missed
  nor double-counted.
- Every window spans at least one period of the reading's slowest layer, else UNMEASURED (Ishko's breath needs 300 s).
- Decision 10 makes "start of pattern" a real state: run each row from t = 0 *and* from three hashed phases.
- Run tempo-dependent rows at all three tempos, windows scaled by the multiplier.
- God-vs-god comparisons use the same start phase and fixture set.
- Perf rows count whole-room bursts (P1 `field`, P4) separately from the average (GPT: averages hide bursts).

## 6. Build order (after decision 7's live Phases 1-4 run and engine B; each step has an offline check)

1. **Owner sitting on §2 and §7.** Check: answers recorded in package §9 and the ledger.
2. **Primitive interface**; port `Breath`, `Spark` (`Index` + `NextChange`). Check: bit-identical to today's
   `PaletteIndex` over the existing 60,000-sample harness; NextChange against the brute evaluator.
3. **`<layers>`**, old `<pattern>` as one layer. Check: shipped defs load unchanged; ConfigErrors cases for bad
   entries, combine and params.
4. **Graph substrate.** Check: selftest geometry cases (ring, branch, open plan, single room, 0-25 fixtures);
   invalidation on a wall edit only.
5. **P3 TIDE** as territory (proposal A) and as a layer; wedge kept. Check: front size, hysteresis, no room jumps;
   L5a-e rows unchanged.
6. **P4 RIPPLE, P5 SWEEP.** Check: monotone rings; direction properties.
7. **P6 PROCESSION**, grid embers only. Check: heads, adjacency, overlap; L8 window test.
8. **P8 TELL** (refactors the tremor), **P9 COUNT**. Check: integer caps; zero changes at steady state.
9. **P7 COIL.** Check: no repeat, `max` crossings, events per frame within B's budget at T = 200 and 1000.
10. **M1-M4.** Check: ECHO delay jitter, APPROACH envelope, SCAR linger bound, HUSH settle.
11. **`RM_SignatureDef`; the Nine authored in the campaign tier.** Check: identity matrix, hue and Narrator guards.
12. **Settings page** with preview strips. Check: round-trip; defaults equal the shipped gentle (extend
    `read_defaults`/`judge_defaults` in `proof_atmosphere.py`).
13. **Drawn ember layer spike** (decision 4). Check: no draw call when no held fixture is black; the look is the
    owner's call on screenshots.
14. **Live** P/G rows, then an owner look at three gods side by side.

## 7. Open taste questions (only the owner can answer)

**Q1. Who gets the settings?** His words: "in the [Utinni]-aligned version they will be player settings"; L3 says the
player never chooses aboard the Utinni.

| option | pro | con |
|---|---|---|
| a. Any game not aboard the Utinni sees the Nine as settings | Matches L3; widest showcase | The Nine appear in colonies with no Jawa faith |
| b. Only a Utinni-faith colony off the ship gets them; a plain colony gets neutral schemes | The gods appear only where they mean something | Most players never see them |
| c. Both: plain colonies get the Nine under neutral labels ("Ember", "Current"); a faith colony gets their names | Beauty for everyone, names where they belong | Two label sets to keep |

**Q2. Sh'kaar's white-gold against the Narrator token (and Rekko against vanilla amber).**

| option | pro | con |
|---|---|---|
| a. His hottest entry stays visibly gold; Rekko leans bronze | Clean guards, no special case | Less "over-exposed" than his canon form |
| b. Near-white allowed only as shimmer (≤ 0.5 s), never held | Over-exposure, and the Narrator's held white stays unique | A guard exception to write and test |
| c. His excess carried by area and sync, not whiteness | No exception at all | Rests on motion alone; weakest at a small share |

**Q3. Do the dark gods go truly dark off the Utinni at Full?** Darkness is real light (L2): work slows, plants suffer.

| option | pro | con |
|---|---|---|
| a. Yes: Full is Full; Gentle keeps the floor | Honest; the most beautiful dark | A player may not connect slow work to the lights |
| b. Full dark only in rooms the player marks (bedrooms, halls) | Beauty where it costs nothing | One more setting |
| c. Off the Utinni, never below ember | Simplest; no hidden penalty | Loses embers-in-black, the most striking image here |

**Q4. When the two front gods' shapes differ, who draws the boundary?**

| option | pro | con |
|---|---|---|
| a. The leader's shape | One rule; the loud god owns the geometry | A rank swap redraws the whole boundary at once |
| b. Each draws its own claim; contested fixtures go by rank | Each god's geography stays true (Ishko core, Ta'Baa rim) | Gaps and overlaps to resolve; more tests |
| c. Authored pairings for the canon pairs (Ishko/Ta'Baa at the threshold, Sh'kaar hunting Ishko), (a) elsewhere | Canon relations become visible | 36 pairs, or a default for most |
