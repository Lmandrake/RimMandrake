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

## open questions still outstanding

- The shape of the mood/ideoligion cost of temperature torture. He flagged it
  explicitly — *"not something nice colonists do"* — and did not specify it.
  ⛔ Do not invent a precept; it comes back to him.
- Whether `capture down` / `convert down` require the warden adjacent to the lip,
  in line of sight, or merely somewhere on the map. Proposed by the spec, ruled by
  him.
- What replaces the anti-mechanoid case now the oubliette is cut, if anything. He
  did not ask for a replacement.

## spec

Not written yet. This is design work and goes to a backgrounded Fable subagent
per `infrastructure/agents/Agent_Policy.md`, not authored in the BENCH window.
The clarifying answers above are its input.

## verify

- No `.cs` file under `Source/Pits/` carries a depth concept of its own; depth is
  read from the primitive.
- No pit def ships `Things/Building/Security/TrapSpikeArmed`.
- `modcheck lint` reports no finding for the pit's walk, and `modcheck doctor`
  reports no ORPHAN_WALK for `Pits`.
- FlowWorks' `## north star` carries the rewritten pit bars, VALIDATED on his
  word, and `Pits.md` no longer exists.
