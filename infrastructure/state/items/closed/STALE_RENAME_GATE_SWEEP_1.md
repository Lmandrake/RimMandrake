# STALE_RENAME_GATE_SWEEP_1 — delete a gate that closed 16 days ago

`NAMING_SCHEME_EXECUTION_1` **closed 2026-08-31 at `54a8e28d`** on the owner's own
word (*"Deploy the full rename."*). Since then, roughly a dozen live design docs
have gone on citing it as a reason NOT to rename something — "governed by
NAMING_SCHEME_EXECUTION_1", "do not rename ahead of it", "migration waits on it".
Every one of those is a gate on nothing, and their combined effect is real: the
FlowWorks mod (named by ruling 20, 2026-09-16) was still shipping as
`fluidcanals` because the dead gate had been copy-pasted into its own build
programme.

Owner, 2026-09-16, on being shown one of them: *"No... we rename right now.
That's crazy."* And: *"That file may be VERY old... please be careful and do not
accept stale info."*

## Already fixed 2026-09-16 (do not redo)

`CLAUDE.md`, `design/NAMING_SCHEME_PLAN.md`, `FLOWWORKS_BUILD_PROGRAM_1.md`
Phase 1, `design/RimMandrake/flowworks_mod_definition.md` (4 citations), and
7 canon-library files (`sith_species`, `klatooinian`, `yoda_species`,
`sith_pureblood`, `massassi`, `RACES_TODO.md` ×2) — the canon ones now point at
`XENOTYPE_CANON_CORRECTION_1`, which is where a xenotype defName fix actually
belongs.

## spec

Sweep the remainder. MEASURED list as of 2026-09-16 — re-grep, since it will have
moved:

```
design/RimStarWars/gizka_ship_pest_draft.md:49
design/RimMandrake/liquids_framework_design.md:19, 241
design/RimMandrake/RM_liquid_types_mod.md:236
design/FABLE_WINDOW_PROPOSITION.md:86
design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md:477
design/Jawa/worldbuilding/biomes/rosters/_fish_assignment_proposal.md:38
design/Jawa/worldbuilding/LIQUID_BIOMES_MAP_1_RECONCILIATION.md:94
design/Jawa/kyber_trade_plot_spec.md:37
design/Jawa/graffiti_spec.md:201
```

For each, decide which of three it is and act — do not blanket-replace:

1. **A rename that is simply owed** → say so, and name the item that will do it
   (or file one). Delete the gate language.
2. **A rename with a real remaining blocker** (a live packageId in
   `ModsConfig.xml`, a tracked DLL, reflection strings) → keep the caution but
   state the ACTUAL blocker, never the closed item.
3. **Historical prose** describing what was decided at the time → leave it, but
   only if a reader cannot mistake it for a current instruction.

🔴 **Second defect, same family, found in the same grep:**
`design/RimMandrake/liquids_framework_design.md:241` still names the consolidated
mod **`Fluidity`**. Ruling 20 (2026-09-16) superseded that with **`FlowWorks`**.
Fix it wherever `Fluidity` survives as the mod's name — and note that the same
doc was already caught (2026-09-16 handoff) blocking engine work on three flood
defects that were fixed 2026-09-02. Treat that file as suspect throughout; a
full read is warranted, not a spot fix.

## verify

```
PROVE   grep -rn 'NAMING_SCHEME_EXECUTION_1' design/ returns only citations that
        say it is CLOSED, or that name a real successor item
EXPECT  every surviving mention is either history that cannot be misread as an
        instruction, or points at the item that will actually do the work
LIES    a blanket find-and-replace. Case 2 above exists — FlowWorks really does
        have a tracked DLL and reflection strings blocking a naive rename, and
        deleting that caution would break the bridge companion silently
```

## criteria

No live doc instructs a reader to defer a rename to `NAMING_SCHEME_EXECUTION_1`,
and `liquids_framework_design.md` no longer calls the mod `Fluidity`.

## not chasing

The FlowWorks rename itself — that is `FLOWWORKS_BUILD_PROGRAM_1` Phase 1, on the
Desktop, and it carries its own MEASURED blast radius.

## Watch out

- ⛔ Do not rewrite the old names in `Transient/**` (`.log` captures, `.rws.bak`
  savegames), `infrastructure/state/modlists/**` (ModsConfig snapshots),
  `events.jsonl` (append-only) or `infrastructure/state/derived/**` (regenerated).
  Those are point-in-time evidence; rewriting them falsifies the record.
- The general lesson, worth carrying past this item: **a gate cited by name
  outlives the item it names.** When a doc defers work to an item, check the
  item's state before believing it.
