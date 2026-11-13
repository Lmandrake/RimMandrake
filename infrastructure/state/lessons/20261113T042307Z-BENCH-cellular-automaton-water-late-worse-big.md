Game-style cellular-automaton water (ca_game) and WCA2D spread a fixed number of cells per pass, so their flood timing gets WORSE as the map grows: after the pit_dig fix, pit mean depth at 150 s was ca_game 0.200/0.013/0.002 m at 64/128/250 cells against local-inertial 1.55/0.72/0.49 [measured, D:\ClaudeWork\mandrakemodels\pitfix\after2_*.txt]. Their low cost per tick buys water that arrives 10-30x late on a 250 map; do not pick them on cost alone.
item: RIMMANDRAKE_SWEEP_WATER_SOLVERS_ON_BIG_MAPS
home: design/specs/water_solver_decision_2026-11-12.md
