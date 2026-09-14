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
