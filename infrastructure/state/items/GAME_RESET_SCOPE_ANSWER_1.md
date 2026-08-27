
## spec
🔑 **This needs one sentence, and BUILD is blocked on it rather than guessing.**

`CLEAR_WORLD_LEAVES_BRIDGE_BLIND_1` asks for a bridge tool that tears down maps and world
and **installs a new `Game` in the same call, or refuses** — because the teardown alone
leaves every other bridge tool throwing, including the one you would use to diagnose it.

Installing a new `Game` means calling `WorldGenerator.GenerateWorld`. That is the whole
question.

### The two readings, and they genuinely conflict
| | |
|---|---|
| ⛔ **Out of scope** | Owner, 2026-08-18: *"Do not build, extend or tune anything that produces ALTERNATIVE planets… A knob that can produce a second planet is out of scope even if we only ever turn it once."* Read literally, this forbids it. |
| ✅ **Already sanctioned** | `rimworld/start_debug_game_ready` already generates quicktest worlds, CHECK uses it routinely, and `skills/rimworld-debug-testing` is built around *"starting and destroying throwaway dev quicktest colonies through the bridge"*. On that reading a scratch reset is the same category and nothing new is being authorised. |

### What BUILD proposes, if the answer is yes
🔑 **No seed parameter and no coverage parameter.** The quicktest shape is hard-coded
exactly as `Root_Play.SetupForQuickTestPlay` sets it, so the tool **cannot roll a second
planet even in principle** — there is no knob to turn. It never touches Ash'karr, which is
a hand-authored artifact with no generator behind it.

## criteria
- [ ] One line on `CLEAR_WORLD_LEAVES_BRIDGE_BLIND_1` saying yes or no.
- [ ] If yes, whether the no-knobs constraint above is the right shape.

## Watch out
- ⚠️ **A "no" costs nothing that is currently working.** The tool does not exist and
  nothing depends on it. The cost of a no is that a seat who calls
  `MemoryUtility.ClearAllMapsAndWorld` through some other route still blinds the bridge —
  so a no should probably come with *"and nothing may call it at all"*.
- 🔑 **The scope answer is not the only blocker.** Even with a yes, the tool needs a
  `LongEventHandler` design: doing worldgen inline would block RimWorld's main thread for
  tens of seconds with every bridge call queued behind it, which is the same wedge
  `DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1` measured. ⛔ **So a yes here does not mean "go
  build it today"** — it unblocks the design, and the design work is real.
- ⚠️ This is filed `needs: owner` because the ruling being interpreted is the owner's own
  words. DECIDE may be able to answer it directly if the intent is already settled.
