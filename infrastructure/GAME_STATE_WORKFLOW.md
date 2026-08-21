# GAME STATE WORKFLOW

**Permanent doctrine. Every seat obeys this every session.**
Not a TRANSIENT file — this is the deployment cycle itself.

Authority: the owner's specification, 2026-08-20. Where this file and a seat file disagree about
the cycle, **this file wins**; fix the seat file in the same commit.

---

## 0. The two things that are always true

1. 🔴 **The OWNER announces every game-state change.** No agent infers one, and no agent announces
   one. An agent reads state with `rimflow game`; it never sets it.
2. 🔴 **ONLY CHECK EVER TAKES THE BRIDGE.** No other seat, no exception, no "just one call".
   CHECK announces possession and release; nobody else touches it.

---

## 1. The states

```
   DOWN ──"game load announced"──▶ DEPLOYING ──"game is loading"──▶ LOADING
     ▲                                                                 │
     │                                                          "game is up"
     │                                                                 ▼
     └──"game is closed"── GOING_DOWN ◀──"game is going down"──────── UP
```

| state | set by | meaning |
|---|---|---|
| `DOWN` | owner | no game running. Assemblies are unlocked and deployable |
| `DEPLOYING` | owner | a load is coming. Get content onto disk |
| `LOADING` | owner | the game is starting. Nothing to do but offline work |
| `UP` | owner | main menu reached. Fresh dumps and a fresh log exist |
| `GOING_DOWN` | owner | the window is closing. Live work only |

---

## 2. What each state means for each seat

### `DOWN` → `DEPLOYING` — "game load is announced"

| seat | does |
|---|---|
| **BUILD** | deploys **primary content** to `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`. ⚠️ Assemblies deploy **only now** — the OS locks them while the game runs. Then `rimflow seat ready` |
| **CHECK** | deploys **bridge content** (companion DLL, JawaBench), **checks the mod list**, then `rimflow seat ready` |
| **DECIDE** | ⭐ **unaffected. Keeps working.** Scope and specs need no game |
| **REP** | shows the readiness gate on the board |

🔑 **Readiness is the gate.** `rimflow seat ready` from BUILD **and** CHECK is what tells the owner
the load may begin. A seat that is ready goes idle — that idleness *is* the signal.

### `LOADING` — "game is beginning to load"

**Everyone continues offline work**, for this test or a future one. Nothing blocks on a loading game.
`needs: game-up` and `needs: bridge` items are simply not offered by `rimflow next`.

### `UP` — "game is up at Main Menu"

This is the valuable window. It opens with **free evidence**:

1. **Fresh dumps and a fresh log exist immediately.** Harvest before anything else.
2. **The log may start a flurry** in BUILD and CHECK — red errors to chase, or confirmations that
   close V&V targets outright. Both are `needs: harvest` work and both rank high.
3. **CHECK processes the fresh files first.** Only then:

```
CHECK announces:  "CHECK has the Bridge"        →  rimflow bridge take
CHECK runs the live testing scheduled for this deployment
CHECK announces:  "CHECK has released the Bridge"  →  rimflow bridge release
CHECK goes idle
```

**While CHECK holds the bridge it may discover three kinds of new work**, and each has a route:

| discovery | command | worked when |
|---|---|---|
| a failure that **one more check would clarify** | `spawn --for CHECK --needs bridge --this-deployment` | ⭐ **now, this deployment** |
| a change **BUILD** must make | `spawn --for BUILD --needs offline` | immediately, in parallel |
| a **design** problem | `spawn --for DECIDE --kind decision` | whenever DECIDE reaches it |

⛔ **A failed check never sends an item back to BUILD.** It records the failing run, files a finding,
and spawns new work. The failure stands as evidence forever.

### `GOING_DOWN` — "game is going down"

