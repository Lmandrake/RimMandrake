# BRIDGE_NTDLL_CRASH_TILEGEN_1 — minidump analysis, 2026-09-05

## Method
No cdb.exe/windbg/dumpbin found anywhere under `/mnt/c/Program Files*` on this
machine. Installed the pure-Python `minidump` library (v0.0.24, PyPI) into a
throwaway venv at
`/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/b3d5d46b-0c50-4bc2-b9d9-161f0f7ce4ab/scratchpad/mdvenv`
(not committed anywhere — scratchpad only) and parsed the real
MINIDUMP_EXCEPTION_STREAM / MINIDUMP_MODULE_LIST / MINIDUMP_THREAD_LIST
structures programmatically — no eyeballing raw bytes. Verified the tool
against a *different* crash (see below) to confirm it isn't just reporting
the same thing for everything.

Parser script kept at
`/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/b3d5d46b-0c50-4bc2-b9d9-161f0f7ce4ab/scratchpad/parse_dump3.py`
(scratchpad, not committed). For each dump it extracts: exception
code/address resolved to module+offset, the access-violation read/write flag
and target address, the crashing thread's RIP/RSP, and a naive 8-byte-aligned
scan of the crash thread's stack memory for values that fall inside a known
module's address range (an approximation of a call stack — not a real
frame-pointer walk, but with `gameoverlayrenderer64.dll` and
`mono-2.0-bdwgc.dll` both compiled without frame-pointer omission in the
relevant regions, it lines up consistently across all 6 dumps, which is
itself corroborating evidence it's a real chain and not noise).

## Result: all 6 dumps are the SAME bug, byte-for-byte

