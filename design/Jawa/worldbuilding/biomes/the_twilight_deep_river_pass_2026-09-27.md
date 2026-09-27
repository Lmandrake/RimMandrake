# The Twilight Deep — river pass (2026-09-27)

_Design spec for the whole underwater river system — current, undersurge, sink, bank
works, travel lane — ready to file as **`TWILIGHT_CHANNEL_CURRENT_1`**. Written by a
DESIGN pass 2026-09-27 against the frozen sheet (`the_twilight_deep.md`), the content
drop (`the_twilight_deep_content_2026-09-26.md`, §2.2 and §8.2 especially), the RULED
danger pass (`the_twilight_deep_danger_pass_2026-09-27.md`, D6/D7), and the bedazzle
doc's §3.5. Owner rulings this rests on, 2026-09-26/27 (`TWILIGHTSEA_FLOOR_PASS_1`):
the channels LOOK like dry mud riverbeds but the denser water inside STILL CARRIES a
pawn (ban 3 live as a mechanism); the biome's immobile anchor prize is **the bank
works** on those banks; and the current and the bank works are **ONE piece of work,
not two**. The dry-river-as-travel-lane question he left open; §5 explores it and ends
in cards. Nothing here re-rules anything; §7 lists what still needs his word._

**Binding constraints carried whole:** all six hard bans (no swimmable river; no
Compact hostility; nothing reaches the waveglass; invented names only; no vanilla-Earth
organisms by name or read; vocabulary *waveglass / the lid / veil-fall*, never
mat/mold). Ship-only access (`RM_SeaDiveHatch` from a gravship is the only way down and
back). Veil-fall litter accelerating on the bed is the surge's tell — kept. All DLC
assumed present. Every new name below is invented, `RM_`-tier (Q11a), and owes a
collision re-check against `src/` and `design/` before authoring, per the drops' own
convention (`RM_BankWeir`, `RM_SiltTrap`, `RM_CargoFloat`, `RM_ChannelCurrent` names
grepped clean 2026-09-27; substring hits were "weird").

## 1. The current mechanism

### 1.1 Prior art — checked before inventing, as briefed

**GravTide (`gravtide.mod`, workshop `294100/3779600989`, 1,097 `.cs` files searched
2026-09-27; nothing named GravTide in the common Mods root — the Doctrine hit there is
a mention, not the mod).** GravTide solved gravship-to-sea-floor play, tides, flooding
and tsunamis — and **it has NO flow-field pawn carry**. Its `PassageCarryRegression`
is a pawn *carrying* a pawn on a voyage; its tsunami (`GameCondition_Tsunami`) batters
and stuns whatever stands in painted water (`StunFor(240)`, blunt damage scaled
`pawnDamagePerHealthScale * HealthScale`) but never conveys anything anywhere. So the
carry itself cannot be copied. Four GravTide shapes ARE worth copying:

1. **`TsunamiFlight.Sweep`** — during a surge, wild AND tame animals flee uphill on a
   repeating sweep, because "the sea has no position, only a height," and the drawdown
   is the folkloric tell. That is our pre-surge tell made mechanism: **the murrol
   vanishing upstream and the nuudal leaving the inner bank hours before the
   undersurge is a `Sweep`-shaped job push**, not prose (§2).
2. **`MapComponent_TidalFlats.BandAt(cell)`** — one cached per-cell answer to "how far
   up does the water come here," `int.MaxValue` for never. Our surge widening (§2)
   wants exactly this shape: a per-cell **bank-distance band** derived once from the
   flow grid, read by the surge, never a second grid.
3. **The production teleport idiom** — `pawn.Position = c; pawn.Notify_Teleported(false)`
   is what GravTide itself ships for placing pawns (`CoastalTavern`,
   `ScenPart_SeabedStart`, `MaritimeLayoutGenerator`), confirming the API shape for a
   one-cell step that the content drop §2.2 already proposed.
