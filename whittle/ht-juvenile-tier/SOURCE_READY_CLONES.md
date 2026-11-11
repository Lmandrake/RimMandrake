# Parent commit requested — actual constructor RNG leak fixed without weakening checks

Required full constructor inspection found actual cause: Verse.Def::.ctor calls Rand.RangeInclusive for debugRandomId. Failure4 contains33 ThingDef and46 LifeStageDef creations, exactly79 calls; observed Rand iterations changed by exactly79 with seed unchanged. Neutral exact count/source evidence: evidence/raw/live-attempt4/rng-constructor-count.json and all-fixture-ctors.il.txt. The menu-attribution hypothesis was wrong. No live retry has run since failure4.

5194384's guard-only version built but has NOT been deployed or live-tested; it would correctly reject those constructors. This followup avoids the owned RNG side effect instead of suppressing it. All prior actual raw attempts preserved.

Two finished paths (hashes evidence/source-ready-clone-hashes.json):

- HugeThings/Source/Titanic/Events/JuvenileTierValidationHooks.cs: retain parent's private-getter ReadRandState accessor and per-call exact guard. Fixture now receives a resolved template ThingDef, MemberwiseClones its ThingDef/RaceProperties, owns new stage/extension lists, and clones every changed LifeStageDef. No Def constructor or shared-def mutation; all clones unregistered. Force extension remains owned. No RNG writes or Push/Pop.
- HugeThings/northstar/juvenile_tier_live.py: passes actual resolved adult template, RESTORES exact entire before/after environment equality INCLUDING RNG, retains per-call guard/idle measurements and every original policy/restoration/preflight control.

Please commit/update SOURCE_COMMITTED.json before required build. This is a concrete fixture correction; no classifier policy, body-size assertion, frozen statement or criterion is lowered. GameDOWN and bridge/actualguardFREE1421 throughout offline work.
