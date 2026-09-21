# PATCH_FILES_UNDER_DEFS_INERT_1 — a patch under `Defs/` does nothing, loudly then silently

## what is wrong

RimWorld loads everything under a mod's `Defs/` folder **as Defs**. A file whose root is
`<Patch>` placed there is parsed by the def loader, which reports
`Type PatchOperationX is not a Def type or could not be found` and then moves on. **Every
operation in the file is inert.**

MEASURED 2026-09-21 from the full-list cold load (`Transient/Player.log.coldload_2026-09-21`,
620 active mods) and confirmed by parsing every XML under `src/` and testing
`root.tag == "Patch"` while a `Defs` path component is present — **exactly 2 files, matching
the log's two errors:**

| file | ops | what is inert |
|---|---|---|
| `src/RimMandrake/GelatinousSlime/Defs/Patches/DryingBiomes.xml` | 4 | the CURE GEOGRAPHY — the owner's mechanic tagging desert/arid biomes and the salt ocean as places slimification DECAYS. The mod's whole cure story. |
| `src/RimMandrake/WreckedMachines/Defs/Patches/WreckedMachines_HideDonorSmelter.xml` | 3 | 🔴 **an owner ruling of 2026-09-16**, verbatim *"remove the VFE factory, not the manual one"* — `WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1`. The donor's Automated Smelter has stayed buildable the whole time. |

🔑 **The content of both files is correct.** This is purely a folder-location defect — move
them to the mod's top-level `Patches/` folder and they work as written.

## spec

1. Move each file from `<Mod>/Defs/Patches/` to `<Mod>/Patches/`. Do not rewrite the XML.
2. Redeploy both mods and confirm the two `is not a Def type` errors are gone from the next
   log.
3. **Prove the operations actually took**, which is the real test — a patch that matches
   nothing logs nothing (`PatchOperationConditional` and `PatchOperationFindMod` both return
   true on no match). For the smelter: confirm `VFEFactory_AutomatedSmelter` has no
   `designationCategory` in the live game. For the cure: confirm the four vanilla BiomeDefs
   carry the `DryingBiomeExtension` modExtension.
4. Add a guard so this cannot recur — a selftest that fails if any `root.tag == "Patch"`
   file sits under a `Defs/` path.

## Watch out

- ⚠️ **Do not widen this to "every file under Defs/ mentioning PatchOperation".** That
  search returns ~20 files and is WRONG — a first pass made exactly that error. Most are
  ordinary def files that merely contain the string. The defect is the ROOT ELEMENT being
  `<Patch>`, and it is 2 files.
- 🔴 **Verify the smelter ruling landed before closing `WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1`
  if it is recorded as done.** It has been shipping as a no-op since 2026-09-16.

## criteria

Both files live under `Patches/`, the two def-loader errors are gone, each patch's effect is
confirmed in the live game, and a selftest refuses the misplacement.
