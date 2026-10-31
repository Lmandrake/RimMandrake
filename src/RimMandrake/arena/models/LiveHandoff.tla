------------------------------ MODULE LiveHandoff ------------------------------
(***************************************************************************)
(* The handing-over of a live resource from a context that is ending to a  *)
(* fresh one while inputs keep arriving (ARENA_HANDOFF_PROVE_MODEL_FINDS_  *)
(* KNOWN_RACE; design/RimMandrake/architecture_switch_harness_2026-10-29.md *)
(* section 7, step 11 of section 6).                                       *)
(*                                                                         *)
(* One spec, three readings of the same shape:                             *)
(*                                                                         *)
(*   spec name        goodbye restart         TestPilot handoff  arena     *)
(*   ---------------  ----------------------  -----------------  --------- *)
(*   Goodbye          his whole-message       pilot handoff      `arena    *)
(*                    goodbye                 request            switch`   *)
(*   CloseOut         light close-out, then   finish the test    STOP,     *)
(*                    seat_restart request    boundary           pass ends *)
(*   Check            Dispatcher grace/quiet  same               wait idle *)
(*   WriteRecord      killed record + cursor  session file       --        *)
(*   Fence            final_fence             same               --        *)
(*   Kill             SIGTERM/SIGKILL pid     same               stop the  *)
(*                                                               target    *)
(*   SwitchRecord     restart.jsonl `killed`  same               `switch`  *)
(*                                                               event     *)
(*   Relaunch         in-tile relaunch, wake  fresh pilot        start new *)
(*                    reads from the cursor   reads session file target    *)
(*                                                                         *)
(* The code this models: src/RimMandrake/rimflow/seat_restart.py           *)
(* (cursor_verdict, restart_kill, final_fence, recheck_at_kill) and        *)
(* .claude/hooks/conductor_goodbye.py.  The unfixed protocol is the one    *)
(* in design/RimMandrake/conductor_briefing_2026-10-28.md B1-B3 before the *)
(* blind reviews of 2026-10-29 (commits a64eaede64, 27e7105189): the       *)
(* request is bound to its own write time after the close-out (GOODBYE.ts) *)
(* and the fresh window reads only what came after it.                     *)
(*                                                                         *)
(* Bugs is the set of protocol defects switched ON.  {} is the fixed       *)
(* protocol.  "goodbye_unfixed" is the known race.  Each other member      *)
(* removes exactly one guard so each invariant is shown to have teeth      *)
(* (check_models.py runs every one and expects its named violation).       *)
(*                                                                         *)
(* Bounds (FixedSafety.cfg / FixedLiveness.cfg): 2 goodbyes, 3 reloads, 1  *)
(* crash, 2 candidates (one hot-loadable, one C#), YieldBound 2; safety    *)
(* with 2 owner messages, liveness with 1 (the 2-message liveness graph    *)
(* outgrows the seat's memory cap).                                        *)
(*                                                                         *)
(* Assumptions, not checked here:                                          *)
(*  A1 Remote Control never accepts a message for a dead window; with      *)
(*     RC_DROPS_TO_DEAD = TRUE S5 fails, and that is the owner's accepted  *)
(*     risk ("If I'm typing at the same time it's an acceptable risk").    *)
(*  A2 the close-out turn answers every message that came before his       *)
(*     goodbye (CloseOut's guard; Claude Code runs queued prompts in       *)
(*     order).  S5 rests on it: mutation closeout_skips_queue breaks S5.   *)
(*  A3 L2's "within the bound" is counted in pilot steps (YieldBound),     *)
(*     not seconds: after his return the pilot may finish its current      *)
(*     step and yield, nothing more.  Dispatcher steps of a handoff in     *)
(*     flight are not counted; L2 proper says they end.                    *)
(*  A4 the candidate queue is on disk: KillOk keeps it by construction,    *)
(*     and only queue_in_memory loses it.  S5's candidate half shows the   *)
(*     invariant can see a loss, not that the code persists the queue.    *)
(*  A5 a handoff starts only at a test boundary (Goodbye's guard), so      *)
(*     KillOk's requeue of an in-flight test is reached only by mutants.   *)
(*  A6 Fence models the input gate only.  The real fence's owner-idle and *)
(*     window-status gates can only hold a kill, so they keep S1-S6.  For  *)
(*     L1/L2 a hold must END: in seat_restart.py each hold bumps `busy`,   *)
(*     and busy >= busy_ticks fails the restart, the window stays live and *)
(*     can yield -- the model's Fence-to-pending loop plus Check cancel /  *)
(*     KillSurvives "failed".  A gate that held forever would break L2.    *)
(*                                                                         *)
(* Process death (ARENA_HANDOFF_PROVE_SURVIVES_PROCESS_DEATH).  Deaths is  *)
(* the set of deaths the environment may do, at most one per behaviour;    *)
(* {} leaves every other state as it was.                                  *)
(*   "old_alone"  the old window dies by itself mid-handoff (OldDiesAlone) *)
(*   "dispatcher" the Dispatcher dies, anywhere up to the relaunch, and    *)
(*                comes back from a state.json saved before that tick      *)
(*                (DispatcherDies/DispatcherRestarts; tick() saves only in *)
(*                its finally, so a SIGKILL loses the tick's state)        *)
(*   "wake"       the fresh window dies after its wake read (WakeDies)     *)
(* Respawn is a later fresh window with no restart generation: what a      *)
(* fleet launch or the owner opens.  Its fairness is generous on purpose:  *)
(* seat_loop.sh drops to a login shell after a death with no record, so    *)
(* in the code it may need him.  selftest_seat_restart_death.py shows each *)
(* of these on real processes under real SIGKILL.                          *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS Msgs,              \* owner messages that may arrive (model values)
          Bugs,              \* set of strings, see BugNames
          RC_DROPS_TO_DEAD,  \* TRUE: Remote Control accepts a message for a dead window and it vanishes
          MaxGoodbyes,       \* goodbye attempts (a cancelled one may be retried)
          MaxReloads,        \* game (re)launches the pilot may spend
          MaxCrashes,
          YieldBound,        \* driver steps allowed between his return and the game being freed
          Deaths             \* subset of DeathNames: the process deaths the environment may do

BugNames == {"goodbye_unfixed", "relaunch_after_survive", "verdict_stale", "deploy_live",
             "silent_reload", "queue_in_memory", "switch_early", "no_park", "ignore_owner", "closeout_skips_queue"}
ASSUME Bugs \subseteq BugNames
DeathNames == {"old_alone", "dispatcher", "wake"}
ASSUME Deaths \subseteq DeathNames

Ctx   == {"old", "new"}
Cands == {"c1", "c2"}
Sha   == [c \in Cands |-> IF c = "c1" THEN "s1" ELSE "s2"]
Class == [c \in Cands |-> IF c = "c1" THEN "hot" ELSE "cs"]   \* hot: def/bridge reload; cs: C# needs a reload
Shas  == {"s0", "s1", "s2"}
Done  == {"resolved", "invalid", "parked"}

VARIABLES
  hp,          \* handoff phase
  goodbyes,
  cst,         \* context state: none | live | closing | idle | dead
  txLen,       \* records in the old window's transcript (his goodbye included)
  cursor,      \* fixed: transcript position just past his goodbye (request input_ts / tx_offset)
  reqPos,      \* transcript position when the request was written (GOODBYE.ts)
  recCursor,   \* the cursor carried by the killed record
  sent, pos,   \* messages he has sent; pos[m] = place in the old transcript (0 = not there)
  handled,     \* messages some context has answered
  inbox,       \* messages the new context has (read at wake, or sent to it directly)
  dropped,     \* messages Remote Control swallowed (only if RC_DROPS_TO_DEAD)
  lost,        \* messages in the old transcript that neither context will answer (set at wake)
  game, deployed, loaded,
  lock,        \* bridge lock holder tag: none | old | new | owner
  holds,       \* holds[c]: c believes it drives the game
  cand, testBy,
  ownerHome, yieldSteps, crashes, reloads,
  ruleOpen,    \* a reload rule has been logged and not yet spent
  n,           \* event counter (ordering of logged events)
  ruleN, reloadN, prevReloadN,
  reloadRuleN, \* the newest rule's n as seen by the newest reload
  lastEmit,    \* lastEmit[c] = n of c's newest event or push
  switchN,     \* switchN[c] = n of the switch event that ended c (0 = none)
  verdicts,    \* set of <<sha the verdict is for, sha the game had loaded>>
  deaths,      \* process deaths so far (at most one per behaviour)
  dispDown     \* the Dispatcher process is dead

vars == <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, sent, pos, handled, inbox,
          dropped, lost, game, deployed, loaded, lock, holds, cand, testBy, ownerHome,
          yieldSteps, crashes, reloads, ruleOpen, n, ruleN, reloadN, prevReloadN,
          reloadRuleN, lastEmit, switchN, verdicts>>
msgVars  == <<sent, pos, handled, inbox, dropped, lost>>
gameVars == <<game, deployed, loaded, lock, holds, cand, testBy, ownerHome, yieldSteps,
              crashes, reloads, ruleOpen, ruleN, reloadN, prevReloadN, reloadRuleN, verdicts>>

Bug(b) == b \in Bugs
Alive(c) == cst[c] \in {"live", "closing", "idle"}
\* The transcript position after which input must cancel the restart, and from which the wake reads.
Bound    == IF Bug("goodbye_unfixed") THEN reqPos ELSE cursor
WakeFrom == IF Bug("goodbye_unfixed") THEN reqPos ELSE recCursor
InputAfter(p) == \E m \in sent : pos[m] > p

Init ==
  /\ hp = "none" /\ goodbyes = 0 /\ deaths = 0 /\ dispDown = FALSE
  /\ cst = [c \in Ctx |-> IF c = "old" THEN "live" ELSE "none"]
  /\ txLen = 0 /\ cursor = 0 /\ reqPos = 0 /\ recCursor = 0
  /\ sent = {} /\ pos = [m \in Msgs |-> 0] /\ handled = {} /\ inbox = {}
  /\ dropped = {} /\ lost = {}
  /\ game = "up" /\ deployed = "s0" /\ loaded = "s0"
  /\ lock = "old" /\ holds = [c \in Ctx |-> c = "old"]
  /\ cand = [c \in Cands |-> "future"] /\ testBy = [c \in Cands |-> "none"]
  /\ ownerHome = FALSE /\ yieldSteps = 0 /\ crashes = 0 /\ reloads = 0
  /\ ruleOpen = FALSE /\ n = 0 /\ ruleN = 0 /\ reloadN = 0 /\ prevReloadN = 0 /\ reloadRuleN = 0
  /\ lastEmit = [c \in Ctx |-> 0] /\ switchN = [c \in Ctx |-> 0]
  /\ verdicts = {}

Emit(c) == /\ n' = n + 1
           /\ lastEmit' = [lastEmit EXCEPT ![c] = n + 1]

(*************************** the owner and the world ***************************)

\* He sends a message.  It lands in whichever window is alive.
Send(m) ==
  /\ m \notin sent
  /\ sent' = sent \cup {m}
  /\ IF Alive("old")
       THEN /\ txLen' = txLen + 1
            /\ pos' = [pos EXCEPT ![m] = txLen + 1]
            /\ UNCHANGED <<inbox, dropped>>
     ELSE IF Alive("new")
       THEN /\ inbox' = inbox \cup {m}
            /\ UNCHANGED <<txLen, pos, dropped>>
     ELSE /\ RC_DROPS_TO_DEAD          \* else no window is up: his phone holds it until one is
          /\ dropped' = dropped \cup {m}
          /\ UNCHANGED <<txLen, pos, inbox>>
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, cursor, reqPos, recCursor, handled, lost, gameVars, n,
                 lastEmit, switchN>>

\* His whole-message goodbye (or a pilot handoff request, or `arena switch`).
Goodbye ==
  /\ hp \in {"none", "cancelled", "failed"}
  /\ goodbyes < MaxGoodbyes
  /\ cst["old"] = "live"
  /\ \A c \in Cands : testBy[c] # "old"        \* a pilot hands off at a test boundary
  /\ goodbyes' = goodbyes + 1
  /\ txLen' = txLen + 1
  /\ cursor' = txLen + 1                        \* fixed: bound to his goodbye (input_ts, tx_offset)
  /\ cst' = [cst EXCEPT !["old"] = "closing"]
  /\ hp' = "closeout"
  /\ UNCHANGED <<deaths, dispDown, reqPos, recCursor, msgVars, gameVars, n, lastEmit, switchN>>

Arrive(c) ==
  /\ cand[c] = "future"
  /\ cand' = [cand EXCEPT ![c] = IF ownerHome /\ ~Bug("no_park") THEN "parked" ELSE "queued"]
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, lock, holds, testBy, ownerHome, yieldSteps, crashes, reloads, ruleOpen,
                 n, ruleN, reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

Crash ==
  /\ game = "up" /\ crashes < MaxCrashes
  /\ game' = "down" /\ loaded' = "none" /\ crashes' = crashes + 1
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, deployed, lock,
                 holds, cand, testBy, ownerHome, yieldSteps, reloads, ruleOpen, n, ruleN,
                 reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

OwnerReturns ==
  /\ ~ownerHome
  /\ ownerHome' = TRUE
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, lock, holds, cand, testBy, yieldSteps, crashes, reloads, ruleOpen, n,
                 ruleN, reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* He sits down at Archmagi once the game is free.
OwnerTakes ==
  /\ ownerHome /\ lock = "none"
  /\ lock' = "owner"
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, holds, cand, testBy, ownerHome, yieldSteps, crashes, reloads, ruleOpen,
                 n, ruleN, reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

Env == \/ \E m \in Msgs : Send(m)
       \/ Goodbye
       \/ \E c \in Cands : Arrive(c)
       \/ Crash
       \/ OwnerReturns

(*************************** the contexts answering him ***************************)

\* A queued prompt may be seen mid close-out, or not (440 of 444 were only queued_command
\* attachments): the old window may answer any message in its transcript while it lives.
HandleOld(m) ==
  /\ Alive("old") /\ pos[m] > 0 /\ m \notin handled
  /\ handled' = handled \cup {m}
  /\ Emit("old")
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, sent, pos, inbox,
                 dropped, lost, gameVars, switchN>>

HandleNew(m) ==
  /\ cst["new"] = "live" /\ m \in inbox /\ m \notin handled
  /\ handled' = handled \cup {m}
  /\ Emit("new")
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, sent, pos, inbox,
                 dropped, lost, gameVars, switchN>>

(*************************** the handoff (Dispatcher / arena switch) ***************************)

\* The close-out turn ends and the window writes its request (GOODBYE.ts = now).
CloseOut ==
  /\ hp = "closeout" /\ cst["old"] = "closing"
  \* A2: Claude Code runs queued prompts in order, so everything before his goodbye has had its
  \* turn by the time the close-out turn ends.  "closeout_skips_queue" drops A2 to show S5 rests on it.
  /\ Bug("closeout_skips_queue") \/ \A m \in sent : 0 < pos[m] /\ pos[m] < cursor => m \in handled
  /\ reqPos' = txLen
  /\ cst' = [cst EXCEPT !["old"] = "idle"]
  /\ hp' = "pending"
  /\ UNCHANGED <<goodbyes, deaths, dispDown, txLen, cursor, recCursor, msgVars, gameVars, n, lastEmit, switchN>>

\* Grace over: any input after the bound cancels; else the window is quiet.
Check ==
  /\ ~dispDown
  /\ hp = "pending"
  /\ IF InputAfter(Bound)
       THEN /\ hp' = "cancelled"
            /\ cst' = [cst EXCEPT !["old"] = "live"]
            /\ UNCHANGED <<n, switchN>>
       ELSE /\ hp' = "checked"
            /\ UNCHANGED cst
            /\ IF Bug("switch_early")            \* the switch event written before the arm is stopped
                 THEN /\ n' = n + 1
                      /\ switchN' = [switchN EXCEPT !["old"] = n + 1]
                 ELSE UNCHANGED <<n, switchN>>
  /\ UNCHANGED <<goodbyes, deaths, dispDown, txLen, cursor, reqPos, recCursor, msgVars, gameVars, lastEmit>>

\* Fixed only: the killed record (with the cursor) reaches disk before the final fence.
WriteRecord ==
  /\ ~dispDown
  /\ hp = "checked" /\ ~Bug("goodbye_unfixed")
  /\ recCursor' = cursor
  /\ hp' = "recorded"
  /\ UNCHANGED <<goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, msgVars, gameVars, n, lastEmit, switchN>>

\* Fixed only: the final fence re-reads the transcript from the cursor; growth puts it back to pending.
Fence ==
  /\ ~dispDown
  /\ hp = "recorded"
  /\ hp' = IF ~InputAfter(cursor) THEN "fenced"
           ELSE IF Alive("old") THEN "pending"
           ELSE "orphaned"                  \* aborted, and the next tick finds the session gone
  /\ UNCHANGED <<goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, gameVars, n,
                 lastEmit, switchN>>

KillReady == IF Bug("goodbye_unfixed") THEN hp = "checked" ELSE hp = "fenced"

\* The kill succeeds: the process is gone; its EXIT trap releases the bridge; an in-flight test
\* goes back to the durable queue (or, with queue_in_memory, the old pilot's queue dies with it).
KillOk ==
  /\ ~dispDown
  /\ KillReady
  /\ cst' = [cst EXCEPT !["old"] = "dead"]
  /\ holds' = [holds EXCEPT !["old"] = FALSE]
  /\ lock' = IF lock = "old" THEN "none" ELSE lock
  /\ cand' = [c \in Cands |->
                IF Bug("queue_in_memory") /\ cand[c] \in {"queued", "testing"} THEN "lost"
                ELSE IF cand[c] = "testing" /\ testBy[c] = "old" THEN "queued"
                ELSE cand[c]]
  /\ testBy' = [c \in Cands |-> IF testBy[c] = "old" THEN "none" ELSE testBy[c]]
  /\ hp' = "killed"
  /\ UNCHANGED <<goodbyes, deaths, dispDown, txLen, cursor, reqPos, recCursor, msgVars, game, deployed, loaded,
                 ownerHome, yieldSteps, crashes, reloads, ruleOpen, n, ruleN, reloadN,
                 prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* The kill does not take (kill_pid "survived"/"refused"): never relaunch beside it.
KillSurvives ==
  /\ ~dispDown
  /\ KillReady
  /\ Alive("old")                               \* a window already dead reads "already gone": KillOk
  /\ cst' = [cst EXCEPT !["old"] = "live"]
  /\ hp' = IF Bug("relaunch_after_survive") THEN "killed" ELSE "failed"
  /\ UNCHANGED <<goodbyes, deaths, dispDown, txLen, cursor, reqPos, recCursor, msgVars, gameVars, n, lastEmit,
                 switchN>>

SwitchRecord ==
  /\ hp = "killed"
  /\ IF Bug("switch_early")
       THEN UNCHANGED <<n, switchN>>
       ELSE /\ n' = n + 1
            /\ switchN' = [switchN EXCEPT !["old"] = n + 1]
  /\ hp' = "switched"
  /\ UNCHANGED <<goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, gameVars, lastEmit>>

\* The fresh context starts and its wake reads the old transcript after WakeFrom.
Relaunch ==
  /\ hp = "switched"
  /\ LET read == {m \in sent : pos[m] > WakeFrom}
     IN /\ inbox' = inbox \cup read
        /\ lost' = {m \in sent : pos[m] > 0 /\ m \notin handled /\ m \notin read}
  /\ cst' = [cst EXCEPT !["new"] = "live"]
  /\ hp' = "done"
  /\ UNCHANGED <<goodbyes, deaths, dispDown, txLen, cursor, reqPos, recCursor, sent, pos, handled, dropped,
                 gameVars, n, lastEmit, switchN>>

\* Death 1.  Before the killed record exists the next tick finds the session gone and cancels: no
\* record, so the tile does not relaunch and no wake reads the cursor.  From the record on a
\* SIGKILLed window leaves its session file saying idle, so execute() carries on: the fence still
\* reads the transcript and kill_pid says "already gone".
OldDiesAlone ==
  /\ "old_alone" \in Deaths /\ deaths = 0
  /\ hp \in {"closeout", "pending", "checked", "recorded", "fenced"}
  /\ deaths' = 1
  /\ cst' = [cst EXCEPT !["old"] = "dead"]
  /\ holds' = [holds EXCEPT !["old"] = FALSE]
  /\ lock' = IF lock = "old" THEN "none" ELSE lock
  /\ hp' = IF hp \in {"recorded", "fenced"} THEN hp ELSE "orphaned"
  /\ UNCHANGED <<goodbyes, dispDown, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, cand, testBy, ownerHome, yieldSteps, crashes, reloads, ruleOpen, n, ruleN,
                 reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* Death 2.  What the Dispatcher did to the window and the record stands; its memory of the tick does not.
DispatcherDies ==
  /\ "dispatcher" \in Deaths /\ deaths = 0
  /\ hp \in {"pending", "checked", "recorded", "fenced", "killed", "switched"}
  /\ deaths' = 1 /\ dispDown' = TRUE
  /\ UNCHANGED <<hp, goodbyes, cst, txLen, cursor, reqPos, recCursor, msgVars, gameVars, n,
                 lastEmit, switchN>>

\* It reads state.json from before the tick: "pending".  With the old window alive it judges again;
\* once the kill happened the record on disk is enough and the tile needs no Dispatcher.
DispatcherRestarts ==
  /\ dispDown
  /\ dispDown' = FALSE
  /\ hp' = IF hp \in {"checked", "recorded", "fenced"} THEN "pending" ELSE hp
  /\ UNCHANGED <<goodbyes, deaths, cst, txLen, cursor, reqPos, recCursor, msgVars, gameVars, n,
                 lastEmit, switchN>>

\* Death 3.  The wake printed his messages and set woken_at; nothing has answered them yet.
WakeDies ==
  /\ "wake" \in Deaths /\ deaths = 0
  /\ hp = "done" /\ cst["new"] = "live"
  /\ deaths' = 1
  /\ hp' = "wake_dead"
  /\ cst' = [cst EXCEPT !["new"] = "dead"]
  /\ holds' = [holds EXCEPT !["new"] = FALSE]
  /\ lock' = IF lock = "new" THEN "none" ELSE lock
  /\ cand' = [c \in Cands |-> IF cand[c] = "testing" /\ testBy[c] = "new" THEN "queued" ELSE cand[c]]
  /\ testBy' = [c \in Cands |-> IF testBy[c] = "new" THEN "none" ELSE testBy[c]]
  /\ UNCHANGED <<goodbyes, dispDown, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, ownerHome, yieldSteps, crashes, reloads, ruleOpen, n, ruleN, reloadN,
                 prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* A later fresh window, with no generation token: no record is replayed to it, so every message
\* no context answered is gone (a pointer in the wake text is not a read).
Respawn ==
  /\ hp \in {"orphaned", "wake_dead"}
  /\ hp' = "respawned"
  /\ cst' = [cst EXCEPT !["new"] = "live"]
  /\ lost' = lost \cup {m \in sent : m \notin handled /\ (pos[m] > 0 \/ m \in inbox)}
  /\ inbox' = {}
  /\ UNCHANGED <<goodbyes, deaths, dispDown, txLen, cursor, reqPos, recCursor, sent, pos, handled,
                 dropped, gameVars, n, lastEmit, switchN>>

\* CloseOut is the window's.  SwitchRecord and Relaunch are the tile reading the killed record: no
\* Dispatcher needed (seat_loop.sh, intile_claim).
Dispatcher == CloseOut \/ Check \/ WriteRecord \/ Fence \/ KillOk \/ KillSurvives
              \/ SwitchRecord \/ Relaunch \/ DispatcherRestarts \/ Respawn

(*************************** the pilot driving the game ***************************)

Pilot(d) == cst[d] = "live" /\ holds[d] /\ lock = d
Starting(d) == Pilot(d) /\ (~ownerHome \/ Bug("ignore_owner"))
Queued == {c \in Cands : cand[c] = "queued"}
Step(d) == yieldSteps' = IF ownerHome /\ lock # "owner" THEN yieldSteps + 1 ELSE yieldSteps

Take(d) ==
  /\ cst[d] = "live" /\ ~holds[d] /\ ~ownerHome
  /\ \/ lock = "none"
     \/ lock \in Ctx /\ ~Alive(lock)            \* a dead holder's tag is stale
  /\ lock' = d /\ holds' = [holds EXCEPT ![d] = TRUE]
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, cand, testBy, ownerHome, yieldSteps, crashes, reloads, ruleOpen, n,
                 ruleN, reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

HotApply(d, c) ==
  /\ Starting(d) /\ cand[c] = "queued" /\ Class[c] = "hot" /\ game = "up" /\ loaded # Sha[c]
  /\ deployed' = Sha[c] /\ loaded' = Sha[c]
  /\ Step(d)   \* no Emit: with it FixedSafety outgrew 480 s; S6 here rests on Pilot(d) needing a live context
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, lock,
                 holds, cand, testBy, ownerHome, crashes, reloads, ruleOpen, n, ruleN, reloadN,
                 prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

StopGame(d) ==
  /\ Starting(d) /\ game = "up" /\ \A c \in Cands : testBy[c] = "none"
  /\ \E c \in Queued : Class[c] = "cs" /\ deployed # Sha[c]
  /\ game' = "down" /\ loaded' = "none"
  /\ Step(d)
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, deployed, lock,
                 holds, cand, testBy, ownerHome, crashes, reloads, ruleOpen, n, ruleN, reloadN,
                 prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

Deploy(d, c) ==
  /\ Starting(d) /\ cand[c] = "queued" /\ Class[c] = "cs" /\ deployed # Sha[c]
  /\ game = "down" \/ Bug("deploy_live")
  /\ deployed' = Sha[c]
  /\ Step(d)   \* no Emit: with it FixedSafety outgrew 480 s; S6 here rests on Pilot(d) needing a live context
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, loaded,
                 lock, holds, cand, testBy, ownerHome, crashes, reloads, ruleOpen, n, ruleN,
                 reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* The burden of proof: the reload rule is written to the log before the reload.
LogRule(d) ==
  /\ Starting(d) /\ game = "down" /\ ~ruleOpen /\ Queued # {} /\ reloads < MaxReloads
  /\ ~Bug("silent_reload")
  /\ ruleOpen' = TRUE /\ Emit(d) /\ ruleN' = n + 1
  /\ Step(d)
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, lock, holds, cand, testBy, ownerHome, crashes, reloads, reloadN,
                 prevReloadN, reloadRuleN, switchN, verdicts>>

Launch(d) ==
  /\ Starting(d) /\ game = "down" /\ Queued # {} /\ reloads < MaxReloads
  /\ ruleOpen \/ Bug("silent_reload")
  /\ game' = "up" /\ loaded' = deployed /\ reloads' = reloads + 1 /\ ruleOpen' = FALSE
  /\ Emit(d) /\ prevReloadN' = reloadN /\ reloadN' = n + 1 /\ reloadRuleN' = ruleN
  /\ Step(d)
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, deployed, lock,
                 holds, cand, testBy, ownerHome, crashes, ruleN, switchN, verdicts>>

StartTest(d, c) ==
  /\ Starting(d) /\ cand[c] = "queued" /\ game = "up" /\ loaded = Sha[c]
  /\ cand' = [cand EXCEPT ![c] = "testing"] /\ testBy' = [testBy EXCEPT ![c] = d]
  /\ Step(d)
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, lock, holds, ownerHome, crashes, reloads, ruleOpen, n, ruleN, reloadN,
                 prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* A verdict re-reads the loaded sha; a game that died or moved under the test gives `invalid`.
Verdict(d, c) ==
  /\ Pilot(d) /\ cand[c] = "testing" /\ testBy[c] = d
  /\ IF (game = "up" /\ loaded = Sha[c]) \/ Bug("verdict_stale")
       THEN /\ cand' = [cand EXCEPT ![c] = "resolved"]
            /\ verdicts' = verdicts \cup {<<Sha[c], loaded>>}
       ELSE /\ cand' = [cand EXCEPT ![c] = "invalid"]
            /\ UNCHANGED verdicts
  /\ testBy' = [testBy EXCEPT ![c] = "none"]
  /\ Emit(d)
  /\ Step(d)
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, lock, holds, ownerHome, crashes, reloads, ruleOpen, ruleN, reloadN,
                 prevReloadN, reloadRuleN, switchN>>

\* Out of reload budget with the game down: park what is left instead of waiting forever.
Park(d, c) ==
  /\ Starting(d) /\ cand[c] = "queued" /\ game = "down" /\ reloads = MaxReloads
  /\ cand' = [cand EXCEPT ![c] = "parked"]
  /\ Step(d)
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, lock, holds, testBy, ownerHome, crashes, reloads, ruleOpen, n, ruleN,
                 reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

\* His return: the pilot parks its queue at the test boundary and frees the game. A live context
\* that does not hold the game (a fresh pilot that woke after he came back) parks the queue too.
Yield(d) ==
  /\ cst[d] = "live" /\ ownerHome /\ ~Bug("ignore_owner")
  /\ holds[d] => lock = d
  /\ \A c \in Cands : testBy[c] # d
  /\ holds[d] \/ (Queued # {} /\ ~Bug("no_park"))
  /\ cand' = [c \in Cands |-> IF cand[c] = "queued" /\ ~Bug("no_park") THEN "parked" ELSE cand[c]]
  /\ lock' = IF holds[d] THEN "none" ELSE lock
  /\ holds' = [holds EXCEPT ![d] = FALSE]
  /\ UNCHANGED <<hp, goodbyes, deaths, dispDown, cst, txLen, cursor, reqPos, recCursor, msgVars, game, deployed,
                 loaded, testBy, ownerHome, yieldSteps, crashes, reloads, ruleOpen, n, ruleN,
                 reloadN, prevReloadN, reloadRuleN, lastEmit, switchN, verdicts>>

Driver(d) == \/ Take(d) \/ StopGame(d) \/ LogRule(d) \/ Launch(d) \/ Yield(d)
             \/ \E c \in Cands : HotApply(d, c) \/ Deploy(d, c) \/ StartTest(d, c)
                                 \/ Verdict(d, c) \/ Park(d, c)

System == Dispatcher \/ \E m \in Msgs : HandleOld(m) \/ HandleNew(m)
          \/ \E d \in Ctx : Driver(d) \/ OwnerTakes

Death == OldDiesAlone \/ DispatcherDies \/ WakeDies     \* environment: never fair

Next == Env \/ System \/ Death

Spec == /\ Init /\ [][Next]_vars
        /\ WF_vars(Dispatcher)
        /\ \A d \in Ctx : WF_vars(Driver(d))
        /\ \A m \in Msgs : WF_vars(HandleOld(m)) /\ WF_vars(HandleNew(m))
        /\ WF_vars(OwnerTakes)

(*************************** properties ***************************)

TypeOK ==
  /\ hp \in {"none", "closeout", "pending", "checked", "recorded", "fenced", "killed",
             "switched", "done", "cancelled", "failed", "orphaned", "wake_dead", "respawned"}
  /\ cst \in [Ctx -> {"none", "live", "closing", "idle", "dead"}]
  /\ sent \subseteq Msgs /\ handled \subseteq sent /\ inbox \subseteq Msgs
  /\ game \in {"up", "down"} /\ deployed \in Shas /\ loaded \in Shas \cup {"none"}
  /\ lock \in Ctx \cup {"none", "owner"}
  /\ cand \in [Cands -> {"future", "queued", "testing", "lost"} \cup Done]

\* S1: at most one live context (driver window / arm target) per lane, and at most one of them
\* believing it drives the game.
S1 == /\ Cardinality({c \in Ctx : Alive(c)}) <= 1
      /\ Cardinality({c \in Ctx : Alive(c) /\ holds[c]}) <= 1

\* S2: no verdict for sha X while the game has sha Y loaded.
S2 == \A v \in verdicts : v[1] = v[2]

\* S3: no C# deploy while the game process lives (a running game holds what is deployed).
S3 == game = "up" => deployed = loaded

\* S4: every reload is preceded by a logged rule, one rule per reload.
S4 == reloadN = 0 \/ (prevReloadN < reloadRuleN /\ reloadRuleN < reloadN)

\* S5: no owner message and no queued candidate is lost across a handoff.
S5 == lost = {} /\ dropped = {} /\ \A c \in Cands : cand[c] # "lost"

\* S6: no event and no push from a context after its switch timestamp.
S6 == \A c \in Ctx : switchN[c] = 0 \/ lastEmit[c] <= switchN[c]

\* L2's bound, checked as safety: after his return the pilot takes at most YieldBound steps
\* before the game is freed.
L2Bound == yieldSteps <= YieldBound

\* L1: every candidate is eventually resolved, marked invalid or parked.
L1 == \A c \in Cands : cand[c] = "queued" ~> cand[c] \in Done

\* L2: his return frees the Archmagi game.
L2 == ownerHome ~> lock = "owner"

\* L3: every message he sends is eventually answered, or read by a live window that can answer it.
L3 == \A m \in Msgs : m \in sent ~> (m \in handled \/ (m \in inbox /\ cst["new"] = "live"))

\* Witnesses, each expected VIOLATED: the instrument can see what the dispatcher case passes on.
NoDeath == deaths = 0
\* A wake recovered a message while the Dispatcher was still dead.
NoTileRecovery == ~(dispDown /\ hp = "done" /\ inbox # {})
=============================================================================
