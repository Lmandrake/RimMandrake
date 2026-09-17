# FLOWWORKS_DOOR_FAMILY_1

Two stuffable doors for FlowWorks: a **Sluice** and a **SecurityGrateDoor**. Both
pass liquid without being opened; the grate also holds a real prisoner. Commissioned
by the owner 2026-09-17, in the middle of ruling on the pit collapse
(`PIT_SUPERDEEP_COLLAPSE_1`), which is why it is a separate item — it is new content,
not part of that collapse.

## the commission  (OWNER'S WORDS — verbatim, 2026-09-17)

Asked how a trapped mechanoid should resolve, he chose "killable from the lip" and
then said:

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

## 🔑 Build the SIMPLER shape — he talked himself out of the other one

He described a three-def ladder (cheap sluice / armoured metal sluice / steel grating)
and then, in the same breath, said he would be happy with **two stuffable defs**
instead. Take the second.

- ⛔ **Do not build three fixed defs.** The armour / fire-survival / prisoner-strength
  ladder he listed is exactly what `stuffCategories` already expresses, so hardcoding
  it would duplicate a vanilla mechanism.
- ✅ **`Sluice`** — cheap, passes liquid, holds **small creatures**.
- ✅ **`SecurityGrateDoor`** — passes liquid, holds a **real prisoner**.
- **Stuff decides** armour, whether it survives burning, and how tough a prisoner it
  holds. *"the player can just learn what happens if you're made of wood"* — so a
  wooden sluice burning down is a lesson, not a bug, and must not be prevented.

## what must survive stuffing

The functional split is the design; the stuff is the tuning. Whatever material is
chosen:

- Both **pass liquid while closed**. That is the whole point — *"so that fluid can
  easily enter without needing to open it"* — and it is what makes them different from
  a vanilla door on a canal mouth.
- Both are **doors in the §4 sense** of `pit_superdeep_collapse_spec.md`: not openable
  from inside a superdeep cell, openable from outside or above. That was already the
  owner's ruling on sluice gates in `PIT_SUPERDEEP_COLLAPSE_1`.
- **Sluice holds small creatures only.** A tough prisoner should get out of a sluice;
  that is the reason the grate exists.
- **`SecurityGrateDoor` holds a real prisoner** — it is the "prisoner door" for the end
  of a canal, and the piece that makes a canal-fed pit a usable prison.

## why it matters beyond doors

🔑 It reframes a problem the pit spec had recorded as unresolvable. A trapped hostile
mechanoid is not a permanent unreachable hostile — it is a **stored asset**: hold it,
then release it through a sluice when you want it loose. `pit_superdeep_collapse_spec.md`
§9 question C called a pit of centipedes "a permanent unreachable hostile with no
resolution"; this commission plus his lip-killing ruling closes that.

## open questions

- **What counts as a "small creature"** for the sluice — a body-size threshold, and it
  should be reconciled with the per-depth body-size field ruled the same day in
  `PIT_SUPERDEEP_COLLAPSE_1` ([J]) so the two do not disagree about what "small" means.
- **Does a grate door block fire spread** the way its stuff implies, given oil is a
  fluid that can be ignited and a grate deliberately passes fluid?
- Art. Nothing is specified, and rulings 19/20/33 already govern how excavation and
  its built half must look (`the terraces, ladders, sluice gates` — ruling 20 names
  sluice gates as part of the built half the FlowWorks name celebrates).

## spec

Not written. Design work; goes to a backgrounded high-tier subagent per
`infrastructure/agents/Agent_Policy.md`, with this file as its input.

## verify

- Two defs only, both stuffable; no fixed armour/fire tiers hardcoded.
- Liquid passes both while closed — proven in game, not by reading the def.
- Neither is openable by a pawn standing in a superdeep cell.
- A wooden one burns.
