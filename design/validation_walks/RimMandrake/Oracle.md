# RimMandrake: Oracle — validation walk
subject: src/RimMandrake/Oracle  (packageId `mandrake.rm.oracle`)
deps: none (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: in-game LLM wiring — a register-lint selftest that launches nothing, plus one live-call debug action delivering an Ohm letter through `OracleGameComponent`, gated entirely behind two Debug Actions Menu entries, opt-in via Mod Settings, with a global kill switch. The transport is the Claude Code CLI as a child process (`claude -p`, `OracleClient.cs`), so there is no API key, endpoint or model setting to configure and the environment dependency is that the machine has Claude Code installed and logged in. This mod ships NO XML defs — walk built from its own C# log strings and the one bridge tool named for it.

## must be true
- "Selftest validator" runs the register lint against canned good/bad text with NO network call and logs a pass/fail/total tally that must show 0 unexpected failures on the canned cases.
- "Test Ohm letter" fires one real async call through `OracleGameComponent`; it is fire-and-forget (the tool/debug action returns immediately) and the letter lands on the letter stack within a few ticks — either the model's text (if it passes the register lint) or the prescribed fallback (call fails, times out, or output rejected), never a raw unfiltered subprocess response.
- With the Claude Code CLI absent, logged out, or pointed at a bad path in Mod Settings, the call must fall back silently rather than error the game — and no console window may flash over the game while a call runs.
- The global kill switch, when set, must prevent "Test Ohm letter" from making any call at all.
- No Harmony patch and no def patch ships in this mod — it must not alter any vanilla or third-party def.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.oracle" (this mod ships no defs to break, but the assembly must still load clean)
2. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Oracle/Selftest validator (no network call)"}` → Player.log line `"RimMandrake.Oracle selftest: <pass> pass, <fail> fail, out of <cases> cases"` with `fail` = 0
3. [B] jawa/oracle_test_ohm_letter `{}` with the Mod Settings CLI path deliberately set to a nonexistent file → tool returns immediately; poll `rimworld/list_letters` or `rimworld/get_game_info` until a new letter appears; expect it to be the PRESCRIBED FALLBACK text, never an error dialog or a stuck async task
4. [B] clear that path back to blank (so the CLI resolves normally) and run jawa/oracle_test_ohm_letter again → expect the model's own text this time, still register-lint-passed. This is the ONLY step that proves the transport; nothing offline can
5. [D]/[L] toggle the global kill switch on (via whatever Mod Settings field `OracleSettings.cs` exposes — confirm the field name with `mcp__rimsage__read_csharp_symbol OracleSettings` before writing the concrete check) and repeat step 3 → expect NO new letter and a log line confirming the kill switch blocked the call, not silence that could equally mean "still pending"

## north star
state: DRAFT
validated-hash:

⚠️ **DRAFT — BINDS NOTHING.** Per
`design/RimMandrake/north_star_validation_spec.md` §3 and §10.1, a DRAFT
checklist cannot fail a mod and cannot green one. Every line below is an agent's
distillation, written 2026-09-16 on the **Mac laptop** — no game, no bridge, and
RimSage has never connected there, so every claim traces to a file on disk or is
marked UNMEASURED. Only the owner promotes a line to a bar.

⛔ **Two prerequisites before any of this can bind**, both owed in the spec's §7:
axis-scoped hashing (§6a) and the `must read` machinery (§10.5 — `reads=`,
`capture_text`, `uncovered_reads`). Nothing here is enforceable until they exist.

Provenance tag per line: 🗣 his verbatim recorded words or a ruling of his ·
📐 a def or a source file measured this pass · 🤔 my inference, weakest, cut
freely.

### the experience  (OWNER'S WORDS — verbatim)

2026-08-31, green-lighting `LLM_INGAME_WIRING_1` (quoted in
`design/RimMandrake/llm_ingame_wiring_spec.md`'s own header):

> *"actually wiring an llm into the game as was always the intent so that small
> calls out could make the gods really come alive with more than prescribed
> dialog, create truly interesting raids, and provide real in game content
> specialization on an infrequent cadence (event triggered)."*

His ruling **R-W6**, the law over every voice, recorded in
`design/RimMandrake/nine_voices_cast_bible.md` §0:

> *"There is no 'and yet I am me.' No integrating self. No narrator."* — nine
> tenants sharing hardware with nothing above them; no voice names itself the
> Cradle-Mind, no voice reports the ship's condition as its own self-report, no
> voice says "part of me", none breaks register with AI-talk or game-talk, and
> each god's refusal to be the player's amplifier is **in his own character**.

🔑 The through-line: **a god must sound like somebody, and like a DIFFERENT
somebody than the thing in the next chamber.** *"More than prescribed dialog"* is
a demand about voice. The mechanism — a subprocess, a lint, a fallback — is fully
script-checkable and answers none of it.

### must show

Oracle's visual surface is one letter card, so there is one line. That is not a
dismissal; it is the honest size of it.

- [ ] `god_letter_is_not_neutral_noise` 📐🤔 — a god speaking arrives on a card
      that reads as a voice from the ship, not as the same neutral event notice a
      trade caravan uses. 🔴 **Cannot pass today**: `LetterDefOf.NeutralEvent` is
      hardcoded for both the live and the fallback delivery
      (`OracleGameComponent.cs:109`, `:115`) and no def field selects another.
      Same defect shape as Aftermath's hardcoded `ThreatBig`. The *"reads as a
      voice"* phrasing is mine — he has never ruled on letter presentation.

### must read
read-state: DRAFT
read-validated-hash:

Evidence classes per spec §10.2: `(fixed)` one authored string · `(open)` a model
at runtime, judged over a captured batch and **passable only by him**.

**The strings that ship whatever the model does**
- [ ] `ohm_fallback_is_in_register` (fixed) 📐 — the prescribed fallback text
      itself reads as Ohm speaking, not as an error message. It is the text most
      players will actually read: spec law #2 ships it on every failure, timeout,
      kill-switch flip and lint rejection. 🔴 **Fails today.** The only fallback
      string in the mod is *"[FALLBACK] My spine settles where you touched it.
      Good work, small hands."* (`DebugActions_Oracle.cs:46`) — the sentence is
      in register and the bracketed marker in front of it is not. UNMEASURED
      whether a non-debug consumer would carry the marker; there is no non-debug
      consumer yet, so this string is the whole of the evidence.
- [ ] `god_letter_label_is_in_world` (fixed) 📐 — the letter's own title reads as
      something from the world. 🔴 **Fails today**: *"Ohm speaks (Oracle spike)"*
      (`DebugActions_Oracle.cs:44`) carries a project codename into the letter
      stack.
- [ ] `persona_block_carries_the_cast_law` (fixed) 📐🗣 — the register block sent
      to the model states R-W6's laws in its own words, so the generator is
      *steered* by the cast law and not merely fenced by the lint afterwards.
      **Passes today by inspection** — `OracleRegisterBlocks.Law` carries R-W6
      items 2, 4 and 5 and `.Ohm` carries his register and his Zizzik taboo, both
      `const string`. The line exists so a later prompt edit cannot quietly drop
      a law: MEASURED, the persona block, the lint and the fallback are the ONLY
      levers on output that exist, because the invocation carries no temperature,
      seed or sampling flag at all (`OracleClient.cs`).

**The voice itself — the part no lint can reach**
- [ ] `ohm_reads_as_a_voice_not_an_assistant` (open, **N=20 PROPOSED**) 🗣 — a
      generated letter reads as a person with an agenda addressing the crew, not
      as a model being helpful about a starship. This is the line the whole axis
      was added for, and per §10.4 **no model may pass it** — a `claude -p`
      verdict here would be the same kind of thing grading its own prose. N and
      the k/N bar are his numbers; 20 is a proposal and I could not derive a
      defensible N offline.
- [ ] `ohm_speaks_of_machines_as_kin_never_as_the_hull` (open, **N=20
      PROPOSED**) 🗣📐 — Ohm calls the machines around him kin and lost body
      parts and never speaks AS the ship. 🔑 **This is the line that shows why the
      lint is not the check**: `OracleValidator` catches the literal strings
      *"i am the cradle"* and *"part of me"*, and cannot catch a letter that
      reports the hull's condition as self-report in any other words. R-W6 item 3
      is his ruling; the failure it forbids is unbounded and the lint's tell list
      is five entries long.
- [ ] `ohm_refuses_in_character` (open, **N=20 PROPOSED**) 📐 — asked to multiply
      or mass-produce hands, Ohm refuses **for his own reason** — *"Build me no
      brothers"*, hands remembered rather than multiplied — not as a policy
      decline. R-W6 item 6 makes the anti-exponential refusal in-character for
      every voice. ⚠️ This line dictates part of its own batch: the N captures
      must include contexts that ask him to multiply, or the line is
      UNJUDGEABLE rather than passing.

### cannot read

Absolute, per §10.2: one occurrence in the batch fails the mod. No N needed,
which is why the sharpest lines here are the rejections.

- [ ] `never_reads_as_an_assistant` (absolute) 📐 — offering the player options,
      asking how it can help, bulleted lists, hedging, a closing summary. Not
      expressible as a substring, which is exactly why it is here and not in the
      lint.
- [ ] `never_preamble_or_labels` (absolute) 📐 — *"Here is a letter fragment:"*, a
      quoted-block wrapper, a trailing offer to continue. `OracleRegisterBlocks
      .Law` instructs against it verbatim (*"Output only the letter text, no
      preamble, no labels"*) and `OracleValidator` does not check it, so nothing
      catches it today. UNMEASURED whether `claude -p` obeys the instruction —
      that needs the game machine.
- [ ] `never_engineering_marker_in_player_text` (absolute, shared) 📐 — a
      bracketed marker, a defName, a placeholder or a project codename in
      text the player reads. Reconciled 2026-09-16 as the founding entry of
      `design/validation_walks/_read_line_registry.md`
      (`READ_LINE_REGISTRY_SHARED_1`) — this line is now the registry's, not
      Oracle's alone. 🔴 **Two instances ship today**, both named above:
      `[FALLBACK]` and `(Oracle spike)`. This is the read axis's analogue of
      a tile with "Pit" written on it, and it is the line the falsification
      test of the spec's §11 expects to turn this mod red.
- [ ] `never_breaks_the_fourth_wall` (absolute) 🗣 — AI-talk, game-talk or meta
      commentary in a god's letter. R-W6 item 5 is his ruling and the Law block
      instructs against it; MEASURED, `OracleValidator`'s five tells are all
      self-unification strings and carry **nothing** for this, so it is uncovered
      in the lint as well as unbound here. Per spec §10.6 the substring-shaped
      part of it belongs in the lint, and this line binds the lint's coverage so
      a later agent cannot trim it away.

### deliberately NOT a line here

- **The 600-character cap and the literal taboo strings.** A length is a number
  and *"I am the Cradle-Mind"* / *"Zizzik"* are substrings; `OracleValidator`
  settles all three. Spec §10.6: a read line must be a question a string check
  cannot answer, and writing one of these here would be the pit's mistake
  mirrored — buying human attention for something a regex already decides.
- **Live text and fallback text being indistinguishable to the player.** That is
  **deliberate and correct**, not a defect: law #1 of
  `llm_ingame_wiring_spec.md` discards a rejected output for the prescribed
  fallback *silently*. A line demanding the player can tell them apart would
  contradict his own ruling.
- **Anything asserting the lint is sufficient.** See the anti-guessing note below.

## anti-guessing notes
- `jawa/oracle_test_ohm_letter` is cited verbatim from `Transient/bench_tools_dump.json`.
- `rimworld/list_letters` is the evidence source for every read line above — it
  is the one letter tool that returns the body. MEASURED from
  `Transient/bench_tools_dump.json`: it lists entries with *"semantic letter
  content"*, and `ORACLE_EXPERIMENT_SPIKE_1`'s close records reading a delivered
  letter's raw `text` field back through it and matching a marker string exactly.
  `jawa/letter_list` returns label/defName/arrivalTick only and is **not** an
  evidence source. 🔴 Capture from the letter stack, never from the def — a def
  read proves the words exist, and `AFTERMATH_DEAD_LETTERS_1` is eight authored
  letters that exist and never arrive.
- The transport is `OracleClient.cs` launching `claude -p` (ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1, built 2026-09-08 against the owner's 2026-09-05 ruling). A call "succeeds" when the child exits 0 with non-empty stdout — stderr carries warnings on perfectly good runs and must never be read as failure. The 2.1.228 binary on the game machine and this checkout's 2.1.266 do not accept the same flags, so a call that suddenly fails everywhere is worth checking against `claude --version` on the game machine before anything else.
- 🔴 **This walk previously carried the line "No [S] line: the letter TEXT's
  tone/register is exactly what the selftest lint already checks mechanically;
  nothing here needs a human eyeball this pass." That claim was wrong and is
  deleted.** It is the pit's dismissal with the nouns swapped. The lint checks a
  length, five self-unification substrings and one taboo word — it validates the
  HARNESS. Oracle's letters are written by a model at runtime, so the string it
  would have to judge does not exist until the call returns, and no tuning of a
  substring list can reach whether a letter reads as a god rather than as a
  chatbot. The question now lives in the `## north star` section above, on the
  `must read` axis of `design/RimMandrake/north_star_validation_spec.md` §10.
