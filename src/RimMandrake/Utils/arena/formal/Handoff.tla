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
(*   -> verified;  pending -> running on cancel (owner wrote again);       *)
(*   killed -> killed on a failed launch (the next Dispatcher tick         *)
(*   retries; at most MaxLaunchFails failures: liveness is CONDITIONAL on  *)
(*   the relaunch eventually succeeding, a permanent failure being an      *)
(*   owner page per B3.5, outside this model).                             *)
(*                                                                         *)
(* Bugs selects protocol defects. Bugs = {} is the FIXED protocol, which   *)
(* is a PROPOSAL, not the as-built one: it assumes an inbox independent    *)
(* of either session process (the as-built RC delivery into a dead        *)
(* session is UNMEASURED, B4 row 2), hand-back of held candidates before   *)
(* the claim, lock release before the claim, whole-target kill.            *)
(*   "dead_session_drop"  AS DESIGNED: a message goes to whichever session *)
(*        process is alive (the old session's jsonl while it lives; the    *)
(*        new one once it lives, an optimistic assumption that only makes  *)
(*        the bug harder to find); with no live process it is dropped.     *)
(*        THE KNOWN GOODBYE RACE.                                          *)
(*   "mem_queue"   candidates are queued in the live context's memory and  *)
(*        the old context need not hand back what it holds before claim.  *)
(*   "overlap"     the new context starts before the old is dead and may   *)
(*        break the bridge lock while its holder lives.                    *)
(*   "stale_verdict"  a test observation is taken without the game having  *)
(*        the candidate's sha loaded.                                      *)
(*   "cs_while_up" a C# deploy is allowed while the game process lives.    *)
(*   "reload_no_rule" a reload (cold, or a bridge hot reload) needs no     *)
(*        logged rule first.                                               *)
(*   "straggler"   kill leaves a child of the old context alive.           *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS Mode, Msgs, Cands, MaxFix, Bugs

ASSUME Mode \in {"goodbye", "testpilot", "arena"}

MaxLaunchFails == 1
HasGame == Mode \in {"testpilot", "arena"}
IsArena == Mode = "arena"
Ctx == {"old", "new"}
Bug(b) == b \in Bugs

VARIABLES
  \* the handoff
  phase,       \* see header
  ctx,         \* [Ctx -> {"absent","live","closing","dead"}]
  stopFile,    \* the STOP / switch request file
  switched,    \* the `switch` event (timestamp) has been written
  armLive,     \* arm targets active on this lane (arena)
  straggler,   \* a child of the dead old context still runs
  launchFails, \* failed relaunch attempts so far
  \* the owner's messages
  msg,         \* [Msgs -> {"unsent","inOld","inNew","durable","handled","lost"}]
  \* candidates
  cand,        \* [Cands -> {"none","queued","held","observed","resolved","invalid","parked","lost"}]
  where,       \* [Cands -> {"durable","old","new","-"}]: whose memory holds a queued/held candidate
  candSha,     \* [Cands -> sha]: the sha the candidate is being tested at (set when taken)
  \* the game and the bridge
  lock,        \* bridge lock holder tag: "free" | "old" | "new" | "owner"
  drivers,     \* contexts that believe they are driving the game
  game,        \* "up" | "down" | "none" (goodbye mode)
  deployed,    \* deployed sha (a counter)
  loaded,      \* the game's loaded sha
  hotPending,  \* a hot-loadable def change is deployed but not yet reloaded by the bridge
  pendingFix,  \* fix classes ready from subagents: SUBSET {"cs","hot"}
  fixes,       \* fixes made so far (bound)
  crashes,     \* game crashes so far (bound)
  ruleLogged,  \* a reload rule is logged since the last reload
  ownerBack,   \* the owner has returned to Archmagi
  \* history (what the safety properties look at)
  verdicts,    \* recorded verdicts [sha, ld]
  csWhileUp,   \* a C# deploy happened with the game up
  reloadNoRule,\* a reload happened with no logged rule
  lateEmit     \* the old arm emitted an event or push after the switch

HV == <<phase, ctx, stopFile, switched, armLive, straggler, launchFails>>
CV == <<cand, where, candSha>>
GV == <<lock, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack>>
XV == <<verdicts, csWhileUp, reloadNoRule, lateEmit>>
vars == <<HV, msg, CV, GV, XV>>

Alive(c) == ctx[c] \in {"live", "closing"}
Inbox(c) == IF c = "old" THEN {"inOld", "durable"} ELSE {"inNew", "durable"}
Holding == {"held", "observed"}
Settled == {"resolved", "invalid", "parked"}
Drives(c) == c \in drivers /\ lock = c /\ Alive(c)

Init ==
  /\ phase = "running"
  /\ ctx = [c \in Ctx |-> IF c = "old" THEN "live" ELSE "absent"]
  /\ stopFile = FALSE /\ switched = FALSE /\ straggler = FALSE /\ launchFails = 0
  /\ armLive = IF IsArena THEN {"old"} ELSE {}
  /\ msg = [m \in Msgs |-> "unsent"]
  /\ cand = [k \in Cands |-> "none"] /\ where = [k \in Cands |-> "-"]
  /\ candSha = [k \in Cands |-> 0]
  /\ lock = IF HasGame THEN "old" ELSE "free"
  /\ drivers = IF HasGame THEN {"old"} ELSE {}
  /\ game = IF HasGame THEN "up" ELSE "none"
  /\ deployed = 0 /\ loaded = 0 /\ hotPending = FALSE
  /\ pendingFix = {} /\ fixes = 0 /\ crashes = 0
  /\ ruleLogged = FALSE /\ ownerBack = FALSE
  /\ verdicts = {} /\ csWhileUp = FALSE /\ reloadNoRule = FALSE /\ lateEmit = FALSE

(* ------------------------------------------------------------ environment *)

\* The owner writes. Fixed: a durable inbox. As designed: the live session process, else nowhere.
Send(m) ==
  /\ msg[m] = "unsent"
  /\ msg' = [msg EXCEPT ![m] =
        IF ~Bug("dead_session_drop") THEN "durable"
        ELSE IF Alive("old") THEN "inOld"
        ELSE IF ctx["new"] = "live" THEN "inNew"
        ELSE "lost"]
  /\ UNCHANGED <<HV, CV, GV, XV>>

\* A candidate arrives. Fixed: the durable queue. Bug: the live context's memory, else nowhere.
Arrive(k) ==
  /\ HasGame /\ cand[k] = "none"
  /\ LET w == IF ~Bug("mem_queue") THEN "durable"
              ELSE IF Alive("old") THEN "old"
              ELSE IF ctx["new"] = "live" THEN "new" ELSE "-"
     IN /\ cand' = [cand EXCEPT ![k] = IF w = "-" THEN "lost" ELSE "queued"]
        /\ where' = [where EXCEPT ![k] = w]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

FixReady(f) ==
  /\ HasGame /\ fixes < MaxFix /\ f \notin pendingFix
  /\ pendingFix' = pendingFix \cup {f} /\ fixes' = fixes + 1
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, game, deployed, loaded, hotPending, crashes, ruleLogged, ownerBack, XV>>

Crash ==
  /\ HasGame /\ game = "up" /\ crashes < 1
  /\ game' = "down" /\ crashes' = crashes + 1 /\ hotPending' = FALSE
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, deployed, loaded, pendingFix, fixes, ruleLogged, ownerBack, XV>>

\* The owner comes back to Archmagi. The agents notice later (Yield); he takes the game once it is free (OwnerTake).
OwnerReturn ==
  /\ HasGame /\ ~ownerBack
  /\ ownerBack' = TRUE
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes,
                 ruleLogged, XV>>

OwnerTake ==
  /\ ownerBack /\ lock = "free" /\ drivers = {}
  /\ lock' = "owner"
  /\ UNCHANGED <<HV, msg, CV, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged,
                 ownerBack, XV>>

\* The old arm (or a straggler of it) writes an event or pushes. Only the late case changes state.
OldEmit ==
  /\ Alive("old") \/ straggler
  /\ switched /\ ~lateEmit
  /\ lateEmit' = TRUE
  /\ UNCHANGED <<HV, msg, CV, GV, verdicts, csWhileUp, reloadNoRule>>

\* The relaunch fails (no new pid within 90 s); the next tick retries from `killed`.
LaunchFail ==
  /\ phase = "killed" /\ launchFails < MaxLaunchFails
  /\ launchFails' = launchFails + 1
  /\ UNCHANGED <<phase, ctx, stopFile, switched, armLive, straggler, msg, CV, GV, XV>>

(* ------------------------------------------------------------- contexts *)

Handle(c, m) ==
  /\ ctx[c] = "live" /\ msg[m] \in Inbox(c)
  /\ msg' = [msg EXCEPT ![m] = "handled"]
  /\ UNCHANGED <<HV, CV, GV, XV>>

Acquire(c) ==
  /\ HasGame /\ ctx[c] = "live" /\ ~ownerBack /\ c \notin drivers
  /\ \/ lock = "free"
     \/ c = "new" /\ lock = "old" /\ Bug("overlap")          \* breaks a lock whose holder lives
  /\ lock' = c /\ drivers' = drivers \cup {c}
  /\ UNCHANGED <<HV, msg, CV, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged,
                 ownerBack, XV>>

\* A closing context releases the bridge (a live one keeps its lane).
Release(c) ==
  /\ ctx[c] = "closing" /\ lock = c
  /\ lock' = "free" /\ drivers' = drivers \ {c}
  /\ UNCHANGED <<HV, msg, CV, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged,
                 ownerBack, XV>>

\* A driver that has noticed the owner is back stops, parks what it holds and frees the bridge.
Yield(c) ==
  /\ ownerBack /\ Alive(c)
  /\ c \in drivers \/ \E k \in Cands : cand[k] \in Holding /\ where[k] = c   \* a released lane may still hold work
  /\ drivers' = drivers \ {c}
  /\ lock' = IF lock = c THEN "free" ELSE lock
  /\ cand' = [k \in Cands |-> IF cand[k] \in Holding /\ where[k] = c THEN "parked" ELSE cand[k]]
  /\ where' = [k \in Cands |-> IF cand[k] \in Holding /\ where[k] = c THEN "-" ELSE where[k]]
  /\ UNCHANGED <<HV, msg, candSha, game, deployed, loaded, hotPending, pendingFix, fixes, crashes,
                 ruleLogged, ownerBack, XV>>

\* Taking a candidate fixes the sha it is tested at: the one deployed now.
Take(c, k) ==
  /\ ctx[c] = "live" /\ Drives(c)
  /\ cand[k] = "queued" /\ where[k] \in {"durable", c}
  /\ cand' = [cand EXCEPT ![k] = "held"] /\ where' = [where EXCEPT ![k] = c]
  /\ candSha' = [candSha EXCEPT ![k] = deployed]
  /\ UNCHANGED <<HV, msg, GV, XV>>

\* A newer deploy landed after the take: retest at the new sha (never keep testing the old one).
Retarget(c, k) ==
  /\ Alive(c) /\ cand[k] = "held" /\ where[k] = c /\ candSha[k] # deployed
  /\ candSha' = [candSha EXCEPT ![k] = deployed]
  /\ UNCHANGED <<HV, msg, cand, where, GV, XV>>

\* The test runs in the game; the fixed protocol observes only with the candidate's sha loaded (S2).
Observe(c, k) ==
  /\ Drives(c) /\ cand[k] = "held" /\ where[k] = c /\ game = "up"
  /\ (loaded = candSha[k] \/ Bug("stale_verdict"))
  /\ cand' = [cand EXCEPT ![k] = "observed"]
  /\ UNCHANGED <<HV, msg, where, candSha, GV, XV>>

\* Recording is a separate, later step. The verdict carries the sha it was tested at and the sha the game has loaded
\* NOW (section 7: no verdict for X while Y is loaded); the fixed protocol records only when the two still agree.
Record(c, k) ==
  /\ Alive(c) /\ cand[k] = "observed" /\ where[k] = c
  /\ (loaded = candSha[k] \/ Bug("stale_verdict"))
  /\ cand' = [cand EXCEPT ![k] = "resolved"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ verdicts' = verdicts \cup {[sha |-> candSha[k], ld |-> loaded]}
  /\ UNCHANGED <<HV, msg, candSha, GV, csWhileUp, reloadNoRule, lateEmit>>

\* The game reloaded between observation and record: the observation is stale and the candidate is retested.
Redo(c, k) ==
  /\ Alive(c) /\ cand[k] = "observed" /\ where[k] = c /\ loaded # candSha[k]
  /\ cand' = [cand EXCEPT ![k] = "held"]
  /\ UNCHANGED <<HV, msg, where, candSha, GV, XV>>

Invalid(c, k) ==
  /\ Alive(c) /\ cand[k] \in Holding /\ where[k] = c
  /\ cand' = [cand EXCEPT ![k] = "invalid"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

\* With the owner back, queued work is parked rather than waited on forever.
Park(c, k) ==
  /\ ctx[c] = "live" /\ ownerBack /\ cand[k] = "queued" /\ where[k] \in {"durable", c}
  /\ cand' = [cand EXCEPT ![k] = "parked"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

\* A closing context hands what it holds back to the durable queue (an observation not yet recorded is redone).
Requeue(k) ==
  /\ ctx["old"] = "closing" /\ cand[k] \in Holding /\ where[k] = "old" /\ ~Bug("mem_queue")
  /\ cand' = [cand EXCEPT ![k] = "queued"] /\ where' = [where EXCEPT ![k] = "durable"]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

StopGame(c) ==
  /\ Drives(c) /\ game = "up" /\ "cs" \in pendingFix
  /\ game' = "down" /\ hotPending' = FALSE
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, deployed, loaded, pendingFix, fixes, crashes, ruleLogged, ownerBack, XV>>

CsDeploy(c) ==
  /\ Drives(c) /\ "cs" \in pendingFix
  /\ (game = "down" \/ Bug("cs_while_up"))
  /\ deployed' = deployed + 1 /\ pendingFix' = pendingFix \ {"cs"}
  /\ csWhileUp' = (csWhileUp \/ game = "up")
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, game, loaded, hotPending, fixes, crashes, ruleLogged, ownerBack,
                 verdicts, reloadNoRule, lateEmit>>

HotDeploy(c) ==
  /\ Drives(c) /\ "hot" \in pendingFix /\ game = "up"
  /\ deployed' = deployed + 1 /\ pendingFix' = pendingFix \ {"hot"} /\ hotPending' = TRUE
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, game, loaded, fixes, crashes, ruleLogged, ownerBack, XV>>

\* The burden of proof: a rule is logged before any reload, cold or hot.
LogRule(c) ==
  /\ Drives(c) /\ (game = "down" \/ hotPending) /\ ~ruleLogged
  /\ ruleLogged' = TRUE
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes,
                 ownerBack, XV>>

HotReload(c) ==
  /\ Drives(c) /\ game = "up" /\ hotPending
  /\ (ruleLogged \/ Bug("reload_no_rule"))
  /\ loaded' = deployed /\ hotPending' = FALSE /\ ruleLogged' = FALSE
  /\ reloadNoRule' = (reloadNoRule \/ ~ruleLogged)
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, game, deployed, pendingFix, fixes, crashes, ownerBack,
                 verdicts, csWhileUp, lateEmit>>

Reload(c) ==
  /\ Drives(c) /\ game = "down"
  /\ "cs" \notin pendingFix                                 \* a ready C# fix is deployed before the game comes back
  /\ (ruleLogged \/ Bug("reload_no_rule"))
  /\ game' = "up" /\ loaded' = deployed /\ ruleLogged' = FALSE
  /\ reloadNoRule' = (reloadNoRule \/ ~ruleLogged)
  /\ UNCHANGED <<HV, msg, CV, lock, drivers, deployed, hotPending, pendingFix, fixes, crashes, ownerBack,
                 verdicts, csWhileUp, lateEmit>>

(* ------------------------------------------------------------- the handoff *)

\* Close-out done, GOODBYE / STOP written. The old context stops taking work. It begins only with its inbox
\* answered: the goodbye is itself his last message, and a goodbye is never read while an earlier one waits.
Begin ==
  /\ phase = "running" /\ ctx["old"] = "live"
  /\ ~\E m \in Msgs : msg[m] \in Inbox("old")
  /\ phase' = "pending" /\ ctx' = [ctx EXCEPT !["old"] = "closing"] /\ stopFile' = TRUE
  /\ UNCHANGED <<switched, armLive, straggler, launchFails, msg, CV, GV, XV>>

\* He wrote again before the claim: the old context goes back to work (B3.1).
Cancel ==
  /\ phase = "pending" /\ \E m \in Msgs : msg[m] \in Inbox("old")
  /\ phase' = "running" /\ ctx' = [ctx EXCEPT !["old"] = "live"] /\ stopFile' = FALSE
  /\ UNCHANGED <<switched, armLive, straggler, launchFails, msg, CV, GV, XV>>

\* The re-check immediately before the kill (B3.3): no unanswered message, the old context's hands empty.
Claim ==
  /\ phase = "pending"
  /\ ~\E m \in Msgs : msg[m] \in Inbox("old")
  /\ (lock # "old" \/ Bug("overlap"))
  /\ (~\E k \in Cands : cand[k] \in Holding /\ where[k] = "old") \/ Bug("mem_queue")
  /\ phase' = "claimed"
  /\ UNCHANGED <<ctx, stopFile, switched, armLive, straggler, launchFails, msg, CV, GV, XV>>

\* SIGTERM/SIGKILL of the old context (its whole target in arena). Its memory is gone.
Kill ==
  /\ phase \in {"claimed", "relaunched"} /\ Alive("old")
  /\ phase = "claimed" \/ Bug("overlap")
  /\ ctx' = [ctx EXCEPT !["old"] = "dead"]
  /\ phase' = IF phase = "claimed" THEN "killed" ELSE phase
  /\ cand' = [k \in Cands |-> IF where[k] = "old" /\ cand[k] \in {"queued"} \cup Holding THEN "lost" ELSE cand[k]]
  /\ where' = [k \in Cands |-> IF where[k] = "old" THEN "-" ELSE where[k]]
  /\ lock' = IF lock = "old" THEN "free" ELSE lock                \* the EXIT trap releases the bridge
  /\ drivers' = drivers \ {"old"}
  /\ armLive' = armLive \ {"old"}
  /\ straggler' = Bug("straggler")
  /\ UNCHANGED <<stopFile, switched, launchFails, msg, candSha, game, deployed, loaded, hotPending,
                 pendingFix, fixes, crashes, ruleLogged, ownerBack, XV>>

\* Switch event, new target / window starts and reads what the old session holds (B1).
Relaunch ==
  /\ phase = "killed" \/ (phase = "claimed" /\ Bug("overlap"))
  /\ ctx["new"] = "absent"
  /\ phase' = "relaunched" /\ ctx' = [ctx EXCEPT !["new"] = "live"]
  /\ switched' = TRUE
  /\ armLive' = IF IsArena THEN armLive \cup {"new"} ELSE armLive
  /\ msg' = [m \in Msgs |-> IF msg[m] = "inOld" THEN "inNew" ELSE msg[m]]
  /\ UNCHANGED <<stopFile, straggler, launchFails, CV, GV, XV>>

Verify ==
  /\ phase = "relaunched" /\ ctx["new"] = "live" /\ ~Alive("old")
  /\ phase' = "verified" /\ stopFile' = FALSE
  /\ UNCHANGED <<ctx, switched, armLive, straggler, launchFails, msg, CV, GV, XV>>

Env ==
  \/ \E m \in Msgs : Send(m)
  \/ \E k \in Cands : Arrive(k)
  \/ \E f \in {"cs", "hot"} : FixReady(f)
  \/ Crash \/ OwnerReturn \/ OwnerTake \/ OldEmit \/ LaunchFail \/ Begin

\* The protocol's obligations. StopGame, HotDeploy and Invalid are choices, not obligations: no fairness.
Progress(c) ==
  \/ \E m \in Msgs : Handle(c, m)
  \/ Acquire(c) \/ Release(c) \/ Yield(c)
  \/ \E k \in Cands : Take(c, k) \/ Retarget(c, k) \/ Observe(c, k) \/ Record(c, k) \/ Redo(c, k)
     \/ Park(c, k)
  \/ CsDeploy(c) \/ HotReload(c) \/ LogRule(c) \/ Reload(c)

Handoff == Cancel \/ Claim \/ Kill \/ Relaunch \/ Verify \/ \E k \in Cands : Requeue(k)

Next == Env \/ Handoff \/ \E c \in Ctx : Progress(c) \/ StopGame(c) \/ HotDeploy(c) \/ \E k \in Cands : Invalid(c, k)

\* Weak fairness on the protocol only; none on the environment (he may never write, nothing may crash). One WF per
\* context over the disjunction of its obligations: each obligation can fire only finitely often between
\* environment steps, so the disjunction cannot be satisfied forever by a loop that starves one of them.
Fairness == WF_vars(Handoff) /\ WF_vars(Progress("old")) /\ WF_vars(Progress("new"))

Spec == Init /\ [][Next]_vars /\ Fairness

(* ------------------------------------------------------------- properties *)

TypeOK ==
  /\ phase \in {"running", "pending", "claimed", "killed", "relaunched", "verified"}
  /\ ctx \in [Ctx -> {"absent", "live", "closing", "dead"}]
  /\ msg \in [Msgs -> {"unsent", "inOld", "inNew", "durable", "handled", "lost"}]
  /\ cand \in [Cands -> {"none", "queued", "held", "observed", "resolved", "invalid", "parked", "lost"}]
  /\ lock \in {"free", "old", "new", "owner"} /\ drivers \subseteq Ctx /\ armLive \subseteq Ctx

\* S1: at most one live driver per game (the owner counts), at most one live arm target per lane.
S1 == /\ Cardinality(drivers \cup (IF lock = "owner" THEN {"owner"} ELSE {})) <= 1
      /\ Cardinality(armLive) <= 1
\* S2: no verdict for sha X while the game had sha Y loaded.
S2 == \A v \in verdicts : v.sha = v.ld
\* S3: no C# deploy while the game process lives.
S3 == ~csWhileUp
\* S4: every reload, cold or hot, is preceded by a logged rule.
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