| seat | does |
|---|---|
| **CHECK** | 🔴 **live items ONLY.** Offline work that can be postponed **is** postponed. When the live list is clear: announce **"Close the Game"**, then switch back to offline work |
| **BUILD** · **DECIDE** | unaffected — offline work continues |

`--this-deployment` flags are cleared on entering `DOWN`, so nothing leaks into the next window as
false urgency.

### `DOWN` — "game is closed"

**Everyone returns to 100% offline work**, and one class ranks above the rest:

⭐ **Finish mining the corpse.** The dumps, logs and artifacts from the load just ended are about to
be overwritten by the next one. Anything `needs: harvest` outranks ordinary offline work until it is
done or the next `DEPLOYING` begins.

Assemblies are unlocked again — this is the only window in which a companion DLL can be replaced.

---

## 3. Dumps: which one is canon

🔴 **The OFFICIAL dump is frozen, and it is the design target.** Ruled by the owner, 2026-08-20.

| kind | modlist | frozen | used for |
|---|---|---|---|
| `official` | the full **578** list | ✅ yes | ⭐ **designing and building against.** DECIDE and BUILD author to this |
| `verification` | whatever was live | ❌ no | answering *"does the running game match?"* — never *"what should I design against?"* |

🔴 **A differing mod count does NOT invalidate the frozen dump — greater or lesser.** Our own custom
mods will change the count constantly and make exceptionally small changes to the def set. That is
expected and is **not** staleness.

**Only the owner re-freezes**, deliberately. `refresh.py` reports a frozen dump as
`FROZEN (by owner, <date>)`, never `STALE`.

Registry: `infrastructure/state/dumps/REGISTRY.jsonl`.

---

## 4. When an agent stops

An agent keeps clearing items for the current deployment until **exactly one** of these is true:

| # | condition | action |
|---|---|---|
| 1 | **No ready work** | `rimflow seat idle --reason no-ready-work` |
| 2 | **Needs the owner, and he is present** | file the question, work something else; idle only if it was the last item |
| 3 | **Needs the owner, and `MODE` is `afk`** | ⭐ **file the question and keep going.** Never idle for an absent owner |
| 4 | **Context ≥ 90%** | the ritual below |
| 5 | **Waiting on a game state** | `rimflow seat idle --reason awaiting-game-state` |

### The 90% ritual

1. **Write down what was learned** — `BUILDABLE.md` (a stack limit) · `observed/LIVE.md` (a live
   fact) · the relevant **skill** (a durable technique).
2. **Close or block the item in hand.** Never leave it `doing`.
3. **Commit and push.**
4. `rimflow seat idle --reason context-exhausted --note "<where I stopped>"`

🔑 **That note is the handoff.** The next seat reads it out of `rimflow next` and resumes cold.

---

## 5. The owner's phrases, and what each one triggers

| the owner says | state | first thing that happens |
|---|---|---|
| *"Game load is announced"* | `DEPLOYING` | BUILD and CHECK deploy; DECIDE ignores it |
| *"Game is loading"* | `LOADING` | everyone to offline work |
| *"Game is up"* | `UP` | harvest dumps and log **before** anything else |
| *"Game is going down"* | `GOING_DOWN` | CHECK drops offline work, closes live items |
| *"Game is closed"* | `DOWN` | harvest work outranks everything until exhausted |
| *"WRAP is initiated"* | — | finish, commit, push, hand off |

⚠️ These reach every window through `broadcast.py`, which is **the owner's tool only.** An agent
running it is breaking the no-peer-messaging ruling by the back door.

---

## 6. Why a load is expensive, and what that buys

| | |
|---|---|
| full 578-mod list | **~25 minutes** |
| minimal 13-mod list | **~22 seconds** |
| a bridge quicktest map | **~90 seconds** |

⇒ **Arrive already confident.** Write down, before the load, the exact `Player.log` strings that will
decide each open item. A load spent discovering what to look for is a load wasted. Never
"restart and see" — see `skills/rimworld-load-round`.
