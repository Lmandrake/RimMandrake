# CONTAGION_GENOME_ORGAN_GROWING_1 — grow a colonist's organs inside a Contagion amoeba

## the ruling

**Owner, 2026-09-22.** A design pass had proposed limb-regrowth as a *jungle* reward — a living chamber
in the Greentide that regrows a lost limb. Offered it as a candidate to build first, he **moved it to a
different biome and made it stranger**:

> *"(2) is a really interesting idea that could be adapted for the Contagion: the ability to inject the
> genome of a colonist into one of the amoeba-like entities within the contagion to produce a plethora
> of organs and limbs from that individual. Add that to a relevant contagion creature."*

⇒ **The Greentide keeps no limb-regrowth content** — its replacement reward is
`GREENTIDE_GRENADE_WEAPONS_1`. ⛔ Do not build a regrowth chamber in the jungle; that idea has moved.

🔑 **And it changed shape in the move, which is the interesting part.** The jungle version was
*medicine* — a patient healed in a chamber, deliberately unstockpilable because the patient was the
vessel. The Contagion version is *manufacture*: you inject a genome into a living creature and it
produces **a plethora of organs and limbs** matched to that individual. ⇒ The output is **items**, and
plural. That is a different economic object entirely and must be balanced as one.

## what this attaches to

**A relevant Contagion creature** — his words. The Contagion is the biome whose cast includes
amoeba-like entities. ⚠️ **Which creature is UNMEASURED and is the first thing to establish**: read the
Contagion's own roster and design doc and propose the host, rather than inventing a new creature. He
said *"add that to a relevant contagion creature"*, which is an instruction to use the existing cast.

⛔ **Do not place this creature in the Greentide or any other biome to make the mechanic reachable.**
The standing fauna law is one home per creature absent an in-game mechanism reason, and roster
placement is settled at a biome's own review sitting — never by a sweep. This mechanic is a reason to
go to the Contagion, and that is the point of it.

## ⚠️ UNMEASURED — the whole feasibility question, and it is the largest on the list

🔴 No game, no def dump, no decompiler on the Mac. ⛔ Name no field, class or value from reasoning.

1. **Whether a mod can produce body parts matched to a specific pawn at all** — the design pass flagged
   this as possibly not buildable. ⚠️ **A lead worth reading rather than a blocker:** the base game
   appears to regrow lost body parts via one of its late-game drugs, so there is an existing mechanism
   to read before concluding anything. ⛔ Do not report that as confirmation — read it.
2. **Whether "matched to that individual" is expressible.** Vanilla body parts are generic items. Does
   a part need to carry a source-pawn identity for this to mean anything, and does the engine support
   that? ⚠️ If not, the fiction survives but the mechanic becomes "organs, generically" — say so rather
   than quietly shipping the weaker version.
3. **How a genome is taken from a colonist** — an existing sampling operation, or something new.
4. **How the creature is made a vessel**: a building-like interaction on a live animal, a bill, or a
   containment mechanism. This is a design choice as much as a mechanism.
5. **Whether the creature survives the process**, and whether it is repeatable on the same host. This
   determines whether the mechanic is a renewable industry or a consumable find — the single most
   important balance question here.

## spec

1. **Read the Contagion's roster and design doc first** and propose the host creature. ⛔ No new
   creature unless the existing cast genuinely has no fit, and say so if it does not.
2. Establish feasibility (question 1) on the Desktop before anything else. If it cannot be done, say so
   plainly and bring him the fallback rather than building a lesser version silently.
3. **Card him on whether it is renewable or consumable** (question 5) — that is his call, not a
   balance detail, and everything else follows from it.
4. Mod Settings toggle per the standing rule.

## verify

The host is an existing Contagion creature, named and justified from that biome's own roster. Organs
produced are matched to the source colonist, or it is recorded that matching is not expressible and he
has ruled on the weaker version. The host's fate after use is decided and recorded.
⛔ No live-proven claim from the Mac.

## criteria

You go to the worst place on the planet to get a piece of someone back.

## Watch out

- 🔴 **"A plethora of organs" is an economy, not a heal.** Vanilla organs are valuable trade goods, so a
  repeatable source of them is a money printer — the exact class of problem that got a creature's
  market value deliberately flattened in this project. ⇒ Bound it before building it: a consumable
  host, a long timer, a cost in something scarce, or output that cannot be sold.
- ⚠️ **This is body horror, and the project deliberately limits that content.** The Contagion may
  already have a ruling on how far it goes; check before designing the visuals.
- ⚠️ **It overlaps whatever medical content already exists.** Check for existing organ, prosthetic or
  healing mechanics of ours before inventing a parallel one.
- ⛔ **Do not reopen the jungle regrowth chamber.** It was moved, not duplicated.
