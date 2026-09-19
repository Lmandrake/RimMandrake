# ENVHAZARDS_DLL_REBUILD_OWED_1 — EnvironmentalHazards repo DLL stale vs source, rebuild + redeploy

Filed 2026-09-18 (FOUNDRY, offline/BELT). Queue description: "EnvironmentalHazards
repo DLL is stale vs source (RM_RootCausewayBiomeExtension.cs 21:29 > DLL build
20:12) — rebuild + redeploy".

## 2026-09-18 (FOUNDRY, offline/BELT) — verified, rebuilt, deployed, closing

**Verified stale first** (mtimes in a fresh worktree checkout are useless — every
file under `Source/` and the `.dll` shared the same checkout-time mtime cluster —
so staleness was checked via git history instead): the most recent commit
touching any `.cs` file under
`src/RimMandrake/EnvironmentalHazards/Source/` is `7e8587ceaa2431f` (2026-09-17
21:38:20 -0700, "Code review: fix RM_Churnmud defName collision between
Greentide and FlowWorks", a real 1-line defName-string fix in
`RM_RootCausewayBiomeExtension.cs`), which postdates the DLL's last committed
build at `b8d87d692bc6b5d1` (2026-09-17 20:25:15 -0700, `ROT_LIVE_PREPARATIONS_1`).
Confirmed genuinely stale — proceeded.

Built clean with the user-local .NET SDK
(`/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build … RM_EnvironmentalHazards.csproj
-c Release`, Windows-native path form, 0 warnings/0 errors). Deployed via
`deploy_custom_mods.py --mod EnvironmentalHazards` (dry run showed exactly one
drifted file, the DLL; `--apply` wrote it and reported `VERIFIED in sync`).
`validate_patch.py` was not run — no XML changed, so it's not applicable to a
pure DLL rebuild.

Note for whoever loads next: the mod reports "not enabled in ModsConfig" in the
current (minimal) mod list, so this deploy is inert until a full-list load; the
DLL is now current regardless.
