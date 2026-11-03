# Relentless improvement loop — owner, 2026-11-03

Primary job now: get Relentless to skilful high productivity, offline and online. Owner,
2026-11-03: *"Keep studying what jams relentless and fixing it, then improving our skills, Relentless
definition files, policies, etc. ... every time we do, we should modify Operations such that it gets
better. Dispatch is part of Operations."*

## The loop

1. **Relentless works.** Its jams and its escapes are the raw material.
2. **Every jam is fixed as a CLASS** — owner: *"absolutely, fix the class should be the rule."* A jam
   gets a class name, an Operations detector and, where safe, an automatic remedy. Target: no class
   jams twice. A Conductor fix that does not land as an Operations change is not done.
3. **Escapes teach the acceptance tests.** An escape = an item that passed, then broke live, was
   reopened, or the owner caught it. Each gets a plain-language tag (below). Designer reads the tags.
4. **Designer names the broken version** each acceptance test would catch (below). A test that
   catches no nameable broken version is decoration.
5. **A small independent regrade** samples closed items — with a noise guard (below).

## Metrics are evidence, not targets

Owner: *"track whatever metrics you'd like. We're not chasing metrics, we're just keeping a record of
them as evidence."* Recorded: items that stay done (closed, not reopened or found broken in 7 days),
offline vs online; tokens and wall-hours per item that stays done; jams by class; escapes by tag.

## Tags must be plain — owner's bar

Owner: *"Please ensure that the lesson/signal we name isn't so obtuse that I can't understand it."*
A tag reads cold to a human with no context, in one short sentence. Good: *"Only proven on the
minimal mod list."* Bad: *"The test never named a live state."* (He: *"what? could you give an
example?"*) — say instead *"The test checked the file, not the running game."*
Example: the hose patch XML loaded cleanly, but in the game the hose never carried water.

## Naming the broken version — example

Test: *"a hose 10 cells long delivers water at the far end within 1 in-game hour."*
Broken version it catches: *"water stops after the first cell."*
A test like *"the hose def loads without errors"* catches no broken version of the hose's job —
so it is not an acceptance test of it.

## Regrade noise guard

Owner: *"there's a lot of noise in these regradings, and I'd hate this to turn into a rabbit hole
chasing noise."* So: a handful of items a day, at most. A regrade disagreement is RECORDED, never
chased alone. Act only when two independent graders agree an item is wrong, or the same kind of
disagreement repeats across items. If after two weeks it has found nothing that held up, stop it.