4. **`StatPart_WaterDrag`** — movement drag as a StatPart, the clean way to slow a pawn
   wading the margin cells without touching the carry at all.

**Our own `src/RimMandrake/` (searched: current/flow/carry/conveyor/vortex/drift over
all `.cs`).** No pawn-carry exists here either — this project has NOT already built it.
Three real precedents feed in:

- **`RM_MapComponent_MudSwallow`** (Greentide) — the shipped "terrain acts on things
  standing on it" component: interval scan (250 ticks) of things on
  `RM_MireExtension` terrain, per-cell persistent record, clean `ExposeData`. The
  scan-and-act skeleton and the modExtension-tags-the-terrain pattern are the direct
  ancestors of the carry tick.
- **`RM_WanderingVortex`** (EnvironmentalHazards) — a moving damager cribbed from
  vanilla Tornado; it moves ITSELF, not its victims. Useful only as the repo's worked
  example of the license-posture crib and the snapshot-the-cell-list defensive loop.
- **FlowWorks** — moves *liquid* (bodies, stock, flood), never a pawn or item; the
  bedazzle doc's "UNMEASURED: whether FlowWorks already carries a current" is hereby
  MEASURED: it does not. The channel current is not a FlowWorks configuration.

**Vanilla.** No conveyor-for-pawns exists (content drop §2.2 already measured this;
`CompPushable` is a one-shot shove). Vanilla's only "pawn moves without pathing" object
is **`PawnFlyer`** — despawn, travel ballistic, respawn — which is the right shape for
a single violent yank (surge grabbing a pawn off the inner bank, §2), and the wrong
shape for a continuous ride. **Verdict: the per-cell carry is genuinely new C#**, one
`MapComponent` plus one genstep, honestly small-medium (§6), and it lands in
`mandrake.rm.terminalbiomes` where every sea can reuse it.

### 1.2 The flow grid — `RM_GenStep_TwilightChannels`

The Grey's `GenStep_GreySeaFloorDressing` already paints channels downhill along the
elevation grid, so the terrain line is a solved shape (content drop §2.2). This genstep
adds the one new thing: **a direction per bed cell**. Concretely:

- Braid one to three channels from a source map edge to a **sink basin** (§3) at the
  low end, following elevation; paint `RM_ChannelBed` (the bed), `RM_BankSilt` either
  side (fertile — §4), stake-line stakes on the outer bank edge (§8.2 of the content
  drop owns the generation order; this genstep is that order's "channels with flow
  field" step).
- Store per bed cell: a **flow direction** (one of 8, a byte) and a **lane class**
  (MARGIN = outer bed cells, CENTRE = inner), both in `RM_MapComponent_ChannelCurrent`
  as a `byte[]` map-sized grid, scribed with `DataExposeUtility` (the compact idiom for
  map grids). Derived at gen time, never recomputed live — the bed does not move.
- Mark two to four **eddies** — widenings where MARGIN widens to 2–3 cells and the
  carry releases (§1.3): the Compact's weirs and the player's stand there (§4).
- Keep every channel clear of the dive-exit footprint (`RM_PlaceSeaDiveExit`) by the
  content drop's own rule: **the ship never lands astride a channel**.

### 1.3 The carry tick — `RM_MapComponent_ChannelCurrent`

The one movement system. Every N ticks (N from settings; default one cell per ~45
ticks in CENTRE, ~90 in MARGIN) the component walks its registered occupant list
(things standing on bed cells register on entry via terrain check at the interval
scan, MudSwallow-style — no per-tick whole-map scan):

- **Pawns**: `pather.StopDead()`, step one cell along the flow
  (`Position = next; Notify_Teleported(false)`), which interrupts the current job
  cleanly (vanilla re-evaluates on teleport). MARGIN pushes at half cadence and a
  pawn there **may still path perpendicular to the flow** — its own moves interleave
  with the pushes, so walking out of the margin is possible and walking out of the
  centre is not. That gradient is the whole teaching mechanism (content drop §2.2,
  kept verbatim). No damage, no stun — the Twilight kills with biology, not physics;
  the current itself only *takes you somewhere*.
- **Items**: drift at half the pawn rate (ruled position in the content drop). A haul
  job whose target moved re-targets or fails gracefully — verify against vanilla
  re-target behaviour in the build's quicktest, per the drop's own flag.
- **Downed pawns** drift like anything else, all the way to the sink (§3); rescue
  re-paths to the pawn's current cell (vanilla `JobDriver_Rescue`; at the sink the
  target has stopped).
