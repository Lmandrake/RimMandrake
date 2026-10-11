# POLE_OWNER_CHANGE_DROPS_WIRES_1 — GS-5: pole ownership change drops wires to other owner poles

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row GS-5 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| GS-5 | Robustness: when a pole changes owner (claimed or captured), drop its wires to the other owner's poles. Otherwise claiming one enemy pole fuses your grid with theirs both ways, which the rules forbid for new links and which also bypasses the one-way tap. | Faction-change hook (a `SetFaction` postfix or a rare-tick check). On a mismatch, cut with a coil, plus a selftest. | S | low | GimmeSomeSlack | `LivePartners` (Aerial/CompAerialAnchor.cs:113-121) checks Up, Spawned and Map but not faction. New-link refusal is player-only (:330, :403). There is no SetFaction handling in Source (grep). |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

- Offline: build clean; RM_MapComponent_Aerial.OwnerMismatchSweep (every 250 ticks, toggle cutWiresOnOwnerChange) coils wires between differently-owned poles. No selftest added (needs game types).
- L2 (owed): claim one enemy pole; its wires to enemy poles are coiled within ~4 s.
