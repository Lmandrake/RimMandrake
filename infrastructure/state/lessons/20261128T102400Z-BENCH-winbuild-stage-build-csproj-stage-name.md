winbuild.stage_build(csproj, stage_name=X) is not compile-only: it copies the built DLL and .srchash back into the mod's Assemblies/ in the clone. A reader or fixer that only wants a compile check dirties the committed DLL (seen 2026-11-28, fresh reader group E). Restore with git show HEAD:<path> > <path>, or build once at the end with every .cs change in.
item: RIMMANDRAKE_READ_FIX_70390D63_WITH_FRESH_EYES
home: skills/clone-landing-commits
