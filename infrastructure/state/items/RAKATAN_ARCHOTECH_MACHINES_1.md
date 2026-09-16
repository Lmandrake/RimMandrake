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

**1. 🔴 The ladder is NAMED GRADES, and there are exactly THREE.** Owner's orders,
verbatim: *"Defunct, Kludged, Refurbished. Only three levels (0.0001, 0.2, 0.5 of the
original capability) One ladder for everything, with large artifacts (e.g. factories)
worth much more than smaller items (e.g. batteries)."*

⚠️ **The ratios were revised the same evening — these are the live numbers**, owner
verbatim: *"I take back the numerical values. They should now be 0.001, 0.2, and 0.75.
The original item (unmodified) is of course 1.0. Wrecked machines can never restore
fully to the original device (mod option, defaults to no)."*

| grade | capability vs. original | reads as |
|---|---|---|
| **Defunct** | 0.001 | inert. A sacred object, not a machine. |
| **Kludged** | 0.2 | works, badly, visibly bodged. |
| **Refurbished** | 0.75 | the default ceiling. Three-quarters. |
| *the original, unmodified* | 1.0 | **unreachable by default** — a real reference point, not a grade |

**1.0 is a genuine rung that the player normally cannot stand on.** A **Mod Setting,
defaulting to OFF**, allows full restoration to 1.0; with it off, 0.75 is the hard cap.
So the asymptote of ruling 2 is enforced by a default rather than by arithmetic, and a
player may switch it off — deliberately his choice.

Discrete states, each its own stat block and its own sprite — not a capacity curve and
not a per-subsystem wear model. **One ladder for every Rakatan thing**, fixed
installation or carried relic. **Worth scales with size**: a factory is worth far more
than a battery at the same grade.

⛔ Deletes every earlier ladder proposal: no "weakly functional", no "semi-functional",
no grade that surpasses the original, and **no `Rewoken`** — that top-grade name was
ruled and reversed inside the same sitting, and the three-level ladder replaces it.

Shipped defNames follow the ladder: `_Wrecked` → `_Defunct`, `_Repaired` →
`_Refurbished`; `_Kludged` already matches. Stepping stays vanilla 1.6 `replaceTags`
(build the next tier's blueprint over the old footprint — ordinary construction, no C#).

**2. 🔴 Nothing equals or exceeds the original.** Owner, verbatim: *"There is nothing
beyond or even equal to the original."* The ladder is **asymptotic and capped at half**
— a Jawa hand approaches the ancients' work and never arrives.

⛔ This kills any grade that surpasses Rakatan design. It does **not** touch the
promise that a refurbished machine exceeds *modern* technology: beating rim-tech gear
and equalling Rakatan work are different bars, and only the second is impossible.

**3. The power curve falls out of 1 and 2 — and needs one confirmation.** If
`Refurbished` is 0.5 of original **and** still beats modern technology, then original
Rakatan capability is at least **2× modern rim-tech**, and realistically well beyond.
⚠️ DERIVED, NOT RULED — it is a canon-shaped number nobody has said out loud, so it
wants his yes before anything is balanced against it.

This is also the answer to the old "does refurbished-exceeds-modern break the power
curve" question: the ceiling is no longer scarcity alone, it is **arithmetic**. Half of
original is the most any player ever gets.

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
in-repo precedent to copy for the persistence. WreckedMachines itself may still be able
to ship as pure XML, which is worth protecting.

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

- **Confirm the 2× arithmetic** in ruling 3 — derived, never spoken.
- Where relics are found, and where Ancient Components come from.
- Mobile structures: which ones, and does a mobile relic still seat in a hull socket?
- Can the ship's floor ever reach `Refurbished`, or does it stop at `Kludged` — with
  only three grades, the floor has very little room to move.
- Does the reliquary need to be readable by the endgame's contest over the ship's
  future, or does Salvation Engine keep that to itself?
