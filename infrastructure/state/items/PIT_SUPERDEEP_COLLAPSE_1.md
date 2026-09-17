# PIT_SUPERDEEP_COLLAPSE_1

A pit is not a building. It is a SUPERDEEP excavated cell — depth 4 on the D/F
primitive that rulings 18 and 19 already established, and that ruling 19 already
called "the trapping level". This item carries the pit code and defs onto it.

## the ruling  (OWNER'S WORDS — verbatim, 2026-09-17)

Asked how to close the gap between rulings 18/19/24 and a pit that is still
`Building_OpenPit : Building, IThingHolderWithDrawnPawn` with its own parallel
depth ladder, he chose "rule it now" and said:

> *"If you're in a superdeep pit, you can't climb out. Period. Welcome to your
> pit. This defines a "room" if it's enclosed that you can use for prisoner
> storage. Should be a button to "jump into pit" and if you do, you are stuck
> there too. A ladder nearby can be pulled up or lowered to allow people out
> (like opening a prison door). Should work just like a prison cell mechanic.
> There is a reference prisoner mod we are subscribed to for inspiration here.
> Covering the pit allows people to fall into it involuntarily (or if they are
> somehow pushed or blasted into it, something that would move them normally
> against their will like weapon blowback). Most of the pit mod detail is no
> longer needed here unless it's just to install certain hardware in tine
> pit/canal. A sluice gate also acts just like a door in a superdeep pit,
> obviously, that you can't open from the inside but you can from the outside or
> above. Ask me any further design questions now you need to clarify this."*

What that fixes, in his own words from the sitting before it: *"I'm not really
sure a pit is any different than a deep canal. You just build spikes or fill it
with oil or cover it... it's really no different and not a separate 'pit' in a
canal."*

## why this item exists — MEASURED 2026-09-17, laptop, offline

The pit was never rebuilt onto the primitive, and that is why it still looks like
a spike trap.

- **1 of 20** `.cs` files under `src/RimMandrake/FlowWorks/Source/Pits/` references
  the excavation primitive at all (`CompPitFitting.cs`). The other 19 are
  building-based.
- The pit carries its **own parallel depth ladder** — dig-site defs are
  `RM_PitDigSite_Shallow_* / _Deep_* / _Chasm_*`. **"Chasm" does not exist in
  `RM_ExcavationDepth`**, and the ruled levels `Mid` (2) and `Superdeep` (4) do
  not exist for pits. Two incompatible depth models ship in one mod.
- **All 18 pit defs share one `texPath`: `Things/Building/Security/TrapSpikeArmed`**
  — vanilla's spike trap. Zero bespoke pit art ships. So the defect that prompted
  the entire north-star system (a pawn "staring at the camera" in a box labelled
  Pit) is unfixed, and is provable from disk without launching the game.
- `Building_OpenPit : Building, IThingHolderWithDrawnPawn, IThingHolder` — the
  pre-ruling-18 model, a building that holds a pawn.

## the twelve stranded bars

`Pits` is not a mod: `src/RimMandrake/Pits/` holds only `__pycache__`, and the pit
content ships inside FlowWorks (`Defs/Pits/`, `Source/Pits/`). `mandrake.rm.pits`
survives only as prose in FlowWorks' `About.xml` line 51.

Yet `design/validation_walks/RimMandrake/Pits.md` carries **11 must-show + 1
cannot-show VALIDATED bars** — his approval, binding nothing, because
`modcheck run Pits` cannot resolve a mod folder. FlowWorks' own 13+3 bars contain
**zero** pit bars: measured, the two rosters have no overlap at all. The pit's
visual floor was silently lost in the merge.

⛔ **Do not move those 12 bars into FlowWorks as they stand.** Several are claims
about a Building — `pit_not_vanilla_trap` is explicitly about "its own texture
path" — and under this ruling a pit is terrain with no texPath to own. Moving them
now would enshrine the retired model inside a validated checklist. They are
rewritten against the primitive as part of this item, and he re-validates.

The roster as it stands, so nothing is lost in the rewrite: `pit_reads_as_hole`,
`pit_not_vanilla_trap`, `pit_occupant_below_floor`, `pit_occupied_distinguishable`,
`pit_reads_at_size`, `pit_covered_invisible`, `pit_covered_seam_at_max_zoom`,
`digsite_stage_legible`, `pitcell_gate_state_legible`, `pitcell_occupant_visible`,
`fitting_reads_distinct`, and (cannot) `never_snared_standing`.

