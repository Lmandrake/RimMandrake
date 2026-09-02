# GAME STATE WORKFLOW

**Permanent doctrine.** Authority: the owner's specification, 2026-08-20; condensed
2026-08-27 for the two-window fleet (BENCH · FOUNDRY — see
`infrastructure/agents/CHARTER.md`). Where this file and a window file disagree
about the cycle, this file wins; fix the window file in the same commit.

## The two things that are always true

1. 🔴 **The OWNER announces every game-state change — and any window MEASURES it.**
   A window never *infers* a state, but bare `./game` looks and corrects the ledger
   on the spot, from anywhere. Never write a sentence comparing a recorded state to
   a measured one — run the probe and the disagreement is gone.
2. 🔴 **One bridge driver at a time.** `rimflow bridge take` / `release`; release
   the instant you stop driving. **Superseded 2026-09-02 — CLAUDE.md's "The bridge
   is passed through one file" is now canonical**: it errs toward ALLOWING, not
   mutual lockout. A stale (45-minute-idle) hold is simply taken, saying so;
   `take --force` always works and is recorded; `infrastructure/state/BRIDGE` is
   the one-glance mirror; `./bridge bench|foundry|free` is the owner's override.
   Do not message the other window about it — that channel is off.

## The states

```
   DOWN ──"game load announced"──▶ DEPLOYING ──"game is loading"──▶ LOADING
     ▲                                                                 │
     │                                                          "game is up"
     │                                                                 ▼
     └──"game is closed"── GOING_DOWN ◀──"game is going down"──────── UP
```

| state | what FOUNDRY does | what BENCH does |
|---|---|---|
| `DOWN` | assemblies + content deploy (only window a DLL can be replaced); finish mining the last load's corpse — `needs: harvest` outranks ordinary work until the dumps and log are drained | offline work with the owner |
| `DEPLOYING` | deploy the build, then `rimflow seat ready` — that idleness is the owner's go-signal | unaffected |
| `LOADING` | offline work; `needs: game-up`/`bridge` items are simply not offered | unaffected |
| `UP` | **harvest fresh dumps and log before anything else**, then bridge work: take, run the live list, release, idle | the owner plays or drives; "spawn me one and I'll read it back" |
| `GOING_DOWN` | live items ONLY; postponable offline work is postponed; announce "Close the Game" when clear | unaffected |

`--this-deployment` items (`rimflow spawn … --this-deployment`) jump the queue while
the game is UP and are cleared automatically on `DOWN`, so no false urgency leaks
forward.

## 🔴 A REBOOT IS YOURS TO CALL — owner, 2026-09-02

> *"When bridge is available go ahead and reboot. That should just be known at this
> point."*

**A window closes and relaunches the game itself, without asking**, whenever there is
a reason to — a staged assembly deploy, a def/content change, a wedged game. Do not
queue a restart behind him and do not ask permission for one. Announce it in your
reply after the fact, not before it as a request.

The two things that still gate it, and they are the only two:

| gate | why |
|---|---|
| **The bridge must be free** (or yours) | someone else may be mid-drive; `rimflow bridge who`, then take it *for the reboot* so the reason is in the file they read |
| **The window still costs ~25 min** | so spend it — `rimworld-load-round` §2/§3: decision strings and one signature per assembly, written BEFORE the game starts |

⭐ Still run `./game --said "<his verbatim words>"` for each transition, exactly as
below. The authorization changed who may *act*; it did not change how the state is
recorded, and his words remain the provenance on the event.

⛔ **What this does NOT unlock:** killing a game he is actively PLAYING. A debug or
test map is disposable and no warning is owed; his campaign session is not. If you
cannot tell which is loaded, that is the one case worth a one-line question.

## His phrases, and what you run

The instant a game-state sentence arrives in your window, run the whole command —
announce AND stamp, his words carried as provenance:

```
./game --said "game up" up          # down | loading | deploying | going-down
```

`--owner-said` refuses bare assent ("yes", "ok") — a short instruction like
"game up" passes. A ledger stamp alone is superseded: it leaves the other window
deaf. This is the ONLY thing a window may reach `broadcast.py` for. The two states
the machine cannot see — `DEPLOYING` vs `DOWN`, `GOING_DOWN` vs `UP` — are the
owner's alone; the probe never touches them, and an inferred state is refused
(`measured: true` is written by `probe.py` and nowhere else; a host with no
`tasklist.exe` answers UNMEASURED, never "not running").

## Dumps: which one is canon

🔴 **The `official` dump (full 578 list) is FROZEN and is the design target** —
ruled 2026-08-20; only the owner re-freezes, and `refresh.py` reports it
`FROZEN (by owner, <date>)`, never `STALE`. A `verification` dump answers only
"does the running game match?", never "what should I design against?". A differing
mod count does NOT invalidate the frozen dump — our own mods shift it constantly.
⚠️ **Every other dump and harvest decays: treat it as stale until its fingerprint
matches the live mod set, and aggressively question whether it still earns its
disk** (owner, 2026-08-27). Registry: `infrastructure/state/dumps/REGISTRY.jsonl`.

## Why a load is expensive, and what that buys

| | |
|---|---|
| full 578-mod list | **~25 minutes** |
| minimal 13-mod list | **~22 seconds** |
| a bridge quicktest map | **~90 seconds** |

⇒ Arrive already confident: write down, before the load, the exact `Player.log`
strings that will decide each open item. Never "restart and see" —
`skills/rimworld-load-round`.
