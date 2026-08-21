## spec
`to_elementtree_xpath()` in `skills/rimworld-modding/scripts/validate_patch.py` stripped
a leading `/Defs/` but not a leading `Defs/`. RimWorld evaluates a patch xpath against
the **XmlDocument**, whose child is `<Defs>`, so the bare form is valid and standard;
ElementTree and lxml evaluate against the `<Defs>` **root element**, so the bare form
silently means `Defs/Defs/...` and matches nothing.

⇒ Every op using it drew `0 nodes in the on-disk Defs` — **which is the same output a
genuinely dead xpath produces, and telling those two apart is the whole reason this
validator exists.** 42 xpaths across this repo's own patches were affected (against
6,321 using `/Defs/`, which is why it survived so long).

Found 2026-08-21 extending `GrimTerraTexPaths_Fix.xml`: all four of its ops came back
0 while three of them were already shipped and working in game.

## verify
`validate_patch.py src/Jawa/Jawa_Patches/Patches/GrimTerraTexPaths_Fix.xml --defs <workshop> --defs <Data>`
reports 4 ops at 1 match each and `0 errors, 0 warning(s)`, where before the fix it
reported four 0-node warnings. Then the whole `Patches/` directory still passes.

## criteria
offline only, and it is BUILD's own gate: no patch this repo ships may report a
0-node warning that is an artefact of the xpath's leading form rather than of the def.

## notes
⚠️ **Historic validator output is now suspect in one direction only.** A past
`0 nodes` warning on a bare-`Defs/` xpath was FALSE and the patch was probably fine;
a past `1 match` was never affected. Do not re-open closed patch items wholesale — but
if one was closed as "matches nothing", re-run it.