## what the ruling settles

1. **Superdeep traps absolutely.** No climbing out, no skill check, no exception.
2. **An enclosed superdeep area is a ROOM**, usable for prisoner storage.
3. **A "jump into pit" gizmo** exists, and using it strands the jumper too.
4. **A ladder** near the lip, raised or lowered, is the way out — and it behaves
   like opening a prison door, not like a pathfinding cost.
5. **It should work like the prison cell mechanic**, with a subscribed reference
   prisoner mod as inspiration.
6. **A cover makes involuntary entry possible** — falling in, being pushed, or
   being blasted in by anything that would normally move a pawn against its will
   (weapon blowback).
7. **A sluice gate is a door** on a superdeep cell: not openable from inside,
   openable from outside or above.
8. **Most pit-mod detail is dropped**, retained only where it installs hardware
   into the pit/canal.

## his answers to the clarifying questions  (2026-09-17, same sitting)

He invited these in the same breath as the ruling. Four asked, four answered.

**1. A pit is a room, and a room is not a prison until you furnish it.** Verbatim:

> *"It's just a room until you put a prisoner bed in it. So when people fall into
> it they aren't prinsoners yet, they're just trapped enemies. But that should be
> one of those interactions that is helped by letting them roast in there: easy
> prisoner capture once they're in the pit, and no you don't have to go down and
> enter the room to capture them. You can "capture down" and "convert down""*

So there are **two states, not one**: a bare enclosed superdeep area holds
*trapped enemies*; the same area with a prisoner bed in it is a genuine prison
room on vanilla's own terms. And it adds two interactions that do not exist in
vanilla:

- 🔑 **`capture down` and `convert down`** — both performed from the lip. A warden
  never has to path into the pit, which matters because by ruling nobody who
  enters can climb out. Any design that requires entering the pit to interact with
  an occupant is wrong.
- **Being trapped makes capture easy.** Time in the pit is itself the softening
  step ("letting them roast in there").

**2. Only SUPERDEEP traps.** Mid (2) and Deep (3) are movement cost only —
confirming ruling 19 exactly as `RM_ExcavationDepth` already documents it, and
keeping LAW 2 intact. A trap must be dug all the way to 4; there is no partial
trap and no escape-attempt state to build.

**3. Fill drowns at superdeep, and slows everywhere else.** He chose drowning as a
consequence of F rising against an occupant, and added:

> *"and all other flooded canal depths just slow you down more with the water than
> the empty canal did"*

- ⛔ **The `Water` fitting RETIRES.** Flooding an occupied pit is just opening a
  sluice; a fitting that pre-floods duplicates it.
- Every non-superdeep depth gets a movement penalty that is **strictly worse
  flooded than dry at the same depth** — a new relation the fill code must honour,
  not just a per-depth constant.

**4. The reference is `legator.prisonerrealism` (Prisoner Realism).** Read its
defs and Harmony patches for how it decides what counts as adequate confinement —
that is the same question a pit raises. It is in the live list
(`ModsConfig.FULL.PRECAPTURE.20260917_085900.xml`), so it can be read on the
Desktop; on the laptop only its About/defs are reachable if a copy is on disk.

**5. TEMPERATURE is the softening mechanism**, and this is the answer he most
wanted on the record. Verbatim:

> *"but I really meant being in brutal high-temp sun should raise the temperature
> in the pit quickly, just as cold-exposure will wear them down as well, and
> swiftly lower their resistance to much of anything. But it's not something nice
> colonists do..."*

- 🔑 **An open pit under a desert sun heats FAST, and a cold night chills it.** The
  pit's temperature is strongly coupled to ambient, more so than a roofed room.
- 🔑 **Exposure swiftly lowers "resistance to much of anything"** — read against
  vanilla that is recruitment resistance first, and general will to resist beyond
  it. This is the mechanism behind "easy prisoner capture once they're in the pit":
  the pit does the breaking, the warden only finishes it.
- ⚠️ **It is a cruel act and should read as one** — *"not something nice colonists
  do"*. So it wants a mood/ideoligion dimension rather than being a free
  optimisation. He has not specified the shape of that; do not invent a precept.
