# TEXREGEN_SWBESTIARY_DECIDE_NO_ROSTER_OWNS_IT

SWBestiary defs in no biome roster that still ship donor bytes (394 per the 2026-10-18 audit; the job builder resolves them
to 248 target defs / 208 rows / 227 job files, many defs sharing one texture).

**Owner decision, 2026-10-18, by question card: redraw ALL of them, in the background, accepted for now (reviewed later).**

Done: `donor_regen_jobs.py build --sw-only` wrote `design/RimMandrake/swbestiary_regen_jobs_2026-10-18.json`; the feeder
(`rm-donor-regen-feeder`, every 10 min, cap 40 shared) now feeds the dregen_ list first, then this one. Canon creatures
carry their `canon` slug. Install: `art_accept_finished.py --prefix dregen_` (no --apply until renders land).
