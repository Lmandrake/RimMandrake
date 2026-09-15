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

## Open for the session

- Does the graceful-degradation curve get a real mechanic (capacity decay, quality
  tiers, a hediff-like wear model), or is it flavour plus stat spread?
- What makes an artefact "sacred" mechanically — ideoligion precept, ritual, or a
  ship-specific slot?
- How does "study the machine" interact with `TECHPRINT_FACTION_GATING_1`'s research
  access classes?
- Does refurbished-exceeds-modern break the campaign's power curve, and where is the
  ceiling?
