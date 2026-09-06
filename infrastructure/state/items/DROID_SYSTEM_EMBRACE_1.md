# DROID_SYSTEM_EMBRACE_1 — spec the droid systems, then PARK the build

## 🔴 RULING — owner, 2026-08-29, later the same day (supersedes the charge below)

> "This is such a big job, we're going to spec it out but then set it aside again
> for now... V1 we're just going to play with all three of these weird systems and
> get to know them a bit, without rationalizing between them."

- **Decision**: finish the spec (census done; owner's sheet decisions; one spec
  doc), then PARK the build. In v1 all three frameworks — ABF/Synstructs, Asimov,
  JDS — run AS SHIPPED, side by side. No spine is chosen, nothing is rationalized
  between them, no droid C# is written under this item.
- **Reason**: the job outweighs the backstory arc, and familiarity should precede
  architecture — a spine chosen before playing the systems is chosen from paper.
- **Supersedes**: this item's original "build it up... right now" charge and its
  phases 2–3 as v1 work; any reading of the census's "spine question" line as a
  present instruction.
- **Does NOT change**: PAWN_FLAVOR_STARWARS_1 (continues); the sheet and census
  (still wanted — they feed the spec); the data-spike correction in
  droid_ruling.md; the dissolved bolt-gate note (buildable stays true, building
  stays parked); all three droid mod families staying in the modlist.
- **Test**: phases 2–3 below read PARKED; no v1 run sheet or queue item instructs
  choosing a droid framework spine or building droid C#. When the spec closes,
  the build is filed as a NEW item at target v2, and this one closes.

Note for PAWN_FLAVOR_STARWARS_1: the droid backstory flavor set does NOT wait on
a spine — KotOR's `guy762BSC_Droid_*` spawnCategories accept plain BackstoryDefs
as shipped. Whether to author them in v1 is that item's own scoping call.

Original charge (owner, 2026-08-29, verbatim): "I'd love to just expand out and
take in all the droid complexity right now. Perhaps its time to really wrap our
arms around what exists in the mods we've accepted already, then build it up,
embrace it, and robustify it right now." Scale acknowledged as bigger than the
backstory arc. Ground truth that already exists and is NOT re-derived here:
`design/Jawa/droid_ruling.md` — the three-family capture ruling is CLOSED
(JDS force-kill-on-down is a feature; KotOR is THE capture target; Droid Depot
captures via data spike). Design target: frozen dump `OFFICIAL-2026-08-29` (584).

## Phases
0. **Census** (running 2026-08-29): functional inventory of every droid VERB the
   frameworks ship — capture, restraining bolt, data spike, memory wipe, repair,
   rebuild-from-corpse, explode, power/recharge, assembly, upgrades — across
   Droid Depot, KotOR Droids + Resources, JDS TSDA, ABF Synstructs. Three
   parallel subagent sweeps of the mod XML; findings marked CONFIRMED/UNCERTAIN.
1. **Owner curation**: census lands as a review sheet (review-sheets skill);
   owner marks each mechanic embrace / extend / cut.
2. ⛔ **PARKED (ruling above)** — spine design: one design doc choosing the
   primary framework, integration, robustification. Not v1 work; the spec
   records the options, the play experience decides later.
3. ⛔ **PARKED (ruling above)** — flavor layer binding onto a chosen spine.
   (Plain droid BackstoryDefs against KotOR's shipped categories are exempt —
   they need no spine; see the note above.)

## verify
Phase 0 closes when the sheet exists, cites only CONFIRMED mechanics or marks
them UNCERTAIN, and covers all five mods. Later phases get their criteria at
curation time.
