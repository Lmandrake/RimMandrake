# SCENARIO_DURATION_CUT_1 — the age-register pass: numbers out, "ages past" in

Owner ruled 2026-09-11 (card sitting): CUT "ten thousand years" from the
opening narration (`src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/
Scenario_Utinni.xml:185` — the file's own header vows no invented duration).

**Owner refined the ruling the same day, verbatim**: *"It is acceptable to
include that it is believed to be around 10,000 years ago but that it is in
fact little known. That is ok and even encouraged. But constantly quoting
1000, 10,000, or 'millennia' are unnecessary. Prefer 'ages past' or 'a
previous era' etc."*

So the blast radius is now REPO-WIDE prose register, superseding this item's
earlier scenario-only scope line:
- The habit dies: routine "ten thousand years" / "10,000" / "millennia" /
  "thousand years" phrasing is replaced with era language ("ages past", "a
  previous era", "time out of memory" — the writer's ear picks per passage).
- The framing lives: where a passage genuinely discusses the origin/age of
  the ancients, ONE "believed to be around ten thousand years ago, though in
  truth little is known" construction is welcome — encouraged, not merely
  tolerated. Belief-with-uncertainty, never bare fact.
- Census 2026-09-11 (MEASURED, grep -riE "ten thousand|10,?000 year|
  millennia|thousand years" over design/ + src/RimUtinni/, *.md+*.xml):
  54 hits, ~30 files — top: wreck_fields.md (4), triad_body.md (4),
  wasteland.md (3), BiomeDescriptions_Ashkarr.xml (2), Scenario_Utinni.xml
  (2), RUT_Lightfall.xml (2), plus ~24 more at 1-2 each.
- Frozen sheets among them (the_lantern_deeps.md, the_rust_cathedral.md):
  the register swap is a wording correction under the owner's direct ruling,
  not a content change — make the minimal phrase edit, nothing else.

## spec
- Repo prose pass over the census files: apply the register above. Keep each
  passage's voice; this is a phrase swap, not a rewrite.
- Redeploy UtinniPatches after the XML edits (repo write ≠ deploy) — the
  deploy half stays FOUNDRY's.

## verify
- The census grep returns only sanctioned belief-framings (each explicitly
  hedged as believed/little-known) — count relayed MEASURED.
- Deployed Scenario_Utinni.xml carries no numeric duration; narration reads
  clean on a quicktest new-game screen.

## criteria
Era language is the default everywhere; the ~10,000-years belief appears only
as hedged in-world belief, where origins are actually being discussed.

## Repo half DONE — 2026-09-11 (BENCH fork)

38 of 54 census hits replaced across 25 files (design prose + 5 XML: scenario
narration, Contagion/Slime biome descriptions ×2 copies each, Lightfall).
Touched XML parses clean; BiomeDescriptions_Ashkarr.xml passes validate_patch
static checks. Frozen sheets (the_lantern_deeps, the_rust_cathedral) took the
minimal phrase swap only.

Remaining census: 16 (MEASURED, same grep) — all sanctioned:
- 9 quantity hyperbole, not ages (urns ×2, cradles ×2, "ten thousand hands"
  ×2, rocks, stormtrooper silhouettes, "small deaths"): the ruling is about
  AGE prose; counts left alone.
- 3 hedged belief-framings, one per doc, per the "encouraged" clause
  (the_propane_lakes.md, the_pyrelands.md, wreck_fields.md).
- 2 meta: the scenario header rule + SCENARIO_SPEC.md quoting the offending
  examples as examples.
- 2 technical: sarlacc draft's "Centuries to millennia" duration parameter;
  contagion_placement_candidates.md quoting the OLD Contagion description as
  historical review evidence.

Remaining work: FOUNDRY — redeploy UtinniPatches, quicktest the new-game
narration screen (verify unchanged below).
