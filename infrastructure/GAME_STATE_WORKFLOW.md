# GAME STATE WORKFLOW

**Permanent doctrine.** Authority: the owner's specification of the game-state cycle, 2026-08-20. On 2026-08-27 this
file was condensed for the two-window fleet of that time (BENCH · FOUNDRY). FOUNDRY is retired since then; see
`infrastructure/agents/CHARTER.md`.

- If this file and a window file disagree about the cycle, this file wins.
- Fix the window file in the same commit.

## The three things that are always true

1. 🔴 **The OWNER announces every game-state change — and any window MEASURES it.**
   - A window never *infers* a state.
   - Bare `./game` looks at the game and corrects the ledger at once. Any window can run it.
   - Do not write a sentence that compares a recorded state with a measured state. Run the probe instead. Then the
     disagreement is gone.
2. 🔴 **One bridge driver per game.** There are several live games:
   - ArchBig: Steam's install on Archmagi. ArchBig is the owner's game. Lock `archmagi`.
   - ArchSmall: its own install on Archmagi. Lock `archmagi.b`.
   - Steve1 and Steve2, the SteveDesktop games. Locks `stevedesktop` and `stevedesktop.b`.

   Each game has one bridge holder at a time. Two holders may drive two games at the same time.
   - Take and free a game with `rimflow bridge take` / `release`. For a game other than ArchBig, add
     `--host <lock>`.
   - Release the bridge the instant you stop driving.
   - CLAUDE.md's "The bridge is passed through one file" is canonical for each lock. That rule errs toward ALLOWING,
     not toward mutual lockout.
   - A holder is a process. When the process ends, the game is free at once. A live holder holds.
   - `take --force` cuts a live holder and is recorded. `--force` does not cut his OWNER hold before 45 minutes after his
     last deliberate interaction.
   - `python3 src/RimMandrake/rimflow/game_lock.py query all` is the one-glance answer for every game.
   - `./bridge conductor|free` is the owner's override.
   - A busy game is never a reason to wait. Name the game, and say why no other game can take the work (CLAUDE.md
     "There are several live games").
3. **The states below are ArchBig's.** `./game` announces and measures ArchBig, the game that the owner plays.
   ArchSmall and the other games have no announced state. A seat starts, measures and stops one of those games with
   `python3 src/RimMandrake/Utils/game_instance.py launch|status|stop`.

## The states

```
   DOWN ──"game load announced"──▶ DEPLOYING ──"game is loading"──▶ LOADING
     ▲                                                                 │
     │                                                          "game is up"
     │                                                                 ▼
     └──"game is closed"── GOING_DOWN ◀──"game is going down"──────── UP
```

The bridge holder is a helper or the Conductor. Before the FOUNDRY seat retired, the holder column was FOUNDRY's.

| state | what the bridge holder does | what the Conductor's window (BENCH) does |
|---|---|---|
| `DOWN` | Deploy assemblies and content. `DOWN` is the only state in which a DLL can be replaced. Finish the harvest of the last load: drain its dumps and its log. Until they are drained, `needs: harvest` outranks ordinary work. | offline work with the owner |
| `DEPLOYING` | Deploy the build, then run `rimflow seat ready`. Going idle is the owner's go-signal. | unaffected |
| `LOADING` | Offline work. Items with `needs: game-up`/`bridge` are simply not offered. | unaffected |
| `UP` | **First harvest the fresh dumps and log, before anything else.** Then do bridge work: take the bridge, run the live list, release the bridge, go idle. | The owner plays or drives; "spawn me one and I'll read it back". |
| `GOING_DOWN` | Live items ONLY. Postpone offline work that can wait. Announce "Close the Game" when clear (the list of live items is empty). | unaffected |

`--this-deployment` items (`rimflow spawn … --this-deployment`) jump the queue while the game is UP. Those items are cleared
automatically on `DOWN`. So no false urgency leaks forward.

## 🔴 A REBOOT IS YOURS TO CALL — owner, 2026-09-02

> *"When bridge is available go ahead and reboot. That should just be known at this
> point."*

