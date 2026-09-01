<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Propane and gas, deep design — a fuel field the size of a sea, and the danger IS the fuel

Canon anchor: `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` R-H6b
(the propane lakes are the nightside's condenser — the decay gradient's
exhaust, condensed; physically real at −42 °C and our painted curve runs to
−58/−80 °C past the terminator) and R-H9's "many paths to fuel" ruling
(helixien, propane, tar — priced by **access cost**, not yield, because a
gravship campaign that starves on one fuel source ends the save). Ties to
`design/Jawa/ownership_settlement_spec.md` where an industrial map has an
owning faction — a ruptured pipe on Hutt or Imperial ground is someone's
infrastructure, not a wilderness hazard.

The owner's framing, verbatim: *"Explosive propane lakes and gas vents? ...
Pipes of flowing propane on a map that, if ruptured, spew burning fuel and
simply won't stop (pump is very far away). Or leaking propane pipes that fill
a whole map with the stuff, making weapons fire too dangerous to entertain."*
Every clause gets a full section below.

---

## 1. Prior art, and where we go past it

- **Rimefeller** ships the closest analogue to "pipes that rupture": pipes are
  explicitly vulnerable, break during production, leave a spill needing
  cleanup, with fire a live threat. But rupture stops at **spill-and-clean** —
  no distant pump, no sustained jet, no quest shape. A chore, not an encounter.
- **Vanilla Chemfuel Expanded** proves the pipe-network *code* already exists
  and is documented — built specifically "to showcase what the new Pipe
  network code in the Vanilla Expanded framework is capable of." Our
  infrastructure layer (§4) is a data build on a proven framework, not new
  plumbing code.
- **Vanilla Helixien Gas Expanded** ships underground pipe routing and
  boilers; community notes say a broken segment leaves buildings reading
  "not connected" until manually deconstructed — rupture as **inert failure**
  (stops working), not active hazard. That gap is exactly the ask.
- **Vanilla gas mechanics** (tox gas, rot stink, deadlife dust, blind smoke)
  prove the engine already handles density-per-tile, diffusion, and
  gameplay thresholds — explosive saturation (§5) is a reskin of a solved
  system, not an invention.
- **"Gas Traps And Shells"** ships gas vents and corrosive gas as standalone
  hazard props — proof "a vent that periodically gasses an area" is a normal,
  buildable shape (§3 leans on it directly).
- **What nothing ships**: a saturation game condition that inverts combat
  doctrine as a standing map state; a rupture whose fix is a **traversal
  quest** rather than a repair job; or a liquid-propane **sea** authored as a
  destination rather than a node. All open ground.

---

## 2. The nightside liquid propane sea — the late-game expedition target

R-H6b is explicit: propane liquefies near −42 °C, and our own curve runs to
−58 °C at arc 150° and −80 °C at the antistellar point
(`ashkarr_paint.py:796`). **The lake needs no special pleading — the world is
simply cold enough.**

**Why it's late-game by nature, not by gate.** R-H10 makes the crossing itself
an engineering cost — the ship must be excellently heated to survive it. The
expedition self-gates on the campaign's own fuel-and-heat economy: you need
fuel (from the *other* two paths) to survive the trip that gets you the
third. R-H6b calls this circularity excellent and it shouldn't be smoothed
away — the lake becomes a reward for already having a functioning fuel
economy, not a bootstrap resource.