- **Exempt**: races carrying `RM_ChannelNativeExtension` (murrol, waelune), anything
  standing on or adjacent to `RM_FordStones` (the ford cancels its cell), anything on
  a cell an **arresting building** claims (the weir, §4), and buildings always —
  buildings never drift.
- **Deliberate entry is allowed**: the bed terrain's high `pathCost` +
  `avoidWander` keeps AI and wanderers out, so a colonist enters only by drafted
  order, a job that targets the bed, **knockback that happens to land there** (a
  bank fight one step from the current — free drama, by design), or the surge coming
  to them (§2). First entry per colonist fires the one-time message *"the ground is
  moving under {PAWN}"* and a mood-free alert (ruled tell (c)).

### 1.4 How it reads on a dry-looking bed

The floor looks dry, so the tell is never the floor (content drop §2.2, all kept):
**(a)** veil-fall litter skates along the bed — an effecter/mote stream that follows
the stored flow vectors, THE tell, and it accelerates when the surge is coming (kept
as briefed); **(b)** the stake-line — `RM_BankStake`, lamp-lit, every ~8 cells along
both banks: people who have lived here for generations do not leave a river unmarked;
**(c)** the margin is recoverable — first contact costs a few cells of drift, only the
centre takes you; **(d)** the sennefan fields all face the flow (§3.5 of the drop);
**(e)** thessmoss stops dead at the stake-line — the turf itself draws the boundary
(§3.8). Five reads, zero UI.

### 1.5 Save/load safety

The flow/lane grid: `byte[]` via `DataExposeUtility.LookByteArray`, rebuilt-refusing
(if absent on load — a save from before the mod — the component regenerates nothing
and the current is simply off on that map; never a null-ref, never a re-roll of the
bed). Occupant list: not scribed — rebuilt from the terrain scan on the first interval
after load, exactly MudSwallow's posture ("a reload just restarts the dwell clock").
`RM_Hediff_Sunk` scribes as any hediff. The `GameCondition` (§2) scribes vanilla.
No per-thing drift state exists to lose: **position IS the state.**

### 1.6 Mod Settings (standing rule; the owed set)

Current **on/off** · current **strength** (cadence multiplier, MARGIN and CENTRE
scale together) · **sink outcome ladder** (§3, ruled) · first-entry warning on/off ·
undersurge frequency (off / rare / common). All-off degrades gracefully: the bed
becomes ordinary slow terrain, the weir catches nothing but its edge still gathers (§4),
the biome loses its teeth and nothing errors.

## 2. The undersurge — the current's flood state (danger pass D6, folded in)

Not a separate system — a **parameter storm on §1.3**, exactly as the danger pass
scoped it. `RM_GameCondition_Undersurge` (a day or so) does three things to the one
component:

