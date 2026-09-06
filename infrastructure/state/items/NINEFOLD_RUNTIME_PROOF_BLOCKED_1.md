# NINEFOLD_RUNTIME_PROOF_BLOCKED_1 — PROVEN 2026-09-05

✅ **The Ninefold god-hook system attaches AND fires.** Both halves proven against a
live game, BENCH holding the bridge, 2026-09-05.

## Attachment — 16/16

Minimal 9-mod load (Core + 5 DLCs + Harmony + RimBridgeServer + Ninefold), restarted
through `src/RimMandrake/bridgetools/launch_and_wait.sh` (Steam route — a bare-exe
launch intermittently breaks Harmony assembly loading, which is the thing under test).
Bridge up in **14 s**.

`jawa/harmony_patches` over all 16 target type+method pairs from
`src/RimMandrake/Ninefold/Source/Patch_*.cs` (17 files, 16 unique pairs — `Pawn`
appears twice, `Kill` and `SetFaction`): **every one shows a `RimMandrake.Ninefold.Patch_*`
attached. Zero misses.** This is the payoff of the `Ninefold.csproj` fix that removed
`EnableDefaultCompileItems=false` and the hand-kept `<Compile Include>` list, which had
been compiling only 5 of the 15 patch files.

## Firing — YES, with before→after on every trigger

Read route: `jawa/drain_log` filtered on `"Ninefold] "`, which surfaces
`GameComponent_Ninefold.ApplyDelta`'s own before→after line. Map generation *itself*
organically fired hooks before any deliberate trigger (a colonist downed in a wildlife
scuffle; several scenario-granted research completions).

| trigger | god: before → after | patch |
|---|---|---|
| `jawa/map_fire`, 25/36 cells caught | Zizzik 0→3 · Sh'kaar 3→6 | `Patch_FireStarted` — the rate limiter collapsed 25 ignitions to one credit each, as designed |
| `jawa/explosion_at` r=2.5 | Ta'Baa 0→3 · Sh'kaar 6→9 · Zizzik 3→6 · **Ozzik 100→97** | `Patch_ExplosionOccurred` — four gods in one postfix; negative delta and clamp math both live |
| `jawa/research_finish_project` (Machining, recursed into Smithing) | Ozzik 97→100→100 (clamped) · Ohm 21→24→27 | `Patch_ResearchCompleted` — recursion guard held, no double-credit |
| `jawa/damage` on a live Rat (`dead:true` in the same call) | Sh'kaar 9→17 | `Pawn.Kill` via `Patch_BattleResolved` |

**No case of success-reported-but-nothing-moved.**

`Patch_KillManner` did not additionally fire on the rat: the synthetic damage carried no
weapon and no instigator to classify. Expected, not a failure — but it means **kill-manner
classification is still unproven** and wants a real armed kill to close.

## What this proved that was only ever asserted before

The fire **rate limiter**, the research **recursion guard**, and the satiation **clamp**
all held under live pressure exactly as their source comments claim. None of the three had
been exercised at runtime until now.

## Owed

- ⚠️ `Mods/Ninefold/About/About.xml` still says **"five Harmony-patched event hooks"**.
  Stale — there are 16. Confirmed, deliberately not fixed in this pass.
- `Patch_KillManner` needs a real armed kill to prove classification.

## Method notes worth keeping

- 🔴 **`ModsConfig.xml` describes the NEXT load, not the running process.** During this
  session the file said 601 mods while the running game had 22, because it was restored
  after that launch. The authoritative readings are `jawa/mod_inventory` and the
  `[JawaBench] context: modSet N/<hash>` line in `Player.log`.
- 🔴 Bridge calls must run under **Windows Python** (`python.exe`). WSL2 is NAT-mode and
  cannot reach Windows loopback; `python3` raises `ConnectionRefusedError`, which says
  nothing at all about whether the game is running.
- The owner's 601-mod list was backed up to
  `Config\ModsConfig.FULL601.bench-backup.xml` and **restored, verified 19767 bytes.**