- He also kept the literal reading alongside it: oil plus ignition remains a real
  kill route, distinct from the capture route.

⚠️ On this desert world that couples the pit directly to the campaign's premise —
brutal sun is the ambient condition, so the pit is a torture instrument by default
rather than by configuration. Worth stating plainly in the spec.

**6. Hardware: spikes survive and are CELL-SCOPED; the oubliette is cut.**
Verbatim:

> *"You can put spikes in a capture canal, they just only kill if you fall into the
> part of the canal with spikes. If you walk up to them they don't hurt you.
> everything else is just "what do you put in the canal pit with them" for oil,
> poison, etc. forget the oubliette/ion thing."*

- **Spikes are per-CELL, not per-pit.** One canal may be part spiked and part bare,
  and the spikes harm **only on a fall into that specific cell**. Walking up to
  them is harmless. That kills the old whole-building `RM_OpenPit_Spiked` model
  outright: the unit of hardware is a cell, like depth and fill already are.
- ⛔ **`Oubliette` / the ion charge is CUT.** Do not carry it forward. That also
  removes the only anti-mechanoid fitting; no replacement was asked for.
- **Oil, poison and the rest are "what you put in the pit with them"** — contents,
  not mechanisms. See the open question below on whether that makes them FluidDefs.

**7. Oil and poison ARE FluidDefs. Only spikes remain hardware.** He confirmed the
inference directly, so:

- ⛔ **The fitting concept collapses to SPIKES ALONE.** `Oiled`, `Poison`, `Water`
  and `Oubliette` all leave `PitFittingType`; oil and poison join water as entries
  in the F dimension, which FlowWorks already models (`FluidDef`, `RM_Fluid_Water`)
  and which his original FlowWorks vision already anticipated: *"fresh water, salt
  water, tar, propane, colored water, slime"*.
- Poison-as-fluid needs its toxin rule keyed to **fill**, not to a comp.
  Oil-as-fluid must stay ignitable, and the canal fire machinery already binds two
  FlowWorks bars (`canal_burning_reads_as_burning_liquid`,
  `canal_fire_reaches_reservoir`), so it has somewhere to land.
- 🔑 This is what makes pit and canal genuinely **one** thing, which was his
  original instinct: *"I'm not really sure a pit is any different than a deep
  canal."*

## the model, assembled

Everything above, as one statement. A cell carries **D** (depth 0-4) and **F**
(fill of some FluidDef) and nothing else; every behaviour is a function of those
two plus what is installed or built on the cell.

| | |
|---|---|
| D = 4 (Superdeep) | traps absolutely — no climbing out, no check, no exception |
| D = 1-3 | movement cost only; they do not hold anything |
| F > 0 at D = 4 | drowns an occupant |
| F > 0 at D = 1-3 | slows movement strictly more than the same depth dry |
| Fluids | water, oil (ignitable), poison (toxin keyed to fill), and the rest of his list |
| Spikes | per-CELL hardware; lethal ONLY on a fall into that cell, harmless to walk up to |
| Cover | conceals, and enables involuntary entry (falling, pushed, blast/weapon blowback) |
| Sluice gate | a door: not openable from inside, openable from outside or above |
| Ladder | raised or lowered near the lip; behaves like opening a prison door |
| Enclosed superdeep area | a ROOM. Occupants are trapped enemies, not prisoners |
| …plus a prisoner bed | a genuine prison room on vanilla's terms |
| Temperature | strongly coupled to ambient; exposure swiftly lowers resistance. Cruel, and should read as cruel |
| Interactions | `capture down` and `convert down`, both from the lip — never by entering |

⛔ **CUT and not to be carried forward:** the `Oubliette` / ion-charge fitting; the
`Water`, `Oiled` and `Poison` fittings; the parallel `Shallow/Deep/Chasm` dig-site
ladder; `RM_OpenPit_*` as buildings; every def pointing at
`Things/Building/Security/TrapSpikeArmed`.

## the art is already ruled, and Quarry is the proof it works

He raised Quarry again in this sitting — *"There is also the great Quarry reference
to check out. It almost DOES this..."* It is `ogliss.thewhitecrayon.quarry`,
**active in the live list**, and it was already his **ruling 33** (2026-09-16):

