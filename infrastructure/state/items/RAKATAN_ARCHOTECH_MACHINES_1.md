# RAKATAN_ARCHOTECH_MACHINES_1

Owner's vision, spoken 2026-09-15 at the bench. Recorded for a design session with
him later; nothing here is built or ruled yet beyond the archotech equivalence he
stated outright.

## The trait

Rakatan technology has one defining engineering character: **it is ROBUST, it
SURVIVES, and it degrades gracefully whenever possible.** That is the trait the
whole mod expresses.

Owner, verbatim: *"Their ships are ancient and still somewhat functional. Their
batteries just slowly lose capacity over millenia yet still work. And if we could
refurbish them, they would exceed modern technology even in a still kludged
manner."*

So the failure curve is the point. Rakatan things do not stop working — they get
weaker, and they keep going. A modern machine breaks; a Rakatan machine sags. And a
refurbished one **beats** modern equipment while still visibly being a kludge.

## What changes about the existing mod

`src/RimMandrake/WreckedMachines` today is about repairing big machines **in place**.
The owner's judgement on that: *"that's excellent"* — it stays.

Two additions:

1. **Study the machine as the research.** Owner: *"Hopefully we can structure it to
   actually have you study the MACHINE itself as part of the 'research.'"* The
   artefact in front of the pawn is the research subject — not a bench, not an
   abstract project. Understanding comes from the thing.
2. **Mobile structures are in scope.** Owner: *"I would now formally like to add that
   other mobile structures should also be included into the mod."* Not only fixed
   installations.

## Archotech is Rakatan — a ruling, stated outright

Owner, verbatim: *"Archotech in the game now officially means Rakatan Ancient
technology."*

This reinterprets vanilla content rather than adding to it: *"The famous Rimworld
'archotech battery' can now be explained."* Every archotech thing in the game
becomes a Rakatan artefact, which retroactively explains why it is absurdly good and
absurdly rare.

⚠️ This has reach beyond this mod — anything in the campaign that references
archotech inherits it. It wants a dated line in `canon.yml`, drafted and awaiting
his yes.

## Sacred loot, and the ship that loves it

Found machines are added to the ship by the player as sacred loot. The ship loves them,
and as it regains the ability to heal itself, they improve with it.

Two coupled ideas to design against:

- **A found artefact arrives at a rung** — Wrecked, Kludged or Refurbished — and seating
  it on the ship is an act with religious weight, not just a stat gain.
- **The ship's self-healing lifts the artefacts with it.** They improve as it does.
  So the player's relationship to these objects is cumulative and long-arc, and the
  ship is the thing that redeems them.

## Refurbishment has a cost and a progression — owner, 2026-09-15

Owner, verbatim: *"introduce the concept that refurbishment requires Ancient
Components, a truly scarce and valuable resource as well as the tech to do so (from
the ship). At first manual refurbishing is all that's possible, but eventually the
ship's auto-repair systems will turn back on that slowly repair ship structure and
refurbish ever-larger machines onboard automatically."*

Three things this fixes at once — it gives refurbishment a real price, it makes the
ship the source of capability rather than a passive container, and it turns the whole
mod into a long-arc progression instead of a repair verb.

- **Ancient Components** — a truly scarce, valuable resource. The gate on every
  refurbishment. Scarcity is the balance lever for "refurbished exceeds modern"
  (§ the power-curve question below): the ceiling is enforced by supply, not by
  nerfing the payoff.
- **The tech comes from the ship.** Refurbishment capability is not a research bench
  the player builds; it is granted by the ship as it recovers. So the ship's own
  healing arc and the player's capability arc are the same arc.
- **Manual first, automatic later.** Early game: every refurbishment is hand-done, one
  machine at a time. Late game: the ship's **auto-repair systems come back online**,
  slowly repairing ship structure and refurbishing *ever-larger* machines onboard
  without the player. The scale of what can be automatically refurbished is itself the
  progression meter.

⇒ Note how this couples to the sacred-loot idea above: the artefacts improve as the
ship heals, and the ship's healing is what unlocks refurbishing them at all. The
player's job early is to feed a convalescent machine; late, it feeds itself.

## Ruled at the bench — owner, 2026-09-15 (design session)

**0. 🔴 ARCHITECTURE — two mods, and the dependency points one way.** Owner, verbatim:
*"the wrecked machines mod should be independent of the god favor... it should be its
own stand-alone mod (RimMandrake level) and the Salvation Engine should require it."*

**THREE layers, each requiring the one below** (the middle layer resolves the tier
conflict — owner ruled it 2026-09-15, same sitting):

