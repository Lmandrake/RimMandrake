# Shared read-line registry

Owner ruling 2026-09-16, `READ_LINE_REGISTRY_SHARED_1`: read-line ids are
**GLOBAL**, with one shared registry. A recurring demand — one that more than
one mod's `### must read` / `### cannot read` checklist wants (no engineering
marker in player text, tier-neutral prose, ...) — is authored ONCE, here, and
cited by every walk that holds it, id and prose copied verbatim. A demand only
one mod's experience raises stays LOCAL: authored directly in that mod's own
walk (or, pre-promotion, in a DRAFT like
`Transient/north_star_read_aftermath_DRAFT_2026-09-16.md`), but its id still
comes from this same flat, global namespace — no per-mod prefix — so a later
promotion to this file never collides with something already in play.

This amends `design/RimMandrake/north_star_validation_spec.md` §10.1, which
already rules "one id namespace across both axes" but is silent on whether
that namespace is per-mod or global across all 77+ walks. It is now global.

Nothing in this file is itself a bar. A registry entry binds a mod only once
that mod's own walk cites it under a `VALIDATED` `## north star` section
(spec §5, §6a) — exactly as a locally-authored line does. This file only
stops the same demand from being independently invented, worded slightly
differently, and drifting, in N different walks.

## How a walk cites an entry here

Copy the id, evidence class and prose verbatim into the walk's own
`### must read` / `### cannot read` checklist, and add `, shared` inside the
class parenthesis so the citation is machine-checkable:

```
- [ ] `some_registered_id` (absolute, shared) — <prose copied verbatim
      from this file, wrapped however the walk wraps its lines>
```

`modcheck/readline_registry.py` (wired into `modcheck lint`; covered by
`modcheck/selftest_readline_registry.py`) fails loudly — class
`DANGLING_CITATION` — if a `shared`-tagged id in any walk is not a member of
this registry. Same failure shape as `walklint`'s `UNKNOWN_ID`: a query bug in
plain sight beats a silently-uncovered demand.

🔴 **Editing an entry's prose here does not, by itself, change any walk's
hash.** `northstar.py` hashes only the walk file's own bytes, never this file.
The propagation is manual and mandatory: after editing an entry below, copy
the corrected prose into every walk that cites it, in the SAME sitting — that
copy is what re-hashes (and therefore re-drafts) each citing walk, per
`NORTHSTAR_HASH_SCOPE_1`'s ruling that a hashed section is corrected and
re-validated together, never left stale to protect the hash. Leaving a citing
walk's copy stale after an edit here is a silent drift the lint cannot see,
because it checks the ID matches, not that the prose still does.

## registry

### cannot read

- [ ] `never_engineering_marker_in_player_text` (absolute) — a bracketed
      marker, a defName, a placeholder, a repo path, an internal item id, a
      C# symbol, a `§` reference or a project codename in any text the player
      reads. First authored in
      `design/validation_walks/RimMandrake/Oracle.md` (2026-09-16, still
      DRAFT) and reconciled here as this registry's founding entry per
      `READ_LINE_REGISTRY_SHARED_1`. Cited by: Oracle
      (`design/validation_walks/RimMandrake/Oracle.md`, DRAFT) and
      Aftermath's DRAFT read-line candidates
      (`Transient/north_star_read_aftermath_DRAFT_2026-09-16.md`, not yet
      written into a walk).

### must read

(none yet — the next promoted demand goes here. Aftermath's
`prose_is_tier_neutral` / `campaign_vocabulary_lives_here` pair, enforcing
R6/R9's "labels/descriptions must read vanilla-generic", is the leading
candidate once a second mod needs the same demand; it stays LOCAL to that
draft for now.)
