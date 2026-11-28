## spec
FlowWorks Mod Settings, section "How cuts and liquids look" (`src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs`,
the `Section(list, "How cuts and liquids look", new[] { ... })` call near line 1848) draws the slider for
`underLiquidShallowOpacity` (line 1949) but does not name it in the section's list. The section's reset and the settings search
work from that list, so the player's "reset this section" leaves the shallow opacity at its changed value and search does not
find it. Its sibling `underLiquidDeepOpacity` is listed. Fix: add "underLiquidShallowOpacity" to that list, rebuild the DLL with
its .srchash.

Found 2026-11-21 by the Manhunter fire-hawk trace while running touched selftests; not caused by that change (the selftest
names no file that change touched). Not fixed there: the FlowWorks in-game visit
(rm-detached-bench-rimmandrake-drive-flowworks-in-game-visi-1795268462) was live on the FlowWorks build, and a source edit plus
DLL rebuild under it would stale its build match.

## verify
`python3 src/RimMandrake/Utils/selftest_settings_screens.py` exits 0.

## criteria
- The section's reset returns underLiquidShallowOpacity to its shipped value, and the settings search finds it.

## Acceptance test
`python3 src/RimMandrake/Utils/selftest_settings_screens.py`. Watched red on base 3b4f44498d (2026-11-21): rc 1, one FAIL line,
"FlowWorks#Main: ... section 'How cuts and liquids look' draws underLiquidShallowOpacity but does not list it (it would not
reset); setting underLiquidShallowOpacity is in no section". Green: rc 0, 0 FAIL lines.

## refs
file: src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs
