# TRIM_VALIDATION_LAYERS_1 Restructure the seats to validate and test less

## spec

Owner, 2026-08-23 14:4x, verbatim:

> *"Restructure the agents to have less validation and testing. Not everything requires
> multiple validation and testing after the initial agent generates it... less traffic
> for CHECK, less thrashing. Let's talk and plan about it."*

🔴 **This is a DOCTRINE change, and it is filed for talk first — do not start rewriting
seat files off this paragraph.** He asked to plan it with REP; the plan is the first
deliverable, not the edits.

## What the plan has to settle

1. **Which classes of work get NO second pass at all.** The candidate line is
   *reversible and self-evidencing* (a def edit whose own tool reported success, a doc,
   a rename, a queue view) versus *irreversible or silent* (`--apply` deploys, anything
   the game must load, anything whose failure mode is silence).
2. **What CHECK is FOR once it stops re-reading BUILD's output.** If CHECK only runs
   what needs a live game or a load, its queue shrinks to the reload blocks and the
   findings — that may be the right answer, but it has to be said out loud.
3. **Where the verify obligation moves** — onto the generating seat's own return value,
   which POLICY already asserts (*"the return value is the verification"*) and the
   practice does not follow.
4. **What we keep, deliberately.** The three named exceptions in POLICY
   (`deploy --apply`, force-push, `ModsConfig.xml` writes) and the `measure` rule for
   numbers are the two things that have actually caught errors; they should survive any
   trim.
5. **How much traffic this is.** Count CHECK items closed with no finding versus with
   one, out of the ledger — that number decides how big the win is and should be
   MEASURED before the doctrine moves.

## Watch out

- ⚠️ **The counter-evidence is on file.** Handoffs this week record two items
  (`JAWA_ROBES_NEVER_WORN_1`, `EMPIRE_GRUNT_SPAWNS_BARE_1`) filed as defects against
  yesterday's defs, and `CLAUDE.md` carries several rulings that exist because a seat
  reported something settled that was wrong. Trimming validation is right where the
  check was ritual; it is wrong where the failure is silent. The plan must name which
  is which rather than lowering everything.
- Touches `infrastructure/agents/POLICY.md`, `CHECK.md`, `BUILD.md` and `CLAUDE.md` —
  files every seat reads, so it supersedes and must write INTO what it overrules.
