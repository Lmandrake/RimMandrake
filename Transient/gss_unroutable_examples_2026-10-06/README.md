# A7: where do unroutable cords come from? (2026-10-06)

You asked to see the geometry before believing the dive-in/dive-out model can't handle it. Here it is.

## What was measured

| source | worlds | unroutable legs |
|---|---|---|
| Offline fuzz worlds (`GssFuzz` cords, 3000 seeds) | 43,270 | **0** |
| Every live GSS record in `src/RimMandrake/GimmeSomeSlack/northstar/` (M2b and the proofs) | 60 records | **0** |
| Random bases using vanilla's hookup rule (2000 maps, 5,670 device leads) | 2,000 | **221** |
| Constructed scenes (the 8 PNGs named `constructed_*`) | 8 | 5 |

The fuzz never produces one because its devices always hook to the conduit cell right beside them. Real games don't work
that way. Vanilla's `PowerConnectionMaker.BestTransmitterForConnector` (checked in the decompiled 1.6 source) hooks a device
to the **nearest conduit within 6 cells, and it never checks for walls or line of sight**.

## The classes (random vanilla-rule bases, 221 legs)

| class | count | what it is | picture |
|---|---|---|---|
| a: the wall the lead crosses has conduit through it at that spot | **0** | Never unroutable. A conduit through a wall already draws as cord, then a plate on the wall face, then a hidden run, then a plate and cord on the far side. That is your dive-in/dive-out, and it has shipped since round 4. | `constructed_1_…`, `constructed_8_…` |
| b: water | 11 | A device on an island or across a pond, hooked to conduit on the far shore. | `constructed_3_…`, `vanilla_b_…` |
| c-wall-conduit-elsewhere | 121 | The device's lead crosses a wall with no conduit in it. Conduit does pass through that wall mass somewhere else, but vanilla hooked the device to a nearer conduit cell. | `vanilla_c_wall_conduit_elsewhere_…` |
| c-wall | 89 | The device sits in a room whose walls have **no conduit in them anywhere**. It is powered through the wall by the 6-cell rule. | `constructed_2_…`, `constructed_6_…` (two walls), `vanilla_c_wall_…` |
| c-building | 0 random, 1 constructed | The device is boxed in by other buildings (shelves, tables). | `constructed_7_…` |

The B9 change (below) adds one more source: a device wired straight to a battery through a wall (`constructed_5_…`, c-wall).

## Verdict: push back on the premise, keep the model

*"If it's a wall, then some conduit must go through the wall"* is not true in RimWorld. In 89 of the 221 legs (40%) there
is no conduit anywhere in the wall. Vanilla simply reaches through it. So "dive in at the conduit" has no place to dive in
those cases. In the 121 conduit-elsewhere cases the dive point would be off the lead's line, sometimes several cells away.

The model does cover every case once the dive point is **wherever the lead meets the barrier** (as if a hole were drilled
there), not only where conduit is. Under that rule:
- water dives under and comes back up (b),
- a wall gets an entry plate on each face, like the existing buried-run plates (c-wall),
- the boxed-in case goes under the neighbouring building's footprint, which hides it anyway (c-building),
- two walls with a closed room between (`constructed_6`) dive twice and surface briefly in the middle room.

No geometry defeats that. You ruled it built (2026-10-06): **dive-through is built** (setting "Cords dive under walls and
water", default on). With it on, the same 2,000 bases hold **0** unroutable legs (MEASURED, 208 dives laid). A wall or rock
crossing gets a plate on each face; water and buildings get no plate (no water art exists; buildings hide the cord).
The PNGs above show the cords as drawn with it OFF.

## Regenerate

    python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --unroutable-census Transient/gss_unroutable_examples_2026-10-06/census.json 200
    python3 src/RimMandrake/GimmeSomeSlack/render_unroutable_examples.py Transient/gss_unroutable_examples_2026-10-06/census.json Transient/gss_unroutable_examples_2026-10-06

How to read the PNGs: brown is wall, grey is rock, blue is water, a tan box is a building footprint (powered ones are labelled),
orange is conduit (darker where it is buried), the black curve is the cord as drawn today, the dashed red line is the
unroutable leg, and red hatching marks the blocked cells it crosses.
