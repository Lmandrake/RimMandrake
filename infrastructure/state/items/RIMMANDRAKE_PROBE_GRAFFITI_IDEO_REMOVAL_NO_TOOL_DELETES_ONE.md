# RIMMANDRAKE_PROBE_GRAFFITI_IDEO_REMOVAL_NO_TOOL_DELETES_ONE

Found by RIMMANDRAKE_SCRIPT_GRAFFITI_SETTINGS_SCENES_IDEO_RELOAD_TOO (2026-11-15) while scripting H1_IDEO_RELOAD.

## spec
H1_IDEO_RELOAD (held walk defect #1: `rmMarkMakerIdeo`, `Filth_Mark.cs:297`) needs the colony's ideoligion REMOVED from
`Find.IdeoManager` before a save and reload. No bridge tool or probe does that: the jawa/ideo_* tools create, assign and edit, and only
the start flow calls `IdeoManager.RemoveUnusedStartingIdeos` (`JawaBenchStartFlowTools.cs:345`). So the component
`colony_ideo_removed` of `scene_ideo_removed_save_reload` (`src/RimMandrake/Graffiti/validation.py`) raises `MISSING TOOL`.
Add a Graffiti probe (e.g. `RM_GraffitiSocialProof.DropIdeo`) that moves the colony's pawns and faction to another ideoligion and
removes the old one from the IdeoManager the way the game does, answering what it removed; then call it from that component.

## verify
Acceptance test:
Watched failing on the base 2026-11-15 (AssertionError); expected `PASS`:

    python3 -c "
    import re;s=open('src/RimMandrake/Graffiti/validation.py').read()
    assert 'MISSING TOOL: no bridge tool or probe removes an ideoligion' not in s
    m=re.search(r'_static\(t, (?:SOCIAL_)?PROOF, \"(\w*Ideo\w*)\"',s);assert m
    src=open('src/RimMandrake/Graffiti/Source/RM_GraffitiProof.cs').read()+open('src/RimMandrake/Graffiti/Source/RM_GraffitiSocialProof.cs').read()
    assert ('public static string %s(' % m.group(1)) in src;print('PASS')"

Live: `bridge: validation.py scene_ideo_removed_save_reload`, recorded UNRUN until run.
