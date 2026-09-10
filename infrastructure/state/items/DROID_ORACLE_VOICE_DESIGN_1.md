## spec
Design (dormant, per `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0 card 14 / §3.4 E5) for
four droid Oracle consumers — the wipe reaction (W), the bolt-removal moment (B),
a wild droid's offer (O), a long-unwiped droid's "I remember" (R) — written at the
rigor of the one built consumer (Ohm: `OracleRegisterBlocks.cs` block +
`OracleValidator.cs` lint). Doc: `design/RimMandrake/droid_oracle_voice_design.md`.

**"Dormant" is the owner's ruling, not a backlog state**: design it, do not build
it. The only thing that un-parks it is his read of the doc. The live path also
waits on the E2 (`DROIDWORKS_SERVICE_RECORD_DRIFT_1`) and E4
(`DROIDWORKS_WILD_DROIDS_1`) hook points, unbuilt; W and B have built hooks.

Resolved in the doc: the speaker is the DROID itself, first person, in a chassis
register carried as a slot (seven `chassisClass` families + Primitive),
tier-gated (mindless/blank never fire; all sapient until B1) — not the Narrator,
not Ohm, whose droid-online hook stays a separate gods-bucket call. Ships a
`DroidLaw` sibling of `Law`, a shared `TryValidateDroid` lint (Cradle tells reused
+ droid identity/mechanism/meta tells + an invented-person check against the
map's pawn names), and per consumer: trigger, block, slots, 3 prescribed
fallback lines, a `TryValidate*` contract.

**Transport is the built `OracleClient.cs`** (`claude -p`, ef628781, re-verified
d9b909c8) — reconciled 2026-09-09 in doc §2.6: system pieces ride
`--system-prompt`, slots ride stdin; the seven-rung failure ladder (kill switch,
bucket, binary missing, timeout, non-zero exit, empty stdout, lint reject) each
ships the prescribed line via `DeliverFallback`; worst-case wall time is
2 × `timeoutSeconds`; a scribed pending list covers save-during-call; one droid
call in flight at a time, never queued; the child's tool sandbox protects the
install, not the text. Design only — no C#, no defs, nothing deployed.

## verify
Design item — nothing runs until un-dormanted; the owner's read is the gate.
When it IS built, the seam that proves every consumer **with and without the
LLM** is already in the shipped mod: `OracleSettings.claudeCliPath`. Point it at
a stub and the real CLI, network and login are never involved. Per consumer
(W and B on their built recipes; O and R on their E4/E2 hooks when those exist):

**Without the LLM** — each rung of doc §2.6's ladder, once, expecting the
prescribed line as the letter body and the named reason in Player.log
(`RimMandrake.Oracle: falling back for "<label>" -- <reason>`):
1. `enabled` off → fire the moment → prescribed line, `kill switch off`.
2. `enabled` on, `claudeCliPath` = a path that does not exist → prescribed line,
   `call failed: could not start …`; confirm Player.log shows ONE attempt (no retry).
3. `claudeCliPath` = a stub that sleeps past the timeout (slider at 5 s) →
   prescribed line, `call failed: … timed out after 5s`, ONE attempt, and no
   orphan `claude`/stub process left behind (Task Manager or `tasklist`).
4. stub that exits 1 → prescribed line, `exited 1`, TWO attempts in the log.
5. stub that exits 0 with empty stdout → prescribed line, `produced no output`.
6. stub that echoes a line carrying a per-consumer tell (W: `I remember`; B at
   band high: `thank you`; O: `silver`; R: a text with no anchor) → prescribed
   line, `validator rejected: <reason>`.
7. save-and-quit while a slow stub is in flight, reload → the prescribed line
   arrives on load with reason `pending across load` (doc §2.6).
8. two moments fired inside one stub's window → the second ships prescribed at
   once with `droid call already in flight`.
Also the offline selftest: `TryValidateDroid` + the four `TryValidate*` against
canned strings, explicit N/N, the Ohm pattern (`jawa/oracle_selftest` shape).

**With the LLM** — stub that echoes a clean, in-register line → that line is the
letter body, no fallback log line. Then, once only, the real binary: `enabled`
on, `claudeCliPath` blank, fire W on a quicktest droid; the letter body is
generated, first person, passes the lint, arrives within 2 × timeout. The stub
proves the mechanism; the real call proves only that the machine is logged in.

Owner reads the doc first: §1 who-speaks, §2.5 budget, §2.6 transport, §7 what
was left out.

## criteria
- [x] 4 consumers, each with trigger, speaker+register, block, slots, fallbacks, lint contract.
- [x] Every trigger tied to a built hook or explicitly "hook point TBD" naming the packet that builds it — no invented C# hooks.
- [x] Each lint contract concrete enough to write `TryValidateX` from (tells, bands, whitelists, caps), and each distinct from Ohm's.
- [x] Prescribed fallback text that ships AS-IS with zero LLM calls (3 lines per consumer, slot-substituted).
- [x] Law #1 (text authority only) and Law #2 (game whole with the LLM absent) hold on every path; one block per call, never a blended cast.
- [x] Transport reconciled against the BUILT client, not an assumed one: every failure the client can raise is named with its fallback; no stale "blocked on the rewrite" line remains.
- [x] A verify protocol that proves each consumer with and without the LLM using only the shipped `claudeCliPath` seam — no network, no login, no real model needed for the mechanism.
- [ ] Owner review — the only gate on this item; nothing closes it but his read.

## Open questions for the owner
Only he can rule these; the doc takes a position on each so his answer is a
yes/no, not a blank.
1. **Who speaks.** Doc §1 derives "the droid, first person" from existing rulings
   (firmware personalities v1, the First Speaker, the bolt as a mute). That is an
   inference, not a card. Confirm, or rule the Narrator instead.
2. **Droid budget unit and number.** He rejected per-game-day for the gods; the
   doc proposes a separate `droids` bucket at 2 per real-world hour. His number.
3. **Latency.** A letter may land up to 2 × timeout (≈2 min default) after the
   moment. Accept, or set a tighter droid-only timeout with no retry (30 s?).
4. **Register table (§2.2).** Eight one-line tone choices. The two that most need
   his ear: Battle (comically bad threat assessment) and Power (the gonk syllable).
5. **Which of the four earn the LLM at all.** R is the only consumer allowed a
   past and the only one whose worst failure (a hallucinated life) no regex can
   catch. Ship W/B/O live and keep R prescribed-only, or all four.
6. **Programmable tier.** Doc fires the consumer in a flat status register with
   one crack. Simpler alternative: programmable never fires. His call.
7. **Prescribed lines now, ahead of un-dormanting?** W and B have built hooks;
   their three fallback lines each could ship today as a letter with no Oracle
   involvement at all. That is a scope question for him, not a design one.
