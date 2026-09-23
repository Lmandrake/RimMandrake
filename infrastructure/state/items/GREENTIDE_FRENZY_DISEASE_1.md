# GREENTIDE_FRENZY_DISEASE_1 — The Frenzy, a disease you infect yourself with on purpose

## the ruling

**Owner, 2026-09-22.** Offered three options for the biome's generic disease load, he chose *replace
two with one of ours* and specified the disease in the same breath:

> *"'The Frenzy' causes colonist to work feverishly and faster until they totally collapse from
> exhaustion in a multi-day coma. Can purposely infect someone with this disease. It will kill you if
> not treated, but you can treat it in the coma stage after benefiting from the rapid work."*

⇒ **Two rulings in one:** the biome's disease count drops (two generic illnesses come out, this goes
in), and this is the first disease this project has ever authored.

### ✅ The delivery route is RULED — owner, 2026-09-22

Offered three routes — travel to a living plant, a harvestable dose, or a medical bill — he chose
**a harvestable dose the player administers**: harvested from a jungle plant, carried, used on
whoever the player picks.

⇒ **It is an item.** It stockpiles, it travels, it works at home, and the timing is entirely the
player's. ⛔ The un-stockpilable plant-interaction route is **declined, not deferred** — do not
reintroduce it later as the "safer" variant.

🔴 **This moves the entire balance burden onto the coma.** With doses on a shelf, nothing in the
delivery route stops a player cycling twenty colonists through the speed boost, so the brake is
now the coma's length and the death risk alone. Those stop being flavour and become load-bearing —
design them as the bound (spec §4, and the anti-exponential warning at the bottom).

## why it is the best thing in the risk/reward pass

🔑 **It is his own "reward and hazard are the same object" principle at its purest** — the hazard IS
the reward, in one hediff, with no paired item and no second system. And it is *player-triggered*, so
the jungle stops being something that happens to you and becomes something you use.

The shape:

1. **Onset** — work speed rises. The colonist is better than they have ever been.
2. **Escalation** — it keeps rising. This is the tempting part and the trap.
3. **Collapse** — total exhaustion, a coma lasting multiple days.
4. **The fork** — untreated, it kills. Treated *during the coma*, the colonist lives, and the work
   already done is kept.
5. **Deliberate infection** — a player may inflict it on a colonist on purpose.

⇒ **The decision it creates is the content**: how long do you ride the speed before you stop being
able to choose? And who do you spend it on?

## ✅ Two measured facts this lands on

1. **The biome carries SEVEN diseases and every one is vanilla** — MEASURED 2026-09-22 on
   `RM_Greentide`: `Disease_Flu`, `Disease_Plague`, `Disease_Malaria`, `Disease_GutWorms`,
   `Disease_AnimalFlu`, `Disease_AnimalPlague`, plus organ decay ruled in this session. ⇒ Two of
   those come out. ⛔ **Do not stack this on top of seven** — the ruling was *replace*, and a biome
   that is tedious is not frightening. Say which two you removed and why.
2. **This project has never authored a disease** (established by the risk/reward audit). ⇒ Expect a
   capability-building pass, not a copy-paste. Budget accordingly.

## ⚠️ What is UNMEASURED and must not be guessed

🔴 All of the following are engine questions, and the Mac laptop has no game, no def dump and no
decompiler. ⛔ Do not name a field, class or value for any of them from reasoning.

1. **How a staged illness escalates and what drives stage transitions** — this needs a real multi-stage
   hediff with a severity curve.
2. **How to raise work speed from a hediff** — a stat offset on a hediff stage is the obvious shape,
   but the exact stat and whether a *global* work-speed multiplier exists must be read, not assumed.
3. **How to produce a multi-day coma** a pawn reliably wakes from — and whether an existing
   incapacitating mechanism can be reused rather than invented.
4. **How treatment gates on stage** — his ruling requires treatment to be possible *in the coma stage
   specifically*, which is a tighter requirement than ordinary tending.
5. **How a harvestable dose applies a hediff to a chosen colonist** — the route is ruled (an item),
   so what is left is the mechanism: which existing consumable/administer pattern carries it, and
   whether applying it needs a colonist's consent or a doctor.
6. **Whether "work already done is kept" needs anything at all** — probably not, since work completed
   is simply completed. Confirm rather than build for it.

## spec

1. **Name the source plant** in the 21-row roster (`GREENTIDE_JUNGLE_TREE_ROSTER_1`) the dose is
   harvested from, and the harvest/craft route to it. The route being an item is ruled; which plant
   pays for it is not.
2. Establish the mechanism questions on the Desktop. ⛔ Author nothing before that.
3. Choose and record which two vanilla diseases are removed.
4. Design the severity curve so the *decision* is real: too short and there is no temptation, too long
   and it is free value. This is the balance heart of the feature.
5. Mod Settings toggle and tuning per the standing every-mod-ships-settings rule — the curve is exactly
   the "a number is the experience" case.

## verify

`RM_Greentide` carries six diseases, two of the original seven removed and recorded, with The Frenzy
among them. The illness escalates, collapses, and is survivable only if treated during the coma.
A player can inflict it deliberately. ⛔ No live-proven claim from the Mac.

## criteria

A player looks at a colonist, looks at the deadline, and does something they know is a bad idea.

## Watch out

- ⚠️ **If riding the speed is strictly better than not, it is not a decision — it is a chore.** The
  temptation must be able to cost you the colonist. Guard against a player learning one safe timing
  and never thinking again.
- ⚠️ **Deliberate infection of your own colonists has a mood dimension** in this game. Whether the
  colony should react to it is unruled — flag it, do not decide it.
- ⛔ **Do not let this become a work-speed exploit.** The anti-exponential concern that flattened a
  creature's market value applies: a repeatable speed boost with a survivable downside is a production
  multiplier, which is exactly the ladder that law forbids. The coma's length is the brake — say so
  explicitly in the tuning.
