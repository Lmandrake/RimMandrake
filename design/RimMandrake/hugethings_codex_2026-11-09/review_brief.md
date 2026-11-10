You are GPT (Codex), doing a DEEP review of one RimWorld 1.6 mod in the RimMandrake project. Read-only: change nothing.
Repo (a read-only mirror of origin/main): D:\Luke\dev\RimMandrake. Read CLAUDE.md first (rules, traps, rulings).
Mod: src\RimMandrake\HugeThings (C# under Source\, Defs, Patches, northstar\ scripts, validation.py, selftests) and its
test-race companion src\RimMandrake\HugeThingsTestRaces. Related design docs: design\RimMandrake\RM_titanoslime_spec.md,
huge_footprints_perf.md, titan_passage_dark_side_calls_2026-11-05.md, and the item files in
infrastructure\state\items\ whose names contain HUGE or TITAN (plus closed\). Use RimWorld/Verse knowledge carefully; never
guess a defName, field or namespace without reading it.

The owner (Mandrake), 2026-11-09 ~10:05 PM PST, verbatim: "Ask GPT to do a deep review of HugeThings".

Deliver, in bullets and tables, with file:line references and no preamble:
1. What the mod actually does today: every capability, with where it lives, and how it's proven (a selftest, a northstar
   script, a live proof) or that it isn't proven.
2. Correctness bugs, ranked by severity, each with a concrete failure scenario (inputs/state → wrong result). Include
   performance (multi-cell footprints, per-tick work), save/load (Scribe), multiplayer-unsafe randomness if relevant,
   Harmony patch fragility, and Mod Settings (every major feature needs on/off and tuning; defaults = shipped behaviour).
3. Gaps between the design docs/items and the code: promised but not built, built but undocumented, docs that are now false.
4. The test position: which selftests and northstar checks exist, which could pass while the feature is broken (a
   checker that can't fail), and the 5 most valuable missing checks.
5. The top 10 recommended actions, each small enough for one agent session, with its acceptance check.
Mark anything you could not verify as UNVERIFIED.
