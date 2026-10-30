------------------------------- MODULE Handoff -------------------------------
(***************************************************************************)
(* One parameterised model of handing a live resource from an ending       *)
(* context ("old") to a fresh one ("new") while inputs keep arriving.      *)
(* design/RimMandrake/architecture_switch_harness_2026-10-29.md section 7. *)
(*                                                                         *)
(*   Mode = "goodbye"   the Conductor window restart (conductor_briefing   *)
(*                      2026-10-28 B2-B4): owner messages only, no game.   *)
(*   Mode = "testpilot" a pilot hands the bridge + running game to a fresh *)
(*                      pilot: candidates, fixes, crash, owner return.     *)
(*   Mode = "arena"     `arena switch`: as testpilot, plus the arm         *)
(*                      targets on the lane and the switch timestamp.      *)
(*                                                                         *)
(* The handoff is the GOODBYE state machine generalised:                   *)
(*   running -> pending (close-out written, STOP/switch file) -> claimed   *)
(*   (re-check passed) -> killed -> relaunched (switch event, new wakes)   *)
(*   -> verified;  pending -> running on cancel (owner wrote again).       *)
(*                                                                         *)
(* Bugs selects protocol defects. {} is the FIXED protocol.                *)
(*   "dead_session_drop"  messages go to whichever session process is      *)
(*        alive (as built: RC writes the old session's jsonl); with no     *)
(*        live process the message is dropped. THE KNOWN GOODBYE RACE.     *)
(*        Fixed: every input lands in a durable inbox owned by neither     *)
(*        context; whoever is live consumes it by id.                      *)
(*   "mem_queue"   candidates are queued in the live context's memory and  *)
(*        the old context need not hand back what it holds before claim.  *)
(*   "overlap"     the new context starts before the old is dead and may   *)
(*        break the bridge lock while its holder lives.                    *)
(*   "stale_verdict"  a verdict is recorded without deployed = loaded.     *)
(*   "cs_while_up" a C# deploy is allowed while the game process lives.    *)
(*   "reload_no_rule" a cold reload needs no logged rule first.            *)
(*   "straggler"   kill leaves a child of the old context alive.           *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS Mode, Msgs, Cands, MaxFix, Bugs

ASSUME Mode \in {"goodbye", "testpilot", "arena"}

HasGame == Mode \in {"testpilot", "arena"}
IsArena == Mode = "arena"
Ctx == {"old", "new"}
Bug(b) == b \in Bugs

VARIABLES
  phase,       \* handoff state machine (see header)
  ctx,         \* [Ctx -> {"absent","live","closing","dead"}]
  msg,         \* [Msgs -> {"unsent","inOld","inNew","durable","handled","lost"}]
  cand,        \* [Cands -> {"none","queued","held","resolved","invalid","parked","lost"}]
  where,       \* [Cands -> {"durable","old","new","-"}]: whose memory holds a queued/held candidate
  stopFile,    \* the STOP / switch request file
  switched,    \* the `switch` event (timestamp) has been written
  lock,        \* bridge lock holder tag: "free" | "old" | "new" | "owner"
  drivers,     \* contexts that believe they are driving the game
  armLive,     \* arm targets active on this lane (arena)
  game,        \* "up" | "down" | "none" (goodbye mode)
  deployed,    \* deployed sha (a counter)
  loaded,      \* the game's loaded sha
  hotPending,  \* a hot-loadable def change is deployed but not yet reloaded by the bridge
  pendingFix,  \* fix classes ready from subagents: SUBSET {"cs","hot"}
  fixes,       \* fixes made so far (bound)
  crashes,     \* game crashes so far (bound)
  ruleLogged,  \* a reload rule is logged since the last cold reload
  ownerBack,   \* the owner returned to Archmagi
  straggler,   \* a child of the dead old context still runs
  verdicts,    \* recorded verdicts [sha, loaded]
  csWhileUp,   \* history: a C# deploy happened with the game up
  reloadNoRule,\* history: a cold reload happened with no logged rule
  lateEmit     \* history: the old arm emitted an event or push after the switch

vars == <<phase, ctx, msg, cand, where, stopFile, switched, lock, drivers, armLive, game, deployed, loaded,
          hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, straggler, verdicts, csWhileUp,
          reloadNoRule, lateEmit>>

Alive(c) == ctx[c] \in {"live", "closing"}
Inbox(c) == IF c = "old" THEN {"inOld", "durable"} ELSE {"inNew", "durable"}
Settled == {"resolved", "invalid", "parked"}

Init ==
  /\ phase = "running"
  /\ ctx = [c \in Ctx |-> IF c = "old" THEN "live" ELSE "absent"]
  /\ msg = [m \in Msgs |-> "unsent"]
  /\ cand = [k \in Cands |-> "none"]
  /\ where = [k \in Cands |-> "-"]
  /\ stopFile = FALSE /\ switched = FALSE
  /\ lock = IF HasGame THEN "old" ELSE "free"
  /\ drivers = IF HasGame THEN {"old"} ELSE {}
  /\ armLive = IF IsArena THEN {"old"} ELSE {}
  /\ game = IF HasGame THEN "up" ELSE "none"
  /\ deployed = 0 /\ loaded = 0 /\ hotPending = FALSE
  /\ pendingFix = {} /\ fixes = 0 /\ crashes = 0
  /\ ruleLogged = FALSE /\ ownerBack = FALSE /\ straggler = FALSE
  /\ verdicts = {} /\ csWhileUp = FALSE /\ reloadNoRule = FALSE /\ lateEmit = FALSE

GameVars == <<lock, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged,
              ownerBack, verdicts, csWhileUp, reloadNoRule>>

(* ------------------------------------------------------------ environment *)

\* The owner writes. Fixed: a durable inbox. Bug: the live session process, else nowhere.
Send(m) ==
  /\ msg[m] = "unsent"
  /\ msg' = [msg EXCEPT ![m] =
        IF ~Bug("dead_session_drop") THEN "durable"
        ELSE IF Alive("old") THEN "inOld"
        ELSE IF ctx["new"] = "live" THEN "inNew"
        ELSE "lost"]
  /\ UNCHANGED <<phase, ctx, cand, where, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

\* A candidate arrives. Fixed: the durable queue. Bug: the live context's memory, else nowhere.
Arrive(k) ==
  /\ HasGame /\ cand[k] = "none"
  /\ LET w == IF ~Bug("mem_queue") THEN "durable"
              ELSE IF Alive("old") THEN "old"
              ELSE IF ctx["new"] = "live" THEN "new" ELSE "-"
     IN /\ cand' = [cand EXCEPT ![k] = IF w = "-" THEN "lost" ELSE "queued"]
        /\ where' = [where EXCEPT ![k] = w]
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

FixReady(f) ==
  /\ HasGame /\ fixes < MaxFix /\ f \notin pendingFix
  /\ pendingFix' = pendingFix \cup {f} /\ fixes' = fixes + 1
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 game, deployed, loaded, hotPending, crashes, ruleLogged, ownerBack, verdicts, csWhileUp,
                 reloadNoRule>>

Crash ==
  /\ HasGame /\ game = "up" /\ crashes < 1
  /\ game' = "down" /\ crashes' = crashes + 1 /\ hotPending' = FALSE
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 deployed, loaded, pendingFix, fixes, ruleLogged, ownerBack, verdicts, csWhileUp, reloadNoRule>>

\* The owner comes back to Archmagi: the agents yield the game at once; what they held is parked.
OwnerReturn ==
  /\ HasGame /\ ~ownerBack
  /\ ownerBack' = TRUE /\ lock' = "owner" /\ drivers' = {}
  /\ cand' = [k \in Cands |-> IF cand[k] = "held" THEN "parked" ELSE cand[k]]
  /\ where' = [k \in Cands |-> IF cand[k] = "held" THEN "-" ELSE where[k]]
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, game, deployed, loaded,
                 hotPending, pendingFix, fixes, crashes, ruleLogged, verdicts, csWhileUp, reloadNoRule>>

\* The old arm (or a straggler of it) writes an event or pushes. Only the late case changes state.
OldEmit ==
  /\ Alive("old") \/ straggler
  /\ switched /\ ~lateEmit
  /\ lateEmit' = TRUE
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, GameVars>>

(* ------------------------------------------------------------- contexts *)

Handle(c, m) ==
  /\ ctx[c] = "live" /\ msg[m] \in Inbox(c)
  /\ msg' = [msg EXCEPT ![m] = "handled"]
  /\ UNCHANGED <<phase, ctx, cand, where, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

Acquire(c) ==
  /\ HasGame /\ ctx[c] = "live" /\ ~ownerBack /\ c \notin drivers
  /\ \/ lock = "free"
     \/ c = "new" /\ lock = "old" /\ Bug("overlap")          \* breaks a lock whose holder lives
  /\ lock' = c /\ drivers' = drivers \cup {c}
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, game, deployed,
                 loaded, hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, verdicts, csWhileUp,
                 reloadNoRule>>

\* Only a closing context releases (a live one keeps its lane).
Release(c) ==
  /\ ctx[c] = "closing" /\ lock = c
  /\ lock' = "free" /\ drivers' = drivers \ {c}
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, game, deployed,
                 loaded, hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, verdicts, csWhileUp,
                 reloadNoRule>>

Take(c, k) ==
  /\ ctx[c] = "live" /\ c \in drivers /\ lock = c
  /\ cand[k] = "queued" /\ where[k] \in {"durable", c}
  /\ cand' = [cand EXCEPT ![k] = "held"] /\ where' = [where EXCEPT ![k] = c]
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

\* A verdict: fixed protocol records it only while the game has the deployed sha loaded (S2).
Resolve(c, k) ==
  /\ Alive(c) /\ c \in drivers /\ lock = c /\ cand[k] = "held" /\ where[k] = c
  /\ game = "up" /\ (deployed = loaded \/ Bug("stale_verdict"))
  /\ cand' = [cand EXCEPT ![k] = "resolved"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ verdicts' = verdicts \cup {[sha |-> deployed, ld |-> loaded]}
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, lock, drivers, game, deployed,
                 loaded, hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, csWhileUp, reloadNoRule>>

Invalid(c, k) ==
  /\ Alive(c) /\ cand[k] = "held" /\ where[k] = c
  /\ cand' = [cand EXCEPT ![k] = "invalid"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

\* With the owner back, queued work is parked rather than waited on forever.
Park(c, k) ==
  /\ ctx[c] = "live" /\ ownerBack /\ cand[k] = "queued" /\ where[k] \in {"durable", c}
  /\ cand' = [cand EXCEPT ![k] = "parked"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

\* A closing context hands what it holds back to the durable queue.
Requeue(k) ==
  /\ ctx["old"] = "closing" /\ cand[k] = "held" /\ where[k] = "old" /\ ~Bug("mem_queue")
  /\ cand' = [cand EXCEPT ![k] = "queued"] /\ where' = [where EXCEPT ![k] = "durable"]
  /\ UNCHANGED <<phase, ctx, msg, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

StopGame(c) ==
  /\ c \in drivers /\ lock = c /\ Alive(c) /\ game = "up" /\ "cs" \in pendingFix
  /\ game' = "down" /\ hotPending' = FALSE
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 deployed, loaded, pendingFix, fixes, crashes, ruleLogged, ownerBack, verdicts, csWhileUp,
                 reloadNoRule>>

CsDeploy(c) ==
  /\ c \in drivers /\ lock = c /\ Alive(c) /\ "cs" \in pendingFix
  /\ (game = "down" \/ Bug("cs_while_up"))
  /\ deployed' = deployed + 1 /\ pendingFix' = pendingFix \ {"cs"}
  /\ csWhileUp' = (csWhileUp \/ game = "up")
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 game, loaded, hotPending, fixes, crashes, ruleLogged, ownerBack, verdicts, reloadNoRule>>

HotDeploy(c) ==
  /\ c \in drivers /\ lock = c /\ Alive(c) /\ "hot" \in pendingFix /\ game = "up"
  /\ deployed' = deployed + 1 /\ pendingFix' = pendingFix \ {"hot"} /\ hotPending' = TRUE
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 game, loaded, fixes, crashes, ruleLogged, ownerBack, verdicts, csWhileUp, reloadNoRule>>

HotReload(c) ==
  /\ c \in drivers /\ lock = c /\ Alive(c) /\ game = "up" /\ hotPending
  /\ loaded' = deployed /\ hotPending' = FALSE
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 game, deployed, pendingFix, fixes, crashes, ruleLogged, ownerBack, verdicts, csWhileUp,
                 reloadNoRule>>

LogRule(c) ==
  /\ c \in drivers /\ lock = c /\ Alive(c) /\ game = "down" /\ ~ruleLogged
  /\ ruleLogged' = TRUE
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ownerBack, verdicts, csWhileUp,
                 reloadNoRule>>

Reload(c) ==
  /\ c \in drivers /\ lock = c /\ Alive(c) /\ game = "down"
  /\ "cs" \notin pendingFix                                 \* a ready C# fix is deployed before the game comes back
  /\ (ruleLogged \/ Bug("reload_no_rule"))
  /\ game' = "up" /\ loaded' = deployed /\ ruleLogged' = FALSE
  /\ reloadNoRule' = (reloadNoRule \/ ~ruleLogged)
  /\ UNCHANGED <<phase, ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, lock, drivers,
                 deployed, hotPending, pendingFix, fixes, crashes, ownerBack, verdicts, csWhileUp>>

(* ------------------------------------------------------------- the handoff *)

\* Close-out done, GOODBYE / STOP written. The old context stops taking work. It begins only with its inbox
\* answered: the goodbye is itself his last message, and a goodbye is never read while an earlier one waits.
Begin ==
  /\ phase = "running" /\ ctx["old"] = "live"
  /\ ~\E m \in Msgs : msg[m] \in Inbox("old")
  /\ phase' = "pending" /\ ctx' = [ctx EXCEPT !["old"] = "closing"] /\ stopFile' = TRUE
  /\ UNCHANGED <<msg, cand, where, switched, armLive, straggler, lateEmit, GameVars>>

\* He wrote again before the claim: the old context goes back to work (B3.1).
Cancel ==
  /\ phase = "pending" /\ \E m \in Msgs : msg[m] \in Inbox("old")
  /\ phase' = "running" /\ ctx' = [ctx EXCEPT !["old"] = "live"] /\ stopFile' = FALSE
  /\ UNCHANGED <<msg, cand, where, switched, armLive, straggler, lateEmit, lock, drivers, game, deployed, loaded,
                 hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, verdicts, csWhileUp, reloadNoRule>>

\* The re-check immediately before the kill (B3.3): no unanswered message, the old context's hands empty.
Claim ==
  /\ phase = "pending"
  /\ ~\E m \in Msgs : msg[m] \in Inbox("old")
  /\ (lock # "old" \/ Bug("overlap"))
  /\ (~\E k \in Cands : cand[k] = "held" /\ where[k] = "old") \/ Bug("mem_queue")
  /\ phase' = "claimed"
  /\ UNCHANGED <<ctx, msg, cand, where, stopFile, switched, armLive, straggler, lateEmit, GameVars>>

\* SIGTERM/SIGKILL of the old context (its whole target in arena). Its memory is gone.
Kill ==
  /\ phase \in {"claimed", "relaunched"} /\ Alive("old")
  /\ phase = "claimed" \/ Bug("overlap")
  /\ ctx' = [ctx EXCEPT !["old"] = "dead"]
  /\ phase' = IF phase = "claimed" THEN "killed" ELSE phase
  /\ cand' = [k \in Cands |-> IF where[k] = "old" /\ cand[k] \in {"queued", "held"} THEN "lost" ELSE cand[k]]
  /\ where' = [k \in Cands |-> IF where[k] = "old" THEN "-" ELSE where[k]]
  /\ lock' = IF lock = "old" THEN "free" ELSE lock                \* the EXIT trap releases the bridge
  /\ drivers' = drivers \ {"old"}
  /\ armLive' = armLive \ {"old"}
  /\ straggler' = Bug("straggler")
  /\ UNCHANGED <<msg, stopFile, switched, lateEmit, game, deployed, loaded, hotPending, pendingFix, fixes, crashes,
                 ruleLogged, ownerBack, verdicts, csWhileUp, reloadNoRule>>

\* Switch event, new target / window starts and reads what the old session holds (B1).
Relaunch ==
  /\ phase = "killed" \/ (phase = "claimed" /\ Bug("overlap"))
  /\ ctx["new"] = "absent"
  /\ phase' = "relaunched" /\ ctx' = [ctx EXCEPT !["new"] = "live"]
  /\ switched' = TRUE
  /\ armLive' = IF IsArena THEN armLive \cup {"new"} ELSE armLive
  /\ msg' = [m \in Msgs |-> IF msg[m] = "inOld" THEN "inNew" ELSE msg[m]]
  /\ UNCHANGED <<cand, where, stopFile, straggler, lateEmit, GameVars>>

Verify ==
  /\ phase = "relaunched" /\ ctx["new"] = "live" /\ ~Alive("old")
  /\ phase' = "verified" /\ stopFile' = FALSE
  /\ UNCHANGED <<ctx, msg, cand, where, switched, armLive, straggler, lateEmit, GameVars>>

Env ==
  \/ \E m \in Msgs : Send(m)
  \/ \E k \in Cands : Arrive(k)
  \/ \E f \in {"cs", "hot"} : FixReady(f)
  \/ Crash \/ OwnerReturn \/ OldEmit \/ Begin

Proto(c) ==
  \/ \E m \in Msgs : Handle(c, m)
  \/ Acquire(c) \/ Release(c)
  \/ \E k \in Cands : Take(c, k) \/ Resolve(c, k) \/ Invalid(c, k) \/ Park(c, k)
  \/ StopGame(c) \/ CsDeploy(c) \/ HotDeploy(c) \/ HotReload(c) \/ LogRule(c) \/ Reload(c)

Handoff == Cancel \/ Claim \/ Kill \/ Relaunch \/ Verify \/ \E k \in Cands : Requeue(k)

Next == Env \/ Handoff \/ \E c \in Ctx : Proto(c)

\* Weak fairness on everything the protocol does; none on the environment (he may never write, nothing may crash).
\* One WF per context over the disjunction of its progress steps (each step is finite in number between environment
\* steps, so the disjunction cannot be starved by a loop of other fair steps); StopGame, HotDeploy and Invalid are
\* choices, not obligations, and carry no fairness.
Progress(c) ==
  \/ \E m \in Msgs : Handle(c, m)
  \/ Acquire(c) \/ Release(c)
  \/ \E k \in Cands : Take(c, k) \/ Resolve(c, k) \/ Park(c, k)
  \/ CsDeploy(c) \/ HotReload(c) \/ LogRule(c) \/ Reload(c)

Fairness == WF_vars(Handoff) /\ WF_vars(Progress("old")) /\ WF_vars(Progress("new"))

Spec == Init /\ [][Next]_vars /\ Fairness

(* ------------------------------------------------------------- properties *)

TypeOK ==
  /\ phase \in {"running", "pending", "claimed", "killed", "relaunched", "verified"}
  /\ ctx \in [Ctx -> {"absent", "live", "closing", "dead"}]
  /\ msg \in [Msgs -> {"unsent", "inOld", "inNew", "durable", "handled", "lost"}]
  /\ cand \in [Cands -> {"none", "queued", "held", "resolved", "invalid", "parked", "lost"}]
  /\ lock \in {"free", "old", "new", "owner"} /\ drivers \subseteq Ctx /\ armLive \subseteq Ctx

\* S1: at most one live driver per game (the owner counts), at most one live arm target per lane.
S1 == /\ Cardinality(drivers \cup (IF lock = "owner" THEN {"owner"} ELSE {})) <= 1
      /\ Cardinality(armLive) <= 1
\* S2: no verdict for sha X while the game has sha Y loaded.
S2 == \A v \in verdicts : v.sha = v.ld
\* S3: no C# deploy while the game process lives.
S3 == ~csWhileUp
\* S4: every cold reload is preceded by a logged rule.
S4 == ~reloadNoRule
\* S5: no owner message and no queued candidate is lost across a handoff.
S5 == /\ \A m \in Msgs : msg[m] # "lost"
      /\ \A k \in Cands : cand[k] # "lost"
\* S6: no event and no push from the old arm after its switch timestamp.
S6 == ~lateEmit

\* L1: every candidate that arrives is eventually resolved, marked invalid or parked.
L1 == \A k \in Cands : (cand[k] # "none") ~> (cand[k] \in Settled)
\* L2 (not in section 7, added): every owner message sent is eventually handled by the old or the new context.
L2 == \A m \in Msgs : (msg[m] # "unsent") ~> (msg[m] = "handled")
=============================================================================