| layer | tier | owns | says "Rakatan"? |
|---|---|---|---|
| **WreckedMachines** | `RimMandrake` — any RimWorld game | the three-grade ladder, refurbishment, Ancient Components, study-the-machine, mobile structures, worth-by-size, its own Mod Settings. **Complete and playable in a vanilla game** — generic ancient wrecked machines, no faction, no setting | ⛔ never |
| **the Rakatan skin** | `RimStarWars` | renames and reskins the base machines as Rakatan: labels, descriptions, art. Thin — a reskin, not a mechanic | ✅ yes |
| **Salvation Engine** | campaign | every god reaction, the reliquary sockets, the veneration precept, the ship-raises-the-floor mechanic | ✅ yes |

**WreckedMachines knows nothing about gods, nothing about the Utinni, and nothing about
Star Wars.** Dependencies point downward only; no layer ever reaches up.

⇒ Two consequences worth holding onto. This **dissolves** the cost flagged against
per-relic allegiance during the session — divine coupling is no longer a permanent
property of the machine mod, because it lives two layers above it. And the base mod is
genuinely publishable to strangers, which is the test of whether the neutrality is real.

🔴 **The discipline this buys must be enforced downward: not one Rakatan word may leak
into the `RimMandrake` layer** — not a defName, not a label, not a description, not a
comment. Any leak collapses the three layers back into one.

**1. The ladder.** Four rungs. One ladder for every machine, fixed or carried.

| rung | capability vs. the original | reads as |
|---|---|---|
| **Wrecked** | 0.001 | inert. A sacred object, not a machine. |
| **Kludged** | 0.2 | works, badly, visibly bodged. |
| **Refurbished** | 0.75 | the ceiling a player normally reaches. |
| **the original** | 1.0 | the ordinary modern machine. No tier name of its own. |

"Repaired" is not a level. It is a synonym for the original, so no def uses it.

**1.0 is the unmodified donor def** — the ordinary machine you could have built anyway.
A Mod Setting, **default OFF**, allows restoration all the way to it; with it off, 0.75
is the cap. So a Refurbished machine is a substitute for something out of reach, not a
better version of it: three-quarters of a working machine, built from scrap, when you
could not have built the real one at all.

**Every ratio is player-tunable** — the three numbers are defaults, not constants.

⚠️ **Ratios are per device class.** 0.001 is the battery number, chosen so a dying
battery flickers like a faint LED. A Wrecked factory needs its own value, and nobody has
set one.

Each rung is a discrete state with its own stat block and its own sprite — not a capacity
curve, not a per-subsystem wear model. **Worth scales with size**: a factory is worth far
more than a battery at the same rung.

**defNames.** `_Wrecked` and `_Kludged` are already correct. `_Repaired` is
donor-identical, so it is the 1.0 case and needs no tier def of its own. **The 0.75
`_Refurbished` tier does not exist yet and must be authored.** Stepping stays vanilla 1.6
`replaceTags` — build the next tier's blueprint over the old footprint, ordinary
construction, no C#.

⛔ **Cosmetic changes need permission first.** Anything touching art, skin, heads, eyes or
`renderNodeProperties` may break animated faces — ask rather than fix. That covers this
mod's `texPath` decisions and every sprite in the ladder.

**2. 🔴 Nothing equals or exceeds the original.** Owner, verbatim: *"There is nothing
beyond or even equal to the original."* The ladder is **asymptotic, capped at 0.75 by
default** — a Jawa hand approaches the machine's original function and never arrives,
unless the player switches the cap off himself.

⛔ Kills any grade that surpasses the original.

**3. ⛔ "Refurbished exceeds modern technology" is WITHDRAWN.** The owner's early vision
said a refurbished machine *"would exceed modern technology even in a still kludged
manner."* Ruling 1's 1.0-is-the-donor-def settles it the other way: 0.75 is **below**
modern, and that is the intent, because the mod is for when modern is not available to
you at all.

⇒ The power curve question is therefore closed, and not by scarcity or by theology. **A
refurbished ancient machine can never out-perform a machine you could simply have
built.** Its value is availability, not power. Nothing in this mod needs balancing
against a fear of it being too strong.

**4. 🔴 Reaching for the top grade is PRIDE.** Owner, verbatim: *"Reaching towards it
would definitely please Ozzik and anger others."* Note the inversion from the design's
first framing: the offence is not surpassing the ancients, it is **presuming you could
make their work whole again.** Which gods anger, and whether Rekko is among them
(his own body-vision is full restoration, which this rules impossible), is UNRULED.

**5. Sacredness is SOCKETS + PRECEPT, layered — and it lives in Salvation Engine.**
Relics are seated in hull reliquary sockets — persistent, not consumed, each granting a
boon — alongside an ideoligion precept venerating them (mood near relics, a ritual to
seat one, real fallout for scrapping or selling). Per ruling 0 this is **not**
WreckedMachines' content: the sockets are on the Utinni's hull and the precept is the
clan's faith, so both sit in the dependent campaign mod.

