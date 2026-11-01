------------------------------- MODULE Handoff -------------------------------
(***************************************************************************)
(* The one model of handing a live resource from an ending context ("old") *)
(* to a fresh one ("new") while inputs keep arriving.                      *)
(* design/RimMandrake/architecture_switch_harness_2026-10-29.md section 7. *)
(* run_tlc.py checks it; LiveHandoff.tla (its older twin) was deleted by   *)
(* ARENA_HANDOFF_RECONCILE_MODEL_WITH_CODE, its deaths and mutants ported. *)
(*                                                                         *)
(*   Mode = "goodbye"   the Conductor window restart: owner messages only, *)
(*        no game.  Code: src/RimMandrake/rimflow/seat_restart.py execute  *)
(*        (recheck_at_kill, _kill_record, final_fence, kill_pid), the wake *)
(*        reading the transcript from the killed record's cursor.          *)
(*   Mode = "testpilot" a pilot hands the bridge + running game to a fresh *)
(*        pilot (src/RimMandrake/Utils/arena/testpilot.py: handoff only at *)
(*        a test boundary; an in_flight test of a dead pilot is recovered  *)
(*        by the next one, requeued, never lost).                          *)
(*   Mode = "arena"     `arena switch` (src/RimMandrake/Utils/arena/       *)
(*        arena.py _switch_locked): STOP, idle wait, and after IDLE_WAIT_S *)
(*        a FORCED stop with the bridge held and a candidate in flight;    *)
(*        the stopped arm's bridge is released AFTER the stop, then the    *)
(*        switch event, then the new target.  Arena arms are headless:     *)
(*        run_tlc.py gives arena rows no owner messages.                   *)
(*                                                                         *)
(* The handoff (the GOODBYE state machine generalised):                    *)
(*   running -> pending (Begin: close-out done, request / STOP written)    *)
(*   pending -> running (Cancel: he wrote again, B3.1)                     *)
(*   pending -> claimed (Claim: the re-check passed; arena: or ForceClaim) *)
(*   claimed -> pending (Abort: recheck_at_kill / final fence hold)        *)
(*   claimed -> killing (Term: SIGTERM, after the fence)                   *)
(*   killing -> killed  (Reap: exit, or SIGKILL after the grace window)    *)
(*   killing -> running (Survive: kill_pid "survived": never relaunch)     *)
(*   killed  -> killed  (LaunchFail, at most MaxLaunchFails)               *)
(*   killed  -> relaunched (Relaunch: wake reads the old transcript)       *)
(*   relaunched -> verified -> running (Rotate: the new context is the old *)
(*   one of the next handoff; MaxHandoffs handoffs per behaviour)          *)
(*                                                                         *)
(* An owner message in the old window (the old transcript):                *)
(*   inOld --Read--> takenOld --Persist--> readOld --Answer--> handled     *)
(* takenOld is "dequeued, its attachment not yet on disk": only with the   *)
(* hazard "dequeue_gap" (the order Claude Code persists a dequeue and its  *)
(* attachment is UNMEASURED, so the fixed rows assume the worst).  A       *)
(* window keeps reading after its goodbye (it does not know it closes).    *)
(* The wake replays inOld and readOld (after the cursor, no ended turn);   *)
(* a takenOld message dies with the process.  That is what the re-check    *)
(* (Claim, Abort, the fence in Term) is for: the "no_recheck" mutant must  *)
(* break S5.                                                               *)
(*                                                                         *)
(* Bugs = {} is the fixed protocol.  Each member puts back one defect:     *)
(*   "dead_session_drop"  a message with no live window is dropped: THE    *)
(*        KNOWN GOODBYE RACE (else his phone holds it: "durable").         *)
(*   "no_recheck"   Claim, Abort and the final fence ignore his inbox.     *)
(*   "no_claim_recheck" only Claim ignores it (Abort and the fence remain:  *)
(*        expected to PASS, the later checks cover it).                    *)
(*   "no_fence"     only the final fence before SIGTERM ignores it.        *)
(*   "wake_skips_old"  the wake does not read the old transcript.          *)
(*   "closeout_skips_queue"  Begin with messages unanswered: they sit      *)
(*        before the cursor (preOld), where the wake does not read.        *)
(*   "mem_queue"   candidates live in the context's memory; nothing hands  *)
(*        back or recovers them.                                           *)
(*   "overlap"     the new context starts before the old is dead and may   *)
(*        break the bridge lock while its holder lives.                    *)
(*   "relaunch_after_survive"  relaunch although the kill did not take.    *)
(*   "stale_verdict"  observe / record without the candidate's sha loaded. *)
(*   "cs_while_up" a C# deploy while the game process lives.               *)
(*   "reload_no_rule" a reload (cold or hot) with no logged rule first.    *)
(*   "straggler"   the kill leaves a child of the old context alive.       *)
(*   "no_adopt"    a window that died alone mid-handoff is not adopted     *)
(*        (restart_orphan): nobody relaunches.                             *)
(*   "wake_once"   a fresh window that dies after its wake read is         *)
(*        replaced by one that replays nothing.                            *)
(* Hazards: environment behaviour that is UNMEASURED, not a protocol bug:  *)
(*   "dequeue_gap" see above (ON in the fixed rows).                       *)
(*   "term_drop"   a message Remote Control hands a SIGTERMed process is   *)
(*        never written to its transcript.  S5 rests on this NOT holding:  *)
(*        its row must break S5 (assumption A1 of the old model).          *)
(* Deaths (environment, never fair, at most one per behaviour):            *)
(*   "old_alone"  the old window dies by itself mid-handoff; the next tick *)
(*        adopts it.  A death before the request is outside the model.     *)
(*   "dispatcher" the Dispatcher dies after claiming; state.json from      *)
(*        before the tick says pending and it judges again.                *)
(*   "wake"       the fresh window dies after its wake read; the next one  *)
(*        reads the wake again until a window has answered it.             *)
(* Liveness is CONDITIONAL on the relaunch eventually succeeding (a        *)
(* permanent failure is an owner page per B3.5, outside this model).       *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS Mode, Msgs, Cands, MaxFix, MaxHandoffs, Bugs, Hazards, Deaths

ASSUME Mode \in {"goodbye", "testpilot", "arena"}
ASSUME Hazards \subseteq {"dequeue_gap", "term_drop"}
ASSUME Deaths \subseteq {"old_alone", "dispatcher", "wake"}

MaxLaunchFails == 1
HasGame == Mode \in {"testpilot", "arena"}
IsArena == Mode = "arena"
Ctx == {"old", "new"}
Bug(b) == b \in Bugs
Hz(h) == h \in Hazards

VARIABLES
  \* the handoff
  phase,       \* see header
  ctx,         \* [Ctx -> {"absent","live","closing","dying","dead"}]
  stopFile,    \* the STOP / switch request file
  switched,    \* the `switch` event (timestamp) has been written
  armLive,     \* arm targets active on this lane (arena)
  straggler,   \* a child of the dead old context still runs
  launchFails, \* failed relaunch attempts in this handoff
  handoffs,    \* handoffs completed (Rotate)
  deaths,      \* process deaths so far (at most one)
  \* the owner's messages
  msg,         \* [Msgs -> MsgStates]
  \* candidates
  cand,        \* [Cands -> {"none","queued","held","observed","resolved","invalid","parked","lost"}]
  where,       \* [Cands -> {"durable","old","new","-"}]: who holds a queued/held candidate
  candSha,     \* [Cands -> sha]: the sha the candidate is being tested at (set when taken)
  \* the game and the bridge
  lock,        \* bridge lock holder tag: "free" | "old" | "new" | "owner" (a dead holder's tag is stale)
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

HV == <<phase, ctx, stopFile, switched, armLive, straggler, launchFails, handoffs, deaths>>
CV == <<cand, where, candSha>>
GV == <<lock, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack>>
XV == <<verdicts, csWhileUp, reloadNoRule, lateEmit>>
vars == <<HV, msg, CV, GV, XV>>

MsgStates == {"unsent", "inOld", "preOld", "takenOld", "readOld", "inNew", "durable", "handled", "lost"}
Alive(c) == ctx[c] \in {"live", "closing", "dying"}     \* the process exists
Working(c) == ctx[c] \in {"live", "closing"}            \* ... and is not being killed
OldOwed == {"inOld", "takenOld", "readOld"}             \* his input after the cursor the old window owes
NewInbox == {"inNew", "durable"}
Holding == {"held", "observed"}
Settled == {"resolved", "invalid", "parked"}
Drives(c) == c \in drivers /\ lock = c /\ Working(c)
Owes == \E m \in Msgs : msg[m] \in OldOwed
Holds(c) == \E k \in Cands : cand[k] \in Holding /\ where[k] = c
\* What the old context's memory loses when its process ends.
LoseMsg == [m \in Msgs |-> IF msg[m] = "takenOld" THEN "lost" ELSE msg[m]]
LoseCand == [k \in Cands |-> IF Bug("mem_queue") /\ where[k] = "old" /\ cand[k] \in {"queued"} \cup Holding
                             THEN "lost" ELSE cand[k]]
LoseWhere == [k \in Cands |-> IF Bug("mem_queue") /\ where[k] = "old" THEN "-" ELSE where[k]]

Init ==
  /\ phase = "running"
  /\ ctx = [c \in Ctx |-> IF c = "old" THEN "live" ELSE "absent"]
  /\ stopFile = FALSE /\ switched = FALSE /\ straggler = FALSE /\ launchFails = 0
  /\ handoffs = 0 /\ deaths = 0
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

\* He writes. A live window's transcript takes it (a dying one too, unless term_drop); with no window up his phone
\* holds it until one is ("durable"); the known race drops it.
Send(m) ==
  /\ msg[m] = "unsent"
  /\ msg' = [msg EXCEPT ![m] =
        IF Working("old") THEN "inOld"
        ELSE IF ctx["old"] = "dying" THEN (IF Hz("term_drop") THEN "lost" ELSE "inOld")
        ELSE IF ctx["new"] = "live" THEN "inNew"
        ELSE IF Bug("dead_session_drop") THEN "lost"
        ELSE "durable"]
  /\ UNCHANGED <<HV, CV, GV, XV>>

\* A candidate arrives. Fixed: the durable queue. Bug: the live context's memory, else nowhere.
Arrive(k) ==
  /\ HasGame /\ cand[k] = "none"
  /\ LET w == IF ~Bug("mem_queue") THEN "durable"
              ELSE IF Working("old") THEN "old"
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
  /\ UNCHANGED <<phase, ctx, stopFile, switched, armLive, straggler, handoffs, deaths, msg, CV, GV, XV>>

\* arena.py: the old target is not idle after IDLE_WAIT_S; it is stopped as it is, the bridge held and a candidate
\* in flight (the clock is the environment: never fair).
ForceClaim ==
  /\ IsArena /\ phase = "pending"
  /\ lock = "old" \/ Holds("old")
  /\ phase' = "claimed"
  /\ UNCHANGED <<ctx, stopFile, switched, armLive, straggler, launchFails, handoffs, deaths, msg, CV, GV, XV>>

\* kill_pid "survived": the window is still there after SIGKILL. The restart fails; the window stays live. A fault
\* like a death: it shares their budget of one per behaviour (a kill that never takes is an owner page, B3.5).
Survive ==
  /\ phase = "killing" /\ ctx["old"] = "dying" /\ deaths = 0
  /\ deaths' = 1
  /\ ctx' = [ctx EXCEPT !["old"] = "live"]
  /\ phase' = IF Bug("relaunch_after_survive") THEN "killed" ELSE "running"
  /\ stopFile' = FALSE
  /\ UNCHANGED <<switched, armLive, straggler, launchFails, handoffs, msg, CV, GV, XV>>

(* --------------------------------------------------------------- deaths *)

\* The old window dies by itself mid-handoff. Its memory goes as at a kill; the next tick adopts it (restart_orphan
\* writes the killed record) unless no_adopt. No EXIT trap: its bridge tag is stale.
OldDiesAlone ==
  /\ "old_alone" \in Deaths /\ deaths = 0
  /\ phase \in {"pending", "claimed"} /\ Working("old")
  /\ deaths' = 1
  /\ ctx' = [ctx EXCEPT !["old"] = "dead"]
  /\ phase' = IF Bug("no_adopt") THEN "orphaned" ELSE "killed"
  /\ msg' = LoseMsg /\ cand' = LoseCand /\ where' = LoseWhere
  /\ drivers' = drivers \ {"old"} /\ armLive' = armLive \ {"old"}
  /\ UNCHANGED <<stopFile, switched, straggler, launchFails, handoffs, candSha, lock, game, deployed, loaded,
                 hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, XV>>

\* The Dispatcher dies after the claim; it restarts from the state.json saved before that tick: pending.
DispatcherDies ==
  /\ "dispatcher" \in Deaths /\ deaths = 0
  /\ phase = "claimed"
  /\ deaths' = 1 /\ phase' = "pending"
  /\ UNCHANGED <<ctx, stopFile, switched, armLive, straggler, launchFails, handoffs, msg, CV, GV, XV>>

\* The fresh window dies after its wake read. What it held goes back to the queue (in_flight recovery).
WakeDies ==
  /\ "wake" \in Deaths /\ deaths = 0
  /\ phase = "relaunched" /\ ctx["new"] = "live"
  /\ deaths' = 1
  /\ ctx' = [ctx EXCEPT !["new"] = "dead"] /\ phase' = "respawn"
  /\ cand' = [k \in Cands |-> IF where[k] = "new" /\ cand[k] \in Holding THEN "queued" ELSE cand[k]]
  /\ where' = [k \in Cands |-> IF where[k] = "new" /\ cand[k] \in Holding THEN "durable" ELSE where[k]]
  /\ lock' = IF lock = "new" THEN "free" ELSE lock
  /\ drivers' = drivers \ {"new"} /\ armLive' = armLive \ {"new"}
  /\ UNCHANGED <<stopFile, switched, straggler, launchFails, handoffs, msg, candSha, game, deployed, loaded,
                 hotPending, pendingFix, fixes, crashes, ruleLogged, ownerBack, XV>>

Death == OldDiesAlone \/ DispatcherDies \/ WakeDies

(* ------------------------------------------------------------- contexts *)

\* The old window takes his next prompt (it reads after its goodbye too). With dequeue_gap the prompt is first only
\* in memory; Persist writes it to the transcript.
Read(m) ==
  /\ Working("old") /\ msg[m] \in {"inOld", "preOld"}
  /\ msg' = [msg EXCEPT ![m] = IF Hz("dequeue_gap") THEN "takenOld" ELSE "readOld"]
  /\ UNCHANGED <<HV, CV, GV, XV>>

Persist(m) ==
  /\ Working("old") /\ msg[m] = "takenOld"
  /\ msg' = [msg EXCEPT ![m] = "readOld"]
  /\ UNCHANGED <<HV, CV, GV, XV>>

\* The turn ends: an ended assistant turn answers it (unanswered() clears what an ended turn follows).
Answer(m) ==
  /\ Working("old") /\ msg[m] = "readOld"
  /\ msg' = [msg EXCEPT ![m] = "handled"]
  /\ UNCHANGED <<HV, CV, GV, XV>>

\* The new window answers what its wake replayed, or what reached it directly. Atomic: a death after the wake is
\* WakeDies, and the next window replays the wake until one has answered it.
HandleNew(m) ==
  /\ ctx["new"] = "live" /\ msg[m] \in NewInbox
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
  /\ ownerBack /\ Working(c)
  /\ c \in drivers \/ Holds(c)                                        \* a released lane may still hold work
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
  /\ Working(c) /\ cand[k] = "held" /\ where[k] = c /\ candSha[k] # deployed
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
  /\ Working(c) /\ cand[k] = "observed" /\ where[k] = c
  /\ (loaded = candSha[k] \/ Bug("stale_verdict"))
  /\ cand' = [cand EXCEPT ![k] = "resolved"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ verdicts' = verdicts \cup {[sha |-> candSha[k], ld |-> loaded]}
  /\ UNCHANGED <<HV, msg, candSha, GV, csWhileUp, reloadNoRule, lateEmit>>

\* The game reloaded between observation and record: the observation is stale and the candidate is retested.
Redo(c, k) ==
  /\ Working(c) /\ cand[k] = "observed" /\ where[k] = c /\ loaded # candSha[k]
  /\ cand' = [cand EXCEPT ![k] = "held"]
  /\ UNCHANGED <<HV, msg, where, candSha, GV, XV>>

Invalid(c, k) ==
  /\ Working(c) /\ cand[k] \in Holding /\ where[k] = c
  /\ cand' = [cand EXCEPT ![k] = "invalid"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

\* With the owner back, queued work is parked rather than waited on forever.
Park(c, k) ==
  /\ ctx[c] = "live" /\ ownerBack /\ cand[k] = "queued" /\ where[k] \in {"durable", c}
  /\ cand' = [cand EXCEPT ![k] = "parked"] /\ where' = [where EXCEPT ![k] = "-"]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

\* testpilot.py `recovering`: a test the dead old pilot had in flight is recovered by the new one and requeued.
Recover(k) ==
  /\ ctx["new"] = "live" /\ ~Alive("old") /\ cand[k] \in Holding /\ where[k] = "old"
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

\* Close-out done, GOODBYE / STOP written; the cursor is his goodbye. It begins only with his inbox answered (A2:
\* Claude Code runs queued prompts in order); closeout_skips_queue leaves them before the cursor.
Begin ==
  /\ phase = "running" /\ ctx["old"] = "live" /\ handoffs < MaxHandoffs
  /\ ~Owes \/ Bug("closeout_skips_queue")
  /\ phase' = "pending" /\ ctx' = [ctx EXCEPT !["old"] = "closing"] /\ stopFile' = TRUE
  /\ msg' = [m \in Msgs |-> IF msg[m] \in {"inOld", "readOld"} THEN "preOld" ELSE msg[m]]
  /\ UNCHANGED <<switched, armLive, straggler, launchFails, handoffs, deaths, CV, GV, XV>>

\* He wrote again before the claim: the old context goes back to work (B3.1).
Cancel ==
  /\ phase = "pending" /\ Owes
  /\ phase' = "running" /\ ctx' = [ctx EXCEPT !["old"] = "live"] /\ stopFile' = FALSE
  /\ UNCHANGED <<switched, armLive, straggler, launchFails, handoffs, deaths, msg, CV, GV, XV>>

\* The re-check (B3.3): nothing he wrote after the cursor is owed; the old context's hands empty, its bridge freed.
Claim ==
  /\ phase = "pending"
  /\ ~Owes \/ Bug("no_recheck") \/ Bug("no_claim_recheck")
  /\ (lock # "old" \/ Bug("overlap"))
  /\ ~Holds("old") \/ Bug("mem_queue")
  /\ phase' = "claimed"
  /\ UNCHANGED <<ctx, stopFile, switched, armLive, straggler, launchFails, handoffs, deaths, msg, CV, GV, XV>>

\* recheck_at_kill / the final fence holds: back to pending, decide() judges again next tick.
Abort ==
  /\ phase = "claimed" /\ Owes /\ ~Bug("no_recheck")
  /\ phase' = "pending"
  /\ UNCHANGED <<ctx, stopFile, switched, armLive, straggler, launchFails, handoffs, deaths, msg, CV, GV, XV>>

\* SIGTERM, right after the final fence (the gap between them is milliseconds: taken as one step).
Term ==
  /\ phase \in {"claimed", "relaunched"} /\ Working("old")
  /\ phase = "claimed" \/ Bug("overlap")
  /\ ~Owes \/ Bug("no_recheck") \/ Bug("no_fence")
  /\ ctx' = [ctx EXCEPT !["old"] = "dying"]
  /\ phase' = IF phase = "claimed" THEN "killing" ELSE phase
  /\ UNCHANGED <<stopFile, switched, armLive, straggler, launchFails, handoffs, deaths, msg, CV, GV, XV>>

\* The process ends: by its EXIT trap (bridge released) or by SIGKILL after the grace window (bridge tag stale).
\* Its memory is gone; with the queue on disk what it held stays in_flight for the new context to recover.
Reap ==
  /\ ctx["old"] = "dying"
  /\ ctx' = [ctx EXCEPT !["old"] = "dead"]
  /\ phase' = IF phase = "killing" THEN "killed" ELSE phase
  /\ msg' = LoseMsg /\ cand' = LoseCand /\ where' = LoseWhere
  /\ \E trap \in BOOLEAN : lock' = IF lock = "old" /\ trap THEN "free" ELSE lock
  /\ drivers' = drivers \ {"old"}
  /\ armLive' = armLive \ {"old"}
  /\ straggler' = Bug("straggler")
  /\ UNCHANGED <<stopFile, switched, launchFails, handoffs, deaths, candSha, game, deployed, loaded, hotPending,
                 pendingFix, fixes, crashes, ruleLogged, ownerBack, XV>>

\* arena.py releases the stopped arm's bridge holds after the stop; a pilot treats a dead holder's tag as stale.
ReleaseStale ==
  /\ phase = "killed" /\ lock = "old" /\ ~Alive("old")
  /\ lock' = "free"
  /\ UNCHANGED <<HV, msg, CV, drivers, game, deployed, loaded, hotPending, pendingFix, fixes, crashes, ruleLogged,
                 ownerBack, XV>>

\* Switch event, new target / window starts; its wake reads the old transcript from the cursor (B1).
Relaunch ==
  /\ phase = "killed" \/ (phase = "claimed" /\ Bug("overlap"))
  /\ ctx["new"] = "absent"
  /\ lock # "old" \/ Bug("overlap")
  /\ phase' = "relaunched" /\ ctx' = [ctx EXCEPT !["new"] = "live"]
  /\ switched' = TRUE
  /\ armLive' = IF IsArena THEN armLive \cup {"new"} ELSE armLive
  /\ msg' = [m \in Msgs |-> IF msg[m] \in {"inOld", "readOld"} /\ ~Bug("wake_skips_old") THEN "inNew" ELSE msg[m]]
  /\ UNCHANGED <<stopFile, straggler, launchFails, handoffs, deaths, CV, GV, XV>>

\* The next window after a wake death reads the wake again (nothing answered it); wake_once replays nothing.
Respawn ==
  /\ phase = "respawn"
  /\ ctx' = [ctx EXCEPT !["new"] = "live"] /\ phase' = "relaunched"
  /\ armLive' = IF IsArena THEN armLive \cup {"new"} ELSE armLive
  /\ msg' = [m \in Msgs |-> IF msg[m] = "inNew" /\ Bug("wake_once") THEN "lost" ELSE msg[m]]
  /\ UNCHANGED <<stopFile, switched, straggler, launchFails, handoffs, deaths, CV, GV, XV>>

Verify ==
  /\ phase = "relaunched" /\ ctx["new"] = "live" /\ ~Alive("old")
  /\ phase' = "verified" /\ stopFile' = FALSE
  /\ UNCHANGED <<ctx, switched, armLive, straggler, launchFails, handoffs, deaths, msg, CV, GV, XV>>

\* The handoff is over; the new context is the old one of the next handoff (once its predecessor's leftovers are
\* recovered: nothing of the dead one is left in hand).
Ren(x) == IF x = "new" THEN "old" ELSE x
Rotate ==
  /\ phase = "verified" /\ ctx["new"] = "live"
  /\ ~\E k \in Cands : where[k] = "old"
  /\ lock # "old"
  /\ phase' = "running" /\ handoffs' = handoffs + 1
  /\ ctx' = [c \in Ctx |-> IF c = "old" THEN "live" ELSE "absent"]
  /\ switched' = FALSE /\ launchFails' = 0
  /\ armLive' = {Ren(a) : a \in armLive}
  /\ msg' = [m \in Msgs |-> IF msg[m] \in NewInbox THEN "inOld" ELSE msg[m]]
  /\ where' = [k \in Cands |-> Ren(where[k])]
  /\ lock' = Ren(lock) /\ drivers' = {Ren(d) : d \in drivers}
  /\ UNCHANGED <<stopFile, straggler, deaths, cand, candSha, game, deployed, loaded, hotPending, pendingFix, fixes,
                 crashes, ruleLogged, ownerBack, XV>>

Env ==
  \/ \E m \in Msgs : Send(m)
  \/ \E k \in Cands : Arrive(k)
  \/ \E f \in {"cs", "hot"} : FixReady(f)
  \/ Crash \/ OwnerReturn \/ OwnerTake \/ OldEmit \/ LaunchFail \/ Begin \/ ForceClaim \/ Survive \/ Death

\* The protocol's obligations. StopGame, HotDeploy and Invalid are choices, not obligations: no fairness.
Progress(c) ==
  \/ IF c = "old" THEN \E m \in Msgs : Read(m) \/ Persist(m) \/ Answer(m)
                  ELSE \E m \in Msgs : HandleNew(m)
  \/ Acquire(c) \/ Release(c) \/ Yield(c)
  \/ \E k \in Cands : Take(c, k) \/ Retarget(c, k) \/ Observe(c, k) \/ Record(c, k) \/ Redo(c, k)
     \/ Park(c, k) \/ (c = "new" /\ Recover(k))
  \/ CsDeploy(c) \/ HotReload(c) \/ LogRule(c) \/ Reload(c)

Requeue(k) ==
  /\ ctx["old"] = "closing" /\ cand[k] \in Holding /\ where[k] = "old" /\ ~Bug("mem_queue")
  /\ cand' = [cand EXCEPT ![k] = "queued"] /\ where' = [where EXCEPT ![k] = "durable"]
  /\ UNCHANGED <<HV, msg, candSha, GV, XV>>

Handoff == Cancel \/ Claim \/ Abort \/ Term \/ Reap \/ ReleaseStale \/ Relaunch \/ Respawn \/ Verify \/ Rotate
           \/ \E k \in Cands : Requeue(k)

Next == Env \/ Handoff \/ \E c \in Ctx : Progress(c) \/ StopGame(c) \/ HotDeploy(c) \/ \E k \in Cands : Invalid(c, k)

\* Weak fairness on the protocol only; none on the environment (he may never write, nothing may crash, a death is
\* never owed). One WF per context over the disjunction of its obligations: each obligation can fire only finitely
\* often between environment steps, so the disjunction cannot be satisfied forever by a loop that starves one.
Fairness == WF_vars(Handoff) /\ WF_vars(Progress("old")) /\ WF_vars(Progress("new"))

Spec == Init /\ [][Next]_vars /\ Fairness

(* ------------------------------------------------------------- properties *)

TypeOK ==
  /\ phase \in {"running", "pending", "claimed", "killing", "killed", "relaunched", "respawn", "verified", "orphaned"}
  /\ ctx \in [Ctx -> {"absent", "live", "closing", "dying", "dead"}]
  /\ msg \in [Msgs -> MsgStates]
  /\ cand \in [Cands -> {"none", "queued", "held", "observed", "resolved", "invalid", "parked", "lost"}]
  /\ lock \in {"free", "old", "new", "owner"} /\ drivers \subseteq Ctx /\ armLive \subseteq Ctx

\* S1: at most one live context per seat / lane, at most one live driver per game (the owner counts), at most one
\* live arm target per lane.
S1 == /\ Cardinality({c \in Ctx : Alive(c)}) <= 1
      /\ Cardinality(drivers \cup (IF lock = "owner" THEN {"owner"} ELSE {})) <= 1
      /\ Cardinality(armLive) <= 1
\* S2: no verdict for sha X while the game had sha Y loaded.
S2 == \A v \in verdicts : v.sha = v.ld
\* S3: no C# deploy while the game process lives.
S3 == ~csWhileUp
\* S4: every reload, cold or hot, is preceded by a logged rule.
S4 == ~reloadNoRule
\* S5: no owner message and no queued candidate is lost across a handoff. A message left in a dead window's transcript
\* once the new window has done its wake read is lost too: nobody will read it again.
Stranded(m) == msg[m] \in {"inOld", "preOld", "readOld"} /\ ~Alive("old") /\ ctx["new"] = "live"
S5 == /\ \A m \in Msgs : msg[m] # "lost" /\ ~Stranded(m)
      /\ \A k \in Cands : cand[k] # "lost"
\* S6: no event and no push from the old arm after its switch timestamp.
S6 == ~lateEmit

\* L1: every candidate that arrives is eventually resolved, marked invalid or parked.
L1 == \A k \in Cands : (cand[k] # "none") ~> (cand[k] \in Settled)
\* L2 (not in section 7, added): every owner message sent is eventually handled by the old or the new context.
L2 == \A m \in Msgs : (msg[m] # "unsent") ~> (msg[m] = "handled")

\* Witnesses, each expected VIOLATED: the fixed rows reach what they pass on.
NotVerified == phase # "verified"
NewNeverDrives == lock # "new"
NoGap == \A m \in Msgs : msg[m] # "takenOld"
NoSecondHandoff == handoffs < 1 \/ phase # "verified"
NoForcedKill == ~(phase = "killing" /\ (lock = "old" \/ Holds("old")))
=============================================================================
