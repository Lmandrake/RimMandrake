## spec
From CHECK's **C42** (`5aca170`, `071cf52`), routed by REP because it lands
directly on the owner's ruling that faction and ideo work is v1.

The owner's words today: *"faction and ideo work are part of v1, and we already
HAVE the ideoligion I believe. The task to build the factions in-game should be
nearly done save for the allowed items, descriptions, etc."* 🔴 **That belief is
the thing C42 cannot yet confirm.**

`The Salvation.rid` and `MandrakeJawa.xtp` both carry a `<modIds>` provenance
block naming **585 mods, 11 of which no longer load** — including all three
xenotype donors. What CHECK cleared offline against the live dump: the xenotype
is CLEAN (35/35 genes plus icon), memes 5/5, culture present, and the
`Outland_*` genes are safe because Outland Genetics is a DIFFERENT mod from the
switched-off `neronix17.outerrim.galacticdiversity`.

⚠️ **The 82 precepts are UNMEASURED, and CHECK asks for that word specifically.**
Not "missing" — an earlier scrape reporting 71 missing was CHECK's own bug: the
precept block nests `RitualBehavior` / `RitualOutcomeEffect` /
`RitualObligationTargetFilter` defNames, which are not `PreceptDef`s. And
`validate_ideoligion.py` does not cover this case — it reads IdeoPresetDef and
FactionDef XML and answers "no religions found" on a `.rid`. **There is no
offline route to the answer.**

Why it is yours and why it is urgent: an ideoligion **bakes at world creation
and cannot be retrofitted**, same as the factions. If the faction work is
"nearly done", this artifact is close to final and is the largest unmeasured
surface on CHECK's board. The live answer is cheap — load the ideo on the
scratch map and read the dialog, one screen — and CHECK has queued it ahead of
any worldgen run. **Sequence it before the faction work is called done.**

## verify
the 82 precepts are measured live and reported as present/absent by defName.

## criteria
the ideoligion loads with every precept resolving, on the mod set that will be
active at world creation.

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready
