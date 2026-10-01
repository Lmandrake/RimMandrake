# NORTHSTAR_EVERYWHERE_PROGRAM_1

Owner, 2026-10-01 (typed): *"Ticket writing basic northstar scripts for all mods at this time centered around their intended functionality. ... It's worth slowing or stopping all current build to get this in place everywhere and really exercise northstar. I really do mean stop and start working a new way. This would be as big a need as rerunning clean dirty code is now."*
Also typed: *"Agents absolutely can build and approve validation scripts and declare passing. I will periodically release adversarial agents and even gpt reviews to criticize them or grow them."*

## spec
Every mod gets a first north-star script (validation.py + driver plan) centred on its intended function, run live through the fast driver (`src/RimMandrake/Utils/northstar_driver/`) and recorded. Debugging then follows `design/RimMandrake/debug_process.md`: script first, every poking session ends by writing what it learned (including informative false theories) into the script. **Until every child is closed, new content work is paused** (bug fixes and script/harness work only).

## children
One `<MOD>_FIRST_SCRIPT_1` per mod (61 non-art mods), `ART_OVERRIDE_FAMILY_SCRIPT_1` for the 48 `*ArtOverride` mods (one parametrized script), `NORTHSTAR_COVERAGE_AUDIT_1` for the 55 mods that already have a validation.py, `NORTHSTAR_ADVERSARIAL_REVIEW_1` (standing: periodic adversarial/GPT review of scripts).

## criteria
All children closed against a results JSON (Transient/northstar/…) or commit; `modcheck status` lists every mod with a script; the pause is lifted by the definition in `debug_process.md`.