⚠️ Salvation Engine therefore needs an **assembly** — a comp plus save/load persistence
plus settings. `src/RimUtinni/ShipMemory/Source/GameComponent_ShipMemory.cs` is the
in-repo precedent to copy for the persistence.

🔴 **WreckedMachines gets an assembly too — the pure-XML protection is REVERSED**
(owner, 2026-09-15, later the same sitting). *"Every mod ships superb Mod Settings, no
exceptions"* wins, and ruling 1 makes it mandatory anyway: the three ratios and the
full-restoration cap are all player-tunable, which needs a settings screen. Its false
exemption in `MOD_OPTIONS_RETROFIT_1` has been deleted.

**6. 🔴 The urns feed Antiquities; the relics do not.** Owner, verbatim: *"The Urns
feed antiquities, not the artifacts."* Antiquities' 48 read artifacts
(`RUT_Antiquity_Urn`/`_Stele`/`_Gravegood`) remain its own economy, untouched. Rakatan
relics move the gods instead — see 7.

**7. Installing a relic moves BOTH per-god scalars** (ruled 2026-09-15). Owner,
verbatim: *"The ship has its literall 'mood' (vector among the gods) increased when
ancient relic artifacts are installed on the ship."* Resolved as **both**: the permanent
**Satiation** ledger records the act, and **Mood** lifts temporarily because a relic is
a gift rather than a duty. The Mood half stays unprinted forever, per canon F8.

🔴 **This needs new code one layer down: Ninefold has no public Mood mutator** — Mood is
a private random walk with no external entry point. Owner authorized building **a
generic external-impulse API** in Ninefold so any mod can nudge a god's Mood, with
relics as its first caller. Open design question inside that: how an external nudge
coexists with a walk that is meant to be the god's own.

**8. Ship raises the FLOOR; components buy the PEAK.** Her recovery guarantees a
climbing minimum grade across all seated relics; Ancient Components push an individual
relic above that floor. Owner, verbatim on the timing: *"players will be manually
upgrading systems for quite some time long before the ship gets the ability to 'bring
everything up to some base level' across the board. It raises the floor to save the
players from manually repairing everything all the time."* ⇒ The floor is **late** and
its purpose is **relief from chore-work**, not a mid-game tide.

**9. "Study the machine" does NOT route through Anomaly.** Anomaly is owned but
owner-benched (*"not fun to user"*), and `CompStudiable` gates on monolith level, which
this campaign's `generateMonolith false` never raises. Research Reinvented's
`SpecialResearchOpportunityDef` with `opportunityType Analyse` is already proven on
disk for exactly this machine (`WreckedMachines/DESIGN.md` §2) and is the route.

## Still open

- 🔴 **Which def gets which name** — see ruling 1. `_Repaired` is the 1.0 rung, so the
  0.75 Refurbished tier must be authored, and the naming is undecided.
- **Per-class Wrecked values.** 0.001 is the battery number. Factories and other
  functional devices each need their own, and nobody has set them.
- **Rekko's endgame vision is now settings-dependent.** His canon body-vision is *"full
  restoration of the original"*, which at a 0.75 cap is undeliverable — but the 1.0 mod
  option makes it deliverable. So whether the god of repair can ever be satisfied depends
  on a player's settings toggle. Interesting rather than broken, but it wants a ruling.
- **Layer-3 naming.** The spec calls it "the Salvation pack" / `mandrake.rut.salvation`;
  this item calls it "Salvation Engine". The packageId does not exist yet, so nothing is
  broken — but one of the two should win before it is minted.
- **Grade steps are invisible to the god engine, and may be inverted.** Ninefold's
  repair hook fires on full hit points, not on a grade step, so refurbishing currently
  earns Rekko nothing; and `Patch_BuildingDeconstructed` fires a large negative Rekko on
  a completed deconstruct, so if a `replaceTags` build-over routes through that path,
  refurbishing *angers* the god of repair. The hook exists (verified); the routing is
  UNVERIFIED and needs the game. Fix per ruling 0: layer 1 publishes a neutral
  "grade changed" signal, layer 3 listens. `ChronicleSubscriber` is the precedent.
- Where relics are found, and where Ancient Components come from.
- Mobile structures: which ones, and does a mobile relic still seat in a hull socket?
- Can the ship's floor ever reach `Refurbished`, or does it stop at `Kludged` — with
  only three grades, the floor has very little room to move.
- Does the reliquary need to be readable by the endgame's contest over the ship's
  future, or does Salvation Engine keep that to itself?