> *"The pit graphic itself should have some perspective to it. Check out quarry mod
> for art and inspiration. They already do this."*

BENCH LOOKED at the reference on disk
(`design/RimMandrake/references/quarry_pit_perspective_2026-09-16.jpg`),
2026-09-17. What it shows, and why it matters to this item:

- 🔑 **The depth read comes from the WALL FACES, not from the occupant.** The north
  and west edges draw the *inner face* of the excavation — lit tan rim above,
  shadowed earth below. Pawns are drawn at ordinary scale standing on the pit
  floor, and they read as being down in it purely because walls rise around them.
- 🔑 **Therefore `pit_occupant_below_floor` may need no custom pawn draw at all.**
  Quarry achieves it with terrain and edge art. If that holds, a whole class of
  work — and the `IThingHolderWithDrawnPawn` machinery in `Building_OpenPit` —
  deletes rather than moves. ⚠️ UNCERTAIN: this is a read of a screenshot, not of
  Quarry's code. Verify against its source on the Desktop before relying on it.
- **Ladders are drawn on the walls, in perspective** — three of them. Under today's
  ruling those are mechanical, not decorative.
- **It is a multi-cell enclosed space that reads as a room**, with irregular organic
  edges rather than a tile grid — which is `pit_reads_at_size` and "this defines a
  room" both satisfied by the same art.
- **No Building is involved.** Quarry is terrain. That is existence proof that the
  collapse ruled here can look right, which is the strongest argument available for
  it.

And the visual half was already ruled before today, so the spec must not re-decide
it:

- **Ruling 19** — depth is visible through fill-tier ramps for wet cells and **"one
  inner-shadow edge treatment"** for dry. That IS the Quarry wall face.
- **Ruling 20** — the name FlowWorks celebrates the **built** half: *"the terraces,
  ladders, sluice gates"*. Ladders and sluice gates were already in the concept;
  today's ruling gives them mechanics.
- **Ruling 33** — perspective, Quarry's manner: *"walls with depth, not a flat tile
  with a lip shadow"*.
- **Rulings 34-36** (2026-09-17) all DELETE art — the three-state source, the
  limited-vs-limitless glyph, the damp irrigation ring. ⛔ Do not restore any of
  them while rewriting the pit bars.

## his rulings on the spec's open questions  (2026-09-17, same sitting)

Four of §9's ten answered by card, after the spec landed. §9 letters in brackets.

**[F] Fluid identity is typed per LIQUID BODY — not per cell, not per map.** He took
the middle option the spec surfaced. A pit fed by its own sluice is its own body, so
his answer 7 (oil in this pit, poison in that) ships without a per-cell grid.
- ✅ Cheaper than per-cell: new state on the body plus a save migration, and a single
  canal's behaviour is unchanged.
- 🔴 **The unresolved case is body MERGING.** Two pits joined by a channel become one
  body. The spec flagged this: their fluids must either merge or refuse to, and
  nothing decides which. **That is now the first thing the implementation must ask
  him** — it is a gameplay-visible rule, not an implementation detail.
- ⛔ `ActiveFluid` as a single per-map field is therefore retired, not kept.

**[D] LAW 2 gets a SECOND STATED EXCEPTION.** He chose D2 over deriving room-hood
from a built lip, so depth is permitted to reach room detection.
- This is a **policy** ruling and stands on its own; the spec's blocking unmeasurable
  does not threaten it, it only prices it. ⚠️ If vanilla's region/room builder never
  considers `TerrainDef` at all, cashing this exception needs a **Harmony patch on
  region building** rather than a terrain choice — read `RegionAndRoomUpdater`,
  `RegionMaker`, `Region.Room`/`District` on the Desktop before estimating.
- ⚠️ The spec's own caution stands and should be written into the exception when it is
  authored: ruling 23 is a RESTRICTION on an existing check, whereas this is an
  ADDITION that makes new systems read depth. **Word the exception so it does not
  become a general precedent** for any future system that wants to read D.
- ⛔ `RM_ExcavationDepth.cs`'s LAW 2 docstring still says "and nothing else". That is
  TRUE today and becomes false when the collapse ships, so it is rewritten as part of
  the implementation — not now, and not ahead of the exception's agreed wording.

