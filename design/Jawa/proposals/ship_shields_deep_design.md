<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# Environmental shields — gating access to the planet, not winning fights

Grounding docs: `design/Jawa/worldbuilding/gravship_flight_invariants.md`
(required components, power/fuel mechanics, module footprint), `design/Jawa/
worldbuilding/setting_physics.md` L6/L6a/L6b/L9 (combat deflector shields —
deliberately NOT what this proposal is), `design/Jawa/research_tree_taxonomy.md`
(THE SHIP tab, Memory Core chain, tech gating), `design/Jawa/worldbuilding/
hydrology_and_fire_ecology.md` (the hazard geography this gates access to).
§4's shield-collapse drama also draws on `research/Jawa/rimworld_weather_mod_concepts.md`
§23 "Weather and Gravships" (countdown framing, launch/mishap penalties under
severe conditions) — only its fire-adjacent framing is used here; that
sheet's general weather-gravship modifiers are a different writer's lane.

**The owner's spark, verbatim:** *"Could the ship have shields installed that
help it survive such hostile elements and thus are required to go onto some
maps late game?"* This proposal is a literal answer: shields as **environmental
survival equipment**, not combat power. It deliberately does not touch L6's
plasma-deflector combat shield — that stays what it is (a personal/vehicle
defence against blaster fire and lightsabers, worn not built, defeated by slow
matter). This is a *different* class of hardware, playing a different role:
**access, not defence.**

**House rules honoured throughout:** no worldgen — every shield gates entry to
a hand-placed map region that already exists in the frozen Ash'karr build,
never a generated one. Anti-exponential — a shield does not make the ship
tougher in a fight; it makes a place reachable that was not reachable before,
and it costs real resources the whole time it's doing that. No player-scalable
ship weaponry (setting_physics.md guardrail 5) is untouched — this proposal
adds zero weapons.

---

## 1. Why this is the anti-exponential answer, stated first

The obvious failure mode for "the ship gets shields" is power creep: shields
as an upgrade that makes the ship strictly better, stacking with everything
else, until survivability inflates every session. **The fix is that these
shields do not defend against attack at all.** They defend against **place** —
heat, cold, particulate, spore load — the specific hazard classes that R-H0
through R-H10 and `desert_world_design.md` already built into the map as
reasons some tiles kill you by simply existing on them. A combat shield makes
you harder to kill. An environmental shield makes a *tile enterable*. Those
are different axes, and keeping them different is the whole proposal.

