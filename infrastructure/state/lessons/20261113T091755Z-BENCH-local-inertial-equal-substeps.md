Local-inertial water must split each recompute into EQUAL substeps (k = ceil(0.2 s / CFL dt), dt = 0.2/k). Splitting as full CFL steps plus a short remainder (0.17 s then 0.03 s) made a lake at rest slosh 2.1 m within 20 water-s, in Python float64 as well as C# integer dL (MandrakeModels stagec drift probe, 2026-11-13); equal substeps hold it to 0.2 mm over 10,000 s. The 60 s fidelity runs never saw it because they used the constant-step Python dt rule.
item: RIMMANDRAKE_TIME_LOCAL_INERTIAL_IN_CSHARP_FIGURES_STILL_GUESSES
home: design/specs/water_solver_decision_2026-11-12.md