**[E] Real path cost, done properly as a depth × tier matrix.** He rejected both the
cheap fixes — relying on perceived cost, and flattening the tiers upward.
- Fixes the live contradiction MEASURED today: `RM_Fill_Water_Half` 42 against dry
  `RM_Channel_Mid` 45, so a half-flooded cell is currently CHEAPER to cross than a dry
  one, against his ruling that flooded slows you more.
- Cost he accepted: each fluid goes from 4 terrains to **12**, and `FluidDef`'s
  shipped shape changes. This is the largest of the three options and touches a def
  format already in the game.
- 🔑 It also preserves what ruling 5's three fill tiers exist for — flattening upward
  would have eroded the depth read to buy a cheaper fix.

**[H] Both hediffs stay: vanilla for damage, `RM_PitExposure` for resistance.**
Heatstroke/Hypothermia keep doing physical harm; his own cover-is-mercy hediff
(2026-08-30) becomes the accumulator that drives resistance down.
- 🔑 So §5's temperature mechanism **does not replace** a mechanism he ruled — it sits
  beside it, and the two are tuned independently: "this is hurting them" and "this is
  breaking them" are separate dials.
- Cost he accepted: two systems on one pawn that a player must tell apart, and they
  can disagree.

## his rulings, second card round  (2026-09-17, same sitting)

**[J] The body-size gate SURVIVES, as a per-depth field on the primitive.** Each
depth carries a max body size, so a shallow pit genuinely cannot hold what a chasm
can, and the existing dig-site fiction ("heavier game", "megafauna") stays true.
- Cost he accepted: `RM_ExcavationDepth` widens beyond the two integers it holds now.
- 🔑 **This couples with [G] below**: body size now decides BOTH whether a depth holds
  you and how hard the spikes hit you. Two mechanics, one stat, pulling in opposite
  directions — a big creature is harder to hold and takes more spike damage. That is
  coherent and worth stating in the spec as a deliberate pairing rather than two
  unrelated uses of `BodySize`.

**[C] A trapped mech is killable from the lip — and he commissioned a door family
off the back of it.** He took option 1, then added:

> *"plus maybe it's handy to keep a hostile mech until you want to release it via a
> sliuce gate? Speaking of which, we should commission a grating door as a "prisoner
> door" for the end of a canal as well... so that fluid can easily enter without
> needing to open it. Sliuce should be cheap to build and really designed to hold in
> small creatures or allow water to flow only. The metal sluice is more armored, can
> survive burning, and can hold tough prisoners. A steel grating is just as strong for
> prisoners but allows liquids to flow and can survive burning. Those are the three.
> Though I'd be happy if we just had Sluice and SecurityGrateDoor and allowed them to
> be stuffably made too, and the player can just learn what happens if you're made of
> wood"*

- 🔑 **A trapped hostile mech becomes a STORED ASSET**, not a problem: hold it, then
  release it through a sluice when you want it loose. That reframes [C] entirely — the
  pit is a mech holding pen, and "unreachable hostile" was the wrong framing.
- 🔑 **His own preferred shape is the SIMPLER one, and it should be built:** two defs,
  **`Sluice`** and **`SecurityGrateDoor`**, both **stuffable**, with the stuff
  deciding armour, fire survival and how tough a prisoner they hold — *"the player can
  just learn what happens if you're made of wood"*. Stuffability replaces the
  hardcoded three-tier ladder he described first (cheap sluice / armoured metal sluice
  / steel grating). ⛔ Do not build three fixed defs; that is the version he talked
  himself out of in the same breath.
- The functional split that must survive stuffing: a **sluice** passes liquid and
  holds small creatures; a **grate door** passes liquid AND holds a real prisoner.
  Both are doors in the §4 sense — not openable from inside a superdeep cell.
- ⚠️ **This is NEW CONTENT, not part of the collapse.** It is a door family for
  FlowWorks and probably wants its own item; recorded here because it was ruled here.
  It also answers §4's sluice-gate question with a concrete def roster.

**[A-item] The debuff is "Exposed Prisoner", and it PIGGYBACKS on vanilla's existing
moral machinery.** Verbatim:

> *"Exposed Prisoner should be the debuff, and it should hit compassionate folks like
> when you turn beggars away and ignore psychopaths or "hard" morality cultures.
> Borrow their structure and piggyback, so we don't end up making a whole new moral
> axis."*

