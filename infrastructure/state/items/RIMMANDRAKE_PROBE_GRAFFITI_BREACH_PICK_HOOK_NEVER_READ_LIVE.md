# RIMMANDRAKE_PROBE_GRAFFITI_BREACH_PICK_HOOK_NEVER_READ_LIVE

Found by RIMMANDRAKE_SCRIPT_GRAFFITI_SETTINGS_SCENES_IDEO_RELOAD_TOO (2026-11-15) while scripting `sc_breach_bias_raid`.

## spec
No probe reads what `Verse.AI.BreachingGrid.FindBuildingToBreach` returns (Graffiti's `BreachBiasHook.cs:31` postfixes it), nor a
breaching lord's current breach target (the jawa/lord_* tools only spawn, move and poke lords). So `scene_breach_bias_raid` and the
breach row of `scene_settings_each_switch` (`src/RimMandrake/Graffiti/validation.py`, `_breach_pick`) raise `MISSING TOOL`.
Add a Graffiti probe (e.g. `RM_GraffitiProof.BreachPick`, a `public static string` like the others, reachable by `jawa/static_call`)
that answers the building FindBuildingToBreach picks for the current map's breaching lord (or a given breach start) and that lord's
current target, with cells; then make `_breach_pick` call it through `_static(t, PROOF, "<Method>")` and return (x, z, line).

## verify
Acceptance test:
Watched failing on the base 2026-11-15 (AssertionError); expected `PASS`:

    python3 -c "
    import re;s=open('src/RimMandrake/Graffiti/validation.py').read()
    assert 'MISSING TOOL: no probe reads BreachingGrid' not in s
    m=re.search(r'_static\(t, PROOF, \"(\w*Breach\w*)\"',s);assert m
    assert ('public static string %s(' % m.group(1)) in open('src/RimMandrake/Graffiti/Source/RM_GraffitiProof.cs').read();print('PASS')"

Live: `bridge: validation.py scene_breach_bias_raid`, recorded UNRUN until run.