**What the sea offers, mechanically:**
- **A field, not a node** — harvested by a tanker operation (pumps, storage,
  the Utinni's own round trip, §6), intentionally the biggest single deposit
  on the planet. R-H9's pricing is paid entirely in cold-survival cost.
- **Standing ignition tension, not a scripted event.** A near-boiling liquid
  off-gasses continuously at its surface (physically correct), so any camp at
  lakeside runs §5's saturation math with cold as the added killer. "Standing
  next to a lake of liquid propane with an ignition source is a story that
  tells itself" — R-H6b's own words; mechanics should stay out of the story's way.
- **Propane-native fauna** (§7) at the lake margin — the in-fiction answer to
  why it hasn't simply boiled off.

**Mechanics sketch:** `RUT_PropaneLake` liquid terrain (flammable, background
off-gas rate feeding §5's saturation field) hand-authored on a specific
nightside tile — map content, never a worldgen feature. A tanker interaction
reusing whatever cargo framework the Utinni's own ship systems already use.

---

## 3. Gas vents on normal maps — the small, frequent cousin

R-H0 already places helixien pockets on volcanic/deep-desert tiles as a held
resource; gas vents are propane's small, local sibling — seeded near the
poison-forest/terminator seam or volcanic terrain where R-H6/R-H6b's chemistry
plausibly seeps close to the surface.

- **Timed/random ignition** — a periodic gas puff (`Gas Traps And Shells`
  proves this ships fine standalone) with a chance-per-tick of self-igniting
  once density crosses a threshold.
- **Harvesting caps** — a `CompVentYield` limits total extractable volume
  before the vent goes dormant: a *found* resource with a lifespan, not a
  build-and-forget generator, keeping R-H9's "no path stops the others
  mattering" rule intact.
- **The payoff**: a small-stakes version of the sea's core tension (fire near
  fuel) a starting colony can survive learning from, before the late-game sea
  raises the stakes to "the whole map."

**Mechanics sketch:** `ThingDef RUT_GasVent` (shape of an existing vanilla
steam-vent prop) + `CompVentYield` (small C#) + a local ignition roll on
vanilla's `Gas`/`GasGrid` density. No DLC required.

---

## 4. PIPE INFRASTRUCTURE — the owner's rupture spark, built out in full

> *"Pipes of flowing propane on a map that, if ruptured, spew burning fuel
> and simply won't stop (pump is very far away)."*

**Map dressing, not worldgen** — pipe networks belong on visited
settlement/industrial maps (a Hutt refinery, an Imperial depot, a
Rimefeller-style operation reskinned), staying inside the house rule while
delivering exactly the set-piece described.

**The core mechanic: an unquenchable jet, not a puddle fire.** Existing pipe
mods (§1) treat rupture as maintenance (stops working, or spill-and-clean).
Here, rupture is **actively, continuously dangerous** for as long as the pipe
stays pressurized:

- Rupture (fire damage to a segment, a raid breach, sabotage, a scripted
  beat) spawns a standing pressurized jet — hotter and louder than tar's slow
  smoky burn (see the tar doc §4c): fast ignition, wide light/heat radius,
  continuous rather than spreading.
- **It does not go out on its own.** `CompPipeRupture` pins the jet's
  fuel/lifetime to "network segment still pressurized" rather than a
  depletable terrain-fuel value — the only way to end it is to cut supply.
- **"The pump is very far away" is the design.** The shutoff is
  architecturally distant — a valve building elsewhere on the map (or
  off-map) that a `CompPipeNetwork` (built on the VEF `PipeNet` class, §1)
  must be reached and operated to depressurize. **Explicitly quest-shaped**:
  reach the pump, defended per the owning faction's security profile
  (`ownership_settlement_spec.md`'s per-faction response tuning already models
  "someone will come"), and shut it down while the jet burns and the clock
  runs. A `QuestScriptDef` is the natural authoring vehicle.
- **Escalation while unaddressed** — risk of igniting adjacent flammable
  stock (a natural pairing with a tar-adjacent industrial site, tying the two
  docs together) or pushing local saturation (§5) past threshold, rising
  linearly with time-on-map rather than spiking into an unsurvivable wall
  (anti-exponential discipline).

**Ownership tie-in.** A rupture on a faction's own map is their emergency;
the owning faction's guards-converging response is exactly what
`ownership_settlement_spec.md` already builds — this doc just gives it a
spectacular reason to fire mid-mission.

**Mechanics sketch:** `CompPipeNetwork` extending VEF `PipeNet`;
`CompPipeRupture` (new C#, the core original lift); a pump `ThingDef` with a
flickable toggle wired to network state; a `QuestScriptDef` template for the
pump-reach traversal. The single largest C# lift in this document — the
rupture-to-pump propagation is the genuinely novel piece.

---

## 5. GAS SATURATION as a map condition — the combat-inverting hazard

> *"...or leaking propane pipes that fill a whole map with the stuff, making
> weapons fire too dangerous to entertain."*

The most mechanically interesting idea in the brief: it changes what "good"
tactics *are*, not just the terrain they're played on.

**The concentration meter.** `GasSaturation`, a map-level 0–100% value tracked
by a `MapComponent` (area-level, with per-tile density layered on top via
vanilla's existing `Gas` field), rises from an unaddressed rupture (§4), a
chronic leaking joint, a vent cluster (§3) firing in sequence, or an authored
start-state on a dangerous location.

**Weapons-fire-as-hazard, blunt about its own math** (legible curve, per
anti-exponential discipline):

| saturation | effect |
|---|---|
| 0–20% | cosmetic haze, no mechanical effect — a warning register |
| 20–50% | ranged discharge risks an escalating **deflagration** — a localized fireball at the shooter's tile, hitting shooter and allies as readily as the target |
| 50–80% | deflagration odds high enough that ranged combat is a coin-flip; melee, spark-free thrown weapons and unpowered tools stay safe |
| 80%+ | **any** heat source — muzzle flare, a lit cigar, an arcing conduit — risks a **flashover**: the whole contiguous volume ignites at once. Rare and telegraphed (rising haze/fx, a warning line), never a silent gotcha |

**What it forces, and why it's good design rather than a gimmick:** it
inverts the colony's default "who has better guns" toolkit. Under high
saturation, guns become the *worst* tool, and melee/stealth/EMP-ion play
(the Star Wars roster already carries a good reason for ion weapons) becomes
the *correct* choice, not merely alternative — a mechanic that changes the
answer to "what do I bring" without making anyone stronger: danger-flavored,
not power-flavored, exactly what anti-exponential discipline rewards.

**Saturation as heist opportunity.** Guards are under the same rule. A crew
that identifies or deliberately triggers (§3/§4) saturation on a target
turns the hazard into a tactical asset, read directly against
`ownership_settlement_spec.md`'s crime suite (pickpocket, night burglary,
smuggling past gate searches) — a saturated depot is a depot whose guards
can't safely shoot back.

**Mechanics sketch:** `MapComponent GasSaturationTracker` (new C#, core lift)
exposing the float and a deflagration-safe query; a careful, isolated check
at the top of the ranged-fire-resolution path (not a scattered patch) rolling
deflagration on discharge; reuses vanilla `Gas`/`FleckMaker` for the haze
visual entirely. Flagged as the **riskiest single piece of C# in either
document** — not because the idea is weak, but because weapon-fire code is
exactly what breaks other mods' assumptions if patched carelessly. Needs real
playtesting before it ships live.

---

## 6. Ship refueling economy — tanker runs

The propane sea's whole campaign-side reason to exist is as the best single
deposit, reached at the highest fixed cost (cold survival, R-H10) — which
only pays off with a concrete loop:

- **Tanker capacity as a real number** against the Utinni's existing
  fuel-storage stat — a lakeside haul should fill it close to capacity in one
  trip, legible as "the run that actually solves the fuel problem" versus
  helixien/tar's steadier trickle.
- **The return trip carries the same cold-crossing cost as the outbound one**
  — R-H10's heating requirement doesn't waive itself with a full hold. Worth
  leaning into the irony: the fuel that solves the ship's heating problem is,
  for the length of the crossing, also the cargo most likely to end the
  mission if fire-safety margins slip. A genuinely tense return leg.
- **A standing tanker route as colony infrastructure** turns the sea from a
  one-off set-piece into a repeatable economic anchor — the payoff for the
  earlier cold-engineering investment (R-H6b: "the ship must survive the cold
  to reach the thing that keeps it warm... that circularity is excellent").

**Mechanics sketch:** reuses the Utinni's existing vehicle-cargo/hauling
framework — no new resource-hauling mechanic proposed; this section is
economy pacing, not new C#.

---

## 7. Propane-dwelling creatures — why the lake is alive

Mirrors the tar doc's §5 in structure, applying the owner's "creatures that
emerge when disturbed... maybe that's why the stuff is there" logic to the
cold-side deposit, but the physics differ.

**The lake's origin needs no creature to explain it** — R-H6b already
establishes it as the decay gradient's exhaust, condensed by cold alone. What
a creature *can* explain is why it hasn't frozen solid or evaporated to
equilibrium: an organism that actively metabolizes the hydrocarbon influx,
keeping the lake dynamic — cold-adapted life that doesn't merely tolerate the
propane but **eats** it, per R-H10's rule that nightside creatures must
genuinely enjoy their conditions.

- **"Emerges when disturbed"**: a lake-margin creature living submerged or
  crusted at the liquid/frost interface — a cousin of the tar doc's
  "surface is sometimes a living lid" — surfaces defensively when a tanker's
  pumping or a raid's gunfire (extremely dangerous per §5) disturbs it.
  Reuses the same dormant-until-disturbed pattern proposed for the tar
  creature.
- **Why it matters for danger, not just flavor**: a fight here happens inside
  the most flammable location on the planet, reinforcing §5's
  melee/stealth-favoring posture from a predator-threat angle rather than a
  deflagration one.
- **Untransportable per R-H10** — hauled dayside without deep refrigeration,
  it dies of heat; any faction shown keeping one alive dayside is making a
  loud, expensive, legible statement about its reach.

**Mechanics sketch:** `PawnKindDef` (placeholder prefix only) with the same
dormancy comp used for the tar lurker; comfyTemp bands set per R-H10's
"must genuinely enjoy cold" rule, verified against `statBases`, never the
name. No new Thing categories.

---

## 8. Interplay — fire ecology and tar, tied off explicitly

Three hydrocarbon systems (R-H9's table: helixien/volcanic, propane/nightside,
tar/Pyrelands-margin) occasionally touch, and that's where the best
set-pieces live:

- **Propane vs. R-H4's fire ecology** — physically excluded from direct
  interaction (deep nightside vs. dayside Pyrelands, R-H10's hard thermal
  barrier), but thematically twinned: R-H6b already calls them "two opposite
  poles of the same design, at opposite ends of the same world."
- **Propane vs. tar, mechanically real** — an industrial map can plausibly
  pipe both past each other, since R-H9 places tar at the Pyrelands margin, a
  dayside/volcanic-adjacent location a helixien-and-tar operation might
  already occupy. A dual rupture (tar's smoke cutting visibility while a
  propane jet burns hot nearby) is a genuinely great single-map set-piece,
  costing nothing beyond placing both infrastructure types on one authored
  map.
- **Both feed §5's saturation logic once ignited** — mechanically distinct
  (particulate vs. explosive vapor) but teaching the same "put the guns down"
  lesson.

---

## 9. Build ladder

**v1 slice** — provably fun with the smallest system:
- `RUT_GasVent` (§3) with timed venting and a self-ignition roll — data-mostly.
- One hand-placed nightside propane-lake tile (§2), harvested by a basic
  hauling interaction — a resource node first, tanker-scale framing in v2.
- `GasSaturationTracker` (§5) wired to just the vent's local density — proves
  the "guns become dangerous" hook before pipes exist to feed it.

**v2** — the pipe-rupture spark, built out fully:
- `CompPipeNetwork`/`CompPipeRupture` (§4) on an authored industrial map, the
  standing jet and distant-pump shutoff as a `QuestScriptDef`.
- Full saturation band table (§5) live across an entire authored map, with
  the melee/stealth/EMP combat shift as a real playtested state.
- Tanker-run economy (§6) formalized against the Utinni's real fuel-capacity
  numbers.
- Lake-margin creature (§7) with dormancy comp, tied to pumping/gunfire
  disturbance.

**Dream** — the full system, played out:
- A named heist location built around §5's "saturation as opportunity" read
  — guards constrained the same as the player, playable against
  `ownership_settlement_spec.md`'s crime suite.
- The tar/propane dual-hazard industrial map (§8) as a signature authored
  location.
- A flashover-tier saturation event (§5, 80%+) as a rare, telegraphed,
  campaign-memorable set-piece — the map that gets talked about after the run.