- 🔑 **The instruction is architectural, not just thematic: do NOT invent a new moral
  axis.** Use the shape vanilla already has for rejecting beggars and similar acts — a
  thought that compassionate pawns feel, that psychopaths and hard-morality cultures
  do not.
- That resolves the spec's hard case for free. §9 warned the cost "has to attach to a
  duration with no acting pawn"; piggybacking on the existing structure sidesteps
  building a duration-tracked mood system from scratch.
- ⛔ Still do not invent the precept's numbers or its exact def shape without him —
  but the STRUCTURE is now ruled, and it is "copy the existing one", not "design one".

**[G] Spikes fire on ANY descent, the jump gizmo warns and confirms — and they are
NOT instant death.** Verbatim:

> *"it isn't instantly lethal, it just inflicts a massive Sharp damage. If you're
> incredibly armored you might survive. Don't use instant death, use regular damage.
> Reason metaphorically to determine what that damage might be. The fact that it's
> based on gravity is interesting: that means the heavier things have more momentum
> than lighter things, cancelling their ordinarily higher health, so I think the damage
> should be scaled proportional to bodysize."*

- ⛔ **No instant-death path.** Massive **Sharp** damage through the normal damage
  pipeline, so armour, body parts and luck all apply and a heavily armoured pawn can
  survive.
- 🔑 **Damage scales proportional to `BodySize`** — his reasoning: the fall is
  gravity-driven, so heavier things carry more momentum, which cancels the higher
  health they would otherwise enjoy. So a thrumbo is not safer than a squirrel merely
  for being large.
- The magnitude is to be reasoned "metaphorically" rather than given: ⛔ do not invent
  a number and present it as his. Propose one with the reasoning shown, for his word.

- The shape of the mood/ideoligion cost of temperature torture. He flagged it
  explicitly — *"not something nice colonists do"* — and did not specify it.
  ⛔ Do not invent a precept; it comes back to him.
- Whether `capture down` / `convert down` require the warden adjacent to the lip,
  in line of sight, or merely somewhere on the map. Proposed by the spec, ruled by
  him.
- What replaces the anti-mechanoid case now the oubliette is cut, if anything. He
  did not ask for a replacement.

## his rulings, third card round — the bars  (2026-09-17, same sitting)

§9's last two questions plus the six new bar claims. **All ten of §9 are now ruled.**

**[B-item] `capture down` / `convert down` require the warden ADJACENT to the lip.**
The most physical option, reusing vanilla's "warden must reach the prisoner" job shape.
⚠️ Carry the cost the spec priced: ruling 23 lets a superdeep occupant trade fire with
whoever is at their own lip, so an adjacent warden stands in exactly the cell an armed
occupant can shoot. A known and accepted risk now, not an oversight to design away.

**[I] Merge rule: his approved wording wins; only genuinely new claims come to him.**
⚠️ BENCH correction, made to him in the sitting: three pit bars were first described as
*duplicates* of approved canal bars, and that was too strong. In each case the pit
version is **broader or stronger**, so a merge means strengthening or generalising a bar
he already validated:
- `fill_tier_legible` (4 states) strengthens approved `canal_partial_fill_distinct` (2).
- `fill_fluid_distinct` (all fluids) generalises approved
  `slime_reads_as_viscous_not_water` (slime vs water).
- `pit_reads_as_hole` and `canal_reads_as_dug_channel` are **not** the same read — a
  trench you cross versus a hole you fall into. Keep both.
- `pit_occupant_below_floor` generalises approved `slime_occupant_below_surface`, whose
  own text already says *"Kin to Pits' `pit_occupant_below_floor`"*.

### 🔴 The depth ruling — bigger than the bar that prompted it

Asked whether `pit_depth_ladder_legible` should be narrowed, because ruling 19's single
inner-shadow treatment probably cannot separate five levels, he **rejected the narrowing
and raised the requirement instead**. Verbatim:

> *"All depths must be visually legible and differentiable graphically. The pawn should
> visibly rise up and lower down as they move over the depths. They should be low enough
> that it is visually clear how they could not possibly climb out (the walls are higher
> than their head by 20%)"*

Three separate requirements, all new:

1. 🔑 **ALL depths legible and differentiable graphically** — not merely "superdeep versus
   the rest". Ruling 19's one-treatment-for-all-dry-depths is therefore **not
   sufficient**, and this ruling effectively reopens that art rule. ⛔ Do not record this
   bar as satisfied by ruling 19.
2. 🔑 **The pawn visibly RISES AND LOWERS as they move over depths.** A rendering
   feature, not art: a pawn's vertical draw offset varies with the depth of the cell they
   occupy. It makes depth legible *and* makes an occupant read as down in the hole, in
   one stroke.
   - ⚠️ **This supersedes an inference BENCH recorded earlier today** from the Quarry
     screenshot — that `pit_occupant_below_floor` "may need no custom pawn draw at all".
     He has now ruled that there IS one. That note was marked UNCERTAIN and is retracted,
     not left standing.
3. 🔑 **The only number he has given here, and it is testable:** in a superdeep cell the
   walls stand **higher than the occupant's head by 20%**, so it is visually obvious they
   could not climb out. Measurable from a screenshot, which makes it an unusually strong
   `must show` line.

🔑 Together these answer what the spec called the single largest new visual risk. The
collapse removes the container that hid the occupant, so a spawned pawn on terrain would
otherwise look exactly like the original defect; a depth-varying draw offset plus walls
20% over head height is the fix, and it came from him.

### The six new bars — all six approved, two with wording he added

- ✅ **`pit_trapped_reads_as_trapped`** — approved, and he chose to **word it against the
  walls explicitly** rather than stating the experience alone, so the bar names the
  mechanism: the occupant reads as trapped *because* the walls rise around them.
  ⚠️ Deliberately against the house style of stating experience not solution; he chose
  that knowingly, to tell whoever draws the art what must be true.
- ✅ **`pit_depth_ladder_legible`** — approved and strengthened per the ruling above.
- ✅ **`fill_tier_legible`** — approved. Ruling 5's three tiers plus dry is exactly four,
  so it matches the ruled mechanism.
- ✅ **`fill_fluid_distinct`** — approved, and it now has real work to do because fluid is
  typed per liquid body ([F]), so two adjacent pits can hold different fluids. ⚠️ Implies
  distinct art per fluid, which is unbudgeted.
- ✅ **`spikes_read_distinct`** — approved, with a constraint on the art that is really a
  constraint on the CAMERA. Verbatim:

  > *"The spikes will barely be able to be tall enough to be visible most likely, but
  > there should still be something showing their presence. make sure the viewing angle
  > of the pit is such that SOME amount of spike is possible"*

  🔑 The pit's viewing angle is **not free** — it must permit some amount of spike to
  render. This binds ruling 33's Quarry-style perspective: it must not be so near-top-down
  that spikes vanish. "Something showing their presence" is the floor; full spikes are not
  required.
- ✅ **`never_reads_as_building`** (cannot) — approved. The general form of his approved
  `pit_not_vanilla_trap`, guarding exactly the failure this collapse exists to end.

## spec

`design/RimMandrake/pit_superdeep_collapse_spec.md` — written 2026-09-17, 1127 lines,
10 sections. ⚠️ It was authored BEFORE the three card rounds above, so where it and this
item disagree, **this item wins**: it carries his rulings and the spec carries the
questions that produced them. The spec's §9 is fully answered here and should be read
alongside, not instead of, these sections.

Owed to the spec as a revision pass: the per-body fluid decision ([F]), the LAW 2
exception ([D]), the depth × tier cost matrix ([E]), both hediffs surviving ([H]), the
body-size field ([J]), the door family (now `FLOWWORKS_DOOR_FAMILY_1`), the Exposed
Prisoner piggyback ([A-item]), BodySize-scaled spike damage ([G]), adjacent-lip capture
([B-item]), and the depth/draw-offset/20%-walls ruling above.

## verify

- No `.cs` file under `Source/Pits/` carries a depth concept of its own; depth is
  read from the primitive.
- No pit def ships `Things/Building/Security/TrapSpikeArmed`.
- `modcheck lint` reports no finding for the pit's walk, and `modcheck doctor`
  reports no ORPHAN_WALK for `Pits`.
- FlowWorks' `## north star` carries the rewritten pit bars, VALIDATED on his
  word, and `Pits.md` no longer exists.
