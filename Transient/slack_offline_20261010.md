# GimmeSomeSlack offline pass 2026-10-10

All four candidates (POLE_OWNER_CHANGE_DROPS_WIRES_1, FALLEN_WIRE_SHOCK_1, WIRE_DOWN_ALERT_1, TAP_CONSERVATION_SELFTEST_1)
were already built at L0 earlier; remaining criteria are live (L1/L2/L4), needs=bridge. Nothing left to implement offline.

Added: probe verbs `owner:ID,player|hostile` and `ownersweep` (AerialProbe.cs) plus walk row
M17_owner_change_cuts_cross_owner_wires in validation_aerial.py, the functional script for GS-5 (live run owed; PROVISIONAL).
Build clean via winbuild.
