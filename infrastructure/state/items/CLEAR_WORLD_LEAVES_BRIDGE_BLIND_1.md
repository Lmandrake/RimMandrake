# CLEAR_WORLD_LEAVES_BRIDGE_BLIND_1 — the teardown that blinds the instrument you would diagnose it with

Row 4 of 5 split out of `BRIDGE_TOOLS_HARD_BLOCK_1`.

## spec
`MemoryUtility.ClearAllMapsAndWorld()`.

## 🔴 Why this is not merely destructive
It leaves the process with **null fields until a new `Game` is installed**, and in that window
**every other bridge tool throws — including the one you would use to find out what happened.**
That is not a bad outcome, it is an *unreportable* one, and it is the exact shape of
`rimworld-zombie-game-state`: a seat cannot tell a wedged bridge from a dead game.

⇒ **A tool that can wedge the bridge is worse than no tool**, because the next seat's first move
is to distrust the bridge rather than the call.

## The only acceptable design
🔑 **It installs a new `Game` in the SAME call, or it refuses.** There is no third option and no
`force` flag that makes one — an argument that leaves the process bare is a footgun with a
label on it, not a safety.

- `confirmDestructive: true` required, like `jawa/pawn_health restore`.
- The result must be read back through a tool that only works when a Game exists, so a success
  that did not restore the process cannot report success.

## verify
Build clean; then on a SCRATCH session only: call it, and immediately afterwards
`jawa/map_info` or `rimworld/get_game_info` must answer normally. A throw there is a FAIL,
not a caveat.

## criteria
- [ ] Never leaves the process without a Game.
- [ ] `confirmDestructive` required.
- [ ] Proven by a call that succeeds *and* by a following read that works.