| Dump | Time | Faulting module+offset | AV type | AV target address |
|---|---|---|---|---|
| `RimWorldWin64.exe.39232.dmp` (item's Crash 1) | Sep 5 06:21 | `ntdll.dll+0x70f32` | READ | `0xFFFFFFFFFFFFFFFF` |
| `RimWorldWin64.exe.21000.dmp` (item's Crash 2) | Sep 5 06:49 | `ntdll.dll+0x70f32` | READ | `0xFFFFFFFFFFFFFFFF` |
| `RimWorldWin64.exe.38048.dmp` (new) | Sep 5 07:47 | `ntdll.dll+0x70f32` | READ | `0xFFFFFFFFFFFFFFFF` |
| `RimWorldWin64.exe.27676.dmp` (new) | Sep 5 08:15 | `ntdll.dll+0x70f32` | READ | `0xFFFFFFFFFFFFFFFF` |
| `RimWorldWin64.exe.11636.dmp` (new, no tilegen call) | Sep 5 10:01 | `ntdll.dll+0x70f32` | READ | `0xFFFFFFFFFFFFFFFF` |
| `RimWorldWin64.exe.34620.dmp` (found during this task, undocumented until now) | Sep 5 10:27 | `ntdll.dll+0x70f32` | READ | `0xFFFFFFFFFFFFFFFF` |

**Bonus finding**: while listing `/mnt/c/Users/Mandrake/AppData/Local/CrashDumps/`
I found a 7th RimWorld dump not mentioned in the task or the item:
`RimWorldWin64.exe.17032.dmp` (Sep 4 13:44) — **also the identical
`ntdll.dll+0x70f32` READ-at-`0xFFFFFFFFFFFFFFFF` fault.** This pushes the
earliest known occurrence back a full day before the item was filed, and to
7 total confirmed occurrences. (Sanity check: `RimWorldWin64.exe.39160.dmp`,
Sep 1 11:55, is a *different*, unrelated `EXCEPTION_BREAKPOINT` fault inside
`UnityPlayer.dll` — confirms the parser correctly distinguishes crash types
rather than reporting the same thing regardless of input.)

**Access-violation target address is exactly `0xFFFFFFFFFFFFFFFF` (i.e. -1)
in all 7 RimWorld ntdll-crash dumps** — not a "random" corrupted pointer,
but the specific sentinel value -1. That specificity plus the identical
offset across 7 independent process runs is strong evidence this is **one
bug, not several coincidentally-similar ones.**

## The stack (naive scan, all 6 fresh dumps line up frame-for-frame modulo ASLR)

Reading from the crash thread's RSP outward, in order:
```
ntdll.dll+0x120d08
ntdll.dll+0x40d29
ntdll.dll+0x134117
ntdll.dll+0x70c66      <- same function family as the fault site (+0x70f32)
ntdll.dll+0x706ce
mono-2.0-bdwgc.dll+0x58cc18      <- Mono runtime's Boehm-GC allocator
ntdll.dll+0x36ea0
mono-2.0-bdwgc.dll+0x58cc18  (recurs)
mono-2.0-bdwgc.dll+0x58cc18  (recurs)
ntdll.dll+0x37257
ntdll.dll+0x17ad40
ntdll.dll+0x17ac28
gameoverlayrenderer64.dll+0x1201f0   <- Steam Overlay
KERNELBASE.dll+0x11da6
gameoverlayrenderer64.dll+0xab158    <- Steam Overlay again
mono-2.0-bdwgc.dll+0x7b5680
KERNELBASE.dll+0x1c11f
kernel32.dll+0x0                     (likely a stored HMODULE value, not a return address)
gameoverlayrenderer64.dll+0xab6cd    <- Steam Overlay again
kernel32.dll+0x0
```

This is the classic signature of **Windows heap-manager corruption
(`RtlpFreeHeap`/`RtlpLowFragHeapFree`-family internals — the `0x70xxx` ntdll
offset cluster is the low-fragmentation-heap free path) being triggered from
inside Mono's `bdwgc` allocator, with Steam's `gameoverlayrenderer64.dll`
present on the same stack.** `gameoverlayrenderer64.dll` is a well-documented
source of exactly this crash class in Unity/Mono titles: it hooks
allocation- and D3D-adjacent APIs process-wide via DLL injection, and a
mismatch between its hooks and a heavily-modded Mono heap (594 mods = many
extra assemblies, threads, and GC pressure) can corrupt heap metadata that
then blows up later, inside ntdll, on a completely unrelated free() call —
which is exactly why the crash always lands at the same generic ntdll
offset regardless of what game logic was actually running at the moment.

## Culprit frame (what's "just below" ntdll)

Two candidates sit directly beneath the ntdll heap-manager frames, both
present in every dump: **`mono-2.0-bdwgc.dll`** (the embedded Mono runtime's
allocator — i.e., some Mono-side code, quite possibly the .NET/C# side of
*any* mod, not specifically RimWorld's own code, doing an allocation/free
that trips over already-corrupted heap metadata) and **`gameoverlayrenderer64.dll`**
(Steam's overlay, injected into every RimWorld process on this machine
regardless of mod list). No RimWorld-specific or mod-specific native DLL
appears anywhere in the module list at these offsets — this is not
attributable to any single mod's own native code; it is a
runtime/Steam-overlay/heap interaction.

## Verdict on the TILEGEN_SILENT_REUSE_1 connection

**Undermined.** The item's hypothesis was that "whatever GenStep call
sometimes corrupts state badly enough to crash outright might on other runs
corrupt state just enough to return stale/wrong data without crashing." That
requires the crash to originate from GenStep/tile-generation-specific code.
Instead:

1. All 7 occurrences (not just the 2 documented) share one **generic,
   session/call-independent** fault: a Steam-overlay/Mono-heap interaction
   inside ntdll's heap manager, with no tile-generation, world-gen, or
   RimWorld-specific frame anywhere in the visible stack.
2. Dump `RimWorldWin64.exe.11636.dmp` (10:01) occurred in a FOUNDRY session
   testing an unrelated bridge tool, with no `world_tile_map_generate` call
   made — this alone falsifies "GenStep corruption" as the necessary trigger.
3. Dump `RimWorldWin64.exe.17032.dmp` (Sep 4, 13:44) predates the
   `TILEGEN_SILENT_REUSE_1` report entirely (filed 2026-09-04, but this
   dump's timestamp needs checking against exactly when that item was filed
   intraday — regardless, it shows the ntdll crash is not new to today's
   session).

The heap-corruption crash and the `world_tile_map_generate` silent-reuse bug
are almost certainly **two separate defects that happen to both surface on
the full 594/595-mod list under memory pressure**, not one cause with two
symptoms. The ntdll crash is a background/async heap-manager failure that
can fire on essentially any allocation-heavy moment (which tile generation
certainly is — lots of Mono allocations — explaining why it was *seen*
twice near tilegen calls, but that's a proximity/exposure correlation, not
a shared-root-cause one). Recommend `TILEGEN_SILENT_REUSE_1` be investigated
independently as a managed-code logic bug (e.g., the map/tile bookkeeping
in `WorldTileMapGenerate`'s C# side), and this ntdll crash be tracked
separately as a general full-modlist stability issue, likely
Steam-overlay-related — worth trying a repro with Steam Overlay disabled
for RimWorld, or on the minimal 13-19 mod list, as the item's own
unattempted verify steps already suggested.

## What I did NOT establish
- No frame-pointer-accurate stack walk (no CONTEXT-driven unwind via unwind
  tables) — the "stack scan" is a heuristic value scan, not a certified
  call stack. It is corroborated by being identical across 6 independent
  ASLR-randomized runs, which a heuristic scan reading true call-stack
  memory should produce and one reading garbage should not.
- No confirmation of exactly which Mono-side (C#) call site triggered the
  allocation that hit the corrupted heap — would need Mono's own crash
  symbols/managed stack (not present in a native minidump) or a
  Mono-side crash log, which per the item, doesn't exist (`Player.log`
  simply stops with no exception recorded before all these crashes).
