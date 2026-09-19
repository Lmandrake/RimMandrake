# ANCIENT_RUINS_FAMILY_CUT_1 — done

Owner ruling 2026-09-09: cut the ancient-urban-ruins mod family
(`xmb.ancienturbanruins.mo` + `aurad` + `aurvl` + orphaned
`Charlie.Muzzle.Flash.for.ancientruins` patch), per the deep audit
`ANCIENT_RUINS_MOD_AUDIT_1` (`design/Jawa/mods/ancient_ruins_mod_audit.md`).

Full method, evidence and the tag-survivor cross-check: see the commit that
closes this (`4d6c684e`) and the `KEYS` block comment in
`src/RimMandrake/Utils/cherrypick_build.py`. Summary: 559 of the family's
1,005 defs are Cherry-Picker-reachable and were cut; the other 446 are types
Cherry Picker never registers and fall out of use once the 5 QuestScriptDef
kill switches are gone. Tag-survivor cross-check confirmed clean — 8 tags go
to zero carriers, all inside the cut family, no surviving pawnkind disarmed.
Cut applied live, verified by reading the config back.

The `<=1h ComplexLayoutDef reference` decompile is
`design/Jawa/worldbuilding/complexlayoutdef_acm_reference.md`.

## Noted, not actioned (outside this item's scope)

Cherry Picker's SHIP/REVIEW snapshot mechanism (`cherrypicker_swap.py
--status`) already read "UNRECOGNISED" (matching neither snapshot) before
this cut — pre-existing drift, unrelated to this change. Worth a look
separately.
