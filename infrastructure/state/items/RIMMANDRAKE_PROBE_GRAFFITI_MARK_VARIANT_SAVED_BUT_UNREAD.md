# RIMMANDRAKE_PROBE_GRAFFITI_MARK_VARIANT_SAVED_BUT_UNREAD

Found by RIMMANDRAKE_SCRIPT_GRAFFITI_SETTINGS_SCENES_IDEO_RELOAD_TOO (2026-11-15) while scripting `sc_settings`.

## spec
`sc_settings` expects each mark's variant equal before and after a reload. `Filth_Mark.variant` is scribed (`rmMarkVariant`,
`Filth_Mark.cs:304`) but no probe reads it: `RM_GraffitiSocialProof.Marks` (`RM_GraffitiSocialProof.cs:177`) prints def, craft, maker,
subject and side only. So `marks_variant_equal_after_reload` in `scene_settings_each_switch` raises `MISSING TOOL`. Add ` variant N` to
the Marks line (before ` side `), extend `_MARK_LINE`/`_mark_rows` in `src/RimMandrake/Graffiti/validation.py` to read it, and fold the
variant into `marks_equal_after_reload`, deleting the MISSING TOOL row.

## verify
Acceptance test:
Watched failing on the base 2026-11-15 (AssertionError); expected `PASS`:

    python3 -c "
    s=open('src/RimMandrake/Graffiti/validation.py').read();c=open('src/RimMandrake/Graffiti/Source/RM_GraffitiSocialProof.cs').read()
    assert 'MISSING TOOL: no probe reads Filth_Mark.variant' not in s
    assert '\" variant \" + m.variant' in c and 'variant' in s.split('_MARK_LINE = ')[1].split('\n')[0];print('PASS')"

Live: `bridge: validation.py scene_settings_each_switch`, recorded UNRUN until run.
