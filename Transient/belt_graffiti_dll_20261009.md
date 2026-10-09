# SacredGraffiti DLL rebuild (belt, 2026-10-09)
- Rebuilt in private clone /home/mandrake/.seat-tmp/graffiti_rebuild via winbuild.py SacredGraffiti; DLL + .srchash landed together, PUBLISHED 163785bcc.
- Behaviour: DLL last built 7a14e5ed2 (2026-09-11); Source/*.cs unchanged since then (only later touch was csproj build-path commit 47560e4ea). Rebuilt DLL is same size (7680 B); no behaviour difference expected.
- Checks: selftest_sacredgraffiti_lint 19/19; dll_source_stamp check reports SacredGraffiti MATCH on origin/main after landing (see report).
- Stray untracked src/RimMandrake/SacredGraffiti/Assemblies/SacredGraffiti.dll.srchash in the shared foundry tree: left untouched; it now collides with the tracked file, so the owner session should delete it (it will block/overwrite on next pull).