1. **Strength up**: CENTRE cadence doubles; MARGIN cells promote to CENTRE behaviour.
2. **Width out**: the push zone extends one to two cells past the stake-line onto the
   inner bank — derived from a per-cell **bank-distance band** computed once at gen
   time from the flow grid (GravTide's `BandAt` shape, §1.1), never a second grid.
   The widened strip is exactly where the murrgrave is thickest, the silt is sown and
   the bank works stand: the ruled coupling ("the richest ground is one step from the
   killer") given a tide, so the step MOVES.
3. **The grab**: a pawn standing on the widened strip when its cell activates gets one
   `PawnFlyer`-shaped yank two cells toward the bed (the one violent moment, §1.1),
   then rides §1.3 like anyone else. Stored loose things on the strip become
   drift-eligible for the condition's duration.

**Tells, hours ahead, all shipped systems**: veil-fall litter on the bed visibly
accelerates (the kept tell — the §1.4(a) effecter reads the condition's ramp-in and
speeds up first); every sennefan snaps to alignment; **the murrol vanish upstream and
the nuudal leave the inner bank** — a `TsunamiFlight.Sweep`-shaped animal push (§1.1),
GravTide's "animals leave the beach before the wave does" learned properly; the stake
lamps swing (effecter); then the letter. The Compact's cast reads it coming (the
net-widow's warning, the well-keeper's chart) so talking to the houses has survival
value — danger pass D6(d), unchanged.

**What the surge never does**: touch the light. Skylights, glowers and plant growth
are untouched, deliberately — partly register (the famine D5 owns light), partly the
briefed engine subtlety: **cached plant growth rates assume surface sunlight via
`GenCelestial`, so a depth-darkening `GameCondition` would not be reflected in them.**
The undersurge is designed to never need what the engine cannot give it. (Where that
subtlety DOES bite is D9 lid-dark's "kelp pauses" — flagged there, not owed here.)

## 3. The sink terminus (danger pass D7 — RULED; specified, not re-asked)

**Ruled at the sitting (C1): recoverable by default, with the harsher Mod Setting
ladder.** This section only specifies.

- **The basin.** Placed by §1.2's genstep at the flow grid's low end — dark by
  construction (a sink is definitionally far from the wells: high ground gets the
  light, low ground gets the river), floored in everything the river ever took:
  litter, panes, shells, stakes, and one `RM_PickedWreck` reading as the sink's
  history. Carry ends here: the component drops the thing on a free basin cell.
  Items simply accumulate — **the basin is also the map's lost-property office**,
  which is what makes a breach (§4) recoverable at a price.
- **`RM_Hediff_Sunk`.** Applied on arrival to any pawn carried the whole way:
  downed-adjacent — Consciousness and Moving crushed, a slow severity ramp (silt,
  cold, exhaustion; a `HediffComp_SeverityPerDay` shape plus a small comp that stops
  the ramp when rescued/indoors), death in a day or two if unrecovered. XML plus one
  tiny comp; no new hediff machinery.
- **The rescue set piece.** Vanilla `JobDriver_Rescue` into the biome's worst ground —
  the dark between (the loohn's and the vaulisk's), possibly during the surge that
  caused it, at the end of the map from home. The design work is siting (dark, far),
  not code. A rescued pawn's hediff ramps down over a day; the letter closes warm.
- **The ladder (Mod Setting, ruled):** default **recoverable**; harsher
  **recoverable-but-injured** (a permanent lung/frostbite-analog scar hediff added at
  rescue); harshest **lost** — the pawn is gone at basin arrival, a death-letter in
  the river's register. Default never deletes a colonist silently: at "recoverable"
  and "injured" the pawn always arrives alive and the clock is the story.
- **Fold**: everything above lands inside `TWILIGHT_CHANNEL_CURRENT_1` — the carry
  always needed an end state; this is the end state (danger pass §3, verbatim
  posture).

## 4. The bank works — the immobile anchor prize (owner-picked)

**What it answers.** The Twilight's standing pressure is D5: the light walks away in
about a week, and the early game is chasing it. The bank works are the mid-game
answer the danger pass already named — *"immobile, current-fed, light-independent
wealth"* — the thing worth staying put for while the gold moves. The river never
walks. That is the whole pitch: **the skylights are rent; the river is a deed.**

**What it IS.** A chained installation of three buildings plus the boundary, built
into a generated **eddy** (§1.2 — two to four per map, where the carry releases;
position is the value, which is why the works cannot move):

1. **The weir — `RM_BankWeir`** (buildable; lattice-timber + net-cord, the Compact's
   own materials §3.1/§3.11 of the drop). Stands on eddy-margin cells; **arrests the
   drift on its cells** (§1.3's arresting building) and accumulates what the river
   delivers into an inner hopper: veil-fall flakes and the odd whole pane (harvest
   material), drifted items (yours back, or a surprise), waelune fetched up lit, the
   murrol that ride in slow enough to pick up by hand. **Job: tend the weir** (empty
   the hopper — hauling-shaped, constant). The weir's water-edge cells are the
   biome's second-richest gathering ground after the wells — the sessile layer
   crowds onto what the current delivers, picked by hand (⛔ not a fishing zone:
   owner-typed 2026-09-26, *"you don't fish at the bottom of the ocean"* — fishing
   is the SHORELINE'S verb; the floor's fish are hunted and its beds are gathered). The Compact's own weirs pre-exist on one eddy — the player learns the form
   by looking, never by being told (their practice: *drop the bundle in upstream,
   collect it at the weir*).
2. **The silt-trap — `RM_SiltTrap`** (buildable behind the weir). Slows the margin
   water; over days it **raises the fertility of adjacent `RM_BankSilt` cells**
   (a ticking comp writing a fertility offset — the engine route is a terrain swap
   to `RM_BankSilt_Rich`, the shipped idiom, never a live fertility patch). The
   sown bank (oruvell, illuvane, noothelm, sarrowhisk — drop §8.3) around a mature
   silt-trap is the richest farm on the planet's whole seabed. **Job: dredge**
   (periodic, or the trap clogs and the bonus stalls).
3. **The stake-line — `RM_BankStake`** (already owed by the drop; the works make it
   load-bearing). It is BOTH the farm boundary and the safety tell, at once, by
   construction: the stakes stand where the surge reaches, not where the calm ends —
   *the Compact set them for the flood, not the fair day* — and **thessmoss stops
   dead at the stake-line** (§3.8), so the turf itself draws the same line the lamps
   do. Everything inside the stakes is farm; everything past them answers to the
   river, some days including the strip you sowed (§2). **Job: re-drive stakes**
   (maintenance — stakes lose HP to the current's ordinary gnaw; a lapsed line is
   the first domino below).

**Yields, summed:** continuous current-fed harvest (pane material, flakes, hand-picked
murrol, returned drift), the second-best gathering ground, the best farm, and — because none of
it needs a skylight — **the only wealth on the floor that ignores D5 entirely.**
Maintenance-hungry by design: tend, dredge, re-drive — three standing jobs, so the
works hold pawns the way the light-chase holds pawns, and a colony that builds them
has chosen to LIVE here.

**Why the richest ground is one step from the current.** Physically: the silt and the
veil-fall the river concentrates are the fertility (the drop's murrgrave rule — the
lace maps the wealth). Mechanically: the fertile strip, the stake-line and the bed are
adjacent by generation (§1.2 paints them in that order, cell-adjacent). The player's
best ground is always one careless step — or one surge-widening (§2) — from the carry.
That coupling is the ruled design, restated here because every piece of §4 exists to
price it.

**The breach — one failure takes the whole thing downstream.** The weir carries HP
and a maintenance state (the re-drive/tend jobs feed it). An untended or battle-damaged
weir that meets an undersurge **breaches**: over ~an hour, with its own letter and a
distinct effecter (the hopper's catch visibly streaming out), (a) the hopper's whole
accumulated stock spills to the bed and rides the carry to the sink; (b) every loose
thing on the works' cells and the sown strip becomes drift-eligible for the rest of
the surge; (c) the stake-line downstream of the breach snaps stake by stake (an HP
cascade on a timer — audible, watchable, stoppable at any stake a colonist reaches in
time); (d) the silt-trap's terrain bonus reverts (the rich silt washes out). Buildings
other than stakes hold — the breach sweeps STOCK and BOUNDARY, never the colony's
walls, so it is a catastrophe of wealth and safety-legibility, not a base-delete. The
recovery is §3's basin: everything the breach took is lying in the dark at the end of
the river, in the loohn's parish — **the breach turns the sink set piece into a cargo
expedition**, which is D7's rescue with the colony's larder as the hostage.

**Tier**: every def above is invented and `RM_`; nothing routes through the Utinni
layer. The Compact's pre-built weir is Inhabited dressing on their eddy, ban 4 intact
(they never suffer for the player's sake; their weir never breaches — it is tended,
which is the lesson).

## 5. The dry river as a travel lane — the open exploration

**The ban, read carefully.** Ban 3 forbids a SWIMMABLE river: free, bidirectional,
pawn-powered movement in the channel. It does not forbid the channel MOVING you —
the 2026-09-26 ruling made that the mechanism. So there are three distinct things,
and the ban only kills the first:

| mode | what it is | ban 3? |
|---|---|---|
| **swimming** | pawn-powered, steerable, reversible movement in the bed | ⛔ banned, forever |
| **being carried** | one-way, no control, ends at an eddy/weir or the sink | ✅ the ruled mechanism |
| **riding** | *choosing* to be carried, with preparation | ← the open question |

The interesting version is the one the brief names: **a travel lane that is also the
biome's hazard.** The river is the floor's only fast road, it only runs one way, and
the price of using it is that everything §2 and §3 say stays true while you are on
it. Downstream in minutes; home again on foot. A lane you must *earn the reading of*
— stake-lines, weirs, surge tells — is the planet's lane-doctrine (the bedazzle's
grammar line) done properly; a lane with the danger patched out is a conveyor belt.

**Three rungs, cheapest first — each usable without the next:**

1. **Freight (already in).** Items drift (§1.3, ruled position); the weir arrests
   (§4). So *drop the bundle upstream, collect it at the weir* — the Compact's own
   practice — ships with the base mechanism, zero additional work. One-way bulk
   freight across the floor, brake included: everything worth carrying is alive or
   expiring, and the weir is not where the ship is. **BENCH position: this is
   simply true at ship time and needs no card.**
2. **The cargo float — `RM_CargoFloat`** (small XML + one comp). A buildable
   lattice-timber-and-bladder raft, minified-container-shaped: load it on the bank,
   push it in (a job), it rides the item drift whole and the weir arrests it intact.
   Protects the cargo from the basin scavengers if it overshoots (a float in the
   sink is recoverable unspoiled). Makes freight *deliberate* rather than
   opportunistic; still items-only, still inside the ruled mechanism. **BENCH
   position: build it with the works — it is the works' third job made portable.**
3. **The pawn ride.** A colonist steps in ON PURPOSE, wearing a **bladder-harness**
   (`RM_FloatHarness`, apparel: hoolimbre bladders + net-cord) that does exactly two
   things: caps carried speed at MARGIN cadence even in the centre (you ride high),
   and guarantees weir-arrest (a harnessed pawn is caught like a float; an
   unharnessed one is not — see card Q2). Arrives winded (a minor hediff), never
   harmed — *unless the surge is up or no weir stands downstream*, in which case the
   ride is exactly as stupid as it sounds and §3 is waiting. Fictionally this is not
   swimming: the pawn is cargo that packed well. Mechanically it is ~40 lines on
   systems already owed. **But it is the rung that flirts with ban 3's spirit** —
   "harvest and travel happen on the banks" reads as intent, not just mechanism —
   and the owner left the lane question open deliberately. **BENCH position: design
   says yes, gated hard (harness required, surge forbids, one-way only, weir
   mandatory) — and it is his call, not ours. Card Q1.**

What is NOT proposed at any rung: steering, paddling, upstream anything, a boat a
pawn pilots, or any UI that presents the bed as a road. The lane stays a river that
tolerates you, never a vehicle system.

## 6. Engine summary

| piece | new C#? | size | rides on |
|---|---|---|---|
| flow-grid genstep (`RM_GenStep_TwilightChannels`) | yes | small (~150 lines) | Grey's dressing-genstep shape; content drop §8.2 generation order |
| carry component (`RM_MapComponent_ChannelCurrent`) | **yes — the one real system** | medium (~300–400 lines incl. items, exemptions, arrest, settings) | MudSwallow's scan skeleton; teleport idiom (§1.1); nothing existing does this — measured, GravTide + our src + vanilla |
| bed/bank/stake/ford defs (`RM_ChannelBed`, `RM_BankSilt`, `RM_BankStake`, `RM_FordStones`) | no | XML | already owed by content drop §8.2 |
| litter-drift effecter (the tell) | no | XML + mote | vanilla effecter system; reads the flow grid |
| undersurge (`RM_GameCondition_Undersurge`) | no new system | tiny (multiplier + band read + one PawnFlyer yank + animal sweep) | §1.3's component; GravTide's `BandAt`/`TsunamiFlight` shapes |
| sink basin + `RM_Hediff_Sunk` + ladder | yes, small | small (hediff comp + terminus branch in the component) | ruled D7; vanilla rescue |
| bank works (`RM_BankWeir`, `RM_SiltTrap`) | small | small (arrest hook is a component check; hopper + dredge comps) | §1.3; hand-gathering on delivered stock; terrain-swap fertility idiom |
| breach cascade | small | small (~100 lines: state check, spill, stake timer) | weir comp + §2's drift-eligibility |
| stake-line as tell | no | XML | thessmoss `sowTags`/terrain bounds already in the drop |
| cargo float (`RM_CargoFloat`) | tiny comp | tiny | item drift + weir arrest |
| float harness (`RM_FloatHarness`) — **RULED IN (§7)** | tiny | tiny (~40 lines) | carry component's cadence + arrest flags |
| Mod Settings panel | no | XML/settings boilerplate | standing MOD_OPTIONS pattern |

**Net-new C# systems: ONE** — the carry component (everything else is a branch,
comp or parameter on it or plain XML). That is the honest cost of the ruling, and it
is why current + surge + sink + works are one item: they are one component wearing
four hats. Where it lives: `mandrake.rm.terminalbiomes` (shared by every sea that
later wants a moving floor), with the Twilight defs in the biome's own mod per the
split rulings.

## 7. Rulings — 2026-09-26 sitting, all three cards answered

Recorded on `TWILIGHT_CHANNEL_CURRENT_1`. Q3's second half is owner-TYPED
(quote-eligible); the rest are decisions taken by question card — our wording,
clicked, never quoted.

- **Q1 — the pawn ride: IN, as specced** (card) — deliberate, one-way, weir-to-weir,
  forbidden in surge. `RM_FloatHarness` moves from conditional to owed; failure
  fairness (what a mid-ride surge or missed weir does) is design-to-spec inside the
  carry component, not a new card.
- **Q2 — weirs catch people too** (card) — the sink is reachable only past the LAST
  weir; building weirs is also building safety rails, and the colony grows safer as
  it matures.
- **Q3 — breach at default, AND ported to normal rivers.** Owner typed: *"breach at
  default, and this should be ported to normal river tiles too!"* ⇒ The §4 breach is
  the factory-settings behaviour, and the weir / bank-works / breach system is owed
  on ordinary SURFACE river tiles as well — filed as `SURFACE_RIVER_WEIRS_1`. The
  carry component stays sea-floor (surface rivers are vanilla water, not the invisible
  dense current); what ports is the works: weir, silt-trap, stake-line, hopper, and
  the untended-weir-meets-flood breach cascade.

*(Not carded: everything §2–§4 states as ruled — D6/D7 verdicts are recorded at the
sitting and only specified here; the freight rung, which is the ruled item-drift
already; and every number, which is tuning, not a ruling.)*
