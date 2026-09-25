# FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1 — feral-race crash-survivor pawnkind, permanent mental-scar hediff, capture-to-slave wiring

## what

`fall_line.md` §8b's "normally sentient races gone feral" beat: humanlike crash
survivors who have been out on the Fall Line long enough to go feral — captured
(never killed outright, per the biome's own "hunting ground, not a battlefield"
framing) and converted to a slave carrying a **permanent** mental-scar hediff, as
opposed to the feral droids' clean memwipe-restores-them-whole path. This is
`COMMISSION_LEDGER_CLEANUP_1`'s `fall_line:feral-races-crash-survivors-pawnkind-
permanent-mental-scar-h` slug, re-filed as its own build item — genuinely new C#,
not a def+art commission.

`rosters/fall_line.json`'s `new_defs` row is explicit:

> *"feral races (crash survivors: pawnkind + permanent mental-scar hediff + capture→
> slave wiring)"* — `mechanic_load`: **"C#, ours (no donor ships capturable feral
> sentients) — §8b verbatim ruling"**

## why re-filed rather than built inline

- **Explicitly excluded from the sibling mechanism item.** `FALL_LINE_ARRIVAL_
  MECHANISM_1` (filed by BENCH 2026-09-20, state proposed, unclaimed — covers the 15
  ambient-pulled species: ship-vermin, feral droids, the joke rat) says outright, in
  its own spec (`design/RimUtinni/fall_line_arrival_mechanism_spec.md` line 305):
  *"Feral RACES (§8b's 'normally sentient races gone feral') — not in this item's 15;
  the flee think-tree and lurker comp are written species-agnostic so they carry over.
  Capture-to-slave with the permanent mental-scar hediff is its own item."* No item
  existed for that "its own item" as of this pass (checked `infrastructure/state/
  items/` and `items/closed/` for `feral`/`crash`/`survivor` — nothing) — this item is
  that filing.
- **New C# on the critical path**, per the roster's own mechanic_load: a new
  PawnKindDef (humanlike, factionless, feral), a permanent HediffDef (mental scar —
  deliberately NOT removable the way the droids' `RUT_Hediff_Feral` is by the memwipe
  recipe; §8b's whole point is that this path is NOT clean), and capture→slave
  conversion wiring (vanilla already has a slave-capture pipeline via `RecruitUtility`/
  the ideology enslavement path — needs verifying which hook fires the hediff-apply
  rather than assumed).
- **Reuses work that is NOT yet built.** The species-agnostic flee/lurker think-tree
  insert (`RUT_FeralDroidInsert`/`JobGiver_FeralFlee`/`JobGiver_FeralLurk`,
  `fall_line_arrival_mechanism_spec.md` §5.2) that this item's own crash-survivor
  behaviour should reuse for its "wily, flee-prone until cornered" beat does not exist
  in code yet either — it ships with `FALL_LINE_ARRIVAL_MECHANISM_1`. **This item is
  blocked on that one landing first** (or must duplicate a smaller version of the same
  insert, which would fork the mechanism in two places — not preferred).

## work owed

1. Confirm `FALL_LINE_ARRIVAL_MECHANISM_1`'s Band B flee/lurker think-tree insert has
   landed (or build a minimal species-agnostic version if this item goes first —
   coordinate rather than duplicate).
2. Author the crash-survivor PawnKindDef: humanlike, factionless (`Faction == null`,
   same "no goodwill hit on death/capture" carve-out the droids get per §8b), backstory/
   flavor reading as "gone feral out here," reusing the flee-then-fight-when-cornered
   behaviour from (1).
3. Author the permanent mental-scar HediffDef — stays on the pawn through capture and
   conversion (contrast the droids' `RUT_Hediff_Feral`, which the memwipe recipe
   removes cleanly). Read the vanilla enslavement/mental-break hediff shapes
   (`RimSage read_csharp_symbol`) before inventing fields from scratch.
4. Wire capture→slave: verify which vanilla hook (ideology enslavement recruitment,
   `RecruitUtility`, or a Harmony postfix on the capture path) is the right place to
   apply the hediff at the moment of conversion — UNMEASURED as of this filing.
5. Spawn route: rides the same wreck-arrival mechanism as Band B once (1) lands (a
   humanlike sibling to the feral-droid "breaks from the wreck" / "drifts in" routes),
   not a separate incident system.
6. Art: a crash-survivor pawn reuses existing humanlike apparel/body art (torn/scarred
   flavor via a coloring or worn-state modifier, not a wholly new race) — checked
   `infrastructure/artpipe/{done,pending}`/`registry.jsonl` for "feral survivor"/
   "crash survivor"/"fall line human" first, clean, nothing pre-existing; likely no new
   art commission needed at all if the pawnkind reuses a stock humanlike xenotype.

## verify

- `FALL_LINE_ARRIVAL_MECHANISM_1`'s Band B insert status checked before step 2 starts,
  not assumed either way.
- The capture→slave hook is verified against real engine code (RimSage or decompiled
  source), not guessed — this is exactly the "never guess a defName, field, or
  namespace" class of risk CLAUDE.md flags.
- New defs load clean under `validate_patch.py --live --defs`; `run_selftests.py`
  green after any C# lands.
- Mental-scar hediff is confirmed non-removable by the existing memwipe recipe (the one
  thing that must NOT be shared with the droid path, per §8b's own contrast).

## criteria

A capturable, factionless, feral-race crash-survivor pawn exists, can be captured and
converted to a slave carrying a permanent (non-memwipeable) mental-scar hediff, and
arrives on the Fall Line by the same wreck-arrival route Band B uses — built, or a
further owner ruling recorded if the design proves ambiguous once (1)-(4) above are
actually investigated.

## FOUNDRY investigation, 2026-09-24 — blocked, not built

Claimed, started, investigated, blocked (not closed) this pass. Findings, so the next
picker-up doesn't re-derive them:

- **`FALL_LINE_ARRIVAL_MECHANISM_1` has not landed** — still `state: file`, unclaimed,
  0 history events beyond its own filing. `grep -r "JobGiver_FeralFlee\|JobGiver_
  FeralLurk\|RUT_FeralDroidInsert" src/ design/` returns only the spec doc
  (`design/RimUtinni/fall_line_arrival_mechanism_spec.md`) — no C# exists.
