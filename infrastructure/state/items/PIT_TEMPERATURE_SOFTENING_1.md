# PIT_TEMPERATURE_SOFTENING_1 — Pit temperature couples hard to ambient and wears down resistance; Exposed Prisoner thought

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- An unroofed superdeep room tracks outdoor temperature faster than a roofed room (multiplier at the seam measured in `SUPERDEEP_SEAM_MEASURE_1` item 5).
- Vanilla Heatstroke/Hypothermia do the harm; `RM_PitExposure` accumulates while exposed and lowers resistance (recruitment first) — two independent dials ([H]).
- **Exposed Prisoner** thought: compassionate pawns feel it; psychopaths and hard-morality cultures do not — copy the beggar-rejection structure, no new moral axis ([A-item]). Numbers and the exact def shape go to the owner with a proposal; never invent them as his.
- Mod Settings: on/off, coupling multiplier, resistance-loss rate.

## verify
Bridge: desert noon, unroofed pit vs roofed twin — the pit's temperature moves faster; an occupant's resistance falls faster in the pit than in a normal prison cell; a compassionate colonist gets the thought, a psychopath does not.

## criteria
"Letting them roast" measurably shortens capture/recruitment, and reads as cruel.

## depends
`SUPERDEEP_PRISON_ROOM_1`.

## northstar
State components: room temperature delta vs twin over N ticks; `RM_PitExposure` severity; resistance delta; thought presence by trait.
