## spec
Owner ruling (2026-11-12, via Conductor): KEEP the shipped-settings fuzz matrix ("V&V pilot 1") and make it a standing
offline scheme. His words: "offline randomized validation scripts with sanity checks and conservation laws/principles
outlined that must be obeyed. Keep it in please. Especially since it's offline."

### Today
`src/RimMandrake/Utils/vv_shipped_matrix.py`, with probes `FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs` and
`EmpirePursuit/Source/SelfTest/VV/EpRatesProbe.cs`. Report: `design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md`.
It ran once (2026-10-16). There were 0 failures at the shipped flags across 266,000 scenes, and it reproduced the pre-fix
`fills_from_limitless` 194/2000. Nothing runs it on a clock (inventory row 85, UNMEASURED). Known defect:
VV_MATRIX_FIX_SURFACE_FAILURES_UNDERCOUNT.

### What to build
1. Per mod, a written list of the conservation laws and sanity principles that must hold, for example water mass in =
   out + stored, no negative depth, heat budget closes, and a rate never exceeds its cap. Each law is a sentence plus
   the check that enforces it, and it lives beside the mod's kernel. Start with FlowWorks and EmpirePursuit (the probes
   exist), then the mods with C# kernel fuzz (`selftest_*_fuzz.py`).
2. The matrix reads each mod's shipped settings, so it cannot drift from what ships. It runs offline on a clock (nightly
   selftests or its own timer) and exits red on any law broken at the shipped settings.
3. A planted-bug check per law family (the `mutate_<mod>_fuzz.py` pattern), so a green result is known to be able to go red.

### Done when
FlowWorks and EmpirePursuit have written law lists. The matrix runs on a clock with a fresh reading, and each law
family has gone red once under a planted break.