- **The droid contrast case this item's spec leans on doesn't exist either.**
  `RUT_Hediff_Feral` (cited throughout this item and the arrival-mechanism item as the
  already-built "clean memwipe" path to contrast against) is NOT in `src/` — it appears
  only in two design docs (`fever_wood_kit_spec.md`,
  `fall_line_arrival_mechanism_spec.md`), never authored. RimSage's def index (live
  connection confirmed this session) also returns nothing for a `Feral` `HediffDef`.
  So there is no existing "clean" path to contrast the permanent scar against yet —
  both halves of the §8b beat are unbuilt.
- **Capture→slave hook, confirmed via RimSage against decompiled source** (item's step
  4, previously UNMEASURED): the vanilla enslavement path is
  `GenGuest.TryEnslavePrisoner(Pawn warden, Pawn prisoner)` in
  `Source/RimWorld/GenGuest.cs`, reached from `InteractionWorker_EnslaveAttempt` (the
  warden interaction) and `Toils_Interpersonal.TryEnslave`/`JobDriver_
  EnslaveOrReduceWillPrisoner` (the `WorkGiver_Warden_Enslave` job). A Harmony postfix
  on `GenGuest.TryEnslavePrisoner` is the correct hook to apply the mental-scar hediff
  at the moment of conversion — it fires exactly once, on the actual state transition,
  regardless of which of the two callers triggered it.
- **Per this item's own "why re-filed" section**, building the crash-survivor's
  flee-then-fight behaviour now means either (a) waiting on (1), which is unclaimed and
  itself carries open, undecided design shape ("wreck incident vs subregion landmark vs
  generator-driven equivalent" — not ruled), or (b) forking a duplicate mini think-tree
  insert, which the item explicitly says is "not preferred." Building the PawnKindDef,
  spawn route, or think-tree insert now would be exactly the fork this item warns
  against, so those steps were not built this pass.
- **Not blocked on the HediffDef or hook design in isolation** — those are recorded
  above as unblocked, real progress, ready to consume the moment (1) lands or is
  overridden. No C# was written this pass because the PawnKindDef/spawn-route half
  (which the HediffDef must be wired to for the criteria to be met) cannot land without
  the same prerequisite.

Blocking on `FALL_LINE_ARRIVAL_MECHANISM_1` rather than closing or forcing a fork.
