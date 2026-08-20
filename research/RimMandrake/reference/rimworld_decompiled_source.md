# RimWorld's decompiled C# source — where it is and how to remake it
## Provenance for a 42 MB derived tree that is deliberately not in git

**Established:** 2026-08-19 · **Location:** `D:\Luke\dev\reference\rimworld-decompiled`

---

## The one command

```powershell
& "$env:USERPROFILE\.dotnet\tools\ilspycmd.exe" -p `
  -o "D:\Luke\dev\reference\rimworld-decompiled" `
  "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll"
```

✅ **Verified by running it, 2026-08-19** — not reconstructed from the output. It produced
**9,217 `.cs` files in 16 seconds**, plus `Assembly-CSharp.csproj`.

🔑 **16 seconds is the whole point.** This tree is cheap to remake, so it is *derived* in the
strict sense: provenance belongs in git, the 42 MB does not. If the folder disappears, run the
command above.

## What it is

| | |
|---|---|
| files | 9,217 `.cs`, 42 MB |
| top namespaces | `Verse\` (1,747 files, incl. `ThingDef.cs`, `Map.cs`), `RimWorld\` (5,913) |
| vendored deps present | Ionic.Zlib, DelaunatorSharp, KTrie |
| project file | `Assembly-CSharp.csproj`, `net472` target declared by ilspycmd as `net40` |
| decompiler | `ilspycmd` 8.2.0.7535 (`ICSharpCode.Decompiler` 8.2.0.7535) |

**Source assembly it was made from:**
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
· 15,777,280 bytes · mtime 2026-06-30 12:11:41 · md5 begins `bf39a6f68f2d`
· game version `1.6.4871 rev590`

## Currency check — how to tell if this tree is stale

**Fingerprint, not timestamp.** Compare the md5 prefix of the live `Assembly-CSharp.dll`
against `bf39a6f68f2d` above. If it differs, the game updated and this tree is stale —
re-run the command. The tree's own file dates prove nothing, because a copy refreshes them.

## ⚠️ Why the earlier tree was replaced

A decompiled tree already existed at `C:\Users\Mandrake\AppData\Local\Temp\rwdec` (9,217
files, 2026-08-15). It was **rescued out of `%TEMP%` on the owner's instruction, then
discarded in favour of a fresh decompile**, because the two differ in quality even though they
come from the same DLL:

- The old tree carried `//IL_0124: Unknown result type (might be due to invalid IL or missing
  references)` comments throughout — the signature of a decompile run without resolvable
  reference assemblies. The fresh tree has **zero** such comments across all 9,217 files.
- Rendering differed too: `Mathf.Min(a, b, c, d)` in the fresh tree vs
  `Mathf.Min(new int[4]{…})` in the old.

🔑 **This is not cosmetic.** RimSage's `read_csharp_symbol` extracts method bodies by brace
counting and **assumes the decompiled source contains no comments**. Feeding it the old tree
would have produced silently wrong symbol boundaries. See
`research\RimMandrake\reference\rimsage_rimcp_source_index_mcp.md` §6.

The file *sets* were identical, which is what confirms both came from the current
`Assembly-CSharp.dll` — so this was a quality upgrade, not a version correction.

## What this tree is NOT

- **Not the mods.** Mod C# source lives at `D:\Luke\dev\Rimworld\vendor\mod_sources`
  (6,280 `.cs`: VanillaExpandedFramework, VehicleFramework, VanillaGravshipExpanded, …).
- **Not Ludeon's shipped samples.** `…\common\RimWorld\Source` holds 43 reference `.cs`
  files, 488 KB — examples, not the game.
- **Not in git, and must not be.** 42 MB of regenerable output. Commit this file instead.

## Licensing

Decompiling for personal use is permitted under the
[RimWorld EULA](https://rimworldgame.com/eula) — this is the same basis on which RimSage
instructs its users to supply a decompiled tree. **Do not publish or redistribute it.**
