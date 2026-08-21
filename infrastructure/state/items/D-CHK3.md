## spec
Filed by CHECK 2026-08-15 from the live log, 7,726 lines, process 07:56:41.

`Config error in RimMandrake<Species>_Kind: initial resistance range is
undefined for humanlike pawn kind.` — **69 of them, one per species.** They
are 69 of the log's 93 config errors, i.e. three quarters of all config noise
on this stack is ours.

`initialResistanceRange` is what a prisoner's recruitment resistance is rolled
from. Undefined on a humanlike kind means every captured pawn of these species
starts from an unset value — so this is not only log noise, it is the prisoner
and recruitment path for all 70 species.

Vanilla humanlike kinds set it (e.g. `<initialResistanceRange>10~20</...>`).
The generator emits the kinds without it. One line per kind in
`gen_races_mod.py`'s PawnKindDef writer fixes all 69.

## verify
after a regenerate + redeploy + load: `grep -c "initial resistance range is
undefined" Player.log` returns 0.

## criteria
BUILD's fix in the generator, not a hand-edit of 69 defs.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
reach the frozen world. Parked, not lost.