**A window closes and relaunches the game itself, without asking**, whenever there is a reason to. A reason is a staged
assembly deploy, a def or content change, or a wedged game.

- Do not queue a restart behind the owner.
- Do not ask permission for a restart.
- Announce the restart in your reply after the fact, not before it as a request.

These gates still apply to a reboot:

| gate | why |
|---|---|
| **The bridge must be free** (or yours) | Someone else may be mid-drive. Run `rimflow bridge who`. Then take the bridge *for the reboot*, so the reason is in the file that the others read. |
| **The window still costs ~25 min** | So spend the load well: `rimworld-load-round` §2/§3. Before the game starts, write the decision strings and one signature per assembly. |
| **`preflight_bridge.py` says GREEN** | Before the launch, run `python3 src/RimMandrake/Utils/preflight_bridge.py --tier full --deep`. It checks for a wrong list, a stale deploy, load-killer lint, wedgers and the lease. In the first five minutes after the launch, run it with `--live`. A NO-GO names the check that failed. Detail: `skills/rimbridge/references/preflight.md`. |

Still run `./game --said "<his verbatim words>"` for each transition, exactly as the next section says. The 2026-09-02
ruling changed who may *act*. The ruling did not change how the ledger records the state. The owner's words stay the
provenance on the event.

⛔ **What this does NOT unlock:** killing a game that the owner is actively PLAYING.
- A debug or test map is disposable. You owe no warning for it.
- His campaign session is not disposable.
- If you cannot tell which kind of game runs, ask the owner one line. Only this case of a game kill is worth a question.

## His phrases, and what you run

When a game-state sentence from the owner arrives in your window, run the whole command at once. Carry his words as
provenance:

```
./game --said "game up" up          # down | loading | deploying | going-down
```

- `--owner-said` records a bare assent ("yes", "ok") and prints a note that asks for `--why`. A short instruction like
  "game up" passes.
- 🔴 **An agent's relay stamps the ledger and messages NO window** (owner, 2026-09-29: cross-window game-state
  broadcasts *"burn tokens unnecessarily and rarely inform"*).
  - The other windows learn the state from `rimflow next`. `rimflow next` measures the game itself.
  - Only `broadcast.py` reaches the windows. The owner runs `broadcast.py`, or the Conductor window as its recorded act
    (owner 2026-11-19). No other seat or helper runs it.
- The machine cannot see two differences: `DEPLOYING` vs `DOWN`, and `GOING_DOWN` vs `UP`. Those states are the
  owner's alone.
  - The probe never touches those states.
  - An inferred state is refused. Only `probe.py` writes `measured: true`.
  - A host with no `tasklist.exe` answers UNMEASURED, never "not running".

## Dumps: which one is canon

🔴 **The `official` dump (full 578 list) is FROZEN and is the design target.** The owner ruled this on 2026-08-20.
- Only the owner re-freezes the `official` dump, or the Conductor window as its recorded act
  (`design/RimMandrake/delegation_policy.md` §2).
- `refresh.py` reports the `official` dump as `FROZEN (by owner, <date>)`, never `STALE`.
- A `verification` dump answers only "does the running game match?". It never answers "what should I design
  against?".
- A different mod count does NOT make the frozen dump invalid. Our own mods change the count all the time.

⚠️ **Every other dump and harvest decays.** Treat each one as stale until its fingerprint matches the live mod set.
Aggressively question whether each one still earns its disk space (owner, 2026-08-27). Registry:
`infrastructure/state/dumps/REGISTRY.jsonl`.

## Why a load is expensive, and what that buys

| list | load time |
|---|---|
| full 578-mod list | **~25 minutes** |
| minimal list | **~22 seconds** (the 13-mod list of 2026-08-19; `ModsConfig.MINIMAL.xml` held 27 mods on 2026-11-23, its load time UNMEASURED) |
| a bridge quicktest map | **~90 seconds** |

⇒ Arrive already confident. Before the load, write down the exact `Player.log` strings that will decide each open item.
Never "restart and see" — `skills/rimworld-load-round`.
