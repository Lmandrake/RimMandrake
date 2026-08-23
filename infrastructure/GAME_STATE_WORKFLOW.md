# GAME STATE WORKFLOW

**Permanent doctrine. Every seat obeys this every session.**
Not a TRANSIENT file — this is the deployment cycle itself.

Authority: the owner's specification, 2026-08-20. Where this file and a seat file disagree about
the cycle, **this file wins**; fix the seat file in the same commit.

---

## 0. The two things that are always true

1. 🔴 **The OWNER announces every game-state change — and any seat MEASURES it.** Superseded in
   part 2026-08-22: an agent still never *infers* a state, but it may *look*, and when the
   machine contradicts the record the record is corrected on the spot. See the ruling at the
   foot of this file. `./game` is the whole of it.
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

⚠️ These reach every window through `broadcast.py`, which is **the owner's tool only —
with one carve-out, added 2026-08-22: the seat he says it TO runs `./game --said "<his
words>" <state>` on the spot.** See §7. Anything else an agent sends through it is
breaking the no-peer-messaging ruling by the back door.

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

---

## 🔴 THE MEASUREMENT WINS, SILENTLY — owner, 2026-08-22 12:47

*"I keep seeing things that say 'something says the game is up, but the owner said it was
down' and neither one is actually just checking to see the truth. We need to simplify this
game state business. Any agent is absolutely able to check what it literally is to some
degree. The point of the user saying anything was to authorize people to react to a game
state change, and there should be precisely ONE place that variable is recorded and no more."*

**Any seat may look, any time. One command, and it corrects the record as it reads it:**

```
./game                                              # or: rimflow game
running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
recorded  : UP  → corrected to DOWN, measured now
```

- ⛔ **Never write a sentence comparing a recorded state to a measured one.** There is
  nothing to compare and nothing to escalate — run the probe and the disagreement is gone.
  That prose is the thing this ruling deletes.
- 🔑 **ONE recorded place: the ledger.** `infrastructure/state/ledger/events.jsonl`, one
  `game` event. The board, `queue/*.md` and `board.json` are DERIVED views of it and are
  never edited. A number about game state that came from anywhere else is a copy.
- ✅ **`rimflow next` measures before it offers**, so a seat cannot be handed `needs: game-up`
  work against a stale reading. Cached 20 s.
- 🔑 **What the owner's word is FOR, and it has not shrunk:** authorization to REACT to a
  change, and naming the two states the machine cannot see — `DEPLOYING` is indistinguishable
  from `DOWN` (no process either way) and `GOING_DOWN` from `UP` (process alive either way).
  The probe never overwrites those.
- ⛔ **An INFERRED state is still refused.** `measured: true` is written by `probe.py` and
  nowhere else. Setting it by hand puts a guess in the one place that is supposed to be true.
- ⚠️ **Ignorance is not a reading.** On a host with no `tasklist.exe` the probe answers
  UNMEASURED and changes nothing — it never rounds "I could not look" down to "nothing is
  running". `selftest_probe.py` pins that.

**Announcing to the other windows is still the owner's**, and still `./game up|down|loading`.
That sends the one message that legitimately crosses windows AND stamps the ledger.

### ⭐ AND WHEN HE SAYS IT TO *YOU*, YOU RUN IT — owner, 2026-08-22

*"make it so that when I say game up, game down, game loading it is IDENTICAL to that
!./game command. Fix it for this specific thing."*

🔴 **The instant he types a game-state sentence to your window, run the whole command —
announce AND stamp — with his words carried on it:**

```
./game --said "game up" up          # down | loading | deploying | going-down
```

- ⛔ **A ledger stamp alone is no longer the right answer.** It leaves the other windows
  deaf, which is the exact split this doctrine exists to prevent. Superseded: any earlier
  line telling a seat to run `rimflow game <STATE> --owner-said "…"` on its own.
- ⭐ **`--said` is provenance, not permission** — his verbatim sentence lands on the event.
  ⛔ `--owner-said` refuses bare **assent** (*"yes"*, *"ok"*, *"go ahead"*): that is him
  agreeing to something YOU said. A short **instruction** passes — **"game up" is fine.**
  (The old guard demanded 12 characters and so refused his own phrasing; fixed 2026-08-22
  in `src/RimMandrake/rimflow/cli.py`.)
- ⛔ **This is the ONLY thing a seat may run `broadcast.py` for**, directly or through
  `./game`. Relaying his game-state sentence *in the moment he says it* is not peer
  messaging. A state you INFERRED, or any other message, is — and stays refused.

