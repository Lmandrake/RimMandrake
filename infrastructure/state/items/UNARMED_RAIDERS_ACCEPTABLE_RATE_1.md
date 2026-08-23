## spec
A scope call for DECIDE, raised by a live measurement rather than a theory.

**RimWorld will not arm a pawn whose backstory disables `Violent`**, and `PawnKindDef`
generation rolls such backstories for combat kinds. Measured on 240 spawns across the 48
authored role kinds:

| | bare (27) | armed (213) |
|---|---|---|
| backstory disables `Violent` | **19** | **0** |

A clean separator, no false positives. ⇒ **19 of the 27 bare-handed raiders are the engine
working correctly**, not a defect in our defs. 8 remain unexplained and are the likely
casualties of `RESTORE_VANILLA_GUN_TAGS_1`.

## the question
`ROLE_KINDS_ARMED_5_OF_5_1` sets the bar at **5/5 armed for all 48 kinds**. That bar cannot
be met while the engine refuses to arm pacifists — it is unreachable by any def edit short
of pinning backstories per kind.

**So: what rate of unarmed raiders is acceptable?** Ours is **11.2%**, of which roughly
8% is engine-correct. Vanilla's own kinds in the same mod list run at **32.5%**.

Three shapes the ruling could take:
1. **Accept it.** A raid with one pacifist in it is vanilla texture. Restate the criteria as
   "no kind is 0/5" rather than "every kind is 5/5", and the roster passes today.
2. **Suppress it per kind** — constrain backstory categories on the 48 authored kinds so
   combat roles cannot roll a pacifist. Costs authoring and narrows pawn variety.
3. **Leave the bar and never meet it.** Not recommended; it keeps two items open forever
   against a cause nobody can remove.

## criteria
A ruling recorded saying which shape, and `ROLE_KINDS_ARMED_5_OF_5_1`'s successor criteria
rewritten to match it.

## note
⚠️ The 8 unexplained rolls were tested against violence-disabling **traits** and the check
came back **UNMEASURED** — the dump reports 0 `TraitDef`s with `Violent` in `degreeDatas`,
which is a dump blind spot, not a proven zero. Settle that before assuming all 8 belong to
the gun-tag defect.
Evidence: `observed/2026-08-21/armed_sweep_48/`.
