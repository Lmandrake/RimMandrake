# DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1

## spec

Big-dump load 2026-09-03: startup dump PROVEN (525 def files, 589 mods, capture
2026-09-03T06-10-14Z). But the on-demand action is UNREACHABLE via bridge.
Measured at both Entry and Playing: `list_debug_action_children('Actions\RMDefDump')`
= 'Could not find'; the category never appears; a flat execute of 'Actions\Dump
defs now (all)' timed out WITHOUT `RunOnDemand`'s own first log line
('[RimMandrake.RimDefDump] ON-DEMAND dump requested') ever printing — so the
handler never ran. KEY DISCRIMINATOR: the proven-working RMInject rimplace
leaves are `actionType=ToolMap` and appear FLATTENED under Actions as
'T: Run plan: ...'; RMDefDump uses plain `actionType=Action` (default) with a
category, and is absent entirely — same as RMInject's own category node
('Actions\RMInject' also 'Could not find'). Hypothesis: the bridge only
surfaces/fires ToolMap + pawn-targeted custom leaves, not plain Action-type
ones. Fix options: (a) give RMDefDump's DebugActions actionType=ToolMap or a
targeting type the bridge fires, or (b) add a jawa/ companion tool that calls
DefDumper.RunOnDemand directly. The DLL is byte-identical repo↔game and
LudeonTK-imported, so this is a bridge-surface gap, not a registration bug.

## what shipped (option b, FOUNDRY, 2026-09-03)

`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchDefDumpTools.cs` —
a new `jawa/rimdefdump_run` tool that calls
`RimMandrake.RimDefDump.DefDumper.RunOnDemand(mode)` **directly**, as a plain
static method call, referencing `RimDefDump.dll` from the game's own deployed
`Mods\RimDefDump\1.6\Assemblies\` folder (same pattern the csproj already uses
for `RimMandrakeOracle.dll`, `Private=false` against the copy already loaded
in-process). This has zero dependency on `GenTypes.AllTypes`, on
`DebugTabMenu_Actions`, or on either bridge's own debug-action discovery
surface — whatever is actually keeping the two `[DebugAction]`s unreachable
(a related, still-open investigation, `FLUID_CANAL_DEBUG_SURFACE_1`, names a
stale `GenTypes.AllTypes` snapshot as the leading theory for a *different*
mod, unconfirmed for this one) simply doesn't matter to this tool, because it
never asks either bridge to find or run a debug action at all.

Also checked, before building anything new: this project's own existing
`jawa/debug_actions` catalogue tool (`JawaBenchDebugActionTools.cs`, built for
a *worse*, unrelated problem — the host's `rimworld/search_debug_actions`
wedging the bridge for minutes) walks `GenTypes.AllTypes` directly and is
explicitly "a catalogue, not a trigger" per its own docstring — even if it can
find RMDefDump's actions, it was never going to be able to run them, so
extending it was not a viable route to this item's fix either way.

Built clean (0 warnings/errors, `bridgetools/build.py --gm --apply`), deployed,
verified `jawa/rimdefdump_run` present in the live bridge's tool list on a
fresh full-589-mod cold-load restart.

## verify

Live, full 589-mod list, fresh restart (2026-09-03):
1. `rimworld/get_game_info` confirms bridge reachable.
2. `jawa/rimdefdump_run` present in `tools/list`.
3. Called with `mode="all"` — `success: true`.
4. **Positive observation, not just success:true**: `DefDump/captures/`
   contained 4 directories before the call; exactly one new directory,
   `2026-09-03T22-20-01Z`, appeared after. Its `manifest.json` reads
   `capturedUtc: 2026-09-03T22-20-01Z`, `modCount: 589` — matching the live
   session exactly, proving the dump that ran was fresh, not a stale replay.

## criteria

1. **RMDefDump's on-demand path is now reachable without a game restart** —
   `jawa/rimdefdump_run` fires it directly. Met.
2. The cause is named: the plain-`Action`-type `[DebugAction]`s are
   unreachable via either bridge's debug-action discovery surface (both the
   host's `rimworld/*` tools and this project's own `jawa/debug_actions`
   catalogue-only tool) — but the fix sidesteps that surface entirely rather
   than repairing it, which is the pragmatic close per the item's own option
   (b). The exact mechanism keeping the debug-action tree itself unreachable
   remains open and is being tracked separately for a related mod under
   `FLUID_CANAL_DEBUG_SURFACE_1` — not re-litigated here since a working
   direct route makes it moot for RMDefDump specifically.
3. `FLUID_CANAL_FLOOD_LIVE_CHECK_1` is unrelated to this item (different mod);
   not affected either way.
