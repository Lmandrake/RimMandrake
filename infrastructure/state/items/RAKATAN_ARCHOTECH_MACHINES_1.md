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

Owner, verbatim: *"Defunct, weakly functional, or semi-functional versions will be
found in the game and added to the ship by the player as a form of sacred loot. The
ship LOVES these, and as it slowly gains the ability to auto-heal itself, so too will
they become better over time."*

Two coupled ideas to design against:

- **A found artefact has a functional grade** — defunct / weakly functional /
  semi-functional — and installing it on the ship is an act with religious weight,
  not just a stat gain.
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

**1. The condition model is NAMED GRADES.** Discrete states, each its own stat block
and its own sprite, not a capacity curve and not a per-subsystem organ model. This
ratifies what the mod already does: `RM_WM_AutomatedSmelter_Wrecked` → `_Kludged` →
`_Repaired`, stepped by vanilla 1.6 `replaceTags` (build the next tier's blueprint
over the old footprint — an ordinary construction job, no C#).

**2. 🔴 Nothing equals or exceeds the original.** Owner, verbatim: *"There is nothing
beyond or even equal to the original. The final word should be something like nearly
restored in a single word."* The ladder is **asymptotic** — a Jawa hand approaches the
ancients' work and never arrives.

⛔ This kills the "ascendant" grade that surpasses Rakatan design. It does **not**
touch the earlier promise that a refurbished machine exceeds *modern* technology:
beating rim-tech gear and equalling Rakatan work are different bars, and only the
second is impossible.

**3. The top grade is `Rewoken`.** Chosen from options because canon already names
Rekko's domain *"the discarded rewoken"* — so the ladder's top is spoken in the god of
repair's own vocabulary, and the word claims a thing is no longer dead without
claiming it is whole.

**4. 🔴 Reaching for the top grade is PRIDE.** Owner, verbatim: *"Reaching towards it
would definitely please Ozzik and anger others."* Note the inversion from the design's
first framing: the offence is not surpassing the ancients, it is **presuming you could
make their work whole again.** Which gods anger, and whether Rekko is among them
(his own body-vision is full restoration, which this rules impossible), is UNRULED.

**5. Sacredness is SOCKETS + PRECEPT, layered.** Relics are seated in hull reliquary
sockets — persistent, not consumed, each granting a boon — alongside an ideoligion
precept venerating them (mood near relics, a ritual to seat one, real fallout for
scrapping or selling). ⚠️ This makes the mod an **assembly** mod: it has zero C#
today, so a comp plus save/load persistence plus Mod Settings is new scope.
`src/RimUtinni/ShipMemory/Source/GameComponent_ShipMemory.cs` is the in-repo
precedent to copy for the persistence.

**6. 🔴 The urns feed Antiquities; the relics do not.** Owner, verbatim: *"The Urns
feed antiquities, not the artifacts."* Antiquities' 48 read artifacts
(`RUT_Antiquity_Urn`/`_Stele`/`_Gravegood`) remain its own economy, untouched. Rakatan
relics move the gods instead — see 7.

**7. Installing a relic moves the ship's standing with the gods.** Owner, verbatim:
*"The ship has its literall 'mood' (vector among the gods) increased when ancient
relic artifacts are installed on the ship."* ⚠️ UNRULED which scalar the divine engine
means: **Satiation** (the signed per-god ledger moved by what the colony DOES) or
**Mood** (each god's own weather, which canon F8 says is never printed as a number).
Ask before building.

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

- Which gods anger when a hand reaches for `Rewoken` — and is Rekko one of them?
- Satiation or Mood (ruling 7). The engine reserves them for different things.
- The full grade ladder's names, and reconciling them with the shipped
  `_Wrecked`/`_Kludged`/`_Repaired` defNames.
- Where relics are found, and where Ancient Components come from.
- Mobile structures: which ones, and does a mobile relic still seat in a socket?
- Does the reliquary need to be readable by the endgame's contest over the ship's
  future, or does this mod stay ignorant of it?