This also answers the "why gate it at all" question honestly: on this planet,
the late-game maps are not guarded by tougher raiders, they are guarded by
**physics** (the firestorm Pyrelands' standing burn, R-H4; the nightside cold
that inverts on crossing the terminator, R-H10; the deep dust; the ocular
forest's spore/toxin load, R-H7). A raid can be out-fought. Physics cannot —
it can only be *equipped for*, and that is precisely the kind of gate this
campaign should prefer: **a checklist, not a boss.**

---

## 2. The four environmental shields — one per hazard class already on the map

Each is a gravship module (a `Building`/`GravshipComponentTypeDef`-style
facility, per `gravship_flight_invariants.md` §2's component-type vocabulary),
not a personal item. It protects the ship and a bubble around it, never a
lone colonist wandering the map — venturing outside the bubble is a real
choice with real consequences (§4).

### 2a. Thermal veil — for the Pyrelands' standing burn

Gates: the Pyrelands (`the_fire_ecology_deep_design.md`'s Stage-2/3 fire
zones), and any volcanic-tile approach (R-H0).

- **What it does:** holds ambient heat load and radiant fire-heat off the
  ship's hull and interior, at a bubble radius. Without it, sustained
  proximity to an active burn or a volcanic tile cooks the ship's own systems
  — a slow, compounding thermal-stress tick against exposed components, the
  hull-scale equivalent of a colonist's `Heatstroke` hediff.
- **Fuel/power shape:** the highest **continuous power draw** of the four —
  always-on while landed in-zone, chemfuel-hungry because it is doing
  thermal work, not electrical — ties into the same "many paths to fuel"
  economy (R-H9) rather than a new resource.
- **Vulnerable emitter:** an external radiator/vent array, necessarily
  hull-mounted and exposed (you cannot radiate heat from inside an insulated
  box) — the one component a hostile actor (raiders, wildlife, flying debris
  in a Fire Whirl, per the fire-ecology proposal §3) can target to collapse
  the shield early. The thing keeping you alive here is also the thing an
  enemy can break to end that.

### 2b. Cryo envelope — for the nightside and the propane sea

Gates: everything past the terminator (R-H6/R-H10's decay gradient, the
propane lakes of R-H6b).

- **What it does:** the mirror problem of the thermal veil — R-H10 rules the
  nightside "as cold as the dayside is hot," with nightside biology taken
  dayside dying of heat and vice versa. A ship with no cryo envelope crossing
  the terminator suffers the ship-scale version: crew-space heating alone
  (already a gravship cost per R-H10's consequence ①) doesn't stop exposed
  systems cold-seizing. The envelope is what makes landing on the nightside
  survivable rather than "land and immediately need to leave."
- **Fuel/power shape:** the opposite profile from the thermal veil — lower
  continuous draw but a heavy **startup fuel spike** each activation, the
  cost of purging heat out of a system before it can hold cold in. This
  makes cryo trips naturally **expedition-shaped**: fuel committed up front,
  no casual hop in and out.
- **Vulnerable emitter:** the coolant-loop radiator — and the interesting
  failure is that **the propane lakes themselves are a hazard to it**: any
  ignition source near a failing cryo envelope beside a propane lake is the
  "story that tells itself" the hydrology doc already flags. A collapse
  there isn't just "now it's cold," it's "now something can ignite the sea
  you're floating next to."

### 2c. Particulate screen — for the deep dust

Gates: `desert_world_design.md`'s deep-desert hazard tiles and any dust-storm
biome (`SW_DrySandstorm`/`VEE_DustStorm`/`VGE_DustCloud`-class weather already
measured live on this modstack per that doc).

- **What it does:** the cheapest and most mundane of the four, deliberately —
  it is a mechanical filtration/electrostatic screen keeping abrasive
  particulate out of thruster intakes, joints and vents. Without it, extended
  time in a dust-storm-active biome accelerates equipment wear (L12's "sand
  fouls mechanisms" already establishes this as a setting-physics fact for
  colonists and droids; this is the ship-scale version) — components degrade
  faster, thrusters lose efficiency, and eventually the ship becomes
  unlaunchable from neglect rather than from any single event.
- **Fuel/power shape:** low power draw, but **maintenance-cost gated** rather
  than fuel-gated — its cost is components/steel upkeep over time (filter
  replacement) rather than a burn rate. This is deliberate variety: not every
  shield should cost the same resource, or the loadout decision (§3) collapses
  into "which one is cheapest" instead of "which one fits this trip."
- **Vulnerable emitter:** none, really — its failure mode is **gradual, not
  dramatic**. No single point of attack; it just stops working if unmaintained,
  which makes it the shield most suited to being forgotten and then
  discovering the cost of having forgotten it. Good texture against the other
  three's sharper collapse drama.

### 2d. Spore membrane — for the ocular forest headwaters (maybe)

Gates: the high-valley ocular forests of R-H7 — "rare and horrible," per that
ruling, and the one biome where a ship module gating access is most
narratively appropriate, because the hazard there is *biological
contamination*, not physics the ship can simply outmuscle.

- **What it does:** a positive-pressure membrane (the same register as a
  cleanroom seal) keeping the ocular forest's reproductive spores and alien
  toxins (R-H7) from entering the ship's interior atmosphere at all — this is
  the one shield that protects the *crew inside the hull*, not the hull
  itself, because the hazard is inhalation/contact, not thermal or kinetic.
- **Fuel/power shape:** the lightest power draw of the four but the highest
  **component/rare-material cost to install** — filtration membranes are
  precision-manufactured, not something a scavenger clan improvises from
  scrap the way the particulate screen can be. This should be the shield the
  player is proudest to have built, not the one they reach for casually.
- **Why "maybe":** R-H8 already rules the ocular forests (and the strange
  biomes generally) as `Ascendant Helix` territory and a live ancient-bioweapon
  test ground — a membrane that protects against it is good fiction, but it
  risks implying the player can safely strip-mine the single most horror-coded
  biome on the planet. Recommend gating this shield's *research* behind a
  Memory Core / Ascendant Helix contact beat (§5) specifically so acquiring it
  is a story event, not a shopping trip — the horror stays horror even once
  the tool exists.

---

## 3. The decision texture — limited hull space, real loadout choices

Per `gravship_flight_invariants.md` §6, hull substructure support is a hard,
measured cap (live-tuned via the Bigger Gravships slider on this modstack,
but the design point holds at any value): **every module competes for the
same finite footprint, power budget, and conduit reach as thrusters, fuel
tanks and everything else that makes the ship fly at all.** Four environmental
shields is deliberately more than a ship can comfortably carry all at once —
that oversupply is the design, not a gap:

- **Before a Pyrelands expedition:** thermal veil, obviously. Particulate
  screen if the route crosses deep desert first. Cryo envelope and spore
  membrane are dead weight — uninstall or leave dry-docked.
- **Before a nightside crossing:** cryo envelope, mandatory. Everything else
  is drag on fuel margin (R-H10 already makes nightside crossings an
  "engineering decision," per that ruling's consequence ①) — a player who
  drags the thermal veil along on a cold trip is paying continuous draw for
  a shield doing nothing.
- **A ship that tries to carry all four permanently** pays continuous power
  and fuel-burn cost across every trip, for protection it only needs on some
  of them — which is the honest cost of "install everything," and it should
  visibly hurt the fuel economy enough that specializing the loadout per
  expedition is the better play almost every time.

This is where "which shields to install" becomes a real pre-expedition
decision on par with choosing a caravan's gear — not a checkbox, a trade.
**Uninstalling and swapping should be possible but not free** — matching how
the grav engine itself can be uninstalled and moved (per the flight
invariants doc) but substructure requalification isn't instant — so the
player plans the trip around the loadout, not the other way around.

---

## 4. Failure states — the bubble, not a wall

None of these shields make the hazard vanish. All of them define a **bubble**
around the ship — inside it, survivable; outside it, the raw hazard applies
exactly as it would with no shield installed. This does three things at once:
it keeps the shields cheap to implement (they gate a radius check, not a new
hazard-immunity flag scattered across every system that touches heat/cold),
it keeps colonists who leave the ship in genuine danger (per
`setting_physics.md` guardrail 6, telegraphed danger, not unavoidable
lethality — the bubble edge is visible), and it gives suits (§4a) a job.

- **Partial protection zones.** The bubble is not binary pass/fail at its
  edge — like RimWorld's existing temperature-gradient rendering around a
  heater, protection fades over a short band rather than cutting off sharply,
  so a colonist stepping just past the edge gets a warning tick before the
  full hazard applies, not an instant death.
- **Venture beyond the bubble in suits.** Thermal-rated suits (Pyrelands),
  cold-rated suits (nightside), respirator gear (spore/particulate) — already
  the natural personal-scale complement to a ship-scale shield, and already
  the kind of apparel this campaign's armoury supports without new mechanics
  (a `statBases` insulation/toxic-resistance stack, same as any other
  apparel). The ship shield buys the *base of operations*; the suit buys the
  *away mission* — two tiers of the same problem, priced separately, which is
  good texture and not a new subsystem.
- **Shield collapse mid-map is the drama beat.** Fuel runs out, the vulnerable
  emitter (§2) is hit or breaks down, or the player simply outstays the
  fuel budget they brought — and the bubble starts shrinking or drops
  entirely, with a telegraphed warning window (an alarm/countdown, not an
  instant cutoff) before the raw hazard reaches the ship interior. This is
  the "evacuate now" scene the owner's spark implies: not a fight, a
  ticking clock, and the correct response is *leave*, which is exactly the
  gravship campaign's existing spine (R-H9's "many paths to fuel": the whole
  arc is keep moving) rather than a new genre of encounter. Read the two
  clocks against each other, per `rimworld_weather_mod_concepts.md` §23's
  framing — *"Firestorm arrival: 7 hours / Gravship repair completion: 9
  hours"* — the same countdown-race shape, with the shield's fuel margin
  standing in for the repair clock: a Pyrocumulus Storm (fire-ecology
  proposal §3) closing in on a thermal veil already running low is exactly
  this scene, told with equipment the player installed rather than a
  scripted event.
- **A shield failing is not a wipe.** Per the anti-exponential and
  no-unavoidable-lethality guardrails, a collapsed shield should give the
  player enough warning time to lift off or retreat to the suit-protected
  minimum, not simply end the expedition. The interesting failure is
  "you have to leave early and empty-handed," not "you die."

---

## 5. Acquisition — through THE SHIP tab, and through story where it should be

Per `research_tree_taxonomy.md` §1, THE SHIP is already the ruled non-linear
research tab carrying gravtech, VGE systems, and the **Memory Core chain** —
"hidden until the ship surfaces them — research as revelation." Environmental
shields belong here, not in a generic industrial-tech line, for the same
reason the tab exists: **the ship should reveal its own late-game capability
through play**, not through a linear unlock ladder visible from turn one.

- **Thermal veil and particulate screen** are the two "common-access" shields
  per the taxonomy's four access classes (§7: common / faction-held via
  techprints / jawa-special / ship-only) — reachable through ordinary Ship-tab
  research once the tree surfaces them, priced at T2–T3 cost bands (1600–5000,
  per the ruled cost table), because they gate hazards the player can already
  see and choose to approach (fire, dust) rather than hazards discovered by
  crossing an unknown line.
- **Cryo envelope** sits slightly higher — it is what makes R-H10's
  terminator crossing possible at all, and the taxonomy's T3 Spacer band
  ("steep + Visibility cost") fits: crossing the terminator is itself a
  Visibility-costing act (per the theology-drip mechanism already ruled for
  the tab), so gating the tool behind a comparable cost keeps the two
  consistent.
- **Spore membrane is `jawa-special` or ship-only-gated**, per §2d's
  recommendation above — surfaced through a Memory Core revelation or an
  Ascendant Helix contact beat (R-H8's gene-cult, already ruled as present
  near the strange biomes specifically), so the player earns entry to the
  planet's most horror-coded biome through a story beat rather than a
  research-point grind. This is the one shield that should feel *given*, not
  *bought*.
- **Coverage or refuse, per the taxonomy's own validator discipline (§4):**
  whichever of these four ships as manifest rows must resolve to a real
  research chain with real prereqs before launch — no shield def should ever
  sit unresearchable with no path to it, the same "zero rows is a failure"
  discipline the taxonomy already enforces on the wider tree.

---

## 6. How map entry checks the requirement — diegetically, not a hard wall

The owner's phrasing — "required to go onto some maps late game" — could read
as a hard gate (game refuses to let you land without the shield). **This
proposal recommends against a hard wall**, for the same reason the launch
refusal list (`gravship_flight_invariants.md` §1) is the right model for
*flight* but the wrong model for *environment*: a flight refusal is binary
because flight is binary (you either fly or you don't). Survival on a hostile
map is not binary — it is a rate.

- **Warning letters on approach.** Before landing on a hazard-flagged tile
  without the matching shield installed, the player gets the same kind of
  diegetic warning RimWorld already uses for hostile-faction or
  extreme-temperature landing sites — readable, skippable, and honest about
  what's coming.
- **Escalating damage ticks instead of a refusal.** Land anyway, and the
  hazard applies from tick one at full raw strength (no shield, no bubble) —
  the same consequence a shielded ship risks only if its shield later fails
  (§4). This means an experienced or reckless player *can* attempt an
  unshielded landing — briefly, at real cost, exactly the way a player can
  already choose to walk a colonist into deep desert without water. The
  shield doesn't gate the ability to try; it gates the ability to **stay**.
- **Why this is the better answer:** it keeps the shields in the "equipment
  that makes an expedition viable" register rather than the "key that opens
  a locked door" register — consistent with the anti-exponential framing in
  §1, and it means a shield failure mid-map (§4) and a no-shield landing are
  the *same mechanical event* viewed from two directions, rather than two
  separate systems to build and maintain.

---

## Build ladder

**v1 slice.** Thermal veil and particulate screen only — the two hazards
already fully specified elsewhere in this design (the Pyrelands fire loop;
`desert_world_design.md`'s dust/sandstorm weather, already measured live on
this modstack). Ship as gravship facility modules with power draw + fuel/
maintenance cost per §2, a simple bubble-radius protection check, and the
diegetic warning-letter-then-damage-tick landing behavior from §6 — no hard
wall, no new incident category. Prove the loadout-choice texture (§3) works
at the colony/expedition-planning level before adding the other two.

**v2.** Cryo envelope, tied to R-H10's terminator-crossing consequences and
priced at the T3 Spacer band per the research taxonomy (§5). Shield-collapse
mid-map as a real telegraphed event (§4) with the evacuate-now drama beat,
plus suits as the personal-scale complement for all three shipped shields.
Wire the vulnerable-emitter targeting (§2's per-shield failure point) into
combat/hazard systems so a collapsed shield reads as caused, not random.

**Dream.** Spore membrane, gated behind a Memory Core / Ascendant Helix story
beat rather than ordinary research (§5), unlocking the ocular forest
headwaters as a reachable — but never safe — late-game destination. Partial-
protection gradient rendering at the bubble edge (§4) polished to the same
quality as RimWorld's existing heater-radius visualization. A fifth,
undesigned shield class held in reserve for whatever hazard the eventual
crystalline-caverns/glowing-landscapes authoring pass (R-H6c) turns out to
need — this proposal's module shape (facility, power/fuel profile, vulnerable
emitter, access class) should be reusable without a rewrite.
