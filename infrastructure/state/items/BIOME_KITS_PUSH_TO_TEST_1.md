# BIOME_KITS_PUSH_TO_TEST_1 — push every biome mechanics kit toward test-readiness

## spec

Umbrella tracking item for a multi-wave push (started 2026-09-14, BENCH+FOUNDRY
sitting) to get every biome's mechanics kit as close to live-test readiness as
offline work allows. Individual per-biome work is tracked and verified in each
kit's own item — this item exists only so the overall push itself is a named,
findable thing rather than living only in a conversation transcript, per the
owner's "anything started together and not finished becomes a normal item"
rule when he steps away.

Scope, as agreed with the owner this sitting:
- Push into L-effort mechanics, not just the small/unblocked ones (Forge
  F3/F4, Miasma M2→M3, and whatever else surfaces).
- Roster-blocked creature content (tar beast, warden mother, etc.) stays as
  clearly-flagged PLACEHOLDER PawnKindDefs (an existing shipped kind, loudly
  commented) — do NOT author real creature content in this item's name. That
  stays the roster pass's job, per every kit spec's own stated scope line.
- Parallel fan-out (3-4 background agents at once) is fine. The shared
  `RM_EnvironmentalHazards.csproj`/assembly will keep producing git-index
  collisions between concurrent agents; that's been cheap to self-correct
  (a plain `git reset --soft` + re-stage) every time so far this session —
  keep doing that, don't slow down the pace to avoid it.
- Scarlands and Greentide get the same file+spike treatment as the other five
  kits (Forge/Scald/Miasma/Sump/RustCathedral already had it before this
  item existed).

Per-biome kit items (the actual tracked work):
`FORGE_MECHANICS_1`, `SCALD_MECHANICS_1`, `MIASMA_MECHANICS_1`,
`SUMP_MECHANICS_1`, `FEVER_WOOD_MECHANICS_1`, `RUST_CATHEDRAL_MECHANICS_1`,
`GREENTIDE_MECHANICS_2`, and (filed this same sitting) a Scarlands item.

## verify

- Each named kit item's own `## verify`/`## criteria` is satisfied as far as
  offline work can take it (spike pass done, build passes landed for every
  mechanic that isn't blocked on roster content, a shared/donor mod
  dependency, or a live quicktest).
- No kit item is closed by this item — closing is each kit's own call, once
  its own live/quicktest bar is met. This item is a coordination pointer,
  not a substitute for any kit's own verify line.

## criteria

Every biome kit that had a drafted spec as of 2026-09-14 has a filed,
started build item and at least one spike pass landed on `main`. Every
mechanic that is genuinely unblocked offline (not gated on roster content,
another kit's own unbuilt generic, or a live/bridge proof) has a build pass
landed. Remaining gaps (L-effort items still open, roster-gated content,
live-test debt) are named honestly in each kit's own item file, not hidden
here.

## status log

- 2026-09-14: item filed at the start of a multi-wave push. Waves so far
  (see each kit's own item for full detail): Forge spike+F1, Scald
  spike+S1/S2/S4/S6, Miasma spike+M1/M4/M5/M6, Sump spike+S1/S2/S5/S6/S3
  (scaffold), Greentide filed as `GREENTIDE_MECHANICS_2` + spike. In
  flight as of this entry: Forge F3/F4, Miasma M2, and filing+spiking
  Scarlands.

- 2026-09-14, later (owner AFK, BENCH stepped away, worked solo per
  "keep your queue filled"): pushed through to the following state.
  **Offline build passes are effectively exhausted for this push** — what
  remains everywhere is either roster/creature content this item's own
  scope explicitly excludes, an external design-only dependency
  (`EXPLOSIVE_PLANT_GROWTH_1`), a genuine unresolved design call
  (Fever Wood's marsh terrain), or live/quicktest proof needing bridge
  access nobody currently holds.

  - `FORGE_MECHANICS_1` — **F1–F6 all shipped.** Offline-complete.
  - `MIASMA_MECHANICS_1` — **M1–M6 all shipped.** Offline-complete.
  - `SUMP_MECHANICS_1` — **S1–S6 all shipped.** Offline-complete.
  - `SCALD_MECHANICS_1` — S1/S2/S4/S5/S6 shipped. S3 (margin fishing)
    still blocked on `FISH_BESTIARY_COMMISSION_1` (external, not this
    push's to close).
  - `SCARLANDS_MECHANICS_2` — §1 (mynock) already shipped elsewhere,
    §2–§5 wired this push. Offline-complete as far as this push's scope
    goes; `SCARLANDS_MECHANICS_1` (spec-only) superseded by this ID.
  - `GREENTIDE_MECHANICS_2` — M1, M2, M3 (vortex), M4, M5, M6, M7, M8,
    M9, M11, M12 all shipped this push or found already shipped
    elsewhere. Only M10 remains, externally blocked on
    `EXPLOSIVE_PLANT_GROWTH_1` not existing yet. One small loose end:
    M3's steam devil isn't yet wired to spawn rarely from the Roil
    condition (M4) — both landed in the same wave and the hook was left
    honestly unbuilt rather than guessed at; small, safe pickup for
    whoever's next. `GREENTIDE_MECHANICS_1` (spec-only, closed) superseded
    by this ID.
  - `FEVER_WOOD_MECHANICS_1` — F1–F4, F6, F7 shipped (F6/F7 unblocked
    mid-push once Greentide's M9/M12 landed, and consumed them as the
    first real customer — confirms that generic surface actually works).
    F5 (ground-refusal terrain) needs a real design call — a new
    biome-specific marsh TerrainDef — against the FROZEN sheet's own
    terrain table; deliberately not guessed blind by a build agent. F8/F9
    remain roster/L-effort design work (a new faction, quest, Lord/Job
    wiring), not a "wire the spec's own numbers" task like everything
    else in this push.
  - `RUST_CATHEDRAL_MECHANICS_1` — was already 6/6 offline-complete
    before this push started; untouched, still just needs a live test.

  Repeated finding worth recording once, here, since it happened across
  ~20 agents this push: the shared `RM_EnvironmentalHazards.csproj` and
  its compiled `.dll` produced git-index collisions constantly under this
  much concurrency (`git commit -- <pathspec>` sweeping a concurrent
  window's uncommitted edits into an unrelated commit, stale
  `.git/index.lock` files, a whole-staged-index sweep more than once).
  Every single time, the content landed correctly and nothing was lost —
  but at least one commit (`6f7f5ff61`) is missing its attribution
  trailer as a result and wasn't worth a corrective commit. If this
  volume of parallel agents on one shared assembly becomes routine, a
  real fix (smaller shared-file surface, or a lock/queue around the
  `.csproj`) is worth a design pass of its own — noted, not filed, since
  it's tooling, not a biome.

  Also several real bugs were caught and fixed in self-review across this
  push, not just wiring — worth naming since it's the actual proof the
  discipline held under pressure: Miasma's under-floor repaint clobber,
  a second Miasma band-pick bug (bridged water misread), Sump's
  `filth-acceptance mask` silently blocking every deposit, Fever Wood's
  `GetModExtension` single-instance trap on a second GenStepDef pass, two
  order-dependent `PatchOperationAdd`s missing `<match>` branches, and a
  Scarlands `wildAnimalScariaChance` that would've left its own arm-gate
  with nothing to ever trigger.
