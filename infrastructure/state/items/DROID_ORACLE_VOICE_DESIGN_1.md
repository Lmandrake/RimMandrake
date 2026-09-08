## spec
Design (dormant, per `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §0 card 14 / §3.4 E5) for
four droid Oracle consumers — the wipe reaction, the bolt-removal moment, a wild
droid's offer, a long-unwiped droid's "I remember" — written at the rigor of the
one built consumer (Ohm: `OracleRegisterBlocks.cs` block + `OracleValidator.cs`
lint). Doc: `design/RimMandrake/droid_oracle_voice_design.md`. Resolved there:
the speaker is the DROID itself, first person, in a chassis register carried as a
slot (seven `chassisClass` families + Primitive), tier-gated (mindless/blank never
fire; all sapient until B1) — not the Narrator, not Ohm, whose droid-online hook
stays a separate gods-bucket call. Ships a `DroidLaw` sibling of `Law`, a shared
`TryValidateDroid` lint (Cradle tells reused + droid identity/mechanism/meta
tells + an invented-person check against the map's pawn names), and per consumer:
trigger, block, slots, 3 prescribed fallback lines, a `TryValidate*` contract.
Design only — no C#, no defs, nothing deployed. Transport assumed only as "prompt
in, text out, or nothing"; the live path is blocked on `ORACLE_EXPERIMENT_SPIKE_1`'s
`claude -p` rewrite; the fallbacks need no LLM at all.

## verify
Owner reads the doc. Design item — nothing runs. Points to look at first:
- §1 the who-speaks ruling and its four reasons (the bolt hediff really does cap
  `Talking` at 0 — `HediffDefs_Droidworks.xml` — so §4 is the first word back).
- §2.5 budget: unit and number are his (he already rejected per-game-day).
- §5/§6 hook points marked TBD (E4 wild-droid incident, E2 service record are
  unbuilt); §3/§4 hooks are the built `Recipe_DWMemoryWipe.ApplyOnPawn` and
  `Recipe_RemoveRestrainingBolt.ApplyOnPawn`.
- §7 what was deliberately left out (no Narrator coda, no god blend).

## criteria
- [x] 4 consumers, each with trigger, speaker+register, block, slots, fallbacks, lint contract.
- [x] Every trigger tied to a built hook or explicitly "hook point TBD" naming the packet that builds it — no invented C# hooks.
- [x] Each lint contract concrete enough to write `TryValidateX` from (tells, bands, whitelists, caps), and each distinct from Ohm's.
- [x] Prescribed fallback text that ships AS-IS with zero LLM calls (3 lines per consumer, slot-substituted).
- [x] Law #1 (text authority only) and Law #2 (game whole with the LLM absent) hold on every path; one block per call, never a blended cast.
- [ ] Owner review — the only gate on this item; nothing closes it but his read.
