## spec
Explosive Knockback, Design Version 0.2.0 (next version; not 0.1.0). A thrown pawn that lands on a pawn standing on its
landing cell (one that walked there mid-flight) gives both a small bruise, scaled by the thrown pawn's weight.

Owner, by card 2026-11-14 about 2:40 PM PST, answering journal question 8 (`design/concepts/ExplosiveKnockback/journal.md`):
"Bruise in the next version".

0.1.0 as built and kept: the thrown pawn lands on its planned cell, the journal writes `land_on_pawn` naming the other pawn,
and neither takes damage (Stage 3, 2026-11-14; scene sc_pawn_arc asks only for the impact line).

## Acceptance test (draft)
1. Offline (kernel selftest, new K case): a landing-bruise function of the thrown pawn's mass returns a small Blunt amount
   that rises with mass (a 40 kg pawn less than a 70 kg pawn less than a 140 kg pawn), stays under a stated cap (the
   designer states it; "small" means it never downs a healthy colonist), and is 0 when there is no pawn on the cell. Seen
   red today (no such function).
2. In game (a revised sc_pawn_arc lane, proof build, minimal list): a second pawn walks onto the planned landing cell
   mid-flight. On landing both pawns take one Blunt hit of the kernel's amount for the thrown pawn's mass; the
   `land_on_pawn` journal line carries that amount; neither is downed; run twice with a light and a heavy thrown pawn,
   the heavy one bruises more. Control: a landing on an empty cell gives no hit to anyone.

Listed in `design/concepts/ExplosiveKnockback/version/next_version/README.md`.
