# COLD_LOAD_STALL_INTERMITTENT_1 — RESOLVED, NOT A BUG

**Verdict:** the "intermittent cold load stall" does not exist. Every reproduction
was the game sitting **healthy at the main menu**, misread as an infinite load hang.

## What the signature actually was

An idle main menu after a completed cold load:

| observed | real meaning |
|---|---|
| Player.log frozen at PerformanceOptimizer's `Finished transpiling N methods` | loading finished; an idle menu logs nothing |
| CPU burning ~75–80 CPU-sec/min | the menu renders frames continuously |
| bridge answers in ~20ms with `no_game` / `Entry`, never `Playing` | there IS no game — nobody loaded a save |
| "main thread alive" (FOUNDRY's own words) | because it was never wedged |

`Playing` only ever arrived in the one run where a save was actually loaded
(prev.log shows WORLDMAP_V1_original then gravship_scratch loading after the
checkpoint). The other launches were killed while idling at the menu — so the
"4 stalls / 5 launches" was really **5/5 loads succeeding to the menu.**

## How it was proven (the instruments are the deliverable)

Two instruments, both committed, both reusable for any future "is the load stuck?":

1. **`jawa/load_stall_probe`** (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchLoadStallProbe.cs`)
   — reads `Verse.LongEventHandler` internals **off the main thread** (a normal
   marshalled tool would join a real hang and never return). During the "stall":
   `programState=Entry`, `coreStaticAssetsLoaded=true`, `currentEvent=null`,
   `queuedEventCount=0`, `eventThread=null`, `toExecuteWhenFinished=[]` — the
   LongEventHandler is **idle**. A real load hang would show a live `currentEvent`
   and an alive `eventThread`.
2. **`LoadTracer`** mod (`src/RimMandrake/LoadTracer/`) — replaces
   `StaticConstructorOnStartupUtility.CallAll` with a byte-equivalent loop that logs
   each `[StaticConstructorOnStartup]` type before invoking it, and brackets
   `FloatMenuMakerMap.Init` / `BakeStaticAtlases`. It showed all **1531** static
   ctors completing, atlases baked, bridge up — every suspected stage finished.
3. **Decisive test:** `rimworld/get_ui_state` (marshals to the main thread) returned
   in **0.0s** → main thread alive; then `start_debug_game_ready` drove the "stalled"
   menu to `programState=Playing` in **56s**. There was nothing to unstick.

## PerformanceOptimizer — cleared

PO's `Finished transpiling` line is just the last thing written before an idle menu;
its FasterGetComp coroutine had already completed. Its workshop folder is unchanged
since 2025-12-06 (no update coincides with the "stalls"). The mechanistic
transpiler-race hypothesis is moot — there is no hang to explain. The staged
`deployed/config/Mod_2664723367_PerformanceOptimizerMod.FasterGetComp-OFF.xml` A/B
variant is kept for reference but is not needed.

## Loose end (a NEW item if it matters, not this one)

Load-time red errors auto-opened the in-game Debug log window
(`focusedWindowType=EditWindow_Log`) — that is why the menu "looked wrong." Whether
those errors matter is a separate question from this (non-)stall. Not filed unless
the owner wants the load-error census run.

## Cleanup

- `LoadTracer` is enabled in ModsConfig for this investigation
  (`Config/ModsConfig.xml`, backup `.pre_loadtracer`). It is a diagnostic; remove it
  from the mod list before the owner's real play sessions.
- Game is currently at `Playing` on a disposable dev quicktest colony. Quit to menu
  and load the campaign in seconds — no cold load needed.
